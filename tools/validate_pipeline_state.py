#!/usr/bin/env python3
"""Read-only process-state validator for a World Forge project folder.

The Pipeline State Ledger (top of Drafts/Master_Design.md) is written by the
same model that runs the phases, so a run that skipped a phase can also have
recorded it as done. This script is the deterministic backstop the DISPATCH
PROTOCOL (workflows/world-forge.md) promises: it re-checks the ledger's claims
against the artifacts actually on disk, without asking the model anything.

Checks, per ledger row that claims COMPLETE:

  1 Refiner            - Drafts/Master_Design.md contains "REFINER SIGN-OFF"
  2 Architect          - the seven mandatory Drafts/ output classes exist and
                         are non-empty (cards, User.md, protagonist + character
                         Tier 2 entries, Tier1_World_Entries.md, the
                         mode-appropriate Tier 3 file(s), Instructions files)
  2.5 Intimacy Arch.   - >=1 Tier2_*_Intimacy_Profile.md + the mode-appropriate
                         Tier 3 register; "INTIMACY ARCHITECT SIGN-OFF" present
                         in some Drafts/ file
  3 Editor             - Drafts/Editor_Critique_*.md exists; the latest round
                         contains "EDITOR SIGN-OFF"
  3.5 Voice Auditor    - Drafts/Voice_Audit_Report_*.md; latest round contains
                         "VOICE AUDITOR SIGN-OFF"
  3.6 Arc Transition   - Drafts/Arc_Transition_Audit_*.md; latest round contains
                         "ARC TRANSITION AUDITOR SIGN-OFF"
  3.7 Intimacy Auditor - Drafts/Intimacy_Audit_Report_*.md; latest round
                         contains "INTIMACY AUDITOR SIGN-OFF"
  4 Compiler           - Export/ populated + Export/Compiler_Log.md contains
                         "COMPILER SIGN-OFF"
  5 Prompt Engineer    - Export/Prompt_Engineer_Audit.md contains
                         "PROMPT ENGINEER SIGN-OFF"; a *ChatPreset.json exists

Cross-checks:

  - world_mode is arc or sandbox; the Tier 3 draft files match the mode
  - conditional skips are legal: 3.6 SKIPPED only in sandbox mode (and never
    COMPLETE in sandbox mode); 2.5/3.7 SKIPPED only when
    intimacy_in_scope: false
  - order: a later row COMPLETE while an earlier required row is neither
    COMPLETE nor SKIPPED is a failure
  - top-level status COMPLETE requires every row COMPLETE or SKIPPED
  - a loop Round above the escalation ceiling (3) without ESCALATED is a WARN
  - artifacts ahead of the ledger (e.g. Export/ populated while the Compiler
    row is PENDING) are a WARN (stale ledger), not a failure

If no ledger block is found (worlds built before the ledger existed), the
script degrades to a WARN-only artifact inventory so legacy projects can still
be examined without failing them wholesale.

Warnings (lines prefixed [WARN]) never change exit status; only failures do.

This script NEVER modifies files. It is the process-level sibling of
tools/validate_export.py (which checks Export/ content): validate_export.py
asks "is what was built well-formed?", this script asks "was everything that
claims to have run actually run?". The phase -> artifact -> anchor mapping must
stay in sync with the DISPATCH PROTOCOL table in workflows/world-forge.md and
the ledger schema's anchor column. Stdlib only; no dependencies. Explicitly
approved as the second sanctioned script (2026-07-30); do not extend it into
anything that modifies files.

Usage:
    python tools/validate_pipeline_state.py <project folder>

Exit status: 0 = all checks passed, 1 = at least one failure, 2 = usage error.
"""

import re
import sys
from pathlib import Path

LEDGER_HEADER = "PIPELINE STATE LEDGER"
ROUND_CEILING = 3

# Phase keys in pipeline order. Each row: (key, label, conditional-on).
PHASE_ORDER = ["1", "2", "2.5", "3", "3.5", "3.6", "3.7", "4", "5"]

STATUS_VALUES = {"PENDING", "IN_PROGRESS", "COMPLETE", "SKIPPED", "BLOCKED", "ESCALATED"}

