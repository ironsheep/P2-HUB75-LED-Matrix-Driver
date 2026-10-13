# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

### Why does the refresh have a line-buffer limit at all? (question; Stephen 2026-10-13)

- **Asked:** at the CONFIG-SIMPLIFICATION closeout, after the 4.0.0 ChangeLog was corrected to state the limit: *"an issue for later (punch-list for now) is why do we have any limit (512)"*.
- **What it is today:** the refresh core holds one row of the whole chain in a line buffer of `LINE_BUFFER_BYTES` = 512 (`driver/isp_hub75_hwBufferAccess.spin2`, CON near :47); `LINE_BUFFER_MAX_COLUMNS` follows from it, and `checkPanelLimit()` stops startup (message M6) when one adapter's panels, added along the cable and doubled for `SCAN_4`, pass it. Stated to users in ChangeLog 4.0.0 (Improvements, Breaking Changes) and `DOCs/WiringGuide.md#driver-limits`.
- **Known:** the buffer is in the refresh cog's own RAM, 128 longs (`MAX_COG_BUFFER_SIZE_IN_LONGS`, `driver/isp_hub75_rgb3bit.spin2:184`, reserved at :1244), so cog RAM space, not hub RAM, is what it competes for.
- **Not known:** why the refresh needs a whole row in cog RAM rather than streaming it from hub, how much cog RAM is free beside it, and what a longer chain costs in refresh rate. Answer from the refresh core before proposing a change.
- **Bears on:** the largest display one adapter can drive; the ChangeLog and Wiring Guide limit statements, which change with it.

### flexspin: measure the latest release against the tree (Stephen 2026-10-13; after the `.md` rework)

- **Found:** bench B-6, 2026-10-10 (`DOCs/bench/RUN-NOTES.md`): flexspin 5.9.21 (Dec 2022) refuses the tree at the stepped enums (`isp_hub75_hwEnums.spin2:38`, `#STEP[STEP]`) and `repeat ... with` (`isp_hub75_display.spin2:310`). The storage-sizing difference it also showed is fixed (`@` labels, `bff8507`).
- **Next:** once the `.md` rework is done, Stephen installs the latest flexspin; build one demo with it and record the exact result. Then decide: accept pnut-ts only (ChangeLog 4.0.0 Known Issues already says so for 5.9.21) or change the two features. Until then the ChangeLog line stands as written.
- **Bears on:** ChangeLog Known Issues; who can build the driver.

### Row-run self-test: the plus layout has never run (gap in a test; Stephen 2026-10-13)

- **What:** `test_hub75_rates.spin2` relays the display over a plus layout as well as the Ls, T and Z (`plus` sentence list near :463), but runs a layout only when its panel count equals the rig's; the quad has 4 panels, the plus needs 5. Bench B-2 (2026-10-10): 1,060 row-run cases PASS, plus skipped.
- **Run it:** the next time the six-panel ICN2037 cube rig is set up, together with the cube-layer run already on the Chip Matrix's not-yet-proven list. Five of the six panels cabled as a plus.
- **Bears on:** nothing users are told: ChangeLog 4.0.0 claims only rows, grids, L, T and Z.

### Turn the process documents into user documentation, then stop publishing them (scope; Stephen 2026-10-10, not this sprint)

- **What:** `DOCs/plans/`, `DOCs/analysis/` and `DOCs/bench/` are tracked and record how the project is built. Some of what they hold would help users, but not in its present form: the analyses' findings (chip timing, refresh and frame-rate measurements, the audits' conclusions) and the bench techniques (how a configuration is checked on a rig, run sheets, what each measurement shows).
- **Ruling:** Stephen, 2026-10-10: *"We probably need to synthesize the analyses and any bench run techniques into something usable by the repo, and then no longer publish the plans, analysis, and bench results."* Not part of the CONFIG-SIMPLIFICATION re-cut: *"For now, I'm not worrying about cleaning up this tree."*
- **Shape:** first write the user-facing synthesis (for example a bench and verification guide, with the chip and performance findings folded into the existing docs); then stop tracking the three folders. Whether to change the `Claude Code` author lines and the dev-container comments is decided in the same sprint.
- **Bears on:** what anyone who clones the repository sees; `tools/check_docs.py`, whose `EXCLUDED_PREFIXES` names `DOCs/plans/` and `DOCs/analysis/`.

