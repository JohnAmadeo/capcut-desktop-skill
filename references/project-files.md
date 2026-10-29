# Local project files and persistence

## Locate and identify

Observed macOS root:
`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`

Each visible project has a folder containing `draft_meta_info.json`, `draft_info.json`, and sidecars. `root_meta_info.json` in the parent contains `all_draft_store`, `draft_ids`, and `root_path`. Do not assume Windows uses this path; discover its actual configured root. Do not guess a target from its name alone when multiple copies exist.

Three identifiers are distinct:

- `draft_meta_info.json.draft_id`: browser/project identity.
- `draft_info.json.id`: active timeline identity.
- `Timelines/project.json.id`: timeline-container identity; its `main_timeline_id` selects the main timeline.

On the observed version, a new blank created through the UI supplied compatible identity and sidecar files. Copying only `draft_info.json` is not a complete new-project creation workflow.

## File roles

| File | Observed role |
| --- | --- |
| `draft_info.json` | Top-level timeline document |
| `draft_info.json.bak`, `template-2.tmp` | Timeline mirrors present in the exercised project |
| `Timelines/project.json` | Main timeline ID and timeline list |
| `Timelines/<timeline-id>/draft_info.json` | Timeline-local document |
| Same directory's `.bak`, `template-2.tmp` | Additional exercised mirrors |
| `draft_meta_info.json` | Name, folder/root paths, project ID, media-bin records, times and duration |
| Parent `root_meta_info.json` | Project-browser index; not the timeline itself |
| `draft_cover.jpg` | Browser cover only; replacing it does not replace the timeline |
| `Resources`, `matting`, attachments, settings and caches | Preserve when cloning existing effects/projects; not all dependencies are plain media files |

The successful rebuild wrote the same candidate JSON into **six existing files**: top-level `draft_info.json`, its `.bak`, `template-2.tmp`, and the corresponding three files under `Timelines/<timeline-id>/`. This was a successful save recipe, not proof that all six are mandatory on every version. `template.tmp` also existed; it was not required to load and export the test project. For multi-timeline projects, resolve the selected timeline rather than copying one document over every timeline.

## Controlled write workflow

- Close the target editor and snapshot the entire target folder plus root index. Do not put a backup folder into the draft root: it can become another browser project.
- Validate an offline candidate. Update known existing mirrors sequentially with temporary-file plus replace where practical. A single-file atomic replace is not a multi-file transaction; keep the recovery snapshot until successful reopen/export.
- Preserve IDs for an in-place edit. For a new blank, preserve its project/timeline/container identities and allocate IDs for the new content. Full clones need intentional re-identification; do not globally replace every UUID indiscriminately.
- Do not modify `crypto_key_store.dat` or attempt to bypass protected/encrypted draft formats. If a newer version no longer exposes plaintext JSON, use a supported app workflow and report the format limitation.
- Reopen, let CapCut save, then inspect the saved document. The observed app expanded shared materials into per-segment entries, often repeating identical records with the same ID. Material counts/IDs can change while visible behavior stays the same. Do not restore an older candidate over a newer app-saved edit.

## Media bin and relinking

Timeline material entries and browser media-bin entries are separate. `draft_meta_info.json.draft_materials` is a list of `{type, value}` groups. The exercised local media group was type `0`. Its records included:

```json
{"id":"<local-material-id>","file_Path":"/absolute/media/clip.mp4","extra_info":"clip.mp4","metetype":"video","type":0,"width":1080,"height":1920,"duration":59800000,"roughcut_time_range":{"start":0,"duration":59800000},"sub_time_range":{"start":-1,"duration":-1},"item_source":1,"import_time":1790000000,"import_time_ms":1790000000000000,"create_time":1790000000}
```

`file_Path` has a capital `P`. The matching timeline material uses `local_material_id`. Observed `metetype` values were `video`, `photo`, and `music`. Clone a current record and use probed metadata instead of fabricating timestamps, sizes or durations.

A first open reported missing media despite all absolute files existing. The exact cause was not established; do not assert an OS-permission or bookmark diagnosis. Choosing the common directory alone did not visibly resolve it. Selecting the exact first missing file in Link media completed recovery; CapCut then loaded all timeline paths and later populated the media bin. Prefer a representative exact-file relink, with the folder-link option enabled, then check the remaining list and saved paths.

## Rename and index cache

`draft_info.json.name` alone did not update the Desktop title: it continued showing `1027`. The browser cached metadata and could overwrite externally changed index/name fields.

The final offline rename moved the folder and updated:

- `draft_meta_info.json`: `draft_name`, `draft_fold_path`, `draft_need_rename_folder`, modified timestamp.
- The matching `root_meta_info.json.all_draft_store` entry: name, folder-related paths and modified timestamp, while preserving unrelated entries.
- Known text sidecars containing the old folder path, including timeline mirrors.

Prefer the UI rename when reliable. If renaming offline, stop concurrent target/index writes, use structural JSON updates, and verify the browser after restart/reopen. Avoid blindly replacing a short name throughout binary/cache files. The historical finalizer used textual replacement of a complete absolute old path in text sidecars; do not generalize that to arbitrary substrings. Inspect `draft_ids` as well for clones/removal—its semantics were not established by this run.
