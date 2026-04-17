#!/usr/bin/env python3
"""
validate_sections.py — Required section checker for Traveller campaign save files.

Usage:
    python validate_sections.py context <filepath>
    python validate_sections.py sectors <filepath>

Exits 0 on pass, 1 on failure. Prints a clear pass/fail report.
"""

import sys

# Required sections by file type.
# These are matched as substrings against lines starting with '#',
# so they survive minor header wording changes while staying exact enough
# to avoid false positives.

REQUIRED_CONTEXT = [
    "## Current Situation",
    "## Key NPCs",
    "## World Quick Reference",
    "## Design Decisions Log",
    "## GM-Only Knowledge",
    "## File & Session Management Notes",
]

REQUIRED_SECTORS = [
    "## House Rules & Generation Variants",
    "## Avalar Subsector",
    "## Offenhold Subsector",
    "## Urnian Subsector",
    "## Shivva Subsector",
    "## Subsector M",
    "## GM-Only Knowledge",
    "## File & Session Management Notes",
]

# Sections that must appear somewhere in the file (not necessarily as headers)
REQUIRED_CONTEXT_CONTENT = [
    "_sectors.md",   # pointer reference to sectors file must exist
]


def check_file(filepath, required_headers, required_content=None):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return False

    line_count = len(lines)
    header_lines = [l.rstrip() for l in lines if l.startswith("#")]
    all_text = "".join(lines)

    failures = []

    # Header checks
    for required in required_headers:
        matched = any(required in h for h in header_lines)
        if not matched:
            failures.append(f"MISSING SECTION: {required}")

    # Content checks
    if required_content:
        for token in required_content:
            if token not in all_text:
                failures.append(f"MISSING CONTENT: '{token}' not found anywhere in file")

    # Report
    print(f"File:       {filepath}")
    print(f"Lines:      {line_count}")
    print(f"Headers:    {len(header_lines)} total")
    print()

    if failures:
        print(f"RESULT: FAIL — {len(failures)} issue(s) found")
        for f in failures:
            print(f"  ✗ {f}")
        return False
    else:
        print(f"RESULT: PASS — all required sections present")
        for r in required_headers:
            print(f"  ✓ {r}")
        if required_content:
            for r in required_content:
                print(f"  ✓ content: '{r}'")
        return True


def main():
    if len(sys.argv) != 3:
        print("Usage: validate_sections.py [context|sectors] <filepath>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    filepath = sys.argv[2]

    if mode == "context":
        ok = check_file(filepath, REQUIRED_CONTEXT, REQUIRED_CONTEXT_CONTENT)
    elif mode == "sectors":
        ok = check_file(filepath, REQUIRED_SECTORS)
    else:
        print(f"Unknown mode: {mode}. Use 'context' or 'sectors'.")
        sys.exit(1)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