### Driver `debug()` footprint: about 10 KB of a program's 16 KB DEBUG data (finding; disposition: punch list, Stephen 2026-10-09)

- **Found:** 2026-10-09, «#111», at the quad recheck. `test_hub75_rates.spin2`'s workload report died partway through ("CLK high") and once printed for 17 minutes: the 16 KB DEBUG data cap fails silently below the compiler's error (P2KB `p2kbSpin2DbgDebugStrategyGuide`). On that program the usable ceiling lay between 15,183 bytes (clean) and 15,357 (broken). The test's prose was moved into `DAT` strings with `zstr_()` (13,593 bytes); every self-test then passed (`DOCs/bench/RUN-NOTES.md`, 2026-10-09 evening).
- **What remains:** the driver's own objects put about 9.5 KB of DEBUG data into any `-d` build (`demo_hub75_text` 9,488, `demo_hub75_color` 9,657, `demo_hub75_scroll` 9,535 bytes; measured as the `-d` `.bin` minus the plain `.bin`), from about 120 `debug()` statements, most in `isp_hub75_rgb3bit.spin2` (43) and `isp_hub75_hwBufferAccess.spin2` (35). A program has about 6 KB left for its own `debug()` text before output can stop silently. Recorded in the 4.0.0 ChangeLog Known Issues.
- **Levers:** move the driver's `debug()` prose into `DAT` strings emitted with `zstr_()` (keep a literal on each side of a `zstr_()` so the debugger adds no ", "); put verbose startup tracing on `debug[N]()` channels under a per-object `DEBUG_MASK`, off by default, keeping the `HUB75:` wiring messages users need.
- **Bears on:** every user who builds with `-d`; the next release's Known Issues line.

### FM6124 and FM6126A: CLK-to-SDO delay not read against the chain clock (finding, 2026-10-07)

- **Found:** 2026-10-07, «#110». Two chained MBI5124GP panels lost or gained red in the first column of each panel at 22.3 MHz: a chip's rated clock is one chip's, and in a chain the period must also cover the CLK-to-SDO delay plus the next chip's SDI setup. The MBI5124GP now runs at that limit (18.9 MHz; `DOCs/ChipCharacteristicsMatrix.md`, ratings notes).
- **Checked:** ICN2037 (35 + 5 ns, 25.0 MHz) and ICN2038S (30 + 5 ns, 28.6 MHz) are within the 25 MHz the 20 ns pulses allow; no change.
- **Not read:** the FM6124 and FM6126A datasheets (`DOCs/FM6124/`, `DOCs/FM6126A/`) are font-encoded and need a visual read of their timing tables. FM6126A chains have run correctly (multi-panel tested); the FM6124 has run only as one panel.
- **Bears on:** FM6124 chains, and whether `MAX_CLK_HZ_FM6124` / `MAX_CLK_HZ_FM6126A` need a chain limit like the MBI5124GP's.

### `display.showFrameSet()` has run only with NULL (test written, not yet run)

- **Found:** 2026-10-05, by the FRAME-RATE closeout audit (§3 verify).
- **What:** `test_hub75_rates.spin2` calls `display.showFrameSet()` only with NULL (refused, PASS). Its accepted path (a valid, caller-built frame set taken by the refresh cog) and its refusal of a foreign address have never run. Nothing in the driver or demos calls it; its first user is the slideshow sprint.
- **Test written:** `DOCs/plans/2026-10-05-showFrameSet-test-checks.patch` adds `showIdleFrameSet()`: copy the set on display into the idle set, post it with `showFrameSet()`, and have the take check expect one more take; then offer the screen buffer's address, which must be refused. Kept out of the tree because it has not completed a run.
- **Not known:** why its one run (single FM6126A, `driver/logs/headless_261005-165311.log`) went silent after the last test pattern at 16:54:06, before reaching the new code. Likely the DEBUG data cap (see the `debug()` footprint item above): on 2026-10-09 the same program's output died at the same point, the first workload report after the last pattern, when its DEBUG data passed about 15.2 KB; the patch adds more `debug()` text. Not yet re-run to confirm. The same path passed at 16:22 (`-162211`). Stephen stopped further runs before release.
- **Bears on:** 4.0.0's `showFrameSet()` claim; the slideshow sprint.

