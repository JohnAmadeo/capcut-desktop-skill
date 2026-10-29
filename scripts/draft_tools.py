#!/usr/bin/env python3
"""Read/validate CapCut JSON; extract sanitized templates into a NEW offline folder."""
import argparse
import copy
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


def load(path):
    with Path(path).open(encoding='utf-8') as f:
        d = json.load(f)
    if not isinstance(d, dict):
        raise ValueError('Expected a JSON object')
    return d


def material_index(d):
    result = {}
    for category, items in d.get('materials', {}).items():
        if isinstance(items, list):
            for m in items:
                if isinstance(m, dict) and m.get('id'):
                    result[m['id']] = (category, m)
    return result


def summary(d):
    tracks = d.get('tracks', [])
    return {
        'timeline_id': d.get('id'),
        'name': d.get('name'),
        'app_version': d.get('last_modified_platform', {}).get('app_version') or d.get('platform', {}).get('app_version'),
        'draft_version': d.get('version'),
        'new_version': d.get('new_version'),
        'duration_us': d.get('duration'),
        'fps': d.get('fps'),
        'canvas': d.get('canvas_config'),
        'render_modes': {k: d.get(k) for k in ('mixed_track_mode_on', 'render_index_track_mode_on', 'free_render_index_mode_on')},
        'tracks': [{'type': t.get('type'), 'name': t.get('name'), 'segments': len(t.get('segments', [])), 'flag': t.get('flag'), 'attribute': t.get('attribute')} for t in tracks],
        'segments': sum(len(t.get('segments', [])) for t in tracks),
        'materials': {k: len(v) for k, v in d.get('materials', {}).items() if isinstance(v, list) and v},
        'inline_keyframe_properties': sorted({g.get('property_type', '') for t in tracks for s in t.get('segments', []) for g in s.get('common_keyframes', [])}),
    }


