---
name: traveller-save
description: >
  Handles all campaign file save operations for the Foreven Sector Traveller campaign.
  Use this skill whenever the user issues /save_tsv, /save_context, /save_sectors, or /save_all
  commands, or whenever any campaign file (TSV sector data, context markdown, or sectors markdown)
  needs to be written and presented for download. This skill enforces pre-flight checks, timestamp
  freshness, correct bash patterns, and single-version validation on every save. Always use
  this skill for save operations — do not rely on memory or improvise the workflow.
---

# Traveller Save Skill

Handles `/save_tsv`, `/save_context`, `/save_sectors`, and `/save_all` for the Foreven Sector campaign.
Each command follows the same three-phase structure: **Pre-flight → Execute → Post-flight**.

---

## File Reference

| File type | Naming pattern | Source baseline |
|---|---|---|
| Sector data | `myGame_foreven_YYYYMMDD_HHMM.tsv` | `/mnt/project/myGame_foreven_[timestamp].tsv` |
| Campaign state | `myGame_foreven_YYYYMMDD_HHMM_context.md` | `/mnt/project/myGame_foreven_[timestamp]_context.md` |
| Worldbuilding ref | `myGame_foreven_YYYYMMDD_HHMM_sectors.md` | `/mnt/project/myGame_foreven_[timestamp]_sectors.md` |

**Never** read from a prior output file in `/mnt/user-data/outputs/` as the working baseline.
Always copy from `/mnt/project/` — it is the authoritative session-start snapshot.

---

## Phase 1 — Pre-flight (all commands)

Run before any save operation:

### 1a. Stage the validation script
```bash
mkdir -p /home/claude/scripts
cp /mnt/skills/user/traveller-save/validate_sections.py /home/claude/scripts/validate_sections.py
```

### 1b. Identify current source files
```bash
ls /mnt/project/myGame_foreven_*.tsv
ls /mnt/project/myGame_foreven_*_context.md
ls /mnt/project/myGame_foreven_*_sectors.md
```

### 1c. Check for duplicates
A duplicate is two or more files of the same base type with different timestamps.
If any duplicate is found: **stop, report the conflict to Clyde, do not proceed.**
Wait for explicit instruction before resuming.

### 1d. Command-specific pre-flight

**`/save_tsv` only:**
- Check whether a **Pending TSV Changes** list exists in the current conversation.
- If it exists: confirm all listed changes will be applied.
- If it does not exist: **flag this to Clyde** — changes made this session may not be captured. Do not silently proceed.

**`/save_context` only:**
- Read the **entire** existing `_context.md` from `/mnt/project/` before writing.
- Use `grep -A 40` after section headers to retrieve full world entries if needed.

**`/save_sectors` only:**
- Read the **entire** existing `_sectors.md` from `/mnt/project/` before writing.

**`/save_all`:**
- Apply all of the above pre-flight checks for all three file types.
- Check for a Pending TSV Changes list and flag if absent.

---

## Phase 2 — Execute

### Timestamp rule
Generate a **fresh timestamp at the moment of execution** in UTC-7 (Pacific).
Format: `YYYYMMDD_HHMM`
**Never reuse or carry forward a timestamp from earlier in the session.**
Even if two saves happen minutes apart, each gets its own timestamp.
For `/save_all`, generate a **single shared timestamp** and use it for all three files.

Get current Pacific time:
```bash
TZ='America/Los_Angeles' date '+%Y%m%d_%H%M'
```

---

### `/save_tsv` execution

```bash
# 1. Get fresh timestamp
TS=$(TZ='America/Los_Angeles' date '+%Y%m%d_%H%M')

# 2. Copy baseline from project (never from outputs)
cp /mnt/project/myGame_foreven_[current_timestamp].tsv /home/claude/work.tsv

# 3. Apply all pending changes via sed -i substitutions
#    Hex values must be zero-padded to 4 digits before matching
#    Example:
#    sed -i 's/^Fore\tA\t0101\t.*/Fore\tA\t0101\tWorld Name\t.../' /home/claude/work.tsv

# 4. Write output
cp /home/claude/work.tsv /mnt/user-data/outputs/myGame_foreven_${TS}.tsv
```

Then call `present_files` with `/mnt/user-data/outputs/myGame_foreven_${TS}.tsv`.

**TSV technical notes:**
- Use `csv.DictReader` with `delimiter='\t'` for any Python-side parsing
- Hex strings: always `.zfill(4)` before slicing into 2-digit column + row components
- Subsector M bounds: `1 <= col <= 8 and 31 <= row <= 40`
- Grep subsector rows: `grep "	[SubsectorLetter]	"` with literal tabs

---

### `/save_context` execution

```bash
# 1. Get fresh timestamp
TS=$(TZ='America/Los_Angeles' date '+%Y%m%d_%H%M')

# 2. Copy existing context to working location
cp /mnt/project/myGame_foreven_[current_timestamp]_context.md /home/claude/context_work.md
```

