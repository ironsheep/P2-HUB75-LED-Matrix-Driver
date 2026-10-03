# Rig state

**Class: current state.** Written by the executing (macOS + hardware) side. It
holds one record: the rig as it is now. Replace the record when the rig changes,
and never append. Keep a prior note only if a reader would act differently for
having read it.

## Now

Recorded 2026-10-03, after FRAME-RATE bench visit A.

- **P2 board:** on `/dev/tty.usbserial-Parw7ukt` (load with
  `pnut-term-ts -r <bin> -p Parw7ukt --headless --timeout N`; logs go to
  `driver/logs/`).
- **Adapter:** one HUB75 adapter on P16-P31 (DISP0). The prototype's monitors use
  P13-P15 inside the P2 (smart-pin input reach ±3), with no external leads.
- **Panel cabled now:** the orange 1 × 64×32 FM6124 (ABCD), the last panel of
  visit A. This does **not** match the committed `isp_hub75_hwPanelConfig.spin2`,
  which describes the quad rig.
- **The quad rig** (re-cabled for the sprint's later visits): 2 × 2 of 128×64
  ICN2037, ADDR_ABCDE, every arrow down, the adapter into C0 (bottom left from the
  front). Full white draws 120 W at 82.2% lit.
- **Power:** not recorded.
- **Other single panels on hand:** 1 × 64×32 FM6126A (ABCD) and the green
  1 × 64×32 MBI5124GP (ABC, 1/8 scan).