def validate(d):
    errors, warnings = [], []
    mi = material_index(d)
    seen = {}
    paths = set()
    material_seen = {}
    repeated_materials = 0
    fps = d.get('fps', 30)
    tolerance = 1e6 / fps + 1000 if isinstance(fps, (int, float)) and fps > 0 else 35000

    def unique(id_, location):
        if not id_:
            errors.append(f'{location}: missing id')
        elif id_ in seen:
            errors.append(f'{location}: duplicate id {id_} (also {seen[id_]})')
        else:
            seen[id_] = location

    def check_path(p, location):
        if not p or p in paths:
            return
        paths.add(p)
        if not isinstance(p, str):
            errors.append(f'{location}: expected a string path')
        elif not Path(p).is_absolute():
            warnings.append(f'{location}: relative or non-file path {p!r}')
        elif not Path(p).is_file():
            errors.append(f'{location}: missing file {p}')

    if not isinstance(d.get('tracks'), list) or not isinstance(d.get('materials'), dict):
        return {'errors': ['Expected tracks list and materials object'], 'warnings': [], 'checked_paths': 0}
    for category, items in d['materials'].items():
        if not isinstance(items, list):
            continue
        for n, m in enumerate(items):
            if not isinstance(m, dict):
                errors.append(f'materials.{category}[{n}]: expected object')
                continue
            loc = f'materials.{category}[{n}]'
            material_id = m.get('id')
            if material_id in material_seen:
                if material_seen[material_id] != (category, m):
                    errors.append(f'{loc}: conflicting duplicate material id {material_id}')
                else:
                    repeated_materials += 1
            else:
                material_seen[material_id] = (category, m)
                unique(material_id, loc)
            if category in ('videos', 'audios'):
                check_path(m.get('path'), loc)
            if category == 'texts':
                check_path(m.get('font_path'), loc + '.font_path')
                for key in ('content', 'base_content'):
                    content = m.get(key)
                    if not content:
                        continue
                    try:
                        rich = json.loads(content)
                        if not isinstance(rich, dict) or not isinstance(rich.get('text'), str):
                            raise ValueError('Expected text string in object')
                        for st in rich.get('styles', []):
                            check_path(st.get('font', {}).get('path'), loc + '.' + key + '.font')
                            r = st.get('range')
                            if r and (len(r) != 2 or any(not isinstance(x, int) for x in r) or min(r) < 0):
                                errors.append(f'{loc}.{key}: malformed style range {r}')
                            # Unicode indexing is version-dependent: do not enforce Python len as a universal rule.
                    except (ValueError, TypeError, AttributeError) as e:
                        errors.append(f'{loc}.{key}: invalid rich text: {e}')
    for ti, t in enumerate(d['tracks']):
        unique(t.get('id'), f'tracks[{ti}]')
        spans = []
        for si, s in enumerate(t.get('segments', [])):
            loc = f'tracks[{ti}].segments[{si}]'
            unique(s.get('id'), loc)
            mid = s.get('material_id')
            if mid not in mi:
                errors.append(f'{loc}: unresolved material_id {mid}')
            for ref in s.get('extra_material_refs', []):
                if ref not in mi:
                    errors.append(f'{loc}: unresolved extra_material_ref {ref}')
            target = s.get('target_timerange')
            for kind, r in [('target', target), ('source', s.get('source_timerange'))]:
                if r is None and kind == 'source':
                    continue
                if not isinstance(r, dict) or any(not isinstance(r.get(k), int) or isinstance(r.get(k), bool) for k in ('start', 'duration')):
                    errors.append(f'{loc}: {kind} range must have integer microseconds')
                    continue
                if r['start'] < 0 or r['duration'] <= 0:
                    errors.append(f'{loc}: invalid {kind} range {r}')
            if isinstance(target, dict) and all(isinstance(target.get(k), int) for k in ('start', 'duration')):
                spans.append((target['start'], target['start'] + target['duration'], loc))
                if isinstance(d.get('duration'), int) and spans[-1][1] > d['duration'] + tolerance:
                    warnings.append(f'{loc}: extends past document duration')
            source = s.get('source_timerange')
            speed = s.get('speed', 1)
            if not isinstance(speed, (int, float)) or not math.isfinite(speed) or speed <= 0:
                errors.append(f'{loc}: invalid speed {speed}')
            elif isinstance(source, dict) and isinstance(target, dict) and all(isinstance(r.get('duration'), int) for r in (source, target)):
                if abs(source['duration'] - target['duration'] * speed) > tolerance * max(speed, 1):
                    warnings.append(f'{loc}: source/target durations differ from constant-speed relation; inspect speed curves/rounding')
                if mid in mi:
                    mat = mi[mid][1]
                    if mat.get('type') != 'photo' and isinstance(mat.get('duration'), int) and source.get('start', 0) + source['duration'] > mat['duration'] + tolerance:
                        warnings.append(f'{loc}: source selection exceeds recorded material duration')
            for group in s.get('common_keyframes', []):
                unique(group.get('id'), loc + '.keyframe_group')
                points = group.get('keyframe_list', [])
                offsets = [k.get('time_offset') for k in points]
                if any(not isinstance(x, int) for x in offsets):
                    errors.append(f'{loc}: keyframe offsets must be integer microseconds')
                elif offsets != sorted(offsets):
                    errors.append(f'{loc}: unordered keyframes')
                for k in points:
                    unique(k.get('id'), loc + '.keyframe')
                    if not isinstance(k.get('values'), list):
                        errors.append(f'{loc}: keyframe values must be a list')
        spans.sort()
        for previous, current in zip(spans, spans[1:]):
            if current[0] < previous[1] - 10:
                warnings.append(f'{current[2]}: overlaps preceding segment on same track; confirm intentional')
    return {'errors': errors, 'warnings': warnings, 'checked_paths': len(paths), 'identical_repeated_material_records': repeated_materials}


