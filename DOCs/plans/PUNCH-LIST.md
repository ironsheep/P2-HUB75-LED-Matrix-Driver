# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

### FM6124 and FM6126A: CLK-to-SDO delay not read against the chain clock (finding, 2026-10-07)

- **Found:** 2026-10-07, «#110». Two chained MBI5124GP panels lost or gained red in the first column of each panel at 22.3 MHz: a chip's rated clock is one chip's, and in a chain the period must also cover the CLK-to-SDO delay plus the next chip's SDI setup. The MBI5124GP now runs at that limit (18.9 MHz; `DOCs/ChipCharacteristicsMatrix.md`, ratings notes).
- **Checked:** ICN2037 (35 + 5 ns, 25.0 MHz) and ICN2038S (30 + 5 ns, 28.6 MHz) are within the 25 MHz the 20 ns pulses allow; no change.
- **Not read:** the FM6124 and FM6126A datasheets (`DOCs/FM6124/`, `DOCs/FM6126A/`) are font-encoded and need a visual read of their timing tables. FM6126A chains have run correctly (multi-panel tested); the FM6124 has run only as one panel.
- **Bears on:** FM6124 chains, and whether `MAX_CLK_HZ_FM6124` / `MAX_CLK_HZ_FM6126A` need a chain limit like the MBI5124GP's.

### `display.showFrameSet()` has run only with NULL (test written, not yet run)

- **Found:** 2026-10-05, by the FRAME-RATE closeout audit (§3 verify).
- **What:** `test_hub75_rates.spin2` calls `display.showFrameSet()` only with NULL (refused, PASS). Its accepted path (a valid, caller-built frame set taken by the refresh cog) and its refusal of a foreign address have never run. Nothing in the driver or demos calls it; its first user is the slideshow sprint.
- **Test written:** `DOCs/plans/2026-10-05-showFrameSet-test-checks.patch` adds `showIdleFrameSet()`: copy the set on display into the idle set, post it with `showFrameSet()`, and have the take check expect one more take; then offer the screen buffer's address, which must be refused. Kept out of the tree because it has not completed a run.
- **Not known:** why its one run (single FM6126A, `driver/logs/headless_261005-165311.log`) went silent after the last test pattern at 16:54:06, before reaching the new code. The same path passed at 16:22 (`-162211`). Stephen stopped further runs before release.
- **Bears on:** 4.0.0's `showFrameSet()` claim; the slideshow sprint.

### Brightness floor: settings 1-11 look the same on the quad rig (behaviour, measured; disposition: punch list, Stephen 2026-10-05)

- **Found:** 2026-10-04 at visit C «#94» (`DOCs/bench/RUN-NOTES.md`, visit C: brightness 1 gave 3.6% lit, the chip-minimum floor).
- **What:** the refresh core floors the lit unit L (`L = T x b / 256`) at the chip's minimum /OE pulse once per frame (`driver/isp_hub75_rgb3bit.spin2`, the `fge litUnitClocks, minOeClocks` at frame start), and every plane scales from L. On the quad at 8-bit (ICN2037, 60 ns) that floor is about 4% of full brightness, so settings 1-11 give the same light. This is the designed behaviour, and `setBrightness` documents it.
- **Option on record:** floor each plane separately (lit = max(2^k x L, minimum /OE)), two instructions per plane outside the shift. Brightness would keep falling to about 0.4% at setting 1 (calculated); the cost is that the darkest colours' low bits are over-weighted at the lowest settings.
- **Bears on:** use of the very bright panels in dark rooms.

### ICN2038S scan setting contradicts its address lines (finding, not yet explained)

