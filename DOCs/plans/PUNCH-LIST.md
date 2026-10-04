# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

### ICN2038S scan setting contradicts its address lines (finding, not yet explained)

- **Found:** 2026-10-01, while writing the THEOPS glossary's scan entry («#68»).
- **What:** `getDriverFlags()` gives `CHIP_ICN2038S` the `SCAN_4` flag (`driver/isp_hub75_hwBufferAccess.spin2`, the ICN2038S branch), and `DOCs/ChipCharacteristicsMatrix.md` (ICN2038S section) and `DOCs/AuthorTestConfigurations.md` (Configuration 12) call it 1/8 scan. But the same docs describe it as a 64×64 panel with `ADDR_ABCDE`, which is 32 row addresses: 64 ÷ 32 = 2 rows lit at once (1/32 scan). `SCAN_4` selects the four-rows-at-once conversion (`convertScreen2PWM_14`, chosen at `driver/isp_hub75_display.spin2` in `commitScreenToPanelSet`). Either the flag, the address-line setting or the panel description is wrong.
- **Not known:** which of the three is wrong. The docs say this panel works in a production road-sign display, so the code may be right and the description wrong.
- **Bears on:** the limits table (§11, «#82») and the scan-term switch in the other docs («#85»). Settle it before «#85» writes a scan value for this chip.

### [~] Refresh core may send a row past the end of a line-buffer load (fix applied, awaiting validation on panels)

- **Found:** 2026-10-01, by the «#72» agent while deriving the line-buffer limit.
- **What:** the refresh core sends whole rows from its line buffer until it reaches the end of each buffer load (`driver/isp_hub75_rgb3bit.spin2`, the row loop around :1020-1067). A buffer load is sized in half-rows (`pwmSubPageCount`, around :286-290). When a load holds an odd number of half-rows, the last row would be sent past the end of the buffer. That happens when floor(1024 / chain columns) is odd: for example 3 × 64 (192 columns) or 5 × 64 (320 columns). The rig (2 × 128 per row along the cable) is not affected.
- **Not known:** whether it shows on panels; no run has observed it.
- **Bears on:** plan §6 "Also in this section" (the PWM frame size and `pwmSubPageCount` come from the chain length), which edits the same lines, so «#76» is the natural place to measure and fix it. The limits table «#82» must not list a panel count this would break.
- **Resolved by «#76» (2026-10-02), by construction; not observed on panels.** The sub-page sizing (`driver/isp_hub75_rgb3bit.spin2`, after `colCtrMax` is set) now sizes a PWM row as the whole row the refresh core shifts per row address (`colCtrMax` column clocks), and a sub-page holds whole rows only, with the sub-pages tiling the frame exactly. The old sizing used half the real row. Values that changed on the «#76» harness (sub-page longs / count, HEAD → fix): 9 half-scan 32-column panels 108/10 → 72/16; 10 panels 120/10 → 80/16; 3 quarter-scan 64-column panels 120/6 → 96/8. The rig is unchanged (128/32). Proving a 9/10-panel or 3-quarter-scan chain shifts out correctly needs those panels: the panel sweep. Sweep this item at closeout.

### Converter bit-plane loop: per-plane work that could be hoisted (efficiency, estimated, not measured)

- **Found:** 2026-10-02, by the «#76» cleanup review of `driver/isp_hub75_panel.spin2`. It is existing code: «#76» changed the panel-index and slot walk around this loop, not the loop itself.
- **What:** inside the per-plane loop of both converters (`convertScreen2PWM`, the 1/2-scan path, and `convertScreen2PWM_14`, the quarter-scan path):
  - the frame-byte address is rebuilt with a MUL for every plane, where one ADD of the frame size per plane would do;
  - `currPwmBffrIdx` then becomes dead;
  - the plane loop could be a `REP` instead of a taken `DJNZ`;
  - in the quarter-scan path, the top/bottom-half test is repeated for every plane although it is constant for the row, and the bottom half does a hub `RDBYTE` read-modify-write per plane.
- **Estimate (reviewer's hand count, not measured):** about 10-15% of the half-scan converter time, more on the quarter-scan path. For scale, the rig's commit is now 14,183 us.
- **Not known:** the real saving; a harness run before and after is needed.
- **Bears on:** refresh/commit headroom in the limits table (§11, «#82»). Any change must re-run the «#76» harness (9/10/16 half-scan, 1/2/3 quarter-scan) and must show the same PASS set.

### Panel-centric clipping looks up the panel for every pixel (efficiency, not measured)

- **Found:** 2026-10-02, by the «#86» cleanup review.
- **What:** a panel-centric line or pixel is clipped by calling `hub75Bffrs.positionAtDisplayPixel()` for every pixel (`driver/isp_hub75_display.spin2`, `drawLineInternal` / `drawPixelInternal` with `clipPanel`). Each call validates the chain index and does two divisions and a table read. The design predates «#86»; «#86» moved the lookup onto mounted tables without changing its cost.
- **Cheaper:** compute the target panel's rectangle once per call (`offsetToPanel` + `cellSizeInPixels`) and clip each pixel with four compares, or clip the line's endpoints once.
- **Not known:** the saving; panel-centric drawing is a small part of the boundary test's 191,538 µs.
- **Bears on:** nothing in this sprint; a candidate for a performance pass.

### [x] Panel clock runs above the ICN2037's 20 MHz rating (finding, calculated from code)

- **Found:** 2026-10-02, by the colour-pipeline survey for Stephen's image brief.
- **What:** the refresh core sets clock cycles per column bit as `clkfreq / 20_000_000` with integer division (`driver/isp_hub75_rgb3bit.spin2`, about :324). At the demos' 335 MHz that is 16 cycles, so the panel clock is 335 / 16 = **20.94 MHz**, about 4.7% above the ICN2037's 20 MHz maximum (`DOCs/ChipCharacteristicsMatrix.md`, ICN2037 section). The comment near :1038 says "20 MHz". The rig works at this rate.
- **Not known:** whether any panel misbehaves at 20.94 MHz; whether the intent was "at most 20 MHz" (round the divisor up) or "about 20 MHz".
- **Bears on:** the limits table (§11, «#82») and refresh measurements at Visit B «#83». Rounding up (17 cycles, 19.7 MHz) would cost about 6% of refresh.
- **Resolved by «#90» (2026-10-03): the premise was wrong.** The ICN2037 is rated 30 MHz, and its 20 ns minimum clock pulse high and low caps it at 25 MHz, so 20.94 MHz is within spec. The canonical ratings are in `DOCs/ChipCharacteristicsMatrix.md` (Datasheet Clock and /OE Ratings). FRAME-RATE §5 sets the shift clock afresh. Sweep this item at closeout.

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

### Interleave the bit-plane repeats to raise the flicker rate (refresh quality, measured motivation)

- **Found:** 2026-10-02 at Visit B «#83». Stephen saw a rainbow test image at each colour depth. At 6-bit (measured 19.7 Hz full cycle) it was *"shimmering but seems to be a side-to-side shifts"*, at 5-bit (40.1 Hz) *"less shimmer"*, and at 4-bit (82 Hz) *"rock steady"*.
- **Stephen, after Visit B:** *"flicker is not location based just specific colors at this color depth"*. Colours whose light is concentrated in the MSB plane flicker most.
- **Why:** binary-coded modulation shows each plane's repeats back to back: at 5-bit the MSB plane takes 16 consecutive scans, then 8, 4, 2, 1 (`driver/isp_hub75_rgb3bit.spin2`, `cmdDsplyFrameSet`). At any instant only one plane is lit. On an image whose colour changes along a row, the lit pattern jumps across the columns phase by phase, and the eye sees that as sideways motion at the full-cycle rate.
- **Cause of the 2026-10-01 'C1 flicker' («#67», closed 2026-10-02):** the same effect. With quadPanel's hues on all four panels at once, Stephen saw *"the most flicker is cyan, next is green, all panels flicker at the same rate"*. Cyan (hue 192) has green 11000 at 5-bit (24 scans on, 7 off in one stretch) and was C1's colour in the original sighting. Green (hue 128) has blue 00100 (one short burst). Red (11111) and yellow-green were steady. It is not the panel, the ribbon, or cable position C1.
- **Candidate:** interleave the plane order within a frame set (scrambled or interleaved BCM, e.g. MSB, lower, MSB, lower ...), so the long planes spread across the cycle. The colour sums are unchanged and the visible artefact rate rises many-fold. It must keep the refresh core's timing budget, and the PWM frame layout stays as it is.
- **Bears on:** the depth a rig can use without visible shimmer (today 4-bit on this rig); the limits table's refresh column.
- **At 8-bit on today's core (2026-10-03, «#91» check, demo_hub75_quadPanel; 4.86 Hz measured at visit B «#89»):** Stephen: *"cyan has deep slow blink vs. flicker"*, then *"so does green"*. The same mechanism at a lower rate: the 8-bit default («#96») landed before the new refresh core («#92»), which removes the repeats. Verdict at visit C «#94», disposition «#95».
- **New core, phase 1 (2026-10-03, «#92», demo_hub75_quadPanel at 8-bit, 66.1 Hz measured):** Stephen: *"yes correct text/arrows/color and no flicker"*. The formal verdict (rainbow and hue images at 5-8 bit) is still visit C «#94».

### [x] Docs disagree on the ICN2037 maximum clock: 20 MHz or 30 MHz (doc conflict, settled)

- **Found:** 2026-10-02, by the DISPLAY-ORGANIZATION closeout audit.
- **What:** `DOCs/ChipCharacteristicsMatrix.md` (ICN2037 section) and the refresh core's comment (`driver/isp_hub75_rgb3bit.spin2` near the clock-target constant) say 20 MHz. `README.md`'s chip table and `DOCs/TheoryOfOperations.md` (chip timing table) say 30 MHz for ICN2037, ICN2037BP and ICN2038S. The authority is the datasheet in `DOCs/ICN2037/`, which this session could not read: no PDF tool (`pdftotext`/`pdftoppm`) is installed.
- **Bears on:** the item "Panel clock runs above the ICN2037's 20 MHz rating": if the rating is 30 MHz, 20.94 MHz is within spec and that item closes.
- **To settle:** read the clock spec in `DOCs/ICN2037/ICN2037_datasheet_EN_2017_V2.0.pdf` (e.g. after `brew install poppler`), correct whichever docs are wrong, and dispose of the clock item.
- **Resolved by «#90» (2026-10-03).** The datasheets (V1.1 throughout, V2.0 p.2/p.7) rate the ICN2037 at 30 MHz, with a 20 ns minimum pulse that caps it at 25 MHz. `DOCs/ChipCharacteristicsMatrix.md` is now the one chip table; README.md, `DOCs/TheoryOfOperations.md` and `DOCs/AuthorTestConfigurations.md` link to it, and the refresh core's comment points there. Sweep this item at closeout.

