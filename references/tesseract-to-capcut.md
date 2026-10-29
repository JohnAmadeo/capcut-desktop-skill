# Tesseract to CapCut Desktop

## Establish the authoritative source

Use the latest actual `.tsrct`, its checked-out document, packaged media and matching export. Read requested revisions from any referenced chat before choosing a version; modification times alone are insufficient. The migration that established this skill included the final earlier music entrance and later gain revision, not just the initial reconstruction.

Use the installed Tesseract CLI and its matching skill/version guidance. `project checkout` supplies authoritative JSON; `project commit` preserves package integrity. Directly replacing `project.json` inside a `.tsrct` ZIP failed because metadata hashes/byte lengths no longer matched. The successful route copied the source project then committed the reduced render document through the CLI. ZIP extraction is useful for reading embedded asset paths; it is not a license to bypass integrity checks. Never extract untrusted archive paths without traversal checks.

## Map clocks and graph

- Tesseract document `duration` is seconds, layer ranges/keyframe times in the exercised document are milliseconds; CapCut uses microseconds. Multiply layer milliseconds by 1000 and document seconds by 1,000,000.
- Compute picture frame-boundary start/end using rational fps; retain original microsecond ranges separately when round-tripping an existing CapCut edit.
- `activeRange` is placement in the parent. `sourceRange` is a source selection. `playback` can encode a distinct retiming/sampling map; do not infer all timing from the name or source range alone.
- Tesseract layer arrays in this composition were front-first. Native CapCut visual tracks were built bottom-first. Flatten groups only after resolving parent transforms, local time and clipping/matte behavior. The tested background group had identity transform, so its images could be mapped directly.
- Apply the centered-image normalized transform mapping in [schema.md](schema.md). Account for anchor points. The initial negative rotation conversion was corrected to the same positive angle for the migrated stills.

For a text box with top-left position $p$, box dimensions $b$, and anchor $a$, the starting candidate center is $p+b/2-a$. Different text layout engines still require visual alignment, font-size and line-wrap calibration.

## Preserve editability deliberately

Translate ordinary text to native text materials, PNGs to native photo clips, audio to separate clips, and supported motion to inline keyframes. A native CapCut timeline with many clips is not the same as importing one final MP4.

The exercised hybrid preserved custom appearance by:

1. Creating a Tesseract render document containing only the graded/retimed picture, hook matte and painting background; exporting it at 4K/30.
2. Splitting that picture render into the original 19 native CapCut cut boundaries. Those visible clips' retiming/color/crop were **baked**, not recreated as native CapCut shaders.
3. Keeping an additional hidden/muted native track from the original raw sources, with source cuts, speed records and original crop/framing. Disclose the visible-versus-raw distinction.
4. Recreating 79 caption phrases, four figure labels, 26 independent image stickers and 66 audio segments natively.
5. Exporting the two short Roman costume groups and custom flame shader through `--fx-solo main:<layer-id> --format prores`, as separate transparent overlays.
6. Building a ProRes foreground speaker cutout from the graded picture plus the original luma matte; placing it above historical stickers and below foreground graphics/text. A consumed matte layer must not also be rendered as a visible grayscale video.

This is one fidelity-preserving strategy, not a mandatory bake-everything workflow. Prefer native CapCut cuts/speeds/effects when their behavior can be represented and verified. Explain which elements remain individually editable; the Roman shapes and custom shader parameters inside an overlay were not native vector/effect controls.

## Alpha interoperability

ProRes 4444 pixel format and alpha extrema alone did not prove correct compositing. The flame asset had a maximum alpha near 0.28 but appeared much too bright in the first CapCut export. Premultiplying RGB before encoding corrected this **specific asset/export path**:

```sh
ffmpeg -i /absolute/flames-straight.mov \
  -vf 'format=gbrap,premultiply=inplace=1,format=yuva444p10le' \
  -an -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le \
  /absolute/flames-premultiplied.mov
```

Keep the original and compare an actual CapCut composite over real footage. Do not blindly premultiply all PNGs/ProRes or apply it twice; other import paths may use straight alpha correctly. Distinguish opacity, color/gamma differences, decoder interpretation and edge halos. Background RGB in transparent areas and luma-matte scale/interpolation also affect results.

A full 59.8-second 2160 by 3840 speaker cutout reached approximately 18.9 GB. Plan storage and use only the necessary time windows/resolution where fidelity permits; keep referenced assets in persistent locations after delivery.

## Text and curve findings

The original builder's claim that CapCut font units always equal 6.25 source pixels was too broad. Preserve the **final corrections**:

- Metropolis size 50 to CapCut size 8 was a starting match; normal/title text center was then shifted up by 15 composition pixels for this edit.
- NType size 250 initially mapped to 40, then needed a 0.875 multiplier (35) and `line_max_width: 2.0` to avoid unintended ANCIENT/RISE AGAIN wraps.
- Rich-style shadow diffuse needed reduction to 0.045 for normal text and 0.015 for NType. Neither value is a universal blur conversion.
- Preserve explicit two-line text such as SATIRE / WRITER. Use the real NType OTF and synthetic bold/italic fields rather than substituting another serif font. The tested NType style used rich-style `bold: true`, `italic: true`, material `bold_width` approximately 0.008 and `italic_degree: 10`; its same-colored Tesseract emboldening stroke was not a black CapCut border.

The tested conversion sampled short entrance Bezier curves approximately every 16 ms into linear native keyframes, retaining source knots and endpoints. Audio gain scripts were sampled every 10 ms, with collinear runs removed. Use sampling appropriate to the curve rather than treating these intervals as fixed requirements. Sample short entrance Bezier curves into linear native keyframes if the native easing graph is unknown. For scripted audio gains, evaluate only trusted/authored source scripts in an appropriate sandbox, sample their envelope, retain nonlinear ramps and fade corners, and map edit-local sample times to source-relative offsets. The historical migration used Node `new Function` on its own authored code; do not run arbitrary code from an untrusted project as a generic parsing step.

## Verification evidence

The finalized CapCut export was H.264/AAC, 2160 by 3840, 30 fps, 59.8 seconds and 1,794 frames, with full decode passing. Its measured mix was -19.30 LUFS / -1.11 dBTP versus the Tesseract export's -19.43 LUFS / -1.09 dBTP. Representative corrected frames were inspected; pixel identity and subjective audio audition were not claimed. These values establish that one conversion worked, not targets to apply to future videos.

## Local case-study provenance

The completed conversion had 46 tracks, 221 segments and 83 native text materials, with no missing media paths at final verification. Its first export exposed rotation sign, NType wrapping/size, normal-caption placement/shadow and flame-alpha differences. The reviewed export followed those corrections; an early builder alone is not the final specification.

Historical evidence files are optional context, not dependencies of the generic Desktop workflow:

- `/Users/johnamadeo/Desktop/content/chn8-capcut-rebuild/final-saved-draft.json`
- `/Users/johnamadeo/Desktop/content/chn8-capcut-rebuild/verification.json`
- `/Users/johnamadeo/Desktop/content/chn8-capcut-rebuild/capcut-corrected-filmstrip.jpg`
- `build_draft.py`, `apply_corrections.py` and `finalize_project.py` in that directory. The initial builder contains superseded rotation, typography and alpha assumptions; consult its corrections and final snapshot together.
