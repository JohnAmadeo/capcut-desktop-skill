---
name: capcut-desktop
description: Inspect, create, repair, and edit local CapCut Desktop timelines programmatically through draft JSON, with native-editor export verification. Use for bulk clips, captions, images, keyframes, audio, project recovery, or project-format conversions. Targets local Desktop projects rather than CapCut cloud drafts or template search.
---

# CapCut Desktop

Use local draft JSON for bulk timeline work, and the Desktop editor to create a compatible blank project, resolve media links, inspect playback, and export. This is a reverse-engineered workflow, not an official CapCut API. The bundled examples were exercised on macOS CapCut **8.9.0**, draft version **360000**, `new_version` **175.0.0**, on 2026-10-27. Revalidate against a blank draft and a small representative edit on a different version.

## Choose the operation

- Read [schema.md](references/schema.md) before constructing or changing timeline JSON. Reuse the complete sanitized [8.9.0 templates](assets/schema-8.9.0/) rather than inventing all the auxiliary fields.
- Read [project-files.md](references/project-files.md) before creating, saving, cloning, renaming, installing, or recovering a project. The active timeline can have several on-disk mirrors and a separate browser index.
- Read [desktop-ui.md](references/desktop-ui.md) when operating the app, relinking media, or exporting. Floating windows can misdirect automation.
- Read [tesseract-to-capcut.md](references/tesseract-to-capcut.md) for that migration. It includes corrected transform mappings, specialty renders, and typography calibration findings.
- Read [evidence.md](references/evidence.md) when deciding whether a field or workaround was actually verified.

## Work from a compatible project

1. Locate the intended draft and installed app version. Inspect it with `python3 scripts/draft_tools.py inspect /absolute/path/draft_info.json`.
2. For a new project, create and save a blank through Desktop once. Snapshot it and use its project/timeline IDs, platform fields, default materials collections, and sidecars. For an existing project, snapshot the complete folder and the relevant root-index entry before editing.
3. Close the target editor before writing its files. The app caches projects and auto-saves; an external write to an open timeline can be overwritten. Save backups outside the project-browser root. Do not restart/force-quit an app merely because an automation snapshot is blank.
4. Build the candidate JSON in the task workspace. Clone matching known-good structures; preserve unknown fields. Generate new IDs for new objects and update every reference. Use absolute, persistent media/font paths. Separate dialogue, music and SFX; preserve source selection and speed independently of timeline placement.
5. Validate with `python3 scripts/draft_tools.py validate candidate.json`. This catches broken references, missing media/fonts, malformed rich text and ranges; it cannot prove that CapCut will render correctly.
6. Write the active draft mirrors described in [project-files.md](references/project-files.md), then reopen in Desktop. Resolve link prompts and read back the app-saved JSON: CapCut may normalize materials and IDs.
7. Export from CapCut and compare representative frames, cut boundaries, animation peaks, typography, layering and audio. Run full decode, duration/fps/dimensions and peak/loudness checks as appropriate. Keep a readable filmstrip. State any unavailable subjective audio review.

Report the actual project name/path and verification status. Explicitly distinguish native editable elements from rendered effect assets. A JSON file passing validation, a successful open, and a verified final export are different milestones. Do not claim pixel identity across renderers without evidence.

When explaining how a feature was applied, state the actual method: Desktop UI actions (accessibility controls or screenshot-based clicks), saved-project JSON changes, reuse of existing CapCut-generated results, or a rendered substitute. For example, say “I edited the project JSON to reuse cutout results CapCut had already generated for the same footage” when that is what happened; say “I clicked Auto removal and waited for CapCut to process the footage” only when processing was actually triggered. Reused native results can still use CapCut’s native Remove BG, but do not describe reuse as a fresh processing run or imply that setting JSON fields generated the masks. Report UI checks and export verification separately from the method used to create or reuse the effect.

## Reusable helpers

`scripts/draft_tools.py` uses the Python standard library and never writes into a live CapCut project:

```sh
python3 scripts/draft_tools.py inspect /absolute/project/draft_info.json
python3 scripts/draft_tools.py validate /absolute/work/candidate.json
python3 scripts/draft_tools.py templates /absolute/project/draft_info.json --output /absolute/work/new-template-folder
```

`templates` creates a fresh folder of sanitized draft/material/segment/keyframe examples from that installed version. Prefer these fresh examples when the bundled version differs. The extraction scrubs paths, hardware identifiers and source wording; IDs and reference relationships inside separate templates still require intentional replacement.
