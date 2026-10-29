# Observed draft schema — CapCut Desktop 8.9.0

This is a field guide to exercised JSON, not an exhaustive JSON Schema or vendor contract. See `assets/schema-8.9.0/` for full sanitized object examples. Preserve auxiliary fields when cloning; the short snippets below are not guaranteed standalone objects.

## Document and graph

The document contains `id`, `version`, `new_version`, `name`, `duration`, `fps`, `canvas_config`, `config`, `tracks`, `materials`, `keyframes`, platform fields, and render-mode flags. The exercised portrait canvas was `{"ratio":"9:16","width":1080,"height":1920,"background":null}`, even though its export was 2160 by 3840. Do not confuse composition coordinates with export dimensions.

`materials` maps collection names to lists. The blank contained many empty collections; retain them. Core graph:

- `tracks[].segments[].material_id` references a material's `id`.
- `segments[].extra_material_refs` references auxiliary objects such as speeds, animations and canvases.
- `segments[].common_keyframes` holds inline keyframe groups, independently of top-level `keyframes` and `keyframe_refs`.
- `materials.videos` holds **both videos and still images** (`type: "video"` or `"photo"`). Do not put ordinary PNG clips exclusively into `materials.images`.
- `materials.texts` contains normal text and subtitles; rich content is serialized JSON inside a JSON string.
- `materials.audios` contains audio material records. Observed audio material types include `extract_music` and `video_original_sound` for detached original video sound.

Use fresh UUIDs for new tracks, segments, materials, auxiliary objects and keyframe objects. Sharing a material can work, but CapCut may repeat/normalize it when saving. The final app-saved draft had identical repeated material records with the same ID. These are not automatically corruption; conflicting records sharing an ID need investigation. Do not rely on exact object counts staying unchanged.

## Tracks and stacking

A track has `id`, `type`, `segments`, `flag`, `attribute`, `name`, and `is_default_name`. Exercised types: `video`, `text`, `audio`. New video overlays used `flag: 2`, text used `flag: 1`; these are observed values, not fully decoded enums.

For the tested `render_index_track_mode_on: true` document, the builder appended visual tracks from bottom to top, assigning each segment `track_render_index` to its track index and ascending `render_index` values (increments of 1000). CapCut normalized audio render indices to zero on save. Preserve the current project's render mode rather than transplanting indices without context.

A hidden raw-source alternative used track `attribute: 2`, segment `visible: false`, and `volume: 0`; the export verified that it did not replace or double the visible picture/audio. Do not infer all attribute bit meanings from that single example. Text and other overlapping segments need separate tracks if their overlaps are intentional.

## Segment and timing

```json
{"id":"<segment-id>","material_id":"<material-id>","source_timerange":{"start":9600000,"duration":21033000},"target_timerange":{"start":38767000,"duration":21033000},"speed":1.0,"volume":0.315632159,"last_nonzero_volume":0.315632159,"visible":true,"extra_material_refs":[],"common_keyframes":[],"clip":{"scale":{"x":1.0,"y":1.0},"rotation":0.0,"transform":{"x":0.0,"y":0.0},"flip":{"vertical":false,"horizontal":false},"alpha":1.0}}
```

Times in the exercised ranges, material durations, keyframe `time_offset`, and document `duration` are integer **microseconds**. `target_timerange` locates the segment in the edit; `source_timerange` selects its media. Text segment source ranges were `null`. `render_timerange` often contained zeroes; do not substitute it for edit placement.

For constant speed, source duration approximately equals target duration multiplied by speed; frame rounding can leave a small discrepancy. Copy the actual saved source selection for exact recovery. For new picture cuts, quantize the absolute start and end to frame boundaries and subtract; independently rounding each duration can create gaps.

Use exact rational fps, including non-integer rates where applicable. At 30 fps, one frame is approximately 33,333 microseconds; do not accumulate that rounded value frame by frame.

A non-unit speed used both `segment.speed` and a referenced `materials.speeds` object:

```json
{"id":"<speed-id>","type":"speed","mode":0,"speed":1.25,"curve_speed":null}
```

Place its ID in `extra_material_refs`. Variable-speed graphs and pitch flags require a current working sample; they were not fully mapped here.

## Media material and crop

Video/photo material records include `id`, `type`, `duration`, absolute `path`, `width`, `height`, `material_name`, `has_audio`, `local_material_id`, `crop`, `crop_ratio`, `crop_scale`, `matting`, and many algorithm/default fields. Probe actual media dimensions/duration. Still material duration `10800000000` occurred as a long-capacity default; the segment target duration controls its visible length.

