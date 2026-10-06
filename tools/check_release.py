#!/usr/bin/env python3
"""Pre-release check: the release manifest is the complete, exact set, and it compiles.

Usage:  python3 tools/check_release.py [--manifest release/manifest.txt]

Run on the macOS host before tagging a release. The GitHub release workflow packages
exactly the files release/manifest.txt names and cannot compile, so this check is where
the package is proved:

  1. SET     derives the files the package must ship from the source itself: the objects
             reachable through OBJ lines from the driver's public objects
             (isp_hub75_display, isp_hub75_scrollingText, isp_hub75_display_bmp) form the
             driver section; the demo top files (demo_hub75_*), isp_hub75_anlyCheck, and
             every object and FILE they reach that the driver section does not hold form
             the demos section. Any file in the manifest but not derived, or derived but not
             in the manifest, fails. Test-only files never ship.
  2. FILES   every manifest path exists and is tracked by git.
  3. BUILD   copies only the manifest's driver and demos files into an empty folder, flat,
             as a user unpacks the package, and compiles every demo top file and
             isp_hub75_anlyCheck there with pnut-ts -d. Any error or warning fails.

Prints each pnut-ts command it runs. Exit 0 when every check passes, 1 when any fails,
2 when it could not run.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_DIR = os.path.join(REPO, "driver")
DEFAULT_MANIFEST = os.path.join("release", "manifest.txt")

SECTIONS = ("driver", "demos", "docs")
DOCS_REQUIRED = {"README.md", "LICENSE", "ChangeLog.md"}

# the objects a user's program includes directly; everything they reach ships with them
DRIVER_ROOTS = ("isp_hub75_display.spin2", "isp_hub75_scrollingText.spin2", "isp_hub75_display_bmp.spin2")
DEMO_PREFIX = "demo_hub75_"
EXTRA_DEMO_TOPS = ("isp_hub75_anlyCheck.spin2",)

# never shipped: test tops, the test-only instrument, and files that are not the driver's
NEVER_SHIPPED = re.compile(r"^(test_hub75_.*|isp_hub75_instrument\.spin2|isp_dummy_flash\.spin2)$")

BLOCK_START = re.compile(r"^(CON|VAR|OBJ|DAT|PUB|PRI)\b", re.IGNORECASE)
OBJ_LINE = re.compile(r'^\s*\w+(\s*\[[^\]]*\])?\s*:\s*"([^"]+)"')
FILE_LINE = re.compile(r'\bFILE\s+"([^"]+)"', re.IGNORECASE)


def read_manifest(path):
    """Return {section: {package name: repo path}}, or raise ValueError on a malformed line."""
    entries = {section: {} for section in SECTIONS}
    with open(path, encoding="utf-8") as handle:
        for lineNbr, line in enumerate(handle, 1):
            text = line.split("#", 1)[0].strip()
            if not text:
                continue
            fields = text.split()
            if len(fields) not in (2, 3) or fields[0] not in SECTIONS:
                raise ValueError("%s:%d: expected '<section> <path> [<name>]', section one of %s" % (path, lineNbr, ", ".join(SECTIONS)))
            section, repoPath = fields[0], fields[1]
            name = fields[2] if len(fields) == 3 else os.path.basename(repoPath)
            entries[section][name] = repoPath
    return entries


def strip_comments(source):
    """Remove { } and {{ }} block comments and ' line comments (strings are left alone)."""
    source = re.sub(r"\{\{.*?\}\}", "", source, flags=re.DOTALL)
    source = re.sub(r"\{.*?\}", "", source, flags=re.DOTALL)
    lines = []
    for line in source.splitlines():
        inString = False
        cut = len(line)
        for idx, char in enumerate(line):
            if char == '"':
                inString = not inString
            elif char == "'" and not inString:
                cut = idx
                break
        lines.append(line[:cut])
    return lines


def references(fileName):
    """Return (objects, files) a .spin2 file names in OBJ lines and FILE directives."""
    objects, files = set(), set()
    inObj = False
    for line in strip_comments(open(os.path.join(DRIVER_DIR, fileName), encoding="utf-8", errors="replace").read()):
        stripped = line.strip()
        if BLOCK_START.match(stripped):
            inObj = stripped.upper().startswith("OBJ")
            stripped = stripped[3:] if inObj else stripped
        if inObj:
            match = OBJ_LINE.match(stripped)
            if match:
                name = match.group(2)
                objects.add(name if name.endswith(".spin2") else name + ".spin2")
        for match in FILE_LINE.finditer(line):
            files.add(match.group(1))
    return objects, files


