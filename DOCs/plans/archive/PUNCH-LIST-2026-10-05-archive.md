# Punch list archive — 2026-10-05 (FRAME-RATE closeout)

Confirmed-done items swept from `DOCs/plans/PUNCH-LIST.md` at the FRAME-RATE sprint closeout. Archive files are never re-edited; a reopened item returns to the active list as a new item that references this file.

### [x] Commit takes 6.58 ms at 5-bit, not the predicted 5 ms (finding, measured, fixed 2026-10-05)

- **Found:** 2026-10-05 at visit E «#101» (`DOCs/bench/RUN-NOTES.md`, visit E; `driver/logs/headless_261005-002129.log`).
- **What:** after the MERGEB converter rewrite («#98»), commit on the quad rig measures 6.58 ms at 5-bit and 8.93 ms at 8-bit (from 14.20 and 21.25 ms). The plan's §7 predicted about 5 ms at 5-bit; that figure was calculated in the study (F10), not measured. The new converter is byte-equal to the old one (216 of 216 cases), so this is speed only.
- **Not known:** the real saving of a fix; only a converter rewrite and a rerun can give it.
- **Cause (2026-10-05, measured; `DOCs/bench/RUN-NOTES.md`, "Commit shortfall explained"):** commit is the conversion (a scratch timing of `convertHalfScan()` alone gives 6,558 / 8,906 us at 5 / 8 bit on the rig geometry). Each extra plane costs exactly 16 clocks per pixel pair. The plane stride is a multiple of 32 bytes, so all of a column's plane bytes are in one hub slice; a plane step is 9 clocks (three instructions and a `WRBYTE`), one more than the 8-clock rotation, so each write waits a whole rotation. A control geometry with the stride off the slice runs the same code at 9 clocks per plane. Every supported geometry has a slice-aligned stride.
- **Fix direction (not designed or agreed):** get a plane's hub write down to one per 8 clocks or fewer. One way: build each plane's bytes for four columns in a register (two `ROLNIB`s per plane per column, no pointer step) and write one long per plane per four columns; estimated (not measured) about 4.1 ms at 5-bit and 5.0 ms at 8-bit on the rig. Any change must pass `test_hub75_converter` (216 cases) and its fail limb.
- **Bears on:** how fast animation can commit frames; the documentation's commit figures («#102» states the measured ones).
- **Resolved by «#104» (2026-10-05, measured):** the converter batches four columns into one long per plane and block-reads the pixels; commit on the rig is 4.09 ms at 8-bit and 3.26 ms at 5-bit (`DOCs/bench/RUN-NOTES.md`, "Converter slice stall removed"). Sweep this item at closeout.

### [x] Refresh core may send a row past the end of a line-buffer load (closed 2026-10-05: the mechanism no longer exists)

- **Found:** 2026-10-01, by the «#72» agent while deriving the line-buffer limit.
- **What:** the refresh core sends whole rows from its line buffer until it reaches the end of each buffer load (`driver/isp_hub75_rgb3bit.spin2`, the row loop around :1020-1067). A buffer load is sized in half-rows (`pwmSubPageCount`, around :286-290). When a load holds an odd number of half-rows, the last row would be sent past the end of the buffer. That happens when floor(1024 / chain columns) is odd: for example 3 × 64 (192 columns) or 5 × 64 (320 columns). The rig (2 × 128 per row along the cable) is not affected.
- **Not known:** whether it shows on panels; no run has observed it.
- **Bears on:** plan §6 "Also in this section" (the PWM frame size and `pwmSubPageCount` come from the chain length), which edits the same lines, so «#76» is the natural place to measure and fix it. The limits table «#82» must not list a panel count this would break.
- **Resolved by «#76» (2026-10-02), by construction; not observed on panels.** The sub-page sizing (`driver/isp_hub75_rgb3bit.spin2`, after `colCtrMax` is set) now sizes a PWM row as the whole row the refresh core shifts per row address (`colCtrMax` column clocks), and a sub-page holds whole rows only, with the sub-pages tiling the frame exactly. The old sizing used half the real row. Values that changed on the «#76» harness (sub-page longs / count, HEAD → fix): 9 half-scan 32-column panels 108/10 → 72/16; 10 panels 120/10 → 80/16; 3 quarter-scan 64-column panels 120/6 → 96/8. The rig is unchanged (128/32). Proving a 9/10-panel or 3-quarter-scan chain shifts out correctly needs those panels: the panel sweep. Sweep this item at closeout.
- **Closed 2026-10-05 (FRAME-RATE closeout):** «#92» replaced the refresh core and deleted sub-page loading. The new core loads exactly one whole row of one plane per `SETQ` block read (`driver/isp_hub75_rgb3bit.spin2`, `rowLongsLessOne` at about :480-483, the `setq` at about :1009), so a load can no longer end part way through a row. A 3 x 64 chain is 192 column clocks (48 longs) in the 128-long line buffer. Sweep at closeout.

### [x] Converter bit-plane loop: per-plane work that could be hoisted (closed 2026-10-05: superseded)

- **Found:** 2026-10-02, by the «#76» cleanup review of `driver/isp_hub75_panel.spin2`. It is existing code: «#76» changed the panel-index and slot walk around this loop, not the loop itself.
- **What:** inside the per-plane loop of both converters (`convertScreen2PWM`, the 1/2-scan path, and `convertScreen2PWM_14`, the quarter-scan path):
  - the frame-byte address is rebuilt with a MUL for every plane, where one ADD of the frame size per plane would do;
  - `currPwmBffrIdx` then becomes dead;
  - the plane loop could be a `REP` instead of a taken `DJNZ`;
  - in the quarter-scan path, the top/bottom-half test is repeated for every plane although it is constant for the row, and the bottom half does a hub `RDBYTE` read-modify-write per plane.
- **Estimate (reviewer's hand count, not measured):** about 10-15% of the half-scan converter time, more on the quarter-scan path. For scale, the rig's commit is now 14,183 us.
- **Not known:** the real saving; a harness run before and after is needed.
- **Bears on:** refresh/commit headroom in the limits table (§11, «#82»). Any change must re-run the «#76» harness (9/10/16 half-scan, 1/2/3 quarter-scan) and must show the same PASS set.
- **Closed 2026-10-05 (FRAME-RATE closeout):** the loop it describes is gone. «#98» rewrote both converters on MERGEB as one shared `convertRowPairs()`, and «#104» rewrote its plane steps (four columns per `WRLONG`, no per-plane MUL or RDBYTE). Sweep at closeout.

### [x] Panel clock runs above the ICN2037's 20 MHz rating (finding, calculated from code)

- **Found:** 2026-10-02, by the colour-pipeline survey for Stephen's image brief.
- **What:** the refresh core sets clock cycles per column bit as `clkfreq / 20_000_000` with integer division (`driver/isp_hub75_rgb3bit.spin2`, about :324). At the demos' 335 MHz that is 16 cycles, so the panel clock is 335 / 16 = **20.94 MHz**, about 4.7% above the ICN2037's 20 MHz maximum (`DOCs/ChipCharacteristicsMatrix.md`, ICN2037 section). The comment near :1038 says "20 MHz". The rig works at this rate.
- **Not known:** whether any panel misbehaves at 20.94 MHz; whether the intent was "at most 20 MHz" (round the divisor up) or "about 20 MHz".
- **Bears on:** the limits table (§11, «#82») and refresh measurements at Visit B «#83». Rounding up (17 cycles, 19.7 MHz) would cost about 6% of refresh.
- **Resolved by «#90» (2026-10-03): the premise was wrong.** The ICN2037 is rated 30 MHz, and its 20 ns minimum clock pulse high and low caps it at 25 MHz, so 20.94 MHz is within spec. The canonical ratings are in `DOCs/ChipCharacteristicsMatrix.md` (Datasheet Clock and /OE Ratings). FRAME-RATE §5 sets the shift clock afresh. Sweep this item at closeout.

### [x] Interleave the bit-plane repeats to raise the flicker rate (refresh quality, closed: steady at 5-8 bit on the new core)

- **Found:** 2026-10-02 at Visit B «#83». Stephen saw a rainbow test image at each colour depth. At 6-bit (measured 19.7 Hz full cycle) it was *"shimmering but seems to be a side-to-side shifts"*, at 5-bit (40.1 Hz) *"less shimmer"*, and at 4-bit (82 Hz) *"rock steady"*.
- **Stephen, after Visit B:** *"flicker is not location based just specific colors at this color depth"*. Colours whose light is concentrated in the MSB plane flicker most.
- **Why:** binary-coded modulation shows each plane's repeats back to back: at 5-bit the MSB plane takes 16 consecutive scans, then 8, 4, 2, 1 (`driver/isp_hub75_rgb3bit.spin2`, `cmdDsplyFrameSet`). At any instant only one plane is lit. On an image whose colour changes along a row, the lit pattern jumps across the columns phase by phase, and the eye sees that as sideways motion at the full-cycle rate.
- **Cause of the 2026-10-01 'C1 flicker' («#67», closed 2026-10-02):** the same effect. With quadPanel's hues on all four panels at once, Stephen saw *"the most flicker is cyan, next is green, all panels flicker at the same rate"*. Cyan (hue 192) has green 11000 at 5-bit (24 scans on, 7 off in one stretch) and was C1's colour in the original sighting. Green (hue 128) has blue 00100 (one short burst). Red (11111) and yellow-green were steady. It is not the panel, the ribbon, or cable position C1.
- **Candidate:** interleave the plane order within a frame set (scrambled or interleaved BCM, e.g. MSB, lower, MSB, lower ...), so the long planes spread across the cycle. The colour sums are unchanged and the visible artefact rate rises many-fold. It must keep the refresh core's timing budget, and the PWM frame layout stays as it is.
- **Bears on:** the depth a rig can use without visible shimmer (today 4-bit on this rig); the limits table's refresh column.
- **At 8-bit on today's core (2026-10-03, «#91» check, demo_hub75_quadPanel; 4.86 Hz measured at visit B «#89»):** Stephen: *"cyan has deep slow blink vs. flicker"*, then *"so does green"*. The same mechanism at a lower rate: the 8-bit default («#96») landed before the new refresh core («#92»), which removes the repeats. Verdict at visit C «#94», disposition «#95».
- **New core, phase 1 (2026-10-03, «#92», demo_hub75_quadPanel at 8-bit, 66.1 Hz measured):** Stephen: *"yes correct text/arrows/color and no flicker"*. The formal verdict (rainbow and hue images at 5-8 bit) is still visit C «#94».
- **Closed 2026-10-04 by «#95», from visit C «#94»; no interleave needed.** The new core («#92») shows each plane once per row, weighted by /OE time, so there are no back-to-back MSB repeats left to interleave, and refresh rose from 4.86-40.0 Hz to 71-85 Hz. Stephen viewed `demo_hub75_quadPanel` (per-panel hues) and `demo_hub75_color` (rainbow sweep, hue groups and lines, palettes) at each depth (logs and method in `DOCs/bench/RUN-NOTES.md`, visit C):
  - 8-bit, 71.0 Hz measured: *"colors all look steady"*.
  - 7-bit, 75.0 Hz: *"no shimmering"*.
  - 6-bit, 79.6 Hz: *"steady"*.
  - 5-bit, 84.7 Hz: *"steady"*.
  Sweep at closeout.

### [x] Docs disagree on the ICN2037 maximum clock: 20 MHz or 30 MHz (doc conflict, settled)

- **Found:** 2026-10-02, by the DISPLAY-ORGANIZATION closeout audit.
- **What:** `DOCs/ChipCharacteristicsMatrix.md` (ICN2037 section) and the refresh core's comment (`driver/isp_hub75_rgb3bit.spin2` near the clock-target constant) say 20 MHz. `README.md`'s chip table and `DOCs/TheoryOfOperations.md` (chip timing table) say 30 MHz for ICN2037, ICN2037BP and ICN2038S. The authority is the datasheet in `DOCs/ICN2037/`, which this session could not read: no PDF tool (`pdftotext`/`pdftoppm`) is installed.
- **Bears on:** the item "Panel clock runs above the ICN2037's 20 MHz rating": if the rating is 30 MHz, 20.94 MHz is within spec and that item closes.
- **To settle:** read the clock spec in `DOCs/ICN2037/ICN2037_datasheet_EN_2017_V2.0.pdf` (e.g. after `brew install poppler`), correct whichever docs are wrong, and dispose of the clock item.
- **Resolved by «#90» (2026-10-03).** The datasheets (V1.1 throughout, V2.0 p.2/p.7) rate the ICN2037 at 30 MHz, with a 20 ns minimum pulse that caps it at 25 MHz. `DOCs/ChipCharacteristicsMatrix.md` is now the one chip table; README.md, `DOCs/TheoryOfOperations.md` and `DOCs/AuthorTestConfigurations.md` link to it, and the refresh core's comment points there. Sweep this item at closeout.