### Brightness floor: settings 1-11 look the same on the quad rig (behaviour, measured; disposition: punch list, Stephen 2026-10-05)

- **Found:** 2026-10-04 at visit C «#94» (`DOCs/bench/RUN-NOTES.md`, visit C: brightness 1 gave 3.6% lit, the chip-minimum floor).
- **What:** the refresh core floors the lit unit L (`L = T x b / 256`) at the chip's minimum /OE pulse once per frame (`driver/isp_hub75_rgb3bit.spin2`, the `fge litUnitClocks, minOeClocks` at frame start), and every plane scales from L. On the quad at 8-bit (ICN2037, 60 ns) that floor is about 4% of full brightness, so settings 1-11 give the same light. This is the designed behaviour, and `setBrightness` documents it.
- **Option on record:** floor each plane separately (lit = max(2^k x L, minimum /OE)), two instructions per plane outside the shift. Brightness would keep falling to about 0.4% at setting 1 (calculated); the cost is that the darkest colours' low bits are over-weighted at the lowest settings.
- **Bears on:** use of the very bright panels in dark rooms.

### Panel-centric clipping looks up the panel for every pixel on diagonal lines (efficiency, not measured)

- **Found:** 2026-10-02, by the «#86» cleanup review.
- **What:** a panel-centric sloped line or single pixel is clipped by calling `hub75Bffrs.positionAtDisplayPixel()` for every pixel: `drawPixelInternal()` in `driver/isp_hub75_display.spin2` does it in its `DRAW_CLIP_TO_PANEL` branch, and `plotLineLowInternal()` / `plotLineHighInternal()` reach it through `drawPixelInternal()` because only a whole-display line in one color takes the one-plot-context PASM path (`isFastPlot()`). Each call validates the chain index, compares the pixel against the display's bounds, does two divisions and reads the mounted cell table. Straight runs (horizontal and vertical lines, boxes, fills) are clipped once per run against the panel's rectangle (`drawLineRun()`), so they do not pay it.
- **Cheaper:** compute the target panel's rectangle once per call (`offsetToPanel` and the panel's size in rows and columns) and clip each pixel with four compares, or clip the line's end points once.
- **Not known:** the saving; it has not been measured.
- **Bears on:** nothing in 4.0.0; a candidate for a performance pass.

### Cube fold path: about five method calls per face pixel (efficiency, estimated, not measured)

- **Found:** 2026-10-02, by the «#80» cleanup review.
- **What:** a face-centric pixel goes drawFoldedPixel -> cube.homeFoldToDisplay -> turnFaceCoords (home) -> foldPoint -> turnFaceCoords (face) -> drawPixelAtRC (`driver/isp_hub75_display.spin2`, `driver/isp_hub75_cube.spin2`, and `drawPixelAtRC` in `driver/isp_hub75_screenUtils.spin2`; the scroller's `plotFacePixel` in `driver/isp_hub75_scrollingText.spin2` is the same). Cheaper: in faceHomeOf, compose the home transform with the home face's face-to-panel transform and cell origin into one affine once per object. Per pixel, apply it with one unsigned on-face test, and call foldPoint only for off-face pixels. That saves about 3 calls on the usual pixel.
- **Not known:** the real cost; there is no cube to time it on. Measure at the six-panel bench.
- **Bears on:** face scrolling speed on a real cube (panel sweep).

### Face drawing's home transform is hidden state (design, low risk today)

- **Found:** 2026-10-02, by the «#80» cleanup review.
- **What:** faceHomeOf writes the home transform into display VAR (faceHomeTurn/AddRow/AddColumn), and drawFoldedPixel reads it later. The scroller keeps its own copy plus eFaceHome. A call site does not show that a draw depends on state left by an earlier call, so a nested or interleaved face draw from another context would use the wrong home. Today all drawing runs in one cog, one call at a time, so it cannot happen.
- **More general:** make the home one record (a STRUCT, or the composed affine above) that cube.homeOnFaceOfExtent returns and the draw path carries; scrollFaceTextAtRCOfColor would then take 7 parameters instead of 10.
- **Also:** face text spaces characters with FACE_TEXT_GAP_PIX while grid text uses horizontalGapInPix (spacing defined twice), and display recomputes the scroller's window width to find the extent (the formula lives in two places).
