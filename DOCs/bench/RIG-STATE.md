# Rig state

**Class: current state.** Written by the executing (macOS + hardware) side. It
holds one record: the rig as it is now. Replace the record when the rig changes,
and never append. Keep a prior note only if a reader would act differently for
having read it.

## Now

Recorded 2026-10-07, two green MBI5124GP panels chained («#110»).

- **P2 board:** on `/dev/tty.usbserial-Parw7ukt` (load with
  `pnut-term-ts -r <bin> -p Parw7ukt --headless --timeout N`; logs go to
  `driver/logs/`).
- **Adapter:** one HUB75 adapter on P16-P31 (DISP0). The prototype's monitors use
  P13-P15 inside the P2 (smart-pin input reach ±3), with no external leads.
- **Panel cabled now:** two green MBI5124GP 64×32 panels (1/8 scan, ADDR_ABC),
  landscape, chained end to end as one 128×32 display. The adapter plugs into C0,
  the right-hand panel from the front; C1 is to its left; both arrows up. This
  does **not** match the committed `isp_hub75_hwPanelConfig.spin2` (the quad):
  bench runs use a scratch copy with `CHIP_MBI5124GP`, `ADDR_ABC`, 64×32,
  `C0 = FIRST_PANEL | ARROW_UP`, `C1 = LEFT_OF | C0 | ARROW_UP`. The identify
  image drew 41.5 W (8.2 A).
- **Quad rig:** 2 × 2 of 128×64 ICN2037, the committed config, not cabled now.
- **Power:** not recorded.
- **Other single panels on hand:** 1 × 64×32 FM6126A (ABCD), the orange 1 × 64×32 FM6124 (ABCD) and the two green
  MBI5124GP panels above.
