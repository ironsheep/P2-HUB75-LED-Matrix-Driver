# FRAME-RATE — Sprint Plan

> **CLOSED 2026-10-05.** Plan certified complete; audit, exit baseline and carryover in
> [`2026-10-05-FRAME-RATE-Sprint-Closeout.md`](2026-10-05-FRAME-RATE-Sprint-Closeout.md).
> Build 4.0.0 is untagged; shaping the release is the next piece of work.

**Status:** started 2026-10-03. The exit gate was met and no questions are open.
**Build:** **4.0.0**, agreed with Stephen at sprint start (2026-10-03): "this also
adds content to the upcoming v4 release". 4.0.0 stays in development and untagged;
FRAME-RATE's ChangeLog entries go under `[4.0.0]`.
**Sources:**
- `DOCs/analysis/2026-10-02-FRAME-RATE-STUDY.md` (findings F1-F26, cited as F*n*;
  F25 and F26 are video-playback notes for the follow-on sprint)
- `DOCs/analysis/2026-10-02-CAPACITY-TRADEOFF-MODEL.md`
**Follow-on sprint (not this plan):** the PSRAM and microSD slideshow (study F16,
F19-F21).

## Open questions

1. *(Answered before research: scope.)* Stephen, 2026-10-02: "ok, stands as
   written". The scope and punch-list dispositions are as in *Scope* below.
2. *(Answered: the superseded performance plans.)* Stephen, 2026-10-02: "yes A".
   Both were moved to `DOCs/plans/archive/` with a "superseded" banner.
3. *(Answered by bench visit A, 2026-10-03: the §1 prototype.)* All four panels
   show a correct image, with no ghosting, while the next plane shifts in during
   the lit time. Refresh and duty are within 5% of the model on each:

   | Panel | Refresh (model) | Lit (model) | Full white |
   |---|---|---|---|
   | Quad rig, 4 × 128×64 ICN2037 | 65.9 Hz (67.0) | 82.2% (83.5) | 120 W |
   | 1 × 64×32 FM6126A, overlapped latch | 155.4 Hz (159.0) | 96.9% (99.1) | 17.6 W |
   | 1 × 64×32 MBI5124GP, 1/8 scan | 307.4 Hz (313.1) | 95.8% (97.6) | 39.93 W |
   | 1 × 64×32 FM6124 | 155.4 Hz (159.0) | 96.9% (99.1) | 14.27 W |

   The instrument's negative case was measured on the quad rig (92.0% lit at a
   doubled unit). Stephen saw flicker at 36.9 Hz and none at 65.9 Hz.

   This settles the two design points §4 had planned both ways:
   - the FM6126A's overlapped latch holds with one shift per plane;
   - the MBI5124GP and the FM6124 accept a shift while lit, so no chip on the
     bench needs shift-while-dark, and §4 does not build it (see §4 and *Named
     unknowns*).

   Details are in `DOCs/bench/RUN-NOTES.md`.

## Agreed scope changes