Preserve normalized crop corners (`upper_left_x/y`, `upper_right_x/y`, `lower_left_x/y`, `lower_right_x/y`), segment clip transform and source sampling separately. Do not assume copying only `clip.scale` preserves every crop. When retaining an existing shot's framing, preserve its original `clip` object and relevant material crop fields. New photo examples used full-image crop corners.

## Transform conventions

For a centered image without parent transforms, let canvas dimensions be $W,H$, desired center in top-left pixel coordinates be $p_x,p_y$, and media dimensions be $w,h$. Observed mappings:

\[
x_{cap} = \frac{p_x-W/2}{W/2},\qquad y_{cap}=\frac{H/2-p_y}{H/2}
\]

\[
f=\min(W/w,H/h),\qquad scale_{cap,x}=\frac{scale_{source,x}/100}{f}
\]

Apply the analogous mapping to Y scale. CapCut's default contain fit is already included; ignoring it causes sticker-size errors. Use the actual media dimensions and account for anchor-point offsets. The same normalized positions/scales were exercised in keyframes.

`clip.rotation` stores the segment's rotation angle. Establish direction with a native rotated sample rather than assuming another editor's sign convention. 3D orientations, arbitrary parent transforms and rotation keyframes were not verified.

`clip.alpha` is a unit opacity value. Audio `volume` is a linear gain; values above one occurred and rendered. For a decibel change $g$, multiply linear gain by $10^{g/20}$; check resulting peak headroom.

## Inline keyframes

```json
{"id":"<group-id>","material_id":"","property_type":"KFTypePositionY","keyframe_list":[{"id":"<key-id>","curveType":"Line","time_offset":9600000,"left_control":{"x":0.0,"y":0.0},"right_control":{"x":0.0,"y":0.0},"values":[0.25],"string_value":"","graphID":""}]}
```

Verified in the final saved draft/export: `KFTypePositionX`, `KFTypePositionY`, `KFTypeScaleX`, `KFTypeScaleY`, `KFTypeVolume`.

Keyframe offsets were **source-relative** in the exercised cases: for a trimmed constant-speed media segment, map local edit time to source start plus local time multiplied by speed. Text/photo examples started at zero. Do not add the timeline target start to every offset.

When native easing controls are unknown, sampled `Line` keyframes can approximate an intended curve. Retain endpoints and changes in slope, and verify the rendered result. Sampling density depends on the curve and playback rate; it is not a schema requirement.

`KFTypeAlpha` and `KFTypeRotation` were **not exercised in the verified keyframe property set**. Treat them as unverified candidates, not established enums.

## Editable text and duplicated style fields

A text material has `type: "subtitle"` or `"text"`, `content`, `base_content`, text/font/style metadata and caption bookkeeping. Parse `content` with JSON before editing it; save it as a JSON string again.

```json
{"text":"Example","styles":[{"range":[0,7],"size":8.0,"font":{"path":"/absolute/fonts/en.ttf","id":""},"fill":{"content":{"render_type":"solid","solid":{"color":[1.0,1.0,1.0]}}},"strokes":[{"width":0.08,"mode":0,"content":{"render_type":"solid","solid":{"color":[0.0,0.0,0.0]}}}]}]}
```

Keep the string style's size/font/fill/stroke/shadow and parallel top-level material fields consistent, including `font_size`, `font_path`, `text_color`, `bold_width`, `italic_degree`, border/shadow fields, and `base_content`. The run used basic Latin text; range-index behavior for emoji, combining text and UTF-16 was not established—obtain a native sample for those cases.

Clear stale recognition data for newly authored text: `recognize_task_id`, incompatible `words`/`current_words`, old caption groups and references. Preserve such data when intentionally editing an existing recognition-linked caption instead of blindly clearing it.

Font size is **not a universal pixel unit**. Calibrate the actual font, size, alignment and line wrapping against a native-editor export. `line_max_width`, explicit newlines, `fixed_width` and `fixed_height` can affect layout; preserve intended line breaks and check long phrases.

Rich-style `bold` and `italic` flags can coexist with top-level `bold_width` and `italic_degree`. Use the actual font file and preserve the intended treatment rather than substituting an unrelated face or interpreting every emboldening treatment as a border.

Rich-style shadow `diffuse` and top-level `shadow_smoothing` are not established pixel equivalents. Calibrate blur, strength and offset visually for the chosen font and canvas. Do not apply another project's text-placement offsets or shadow settings globally.
