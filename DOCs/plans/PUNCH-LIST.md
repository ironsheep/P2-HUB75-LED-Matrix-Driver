# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

### ICN2038S scan setting contradicts its address lines (finding, not yet explained)

- **Found:** 2026-10-01, while writing the THEOPS glossary's scan entry («#68»).
- **What:** `getDriverFlags()` gives `CHIP_ICN2038S` the `SCAN_4` flag (`driver/isp_hub75_hwBufferAccess.spin2`, the ICN2038S branch), and `DOCs/ChipCharacteristicsMatrix.md` (ICN2038S section) and `DOCs/AuthorTestConfigurations.md` (Configuration 12) call it 1/8 scan. But the same docs describe it as a 64×64 panel with `ADDR_ABCDE`, which is 32 row addresses: 64 ÷ 32 = 2 rows lit at once (1/32 scan). `SCAN_4` selects the four-rows-at-once conversion (`convertScreen2PWM_14`, chosen at `driver/isp_hub75_display.spin2` in `commitScreenToPanelSet`). Either the flag, the address-line setting or the panel description is wrong.
- **Not known:** which of the three is wrong. The docs say this panel works in a production road-sign display, so the code may be right and the description wrong.
- **Bears on:** the limits table (§11, «#82») and the scan-term switch in the other docs («#85»). Settle it before «#85» writes a scan value for this chip.

### Refresh core may send a row past the end of a line-buffer load (finding, reasoned from code, not measured)

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

