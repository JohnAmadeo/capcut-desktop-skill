# Evidence and confidence

This skill was derived from direct local-file inspection and Desktop open/export tests, not a searched official schema. No claim is made that CapCut has no official documentation anywhere; none was used for these internal fields.

## Verified Desktop capabilities

- CapCut macOS 8.9.0 loaded programmatically assembled local drafts, normalized their records and exported them.
- Videos, photos, subtitles, separate audio, constant speeds, normalized image transforms and five inline keyframe property types were exercised.
- App-saved JSON can contain identical repeated material records with the same ID; conflicting duplicates require investigation.
- Exported video was checked through complete decoding, measured audio peaks/loudness and visual frame inspection. These checks are distinct from structural JSON validation.

## Successful recipes, incomplete semantics

- Six draft mirrors were written successfully, but the necessity of every mirror was not isolated experimentally.
- Track flags and attribute values came from working examples; only specific configurations were tested.
- Exact-file relinking resolved missing-media prompts even though files existed. The cause of the initial prompt was not established.
- Offline name/path/index updates succeeded; the project browser had cached old names. Other versions, clones and multi-timeline projects need separate checking.
- Alpha appearance must be checked in an actual CapCut composite; codec and alpha metadata alone do not prove correct blending.

## Not established

Windows paths/compatibility, future draft versions/encryption, generic auto-export API/CLI, arbitrary effects/transitions, native variable-speed graphs, exact Bezier controls, 3D group transforms, Unicode range indexing, all track attribute bits, keyframe alpha/rotation enums, universal font/blur units, pixel identity across renderers, subjective listening.

## Template provenance

Bundled examples are sanitized CapCut Desktop 8.9.0 object structures, not ready-to-install complete projects. They remove source wording, user paths, hardware identity and project identity. Prefer fresh examples from the installed version when it differs, and confirm behavior through an editor open/export check. Do not treat an early experimental builder as more authoritative than the final app-saved document and reviewed export.
