#!/usr/bin/env python3
"""Documentation-drift instrument (advisory) -- the project's DOC_AUDIT_COMMAND.

Usage:  python3 tools/check_docs.py

Compares what the user-facing Markdown describes against what the driver
source actually contains. Spec: ~/.claude/skills/sprint-plan/references/
doc-audit-instruments.md. Findings, one per line, grouped by type:

  ORPHAN     a doc names a .spin2 file, an object method (`obj.method(`)
             or an object constant (`obj.NAME`) the source does not have.
             Released upgrade checklists (files named Checklist-v*.md) are
             exempt: they show the old calls and settings of the version
             being left, by design, so those names are not drift.
  DUPLICATE  the same fenced code block is maintained in more than one doc
  COUNT      a number or roster the docs assert disagrees with its source
             (named driver chips in hwEnums vs README; DISPn adapter
             groups in hwPanelConfig vs README's adapter count)

Advisory by design: exit 0 whenever it ran, whatever it found; 2 only when
it could not run. Never wire it in as a build gate.

The document set is every tracked *.md minus the working areas, history
and agent files named in EXCLUDED_PREFIXES / EXCLUDED_FILES -- coverage is
derived, never opt-in.
"""

import hashlib
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_DIR = os.path.join(REPO_ROOT, "driver")

# Working areas and intent documents: plans, policy, analyses and triage
# say what should be, never what is, so they are not evidence and not audited.
EXCLUDED_PREFIXES = ("DOCs/plans/", "DOCs/policy/", ".github/")
EXCLUDED_FILES = {
    "ChangeLog.md",                   # history: names files as they were
    "Checklist-v1-v2.md",             # migration between two retired versions
    "HUB75-Driver-SWver0.md",         # describes the retired v0 driver
    "DOCs/CodeAssessment.md",         # analysis
    "DOCs/LOGIC-BUG-ANALYSIS.md",     # analysis
    "DOCs/MAGIC-NUMBER-TRIAGE.md",    # triage record
    "DOCs/TECHNICAL_DEBT.md",         # analysis
    "DOCs/FutureDirections-ImageAndColor.md",  # intent
    "DOCs/PSRAMExpansion.md",         # intent
    "CLAUDE.md",                      # agent configuration, not user-facing
}

# Chip enum entries that are not a named, supported driver chip.
NON_CHIP_ENUMS = ("CHIP_UNKNOWN", "CHIP_MANUAL_SPEC", "CHIP_UNK_")

# Not preceded by a URL/domain character: `ironsheepproductionsllc.spin2`
# in a marketplace badge URL is an extension id, not a file.
SPIN2_FILE = re.compile(r"(?<![/.\w-])([A-Za-z0-9_\\]+\.spin2)\b")
# How-to examples name a hypothetical constant or method on purpose.
PLACEHOLDER = re.compile(r"(^|_)(NEW|YOUR|MY|EXAMPLE)(_|$)")
PLACEHOLDER_METHODS = {"method", "foo", "bar"}
# An upgrade checklist (Checklist-v<from>-v<to>.md) documents the API of the
# version being left: its old files, methods and constants no longer exist in
# the source on purpose. Such files are exempt from ORPHAN checking (they are
# still checked for DUPLICATE and COUNT).
UPGRADE_CHECKLIST = re.compile(r"^Checklist-v[\w.-]*\.md$")
OBJECT_METHOD = re.compile(r"\b([a-z][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\(")
OBJECT_CONSTANT = re.compile(r"\b([a-z][A-Za-z0-9_]*)\.([A-Z][A-Z0-9_]{2,})\b")
CODE_SPAN = re.compile(r"`([^`]+)`")
FENCE = re.compile(r"^\s*```")
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
ADAPTER_CLAIM = re.compile(r"\b(\d+|%s)\s+(?:HUB75\s+)?adapter" % "|".join(NUMBER_WORDS),
                           re.IGNORECASE)
# Duplicate blocks shorter than this many non-blank lines are boilerplate
# (the three-line author sign-off closing most docs is deliberate).
DUPLICATE_MIN_LINES = 4

