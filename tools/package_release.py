#!/usr/bin/env python3
"""Build the release package from release/manifest.txt (no compiling).

Usage:  python3 tools/package_release.py --version 4.0.0 [--out dist] [--date YYYY-MM-DD]
                                         [--manifest release/manifest.txt]

The GitHub release workflow (.github/workflows/release.yml) runs this on a pushed v* tag;
run it locally to preview the package. It writes into --out:

  p2-obex-driver-v<version>.zip   flat: README.md (its "Version:" and "Updated:" lines
                                  stamped), LICENSE, ChangeLog.md, the driver objects,
                                  and isp_hub75_demos.zip (the demos section)
  release-notes.md                the ChangeLog.md section for <version>

It packages exactly the manifest's files: the manifest is proved complete and compiling by
tools/check_release.py before the tag. Exit 0 when the package was built, 1 when a manifest
file is missing, the README lacks a stamp line, or ChangeLog.md has no section for the
version; 2 when it could not run.
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_release import DEFAULT_MANIFEST, REPO, read_manifest   # one reader for the one list

DEMOS_ZIP = "isp_hub75_demos.zip"
PACKAGE_NAME = "p2-obex-driver-v%s.zip"
NOTES_NAME = "release-notes.md"
README_NAME = "README.md"
CHANGELOG_NAME = "ChangeLog.md"


def commit_date():
    """Return the date of the checked-out commit (the tagged commit in the workflow)."""
    out = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%cI"], capture_output=True, text=True, check=True)
    return datetime.date.fromisoformat(out.stdout.strip()[:10])   # %cI: strict ISO 8601, any git version


def stamp_readme(text, version, date):
    """Set the README's "Version:" and "Updated:" lines; raise ValueError if either is missing."""
    stamps = {"Version": version, "Updated": date.strftime("%d-%b-%Y").upper()}
    for key, value in stamps.items():
        text, count = re.subn(r"(?m)^%s:.*$" % key, "%s: %s" % (key, value), text)
        if count != 1:
            raise ValueError("%s has %d \"%s:\" lines; it needs exactly one" % (README_NAME, count, key))
    return text


def release_notes(changelog, version):
    """Return the ChangeLog section headed "## [<version>]"; raise ValueError if absent."""
    match = re.search(r"(?ms)^## \[%s\].*?(?=^## \[|\Z)" % re.escape(version), changelog)
    if match is None:
        raise ValueError("%s has no \"## [%s]\" section" % (CHANGELOG_NAME, version))
    return match.group(0).rstrip() + "\n"


def add_file(archive, name, data, date):
    """Add one file, dated the release date, so the same tag always gives the same zip."""
    info = zipfile.ZipInfo(name, date_time=(date.year, date.month, date.day, 0, 0, 0))
    info.external_attr = 0o644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def build(entries, version, date, outDir):
    """Write the package and the notes into outDir; return the package path and its listing."""
    missing = [path for section in entries.values() for path in section.values() if not os.path.exists(os.path.join(REPO, path))]
    if missing:
        raise ValueError("manifest files missing: %s" % ", ".join(sorted(missing)))
    read = lambda path: open(os.path.join(REPO, path), "rb").read()

    os.makedirs(outDir, exist_ok=True)
    demosPath = os.path.join(outDir, DEMOS_ZIP)
    with zipfile.ZipFile(demosPath, "w") as demos:
        for name, path in sorted(entries["demos"].items()):
            add_file(demos, name, read(path), date)

    top = {}
    for name, path in entries["docs"].items():
        data = read(path)
        if name == README_NAME:
            data = stamp_readme(data.decode("utf-8"), version, date).encode("utf-8")
        top[name] = data
    for name, path in entries["driver"].items():
        top[name] = read(path)
    top[DEMOS_ZIP] = open(demosPath, "rb").read()
    os.remove(demosPath)

    packagePath = os.path.join(outDir, PACKAGE_NAME % version)
    with zipfile.ZipFile(packagePath, "w") as package:
        for name in sorted(top):
            add_file(package, name, top[name], date)

    notes = release_notes(open(os.path.join(REPO, CHANGELOG_NAME), encoding="utf-8").read(), version)
    with open(os.path.join(outDir, NOTES_NAME), "w", encoding="utf-8") as handle:
        handle.write(notes)
    return packagePath, sorted(top)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", required=True, help="release version, without the leading v (4.0.0)")
    parser.add_argument("--out", default="dist", help="output folder, relative to the repo root")
    parser.add_argument("--date", help="Updated date as YYYY-MM-DD (default: the checked-out commit's date)")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="manifest path, relative to the repo root")
    args = parser.parse_args()
    try:
        entries = read_manifest(os.path.join(REPO, args.manifest))
        date = datetime.date.fromisoformat(args.date) if args.date else commit_date()
    except (OSError, ValueError, subprocess.CalledProcessError) as err:
        print("CANNOT RUN: %s" % err)
        return 2
    outDir = os.path.join(REPO, args.out)
    try:
        packagePath, listing = build(entries, args.version, date, outDir)
    except ValueError as err:
        print("PACKAGE FAIL: %s" % err)
        return 1
    print("PACKAGE: %s" % os.path.join(args.out, os.path.basename(packagePath)))
    for name in listing:
        print("  %s" % name)
    print("PACKAGE: %s (demos zip holds %d files)" % (os.path.join(args.out, NOTES_NAME), len(entries["demos"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
