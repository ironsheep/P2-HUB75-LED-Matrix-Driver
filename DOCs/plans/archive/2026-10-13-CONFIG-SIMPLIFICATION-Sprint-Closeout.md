# CONFIG-SIMPLIFICATION — Sprint Closeout

**Closed:** 2026-10-13. **Plan:** [`CONFIG-SIMPLIFICATION-SPRINT-PLAN.md`](CONFIG-SIMPLIFICATION-SPRINT-PLAN.md)
(archived beside this file). **Build:** 4.0.0, re-cut and re-released 2026-10-11 (tag `v4.0.0` at
`de8ad7d`). Retrospective: not run at this closeout; Stephen set the next focus to the reader
documents.

**Verdict: the plan is certified complete.** Every code and documentation commitment is SHIPPED or
was changed in flight for a recorded reason, now logged in the plan's Revisions. The audit found two
shipped statements that disagreed with the tree; both are corrected in this closeout. Three gaps
that cannot close now are on the punch list with Stephen's disposition.

## How this was audited

- A read-only survey at `de8ad7d` walked the plan section by section against the code and the
  bench record, marking each commitment SHIPPED / PARTIAL / MISSING / AMBIGUOUS with file:line
  evidence, ran the plan's removed-name greps over `driver/*.spin2` and the blast-radius docs, and
  checked the sprint's user-facing claims against the code.
