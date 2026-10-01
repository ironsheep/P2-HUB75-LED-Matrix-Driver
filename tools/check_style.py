#!/usr/bin/env python3
"""Spin2 style gate -- the T1 tier of central:spin2-authoring-guide.

Usage:  python3 tools/check_style.py [file.spin2 ...]

With no arguments it checks every tracked driver/*.spin2 file.

Reports three things, as the guide's "Enforcement tiers" section requires:
  1. each implemented T1 rule, PASS or FAIL, with file:line findings
  2. the assigned-T1 rules this script does NOT implement yet
  3. the T1+T2 / T2 / T3 rules no script can settle (agent audit / Stephen)

Items 2 and 3 are derived from the tier marks on the central guide's
headings at run time, never restated here, so they track the guide.

Exit status: 0 = every implemented rule passes, 1 = at least one FAIL,
2 = usage or I/O error.
"""

import glob
import os
import re
import subprocess
import sys

GUIDE_PATH = os.path.expanduser("~/.claude/skills-docs/guides/spin2-authoring-guide.md")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Box-drawing (U+2500-U+257F) and block elements (U+2580-U+259F): the only
# non-ASCII the guide permits, anywhere in a file (rule 1.1).
BOX_DRAWING_FIRST = 0x2500
BOX_DRAWING_LAST = 0x259F
ASCII_LAST = 0x7F

# A comment made of nothing but a run of separator characters (rule 4.9).
SEPARATOR_MIN_RUN = 4
SEPARATOR_LINE = re.compile(r"^[-=_*#~+─-▟\s]{%d,}$" % SEPARATOR_MIN_RUN)

BLOCK_START = re.compile(r"^(CON|OBJ|VAR|DAT|PUB|PRI)\b", re.IGNORECASE)
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TYPE_WORDS = {"BYTE", "WORD", "LONG", "^BYTE", "^WORD", "^LONG"}

# Rule id -> short title, for the rules this script implements.
IMPLEMENTED = {
    "1.1": "ASCII only",
    "1.8": "no @\"\" empty-string pointer",
    "2.1": "no single-letter variable names",
    "3.2": "PUB before PRI",
    "4.9": "no horizontal lines inside CON blocks",
    "5.2": "single exit point per method",
    "5.3": "exit loops with quit, never return",
}


