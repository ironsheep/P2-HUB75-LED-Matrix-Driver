# RELEASE 4.0.0 — Plan

**Status:** agreed with Stephen 2026-10-05; items 1-3 done (manifest and check, release workflow, OBEX README).
**Build:** 4.0.0 (DISPLAY-ORGANIZATION and FRAME-RATE). Tagging and pushing are Stephen's.

## The line of division (Stephen, 2026-10-05)

- **Before the tag, local (macOS):** release preparation. Everything that ships is compiled
  and certified here, and the exact set of files that ships is written to a committed
  manifest. Compile, certification, ChangeLog and voicing adjustments and code audits all
  happen before release.
- **At the tag, GitHub Actions:** the release workflow is packaging only. On push of a `v*`
  tag it packages exactly the manifest's files with the version number, the latest
  ChangeLog and the LICENSE, and attaches the zip to the GitHub release. It cannot compile.
- **The manifest is the contract.** Neither side keeps its own file list. Stephen then
  uploads the release zip to the OBEX by hand.

## Package shape (the v0.9.0 shape; `REF-NO-COMMIT/packaging/p2-obex-driver-v0.9.0/`)

`p2-obex-driver-v<version>.zip`, flat:

- `README.md` — the OBEX header (`driver/README.md`), Version and Updated stamped from the tag
- `LICENSE`, `ChangeLog.md` (new in 4.0.0's package)
- the driver objects: `isp_hub75_color`, `colorUtils`, `cube`, `display`, `display_bmp`,
  `fonts`, `hwBufferAccess`, `hwBuffers`, `hwEnums`, `hwPanelConfig`, `panel`, `rgb3bit`,
  `screenUtils`, `scrollingText`
- `isp_hub75_demos.zip`: every `demo_hub75_*.spin2`, the demo-only objects
  `isp_hub75_7seg` and `isp_hub75_segment`, the pin exercisor `isp_hub75_anlyCheck`, and
  `TstBG-Up.bmp`

Never shipped: `test_hub75_*`, `isp_hub75_instrument` (test-only), `isp_dummy_flash` (not
part of the driver), untracked files, logs, build outputs, macOS metadata.
Judgement calls agreed (Stephen, 2026-10-05: "yes that all sounds correct"): `display_bmp`
is a driver object; `anlyCheck` goes in the demos zip; `TstBGCol.bmp` is dropped (no demo
uses it).

## Work

1. **Manifest and pre-release check.** A committed manifest of the package's files by
   section (driver, demos, docs). A local check (`tools/`) that derives the set from the OBJ
   graph and the demos' `FILE` lines and fails on any difference with the manifest, copies
   only the manifest's files into a clean folder laid out as the package, and compiles every
   demo and `isp_hub75_anlyCheck` there with 0 warnings. Its fail limb is shown: a manifest
   missing one object must fail.
2. **GitHub release workflow** (`.github/workflows/release.yml`, packaging in `tools/package_release.py`, previewable locally with `python3 tools/package_release.py --version <v>`): on push of a `v*` tag, read the
   manifest, check every file exists, stamp the README, build the inner and outer zips, and
   create the GitHub release with the tag's ChangeLog section as notes and the zip attached.
   No compile.
3. **OBEX README** (`driver/README.md`): fix the stale header (add `Version:`, the
   "Upadted" typo and date, License pointing at the included LICENSE).
4. **Release preparation:** README "Latest Updates" block gains FRAME-RATE's changes; the
   README Releases badge link points at the real repository; ChangeLog `[4.0.0]` voicing
   review and date; the code audit (style guide T2 rules); the 18-file compile and the
   pre-release check on the final tree.

Then any testing Stephen wants, then the tag and push (Stephen).

## The 4.0.0 release process, and later releases (Stephen, 2026-10-05)

- **4.0.0 is a one-time bring-up of the packaging.** Certify that everything is ready, commit,
  tag and push. Download the release zip. If it is not correct, fix, move the tag, and push
  again until the zip is built correctly. That ends the 4.0.0 release.
  - The workflow must therefore replace the zip on an existing `v4.0.0` release when the tag
    is pushed again, not fail and not attach a second copy.
  - Moving a published tag is acceptable only while no one has taken 4.0.0; it is not the
    process for later releases.
- **Later releases do not re-verify the zip**: 4.0.0 proves the packaging. What remains is
  watching for files added or removed, which the pre-release check's SET step catches (a
  new or deleted object, demo or data file fails it until the manifest is updated).