def reach(roots):
    """Return (spin2 files, data files) reachable from roots through OBJ and FILE."""
    seen, data, stack = set(), set(), list(roots)
    while stack:
        fileName = stack.pop()
        if fileName in seen:
            continue
        seen.add(fileName)
        if not os.path.exists(os.path.join(DRIVER_DIR, fileName)):
            continue                                            # reported by the set check
        objects, files = references(fileName)
        data |= files
        stack.extend(objects - seen)
    return seen, data


def derived_set():
    """Return {section: set of package names} the source says the package must hold."""
    demoTops = sorted(name for name in os.listdir(DRIVER_DIR) if name.startswith(DEMO_PREFIX) and name.endswith(".spin2"))
    driverSet, driverData = reach(DRIVER_ROOTS)
    demoReach, demoData = reach(demoTops + list(EXTRA_DEMO_TOPS))
    return {"driver": driverSet | driverData, "demos": (demoReach | demoData) - driverSet - driverData}, demoTops


def tracked(repoPath):
    result = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch", repoPath], capture_output=True, text=True)
    return result.returncode == 0


def check_set(entries, problems):
    expected, demoTops = derived_set()
    for section in ("driver", "demos"):
        listed = set(entries[section])
        for name in sorted(expected[section] - listed):
            problems.append("SET: %s is needed by the %s section but is not in the manifest" % (name, section))
        for name in sorted(listed - expected[section]):
            problems.append("SET: %s is in the manifest's %s section but nothing in that section uses it" % (name, section))
    for section in SECTIONS:
        for name in sorted(entries[section]):
            if NEVER_SHIPPED.match(name):
                problems.append("SET: %s must never ship (test-only or not part of the driver)" % name)
    for name in sorted(DOCS_REQUIRED - set(entries["docs"])):
        problems.append("SET: the docs section has no %s" % name)
    return demoTops


def check_files(entries, problems):
    for section in SECTIONS:
        for name, repoPath in sorted(entries[section].items()):
            if not os.path.exists(os.path.join(REPO, repoPath)):
                problems.append("FILES: %s (%s) does not exist" % (repoPath, section))
            elif not tracked(repoPath):
                problems.append("FILES: %s (%s) is not tracked by git" % (repoPath, section))


def check_build(entries, buildTops, problems):
    workDir = tempfile.mkdtemp(prefix="hub75-release-")
    try:
        for section in ("driver", "demos"):
            for name, repoPath in entries[section].items():
                source = os.path.join(REPO, repoPath)
                if os.path.exists(source):
                    shutil.copy2(source, os.path.join(workDir, name))
        print("BUILD: package files copied to %s (%d files)" % (workDir, len(os.listdir(workDir))))
        for top in buildTops:
            command = ["pnut-ts", "-d", top]
            print("BUILD: + (cd %s && %s)" % (workDir, " ".join(command)))
            result = subprocess.run(command, cwd=workDir, capture_output=True, text=True)
            output = result.stdout + result.stderr
            nWarnings = len(re.findall(r"warning", output, re.IGNORECASE))
            if result.returncode != 0 or re.search(r"error", output, re.IGNORECASE) or nWarnings:
                problems.append("BUILD: %s failed (exit %d, %d warning lines): %s" % (top, result.returncode, nWarnings, output.strip().splitlines()[-1] if output.strip() else "no output"))
            else:
                print("BUILD:   %s compiled, 0 warnings" % top)
    finally:
        shutil.rmtree(workDir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="manifest path, relative to the repo root")
    args = parser.parse_args()
    manifestPath = os.path.join(REPO, args.manifest)
    if shutil.which("pnut-ts") is None:
        print("CANNOT RUN: pnut-ts is not on PATH")
        return 2
    try:
        entries = read_manifest(manifestPath)
    except (OSError, ValueError) as err:
        print("CANNOT RUN: %s" % err)
        return 2

    problems = []
    demoTops = check_set(entries, problems)
    check_files(entries, problems)
    buildTops = [top for top in demoTops + list(EXTRA_DEMO_TOPS) if top in entries["demos"]]
    check_build(entries, buildTops, problems)

    counts = ", ".join("%s %d" % (section, len(entries[section])) for section in SECTIONS)
    for problem in problems:
        print(problem)
    if problems:
        print("RELEASE CHECK FAIL: %d problem(s); manifest %s" % (len(problems), counts))
        return 1
    print("RELEASE CHECK PASS: manifest complete and exact (%s); %d top files compiled with 0 warnings" % (counts, len(buildTops)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
