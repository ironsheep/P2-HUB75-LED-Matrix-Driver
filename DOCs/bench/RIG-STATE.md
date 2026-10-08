# Rig state

**Class: current state.** Written by the executing (macOS + hardware) side. It
holds one record: the rig as it is now. Replace the record when the rig changes,
and never append. Keep a prior note only if a reader would act differently for
having read it.

## Now

Recorded 2026-10-08, the quad recabled for the 4.0.0 release certification
(Stephen: "starting with a quad that's already attached").

- **P2 board:** on `/dev/tty.usbserial-Parw7ukt` (load with
  `pnut-term-ts -r <bin> -p Parw7ukt --headless --timeout N`; logs go to
  `driver/logs/`).
- **Adapter:** one HUB75 adapter on P16-P31 (DISP0). The prototype's monitors use
  P13-P15 inside the P2 (smart-pin input reach ±3), with no external leads.
- **Panel cabled now:** the quad, 2 × 2 of 128×64 ICN2037 (1/32 scan,
  ADDR_ABCDE), 256×128. This **matches** the committed
  `isp_hub75_hwPanelConfig.spin2`: `C0 = FIRST_PANEL | ARROW_DOWN`,
  `C1 = RIGHT_OF | C0`, `C2 = ABOVE | C0`, `C3 = RIGHT_OF | C2`, all arrows down,
  8-bit, 60 Hz target. Builds need no scratch config.
- **Power:** not recorded.
- **Other panels on hand:** two green MBI5124GP 64×32 (1/8 scan, ADDR_ABC; chained
  as 128×32 they need a scratch config: `C0 = FIRST_PANEL | ARROW_UP`,
  `C1 = LEFT_OF | C0 | ARROW_UP`, C0 the right-hand panel from the front), 1 ×
  64×32 FM6126A (ABCD) and the orange 1 × 64×32 FM6124 (ABCD).
