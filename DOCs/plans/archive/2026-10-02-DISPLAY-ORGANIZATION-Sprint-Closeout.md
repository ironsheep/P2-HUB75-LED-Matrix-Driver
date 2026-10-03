# DISPLAY-ORGANIZATION — Sprint Closeout

**Closed:** 2026-10-02. **Plan:** [`DISPLAY-ORGANIZATION-SPRINT-PLAN.md`](DISPLAY-ORGANIZATION-SPRINT-PLAN.md)
(archived beside this file). **Build:** 4.0.0, which is **not finished by this sprint**.
Stephen, 2026-10-02: *"v4.0.0 is correct but we are not done with new content this just
starts the content"*. Nothing is tagged. The changelog's `[4.0.0]` entry is marked in
development and grows with later sprints. All commits are local, not pushed.

**Verdict: the plan is certified complete.** Every commitment is SHIPPED, or is
explicitly deferred to the panel sweep by the plan itself (§13 "not yet proven"). No
item is MISSING or PARTIAL in code. The audit found a few records missing from the
plan and some documentation defects; each is resolved below, or carried with a
specific punch-list entry.

## How this was audited

A read-only audit walked the plan section by section against the tree at `e814e2b`. It
covered:
- every commitment in §1-§13;
- the Documentation Blast Radius rows;
- §12 deliverables 1-5;
- the named unknowns;
- *What done means*.

Each commitment is marked with a `file:line` in the current tree, or with the plan's
bench record line. The arbiter then resolved the audit's PARTIAL and AMBIGUOUS marks
from the per-task commit messages and their P2 runs. Those runs are cited below.

## Per-section status

`hba` = `driver/isp_hub75_hwBufferAccess.spin2`.

