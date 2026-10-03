# Rig state

**Class: current state.** Written by the executing (macOS + hardware) side. It
holds one record: the rig as it is now. Replace the record when the rig changes,
and never append. Keep a prior note only if a reader would act differently for
having read it.

## Now

Recorded 2026-10-03, after FRAME-RATE bench visit A (Stephen: "quad panel now
configured and powered").

- **P2 board:** on `/dev/tty.usbserial-Parw7ukt` (load with
  `pnut-term-ts -r <bin> -p Parw7ukt --headless --timeout N`; logs go to
  `driver/logs/`).
- **Adapter:** one HUB75 adapter on P16-P31 (DISP0). The prototype's monitors use
  P13-P15 inside the P2 (smart-pin input reach ±3), with no external leads.
- **Panels:** the quad rig, 2 × 2 of 128×64 ICN2037, ADDR_ABCDE, every arrow
  down, the adapter into C0 (bottom left from the front). This matches the
  committed `isp_hub75_hwPanelConfig.spin2`.
- **Power:** not recorded. Full white on the quad rig draws 120 W at 82.2% lit.
- **Single panels used at visit A, now off the rig:** 1 × 64×32 FM6126A (ABCD)
  and the green 1 × 64×32 MBI5124GP (ABC, 1/8 scan).
