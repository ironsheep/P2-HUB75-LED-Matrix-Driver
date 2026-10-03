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

**Steps completed:** visit A on the quad rig. Image correct by eye, refresh and duty within 5% of the model, instrument negative case measured. Checkerboard (one-pixel white/black), Stephen: "inbetween whites the others are black", so no ghosting from shifting while lit. Not separately confirmed: that the flicker was gone after the normal build was reloaded (the monitors read 65.9 Hz). FM6126A and MBI5124GP are held until Stephen says.


### 2026-10-03 — FRAME-RATE visit A, single FM6126A (prototype `test_hub75_oe_bcm.spin2`)

**Tree:** `driver/*.spin2` at `28b2263` plus an uncommitted `isp_hub75_hwPanelConfig.spin2` edit for the bench: DISP0 = one 64×32 FM6126A, ADDR_ABCD, C0 only (C1-C3 NO_PANEL). The prototype is unchanged.
**Rig:** 1 × 64×32 FM6126A on P16-P31, 64 column clocks, 16 row addresses, 335 MHz; prototype at 8-bit, T = 512 clocks (j = 1), shift while lit, overlapped latch (LATCH high over the last 3 columns), FM6126A register init run; loaded to RAM with `pnut-term-ts -r test_hub75_oe_bcm.bin -p Parw7ukt --headless --timeout 75`.

**Observed** (`driver/logs/headless_261003-121958.log`):
- Monitors steady over the run: LATCH 19,899-19,904/s, so refresh 155.4 Hz (model 159.0, −2.2%). The refresh cog counted 155-156 frames/s. /OE lit 96.9% (model 99.1%). CLK 1.274 M rises/s (model 1.303 M).
- Patterns cycled every 10 s, checkerboard first, then grey ramp, RGB bands, solid R/G/B/W.
- Stephen: "no ghosting, colors look good."
- Stephen: "full white 17.6 watt".

**Steps completed:** visit A on the single FM6126A. The overlapped latch gives a correct image with one shift per plane, and refresh and duty are within 5% of the model. The MBI5124GP is next.

### 2026-10-03 — FRAME-RATE visit A, single MBI5124GP (prototype `test_hub75_oe_bcm.spin2`)

**Tree:** `driver/*.spin2` at `5fb9bfd` plus an uncommitted `isp_hub75_hwPanelConfig.spin2` edit for the bench: DISP0 = one 64×32 MBI5124GP (the green 1/8-scan panel), ADDR_ABC, C0 only. The prototype is unchanged. The edit was reverted after the run.
**Rig:** 1 × 64×32 MBI5124GP on P16-P31, SCAN_4 path: 8 row addresses × 128 column clocks, 335 MHz; prototype at 8-bit, T = 512 clocks (j = 2), **shift while lit**, latch at end (enclosed), no chip init (the driver has none for this chip); loaded to RAM with `pnut-term-ts -r test_hub75_oe_bcm.bin -p Parw7ukt --headless --timeout 75`.

**Observed** (`driver/logs/headless_261003-122254.log`):
- Monitors steady over the run: LATCH 19,660-19,680/s, so refresh 307.4 Hz (model 313.1, −1.8%). The refresh cog counted 307-308 frames/s. /OE lit 95.8% (model 97.6%). CLK 2.519 M rises/s (model 2.566 M).
- Patterns cycled every 10 s, checkerboard first, then grey ramp, RGB bands, solid R/G/B/W.
- Stephen: "no ghosting, good colors".
- Stephen: "white 39.93 watt".

**Steps completed:** visit A on the single MBI5124GP. The chip shows a correct image while shifting in the lit time, so shift-while-dark is not needed for it. Refresh and duty are within 5% of the model. Visit A is complete on all three panels.

### 2026-10-03 — FRAME-RATE visit A, single FM6124 (prototype `test_hub75_oe_bcm.spin2`)

**Tree:** `driver/*.spin2` at `4bde095` plus an uncommitted `isp_hub75_hwPanelConfig.spin2` edit for the bench: DISP0 = one 64×32 FM6124 (the orange Hackerbox panel), ADDR_ABCD, C0 only. The prototype is unchanged. The edit was reverted after the run.
**Rig:** 1 × 64×32 FM6124 on P16-P31, 64 column clocks, 16 row addresses, 335 MHz; prototype at 8-bit, T = 512 clocks (j = 1), **shift while lit**, latch at end (enclosed), no chip init (chip flags $0000); loaded to RAM with `pnut-term-ts -r test_hub75_oe_bcm.bin -p Parw7ukt --headless --timeout 75`.

**Observed** (`driver/logs/headless_261003-123759.log`):
- Monitors steady over the run: LATCH 19,903-19,904/s, so refresh 155.4 Hz (model 159.0, −2.2%). The refresh cog counted 155-156 frames/s. /OE lit 96.9% (model 99.1%). CLK 1.274 M rises/s (model 1.303 M). The same as the FM6126A run, which has the same geometry and timing.
- Patterns cycled every 10 s, checkerboard first, then grey ramp, RGB bands, solid R/G/B/W.
- Stephen: "no ghosting, colors good".
- Stephen: "14.27 watts" (full white).

