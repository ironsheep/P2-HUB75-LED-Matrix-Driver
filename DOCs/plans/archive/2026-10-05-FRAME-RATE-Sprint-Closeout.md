# FRAME-RATE — Sprint Closeout

Retrospective: [`2026-10-05-FRAME-RATE-Retrospective.md`](2026-10-05-FRAME-RATE-Retrospective.md)

**Closed:** 2026-10-05. **Plan:** [`FRAME-RATE-SPRINT-PLAN.md`](FRAME-RATE-SPRINT-PLAN.md)
(archived beside this file). **Build:** 4.0.0, still untagged. Shaping the 4.0.0 release is
the next piece of work (Stephen, 2026-10-05): release preparation (compile, certification,
ChangeLog and voicing adjustments, code audits) happens before release, and the release
workflow itself is packaging only. All commits are local, not pushed.

**Verdict: the plan is certified complete.** Every code and documentation commitment is
SHIPPED. One acceptance clause (§2's 5% agreement at 8-bit) was met only by diagnosis and is
put to Stephen below. The audit's other gaps were missing records, now written, and one
public call (`display.showFrameSet()`) whose accepted path has not run; it is carried on the
punch list with its test written.

## How this was audited

- Two read-only surveys at `e1c76d1`: the plan walked section by section against the code
  (every commitment marked SHIPPED / PARTIAL / MISSING / AMBIGUOUS with file:line evidence),
  and every reader `.md` checked against this sprint's driver changes.
- Every survey finding was checked against the code before it was acted on. One survey claim
  overturned an earlier record: the chip matrix said the driver sends no init sequence to the
  MBI5124GP, but `isp_hub75_rgb3bit.spin2` runs `resetPanelMBI5124()` for it (about :429-434).
- Gates run by the arbiter: the 18-file compile, the style gate, the docs gate.

## Per-section status

| § | Commitment | Status | Evidence |
|---|---|---|---|
| §1 | OE-weighted prototype proven on four chips (planning, visit A) | SHIPPED | `driver/test_hub75_oe_bcm.spin2`; RUN-NOTES visit A |
| §2 | `HUB75_INSTRUMENT` harness, monitors, stopwatches, `test_hub75_rates` | SHIPPED | `driver/isp_hub75_instrument.spin2`; rgb3bit strobes behind `#IFDEF` |
| §3 | Tear-free commit (`dvrShowing` handshake), `display.showFrameSet()` | SHIPPED | `driver/isp_hub75_panel.spin2` `waitPostedSetTaken`, `showFrameSet`; take check 824/824, fail limb shown (visit C) |
| §4 | /OE-weighted core, target refresh, brightness as /OE time, min-/OE table, dead code removed | SHIPPED | rgb3bit :47-69, :297-505, :890-1050; visit C within 0.2% of the model |
| §5 | Per-chip clock, 20 ns halves, 15 clocks per column | SHIPPED | rgb3bit :18-37, :742-780; high 7 clocks (20.9 ns), low 8 (23.9 ns) |
| §6 | Shimmer closed | SHIPPED | steady at 5-8 bit (Stephen, visit C) |
| §7 | MERGEB converter, both scans, equivalence harness; commit time | SHIPPED | `convertRowPairs()`; 216/216 with fail limb; 4.09 / 3.26 ms at 8 / 5-bit after SC-1 |
| SC-1 | Converter hub-slice stall removed («#104») | SHIPPED | RUN-NOTES "Converter slice stall removed" |
| §8 | Per-adapter colour table | SHIPPED | `driver/isp_hub75_colorUtils.spin2`; 3,840 entries equal the old function |
| §9 | Row runs, shared address rule, panel rectangle once per run | SHIPPED | `driver/isp_hub75_screenUtils.spin2` run primitives; 468 cases byte-equal |
| §10 | 8-bit default | SHIPPED | `DISPn_COLOR_DEPTH = DEPTH_8BIT`; 18 files compile at 8-bit |
| §11 | Bench visits A-E | SHIPPED | RUN-NOTES; plan "Visit B/C/D/E results" |
| §12 | Documentation blast radius, ChangeLog | SHIPPED | «#90», «#102»; closeout sweep (below) |

Visit D also produced «#105»: the overlapped-latch path held one clock pulse high through
the dark wait. It now ends the pulse first (FM6126A CLK high reads 21.7 ns, was 1,407.5 ns).

## Findings from the audit, and their disposition

1. **§2 Normal, 8-bit at +5.7% against THEOPS's table (clause: within 5%).** RUN-NOTES visit
   B diagnoses THEOPS's 8-bit figure, not the counters: refresh is the LATCH rate divided by
   (2^depth - 1) x 32, and the counters match THEOPS at the four depths whose figures follow
   that scaling. **Put to Stephen for ratification.**
2. **§2 Edge, no instrument code in a normal build.** Checked at closeout: no strobe, monitor
   or instrument call in any driver object outside `#IFDEF HUB75_INSTRUMENT`. Resolved.
3. **§3 Error, `showFrameSet()`.** The NULL refusal passes on every rates run. The accepted
   path and the foreign-address refusal had never run. A test was written
   (`DOCs/plans/2026-10-05-showFrameSet-test-checks.patch`); its one run went silent after the
   last test pattern, before reaching the new code, cause unknown, and Stephen stopped
   further runs before release. **Carried on the punch list; stated in the ChangeLog's Known
   Issues.**
4. **§4 Cog RAM headroom not recorded.** The refresh core's image ends at cog address 280 of
   the 496 its `FIT` allows: 215 longs free. Recorded in the plan's named unknowns.
5. **§5 14-clock question not written down.** The fixed high half is 6 clocks (17.9 ns at
   335 MHz), so 15 is the shortest loop. Recorded in the plan's named unknowns.
6. **§5 Normal, both halves measured.** Only the high half is measured; the 8-clock low half
   (23.9 ns) holds by the instruction count. The docs had the halves swapped since visit C;
   corrected in «#105».
7. **§9 `panelCoordsAt` divides.** The per-pixel path still divides; runs bypass it. The
   section's Target did not require removing them. Noted; no action.
8. **§10 8-bit compile of all top files.** The committed default is 8-bit and all 18 top files
   compile with 0 warnings (exit baseline below).
9. **Plan text stale.** Named unknowns 2 and 3 settled; the task table gains «#103»-«#105»;
   the revision history covers visit D, SC-1, «#105» and this closeout.
10. **Docs currency sweep (Stephen asked that every `.md` be current).** 36 stale items in 13
    reader files, all fixed: converter descriptions (one shared converter, four columns per
    plane write), startup-message table (width check, unrated-chip clock notice, /OE-unit
    wording), the panel-width rule, the removed wide-clock setting, hub-RAM figures at 11 bytes
    per pixel, 2D grids and gamma no longer listed as future work, the descriptor's 14th long,
    and the MBI5124GP init record.
11. **README vs chip matrix, multi-panel status.** Stephen: assume the README is correct for
    the DP5125D (now marked multi-panel in the matrix and test configurations). The ICN2038S
    is a single-ended panel and cannot chain; the README row is corrected to single-panel
    (Stephen: *"if we have a panel that is single-ended, it cannot be multi-panel"*).

## Exit baseline (protection point for the next sprint)

Measured 2026-10-05 on the macOS host, on `e1c76d1` plus this closeout's documentation
changes (no `.spin2` differs from `e1c76d1`).

- **Build (the substitute gate; the project has no automated test suite):** all 18 top files
  compile with `pnut-ts -d -l -m` (the `BUILD_COMMAND` list): 0 failed, 0 warnings and 0
  errors in the full captured log, 54 outputs written.
- **Coverage:** the 18 files in the list are exactly the 18 `driver/` files that set
  `_clkfreq`. No top file is excluded.
- **Style gate** `python3 tools/check_style.py`: exit 0 (the same T1 subset as at entry; the
  rules the script does not check are unchanged).
- **Doc audit** `python3 tools/check_docs.py`: 0/0/0 (23 documents, 36 `.spin2` sources).
- **Against the entry baseline (16 files, 0 warnings, style exit 0, docs 0/0/0): unchanged**,
  with two more top files (`test_hub75_rates.spin2`, `test_hub75_converter.spin2`) and no
  failure groups.
- **What this does not prove:** compiling is not running. Behaviour was verified at the bench
  visits and on the P2 self-tests (below).

## Verification, stated honestly

- **Verified on panels:** the quad rig (4 x ICN2037 128x64) at every depth 3-8 (visit C) and
  after SC-1 at 8 and 5 bit; single FM6126A, MBI5124GP and FM6124 panels at 8 and 5 bit
  (visit D), with patterns correct by Stephen's eye on every run; the FM6126A again after
  «#105».
- **Verified on the P2 without panels:** converter equivalence (216 cases, both scans) with
  its fail limb; colour table (3,840 entries); row runs (468 cases); cube fold (163 cases).
- **Not run on panels (ChangeLog Known Issues):** the cube on six panels; two adapters cabled
  at once; chains of quarter-scan panels; chains of more than nine panels (no bench can hold
  one); `showFrameSet()` with a caller-built set; the ICN2037 64x64, FM6124C, ICN2038S,
  GS6238S and DP5125D on this release.
- **Instrument limits:** the clock monitor reads the high half long by up to about one clock;
  the low half is not measured directly.
- **Tooling:** pnut-term-ts headless mode cuts off the line that arrives just before
  `END_SESSION`. Every PASS in RUN-NOTES was read from the count line before it, which arrives
  whole. Raised with Stephen (his tool).

## Carryover: the active punch list

`DOCs/plans/PUNCH-LIST.md` after the sweep holds:

- `display.showFrameSet()` has run only with NULL (test written as a patch; one stalled run unexplained).
- Brightness floor: settings 1-11 look the same on the quad rig (Stephen: punch list).
- ICN2038S scan setting contradicts its address lines.
- Panel-centric clipping looks up the panel per pixel on diagonal lines (narrowed by «#100»).
- Cube fold path: about five method calls per face pixel.
- Face drawing's home transform is hidden state.

Swept to the dated archive: the commit-time finding (fixed by «#104»), the line-buffer row
item (mechanism deleted by «#92»), the converter per-plane hoists (superseded by «#98» and
«#104»), the ICN2037 clock items (settled by «#90»), and the shimmer item (closed by «#95»).

## Board record (captured before archiving)

- 18 tasks completed, «#88»-«#105»; none paused. Roster:
  [`DOCs/analysis/2026-10-05-FRAME-RATE-task-roster.md`](../../analysis/2026-10-05-FRAME-RATE-task-roster.md).
- Estimated 82.0 h, tracked 13.8 h (observational only).
- Added mid-sprint: «#103» (visit C finding), «#104» (SC-1, agreed with Stephen), «#105»
  (visit D finding, agreed with Stephen).
- Task cards, this session (2026-10-05): read at 2 of 4 task starts («#104» start, «#97»
  resume; not at «#102» resume or «#105» start) and at 0 of 4 closes, which were worked from
  memory of the card. Earlier sessions' counts are in their own records. A finding for the
  retrospective.