- **Found:** 2026-10-01, while writing the THEOPS glossary's scan entry («#68»).
- **What:** `getDriverFlags()` gives `CHIP_ICN2038S` the `SCAN_4` flag (`driver/isp_hub75_hwBufferAccess.spin2`, the ICN2038S branch), and `DOCs/ChipCharacteristicsMatrix.md` (ICN2038S section) and `DOCs/AuthorTestConfigurations.md` (Configuration 12) call it 1/8 scan. But the same docs describe it as a 64×64 panel with `ADDR_ABCDE`, which is 32 row addresses: 64 ÷ 32 = 2 rows lit at once (1/32 scan). `SCAN_4` selects the four-rows-at-once conversion (`convertScreen2PWM_14`, chosen at `driver/isp_hub75_display.spin2` in `commitScreenToPanelSet`). Either the flag, the address-line setting or the panel description is wrong.
- **Not known:** which of the three is wrong. The docs say this panel works in a production road-sign display, so the code may be right and the description wrong.
- **Bears on:** the limits table (§11, «#82») and the scan-term switch in the other docs («#85»). Settle it before «#85» writes a scan value for this chip.

### Panel-centric clipping looks up the panel for every pixel on diagonal lines (efficiency, not measured)

- **Found:** 2026-10-02, by the «#86» cleanup review.
- **What:** a panel-centric line or pixel is clipped by calling `hub75Bffrs.positionAtDisplayPixel()` for every pixel (`driver/isp_hub75_display.spin2`, `drawLineInternal` / `drawPixelInternal` with `clipPanel`). Each call validates the chain index and does two divisions and a table read. The design predates «#86»; «#86» moved the lookup onto mounted tables without changing its cost.
- **Cheaper:** compute the target panel's rectangle once per call (`offsetToPanel` + `cellSizeInPixels`) and clip each pixel with four compares, or clip the line's endpoints once.
- **Not known:** the saving; panel-centric drawing is a small part of the boundary test's 191,538 µs.
- **Bears on:** nothing in this sprint; a candidate for a performance pass.
- **Narrowed 2026-10-05:** «#100» clips straight runs (horizontal and vertical lines, boxes, fills) once per run against the panel's rectangle (`driver/isp_hub75_display.spin2`, about :1514-1527). A panel-centric diagonal line or single pixel still calls `positionAtDisplayPixel()` per pixel (about :1623).

### Cube fold path: about five method calls per face pixel (efficiency, estimated, not measured)

- **Found:** 2026-10-02, by the «#80» cleanup review.
- **What:** a face-centric pixel goes drawFoldedPixel -> cube.homeFoldToDisplay -> turnFaceCoords (home) -> foldPoint -> turnFaceCoords (face) -> drawPixelAtRC (`driver/isp_hub75_display.spin2`, `driver/isp_hub75_cube.spin2`; the scroller's plotFacePixel is the same). Cheaper: in faceHomeOf, compose the home transform with the home face's face-to-panel transform and cell origin into one affine once per object. Per pixel, apply it with one unsigned on-face test, and call foldPoint only for off-face pixels. That saves about 3 calls on the usual pixel.
- **Not known:** the real cost; there is no cube to time it on. Measure at the six-panel bench.
- **Bears on:** face scrolling speed on a real cube (panel sweep).

### Face drawing's home transform is hidden state (design, low risk today)

- **Found:** 2026-10-02, by the «#80» cleanup review.
- **What:** faceHomeOf writes the home transform into display VAR (faceHomeTurn/AddRow/AddColumn), and drawFoldedPixel reads it later. The scroller keeps its own copy plus eFaceHome. A call site does not show that a draw depends on state left by an earlier call, so a nested or interleaved face draw from another context would use the wrong home. Today all drawing runs in one cog, one call at a time, so it cannot happen.
- **More general:** make the home one record (a STRUCT, or the composed affine above) that cube.homeOnFaceOfExtent returns and the draw path carries; scrollFaceTextAtRCOfColor would then take 7 parameters instead of 10.
- **Also:** face text spaces characters with FACE_TEXT_GAP_PIX while grid text uses horizontalGapInPix (spacing defined twice), and display recomputes the scroller's window width to find the extent (the formula lives in two places).
