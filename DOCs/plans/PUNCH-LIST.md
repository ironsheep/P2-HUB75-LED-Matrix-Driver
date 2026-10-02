# Punch list

Active items only. Confirmed-done items are swept to a dated archive at sprint closeout.

## Active

### ICN2038S scan setting contradicts its address lines (finding, not yet explained)

- **Found:** 2026-10-01, while writing the THEOPS glossary's scan entry («#68»).
- **What:** `getDriverFlags()` gives `CHIP_ICN2038S` the `SCAN_4` flag (`driver/isp_hub75_hwBufferAccess.spin2`, the ICN2038S branch), and `Docs/ChipCharacteristicsMatrix.md` (ICN2038S section) and `DOCs/AuthorTestConfigurations.md` (Configuration 12) call it 1/8 scan. But the same docs describe it as a 64×64 panel with `ADDR_ABCDE`, which is 32 row addresses: 64 ÷ 32 = 2 rows lit at once (1/32 scan). `SCAN_4` selects the four-rows-at-once conversion (`convertScreen2PWM_14`, chosen at `driver/isp_hub75_display.spin2` in `commitScreenToPanelSet`). Either the flag, the address-line setting or the panel description is wrong.
- **Not known:** which of the three is wrong. The docs say this panel works in a production road-sign display, so the code may be right and the description wrong.
- **Bears on:** the limits table (§11, «#82») and the scan-term switch in the other docs («#85»). Settle it before «#85» writes a scan value for this chip.
