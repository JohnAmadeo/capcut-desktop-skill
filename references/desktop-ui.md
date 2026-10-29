# Desktop control, media linking and export

Use the available native computer-use tool for UI actions. The local draft workflow does not require CapCut's cloud plugin, login recovery or a cloud-draft handoff. Do not let cloud-plugin instructions silently replace a user's Desktop target.

## Control methods

In the exercised `cua_repl` API:

```javascript
let app = await cua.getApp("CapCut");
await app.getAXState();
// After identifying a current element index:
await app.click(exportButtonIndex);
await app.getAXState();
// Use a current screenshot when accessibility controls are incomplete:
await app.getScreenshot();
await app.click([x, y]);
await app.getAXState();
```

Read the current tool's documentation; API availability and coordinate conventions belong to that tool. Do not assume screenshot pixels, macOS screen points and window-relative coordinates are interchangeable. Named AX elements included `MainWindowTitleBarExportBtn`, `ExportOkBtn`, `automationbackupCheckBox` and `ExportFileNameInput`. Element indices become stale after window/selection changes.

macOS file pickers exposed proper path fields. The successful flow used `super+shift+g`, set the resulting `PathTextField`, Return, then the current Open button. CapCut's inline filename field sometimes needed screenshot-coordinate focus, select-all and typing.

## Avoid the floating-window trap

The tool sometimes selected a tiny untitled **EditPilot** floating window instead of the main editor/export sheet. Symptoms included:

- An empty `dialog`, disabled menu items, or a screenshot containing only the EditPilot button.
- `noWindowsAvailable` on coordinate actions while a user screenshot showed the main export dialog ready.
- A button click reporting no immediate AX change, even though a render later appeared on disk.

A blank automation tree is not evidence that CapCut itself is frozen. Refresh the app binding and AX state, inspect the window screenshot/title, and check the intended output file before retrying Export. Avoid repeated clicks on an unverified project-browser aggregate: an extra project copy was accidentally created during this control issue.

Do not use force-quit/restart as the first response. It can disrupt a healthy editor/export, and normal quit can be blocked by an open export sheet. If the control tool cannot identify the intended dialog after a fresh binding, ask the user for one specific click or to bring that dialog forward, then resume verification. Do not repeatedly ask the user for the same action after it has completed.

Selecting by bundle ID was ambiguous because both `/Applications/CapCut.app` and an embedded app shared it. A full app path removed identifier ambiguity but did not by itself fix the floating-window selection problem. `cua.listWindows` and `cua.computer.launch_app` were unavailable in that macOS tool session; do not assume optional APIs exist or rediscover them repeatedly.

## Export checklist

- Confirm destination/filename, dimensions, fps, codec, color space and intended duration.
- The example exported 4K, Higher bitrate, H.264, MP4, 30 fps, Rec.709 SDR.
- The export sheet's **Sync exported videos to space** checkbox was initially on. Turn it off for a local-only deliverable unless cloud sync is requested; do not accidentally upload during a Desktop task.
- Export completion opens a share screen. A local export is complete without pressing Share or signing in to TikTok/YouTube. Close/cancel that share screen, rather than publishing.
- Check the actual file with ffprobe and full decode, not just a progress UI. Do not repeatedly export while a completed file already exists.
- Capture and inspect representative frames against the source. Validate text wrapping, layer order, sticker scale/rotation, alpha edges, entrance/end holds and audio cues.

Useful commands:

```sh
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration,nb_frames -of json /absolute/final.mp4
ffmpeg -v error -i /absolute/final.mp4 -f null -
```

Audio loudness/peaks and decoding do not substitute for subjective listening. State if listening was unavailable.