**Steps completed:** visit A on the single FM6124, offered by Stephen after the plan was marked ready. The chip shows a correct image while shifting in the lit time.

### 2026-10-03 — FRAME-RATE visit B, quad rig, today's refresh core (`test_hub75_rates.spin2`)

**Tree:** `driver/*.spin2` at `9a695c5`, plus a temporary edit of `DISP0_COLOR_DEPTH` in `isp_hub75_hwPanelConfig.spin2` for each depth. The file was restored to `9a695c5` after the sweep (`git diff` empty). The negative-limb and base-0 runs used a scratch copy of `driver/` outside the tree.
**Rig:** quad rig, 2 x 2 of 128x64 ICN2037 on P16-P31, 512 column clocks, 32 row addresses, 335 MHz, today's refresh core (16 clocks per column). Stephen: "yes, quad ready and powered". For each depth: `pnut-ts -d -l -m test_hub75_rates.spin2`, then `pnut-term-ts -r test_hub75_rates.bin -p Parw7ukt --headless --timeout 90 --end-marker END_SESSION`.

**Observed** (`driver/logs/headless_261003-154011.log` 8-bit, `-154341` 7, `-154450` 6, `-154557` 5, `-154702` 4, `-154804` 3). Refresh is computed from the LATCH counts over 15 windows (printed figures truncate to 0.1 Hz):

| Depth | Refresh (Hz) | THEOPS (Hz) | Diff | /OE lit | Commit (ms) | Draw fill / lines / text / BMP (ms) |
|---|---|---|---|---|---|---|
| 3 | 177.18 | 177 | +0.1% | 97.3% | 9.50 | 636.2 / 234.9 / 1,108.6 / 306.0 |
| 4 | 82.68 | 82 | +0.8% | 97.4% | 11.84 | 636.2 / 236.0 / 1,113.0 / 306.9 |
| 5 | 40.01 | 40.1 | -0.2% | 97.4% | 14.19 | 636.2 / 237.1 / 1,118.3 / 307.6 |
| 6 | 19.69 | 19.7 | -0.1% | 97.4% | 16.54 | 636.2 / 238.2 / 1,123.6 / 308.5 |
| 7 | 9.77 | 9.6 | +1.7% | 97.4% | 18.89 | 636.2 / 239.3 / 1,128.9 / 309.4 |
| 8 | 4.86 | 4.6 | +5.7% | 97.4% | 21.24 | 636.2 / 240.4 / 1,134.2 / 310.3 |

- LATCH 39,687-39,690/s at every depth. The frame-start strobe (P9) averages 4.87/s at 8-bit and 177.13/s at 3-bit, agreeing with the LATCH figure.
- Row and plane strobes (P10, P11) count 39,689-39,690/s, the same as LATCH: the monitors catch the 2-clock strobe pulses.
- CLK 20.32 M rises/s mean. The printed "high 29.8 ns" includes the row gaps, where CLK idles high.
- The command strobe (P8) read 0 throughout. It fires only when the command code changes, and every commit reposts `CMD_SHOW_PWM_BUFFER`, so today's core has no "command taken" event to mark.

**Verdict:** depths 3-7 within 2% of THEOPS's logic-analyzer table. 8-bit is +5.7%, which is outside 5%. Diagnosed as THEOPS's figure: the LATCH rate does not change with depth, refresh is that rate divided by (2^depth - 1) x 32, and the counters match THEOPS at the four depths where its figures follow that scaling. The strobes cost 8 system clocks per row against about 8,440 (0.1%), too small to move these figures.

**Negative limb** (scratch copy, `TARGET_PANEL_HZ = 10_000_000`, 8-bit; `scratchpad/neg89/logs/headless_261003-155005.log`): `TIMING cycles/bit=33`. CLK fell to 10.00 M rises/s and refresh to 2.3 Hz (from 20.32 M and 4.86 Hz), so the counters respond.

**Base 0** (scratch copy, `DISP0_ADAPTER_BASE_PIN = PIN_GROUP_P0_P15`, nothing cabled on P0-P15; `scratchpad/neg89/logs/headless_261003-155136.log`): printed "RG3: instrument strobes P8-P11 are this adapter's own pins (base P0): strobes off" and "INSTR: monitors unavailable: the adapter at P0 owns P0-P13, which holds strobes P8-P11 and the monitor pins; none driven, none started". Draw and commit times were still reported.

**Clock low half (finding):** the exact low time is (window clocks - high clocks) / periods, because CLK idles high in the gaps. It gives 6.5 clocks (19.5 ns) against 7 clocks (20.9 ns) on paper at 16 cycles per column, and 14.5 against 15 at 33. The same half-clock offset at both settings points to edge asymmetry in how the monitor sees the pin. This instrument therefore resolves the 20 ns minimum only to about +/-0.5 clock (1.5 ns).

**Steps completed:** visit B. The before table exists for all six depths; the negative limb and the base-0 check are recorded.
