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

### 2026-10-03 / 2026-10-04 — FRAME-RATE visit C, quad rig, new refresh core (`test_hub75_rates.spin2`)

**Tree:** `driver/*.spin2` at `9ea5959` (after «#103»). Each depth was a temporary edit of `DISP0_COLOR_DEPTH` in `isp_hub75_hwPanelConfig.spin2`, restored to `9ea5959` after each sweep (`git diff` empty). On 2026-10-04 the instrument gained the frame-set take check and the test gained brightness-step labels and 5 s brightness steps (committed with this entry). The unreachable-target run and the take check's negative limb used scratch copies of `driver/` outside the tree.
**Rig:** quad rig, 2 x 2 of 128x64 ICN2037 on P16-P31, 512 column clocks, 32 row addresses, 335 MHz, 15 clocks per column. A second P2 (another project's motor rig) was on the same Mac from 2026-10-04 on `/dev/tty.usbserial-P6yh4spg`; every load named the LED plug: `pnut-term-ts -r <bin> -p Parw7ukt --headless --end-marker --timeout 180`.

**First sweep failed (2026-10-03, `driver/logs/headless_261003-210125.log` to `-210748.log`):** refresh was below the model at every depth (8-bit 70.3 / 71.1 Hz, 3-bit 135.8 / 193.4) and brightness 128 gave 79% of full light. Two §4 defects: the /OE pulse waited up to one base period to start, and a shorter pulse period shortened the row. Fixed by «#103» (`9ea5959`); these logs are kept as the defect evidence.

**Unattended sweep on the fixed core (2026-10-03).** Model = the RG3 MODEL line, 60 Hz target:

| Depth | Refresh / model (Hz) | /OE lit / model | j chosen | Clock (M rises/s, mean) | CLK high | Commit (ms) | Draw fill / lines / text / BMP (ms) | Log |
|---|---|---|---|---|---|---|---|---|
| 8 | 71.0 / 71.1 | 83.0 / 83.1% | 4 | 9.31 | 23.9 ns | 21.25 | 635.4 / 233.3 / 1,103.0 / 304.2 | `-213601` |
| 7 | 75.0 / 75.1 | 87.4 / 87.5% | 3 | 8.61 | 23.9 ns | 18.90 | 635.4 / 232.2 / 1,097.7 / 303.4 | `-224253` |
| 6 | 79.6 / 79.6 | 91.9 / 92.0% | 2 | 7.83 | 23.9 ns | 16.55 | 635.4 / 231.0 / 1,092.4 / 302.5 | `-224433` |
| 5 | 84.7 / 84.7 | 96.3 / 96.3% | 1 | 6.94 | 23.9 ns | 14.20 | 635.4 / 229.9 / 1,087.1 / 301.7 | `-213739` |
| 4 | 90.5 / 90.5 | 99.6 / 99.6% | 0 | 5.93 | 23.9 ns | 11.86 | 635.4 / 228.8 / 1,082.7 / 300.9 | `-224607` |
| 3 | 193.3 / 193.4 | 99.2 / 99.3% | 0 | 9.50 | 23.9 ns | 9.51 | 635.4 / 227.9 / 1,077.4 / 299.8 | `-213911` |

- Every depth within 0.2% of the model on refresh and lit share; the target chose the predicted j at every depth. Handshake PASS at every depth.
- Brightness at every depth: 128 gave half the lit share of 256 with refresh unchanged; at 8-bit, 1 gave 3.6% (the chip-minimum floor) and 0 gave 0.0%.
- Unreachable target (scratch, `DISP0_TARGET_REFRESH_HZ = 200` at 8-bit; `driver/logs/scratch-unreach94_headless_261003-224750.log`, copied from the scratch run): "HUB75: DISP0: DISP0_TARGET_REFRESH_HZ = 200 Hz is out of reach for this display; running at 165.7 Hz, its fastest (j = 8)"; measured 165.0 Hz.
- The commit and draw columns are the "before" figures for §7-§9 (visit E compares against them).

**Attended part, 8-bit (2026-10-04).** Stephen at the rig.
- Runs `-172034` and `-172454` (5 s brightness steps from the second): identical to the unattended 8-bit figures. Tearing run 712 commits in 20 s.
- **Tearing, by eye and on video.** Stephen: "the tearing test seems to break the panel into 4 horizontal equally sized rows". Stephen: "I never saw white and black simultaneously. What I did see on the four rows was that they were flickering badly." Stephen: "So maybe too fast for me to distinguish". On a normal-rate phone video: "I saw them go from all white to all black, with two or three steps in between, so there's no tearing. It's the amount of pixels that were white versus black." Stephen: "the four rows were identically filled with white at each step". Verdict: consistent with no tearing, but not proof. A camera cannot tell an unlit row from the black image, so a white/black flip on a scanned panel looks the same torn or not. The four regions are the four 32-row panel halves that the shared row address scans in lockstep (2 x 2 of 1/32-scan panels): expected.
- **Tearing, by pins (the §3 acceptance from here; Stephen: "I like your pin measurement idea").** The instrument's take check catches every rise of P8 (posted set taken) as a pin event and reads the row-address pins A-E at that moment. A take at a frame boundary finds row address 31, the frame's last; the takes counted must equal the commits made. `-174204` and `-174541`: **TAKE CHECK PASS: 824 of 824 frame-set takes at a frame boundary (row address 31 on the pins), one per commit**, from the first workload commit to the end of the tearing test.
- **Take check negative limb** (scratch copy, P8 also pulsed at every row start; `driver/logs/scratch-takeneg_headless_261004-174335.log`, copied from the scratch run): **TAKE CHECK FAIL**: 128,386 takes off the boundary, 4,965 on it, 133,351 takes for 824 commits. The counts agree with the scan: about 4,141 frames ran, giving 4,141 false marks at row 31 (+ 824 real) and 31 x 4,141 = 128,371 elsewhere.
- **Brightness by eye.** Each step labelled on the panel with its step, brightness and lit share relative to full, measured from the step's second window. `-174204` first used the first window, which began before the step change, and showed 58% / 11% for the 128 / 1 steps. Fixed to the second window; `-174541` labels 100 / 50 / 4 / 0% of full from lit 83.0 / 41.5 / 3.6 / 0.0%. Stephen: "yes dimming looks good... seems to be correct".
- **Shimmer** (`demo_hub75_quadPanel` 30 s, then `demo_hub75_color` about 100 s, at each depth):
  - 8-bit (`-174900`, `-174931`): Stephen: "colors all look steady".
  - 7-bit (`-175608`, `-175639`): Stephen: "no shimmering".
  - 6-bit (`-180658`, `-180729`): Stephen: "steady".
  - 5-bit (`-181922`, `-181953`): Stephen: "steady".

**Verdicts:** §3 accepted (handshake PASS; take check PASS with its negative limb shown failing). §4 accepted (refresh and lit share within 0.2% of the model at every depth; target j as predicted; brightness linear, floor and 0 correct; unreachable target reported and run at the fastest rate). §5 accepted (CLK high 23.9 ns at every depth; the low half is 7 clocks, 20.9 ns, on paper, resolved by this instrument to about +/-0.5 clock). Shimmer steady at 5-8 bit, for «#95».

**§1 patterns on the quad (added 2026-10-04, run `driver/logs/headless_261004-204525.log`, «#97»):** the seven patterns shown at start; asked whether the grey ramp was even and the checkerboard's dark pixels stayed dark, Stephen: "even and stayed dark". This closes the §1 pattern limb visit C did not run.

**Steps completed:** visit C.

### 2026-10-05 — FRAME-RATE visit E, quad rig (`test_hub75_converter.spin2`, `test_hub75_rates.spin2`)

**Tree:** `driver/*.spin2` at `780421a` («#98» converters, «#99» colour table, «#100» row runs), plus a temporary `DISP0_COLOR_DEPTH = DEPTH_5BIT` edit for the 5-bit run, restored after it (`git diff` empty).
**Rig:** quad rig, 2 x 2 of 128x64 ICN2037 on P16-P31, 335 MHz. Loads: `pnut-term-ts -r <bin> -p Parw7ukt --headless --end-marker --timeout 500`.

**Converter equivalence** (`driver/logs/headless_261005-001919.log`): `CONVERTER TEST: 216 cases, 216 PASS, 0 FAIL`. Its fail limb was shown in «#98»: with one output bit corrupted, all 192 new-converter cases fail (`-261004-215319`).

**Commit and draw times against visit C** (8-bit `driver/logs/headless_261004-235552.log`, same code as `780421a`; 5-bit `-261005-002129`):

| Item | Visit C 8-bit | Now 8-bit | Speedup | Visit C 5-bit | Now 5-bit | Speedup | Predicted |
|---|---|---|---|---|---|---|---|
| Commit | 21.25 ms | 8.93 ms | 2.4x | 14.20 ms | 6.58 ms | 2.2x | about 5 ms at 5-bit (calculated) |
| Draw fill | 635.4 ms | 114.0 ms | 5.6x | 635.4 ms | 114.0 ms | 5.6x | — |
| Draw lines | 233.3 ms | 116.8 ms | 2.0x | 229.9 ms | 116.8 ms | 2.0x | — |
| Draw text | 1,103.0 ms | 300.9 ms | 3.7x | 1,087.1 ms | 300.9 ms | 3.6x | — |
| Draw BMP | 304.2 ms | 188.4 ms | 1.6x | 301.7 ms | 188.4 ms | 1.6x | — |

- Draw time no longer depends on colour depth: the colour table («#99») replaced the per-pixel depth arithmetic.
- Self-tests in the same runs, at both depths: `COLOUR TABLE PASS: 3_840 entries compared with the old function, none differ`; `ROW RUN PASS: 468 cases identical byte for byte, address rule equal on every layout, in 107 s`; handshake PASS; take check 1,541 of 1,541 (8-bit) and 1,815 of 1,815 (5-bit). Their fail limbs were shown in their own tasks: colour table «#99» (`-261004-221156`, 15 of 15 cases fail), row runs «#100» (`-261005-000046`, 468 fail; `-261005-000459`, 48 address-rule checks fail).
- Refresh and lit share unchanged from visit C: 71.0 Hz / 83.0% at 8-bit, 84.7 Hz / 96.3% at 5-bit.

**By eye** (`demo_hub75_quadPanel` `-261005-002615`, `demo_hub75_text` `-002725`, `demo_hub75_boundary` `-002905`): Stephen: "all three demos look good".

**Verdicts:** §7 accepted on equivalence; commit is 2.2x faster at 5-bit but misses the calculated "about 5 ms" by about 30% (6.58 ms); the shortfall is not explained yet and is on the punch list. §8 accepted (table equal to the old function; draw no longer scales with depth). §9 accepted (row runs byte-equal; draw 1.6x-5.6x faster). Demos correct by eye.

**Steps completed:** visit E.

### 2026-10-05 — Commit shortfall explained: converter timing on the quad rig's P2 (scratch program, no panels driven)

**Tree:** `driver/*.spin2` at `24ffeeb`, copied to a scratch folder with DISP0 set to no panels (so no buffers are reserved and no pins are driven); the tree was not edited. The scratch program times `isp_hub75_panel.convertHalfScan()` with `GETCT` (best of 4) at depths 3-8 on two geometries. Source kept as `driver/logs/scratch-convtime_scratch_commit_timing.spin2.txt`; log `driver/logs/scratch-convtime_headless_261005-123702.log`.
**Rig:** the quad rig's P2, `-p Parw7ukt`, 335 MHz.

| Geometry | Plane stride | 3-bit | 5-bit | 8-bit | Each extra plane |
|---|---|---|---|---|---|
| 4 x 128 x 64 (the quad rig) | 16,384 B (a multiple of 32) | 4,993 us | 6,558 us | 8,906 us | 16.0 clocks per pixel pair |
| 4 x 129 x 62 (control) | 15,996 B (not a multiple of 32) | 4,171 us | 5,031 us | 6,320 us | 9.0 clocks per pixel pair |

- The rig geometry reproduces visit E's commit times (6.58 ms at 5-bit, 8.93 ms at 8-bit) to within 0.3%, so commit is the conversion; the handshake and Spin2 overhead are about 20 us.
- **Cause:** every plane byte of one column lies in the same hub slice, because the plane stride is a multiple of 32 bytes (8 slices x 4 bytes, slice = address bits [4:2]; p2kbArchHub). A plane step is three instructions (6 clocks) and a `WRBYTE` (3 clocks at best), 9 clocks, one more than the 8-clock hub rotation, so each write waits a whole extra rotation: 16 clocks. With the stride moved off the slice (control row), the same code takes the 9-clock minimum. The study's "about 5 ms" (F10) assumed about 8 clocks per plane and did not model the slice.
- Every supported geometry has a stride that is a multiple of 32 (half a panel's rows x chain columns, with columns a multiple of 32), so every display pays this.

**Steps completed:** none of a visit; this answers the punch-list item "Commit takes 6.58 ms at 5-bit".

### 2026-10-05 — Converter slice stall removed («#104», FRAME-RATE SC-1), quad rig

**Tree:** `driver/*.spin2` at `65320a9` plus the uncommitted «#104» converter (`convertRowPairs()` in `isp_hub75_panel.spin2`), committed with this entry. Temporary `DISP0_COLOR_DEPTH = DEPTH_5BIT` for the 5-bit run and `DISP0_MAX_PANEL_COLUMNS = 126` for the width-check limb, each restored after its build (`git diff` empty).
**Rig:** quad rig, 2 x 2 of 128x64 ICN2037 on P16-P31, 335 MHz, `-p Parw7ukt`.

**Candidates** (scratch harness: each candidate timed with `GETCT`, best of 3, and compared byte for byte with the driver's converter at depths 3-8 on 4x128x64 with and without the R/B swap, 9x32x16, and quarter-scan 3x64x32; generator and harness kept as `driver/logs/scratch-cand_gen.py.txt` and `scratch-cand_mkharness.py.txt`; logs `driver/logs/scratch-cand_headless_261005-125329.log`, `-125428`, `-125555`, `-125825`). Rig geometry, converter alone:

| Method | 5-bit | 8-bit | Each extra plane, per column |
|---|---|---|---|
| Visit E converter (one `WRBYTE` per plane per column) | 6,560 us | 8,908 us | 16 clocks |
| 1: four columns batched in registers, one `WRLONG` per plane per four columns | 4,262 us | 5,289 us | 6 clocks |
| 2: as 1, plus a `SETQ` block read of each four pixels | 3,700 us | 4,580 us | 6 clocks |
| 3: as 2, columns unrolled under `SKIPF` (no call or jump per column) | 3,235 us | 4,067 us | about 5 clocks |
| 4: as 3, channel-order `MOVBYTS` under the same `SKIPF` (skipped with no swap) | 3,138 us (3,235 with a swap) | 3,969 us (4,067 with a swap) | about 5 clocks |

- Every case of every candidate was byte-equal to the driver's converter (`CT: TOTAL cases with a difference: 0` in `-125825`; the earlier logs list `diff 0` per case).
- Block writes of the planes (the plan's third candidate) were not built: after candidate 2 the plane writes cost 2 clocks per plane per column (the 6-clock slope less the two 2-clock `ROLNIB`s), which bounds their whole saving at about 4%.
- **Kept: candidate 4**, the fastest that passed.

**Equivalence** (`test_hub75_converter`, after the review cleanups): `CONVERTER TEST: 216 cases, 216 PASS, 0 FAIL` (`driver/logs/headless_261005-132139.log`). Fail limb (`HUB75_CORRUPT_CONVERTER`, temporary copy of the test): `216 cases, 24 PASS, 192 FAIL`, every new-converter case failing as in «#98» (`-132216`).

**Width check** (startup now requires panel columns to be a multiple of 4): with 126 columns, `HUB75: DISP0: panels 126 columns wide (DISP0_MAX_PANEL_COLUMNS) are not supported; the width must be a multiple of 4`, then startup stopped (`-132339`). With 128 columns the rates runs below start normally.

**Rates** (`test_hub75_rates`, the rig's config, which uses a channel swap; 8-bit `driver/logs/headless_261005-132532.log`, 5-bit `-133027`):

| Item | Visit E 8-bit | Now 8-bit | Visit E 5-bit | Now 5-bit |
|---|---|---|---|---|
| Commit | 8.93 ms | 4.09 ms | 6.58 ms | 3.26 ms |
| Refresh / lit | 71.0 Hz / 83.0% | 71.0 Hz / 83.0% | 84.7 Hz / 96.3% | 84.7 Hz / 96.3% |

- Self-tests at both depths: colour table PASS (3,840 entries), row runs PASS (468 cases), handshake PASS, take check 1,541 of 1,541 (8-bit) and 1,815 of 1,815 (5-bit).
- Draw times are within 1.2% of visit E's (fill 114.9, lines 115.4, text 301.8, BMP 186.7 ms at both depths); the draw code did not change.

**Logging note:** in every headless run, pnut-term-ts cuts off the line that arrives just before `END_SESSION` (the converter test's verdict line, the rates test's take-check line, this harness's last case line; visit C and E logs show the same). Every verdict above is read from the count line before it, which arrives whole.

**Verdict:** SC-1 met. Commit is 2.2x faster than visit E at 8-bit (2.0x at 5-bit) and 5.2x faster than visit C at 8-bit, and it is under §7's "about 5 ms" at both depths.

**Steps completed:** «#104».

### 2026-10-05 — FRAME-RATE visit D, single 64x32 panels (`test_hub75_rates.spin2`)

**Tree:** `driver/*.spin2` at `620d1c1`, plus a temporary `isp_hub75_hwPanelConfig.spin2` edit per chip: DISP0 = one 64x32 panel (`CHIP_FM6126A` / `CHIP_MBI5124GP` / `CHIP_FM6124`, `ADDR_ABCD` / `ADDR_ABC` / `ADDR_ABCD`), `C0 = FIRST_PANEL | ARROW_UP`, C1-C3 `NO_PANEL`; one build per chip and depth (`DISP0_COLOR_DEPTH` 8, then 5). Restored after the last run (`git diff` empty for the config). After the first run, two changes to `test_hub75_rates.spin2` (below) were in every later build.
**Rig:** each panel alone on the P16 adapter, 335 MHz, `pnut-term-ts -r <bin> -p Parw7ukt --headless --end-marker --timeout 500`. The pink panel is the FM6126A, the green the MBI5124GP (1/8 scan), the orange the FM6124.

| Chip | Depth | Log | Refresh | Lit | b = 128 / 1 / 0 | CLK high | Commit | Handshake | Take check |
|---|---|---|---|---|---|---|---|---|---|
| FM6126A | 8 | `headless_261005-150541` | 85.1 Hz | 99.6% | 49.8 / 1.4 / 0.0% | 1,407.5 ns (mean; see below) | 283 us | PASS | 1,825 of 1,825 at row 15 |
| FM6126A | 5 | `-151115`, viewed in `-152428` | 688.9 Hz | 97.9% | 48.9 / 1.4 / 0.0% | 258.0 ns (mean) | 231 us | PASS | 13,893 of 13,893 at row 15 |
| MBI5124GP | 8 | `-152803` | 85.4 Hz | 99.8% | 49.9 / 0.8 / 0.0% | 24.0 ns | 284 us | PASS | 1,823 of 1,823 at row 7 |
| MBI5124GP | 5 | `-153107` | 698.5 Hz | 99.2% | 49.6 / 0.8 / 0.0% | 24.0 ns | 233 us | PASS | 14,083 of 14,083 at row 7 |
| FM6124 | 8 | `-153437` | 85.3 Hz | 99.7% | 49.8 / 1.1 / 0.0% | 24.2 ns | 283 us | PASS | 1,821 of 1,821 at row 15 |
| FM6124 | 5 | `-153742` | 694.1 Hz | 98.6% | 49.3 / 1.1 / 0.0% | 24.2 ns | 231 us | PASS | 13,995 of 13,995 at row 15 |

- Startup lines: FM6126A and FM6124 S = T = 960 clocks (j = 0); MBI5124GP S = T = 1,920 clocks (128 column clocks per row address). Minimum /OE 14 / 17 / 11 clocks (40 / 50 / 30 ns ratings).
- Colour table PASS and row runs PASS (own wiring, 156 cases) on every run.
- **FM6126A clock:** the overlapped latch path holds the last clock pulse before the latch high while the previous plane goes dark, so the monitor's mean high time (1,407.5 ns at 8-bit) includes one long pulse per plane per row. It cannot show the short pulses; the >= 20 ns high half holds by construction (the same shift loop and clock as the quad, 23.9 ns at visit C), not by this run. A long high half is within the chip's rules; data is taken on the rising edge.
- **MBI5124GP quarter scan:** 699,648 clock rises/s at 85.4 Hz = 128 x 8 row addresses x 8 planes, so S uses the doubled column count.
- **FM6124 floor:** brightness 1 reads 1.1% lit, the 11-clock floor (11/960); unclamped it would be about 3.75 clocks (11 ns, 0.4%).
- **By eye (Stephen):** FM6126A 8-bit: "all patterns look correct"; 5-bit (rerun to view): "all patterns good". MBI5124GP 8-bit: "all patterns good"; 5-bit: "5-bit all good". FM6124 8-bit: "looks good"; 5-bit: "all good".
- **Tearing test by eye:** at 8-bit the flashing is visible (about 43 white/black cycles/s); at 5-bit it alternates about 345 times/s and looks solid grey (Stephen: "too fast for tearing view, just solid grey"). On the MBI5124GP at 8-bit, Stephen: "tearing this time shows four rows but line between black/white is angular this time". The four bands are the rows a 1/8-scan address lights together (m, m + 8, m + 16, m + 24). Every frame-set take was at row address 7 (take check), so no switch landed mid-frame; Stephen, on the video: "spans 2, sometimes 3 rows - white full rows, partial white rows top of three more pixles mid less and bottom of three even less... all partial rows start with white on left edge then we have full black rows". That is the phone camera's rolling shutter, which records the panel's columns a little apart in time, crossing the panel's scan (about 1.5 ms per row address at 8-bit): each row caught mid-switch shows white from the left edge to the column the camera read as it switched, and lower rows switch later. It is not a mid-frame switch; every take was at row address 7.

**Rates-test changes made during the visit** (Stephen, on the first run: "the bitmap with single panel doesn't have room for additional text, should likely disable when won't fit on display"):
- The brightness-step labels are drawn only when a label line (24 characters) fits across the display; otherwise the log says `brightness labels off: the display holds 10 text columns and a label needs 24`.
- The row-run test's two L layouts need exactly 4 panels; on another panel count they are reported `not run` instead of being counted as refused FAILs (the first FM6126A run printed `ROW RUN FAIL: 0 failed, 32 layouts refused`, all from this).
- On the quad (4 panels, about 42 text columns in the 5x7 font) both changes fall through to the code that passed there at 13:25 today (`-132532`: 468 row-run cases, labels shown), so no separate quad run was made; the next quad run shows it.

**Verdicts:** §4 and §5 accepted on the FM6126A, MBI5124GP and FM6124 at 8 and 5 bit. No chip needs shift-while-dark.

**Steps completed:** visit D.

### 2026-10-05 — Overlapped-latch clock pulse ended before the dark wait («#105»), single FM6126A

**Tree:** `driver/*.spin2` at `8e2df8d` plus the «#105» change to `isp_hub75_rgb3bit.spin2` (overlapPlane: `waitx #WAITX_EOBYTE_TICKS` and `drvl pinLedCLK` after the first `shiftColumns`), committed with this entry; a temporary single-FM6126A `DISP0` config as at visit D, restored after the build (`git diff` empty for it).
**Rig:** the pink FM6126A alone on P16, 335 MHz, `pnut-term-ts -r <bin> -p Parw7ukt --headless --end-marker --timeout 500`. Log `driver/logs/headless_261005-162211.log`.

| 8-bit | Visit D (`-150541`) | Now |
|---|---|---|
| CLK high (monitor mean) | 1,407.5 ns | 21.7 ns |
| Refresh / lit | 85.1 Hz / 99.6% | 85.1 Hz / 99.6% |
| Clock rises | 697,856/s | 697,856/s |
| Brightness 128 / 1 / 0 | 49.8 / 1.4 / 0.0% | 49.8 / 1.4 / 0.0% |
| Handshake / take check | PASS / 1,825 of 1,825 | PASS / 1,817 of 1,817 at row 15 |

- Colour table PASS, row runs PASS (156 cases; L layouts not run on one panel). Stephen: "all looks good visually".
- **Clock halves (correction to visit C's note):** the driver's startup line reads `CLK high 7 low 8 clocks` at 15 clocks per column: high is DRVH, WAITX #1, SETBYTE = 7 clocks (20.9 ns), low is DRVL, ALTGB, GETBYTE, WAITX #0 = 8 clocks (23.9 ns). Visit C wrote "CLK high 23.9 ns; the low half is 7 clocks (20.9 ns) on paper", which swaps the halves (the 7-clock low half was the 16-clock loop's). The monitors read the high half long through the pin's input threshold, by about 0.3 clock on the FM6126A (21.7 ns) and about 1 clock on the quad, MBI5124GP and FM6124 (23.9-24.2 ns); a true 8-clock high half could not read 21.7 ns. Both halves are >= 20 ns, so no acceptance changes. The reader docs now state 7 and 8 clocks.

**Verdict:** the overlapped path ends every clock pulse before waiting, like the latch-at-end path; image, refresh and lit share unchanged.

**Steps completed:** «#105».

### 2026-10-07 — Two MBI5124GP panels chained as one 128x32 display («#110»)

**Tree:** `driver/*.spin2` at `b240a55` plus the uncommitted «#110» edits to `isp_hub75_rgb3bit.spin2` (MBI5124 configuration-register init; MBI5124GP clock held to the chain limit) and `demo_hub75_scroll.spin2` (layout by display height), committed after this entry. Bench builds in a scratch copy of `driver/` with `DISP0` = `CHIP_MBI5124GP`, `ADDR_ABC`, 64x32, `C0 = FIRST_PANEL | ARROW_UP`, `C1 = LEFT_OF | C0 | ARROW_UP` (or `C1 = NO_PANEL` for one panel); the committed config is the quad and was not changed.
**Rig:** two green MBI5124GP 64x32 panels, landscape, end to end on P16-P31; the adapter into C0, the right-hand panel from the front. 335 MHz. Loaded with `pnut-term-ts -r <bin> -p Parw7ukt --headless --end-marker --timeout N`.

**Observed:**
- Identify (`demo_hub75_numberPanels`), first guess `C1 = RIGHT_OF C0`, arrows down: the whole image turned 180°, C0 on the right. With `C1 = LEFT_OF C0`, arrows up: upright, C1P0 left, C0P1 right (Stephen). 41.5 W, 8.2 A.
- At 22.3 MHz (the old 25 MHz rating), the first column of each panel showed the wrong red in some rows: C0 lost red in rows 8-15 and 24-31 (the first stage of its R1 and R2 lines), C1 gained it; at first it flickered. It came and went between loads: an identify image and a cyan (G=$FA) | red split showed it; 8-row and 4-row colour bands, single-column probes and a cyan (G=$FF) | red split did not.
- A frame-set dump of the identify image (all 8 planes, all 8 row addresses, the edge columns) held the right bytes: the converter was not the cause.
- With the new configuration-register init, on panels power-cycled with the P2: no init, fault present; init, fault still present. So the register is not the cause.
- Clock, same image, init present: 12.4 MHz clean twice; 22.3 MHz bad (two places per panel, the same row groups); 18.6 MHz (the chain limit, CLK-to-SDO 50 ns + SDI setup 3 ns) clean, then the identify image clean. Scroll demo clean across the seam (Stephen: "what is showing is clean"); the size-aware scroll demo showed all four directions, one per line.
- `test_hub75_rates` at 18.6 MHz, every self-test PASS (colour table, 208 row-run cases, handshake 100 commits, take check):

| Panels | Depth | Log | Refresh | Lit | b = 1 | Commit | Take check |
|---|---|---|---|---|---|---|---|
| 2 | 8 | `headless_261007-222532` | 70.9 Hz | 99.4% | 0.7% | 532 us | 1,531 of 1,531 at row 7 |
| 2 | 5 | `-222821` | 292.1 Hz | 99.6% | 0.3% | 428 us | 5,957 of 5,957 at row 7 |
| 1 | 8 | `-223108` | 71.2 Hz | 99.8% | 0.7% | 284 us | 1,537 of 1,537 at row 7 |
| 1 | 5 | `-223352` | 582.7 Hz | 99.4% | 0.7% | 233 us | 11,769 of 11,769 at row 7 |

- Clock rises at two panels, 8-bit: 1,162,230/s = 256 column clocks x 8 row addresses x 8 planes x 70.9 Hz.

**Steps completed:** the chain runs as one display at the chain-limit clock, by eye and by the rates self-tests. Not run: the rates runs were not watched by eye; the quad was not re-run (Stephen: no recabling); one panel was not checked by eye at the new clock. Stephen will check the panels by eye once, at the final release gate.

### 2026-10-09 — 4.0.0 certification by eye: quad, MBI5124GP pair and single, FM6124; v3.0.2 against v4 («#111»)

**Tree:** `driver/*.spin2` at `3fe70d9` plus the uncommitted certification fixes (`isp_hub75_scrollingText.spin2`: the window drawn again when a loop mode is set, the text index wrapped as often as needed, no gap painted over a window's last character; `test_hub75_rates.spin2`: a whole-window reference, a clear-mode scroll case, the scroll oracle self-test; `demo_hub75_multiPanel`, `demo_hub75_7seg`, `demo_hub75_color` layout and length; `pwmFrameCount()` removed). Scratch `DISP0` configs per panel, the committed quad config restored before commit. v3.0.2 was built from `git archive v3.0.2` in a scratch folder with `DISP0` = one FM6124, `ADDR_ABCD`, 64x32, 8-bit.
**Rig:** P16 adapter, 335 MHz, `pnut-term-ts -r <bin> -p Parw7ukt --headless [--end-marker] --timeout N`. The board was found unpowered twice (download exit 3, "No Propeller v2 device found"); powering it fixed both.

**Observed:**
- Quad (committed config): every demo correct by eye (Stephen) except two findings. `demo_hub75_text` line 2 (left, `SCROLL_ONCE_TO_CLEAR`) stopped with "First long te" at the left edge: a buffer probe showed the first window drawn wrapped, before the mode was set, then moved frame by frame. `demo_hub75_multiPanel` and `demo_hub75_7seg` were laid out for a six-panel row and 64-column panels. Both fixed and seen correct on the quad.
- Self-test with the clear-mode fix removed: 12 of 12 new clear-mode cases FAIL (`headless_261009-155746`); with it, ROW RUN PASS 636 cases (`-160319`).
- MBI5124GP pair at 18.6 MHz: identify, colour, scroll, 7-seg correct. Scroll line 1 ("2nd shorter - ", left, forever): the "o" showed as "c" on the right panel and became "o" crossing the seam, as the next copy appeared (Stephen). A buffer probe: the whole-window draw left the window's last column undrawn (the last character's field passed with no gap, then a gap painted over its fifth column), and the edge column wrapped the text index once, so positions needing two wraps were blank until the next whole redraw. Fixed; Stephen: "text is now correct".
- Scroll oracle self-test (scroller frames against the same characters drawn as static text): 15 of 15 FAIL against the scroller as committed at `3fe70d9`, 15 of 15 PASS with the fixes, on the pair (`-170749`); colour table, row runs (212), handshake, take check PASS.
- One MBI5124GP at 18.6 MHz (the pair's second panel unplugged; Stephen noted the config alone would have done): identify, colour, scroll correct.
- FM6124 (orange): identify, colour, scroll correct, no bad characters (Stephen).
- v3.0.2 against v4 on the FM6124, 8-bit, the same measurement program: refresh counted from the frame-start mark with a pin-edge event (`SETSE1 %001_PPPPPP`) over 5 s (v3.0.2 mark on P25, which is also G1, so measured on a blank screen; v4 strobe P9 in an instrument build); draw and commit times the best of 5 by system counter.

| Build | Refresh | Fill | 4 lines text | Diagonal | Commit |
|---|---|---|---|---|---|
| v3.0.2 | 74.0 Hz (370 marks / 5 s) | 183.2 ms | 129.2 ms | 5.8 ms | 1.37 ms |
| v4 | 85.3 Hz (426 / 5 s; model 85.3) | 0.34 ms | 2.79 ms | 0.34 ms | 0.28 ms |

**Steps completed:** quad, MBI5124GP pair and single, FM6124 certified by eye. Not run: 5-bit comparison (v3.0.2's 5-bit screen buffer is undersized, so its drawing figures there are not trusted); the scroll oracle on the quad. Remaining: FM6126A (pink) single, the pink pair, GS6238S (cyan).

### 2026-10-09 (evening) — FM6126A pair and single, GS6238S; quad recheck; the self-test's debug-data overflow («#111»)

**Tree:** as the entry above, plus `test_hub75_rates.spin2` debug prose moved to `DAT` (below). Scratch `DISP0` configs per panel; the committed quad config restored after (`git diff` empty for it).
**Rig:** P16 adapter, 335 MHz. The board was unpowered after each recable until Stephen powered it (download exit 3).

**Observed:**
- Pink FM6126A, powered with no data cable: the good panel 0 A / 0 W, the suspect panel 1.2 A / 5.1 W (Stephen). The suspect panel was set aside.
- Two good pink FM6126A, landscape, stacked, `C0` on top (`C1 = BELOW | C0`): first only sparse red on `C0` and `C1` dark; with the top panel alone, red only (right half filled, two 2-pixel bars on the left). Stephen replaced the diagonal link cable: identify correct on both panels, then colour and scroll correct (Stephen). One panel alone by config: identify and colour correct. 22.3 MHz, model 84.9 Hz (pair).
- Cyan GS6238S (P2.5-16S, 64x32, ABCD, G/B swap): the driver held the clock to 20 MHz (no rating, 19.7 MHz actual), model 75.3 Hz; identify (white text), colour (eight solids in order, hues in order) and scroll correct (Stephen). First run of this chip with 4.0.0.
- Quad recheck: scroll demo correct (line 3 phrase whole and continuous; Stephen). `test_hub75_rates` timed out (exit 124): its first workload report line printed junk from "CLK high" on for 17 minutes (`-190023`). The same line was already broken, shorter, in every full build since `17276dd` (this morning's `-160319`, a `HEAD` build). Cause, per P2KB `p2kbSpin2DbgDebugStrategyGuide`: the 16 KB debug-data cap fails silently below the compiler's error. Debug data (`-d` minus plain `.bin`): `9fc42ad` 15,183 bytes, report clean; `HEAD` 15,357, report dies; current 15,679, runaway. The self-test's long literals moved into `DAT` strings emitted with `zstr_()` (first and last character kept inline, so the debugger adds no ", "): 13,593 bytes. Then (`-204326`) every self-test PASS (colour table, row runs 636, scroll oracle 15, handshake, take check), the report lines clean: refresh 71.0 Hz, commit 4,087 us, fill 4,685 / lines 12,743 / text 24,474 / BMP 3,806 us.
- Demo builds carry about 9.5 KB of debug data from the driver's own objects (`demo_hub75_text` 9,488, `color` 9,657, `scroll` 9,535 bytes).

**Steps completed:** FM6126A pair and single, GS6238S, quad scroll recheck and full self-test. Panel certification by eye complete for every panel on hand.