# Ledger table rows are matched on the leading phase token of the first cell
# ("1 Refiner", "2.5 Intimacy Arch.", "3.6 Arc Transition", ...).
ROW_RE = re.compile(r"^\|\s*(\d+(?:\.\d+)?)\s+[^|]*\|\s*([A-Z_]+)[^|]*\|\s*([^|]*)\|")
FIELD_RE = re.compile(r"^-\s*(world_mode|intimacy_in_scope|current_phase|status)\s*:\s*(\S+)")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def non_empty(path):
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def latest_round(paths):
    """The file with the highest number in its name (round), else the newest name."""
    def round_of(p):
        numbers = re.findall(r"(\d+)", p.stem)
        return int(numbers[-1]) if numbers else 0
    return max(paths, key=lambda p: (round_of(p), p.name)) if paths else None


def parse_ledger(text):
    """Extract the ledger's top-level fields and phase-row statuses/rounds."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if LEDGER_HEADER in l), None)
    if start is None:
        return None
    fields = {}
    rows = {}
    for line in lines[start:start + 60]:
        stripped = line.strip()
        m = FIELD_RE.match(stripped)
        if m:
            fields[m.group(1)] = m.group(2).strip().rstrip(",")
            continue
        m = ROW_RE.match(stripped)
        if m:
            key, status, round_cell = m.group(1), m.group(2), m.group(3).strip()
            rows[key] = {"status": status, "round": round_cell}
    return {"fields": fields, "rows": rows}


def check_architect_outputs(drafts, mode, fail):
    """The seven mandatory Phase 2 output classes, per the drafting stage file."""
    classes = [
        ("Card_*.md", "character card drafts"),
        ("User.md", "the {{user}} persona description"),
        ("Tier1_World_Entries.md", "the Tier 1 world entries"),
        ("Tier2_*_Entries.md", "Tier 2 entry files (protagonist + characters)"),
        ("Instructions_*.md", "per-card LLM instruction drafts"),
    ]
    if mode == "sandbox":
        classes.append(("Tier3_Sandbox_Entries.md", "the sandbox Tier 3 lorebook"))
    else:
        classes.append(("Tier3_Arc*_Entries.md", "arc Tier 3 lorebooks"))
    for pattern, label in classes:
        matches = [p for p in drafts.glob(pattern) if p.is_file()]
        if not matches:
            fail(f"2 Architect claims COMPLETE but no {pattern} in Drafts/ ({label})")
            continue
        empties = [p.name for p in matches if not non_empty(p)]
        for name in empties:
            fail(f"2 Architect: Drafts/{name} exists but is empty (checkpoint rule 2 - the write never landed)")


def check_report_phase(drafts, pattern, anchor, phase_label, fail):
    """A loop/audit phase: report file(s) exist, latest round carries the anchor."""
    reports = sorted(p for p in drafts.glob(pattern) if p.is_file())
    if not reports:
        fail(f"{phase_label} claims COMPLETE but no Drafts/{pattern} report exists - "
             "the phase did not run; re-dispatch it (DISPATCH PROTOCOL rule 2)")
        return
    newest = latest_round(reports)
    text = read_text(newest) or ""
    if anchor not in text:
        fail(f"{phase_label}: latest report Drafts/{newest.name} does not contain "
             f"'{anchor}' - the phase ran but never signed off")


def check_round(key, row, warn):
    numbers = re.findall(r"\d+", row.get("round", ""))
    if numbers and int(numbers[0]) > ROUND_CEILING and row["status"] not in ("ESCALATED", "COMPLETE"):
        warn(f"{key}: Round {numbers[0]} exceeds the escalation ceiling ({ROUND_CEILING}) "
             "but the row is not ESCALATED - the round gate was not honored")


def validate(project, fail, warn):
    drafts = project / "Drafts"
    export = project / "Export"
    master = drafts / "Master_Design.md"

    master_text = read_text(master)
    if master_text is None:
        if non_empty(project / "World_Seed.md"):
            warn("no Drafts/Master_Design.md - project has not completed Phase 1; "
                 "nothing to validate yet")
        else:
            fail(f"{project} does not look like a World Forge project "
                 "(no Drafts/Master_Design.md and no World_Seed.md)")
        return

    ledger = parse_ledger(master_text)
    if ledger is None:
        warn("no Pipeline State Ledger found in Drafts/Master_Design.md (pre-ledger world?) - "
             "degrading to a WARN-only artifact inventory")
        inventory(drafts, export, master_text, warn)
        return

    fields, rows = ledger["fields"], ledger["rows"]

    mode = fields.get("world_mode", "")
    if mode not in ("arc", "sandbox"):
        fail(f"ledger world_mode {mode!r} is not 'arc' or 'sandbox' (never silently default a typo)")
        mode = "arc"
    intimacy = fields.get("intimacy_in_scope", "").lower()
    if intimacy not in ("true", "false"):
        warn(f"ledger intimacy_in_scope {intimacy!r} is not true/false")
    intimacy_in_scope = intimacy == "true"

    for key in PHASE_ORDER:
        if key not in rows:
            fail(f"ledger is missing the phase row for '{key}'")
    for key, row in rows.items():
        if row["status"] not in STATUS_VALUES:
            fail(f"ledger row {key}: unknown status {row['status']!r}")

    # Conditional-skip legality (both directions).
    r36 = rows.get("3.6", {}).get("status")
    if r36 == "SKIPPED" and mode != "sandbox":
        fail("3.6 Arc Transition is SKIPPED but world_mode is arc - "
             "the auditor is only skippable in sandbox mode")
    if r36 == "COMPLETE" and mode == "sandbox":
        fail("3.6 Arc Transition is COMPLETE in a sandbox world - "
             "there are no arc seams to audit; the ledger is incoherent")
    for key, label in (("2.5", "2.5 Intimacy Architect"), ("3.7", "3.7 Intimacy Auditor")):
        status = rows.get(key, {}).get("status")
        if status == "SKIPPED" and intimacy_in_scope:
            fail(f"{label} is SKIPPED but intimacy_in_scope is true - "
                 "conditional phases are skipped by their declared condition only")
        if status == "COMPLETE" and not intimacy_in_scope:
            warn(f"{label} is COMPLETE while intimacy_in_scope is false - "
                 "either the flag or the row is wrong")

    # Order: a later COMPLETE row over an earlier row that is neither COMPLETE nor SKIPPED.
    done_seen = [k for k in PHASE_ORDER if rows.get(k, {}).get("status") == "COMPLETE"]
    if done_seen:
        last_done = PHASE_ORDER.index(done_seen[-1])
        for key in PHASE_ORDER[:last_done]:
            status = rows.get(key, {}).get("status")
            if status not in ("COMPLETE", "SKIPPED"):
                fail(f"order violation: {done_seen[-1]} is COMPLETE while earlier phase "
                     f"{key} is {status} - a phase was skipped without being marked SKIPPED")

    # Top-level status coherence.
    if fields.get("status") == "COMPLETE":
        for key in PHASE_ORDER:
            status = rows.get(key, {}).get("status")
            if status not in ("COMPLETE", "SKIPPED"):
                fail(f"ledger status is COMPLETE but row {key} is {status}")

    # Per-row artifact gates (the point of this script).
    if rows.get("1", {}).get("status") == "COMPLETE":
        if "REFINER SIGN-OFF" not in master_text:
            fail("1 Refiner claims COMPLETE but Drafts/Master_Design.md has no 'REFINER SIGN-OFF'")

    if rows.get("2", {}).get("status") == "COMPLETE":
        check_architect_outputs(drafts, mode, fail)

    if rows.get("2.5", {}).get("status") == "COMPLETE":
        profiles = [p for p in drafts.glob("Tier2_*_Intimacy_Profile.md") if non_empty(p)]
        if not profiles:
            fail("2.5 Intimacy Architect claims COMPLETE but no non-empty "
                 "Drafts/Tier2_*_Intimacy_Profile.md exists")
        register_glob = ("Tier3_Sandbox_Intimacy_Register.md" if mode == "sandbox"
                        else "Tier3_Arc*_Intimacy_Register.md")
        if not any(non_empty(p) for p in drafts.glob(register_glob)):
            fail(f"2.5 Intimacy Architect claims COMPLETE but no non-empty Drafts/{register_glob} exists")
        anchored = any("INTIMACY ARCHITECT SIGN-OFF" in (read_text(p) or "")
                       for p in drafts.glob("*.md"))
        if not anchored:
            fail("2.5 Intimacy Architect claims COMPLETE but no Drafts/ file contains "
                 "'INTIMACY ARCHITECT SIGN-OFF' (it is appended to the final output file)")

    report_phases = (
        ("3", "Editor_Critique_*.md", "EDITOR SIGN-OFF", "3 Editor"),
        ("3.5", "Voice_Audit_Report_*.md", "VOICE AUDITOR SIGN-OFF", "3.5 Voice Auditor"),
        ("3.6", "Arc_Transition_Audit_*.md", "ARC TRANSITION AUDITOR SIGN-OFF", "3.6 Arc Transition Auditor"),
        ("3.7", "Intimacy_Audit_Report_*.md", "INTIMACY AUDITOR SIGN-OFF", "3.7 Intimacy Auditor"),
    )
    for key, pattern, anchor, label in report_phases:
        row = rows.get(key, {})
        if row.get("status") == "COMPLETE":
            check_report_phase(drafts, pattern, anchor, label, fail)
        check_round(label, row, warn)

    if rows.get("4", {}).get("status") == "COMPLETE":
        if not any(export.glob("*.json")):
            fail("4 Compiler claims COMPLETE but Export/ has no .json files")
        log_text = read_text(export / "Compiler_Log.md")
        if log_text is None:
            fail("4 Compiler claims COMPLETE but Export/Compiler_Log.md does not exist")
        elif "COMPILER SIGN-OFF" not in log_text:
            fail("4 Compiler: Export/Compiler_Log.md has no 'COMPILER SIGN-OFF'")

    if rows.get("5", {}).get("status") == "COMPLETE":
        audit_text = read_text(export / "Prompt_Engineer_Audit.md")
        if audit_text is None:
            fail("5 Prompt Engineer claims COMPLETE but Export/Prompt_Engineer_Audit.md does not exist")
        elif "PROMPT ENGINEER SIGN-OFF" not in audit_text:
            fail("5 Prompt Engineer: Export/Prompt_Engineer_Audit.md has no 'PROMPT ENGINEER SIGN-OFF'")
        if not any(export.glob("*ChatPreset.json")):
            fail("5 Prompt Engineer claims COMPLETE but no Export/*ChatPreset.json exists")

    # Artifacts ahead of the ledger: a stale ledger is a WARN, not a failure -
    # the artifact is the truth, but the ledger should be brought current.
    if rows.get("4", {}).get("status") in ("PENDING", None) and any(export.glob("*.json")):
        warn("Export/ contains .json files but the ledger's Compiler row is PENDING - "
             "stale ledger? bring it current from the artifacts")

    # Tier 3 drafts vs. mode.
    if mode == "sandbox" and any(drafts.glob("Tier3_Arc*_Entries.md")):
        warn("world_mode is sandbox but Drafts/ contains Tier3_Arc*_Entries.md - "
             "arc machinery in a sandbox world (or a stale mode flag)")
    if mode == "arc" and any(drafts.glob("Tier3_Sandbox_Entries.md")):
        warn("world_mode is arc but Drafts/ contains Tier3_Sandbox_Entries.md - "
             "sandbox machinery in an arc world (or a stale mode flag)")


def inventory(drafts, export, master_text, warn):
    """Ledger-less fallback: report what the artifacts alone show, WARN-only."""
    if "REFINER SIGN-OFF" not in master_text:
        warn("Drafts/Master_Design.md has no 'REFINER SIGN-OFF'")
    expectations = (
        ("Editor_Critique_*.md", "Editor critique"),
        ("Voice_Audit_Report_*.md", "Voice Audit report"),
        ("Arc_Transition_Audit_*.md", "Arc Transition audit"),
        ("Intimacy_Audit_Report_*.md", "Intimacy Audit report"),
    )
    exported = any(export.glob("*.json"))
    for pattern, label in expectations:
        if exported and not any(drafts.glob(pattern)):
            warn(f"Export/ is populated but Drafts/ has no {label} ({pattern}) - "
                 "if this world was built after the auditors existed, an audit phase was skipped")


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    project = Path(argv[1])
    if not project.is_dir():
        print(f"error: {project} is not a directory")
        return 2

    failures = []
    warnings = []
    validate(project, failures.append, warnings.append)

    status = "PASS" if not failures else "FAIL"
    print(f"[{status}] {project}")
    for message in failures:
        print(f"       - {message}")
    for message in warnings:
        print(f"       [WARN] {message}")
    print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        sys.stderr.close()
        sys.exit(1)
