# Bench run notes

**Class: append-only log.** Written by the executing (macOS + hardware) side.
Never pruned and never re-cut. The authoring side reads it and does not edit it.
Each hand-back adds one dated entry with three parts: tree state (scoped to
`driver/*.spin2`), the observation rather than a verdict, and which steps completed.

## Entries

### 2026-10-03 — FRAME-RATE visit A, quad rig only (prototype `test_hub75_oe_bcm.spin2`)

**Tree:** `driver/*.spin2` at `4b172e7` plus uncommitted prototype edits (second frame set, one-decimal print, checkerboard first), committed after this entry.
**Rig:** 4 × 128×64 ICN2037 on P16-P31, 512 column clocks, 32 row addresses, 335 MHz; prototype at 8-bit, T = 512 clocks (j = 4), shift while lit; loaded to RAM with `pnut-term-ts -r test_hub75_oe_bcm.bin -p Parw7ukt --headless --timeout N`.

**Observed:**
- Run 1 (`driver/logs/headless_261002-235012.log`):
  - Monitors steady for 60 s: LATCH 16,882-16,887/s, so refresh 65.95 Hz (model 66.98). The refresh cog counted 66 frames/s. /OE lit 82.25% (model 83.5). CLK 8.645 M rises/s (model 8.78).
  - Stephen saw the panels "paint one by one in interesting order". The cause was the Spin2 pattern build writing into the frame set on show, in cable order C0-C3.
  - Stephen: "yes all appear to be correct" (grey ramp, colour bands, solid R/G/B/W).
- Run 2 (`driver/logs/headless_261003-000720.log`):
  - Patterns are now built in the second frame set and switched at a frame start. Stephen: "geez thats fast! full display at once paint looks great!"
  - The monitors read the same as run 1. The checkerboard was shown first.
  - Stephen: "fyi white is 120watt" (full white at 82.2% lit).
- Instrument check (`OE_UNIT_ERROR_SCALE = 2`, T = 1,024): lit 92.0%, refresh 36.9 Hz, against the T = 512 model of 83.5% and 66.9 Hz. The duty monitor shows the difference. The prediction for T = 1,024 is about 93.8% and 37.6 Hz.
- After the check ended the board kept running the T = 1,024 build. Stephen: "wait now there's a noticable flciker", at **36.9 Hz**. The normal build was reloaded: 65.9 Hz, 82.2%.

**Steps completed:** visit A on the quad rig. Image correct by eye, refresh and duty within 5% of the model, instrument negative case measured. Open: the checkerboard ghosting verdict. FM6126A and MBI5124GP are held until Stephen says.