| § | Commitment | Status | Evidence |
|---|---|---|---|
| §1 | Glossary in THEOPS.md; other docs link to it | SHIPPED | `THEOPS.md:78-138`; `DOCs/ChipCharacteristicsMatrix.md:5`, `DOCs/AuthorTestConfigurations.md:5` |
| §1 | Scan term "1/S scan" | SHIPPED | `THEOPS.md:138`. "1/8 scan" in code comments is that term's form for a 32-row SCAN_4 panel (8 addresses), not drift |
| §2 | Sentence words, settings, `DISPn_PANEL_COUNT`, buffers by panel count, old settings removed | SHIPPED | `driver/isp_hub75_hwEnums.spin2:175-226`; `driver/isp_hub75_hwPanelConfig.spin2:116-152`; `driver/isp_hub75_hwBuffers.spin2:37-65`; grep for the removed names finds none in `driver/` |
| §3 | Decode, check (catalogue rows 1-21 + notice + summary), derive, picture, one call per adapter | SHIPPED | `hba:1002` `checkAndDeriveLayout`, `:1296` `placePanels`, `:1358` `buildLayoutTables`, `:1431` `buildMountedTables`, `:1612` halt, `:1622` summary; `driver/isp_hub75_display.spin2:179` `start(eHub75Adapter)` |
| §3 | Verify: example configs and one broken config per check, run headless | SHIPPED | 21 P2 captures (7 configs, 14 mistakes) for the wiring guide, each mistake printing its catalogue row (`bf3942c`). Four wrong cube configs halted with rows 15/16/19/20 (`7ef911d`) |
| §4 | One mapping; old tables deleted; panel-centric clipping; fillScreen by panel; cost | SHIPPED | `hba:625` `displayPixelAddress`; `driver/isp_hub75_screenUtils.spin2:52`; draw 287,436 → 191,883 µs (§13) |
| §5 | Mounted size from the accessors; clamp at mounted size; `displayRotation` | SHIPPED | `hba:272,281,290,429`; Visit A rows 4-7 |
| §5b | Content rotation: `placeBMP`, any size, turned at placement, invalid value rejected | SHIPPED | `driver/isp_hub75_display_bmp.spin2:63-120`; readback 8/8 cases at both mountings, including 64x32 and 290x150 images (row padding) and text drawn earlier surviving; a swapped-turn copy fails every turned case (`29aacc3`); Visit A runs 8-9 |
| §5c | Panel-centric calls in the viewer's frame | SHIPPED | `hba:681,719,1431`; probe 0 FAIL at four mountings, HEAD 4/4 FAIL at 90/270 (`9914227`); Visit A rows 5-7 |
| §6 | F1 panel cap, F2 quarter-scan read, F3 own buffer, sub-page sizing | SHIPPED | harness on P2: HEAD fails 10/16 half-scan and 2/3 quarter-scan, fix passes all; F3 two-display check HEAD 2/4, fix 4/4; the per-commit debug line names `PNL #n screen 0x...` (`e17821a`); `driver/isp_hub75_display.spin2:323,325`; `driver/isp_hub75_rgb3bit.spin2:488-499`. PASM2 changes cited p2kb `p2kbPasm2Cmpsub`, `p2kbPasm2Qdiv` (rejected), `p2kbPasm2Mul` and others in the «#76» design return |
| §7 | Cube checks, fold, edge table, faces, STABLE up conventions, corner gap, seam, face-centric primitives, one core | SHIPPED | `driver/isp_hub75_cube.spin2:174-433`; `hba:1213-1281`; `driver/isp_hub75_display.spin2:151-153,634,823,970,1063,1097,1146` |
| §7.7 | Fold self-test: every case PASS; a flipped expected value FAILs | SHIPPED | `driver/test_hub75_cube_fold.spin2`: 132/132 with E1 flipped → that case alone FAIL (`7ef911d`); 163/163 with b5 flipped → that case alone FAIL (`cfb89d8`); 163/163 again at Visit B |
| §7 | Proof on six real panels | DEFERRED (by plan) | §13 Visit B "Not yet proven" |
| §8 | Identify routine; normal, edge, negative | SHIPPED | `driver/demo_hub75_numberPanels.spin2:96-162`; Visit A rows 1-3; white-text fix `9254a4c` |
| §9 | Boundary test; four mountings | SHIPPED | `driver/demo_hub75_boundary.spin2`; Visit A draw times |
| §9 | "exercises content rotation once §5b lands" | SUPERSEDED (recorded) | Q1 made content rotation a BMP placement parameter, so the drawn test has nothing to turn; certified by `29aacc3` and Visit A runs 8-9. Note added to plan §9 |
| §10 | One-call startup everywhere; panel constants in reading order; hwGeometry deleted; dummy flash tracked and swept | SHIPPED | `54d16e1`; readback of `multi2x2panel`/`quadPanel` quadrants; Stephen *"Labels are all correct"*; `.claude/skill-conventions.md:27-29` |
| §11 | Limit constants, `checkPanelLimit`, per-type table, hub-RAM proof, measured rig refresh and flicker | SHIPPED | `hba:61-80,1189`; `DOCs/WiringGuide.md#driver-limits`; plan §11 working table; 6 x 128x64 at 8-bit fails with "exceeds 512KB hub RAM by 89108 bytes" (re-run by the arbiter) |
| §12.1 | Wiring guide, seven examples x five parts | SHIPPED | `DOCs/WiringGuide.md`; 65 quoted output lines all verbatim in the P2 captures (script check, with a negative probe); catalogue 30/30 matches the plan (`bf3942c`) |
| §12.2-5 | Glossary, upgrade checklist, changelog, blast radius | SHIPPED | `THEOPS.md:78`; `Checklist-v3-v4.md`; `ChangeLog.md:9`; the plan's Blast Radius table, ticked (`c7643a4`) |
| §13 | Visits 0, A, B | SHIPPED | plan §13 records (Stephen's words, draw times, verdicts) |

## Cross-reference table

The table was reconciled both directions. Every numbered section has a row, and every
row maps to a real section. The table had gone stale in two places, both fixed in the
plan before this closeout (`e814e2b`):
- §5b still said "not yet generated";
- §5c had no row.

«#67» was outside the sprint's numbered sections by agreement. It is closed, with its
cause recorded in the named-unknowns table.

## Findings from the audit, and their disposition

| Finding | Disposition |
|---|---|
| `DOCs/TheoryOfOperations.md` said the line buffer is "512 longs" (three places); the code has 512 **bytes**, 128 longs (`driver/isp_hub75_rgb3bit.spin2:50`) | **Fixed** in this closeout |
| ICN2037 maximum clock is 20 MHz in `ChipCharacteristicsMatrix.md` and the code comment, but 30 MHz in `README.md` and `TheoryOfOperations.md` | **Punch list**, with the steps to settle it: the datasheet in `DOCs/ICN2037/` could not be read here (no PDF tool installed) |
| Plan §10 text still said 13/14 top files | **Fixed**: an as-built note gives 15 |
| ChangeLog conformance row said "Released"; `[4.0.0]` is in development | **Fixed**: the row records the in-development entry |
| ChangeLog did not mention the deleted `demo_hub75_hwGeometry.spin2` | **Fixed**: a `#### Removed` bullet. `isp_dummy_flash` is not part of the driver and is not in the changelog, by design |
| Human-reader docs (`README.md`, `THEOPS.md`, `Checklist-v*.md`, `DOCs/*.md`) have no `CONFORMANCE_GUIDES` row | **Central gap**: central has only `changelog-voicing` and `spin2-authoring-guide`, so there is no guide to bind them to. Proposed row once one exists: `surface: README.md, THEOPS.md, Checklist-v*.md, DOCs/*.md` / `guide: central:<human-reader doc guide>` / `when: any doc edit` / `strength: reference`. For the retrospective |

**Conformance rows, quoted verbatim from `.claude/skill-conventions.md`:**

```
  - surface:  ChangeLog.md
    guide:    central:changelog-voicing
    class:    1 — embedded driver / library (authored; no local profile)
    mode:     Released — v3.0.x shipped; §4 governs. [4.0.0] is in development (not tagged; grows across sprints)
    when:     any changelog entry
    strength: reference
  - surface:  driver/*.spin2
    guide:    central:spin2-authoring-guide
    when:     any .spin2 edit
    strength: reference      # STYLE_GATE_COMMAND runs the partial T1 tier; gate needs T2 audit_record («#14», v12(g))
```

Neither row is `strength: gate`. The style gate (`python3 tools/check_style.py`) was
nonetheless run at every task close and at exit, and passes its 7 implemented T1 rules.

**Assertions:** the domain claims the sprint added are each supported by code or by a
recorded measurement:
- the panel clock: `clkfreq / 20_000_000`, 16 cycles at 335 MHz, 20.94 MHz;
- the refresh formula and the 2^N − 1 scans per cycle;
- the smart-pin counter method (calibrated, recorded in plan §11);
- the hub-RAM ceiling (a compiler measurement).

The ICN2038S scan setting is carried as disputed, not asserted. One assertion is
contradicted between documents: the ICN2037 clock rating, now on the punch list. None
is contradicted by the domain authority (p2kb-mcp), so sprint stop 6 does not apply.

## Exit baseline (protection point for the next sprint)

Measured 2026-10-02 on macOS, the canonical environment.

| Check | Entry (2026-10-01) | Exit (2026-10-02) |
|---|---|---|
| Tree | clean | clean |
| Compile sweep (`TEST_COMMAND`) | 13 of 13 top files, 0 warnings | **15 of 15**, 0 warnings. The 15 are every file in `driver/` that sets `_clkfreq`: added `test_hub75_cube_fold`, `isp_dummy_flash` and `demo_hub75_boundary`; removed `demo_hub75_hwGeometry` |
| Style gate | exit 0, 7 rules PASS | exit 0, 7 rules PASS (31 sources) |
| Doc audit | 21 docs: ORPHAN 0, DUPLICATE 0, COUNT 0 | 23 docs: **ORPHAN 0, DUPLICATE 0, COUNT 0**. Released upgrade checklists are exempt from ORPHAN by design (`c7643a4`) |
| Hardware | `quadPanel` download ok | `quadPanel` runs to its end marker, cable map `C0->P2 C1->P3 C2->P0 C3->P1` (`headless_261002-211132.log`) |

**Health has not worsened.** Every check is at least as good as at entry.

## Verification, stated honestly

- **Verified on the canonical target, the P2 rig with Stephen observing:**
  - the mapping and the identify routine;
  - mounting rotation at all four values, and the viewer's frame;
  - content rotation;
  - the converter fixes, as far as the rig shows (four half-scan panels);
  - the demos;
  - measured refresh and the flicker threshold;
  - the C1 flicker cause.
- **Verified on the P2 by harness or readback, not by eye:**
  - F1 at 9/10/16 panels and F2 at 1-3 quarter-scan panels (buffer-level harness);
  - F3 with two displays configured (no second adapter cabled);
  - the cube fold (163-case self-test, no cube attached);
  - BMP placement at every rotation;
  - panel-frame placement at four mountings.
- **Not verified:**
  - a cube on six real panels;
  - the green MBI5124GP quarter-scan panels;
  - two adapters cabled at once;
  - panel types other than ICN2037 128x64;
  - measured refresh for other types.

  These belong to the panel sweep (plan §13).

## Carryover: the active punch list

Each item is carried as a specific entry in `DOCs/plans/PUNCH-LIST.md`:
- **Interleave the bit-plane repeats**, in `driver/isp_hub75_rgb3bit.spin2`
  `cmdDsplyFrameSet`. This fixes the 5-bit-and-up shimmer and was the cause of the old
  C1 flicker.
- **Panel clock** 20.94 MHz against the ICN2037 rating. Settle it together with the
  20/30 MHz docs conflict, from the datasheet.
- **ICN2038S scan**: the `SCAN_4` flag against ABCDE addressing.
- **Converter speed**: per-plane hoists in `driver/isp_hub75_panel.spin2`, estimated at
  10-15%.
- **Panel-centric clipping** looks up the panel per pixel.
- **Cube fold path**: about five calls per face pixel.
- **Face drawing's home transform** is hidden state.

The refresh-core row-overrun item stays **active, marked `[~]`**. «#76» fixed it by
construction (sub-pages hold whole rows), but it is not yet observed on a 9/10-panel or
3-quarter-scan chain, and the sweep rule keeps a fix that has not been validated active.
One item was archived at this closeout, the stale refresh figures in the docs (fixed in
«#85»): [`PUNCH-LIST-2026-10-02-archive.md`](PUNCH-LIST-2026-10-02-archive.md).

## Board record (captured before archiving)

- **Completed roster:** 21 tasks, «#67»-«#87», all completed, none superseded:
  [`DOCs/analysis/2026-10-02-DISPLAY-ORGANIZATION-task-roster.md`](../../analysis/2026-10-02-DISPLAY-ORGANIZATION-task-roster.md).
- **Paused tasks:** none.
- **Today's session summary:** 5 tasks completed, 2 h 51 min tracked. Over the sprint,
  22 h 13 min was tracked against 44 h 30 min estimated.
- **Task cards read against tasks started:** the card was read in full at 1 of the 14
  task starts in this session (the «#75» resume), and partly at 1 (the «#77» start).
  It was not read at the others, and not at closes. Breadcrumbs were written for 13 of
  the 14; «#81» ran inline without one. Both counts are protocol findings for the
  retrospective.
