# traveller-save — Claude Skill Example

A working skill for Claude's skill system, packaged as a concrete example of how to structure a campaign file save workflow for a tabletop RPG campaign.

This skill is specific to a Mongoose Traveller 2e campaign set in the Foreven Sector. It is published here not as a general-purpose tool, but as a reference showing how skills can be structured to enforce multi-step workflows, pre/post-flight checks, and external validation scripts.

---

## What This Skill Does

Handles `/save_tsv`, `/save_context`, `/save_sectors`, and `/save_all` save commands for a Traveller campaign with three active data files:

- **TSV** — sector world data (UWPs, trade codes, allegiances)
- **`_context.md`** — active campaign state (arc, NPCs, GM secrets, session notes)
- **`_sectors.md`** — worldbuilding reference (subsector logs, polity profiles, house rules)

Each save command follows a three-phase structure: **pre-flight → execute → post-flight**.

---

## Files

```
traveller-save/
├── SKILL.md                        # Skill definition — read by Claude before executing save commands
└── scripts/
    └── validate_sections.py        # Validation script — checks required sections are present in output files
```

---

## How Claude Skills Work (Brief Overview)

A skill is a markdown file (`SKILL.md`) that Claude reads before executing a category of task. The skill description in the project instructions triggers Claude to load and follow the skill's content rather than improvise the workflow from memory.

The skill system allows:
- Enforcing consistent multi-step procedures
- Shipping supporting assets (scripts, templates) alongside the skill definition
- Separating "how to do this task" from the main system prompt

In this campaign, the skill is stored at `/mnt/skills/user/traveller-save/SKILL.md` and is triggered by the description in the project instructions whenever a save command is issued.

---

## Structural Patterns Worth Noting

### Three-phase enforcement
Every save command — regardless of which file type — runs the same pre-flight, execute, post-flight loop. This makes it hard to accidentally skip steps like duplicate checking or post-save reminders.

### Validation as a separate script
`validate_sections.py` is staged from the skill directory to `/home/claude/scripts/` at the start of every save. This keeps the validation logic version-controlled alongside the skill, and gives Claude a clear pass/fail signal it can act on (stop and report) rather than making a judgment call.

### Timestamp freshness rule
The skill explicitly forbids reusing timestamps from earlier in the session and specifies how to generate a fresh one (`TZ='America/Los_Angeles' date '+%Y%m%d_%H%M'`). This was added to fix a real failure mode where carried timestamps caused file versioning confusion.

### Hard stops on ambiguity
Duplicate detection, missing Pending TSV Changes list, and validation failures all result in an explicit stop-and-report rather than a best-effort continuation. The cost of a wrong save is higher than the cost of a pause to confirm.

### Source baseline discipline
The skill specifies that the working baseline must always be copied from `/mnt/project/` (the session-start snapshot), never from a prior output file. This prevents a class of errors where edits compound incorrectly across saves.

---

## Campaign Context

The campaign this skill supports:
- **System:** Mongoose Traveller 2e
- **Setting:** Foreven Sector, Milieu 1100
- **Group:** REACT (Recognised Non-Combatant Company), operating a converted Zhodani fat trader as a humanitarian NGO
- **Files managed:** one TSV (sector data) + two markdown files (campaign state + worldbuilding reference)

The campaign file structure, naming conventions, and session management workflow are defined in the project's system prompt, which the skill references but does not duplicate.

---

## Licence

MIT. Use freely, adapt to your own campaign or workflow structure.
