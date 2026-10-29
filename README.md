# CapCut Desktop Skill

A Codex skill for inspecting, creating, repairing, and editing local CapCut Desktop timelines through draft JSON, with native-editor export verification.

Start with [SKILL.md](SKILL.md) for the workflow, requirements, and verification limits.

## Contents

- `references/`: timeline schema, project files, Desktop UI, migration guidance, and evidence.
- `assets/schema-8.9.0/`: sanitized examples from CapCut Desktop 8.9.0.
- `scripts/draft_tools.py`: Python standard-library helpers for inspection, validation, and template extraction.
- `agents/openai.yaml`: agent display metadata.

## Install

Clone this repository into your Codex skills directory:

```sh
git clone https://github.com/johnamadeo/capcut-desktop-skill.git ~/.codex/skills/capcut-desktop
```

## Helper usage

```sh
python3 scripts/draft_tools.py inspect /absolute/project/draft_info.json
python3 scripts/draft_tools.py validate /absolute/work/candidate.json
python3 scripts/draft_tools.py templates /absolute/project/draft_info.json --output /absolute/work/new-template-folder
```

This is a reverse-engineered workflow, not an official CapCut API. Revalidate templates against the installed CapCut version. JSON validation does not establish successful playback or export.