Read the file in full. Then construct the new context file incorporating all session changes.
Use `str_replace` for targeted edits, or write the full file fresh if changes are extensive.

```bash
# 3. Write output
cp /home/claude/context_work.md /mnt/user-data/outputs/myGame_foreven_${TS}_context.md

# 4. Validate
python3 /home/claude/scripts/validate_sections.py context /mnt/user-data/outputs/myGame_foreven_${TS}_context.md
```

If the script exits non-zero: **stop, report the missing sections to Clyde, do not present the file.**

Then call `present_files` with the output path.

**`/save_context` does not update `_sectors.md`.** If worldbuilding data changed, prompt Clyde to also run `/save_sectors`.

---

### `/save_sectors` execution

```bash
# 1. Get fresh timestamp
TS=$(TZ='America/Los_Angeles' date '+%Y%m%d_%H%M')

# 2. Copy existing sectors file to working location
cp /mnt/project/myGame_foreven_[current_timestamp]_sectors.md /home/claude/sectors_work.md
```

Read the file in full. Then construct the new sectors file incorporating all session changes.

```bash
# 3. Write output
cp /home/claude/sectors_work.md /mnt/user-data/outputs/myGame_foreven_${TS}_sectors.md

# 4. Validate
python3 /home/claude/scripts/validate_sections.py sectors /mnt/user-data/outputs/myGame_foreven_${TS}_sectors.md
```

If the script exits non-zero: **stop, report the missing sections to Clyde, do not present the file.**

Then call `present_files` with the output path.

---

### `/save_all` execution

`/save_all` saves all three files unconditionally using a single shared timestamp.
Use this when forcing a fresh timestamp across all files regardless of whether content changed.

```bash
# 1. Get single shared timestamp for all three files
TS=$(TZ='America/Los_Angeles' date '+%Y%m%d_%H%M')

# 2. Copy all three baselines
cp /mnt/project/myGame_foreven_[current_timestamp].tsv /home/claude/work.tsv
cp /mnt/project/myGame_foreven_[current_timestamp]_context.md /home/claude/context_work.md
cp /mnt/project/myGame_foreven_[current_timestamp]_sectors.md /home/claude/sectors_work.md
```

Apply any pending TSV changes to `/home/claude/work.tsv` via `sed -i` substitutions.
Apply any session changes to context and sectors files via `str_replace` or full rewrite.

```bash
# 3. Write all three outputs
cp /home/claude/work.tsv /mnt/user-data/outputs/myGame_foreven_${TS}.tsv
cp /home/claude/context_work.md /mnt/user-data/outputs/myGame_foreven_${TS}_context.md
cp /home/claude/sectors_work.md /mnt/user-data/outputs/myGame_foreven_${TS}_sectors.md

# 4. Validate both markdown files
python3 /home/claude/scripts/validate_sections.py context /mnt/user-data/outputs/myGame_foreven_${TS}_context.md
python3 /home/claude/scripts/validate_sections.py sectors /mnt/user-data/outputs/myGame_foreven_${TS}_sectors.md
```

If either script exits non-zero: **stop, report the missing sections to Clyde, do not present any files.**

Then call `present_files` with all three output paths in a single call:
```
/mnt/user-data/outputs/myGame_foreven_${TS}.tsv
/mnt/user-data/outputs/myGame_foreven_${TS}_context.md
/mnt/user-data/outputs/myGame_foreven_${TS}_sectors.md
```

---

## Phase 3 — Post-flight (all commands)

After presenting the file(s) for download:

1. **Report what was saved** — filename(s) and timestamp.
2. **Remind Clyde** to:
   - Upload the new file(s) to project knowledge
   - Remove the old version of each updated file type from project knowledge
   - Confirm project knowledge contains exactly one current version of each file type
3. **If `/save_context` was run alone and worldbuilding changed this session:** prompt whether `/save_sectors` should also be run.
4. **If `/save_tsv` or `/save_all` was run:** clear the Pending TSV Changes list for this session.

---

## Common Failure Modes

| Failure | Symptom | Prevention |
|---|---|---|
| Stale baseline | Edits lost because prior output used as source | Always copy from `/mnt/project/` |
| Carried timestamp | Two files with same timestamp | Generate fresh `date` call each save |
| Shared timestamp skew | `/save_all` files have different timestamps | Generate TS once, reuse for all three |
| Script not found | `validate_sections.py` missing at runtime | Stage script in Phase 1 pre-flight |
| Validation failure | Required section missing from output | Read full source file before writing |
| Missing TSV changes | World edits not in saved TSV | Maintain Pending TSV Changes list; warn if absent |
| Duplicate versions | Two files of same type in project knowledge | Post-flight reminder; stop on pre-flight detection |
