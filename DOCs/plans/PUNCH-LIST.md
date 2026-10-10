# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

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

### ICN2038S scan setting contradicts its address lines (finding, not yet explained)

- **Found:** 2026-10-01, while writing the THEOPS glossary's scan entry («#68»).
- **What:** `getDriverFlags()` gives `CHIP_ICN2038S` the `SCAN_4` flag (`driver/isp_hub75_hwBufferAccess.spin2`, the ICN2038S branch), and `DOCs/ChipCharacteristicsMatrix.md` (ICN2038S section) and `DOCs/AuthorTestConfigurations.md` (Configuration 12) call it 1/8 scan. But the same docs describe it as a 64×64 panel with `ADDR_ABCDE`, which is 32 row addresses: 64 ÷ 32 = 2 rows lit at once (1/32 scan). `SCAN_4` selects the four-rows-at-once frame-set layout (`convertScreen2PWM_14()` in `driver/isp_hub75_panel.spin2`, chosen in `commitScreenToPanelSet()` in `driver/isp_hub75_display.spin2`) and doubles the columns the refresh core shifts per row address. Either the flag, the address-line setting or the panel description is wrong.
- **Not known:** which of the three is wrong. The docs say this panel works in a production road-sign display, so the code may be right and the description wrong.
- **Bears on:** the limits table (§11, «#82») and the scan-term switch in the other docs («#85»). Settle it before «#85» writes a scan value for this chip.

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