def tracked(pattern):
    try:
        return subprocess.run(["git", "-C", REPO_ROOT, "ls-files", pattern],
                              check=True, capture_output=True, text=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return []


def document_set():
    return sorted(path for path in tracked("*.md")
                  if path not in EXCLUDED_FILES and not path.startswith(EXCLUDED_PREFIXES))


def source_inventory():
    """Names the source really has: files, PUB methods, CON-style names."""
    files = {name.lower() for name in os.listdir(DRIVER_DIR) if name.endswith(".spin2")}
    methods = set()
    constants = set()
    sources = {}
    for name in sorted(files):
        with open(os.path.join(DRIVER_DIR, name), encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        sources[name] = text
        methods.update(match.lower() for match in
                       re.findall(r"^PUB\s+([A-Za-z_]\w*)", text, re.MULTILINE | re.IGNORECASE))
        constants.update(match.upper() for match in re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", text))
    return files, methods, constants, sources


def code_fragments(lines):
    """Yield (lineno, text) for code: fenced lines and inline `spans`."""
    in_fence = False
    for lineno, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            yield lineno, line
        else:
            for span in CODE_SPAN.findall(line):
                yield lineno, span


def fenced_blocks(lines):
    """Yield (start_lineno, normalized_text) for each fenced block."""
    block = None
    for lineno, line in enumerate(lines, start=1):
        if FENCE.match(line):
            if block is None:
                block = (lineno, [])
            else:
                body = [text.strip() for text in block[1] if text.strip()]
                if len(body) >= DUPLICATE_MIN_LINES:
                    yield block[0], "\n".join(body)
                block = None
            continue
        if block is not None:
            block[1].append(line)


def check_orphans(path, lines, inventory, findings):
    files, methods, constants, _ = inventory
    if UPGRADE_CHECKLIST.match(os.path.basename(path)):
        return                        # documents the old API on purpose
    for lineno, line in enumerate(lines, start=1):
        for name in SPIN2_FILE.findall(line):
            plain = name.replace("\\", "")
            if plain.lower() not in files:
                findings.append(("ORPHAN", path, lineno, "file %s does not exist in driver/" % plain))
    for lineno, fragment in code_fragments(lines):
        for _, method in OBJECT_METHOD.findall(fragment):
            if method.lower() not in methods and method not in PLACEHOLDER_METHODS:
                findings.append(("ORPHAN", path, lineno, "no PUB method %s()" % method))
        # Only object-qualified names (`hwEnum.NAME`): bare ALL_CAPS tokens in
        # these docs are mostly HUB75 signal names, not constants.
        for _, constant in OBJECT_CONSTANT.findall(fragment):
            if constant not in constants and not PLACEHOLDER.search(constant):
                findings.append(("ORPHAN", path, lineno, "no constant %s" % constant))


def check_counts(documents, inventory, findings):
    sources = inventory[3]
    enums = sources.get("isp_hub75_hwenums.spin2", "")
    declared = re.findall(r"#0\s*,(.*?)(?:\n\s*\n|$)", enums, re.DOTALL)
    chips = []
    if declared:
        chips = [name for name in re.findall(r"\bCHIP_\w+", declared[0])
                 if not name.startswith(NON_CHIP_ENUMS)]
    readme_path = "README.md"
    if readme_path in documents:
        readme = documents[readme_path]
        for chip in chips:
            if chip[len("CHIP_"):] not in readme:
                findings.append(("COUNT", readme_path, 0,
                                 "driver chip %s (hwEnums) is not named in README" % chip))
        adapters = len(set(re.findall(r"\bDISP(\d+)_", sources.get("isp_hub75_hwpanelconfig.spin2", ""))))
        for lineno, line in enumerate(readme.split("\n"), start=1):
            for claim in ADAPTER_CLAIM.findall(line):
                value = NUMBER_WORDS.get(claim.lower(), None) or int(claim)
                if adapters and value not in (1, adapters):
                    findings.append(("COUNT", readme_path, lineno,
                                     "claims %s adapters; hwPanelConfig defines %d DISPn groups"
                                     % (claim, adapters)))


def check_duplicates(documents, findings):
    seen = {}
    for path, text in documents.items():
        for lineno, body in fenced_blocks(text.split("\n")):
            seen.setdefault(hashlib.sha1(body.encode()).hexdigest(), []).append((path, lineno))
    for places in seen.values():
        if len({path for path, _ in places}) > 1:
            first_path, first_line = places[0]
            others = ", ".join("%s:%d" % place for place in places[1:])
            findings.append(("DUPLICATE", first_path, first_line, "same block also at " + others))


def main():
    paths = document_set()
    if not paths:
        print("check_docs: no tracked Markdown found (not a git checkout?)", file=sys.stderr)
        return 2
    inventory = source_inventory()
    documents = {}
    for path in paths:
        with open(os.path.join(REPO_ROOT, path), encoding="utf-8", errors="replace") as handle:
            documents[path] = handle.read()

    findings = []
    for path, text in documents.items():
        check_orphans(path, text.split("\n"), inventory, findings)
    check_duplicates(documents, findings)
    check_counts(documents, inventory, findings)

    print("Doc-drift audit (advisory) -- %d documents, %d .spin2 sources"
          % (len(documents), len(inventory[0])))
    for kind in ("ORPHAN", "DUPLICATE", "COUNT"):
        hits = [finding for finding in findings if finding[0] == kind]
        print()
        print("%s (%d)" % (kind, len(hits)))
        for _, path, lineno, detail in hits:
            print("  %s:%d  %s" % (path, lineno, detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