**SC-1 (Stephen, 2026-10-05: "yes, fix now"). Fix the converter's hub-slice
stall, under §7.**
- **What changed:** §7's commit target is pursued past visit E. Visit E measured
  6.58 ms at 5-bit against about 5 ms. The cause was then measured: every plane
  write of a column hits one hub slice and waits a full rotation, 16 clocks per
  plane where 9 is possible (`DOCs/bench/RUN-NOTES.md`, "Commit shortfall
  explained").
- **Why:** it is the §7 deliverable, the cause is proven, and every check runs on
  the quad rig without the bench supply.
- **What it touches:** `convertRowPairs()` in `driver/isp_hub75_panel.spin2` (both
  scans); the scratch timing harness; RUN-NOTES; «#102»'s commit figures
  (WiringGuide, ChangeLog) once measured.
- **How the method is chosen:** Stephen asked whether the search for faster
  methods was exhausted. Three single-cog candidates are built and timed on the
  rig geometry, and the fastest that passes `test_hub75_converter` (216 cases and
  its fail limb) is kept: (1) four columns batched in registers, one `WRLONG` per
  plane; (2) as 1, plus block reads of the screen rows; (3) as 2, plus block
  writes of the planes from cog RAM.
- **Result («#104», 2026-10-05):** candidate 4 kept (the three plus a fourth that
  moves the channel-order MOVBYTS under the same SKIPF); commit 4.09 ms at 8-bit and
  3.26 ms at 5-bit on the rig, refresh unchanged, 216/216 equivalence with the fail
  limb failing. New startup rule: panel width a multiple of 4. Details: RUN-NOTES,
  "Converter slice stall removed".
- **What it does not admit:** a converter cog (F11) and pre-converted frames
  (F16) stay out; the brightness floor is a punch-list item (Stephen,
  2026-10-05: "let's do C").

## Goal, and what done means

**Goal:** every supported panel at the best display rate it can reach. Refresh
should be at least 60 Hz at the deepest colour depth the chain allows. A new
frame should replace the old one without tearing and with no visible gap.
Drawing and committing should be fast enough not to limit animation.

**Done means:**
- Every section's verification passes on its stated benches.
- All top files (16 today, 18 after §2 and §7) compile with 0 warnings, the style gate passes, and the doc
  audit reports 0/0/0.
- The measured results replace the calculated ones in the docs.

## Standing rulings this plan rests on (all Stephen, 2026-10-02)

- *Refresh target:* "q1 yes B". Each display gets a target refresh rate in
  `hwPanelConfig`, defaulting to 60 Hz; the driver chooses the brightest OE unit
  that meets it.
- *Default depth:* "q2 A". 8-bit becomes the default in the configuration
  template and the demos.
- *Bench:* "i'd prefer to use (1) the quad panel set we have now, and then only
  2 or three other panels you pick ... keep the other panel to single panel
  displays ... treat the multi-panel (green) research as being outside of this
  effort." The picks are FM6126A (pink), MBI5124GP (green, single), and FM6124
  (orange, optional).
- *Instrumentation:* "we only do testing / instrumentation using one adapter".
  The monitoring approach comes from Stephen: nearest-neighbour smart pins
  (±3 confirmed by him), with no logic-analyzer leads.
- *Build selection:* "`ifdef` switches can be used to enable and disable
  individual OBJ lines". Optional code goes behind `#IFDEF`, passed down with
  `#PRAGMA EXPORTDEF` (p2kbSpin2PreprocessorOverview).
- *Pins:* "we can not have multiple cogs drive any pin as if they both drive
  outputs they are OR'd". One cog owns each pin.
- *Brightness:* brightness becomes OE time (F24). Stephen: the panels are very
  bright, so 84% is unlikely to be noticed, and average current falls.
- *Prove early:* Stephen asked whether to "put the new drive mechanism in place
  early and drive the quad panel just to prove that it does drive". Answered with
  the §1 prototype.
- *Standing doctrine:*
  - Don't damage a working thing (D5).
  - Instrumentation is permanent but stays off the critical path (D6).
  - Delete a superseded mechanism in the same change (D5).

## Scope

**In:** §1-§12 below.

**Out, each with its reason:**
- F5, the streamer: it is a capacity change, not a rate change. It's the next
  lever after F2.
- F11, a converter cog: not needed once §7 lands.
- F7, a display spanning adapters: a new feature.
- F18 and F22, PSRAM buffers, and F16 and F19-F21, the slideshow: the follow-on
  sprint.
- The green multi-panel research.
- The cube fold path and the face home state: they need the cube bench.
- 360 MHz (F4).
- Gamma behaviour: today it is off by default with no setter. Its cost is folded
  into §8's table, but its behaviour does not change.

**Punch list (Stephen, 2026-10-02):**

| Item | Disposition |
|---|---|
| Interleave the bit-plane repeats | taken: §6 |
| Converter per-plane hoists | taken, replaced by §7 |
| Panel-centric clip per pixel | taken: §9 |
| Panel clock above the ICN2037's 20 MHz | taken, closes: 30 MHz (§12) |
| ICN2037 docs 20 vs 30 MHz | taken, closes (§12) |
| Refresh core row past a line-buffer load | stays open. §4 keeps the whole-row rule; the long chains needed to show it are outside this bench. |
| ICN2038S scan dispute | stays open |
| Cube fold path calls | stays open |
| Face home hidden state | stays open |

## Bench visits

Each visit is earned by work that has landed, and every measurement names the
decision it feeds. Visits run on the macOS host; the run sheet is
`DOCs/bench/RUN-SHEET.md`.

| Visit | Earned by | Panels | Measures | Decision it feeds |
|---|---|---|---|---|
| **A** | §1 prototype | quad rig, then FM6126A, MBI5124GP and FM6124 | image correct (by eye, against a reference pattern); refresh, OE duty and clock from the monitors | the §4 design per latch path; the MBI5124GP fallback |
| **B** | §2 harness | quad rig, today's driver | baseline: refresh at each depth 3-8, duty, clock, commit and draw times | the "before" for every later claim |
| **C** | §3, §4, §5 | quad rig | refresh, duty and clock at each depth; tearing test; brightness scale | §4 and §5 accepted; §6 shimmer verdict |
| **D** | §4, §5 | FM6126A, MBI5124GP, FM6124 (optional), single panels | as visit C, per chip | per-chip acceptance; chip-matrix updates |
| **E** | §7, §8, §9 | quad rig | commit and draw times before and after; converter equivalence on the P2 | §7-§9 accepted |

### Visit B results (2026-10-03, quad rig, today's refresh core)

Measured by `driver/test_hub75_rates.spin2` (one build per depth) on the quad rig;
logs and method in `DOCs/bench/RUN-NOTES.md` (2026-10-03, visit B). Refresh is the
LATCH count divided by (2^depth - 1) x 32 rows; the frame-start strobe agrees at
every depth.

| Depth | Refresh (Hz) | THEOPS (Hz) | Diff | /OE lit | Commit (ms) | Draw fill / lines / text / BMP (ms) |
|---|---|---|---|---|---|---|
| 3 | 177.18 | 177 | +0.1% | 97.3% | 9.50 | 636.2 / 234.9 / 1,108.6 / 306.0 |
| 4 | 82.68 | 82 | +0.8% | 97.4% | 11.84 | 636.2 / 236.0 / 1,113.0 / 306.9 |
| 5 | 40.01 | 40.1 | -0.2% | 97.4% | 14.19 | 636.2 / 237.1 / 1,118.3 / 307.6 |
| 6 | 19.69 | 19.7 | -0.1% | 97.4% | 16.54 | 636.2 / 238.2 / 1,123.6 / 308.5 |
| 7 | 9.77 | 9.6 | +1.7% | 97.4% | 18.89 | 636.2 / 239.3 / 1,128.9 / 309.4 |
| 8 | 4.86 | 4.6 | +5.7% | 97.4% | 21.24 | 636.2 / 240.4 / 1,134.2 / 310.3 |

- **Shift clock:** 20.32 M rises/s mean at every depth (the loop runs 16 system
  clocks per column, 20.94 MHz, with row gaps between). On paper the loop is 9
  clocks high and 7 low (26.9 / 20.9 ns).
- **Verdict:** depths 3-7 agree with THEOPS within 2%. 8-bit is +5.7%: diagnosed as
  THEOPS's reading, not the counters. The LATCH rate is 39,687-39,690/s at all six
  depths, so refresh scales exactly with 1 / (2^depth - 1), and the counters agree
  with THEOPS wherever it is consistent with that scaling.
- **This table is the "before"** for refresh, duty and clock. Commit and draw times
  are the before for §3; §7-§9 compare against visit C (§3 changes commit).

### Visit C finding (2026-10-03): two §4 defects, fixed by «#103» before visit C resumes

The first visit-C sweep (`driver/logs/headless_261003-210125.log` to `-210748.log`) failed
§4's "within 5% of the model" limb below 7-bit, and the brightness limb:
- **/OE pulse start latency.** P_PULSE starts at the next base period after WYPIN
  (p2kbArchSmartPin00100PulseCycleOutput), so each plane waits up to one period T before it
  lights. Refresh vs model: 8-bit 70.3 / 71.1 Hz, 5-bit 75.6 / 84.7, 4-bit 71.6 / 90.5,
  3-bit 135.8 / 193.4. The 4-bit row excess is 4 x T.
- **Brightness is not linear.** A shorter pulse period shortens the row, so refresh rises as
  brightness falls, and brightness 128 delivers 79% of full light, not 50%.

What passed: the 60 Hz target picked the predicted j at every depth, the handshake passed,
brightness 0 read 0.0%, and brightness 1 sat at the chip-minimum floor. «#103» fixes both
defects inside §4's targets; it is not a scope change. «#94» then re-runs visit C in full.

### Visit C results (2026-10-03 and 2026-10-04, quad rig, new refresh core)

Measured by `driver/test_hub75_rates.spin2` on the fixed core (`9ea5959`), one build per
depth; logs, method and Stephen's words in `DOCs/bench/RUN-NOTES.md` (visit C).

| Depth | Refresh / model (Hz) | /OE lit / model | j (60 Hz target) | Commit (ms) | Draw fill / lines / text / BMP (ms) |
|---|---|---|---|---|---|
| 8 | 71.0 / 71.1 | 83.0 / 83.1% | 4 | 21.25 | 635.4 / 233.3 / 1,103.0 / 304.2 |
| 7 | 75.0 / 75.1 | 87.4 / 87.5% | 3 | 18.90 | 635.4 / 232.2 / 1,097.7 / 303.4 |
| 6 | 79.6 / 79.6 | 91.9 / 92.0% | 2 | 16.55 | 635.4 / 231.0 / 1,092.4 / 302.5 |
| 5 | 84.7 / 84.7 | 96.3 / 96.3% | 1 | 14.20 | 635.4 / 229.9 / 1,087.1 / 301.7 |
| 4 | 90.5 / 90.5 | 99.6 / 99.6% | 0 | 11.86 | 635.4 / 228.8 / 1,082.7 / 300.9 |
| 3 | 193.3 / 193.4 | 99.2 / 99.3% | 0 | 9.51 | 635.4 / 227.9 / 1,077.4 / 299.8 |

- **§3 accepted.** Handshake PASS at every depth. Take check (the §3 acceptance below):
  824 of 824 frame-set takes at a frame boundary, one per commit; its negative limb (P8
  also pulsed at every row start) reported 128,386 takes off the boundary.
- **§4 accepted.** Refresh and lit share within 0.2% of the model at every depth, and the
  target picked the predicted j. Brightness 128 gives half the lit share of 256 with
  refresh unchanged; 1 sits at the chip-minimum floor (3.6% at 8-bit); 0 is dark. By eye,
  with each step labelled on the panel: Stephen, "yes dimming looks good... seems to be
  correct". A target above reach (200 Hz at 8-bit) printed its catalogue message and ran
  at 165.0 Hz against 165.7 Hz predicted.
- **§5 accepted.** CLK high 23.9 ns at every depth; the low half is 7 clocks (20.9 ns) on
  paper, which this instrument resolves to about +/-0.5 clock. *(Corrected 2026-10-05, «#105»:
  the 15-clock loop is high 7 clocks (20.9 ns) and low 8 (23.9 ns); the 23.9 ns reading is the
  high half read long. Both halves are still >= 20 ns.)*
- **Shimmer (§6):** steady at 5, 6, 7 and 8 bit by eye (Stephen's words per depth in
  RUN-NOTES). «#95» records the disposition.
- **The commit and draw columns are the "before"** for §7-§9; visit E compares against them.

**§3 acceptance changed (agreed with Stephen, 2026-10-04).**
- *What changed:* the tearing test's acceptance is a pin measurement, not an observation.
  The instrument catches every rise of P8 (posted set taken) and reads the row-address pins
  at that moment; every take must find the frame's last row address, and the takes counted
  must equal the commits made. Its negative limb must report FAIL.
- *Why:* by eye the 18 Hz white/black flip is too fast to judge (Stephen: "So maybe too fast
  for me to distinguish"), and a camera cannot tell an unlit row from the black image, so
  neither can show a torn frame on a scanned panel. Stephen: "I like your pin measurement
  idea".
- *What it touches:* `isp_hub75_instrument.spin2` (the take check) and
  `test_hub75_rates.spin2` (the report, and the brightness-step labels Stephen asked for so
  the dimming can be judged by eye).
- *What it does not admit:* no change to the driver; the white/black flip stays in the test
  as the load the take check runs under.

### Visit D results (2026-10-05, single 64x32 panels on the P16 adapter)

Measured on `620d1c1` (plus, after the first run, the rates-test change in RUN-NOTES) with a
temporary single-panel `DISP0` config per chip (restored after);
logs, method and Stephen's words in `DOCs/bench/RUN-NOTES.md` (visit D). Target 60 Hz; each
panel reaches it at the longest unit (T = S, j = 0), so it runs at its fastest rate.

| Chip (latch, scan) | Depth | Refresh | Lit | Floor at b = 1 | CLK high | Commit | Take check | By eye |
|---|---|---|---|---|---|---|---|---|
| FM6126A (overlapped, 1/16) | 8 / 5 | 85.1 / 688.9 Hz | 99.6 / 97.9% | 1.4% (40 ns) | 21.7 ns (after «#105») | 283 / 231 us | 1,825 / 13,893 all at row 15 | patterns correct at both |
| MBI5124GP (at end, 1/8, SCAN_4) | 8 / 5 | 85.4 / 698.5 Hz | 99.8 / 99.2% | 0.8% (50 ns) | 24.0 ns | 284 / 233 us | 1,823 / 14,083 all at row 7 | patterns correct at both |
| FM6124 (at end, 1/16) | 8 / 5 | 85.3 / 694.1 Hz | 99.7 / 98.6% | 1.1% (30 ns) | 24.2 ns | 283 / 231 us | 1,821 / 13,995 all at row 15 | patterns correct at both |

- **§4 and §5 accepted on all three chips.** Handshake PASS on every run.
- **FM6126A overlapped latch:** correct image with one shift per plane and its register init.
  The overlapped path held the last pre-latch clock pulse high while the previous plane went
  dark, so the CLK monitor first read a mean high of 1,407 ns. «#105» ends that pulse before
  the wait, as the latch-at-end path does: CLK high now reads 21.7 ns, refresh and lit share
  unchanged.
- **MBI5124GP:** correct on the 8-row quarter-scan path shifting while lit; the clock count
  (699,648 rises/s at 85.4 Hz = 128 x 8 x 8) confirms S uses the doubled column count. The
  new quarter-scan converter (SC-1) shows a correct image.
- **FM6124:** the brightness-1 step reads 1.1% lit, the 11-clock floor; unclamped it would be
  about 0.4% (an 11 ns pulse, below the chip's 30 ns).
- No chip needed shift-while-dark, so the named unknown closes without a scope change.

### Visit E results (2026-10-05, quad rig, after §7-§9)

Measured on `780421a`; logs, method and Stephen's words in `DOCs/bench/RUN-NOTES.md`
(visit E). "Before" is visit C.

| Item | 8-bit before / after | 5-bit before / after | Prediction |
|---|---|---|---|
| Commit | 21.25 / 8.93 ms (2.4x) | 14.20 / 6.58 ms (2.2x) | about 5 ms at 5-bit |
| Draw fill | 635.4 / 114.0 ms (5.6x) | 635.4 / 114.0 ms (5.6x) | — |
| Draw lines | 233.3 / 116.8 ms (2.0x) | 229.9 / 116.8 ms (2.0x) | — |
| Draw text | 1,103.0 / 300.9 ms (3.7x) | 1,087.1 / 300.9 ms (3.6x) | — |
| Draw BMP | 304.2 / 188.4 ms (1.6x) | 301.7 / 188.4 ms (1.6x) | — |

- **§7 accepted on equivalence:** the converter test passes 216 of 216 on HEAD; its fail limb
  was shown in «#98». **Commit misses its prediction:** 6.58 ms at 5-bit against about 5 ms
  (calculated), about 30% over. Explained and fixed afterwards by SC-1 («#104»): 4.09 /
  3.26 ms at 8 / 5-bit.
- **§8 accepted:** the colour table equals the old function on all 3,840 entries; draw time
  no longer depends on colour depth.
- **§9 accepted:** row runs are byte-equal to the per-pixel path in 468 cases (three layouts,
  four rotations, four arrows); draw is 1.6x to 5.6x faster.
- **By eye:** `demo_hub75_quadPanel`, `demo_hub75_text` and `demo_hub75_boundary` — Stephen:
  "all three demos look good".

## 1. Prototype: prove the OE-weighted method on panels (planning phase)

**Why:** §4 rewrites the shared refresh core. Two premises are unproven on panels:
- that a chip shows correct data while the next plane shifts in, and the
  short-plane pulses light in proportion;
- that the FM6126A's latch protocol holds when planes are no longer repeated.

Stephen asked to prove the mechanism early. The `sprint-plan` exit gate requires a
risky design to be prototyped.

**Starting point:**
- The two shift loops: latch-at-end `isp_hub75_rgb3bit.spin2:1025-1077` and
  overlapped `:969-1020`.
- Pin layout `:83-95` and the chip flags from `getDriverFlags`
  (`isp_hub75_hwBufferAccess.spin2`).

**Target:** a new standalone top file, `driver/test_hub75_oe_bcm.spin2`, in the
manner of `test_hub75_pin_identify.spin2`. It is kept as the low-level check of
the method.
- One adapter at P16, using the chip and geometry from `hwPanelConfig`.
- It builds an 8-bit frame set in hub from fixed patterns: horizontal grey and
  RGB ramps, solid primaries, and a checkerboard.
- One cog runs, per row address and per plane k: load the row, shift it, latch,
  then pulse /OE for 2^k·T with a `P_PULSE` smart pin. The pulse uses period
  P = T and count Y = 2^k, because the MSB on the rig, 128 × 512 = 65,536
  clocks, is one over the 16-bit period field (p2kbArchSmartPin00100PulseCycleOutput).
  The pin is configured DIRL → WRPIN → WXPIN → DIRH → WYPIN, and the cog polls
  IN with `TESTP`.
- Both latch styles are built in, chosen by the chip's flags, plus the FM6126A
  overlapped latch (LE high for the last 3 columns).
- **A shift-while-dark mode**, selectable at compile time: wait for the pulse to
  end before shifting. This is the fallback if a chip can't take data while lit.
- T is fixed in a `CON`, set from the §3 model of the study, so the rig runs at
  about 60-70 Hz at 8-bit.
- It counts with P13-P15 monitor smart pins (CLK, OE, LATCH; ±3 reach) and prints
  refresh, OE duty and clock once a second through DEBUG.

**Verification (visit A):**
- **Normal:** on the quad rig, the ramps step evenly through 256 levels with no
  missing or doubled bands, the primaries are correct, and refresh and duty
  measure within 5% of the model.
- **Edge:**
  - FM6126A: correct image with the overlapped latch.
  - MBI5124GP: correct image in shift-while-lit mode. If not, shift-while-dark
    must be correct.
  - The checkerboard shows no ghosting from shifting while lit.
- **Error:** a deliberately wrong T (pulse longer than a slot) must show as a
  measured duty above the model. That proves the duty monitor can see the
  difference (D2).

## 2. Instrumentation harness (single adapter, behind `HUB75_INSTRUMENT`)

**Why:**
- Every later claim needs measured before and after figures.
- The strobes on P8-P11 are compiled into every build today, with two faults
  (F23): several cogs drive them, and they toggle an adapter at base 0's colour
  lines.

**Starting point:**
- `isp_hub75_rgb3bit.spin2:36-40`, `:303-314` and `:738-739` (strobe setup), and
  the `OUTNOT`s at `:817`, `:843`, `:853` and `:872`.
- `markStart` and `markEnd` (`isp_hub75_panel.spin2:783-810`), which time the
  converter only.
- `showDuration` (`demo_hub75_boundary.spin2:162-173`).

**Target:**
- **One symbol, `HUB75_INSTRUMENT`,** defined in a test top file and passed down
  with `#PRAGMA EXPORTDEF`.
  - Without it, no strobe instruction, strobe pin setup or monitor code is
    compiled. The refresh loop loses its `OUTNOT`s.
  - With it, the refresh cog drives P8-P11 (the single-adapter rule).
- **The strobes are redefined for the new core:**

  | Pin | Marks |
  |---|---|
  | P8 | new command taken |
  | P9 | frame start |
  | P10 | row start |
  | P11 | plane latch |

- **A new object, `driver/isp_hub75_instrument.spin2`.** It starts the monitor
  smart pins:

  | Monitor | Watches | Mode |
  |---|---|---|
  | P5 | P8 | count rises over a 1 s window |
  | P6 | P9 | count rises over a 1 s window |
  | P7 | P10 | count rises over a 1 s window |
  | P12 | P11 | count rises over a 1 s window |
  | P13 | P16, CLK | `P_COUNTER_HIGHS` and ticks, for frequency and duty (p2kbArchSmartPin10110CountHighsInXClocks) |
  | P14 | P17, OE | high time, for duty |
  | P15 | P18, LATCH | count rises over a 1 s window |

  It prints one DEBUG line a second, which `pnut-term-ts` logs. The pins it uses
  are chosen from the configured adapter base. A signal with no free neighbour is
  reported as "not monitored: jumper needed".
- **Stopwatch helpers** for commit and draw time, replacing `markStart` and
  `markEnd` and the demos' `showDuration`. Those are deleted in the same change
  (D5).
- **A new test top file, `driver/test_hub75_rates.spin2`.** It defines the
  symbol and runs the fixed workload: a flat fill, lines, text, a BMP, and
  commits, at each depth.

**Verification:**
- **Normal (visit B):** a complete baseline table on today's driver: refresh,
  duty and clock at depths 3-8, plus commit and draw times. The refresh figures
  must agree with THEOPS's measured table (4.6-177 Hz) within 5%. That confirms
  the counters agree with the old logic-analyzer method (D2).
- **Edge:** a build without the symbol has no reference to P5-P15 or P8-P11.
  Checked with a grep of the listing, and by a non-debug `.bin` sha256 equal to
  the same source with the strobe lines removed.
- **Error:** with the adapter at base 0 in the config, the harness reports that
  its monitors are not available rather than driving that adapter's colour pins.

## 3. Double buffering connected, and a public "show this frame set" call (F9)

**Why:**
- Both converters write into the frame set on display, so every commit can tear.
- The second set, 80 KB on the rig, is unused.
- The slideshow sprint needs a call that shows a pre-built frame set.

**Starting point:**
- `clearPwmFrameBuffer` and `getActivePwmBuffer` (`isp_hub75_panel.spin2:750-765`),
  called only at `:148-149`.
- The converters take `getActivePwmBuffer()` at `:255` and `:506`.
- `cmdWritePwmBuffer` (`isp_hub75_rgb3bit.spin2:584-593`) has no
  acknowledgement.
- The PASM reads a new argument only at `getCommand` (`:802-810`).

**Target:**
- The refresh cog writes the hub address of the set it is showing into a new hub
  long (`dvrShowing`) at each frame start.
- `commitScreenToPanelSet` converts into the set that is *not* `dvrShowing`,
  posts it, and returns. Before converting again it waits until `dvrShowing`
  equals the set it last posted, so it never writes the set on display.
- A new public `display.showFrameSet(pFrameSet)` takes a caller-built frame set
  of the adapter's exact size and posts it the same way. Its doc comment states
  the layout (plane-major, MSB first, row-major, one byte per column clock) and
  the size.
- `usePwmFrameset1` and the toggle-on-clear are replaced by this rule and
  deleted.

**Verification:**
- **Normal (visit C):** a tearing test. Two full-screen patterns alternate at the
  fastest commit rate while the instrument's take check reads the row-address pins at
  every frame-set take: every take is at a frame boundary, one per commit, and the check
  reports FAIL on a build that marks takes mid-frame (acceptance changed 2026-10-04; see
  "Visit C results").
- **Edge:**
  - A commit issued while the previous one has not yet been taken waits, and
    never overwrites the set on display.
  - The first commit after start, when nothing has been taken yet, works.
- **Error:** `showFrameSet` with an address that isn't one of the adapter's sets,
  or with a NULL, is refused, and a startup-catalogue-style message names the
  call.

## 4. OE-weighted refresh core, target refresh and brightness as OE time (F2, F24)

**Why:** this is the frame-rate change. On the rig, 8-bit goes from 4.6 to about
67 Hz, and 5-bit from 40 to about 142 Hz (study §3, calculated).

**Starting point:**
- `cmdDsplyFrameSet` (`isp_hub75_rgb3bit.spin2:842-866`) repeats plane k
  2^(N-1-k) times.
- Sub-page sizing is in `start()` (`:486-504`). The flags are set at `:370-379`.
- The two shift loops are as in §1.
- Cog RAM: `FIT 496` (`:1198`), about 100 longs free (inferred, to be confirmed
  from the listing), and the LUT is unused.
- Dead or unused paths:
  - `CMD_SHOW_BUFFER`, `cmdWriteBuffer` and `cmdClearPanel` have no callers.
  - `CMD_CLEAR` and `CMD_STOP` are not implemented in the PASM.
  - `modeSlowCLK` is never read (`:1111`), and `bSetMidPins` is never set.
  - The ISR stubs are unused.
- `cmdFillScreenNoPWM` is used, through `panel.fillScreenNoPWM` and
  `display`/demos.

**Target:**
- **The core loop.** Per frame, per row address, per plane k from MSB to LSB:
  - load the plane's row from hub with `SETQ`+`RDLONG`, at most 512 bytes;
  - shift it, then latch in the chip's style (enclosed or offset, or the
    FM6126A's overlapped latch);
  - start the OE pulse of Y = 2^k periods of length P = T·b, where b is the
    brightness scale;
  - move on to the next plane's load and shift while this plane is lit. Visit A
    showed that every chip on the bench accepts this, so the core has no
    shift-while-dark path. The prototype keeps that mode as a compile-time
    choice for diagnosing a new chip.
- **The address changes only with OE off.** The sub-page machinery goes; one row
  is the unit. This keeps the whole-row rule from the open punch item.
- **OE becomes a smart pin owned by the refresh cog.** `start()` releases cog 0's
  hold on OE (`pinclear`) **before** `COGINIT`, not after (`:525-527`), so the
  cog's `WRPIN` cannot be wiped by a later `pinclear` (study research,
  pin-ownership race). `stop()` clears the smart pin.
- **The target refresh rate.**
  - A new `DISPn_TARGET_REFRESH_HZ` in `hwPanelConfig`, default 60, with three
    groups.
  - `start()` computes S = columns × clocks per column, then the smallest j with
    refresh(j) ≥ target, and T = S / 2^j.
  - T is clamped to at least the chip's minimum OE in clocks: a new per-chip
    table from the datasheets (FM6124 30 ns; ICN2038S, FM6126A 40 ns; ICN2037
    60 ns; MBI5124GP 50 ns), rounded up at `clkfreq`.
  - The ICN2037 value is 60 ns because its datasheet revisions disagree: V1.1
    (Nov 2016, p.2 and p.8) and Stephen's `DOCs/ICN2037/ICN2037-timing.pdf` give
    60 ns, V2.0 (Nov 2017, p.8) gives 40 ns. The panels' revision is unknown, so
    the value that holds for both is used.
  - If no j meets the target, start uses the largest j and prints a catalogue
    message giving the rate it does reach.
- **Brightness (F24).** `display.setBrightness(0-256)` keeps its signature and
  meaning (`isp_hub75_display.spin2:260-276`). It now writes b, which the
  refresh cog reads once per frame. The value multiply in `correctedSingleColor`
  goes (§8). When b would make T·b fall below the chip's minimum OE, P is held
  at the minimum, and the brightness floor is that value; the doc comment says
  so.
- **`fillScreenNoPWM` keeps its behaviour.** It is re-implemented as "fill the
  idle frame set with the colour's planes and show it". `CMD_FILL_COLOR`,
  `writeColorToBuffer` and `displayCogBffrFullFrame` are deleted.
- **Removed in the same change (D5):**
  - the repeat loop, the sub-page counters and the `maxCtPerFrame` sizing;
  - `CMD_SHOW_BUFFER`, `CMD_CLEAR`, `CMD_STOP`, `cmdWriteBuffer` and
    `cmdClearPanel`;
  - the dead `modeSlowCLK` and `bSetMidPins`, and the ISR stubs.

**No old-mode switch** (Stephen asked, 2026-10-02, whether to keep the old method
as a compile-time choice for small displays). Not needed:
- The old method is this loop with j = 0 (T = S): every plane fills its slot,
  brightness is 100%, and the refresh rate is today's.
- The target rule picks j = 0 whenever the old method already reaches the target.
- At a 60 Hz target (calculated, 16 clocks per column), 1 × 64×32 gets 100% at
  every depth. 2 × 64×32 and 1 × 64×64 get 99.6% at 8-bit (80 Hz against today's
  40). 1 × 128×64 gets 98% at 8-bit (79 Hz against 20). Only long chains at deep
  colour drop noticeably; the rig at 8-bit gets 84%, at 67 Hz against 5.
- A user wanting full brightness on a large display lowers
  `DISPn_TARGET_REFRESH_HZ`.
- Keeping two cores would double every chip path's code and its bench
  validation (D5: delete the superseded mechanism).

**Adversarial premise check** (sprint-plan overlay: what input breaks each derived
quantity, and the planned check that catches it):

| Input that breaks it | Planned check |
|---|---|
| T > 65,535 (the period field) | Can't happen: S ≤ 512 × 16 = 8,192. An assert in `start()` aborts with a catalogue message if a future change allows it. |
| T below the chip's minimum OE (short chains, high j, low brightness) | Clamped (above). The resulting brightness floor is documented. |
| Target unreachable on a long chain at high depth | Catalogue message giving the rate reached. |
| Rows = 8 (ABC, the MBI5124GP) with quarter-scan doubling `colCtrMax` | S uses `colCtrMax` after doubling (`:487-488`). Checked on the MBI5124GP at visit D. |
| Brightness 0 | OE never pulses. Defined as "off"; tested at visit C. |
| A chip with no known minimum OE (`CHIP_UNKNOWN`, DP5125D, GS6238S) | Uses the largest minimum in the table (50 ns) and says so at startup. |

**Verification:**
- **Normal (visit C):** at each depth 3-8 on the quad rig, refresh and duty match
  the model within 5%, the §1 patterns are correct, and the 60 Hz target picks
  the predicted j.
- **Edge:**
  - Brightness 256, 128 and 1, plus the clamp.
  - Visit D: FM6126A overlapped latch, MBI5124GP 8-row quarter-scan shifting
    while lit, FM6124 at 30 ns.
- **Error:** a target set above what the chain can reach prints the catalogue
  message and runs at the best rate.
- **Compiled:** cog RAM fits, with the listing count recorded.

## 5. Faster shift clock (F3)

**Why:** +7% (15 clocks) to +14% (14 clocks) on every scheme, within the chips'
ratings.

**Starting point:** `TARGET_PANEL_HZ = 20_000_000` (`:20`), `BASE_LOOP_CYCLES 14`
(`:24`), and the wait split at `:324-335`. The loop is at `:1039-1047`, about 7
clocks low and 9 high.

**Target:**
- The target comes from a per-chip maximum clock: 30 MHz, or 25 MHz for the
  MBI5124GP.
- A 20 ns minimum high time and low time each, rounded up in clocks at
  `clkfreq`.
- The loop is reordered so its high and low halves meet those minimums at 15
  clocks, and at 14 if a split that meets both exists.

**Premise settled (study Q3, read 2026-10-03 from each chip's dynamic table):** the
minimum clock pulse width, high or low, is **20 ns on every bench chip**:
- FM6126A `TwCLK` 20 ns, `DOCs/FM6126A/FM6126A-timing.pdf` p.2;
- MBI5124GP `tw(CLK)` 20 ns at both VDD 5.0 V and 3.3 V, `MBI5124GP-B_C.pdf` pp.9-10;
- ICN2037 `twCLK` 20 ns, `ICN2037_datasheet_EN_2017_V2.0.pdf` p.8;
- ICN2038S `twCLK` 20 ns, `icn2038s.pdf` p.9;
- FM6124 `TWCLK` 20 ns, `fm6124-datasheet_en.pdf` p.4.

20 ns high plus 20 ns low caps every chip at 25 MHz, below each rated maximum. The
ICN2037 V2.0 sheet gives `FCLK` 35 MHz in its transition table (p.8) but 30 MHz in
its feature list (p.2) and absolute maximums (p.7); V1.1 gives 30 MHz throughout.
30 MHz is the rating used here and in §12.

**Verification (visits C and D):**
- **Normal:** P13 measures clock frequency and high-time duty. Both halves are at
  least 20 ns, and refresh rises by the predicted factor.
- **Edge:** the four-panel chain (longest ribbon) shows correct images, and so
  does each single panel.
- **Error:** none to construct. A chip without a table entry falls back to
  20 MHz.

## 6. Shimmer: verify, then close or interleave (punch-list item)

**Why:** the 5-bit-and-above shimmer came from long back-to-back MSB repeats at
20-40 Hz. §4 removes the repeats and raises the rate.

**Target:**
- At visit C, Stephen views the rainbow and quadPanel hue images at 5-8 bit.
- If they are steady, close the punch item with that observation.
- If not, interleave the plane order within each row inside §4's loop. The
  weights are unchanged.

**Verification:** Stephen's observation by eye, quoted, plus the measured refresh.

**Outcome (2026-10-04, «#95»):** steady at 5-8 bit on the new core (71.0-84.7 Hz). The
punch item is closed with Stephen's words; the plane order is unchanged.

## 7. `MERGEB` converter, both paths (F10)

**Why:** commit 14.2 ms → about 5 ms on the rig at 5-bit (calculated). It replaces
the punch list's per-plane hoists.

**Starting point:**
- Half-scan `isp_hub75_panel.spin2:523-655`: per plane, a `MUL` address, six
  `TESTB`s with conditional ORs, and a `WRBYTE` (`:611-638`).
- Quarter-scan `:385-468`: a per-plane top/bottom branch, plus `RDBYTE`
  read-modify-write (`:417-452`).
- The swaps are applied by remapping the bit constants (`:305-324`, `:556-573`).
  With both swaps set the remap is wrong; no chip sets both today (latent).
- Pixel = R, G, B at +0/+1/+2; `RDLONG` takes the next pixel's R in byte 3.
- The frame set is plane 0 = MSB.

**Target:**
- **Per pixel pair:**
  - `RDLONG` top and bottom, mask byte 3, and apply the swap as a byte reorder
    hoisted out of the loop;
  - `MERGEB` each (p2kbPasm2Mergeb), so nibble p holds plane p's
    {0, B, G, R} for that pixel;
  - per plane, OR the top nibble with the bottom nibble shifted left 3, and
    `WRBYTE` it through a running frame pointer (`ADD` frame size), with no
    `MUL`.
- **Quarter-scan** iterates physical row m with m + half-panel, the half-scan
  pairing: no `RDBYTE`, no branch.
- **Both-swap remap fixed** by the byte-reorder design. Meaning (decided at «#98»,
  2026-10-04): red/blue swap first, then green/blue on the result, so the R pin
  carries blue, G red and B green. That is the order the old code applied them; no
  chip sets both today.

**Verification (visit E):**
- **Equivalence:** a new test top file, `driver/test_hub75_converter.spin2`,
  replaces the «#76» harness, which was never committed. It keeps the old
  converter as the reference and compares new against old byte for byte, on the
  P2, for half-scan 1/4/9/10/16 panels and quarter-scan 1/2/3 panels, at depths
  3-8, with RB swap, GB swap and both. All must match, except the both-swap case,
  which must match a hand-built expected set.
- **Normal:** commit time measured before and after on the rig.
- **Error:** none applies. The converter has no error inputs beyond what
  `start()` rejects.

**Equivalence result (2026-10-04, «#98», on the P2 with no panels):** 216 of 216 cases
PASS (`driver/logs/headless_261004-215656.log`): new against old, byte for byte, for
every case except both-swap; both-swap against the hand-built set, which itself agrees
with the old converter in all 24 cross-checks. With one output bit corrupted
(`-D HUB75_CORRUPT_CONVERTER`) all 192 new-converter cases FAIL (`-215319`). The
harness's geometries are capped at 8,192 pixels so its buffers fit beside the driver's:
half-scan 1x128x64, 4x64x32, 9x32x16, 10x32x16, 16x32x16; quarter-scan 1/2/3 x 64x32.

## 8. Colour table and brightness out of the values (F12, F24 colour side)

**Why:** colour correction is 27 of the 36 calls per pixel
(`isp_hub75_screenUtils.spin2:107-111`; `isp_hub75_colorUtils.spin2:109-127`,
`:271-303`).

**Target:**
- A per-adapter 256-byte DAT table maps an 8-bit input to its stored value
  (gamma if enabled, then the depth mapping `(v * frames) / 255 << (8-N)`).
  It's indexed by chain, and it's one table for R, G and B, because all three
  channels use the same curve today (`gammaPtrs`, `:260-269`).
- Built at adapter start, after `configureAdapter`, and on any gamma change.
- `correctedSingleColor` becomes one table read. The brightness multiply goes,
  because §4 does brightness.
- The DAT writes of `shiftLtValue` and `nbrPwmFrames` (`:307-308`), shared across
  adapters, are removed.
- `reducedBrightnessOfCValue` (dithered text, `display:1256`) stays value-based.
  It is per-pixel dimming, not global brightness.

**Verification (visit E):**
- **Normal:** draw time before and after.
- **Edge:** the stored bytes for every input 0-255 at each depth 3-8 match the
  old function with brightness 256. A self-test in `test_hub75_rates.spin2`
  checks this exhaustively.
- **Error:** an out-of-range chain index aborts, as today.

## 9. Row-run primitives, divides and the panel-centric clip (F13, F14, punch item)

**Why:**
- Lines, filled boxes, glyph rows, BMP rows and fills go pixel by pixel through
  the full path (`display:1354-1359`, `:1545`, `:1228`, `:1270`;
  `display_bmp:174`).
- `panelCoordsAt` does 4 divides per pixel (`hwBufferAccess:1716-1739`).
- The panel-centric clip looks up the panel for every pixel.

**Target:**
- **An internal run primitive** (working name `fillRowRun(chain, mountedRow,
  mountedColStart, count, corrected colour)`). It splits the run at cell
  boundaries. Per cell it resolves the start address and a signed stride once,
  using the same rotation and arrow cases as `displayPixelAddress`:
  - +3 or −3 for upright and down arrows;
  - ±nativeCols·3 for sideways arrows and 90-degree mounting.

  It then writes the run with a stride loop.
- **Callers move to it:** the horizontal line, filled box, glyph rows, BMP rows,
  and `fillLayoutArea`. `fillLayoutArea` also switches to row-major order.
- **Vertical runs** use the same primitive with the axes exchanged.
- **The panel-centric clip** computes the panel's rectangle once per call.
- **One rotation rule.** The stride derivation is shared with
  `displayPixelAddress`, never copied. It is the same rule the history memory
  notes lives in two places that must change together; this section adds no
  third copy.

**Verification (visit E):**
- **Normal:** draw times before and after.
- **Edge:** a byte-for-byte check, on the P2, that every converted primitive
  writes the same screen buffer as the per-pixel path. It covers all four
  mounting rotations, all four arrows, runs that cross 1, 2 and 3 cells, and
  clipped panel-centric lines. It's a self-test in `test_hub75_rates.spin2`.
- **Error:** a run that starts or ends off the display is clipped exactly as the
  per-pixel path clips it.

## 10. 8-bit by default (Stephen: "q2 A")

**Target:**
- `DISP0_COLOR_DEPTH`, `DISP1_COLOR_DEPTH` and `DISP2_COLOR_DEPTH`
  (`isp_hub75_hwPanelConfig.spin2:83`, `:170`, `:245`, today 5, 6 and 4) become
  `DEPTH_8BIT`, with their template comments.
- The README and THEOPS examples follow (§12).

**Verification:**
- All top files compile at 8-bit on the rig config. The rig's buffers are
  4 × 8,192 × 11 = 360,448 bytes against 451,564 free.
- **Error:** a config over RAM fails at compile with `Program requirement exceeds
  512KB hub RAM`. The Wiring Guide states that (it is not a startup check).

## 11. Bench validation

The visits are as in the table above. Results go to `DOCs/bench/RUN-NOTES.md`
(the executing side's custody). Each chip's acceptance updates
`DOCs/ChipCharacteristicsMatrix.md` and `DOCs/AuthorTestConfigurations.md` (§12).

## 12. Documentation

**Conformance:**
- `driver/*.spin2` follow `central:spin2-authoring-guide`; `STYLE_GATE_COMMAND`
  (`python3 tools/check_style.py`) passes for every changed file.
- `ChangeLog.md` follows `central:changelog-voicing` (class 1).

### Documentation Blast Radius

The doc audit at plan time (`python3 tools/check_docs.py`), verbatim:
```
Doc-drift audit (advisory) -- 23 documents, 32 .spin2 sources
ORPHAN (0)
DUPLICATE (0)
COUNT (0)
```

The audit's 0/0/0 is not the whole picture: the survey found duplicated tables
the audit can't see, and those are fixed by keeping one canonical copy.

| Behaviour changed | Artifacts that describe it | Action |
|---|---|---|
| **Refresh method and rates** | THEOPS.md:194-202; DOCs/TheoryOfOperations.md:150, :202, :385-391; DOCs/WiringGuide.md:228-250; ChangeLog.md:58-59 (known issues); README.md:23, :101, :390; DOCs/FutureDirections-ImageAndColor.md:146-171, :232, :266, :316, :329; HUB75-Driver-SWver1.md:100, :139, :159, :202; rgb3bit doc comments (:846 and `cmdDsplyFrameSet`) | Canonical method and rate tables in **DOCs/WiringGuide.md "Refresh rate"**, rewritten with visit C and D measurements. THEOPS and TheoryOfOperations keep a short description of the method and **link** to it. The FutureDirections copy is replaced by a link. The HUB75-Driver-SWver1 notes are history and get a "superseded" banner. |
| **Target refresh setting (new)** | README config table :167 and its duplicate THEOPS.md:174 | Add the `DISPn_TARGET_REFRESH_HZ` row. **Make README the canonical config table and have THEOPS link to it.** |
| **Shift clock and chip timing** | DOCs/TheoryOfOperations.md:389; DOCs/WiringGuide.md:230; DOCs/FutureDirections-ImageAndColor.md:171; DOCs/AuthorTestConfigurations.md:95, :121, :196, :243, :294, :317-318, :398; DOCs/ChipCharacteristicsMatrix.md:73-85, :173, :177, :225, :229, :702; README.md:111-116; THEOPS / TheoryOfOperations :487-491; DOCs/ICN2037/README.md:50, :55, :81, :215-218, :274, :342, :409, :413; HUB75-Driver-SWver0.md | Correct to the datasheets: ICN2037 rated 30 MHz (20 ns pulses cap it at 25 MHz) and /OE minimum 60 ns, which `DOCs/ICN2037/README.md` already says correctly (the V2.0 sheet's 40 ns is noted beside it); MBI5124GP OE 50/60/70; FM6124 30 ns added; ICN2038S has register commands. **Canonical chip table in DOCs/ChipCharacteristicsMatrix.md**, with README, THEOPS, TheoryOfOperations and AuthorTestConfigurations linking to it rather than repeating the clock column. SWver0 gets a history banner. |
| **Default depth 8-bit** | hwPanelConfig :83, :170, :245 and template comments; README.md:208, :245, :284; THEOPS.md:210 | Update the examples and comments. |
| **Double buffering and `showFrameSet`** | DOCs/TheoryOfOperations.md:56, :121, :125, :186-188, :280, :310 (these claim double buffering that wasn't connected); THEOPS.md:194; panel.spin2 comments :93, :146-149, :184, :488, :688-701 | Describe the real rule and the new call; doc comment on `showFrameSet`. |
| **Brightness** | display.spin2:260-276 doc comments; DOCs/TheoryOfOperations.md:150, :171-172; colorUtils `setBrightness` comments | Brightness is OE time; full depth at any brightness; the floor at the chip's minimum OE; lower average current. |
| **Instrumentation** | DOCs/AuthorTestConfigurations.md:368-416 (logic-analyzer setup) | Replace with the `HUB75_INSTRUMENT` harness and its monitor map; the logic analyzer kept for waveform shape only. |
| **Limits and capacity** | DOCs/WiringGuide.md:189 "Driver limits" (canonical); DOCs/AuthorTestConfigurations.md:325-333 (duplicate) | Fold the capacity model's tables into the Wiring Guide; replace the AuthorTestConfigurations copy with a link. |
| **Timing claims** | `14,183`, `24,742` in analysis and plan docs only | Updated by measurement in the Wiring Guide where rates are stated; analysis docs keep their dated figures. |
| **New files** (`test_hub75_oe_bcm`, `test_hub75_rates`, `test_hub75_converter`, `isp_hub75_instrument`) | THEOPS file-organization table; CLAUDE.md architecture and top-file count (16 → 18; `test_hub75_oe_bcm` is already in the `BUILD_COMMAND` list); `.claude/skill-conventions.md` `BUILD_COMMAND` list | Add them, and update the count wherever it is stated. |
| **ChangeLog** | ChangeLog.md `[4.0.0]` (in development) | User-facing entries: the refresh method, the target refresh setting, 8-bit default, brightness, tear-free commit, `showFrameSet`, faster commit and drawing, chip-doc corrections, and the strobe-pin fix for base-0 adapters. Known issues :58-59 rewritten from measurement. |
| **Prior art** | THEOPS refresh section | One sentence: the method is the widely used binary-coded (bit-angle) modulation with output-enable weighting. |

## Entry baseline (measured 2026-10-03 on the sprint-start commit `407b609`, macOS)

- **Build (the substitute gate; the project has no automated test suite):** all 16
  top files compile with `pnut-ts -d -l -m` (the `BUILD_COMMAND` list in
  `.claude/skill-conventions.md`): rc 0 each, 0 warnings and 0 errors in the full
  captured log, 48 outputs written (`.bin`, `.lst`, `.map` per file).
- **Coverage:** the 16 files in the list are exactly the 16 `driver/` files that set
  `_clkfreq`. No top file is excluded.
- **Style gate** `python3 tools/check_style.py`: exit 0. Not checked by the script:
  19 rules assigned T1 but not yet implemented, 5 T1+T2, 20 T2 (agent audit) and
  2 T3 (Stephen's decision). The script is unchanged since the first measurement
  at `86830c4`, so these were unchecked then too.
- **Doc audit** `python3 tools/check_docs.py`: 0/0/0 (23 documents, 33 `.spin2`
  sources).
- **Failure groups:** none, so there is no fix-when decision to record.
- **What this does not prove:** compiling is not running. Behaviour is verified
  only at the bench visits (`DOCs/bench/RUN-SHEET.md`, results in `RUN-NOTES.md`).

## Sprint start (2026-10-03)

- **Build number:** 4.0.0 (see Status).
- **Working tree:** clean apart from Stephen's untracked
  `driver/PSRAM_driver_RJA_Platform_1b.spin2`. It is outside this sprint's blast
  radius and belongs to the follow-on slideshow sprint, so it stays untracked and
  untouched.
- **Tracking readiness:** ready. No tasks on the board (0 to archive, none left
  over); 2 context keys, the live resume pointer and the paused green-panel sweep
  notes (outside this sprint); `MEMORY.md` 7 lines, no misfiled judgement.
- **Entry baseline:** above, re-measured on the sprint-start commit.

## Named unknowns (each with its planned response)

- **A chip that cannot take data while lit:** none was found at visit A, on all
  four bench chips, so §4 has no shift-while-dark path. The ICN2038S, DP5125D and
  GS6238S have no panel on this bench and are untested. If one later shows a
  wrong image, the prototype's `SHIFT_WHILE_DARK` mode confirms the cause, and
  adding the path to the core is raised with Stephen as a logged scope change.
- **Cog RAM headroom:** settled at closeout (2026-10-05): the refresh core's cog image
  ends at cog address 280 of the 496 its `FIT` allows, so 215 longs are free at
  `e1c76d1` (compiler listing of `isp_hub75_rgb3bit.spin2`). The line buffer stayed in
  cog RAM.
- **A 14-clock shift split meeting 20 ns both ways:** settled by the loop's
  instruction count («#93»): the shift loop's fixed high half is 6 clocks (DRVH, WAITX,
  SETBYTE), 17.9 ns at 335 MHz, so it needs one WAITX clock to reach 20 ns, and 15 is
  the shortest loop (high 7 clocks, 20.9 ns; low 8, 23.9 ns).
- **The shimmer verdict:** settled at visit C (2026-10-04): steady at 5, 6, 7 and 8 bit
  by eye (Stephen, quoted in RUN-NOTES and the punch list). §6 needed no interleave;
  the punch item is closed («#95»).

## Tasks (generated 2026-10-03, sprint tag `framerate`)

| Plan § | Deliverable | Task | seq | Runs on |
|---|---|---|---|---|
| §2 | `HUB75_INSTRUMENT` harness, `test_hub75_rates` | «#88» | 1 | either (compile) |
| Visit B | today's driver measured: the "before" | «#89» | 2 | macOS + quad rig |
| §12 (chip ratings) | chip-rating docs corrected to the datasheets | «#90» | 3 | either |
| §3 | tear-free commit, `display.showFrameSet` | «#91» | 4 | either + rig check |
| §4 | OE-weighted refresh core, target refresh, brightness as OE time | «#92» | 5 | either + rig check |
| §5 | shift clock at the 20 ns limit | «#93» | 6 | macOS + quad rig |
| Visit C | §3-§5 accepted on the quad; shimmer observed; §7-§9 "before" times | «#94» | 7 | macOS + quad rig |
| §6 | shimmer punch item closed, or planes interleaved | «#95» | 8 | either |
| §10 | 8-bit default | «#96» | 9 | either |
| Visit D | per-chip acceptance, single panels | «#97» | 10 | macOS + singles |
| §7 | `MERGEB` converters, `test_hub75_converter` | «#98» | 11 | either + P2 harness |
| §8 | colour table | «#99» | 12 | either + P2 self-test |
| §9 | row-run primitives | «#100» | 13 | either + P2 self-test |
| Visit E | §7-§9 accepted | «#101» | 14 | macOS + quad rig |
| §12 (measured) | refresh, brightness, buffering docs; ChangeLog | «#102» | 15 | either |
| §4 (visit C finding) | /OE pulses start at once; brightness linear (added 2026-10-03) | «#103» | — | either + quad rig |
| §7 (SC-1) | converter hub-slice stall removed (added 2026-10-05) | «#104» | — | either + P2 timing |
| §4/§5 (visit D finding) | overlapped-latch clock pulse ended before the dark wait (added 2026-10-05) | «#105» | — | either + FM6126A |

§1 (the prototype) and §11 (bench validation) have no task of their own: §1 was done
in planning (visit A), and §11 is the visit tasks.

- **Dispatch model:** `arbiter-serial`, the project default. The exclusive resources
  are the compiler outputs in `driver/`, `ChangeLog.md` and the user configuration
  files, so no two tasks run at once.
- **Two-phase tasks:** «#92» (§4), «#98» (§7) and «#100» (§9). The first dispatch
  returns the design with one instance applied for review.
- **One boundary moved:** the brightness multiply in `correctedSingleColor` is
  removed in «#92» (§4), not in §8. Brightness becomes OE time in §4, so leaving the
  multiply until §8 would apply brightness twice in between.
- **Ordering:** visit B runs before any core change, so it measures today's driver.
  Visit C records the commit and draw times that visit E compares against, because
  §3 changes commit. The chip-ratings docs task needs no hardware and runs during
  bench waits.

## Revision history

- 2026-10-02 — draft written after scope confirmation and the research pass.
- 2026-10-03 — bench visit A completed on the quad rig, FM6126A and MBI5124GP.
  Question 3 answered; §4 drops the shift-while-dark path; exit gate walked and
  the plan marked ready. Visit A then also run on the FM6124 (Stephen offered the
  panel): correct while shifting lit.
- 2026-10-03 — sprint started: build 4.0.0 agreed; entry checks recorded.
- 2026-10-03 — §5's premise (study Q3, 20 ns minimum clock pulse) settled from the
  five datasheets at task generation. It had been left open when the exit gate was
  walked.
- 2026-10-03 — at task generation, the ICN2037 minimum /OE was corrected from 40 to
  60 ns in §4 and §12. The datasheet revisions disagree (V1.1 and the timing sheet
  say 60, V2.0 says 40), and §12 would otherwise have changed a correct doc to a
  wrong one.
- 2026-10-03 — tasks «#88»-«#102» generated; cross-reference table added.
- 2026-10-04 — visit C completed; results table added. §3's tearing acceptance changed
  from an observation to the pin take check (agreed with Stephen).
- 2026-10-03 — visit C finding: two §4 defects fixed by «#103» (/OE start latency,
  linear brightness), added mid-sprint; visit C resumed after it.
- 2026-10-05 — visit E completed; results table added. §7's commit time misses its
  prediction (6.58 ms against about 5 ms at 5-bit); recorded on the punch list.
- 2026-10-05 — cause of the commit miss measured (plane writes share one hub slice);
  SC-1 agreed with Stephen and done in «#104» (4.09 / 3.26 ms at 8 / 5-bit).
- 2026-10-05 — visit D completed on the FM6126A, MBI5124GP and FM6124 («#97»); results
  table added. «#102»'s visit-D doc rows done.
- 2026-10-05 — visit D finding: the overlapped-latch path held one clock pulse high
  through the dark wait; ended before it in «#105». The clock halves were found
  swapped in the visit C note and the docs (high 7 clocks, low 8); corrected.
- 2026-10-05 — closeout audit: named unknowns 2 and 3 settled; task table gains
  «#103»-«#105».