- Every non-SHIPPED finding was re-checked by the arbiter before disposition. One survey finding
  was overturned: "MBI5124GP flag fix MISSING" is a deliberate reversal at the bench (`bff8507`:
  "restored to the 4.0.0 value certified on its panels; the earlier respelling had no effect and no
  reason"), unlogged in the plan.
- Gates run by the arbiter (below).

## Per-section status

| § | Commitment | Status | Evidence |
|---|---|---|---|
| §0 D-1..D-15 | Per-display block; derived address lines; panel list; `ROW_`/`COL_`/`TOP_` words; n+1 fields; identify-first; cube by marks; mounting words; aliases dropped; presence and override flags; one-piece rule; author configs as blocks; scope | SHIPPED (D-12 see below) | `driver/isp_hub75_hwPanelConfig.spin2:54-151`; `driver/isp_hub75_hwEnums.spin2:158-232`; `driver/isp_hub75_hwBufferAccess.spin2` `deriveAddressLines` :1484, `checkOnePiece` :1600, `checkCubeMarks` :1667 |
| §1 | Enum words added; `C0..C15`, `ARROW_*`, `SHAPE_*`, `NO_PANEL`, `FIRST_PANEL` removed | SHIPPED | `isp_hub75_hwEnums.spin2:186-232`; removed-name grep clean (only `cube.NO_PANEL_POSITION` and demo-local `ARROW_*` constants, unrelated) |
| §2 | Config file: how-to, user section, defaults, storage, accessors | SHIPPED | `isp_hub75_hwPanelConfig.spin2:14-50`, :97-151, :181-206, `panelList` :212, `displayStorage` :233 |
| §3 | `isp_hub75_hwBuffers.spin2` retired | SHIPPED | file absent; guard longs at `hwPanelConfig:184-190` |
| §4 | Two-pass checks, tables sized by N, `placePanels` deleted, `testRelayout` takes a list | SHIPPED | `hwBufferAccess:1418-1740`, `testRelayout` :1174; M1-M18 and N1 printed as catalogued (bench B-7) |
| §4 | Hot path reads a table base once per call | SHIPPED | B-2: draw and commit within 0.4% of 4.0.0 |
| §4 | `getDriverFlags`: MBI5124GP respelled | REVERSED (logged) | `hwBufferAccess:1086` keeps the certified value; plan Revisions |
| §4 | DEBUG data does not grow | SHIPPED | measured 2026-10-13: `demo_hub75_text` plain 401,988, `-d` 411,213, delta **9,225** (limit 9,488) |
| §5 | Refresh core and OE test use derived address lines; no `ADDR_UNKNOWN` path | SHIPPED | `driver/isp_hub75_rgb3bit.spin2:474`; `driver/test_hub75_oe_bcm.spin2:261` |
| §6 | Cube marks feed `foldNet`; override notice | SHIPPED | `hwBufferAccess:1321-1322`, :1456; B-7 cube cases |
| §7 | Identify notes for identify-first | SHIPPED | `driver/demo_hub75_numberPanels.spin2:4`, :21-22, :105 |
| §8 | Row-run test: T, Z, plus | SHIPPED (plus unrun) | `driver/test_hub75_rates.spin2:459-464`; B-2 1,060 cases PASS; plus skipped (needs 5 panels) — carried |
| §9 | BMP rotation names; driver comments current | SHIPPED | `driver/isp_hub75_display_bmp.spin2:26-29`; `driver/isp_hub75_display.spin2:201-215` |
| §10 | Wiring Guide the canonical grammar; catalogue with exact text; pictures from the bench | SHIPPED | `DOCs/WiringGuide.md:450-505`; B-8 "all 13 mistake transcripts equal the guide's text" |
| §10 | Every other user doc | SHIPPED | blast-radius grep clean; hits only in `Checklist-v3-v4.md` and ChangeLog BREAKING lines, which name removed items by design |
| §11 | ChangeLog 4.0.0 re-cut | SHIPPED; two lines corrected here | see Assertions |
| §12 | Bench B-1..B-8 | SHIPPED | `DOCs/bench/RUN-NOTES.md` 2026-10-10: B-1 correct, B-2 PASS, B-3 rotated, B-4/B-5 `SCAN_4` right, B-6 flexspin refuses, B-7/B-8 as catalogued |
| §13 | Re-release gates and hand-off | SHIPPED | tag `v4.0.0` at `de8ad7d`; gates re-run below |

**Cross-reference table.** Every section §1-§13 has a row and every row maps to a section. Two
mismatches, logged in Revisions: §12's run table lists B-1..B-6 while the task row and §4/§10 name
B-7 and B-8; §0's text says D-1..D-14 while the table runs to D-15.

## Assertions checked against the tree

| Claim | Finding | Disposition (Stephen, 2026-10-13) |
|---|---|---|
| ChangeLog 4.0.0 Improvements: "Hub RAM is the only limit on panel count" | Contradicted by the code (`LINE_BUFFER_BYTES` = 512, M6) and by the same section's Breaking Changes | Corrected in place, no tag move: *"we need the changelog and the code to agree without question"*. Now states the 512-column-clock limit per adapter, with `SCAN_4` counting each column twice (`SCAN_4_COLUMN_FACTOR` = 2) |
| ChangeLog 4.0.0 Breaking Changes: "one row of panels along the cable is at most 512 columns" | Omitted the `SCAN_4` doubling the code applies (`checkPanelLimit`, `hwBufferAccess:1540`) | Corrected in the same edit |
| ChangeLog 4.0.0 cube feature, no caveat | Chip Matrix lists the cube layer on six real panels as not yet proven | Caveat and link added |
| `DOCs/AuthorTestConfigurations.md` Configuration 12 on `PIN_GROUP_P0_P15` | Bench ran it on P16-P31; P0-P15 loads were dark | Set to P16-P31: *"our test platform uses p16-p31 no matter which panel"* |
| ChangeLog Known Issues: flexspin 5.9.21 does not build | Agrees with B-6 | Stands; latest flexspin measured after the `.md` rework (punch list) |

## Carryover (punch list, `DOCs/plans/PUNCH-LIST.md`)

- **Why any line-buffer limit?** The refresh line buffer is 128 longs of cog RAM
  (`driver/isp_hub75_rgb3bit.spin2:184`, :1244); `checkPanelLimit()` caps one adapter at 512 column
  clocks. Stephen asked why a limit exists at all.
- **flexspin, latest release.** 5.9.21 refuses `#STEP[STEP]` (`isp_hub75_hwEnums.spin2:38`) and
  `repeat ... with` (`isp_hub75_display.spin2:310`). Stephen installs the latest after the `.md`
  rework; then accept pnut-ts only or change the two features (D-12).
- **Plus layout unrun.** `plusSentences` (`test_hub75_rates.spin2:463-464`) needs 5 panels; run it
  with the six-panel ICN2037 cube rig, alongside the cube-layer run.

No task was paused; none was superseded.

## Exit baseline (2026-10-13, tree `de8ad7d` plus this closeout's doc edits)

| Gate | Entry (2026-10-10, `6e804ba`) | Exit |
|---|---|---|
| 18 top files, `pnut-ts -d -l -m` | exit 0, 0 warnings | exit 0, 0 warnings (all 18) |
| DEBUG data, `demo_hub75_text` | 9,488 | 9,225 |
| `python3 tools/check_style.py` | clean | clean (T1 rules implemented; 19 T1 rules not yet implemented, as at entry) |
| `python3 tools/check_docs.py` | clean | ORPHAN 0, DUPLICATE 0, COUNT 0 |

Not worsened. Verification mode: compile-level on the Mac; behaviour verified on the P2 at the
2026-10-10 bench (quad, ICN2038S road sign, FM6124C), not re-run at closeout because no driver
source changed after `de8ad7d`.

## Tracking tools

- Board: 10 completed tasks archived (`tasks/archives/archive_20261013_120634.md`); roster exported
  first (`tasks/exports/export_20261013_120624.md`). No pending, in-progress or paused tasks.
- Context: `resume_config_simplification` deleted; no `task_#N_*` breadcrumbs remained. The
  2026-10-01 MBI5124GP research note was retired after the panel was shown solved and proven
  (single and two chained, RUN-NOTES 2026-10-05 / -07 / -09).
- Task cards read against tasks started (this project's transcripts since 2026-10-10): 12
  `todo_start` calls, 2 task-card reads; about 0.17 reads per start against a healthy ~2. Finding
  for the next retrospective: the card was not being read.
- Verdict: **ready** for new work.