def scrub_templates(objects):
    """Redact example-specific data while preserving unknown structural fields."""
    ids = {}
    def scrub(value, key=''):
        if isinstance(value, list):
            return [scrub(v, key) for v in value]
        if isinstance(value, dict):
            result = {}
            for k, v in value.items():
                if k in ('device_id', 'hard_disk_id', 'mac_address', 'recognize_task_id', 'group_id', 'recognize_text'):
                    result[k] = ''
                elif k in ('words', 'current_words'):
                    result[k] = {'start_time': [], 'end_time': [], 'text': []}
                else:
                    result[k] = scrub(v, k)
            return result
        if isinstance(value, str):
            if key in ('content', 'base_content'):
                try:
                    rich = json.loads(value)
                    if isinstance(rich, dict) and 'text' in rich:
                        rich = scrub(rich)
                        rich['text'] = 'Example'
                        for style in rich.get('styles', []):
                            style['range'] = [0, 7]
                        return json.dumps(rich)
                except (ValueError, TypeError):
                    pass
            if key in ('text', 'name') and value:
                return 'Example'
            if key == 'material_name' and value:
                return 'example' + Path(value).suffix
            if re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', value):
                return ids.setdefault(value, f'EXAMPLE-ID-{len(ids)+1:05}')
            if value.startswith('/'):
                suffix = Path(value).suffix.lower()
                area = 'fonts' if suffix in ('.otf', '.ttf', '.ttc') else 'media'
                return '/absolute/' + area + '/example' + suffix
        return value
    return {k: scrub(v) for k, v in objects.items()}


def extract(d, output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    objects = {}
    shell = copy.deepcopy(d)
    shell.update(name='', duration=0, tracks=[])
    shell['materials'] = {k: [] if isinstance(v, list) else v for k, v in shell.get('materials', {}).items()}
    shell['keyframes'] = {k: [] for k in shell.get('keyframes', {})}
    shell['config'] = {k: v for k, v in shell.get('config', {}).items() if k not in ('subtitle_taskinfo',)}
    shell['path'] = ''
    objects['draft-shell'] = shell
    for category, items in d.get('materials', {}).items():
        if category not in ('videos', 'audios', 'texts', 'speeds') or not isinstance(items, list):
            continue
        for m in items:
            key = {'video': 'video', 'photo': 'photo', 'subtitle': 'subtitle', 'text': 'text'}.get(m.get('type'), 'audio' if category == 'audios' else 'speed' if category == 'speeds' else category)
            objects.setdefault(key + '-material', copy.deepcopy(m))
            if category == 'texts' and (m.get('bold_width', 0) or m.get('italic_degree', 0)):
                objects.setdefault('emphasis-text-material', copy.deepcopy(m))
    for t in d.get('tracks', []):
        if t.get('segments'):
            track_shell = {k: copy.deepcopy(v) for k, v in t.items() if k != 'segments'}
            track_shell['segments'] = []
            objects.setdefault(t['type'] + '-track', track_shell)
        for seg in t.get('segments', []):
            clean = copy.deepcopy(seg)
            clean.update(extra_material_refs=[], common_keyframes=[], keyframe_refs=[])
            objects.setdefault(t['type'] + '-segment', clean)
            if t['type'] == 'video' and abs(seg.get('speed', 1) - 1) > 1e-6:
                objects.setdefault('retimed-video-segment', copy.deepcopy(clean))
            for group in seg.get('common_keyframes', []):
                objects.setdefault(group.get('property_type', 'unknown') + '-keyframes', copy.deepcopy(group))
    for name, obj in scrub_templates(objects).items():
        (out / (name + '.json')).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
    provenance = {'app_version': summary(d)['app_version'], 'draft_version': d.get('version'), 'new_version': d.get('new_version'), 'status': 'Sanitized working examples; clone fields and replace IDs/references intentionally. Not a standalone complete project.'}
    (out / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return {'output': str(out.resolve()), 'templates': len(objects)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'validate', 'templates'):
        p = sub.add_parser(name)
        p.add_argument('draft', type=Path)
        if name == 'templates':
            p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        d = load(args.draft)
        if args.command == 'inspect':
            result = summary(d)
        elif args.command == 'validate':
            result = validate(d)
        else:
            result = extract(d, args.output)
        print(json.dumps(result, indent=2))
        return 1 if args.command == 'validate' and result['errors'] else 0
    except (OSError, ValueError, TypeError, KeyError) as e:
        print(f'Error: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
