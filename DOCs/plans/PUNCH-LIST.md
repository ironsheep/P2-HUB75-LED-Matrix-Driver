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