def tracked_spin2_files():
    """Every tracked driver/*.spin2 file, falling back to a glob outside git."""
    try:
        listing = subprocess.run(
            ["git", "-C", REPO_ROOT, "ls-files", "driver/*.spin2"],
            check=True, capture_output=True, text=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        listing = []
    if not listing:
        listing = [os.path.relpath(path, REPO_ROOT)
                   for path in glob.glob(os.path.join(REPO_ROOT, "driver", "*.spin2"))]
    return sorted(os.path.join(REPO_ROOT, path) for path in listing)


def strip_line(line, depth):
    """Return (code, comment, depth): code with strings blanked, comment text.

    `depth` is the open { } nesting carried from previous lines. Strings
    are blanked so their contents never read as code or comments.
    """
    code_chars = []
    comment_chars = []
    index = 0
    while index < len(line):
        char = line[index]
        if depth > 0:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            else:
                comment_chars.append(char)
            index += 1
            continue
        if char == "{":
            depth = 1
            index += 1
            continue
        if char == "'":
            comment_chars.append(line[index + 1:])
            break
        if char == '"':
            closing = line.find('"', index + 1)
            if closing < 0:
                closing = len(line) - 1
            code_chars.append('"' + " " * (closing - index - 1) + '"')
            index = closing + 1
            continue
        code_chars.append(char)
        index += 1
    return "".join(code_chars), "".join(comment_chars), depth


def parse_file(path):
    """Split a file into per-line records.

    Each record is (lineno, raw, code, comment, block, in_doc), where
    `in_doc` is true for a line that starts inside a {{ }} doc block.
    """
    with open(path, encoding="utf-8", errors="replace") as handle:
        raw_lines = handle.read().split("\n")
    records = []
    depth = 0
    block = None
    in_doc = False
    for lineno, raw in enumerate(raw_lines, start=1):
        starting_depth = depth
        if starting_depth == 0:
            in_doc = raw.lstrip().startswith("{{")
        code, comment, depth = strip_line(raw, depth)
        if starting_depth == 0:
            match = BLOCK_START.match(code)
            if match:
                block = match.group(1).upper()
        records.append((lineno, raw, code, comment, block, in_doc))
    return records


def check_ascii(path, findings):
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8", errors="replace")
    for lineno, line in enumerate(text.split("\n"), start=1):
        for char in line:
            codepoint = ord(char)
            if codepoint > ASCII_LAST and not BOX_DRAWING_FIRST <= codepoint <= BOX_DRAWING_LAST:
                findings.append(("1.1", path, lineno, "non-ASCII U+%04X" % codepoint))
                break


def method_spans(records):
    """Yield (kind, start_index, end_index) for each PUB/PRI method."""
    block_starts = [index for index, record in enumerate(records) if BLOCK_START.match(record[2])]
    for start in block_starts:
        if records[start][4] not in ("PUB", "PRI"):
            continue
        following = [index for index in block_starts if index > start]
        end = following[0] if following else len(records)
        yield records[start][4], start, end


def signature_text(records, start):
    """The method's declaration line, with `...` continuations joined."""
    text = records[start][2]
    index = start
    while text.rstrip().endswith("...") and index + 1 < len(records):
        index += 1
        text = text.rstrip()[:-3] + " " + records[index][2]
    return text


def signature_names(signature):
    """Parameter, return and local names declared by a PUB/PRI line."""
    body = re.sub(r"^(PUB|PRI)\s+", "", signature.strip(), flags=re.IGNORECASE)
    names = []
    params = re.search(r"\(([^)]*)\)", body)
    if params:
        names += [part.strip() for part in params.group(1).split(",")]
    after_params = body[params.end():] if params else body
    returns_part, _, locals_part = after_params.partition("|")
    if ":" in returns_part:
        names += [part.strip() for part in returns_part.split(":", 1)[1].split(",")]
    names += [part.strip() for part in locals_part.split(",")]
    declared = []
    for name in names:
        words = [word for word in re.split(r"[\s\[]", name) if word]
        words = [word for word in words if word.upper() not in TYPE_WORDS]
        if words and IDENTIFIER.fullmatch(words[0]):
            declared.append(words[0])
    return declared


def check_methods(path, records, findings):
    seen_pri = False
    for kind, start, end in method_spans(records):
        lineno = records[start][0]
        if kind == "PRI":
            seen_pri = True
        elif seen_pri:
            findings.append(("3.2", path, lineno, "PUB after a PRI"))

        for name in signature_names(signature_text(records, start)):
            if len(name) == 1:
                findings.append(("2.1", path, lineno, "single-letter name '%s'" % name))

        in_pasm = False
        code_lines = []
        for index in range(start + 1, end):
            code = records[index][2]
            stripped = code.strip()
            if not stripped:
                continue
            first_word = stripped.split()[0].lower()
            if first_word in ("org", "asm"):
                in_pasm = True
            elif first_word in ("end", "endasm"):
                in_pasm = False
                continue
            if not in_pasm:
                code_lines.append((index, code))
        repeat_indents = []
        for position, (index, code) in enumerate(code_lines):
            indent = len(code) - len(code.lstrip())
            repeat_indents = [level for level in repeat_indents if level < indent]
            words = code.strip().split()
            if words and words[0].lower() == "repeat":
                repeat_indents.append(indent)
            if words and words[0].lower() == "return":
                lineno_return = records[index][0]
                if repeat_indents:
                    findings.append(("5.3", path, lineno_return, "return inside a repeat loop"))
                elif position != len(code_lines) - 1:
                    findings.append(("5.2", path, lineno_return, "early return"))


def check_con_lines(path, records, findings):
    # The {{ }} license footer is exempt: rule 4.2.1's own template draws
    # its separator lines.
    for lineno, raw, code, comment, block, in_doc in records:
        if block != "CON" or in_doc or BLOCK_START.match(code):
            continue
        if code.strip() == "" and comment.strip() and SEPARATOR_LINE.match(comment.strip()):
            findings.append(("4.9", path, lineno, "separator line in CON block"))


def check_var_names(path, records, findings):
    for lineno, raw, code, comment, block, in_doc in records:
        if block != "VAR" or BLOCK_START.match(code):
            continue
        words = code.strip().split(None, 1)
        if len(words) == 2 and words[0].upper() in TYPE_WORDS:
            for declaration in words[1].split(","):
                name = IDENTIFIER.match(declaration.strip())
                if name and len(name.group(0)) == 1:
                    findings.append(("2.1", path, lineno, "single-letter name '%s'" % name.group(0)))


def check_empty_string(path, records, findings):
    for lineno, raw, code, comment, block, in_doc in records:
        if re.search(r'@\s*""', code):
            findings.append(("1.8", path, lineno, '@"" empty-string pointer'))


def guide_tiers():
    """{rule id: (tier, title)} from the central guide's headings."""
    tiers = {}
    try:
        with open(GUIDE_PATH, encoding="utf-8") as handle:
            for line in handle:
                match = re.match(r"^###\s+([\d.]+)\s+(.*?)\s+\S\s+\*\*(T[0-3](?:\+T2)?)\*\*", line)
                if match:
                    tiers[match.group(1)] = (match.group(3), match.group(2))
    except OSError:
        pass
    return tiers


def main(argv):
    files = [os.path.abspath(path) for path in argv] or tracked_spin2_files()
    if not files:
        print("check_style: no .spin2 files found", file=sys.stderr)
        return 2
    findings = []
    for path in files:
        try:
            records = parse_file(path)
        except OSError as error:
            print("check_style: %s" % error, file=sys.stderr)
            return 2
        check_ascii(path, findings)
        check_empty_string(path, records, findings)
        check_methods(path, records, findings)
        check_con_lines(path, records, findings)
        check_var_names(path, records, findings)

    print("Spin2 style gate (T1) -- %d files" % len(files))
    print()
    for rule, title in IMPLEMENTED.items():
        hits = [finding for finding in findings if finding[0] == rule]
        print("  %-5s %-42s %s" % (rule, title, "FAIL (%d)" % len(hits) if hits else "PASS"))
        for _, path, lineno, detail in hits:
            print("          %s:%d  %s" % (os.path.relpath(path, REPO_ROOT), lineno, detail))

    tiers = guide_tiers()
    print()
    if not tiers:
        print("NOT CHECKED: central guide not found at %s --" % GUIDE_PATH)
        print("  cannot enumerate the unimplemented T1 rules or the T2 audit set.")
    else:
        unimplemented = sorted((rule for rule, (tier, _) in tiers.items()
                                if tier == "T1" and rule not in IMPLEMENTED),
                               key=lambda rule: [int(part) for part in rule.split(".")])
        print("NOT CHECKED -- assigned T1, not yet implemented here (%d):" % len(unimplemented))
        for rule in unimplemented:
            print("  %-5s %s" % (rule, tiers[rule][1]))
        for tier_name, meaning in (("T1+T2", "script could detect, agent judges"),
                                   ("T2", "agent audit"),
                                   ("T3", "Stephen's decision")):
            rules = [rule for rule, (tier, _) in tiers.items() if tier == tier_name]
            print("NOT CHECKED -- %s (%s): %d rules" % (tier_name, meaning, len(rules)))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
