# Frame-Rate Study

**Status:** register complete, waiting for Stephen's review. This study is
report-only: nothing in the driver was changed.
**Date:** 2026-10-02. **Build:** 4.0.0 in development.

## 1. Scope (agreed with Stephen, 2026-10-02)

**The question:** where can the driver be made faster, so that every supported panel
reaches the best display rate it can, and which of those opportunities give the
largest wins?

Four paths are studied, and each is ranked separately:

1. **Refresh.** One full colour frame sent from the refresh cog to the panels. The
   goal is 60 Hz or more, at the deepest colour depth possible, without flicker.
2. **One frame to the display.** Draw, then commit (convert to bit-planes), then
   hand-off to the refresh cog.
3. **Back-to-back frames.** How often a new frame can replace the previous one, and
   how short and invisible the switch is.
4. **Slideshow** (added by Stephen during the study). BMP images from microSD,
   staged through PSRAM, and the time and visibility of the switch between images.

**Resources in scope:**
- LUT RAM, more cogs, the streamer, smart pins, data structures and code.
- The 32 MB PSRAM and the microSD slot on the P2-EC32MB Edge.
- The clock: 335 MHz is the baseline. 360 MHz is reported separately as a trade
  against heat, and no finding depends on it.

**Ranking criteria:**
1. Expected gain.
2. Size of the driver change.
3. Cost in cogs and RAM.
4. How the RAM cost grows with total pixel count. Stephen: RAM grows with panel
   size, so efficiency matters most on large displays.

**Source material:** these were read for their topics only, and every claim was
checked against today's code:
- `DOCs/plans/archive/Sprint-Performance-Upgrade.md`
- `DOCs/plans/archive/DRAW-PATH-PERFORMANCE-SPRINT-PLAN.md`
- `DOCs/CodeAssessment.md` §2 and §4
- the punch list's performance items

**Excluded:**
- Changes to the meaning of the public drawing API. Its speed is in scope.
- Panel chips the driver doesn't support.
- Hardware changes to the adapter board.

**Measurement:**
- *Measured* means a rig figure: the 2x2 ICN2037 rig, at 335 MHz and 5-bit.
- *Calculated* means derived from cycle counts and datasheet timing, as noted
  in each row.

## 2. Read order

- [x] R1 Refresh core: `driver/isp_hub75_rgb3bit.spin2` PASM (:718-1199), read in full by the arbiter
- [x] R2 Commit and hand-off: `isp_hub75_panel.spin2` converters, `display` commit, `hwBuffers` allocation (survey; frame-set toggle verified by the arbiter)
- [x] R3 Draw path: `screenUtils`, `colorUtils`, `hwBufferAccess`, `display` primitives, text, BMP, scroller (survey; colour path and line loop verified by the arbiter)
- [x] R4 P2 resources (P2KB): streamer, smart pins, LUT RAM, hub FIFO, MERGEB (survey; MERGEB checked by the arbiter)
- [x] R5 Chip limits: the datasheets under `DOCs/<chip>/` (survey; text extracted with PDFKit)
- [x] R6 Source documents: their topics, checked against R1-R5 (arbiter)
- [x] R7 PSRAM on the P2-EC32MB (P2KB survey)
- [x] R8 BMP and slideshow path, SD drivers (survey)

## 3. The refresh model

Every refresh number below comes from this model.

**Terms:**
- **S** is the time to shift one row of the chain: columns × clocks per column ÷
  sysclk.
- **R** is the number of row addresses.
- **N** is the colour depth.

**Today:** each plane k is shifted out again 2^k times, so one frame costs
**R · S · (2^N − 1)**. This is traced at `isp_hub75_rgb3bit.spin2:842-866`: the
repeat count `pwmFrameSetCt` runs 16, then 8, 4, 2, 1.

**Check against the rig:** 512 columns × 16 clocks ÷ 335 MHz gives S = 24.45 µs, and
R = 32.
- At 5-bit the model gives **41.2 Hz** against **40.1 Hz measured**, so the
  refresh core is at about 97% of the shift ceiling.
- At 8-bit the model gives 5.0 Hz against 4.6 Hz measured.

**OE-weighted method (F2):**
- Shift each plane **once** per row address, and hold OE on for that plane's
  weight, 2^k · T.
- The next plane shifts in while the current one is lit.
- With T = S / 2^j, one row costs S · (j + 2^(N−j) − 1).
- Brightness duty is (2^N − 1) / 2^j ÷ (j + 2^(N−j) − 1). The parameter j trades
  refresh against brightness.

**Calculated refresh, with j chosen for at least 80% brightness:**

| Configuration | Clocks/col | 4-bit | 5-bit | 6-bit | 7-bit | 8-bit |
|---|---|---|---|---|---|---|
| Rig, 4×128×64 chained (512 col, 32 addr), today | 16 | 85 | 41 *(40.1 measured)* | 20 | 10 | 5.0 *(4.6 measured)* |
| Rig, OE-weighted | 16 | 160 (94%) | 142 (86%) | 75 (93%) | 71 (88%) | **67 (84%)** |
| Rig, OE-weighted + F3 clock | 14 | 183 | 162 | 86 | 81 | **77** |
| 4×64×64 chained (256 col, 32 addr), today | 16 | 170 | 82 | 41 | 20 | 10 |
| 4×64×64 chained, OE-weighted | 16 | 320 | 284 | 150 | 142 | **135** |
| **Cube: 6 × 64×64 ICN2037BP, unwrapped chain (384 col, 32 addr), today** | 16 | 114 | 55 | 27 | 13 | 6.7 |
| **Cube, 60 Hz target** (the brightest setting that meets it) | 16 | 114 (100%) | 106 (97%) | 100 (93%) | 95 (88%) | **90 (84%)** |
| **Cube, 60 Hz target** + F3 clock | 14 | 130 (100%) | 63 (100%) | 61 (98%) | 108 (88%) | **102 (84%)** |
| 1×64×64 (64 col, 32 addr), today | 16 | 682 | 330 | 162 | 81 | 40 |
| 1×64×64, OE-weighted | 16 | 1278 | 1136 | 601 | 568 | **538** |

Percentages are brightness duty against today's method.

## 4. Findings register

**Rate** is R (refresh), F (one frame), B (back-to-back frames) or S (slideshow).
**Mark** is *traced*, *calculated* or *inferred*.

| # | Rate | Finding | Evidence | Mark | Expected gain | Change size | Cog / RAM cost | Chips helped |
|---|---|---|---|---|---|---|---|---|
| F1 | R | The refresh core re-shifts each plane 2^k times. The frame cost is exponential in depth, and the core already runs at about 97% of that ceiling, so tuning the shift loop has about 3% left to win. | rgb3bit:842-866, 1039-1047; model in §3 against measured 40.1 / 4.6 Hz | traced | (diagnosis) | n/a | n/a | all |
| F2 | R | **Weight planes by OE time instead of repeating shifts.** Per row address, shift each plane once and hold OE for 2^k·T with a smart-pin pulse (`P_PULSE` with inverted output; one `WYPIN` starts it, `IN` flags the end). The next plane shifts in during the lit time. The frame-set layout stays as it is: row r of plane k is still at base + k·frame + r·row. | §3 model; p2kbArchSmartPin00100PulseCycleOutput. No supported chip has a grayscale engine, and the dual latch takes data while lit (ICN2037 p.5-6, FM6126A p.5-6, FM6124 p.1, ICN2038S p.7). Shortest OE: 30-60 ns, below 0.3% of S. | calculated | **Rig 8-bit 5 → 67 Hz (13×), 5-bit 41 → 142 Hz (3.4×)**, at 84-94% brightness. j can be tuned per configuration. | Large: the refresh core's frame loop and per-row sequencing are rewritten; the PASM stays within cog RAM | 0 cogs, 0 RAM | all except MBI5124GP, where the dual-latch behaviour is undetermined (Q2) |
| F3 | R | The shift clock runs at 16 clocks per column (20.94 MHz). The datasheets allow 30 MHz (ICN2037 V2.0, ICN2038S, FM6124, FM6126A) or 25 MHz (MBI5124GP), but a 20 ns minimum clock pulse makes 7 + 7 = **14 clocks (23.9 MHz)** the practical floor at 335 MHz. Today's loop is 7 two-clock instructions plus two `WAITX`, with about 7 clocks low and 9 high. An exact 7/7 split in 14 clocks needs an odd-length `WAITX` in each half, which may not fit around the instructions that must sit inside the loop. The safe software target is **15 clocks (22.3 MHz)**. An exact 14 needs a reordered loop or F5's smart-pin clock. | rgb3bit:1039-1047, the `clkfreq / 20_000_000` divisor near :324; chip survey | calculated | **+7% (15 clocks) to +14% (14 clocks)** on every scheme | Small: the divisor and the loop's instruction order | none | all; check on the rig |
| F4 | R | **360 MHz gives no shift-rate gain.** A 20 ns pulse needs at least 7.2 clocks at 360 MHz, so the clock becomes 8 + 8 = 16 clocks, or 22.5 MHz. That is slower than 335 MHz at 14 clocks. Spin2 drawing gains about 7.5%. | arithmetic from F3 | calculated | refresh 0 (−6%); draw +7.5% | config only | heat | none for refresh |
| F5 | R | **Streamer plus a smart-pin CLK** (the documented flash-loader pattern: 8-bit `X_RFBYTE` on base+8..15, `P_TRANSITION` on CLK). It can't beat the chip's clock limit, so it gives **no rate gain** beyond F3. It does free the cog during the shift, to run OE timing, prefetch and command polling, and it streams from hub through the FIFO. That **removes the 512-byte line-buffer limit on columns per adapter**. Data-to-CLK alignment is empirical and needs logic-analyzer proof. | p2kbPasm2Xinit, p2kbPasm2StreamerSmartpinControl, p2kbArchModesReference; line-buffer limit in the DISPLAY-ORGANIZATION limits table | inferred | 0% rate; raises the chain-length limit | Large | 0 cogs; the cog line buffer is freed | all; matters for long chains |
| F6 | R | Per-row overhead (latch, address, settle waits, sub-page reload) is about 3% of a pass. The old plan's LUT double buffer with a loader cog (+1.6%) **isn't worth a cog**. | rgb3bit:1049-1077, :907-911; old plan Finding 3a | calculated | ≤3% | Small to medium | +1 cog for the LUT scheme | all |
| F7 | R | Refresh scales with 1 / (columns per adapter). Splitting one display over two adapters doubles refresh, but the driver treats each adapter as its own display. A display that spans adapters would be a new feature. | `display.start(HUB75_ADAPTER_n)`, one DISPn per adapter | inferred | 2× per extra adapter | Large (new feature) | +1 refresh cog per adapter | all |
| F8 | R | The 5-bit+ shimmer (punch list) comes from long back-to-back MSB repeats at a 20-40 Hz frame rate. F2 raises the frame rate to 140+ Hz and puts all of a row's planes inside one row slot, so it **probably removes the shimmer**. Plane-order interleaving stays as a fallback. | PUNCH-LIST "Interleave the bit-plane repeats"; §3 | inferred | visual | none beyond F2 | none | all |
| F9 | B | **Double buffering is allocated but never connected.** Two frame sets exist per adapter, but `clearPwmFrameBuffer` (the only toggle) runs only twice at start, which cancels out. Both converters write into `getActivePwmBuffer()`, which is the set the panels are showing. So every commit **tears** for about 14 ms, while the second set (80 KB on the rig) sits unused. The refresh cog already reads a new pointer only at the end of a frame set, so a swap would be gap-free. | panel:148-149, 255, 506, 750-765; rgb3bit:802-809 | traced | correct, zero-gap frame switch; no tearing | Small: convert into the idle set, swap, and add a "swap taken" handshake before reusing the old set | 0 (the RAM is already spent) | all |
| F10 | F, B | **The converter extracts bits one at a time:** 6 `TESTB` and conditional `OR`s per plane per pixel pair, about 300 clocks per pair. That matches the measured 14.2 ms. The P2's `MERGEB` transposes 4 bytes × 8 bits in 2 clocks, which gives every plane's nibble for R1, G1, B1 in one instruction (and for R2, G2, B2 in a second). The per-plane cost falls to about 5 instructions. This change supersedes the punch-list's per-plane hoists. | panel:594-644; p2kbPasm2Mergeb | calculated | commit **14.2 → about 5 ms** at 5-bit, and about 23 → 7 ms at 8-bit (about 3×) | Medium: rewrite both converter inner loops | none | all |
| F11 | F, B | The converter runs inline in cog 0, so drawing frame N+1 has to wait for frame N's commit. Moving the converter to its own cog pipelines them, and frame throughput becomes max(draw, convert) instead of their sum. | panel:523-655 (ORG in a PUB); survey §4 (only refresh cogs are started) | traced (placement), inferred (gain) | up to the full convert time per frame | Medium | +1 cog | all |
| F12 | F | **Colour correction is 27 of the 36 Spin2 calls per pixel.** Each channel re-resolves depth and frame count through `ptrTableEntry` and does a divide, three times per pixel, even for a flat fill. A per-adapter correction table (3 × 256 bytes, rebuilt when brightness, gamma or depth changes) and cached chain settings would replace that with 3 byte reads. | screenUtils:107-111; colorUtils:271-303; draw survey | traced (count), inferred (gain) | **draw about 60-70% faster** (rig flat draw 192 ms → about 60-75 ms) | Small to medium | 768 B per adapter | all |
| F13 | F | Horizontal lines, filled boxes, text glyphs and BMP rows go through the full per-pixel path. `fillLayoutArea` is the only partial run primitive, and it still resolves the address per pixel. A row-run primitive (resolve the address once, then step by the pixel stride) and an inline-PASM fill/blit for rotation 0 would cut these to a few cycles per pixel. | display:1350-1355, :1545, :1228/1270; screenUtils:114-149 | traced | large for fills, boxes, text, BMP | Medium | none | all |
| F14 | F | `panelCoordsAt` does 4 divides per pixel (2 `/`, 2 `//`). Stepping incrementally along a run, or a single-panel fast path, removes them. | hwBufferAccess:1716-1739 | traced | about 10-15% of draw (inferred) | Small | none | all |
| F15 | S | **A slideshow image takes about 0.2-0.27 s today.** BMPs are compiled into the image (no SD), and each display pixel goes through the 35-call path; the draw is about 93% of the time. | display_bmp:111-174; demo_hub75_color:1155-1164 | inferred (time) | (diagnosis) | n/a | n/a | all |
| F16 | S | **Pre-converted frame-set files.** On the PC, convert each image to the exact frame-set layout for the wiring and depth. Read it from SD straight into the idle frame set and swap (F9): no draw and no commit. Stephen's own FAT32 SD drivers are OBEX 5404 and 5405. With PSRAM, about 400 rig frame sets fit in 32 MB, and one copies to hub in about 0.3-0.5 ms. The fallback that keeps BMP files: bulk row reads with the F12 colour table. | survey §3; p2kbHwEdge32mbModuleEdge32mbModule | inferred | image switch about 0.25 s → **under 1 ms from PSRAM**, and invisible | Medium: a PC-side converter tool, a raw-load call, and slideshow staging | +1 cog (PSRAM); the SD cost is not measured | all; files are tied to one configuration |
| F17 | S | **PSRAM uses pins P40-P57.** The adapters at base 32 and base 48 collide with it, so with PSRAM at most 2 adapters (base 0 and 16) can run. microSD shares the boot flash's pins, P58-P61 (Stephen, 2026-10-02), so it doesn't conflict. | `driver/PSRAM_driver_RJA_Platform_1b.spin2`:11-14 (CS P57, CK P56, data on DIRB `$00FF_FF00` = P40-P55); p2kbHwEdge32mbModuleEdge32mbModule | traced | constraint | n/a | caps the adapter count | n/a |
| F18 | all | **RAM per adapter is P · (3 + N) bytes**, where P is the pixel count. That is the 3-byte screen buffer plus two N-plane frame sets of P/2 bytes each. The rig uses 256 KB at 5-bit and 352 KB at 8-bit, out of 512 KB of hub. Large displays can't hold both. The levers: put the screen buffer in PSRAM (convert by row chunks), or drop it on a pre-converted slideshow path (F16). | hwPanelConfig:128-152; hwBuffers:36-60 | calculated | sets the largest display per depth | Medium | n/a | all |
| F19 | S | **Stephen's PSRAM driver** (`driver/PSRAM_driver_RJA_Platform_1b.spin2`). What it provides:<br>- One cog, started with `coginit(16, ...)`.<br>- A 16-bit bus, moving one long every 4 clocks (1 byte per clock, about 335 MB/s peak at 335 MHz).<br>- Block copy only, between hub and PSRAM, through a 3-long mailbox per cog (hub address, PSRAM long address, count; negative count = write; the driver zeroes the count when done). Any cog, including a PASM cog, can make a request from its own slot at `pointer() + cogid() * 12`.<br>- Transfers are split at 4 KB pages, with a few dozen clocks of overhead per page.<br>- Tuned for 250-340 MHz, which is one more reason not to run at 360 MHz (F4).<br>It has no fill, no 2-D copy and no output to pins. For F16 that is enough: an 80 KB rig frame set is 20,480 longs, about 82,000 clocks, or **about 0.25 ms**. | driver file :1-6, 38-45, 56-75, 112-188, 193-219 | traced | confirms F16's switch in under 1 ms | none: the driver is used as it is | +1 cog | n/a |
| F20 | S | **A pin fault in the driver's Edge setup, on every PSRAM read.** `start()` runs `pinl(49)` in the calling cog (cog 0), commented "keep other PSRAM bank CS from turning on". That line belongs to the SimpleP2 board setup (the copy in `REF-23MB/` has that setup active). On the Edge, P49 is a data pin (bank 2, SIO1). Every cog's pin direction and output are OR'd onto the pin. So cog 0's direction bit keeps P49 an output, driven at the OR of the outputs, even after the driver cog floats its own data pins to read (:228). The P2 then fights PSRAM bank 2's SIO1 on every read, and that bit can come back wrong. Writes are not affected: cog 0's low output ORs with the driver's data. | driver file :42, :98, :228; diff against `REF-23MB/`; the pin-sharing rule from Stephen, 2026-10-02 | traced | correctness of every PSRAM read | One line: remove `pinl(49)` from the Edge configuration, or move it inside the SimpleP2 block | none | n/a |
| F21 | S | **CS is held low longer than the chip allows.** A 4 KB page at 1 byte per clock holds CS low for about 4,100 clocks, or **12.2 µs at 335 MHz**. P2KB gives the APS6404L's maximum CS-low time as **8 µs**, so the chip can refresh itself. Holding it longer risks data loss over time, which matters for a slideshow library that stays in PSRAM. | driver :207-219 (page = `$400` longs); p2kbHwEdge32mbModuleEdge32mbModule (`max_cs_low_us = 8`) | calculated | data integrity for long-held content | Small (a smaller page split) | none | n/a |
| F22 | F, R | **PSRAM is a capacity and staging resource, not a speed one.**<br>*Present, with buffers in hub:*<br>- Refresh, drawing and commit are unaffected; all three touch only hub RAM.<br>- Whether a busy PSRAM cog slows another cog's hub access is unverified (P2KB doesn't settle it). Measure refresh with the PSRAM cog copying against idle.<br>- Cost: one cog, the adapters at base 32 and 48, and a little constant power, because the driver's idle loop re-reads its command list without pause.<br>*Buffers moved into PSRAM (F18):*<br>- Every pixel access becomes a mailbox request costing hundreds of clocks. Drawing would need a hub row-band cache to stay usable.<br>- Commit adds about 0.3 ms per rig frame for band reads.<br>- Refresh is unchanged if the frame sets stay in hub. | PSRAM driver :112-124 (idle loop), :56-75 (mailbox); hwBufferAccess `displayPixelAddress` (hub byte writes) | inferred | none for normal drawing; a slowdown if the screen buffer moves to PSRAM | n/a | +1 cog; heat | n/a |
| F23 | all | **The logic-analyzer strobe pins are fixed at P8-P11 for every adapter.** Each refresh cog sets them to `P_LOW_1MA` and toggles them at command, frame-set, plane and sub-page starts. With two or more adapters, several cogs drive the same pins (the one-owner rule is broken, and the strobes OR together). An adapter at base 0 has P8-P11 as its R1, G1, B1 and R2 colour lines, so its colour pins get weak drive and every adapter's strobes toggle them. The rig (one adapter at P16) is not affected. | rgb3bit:36-40, :303-314, :738-739, :817, :843, :853, :872 | traced | correctness with multiple adapters or an adapter at base 0 | Small: put the strobes, and the monitor harness that counts them, behind one instrumentation `#IFDEF`. Instrumentation is only ever run with one adapter (Stephen, 2026-10-02), so test builds keep P8-P11, and a normal build never touches them. This also takes the strobe instructions out of the refresh loop in normal builds. | none | all |
| F24 | R | **Apply brightness as OE time, not value scaling.** Today brightness multiplies each colour value before depth reduction (colorUtils:124), so dimming throws away colour depth (at 50%, 8-bit values reach only 128). With F2, a global brightness can shorten the OE unit T instead, keeping all N bits at any brightness. F2's brightness ceiling (84-94%) then costs nothing for anyone running at or below it: it is where their dimming happens anyway. Stephen, 2026-10-02: the panels are very bright, so 84% is unlikely to be noticed. **Supply current:** the current while a row is lit is unchanged, so peak current and supply sizing stay the same, but **average current and heat at full white fall in proportion to duty** (about 16% at 84%). | colorUtils:100-126 (brightness, gamma); §3 model | inferred | full colour depth at every brightness; lower average current | Small, alongside F2: one OE-unit scale and dropping the value multiply | none | all |
| F25 | S | **Pre-built frames run at video rates; two things decide video quality.** The rig refreshes 8-bit at 65.9 Hz (measured, visit A), so one new frame per refresh is about 66 fps.<br>(1) **Exact-rate pacing.** The target rule gives at least 60 Hz (65.9), not exactly 60, so 30 fps content judders (frames shown 2 or 3 times). Pace the refresh to a multiple of the content rate (60.0 for 30/60 fps, 48 for 24 fps) with a timed end-of-frame pause.<br>(2) **Supply rate.** PSRAM holds about 250 8-bit rig frames (128 KB each; about 8 s at 30 fps) or about 400 at 5-bit. Longer video streams from microSD and needs about 3.9 MB/s for 30 fps at 8-bit on the rig. **Stephen's microSD driver reads 2,400 KB/s** (his figure, 2026-10-03). Streaming frame rate by display at that rate (calculated): rig 18.3 fps at 8-bit, 24.4 at 6-bit (film), 29.3 at 5-bit; cube 24.4 at 8-bit, 39 at 5-bit; 1 × 128×64 or 2 × 64×64, 73 at 8-bit; 1 × 64×64, 146 at 8-bit. Hybrid: prefill PSRAM (256 rig 8-bit frames) and stream behind it. At 30 fps on the rig at 8-bit the buffer drains at 11.7 frames/s, so about 22 s of playback beyond what SD keeps up with. | visit A (RUN-NOTES 2026-10-03); F16, F19 | calculated | true video rates for clips and loops | Small (pacing); SD rate is a measurement | none | all |
| F26 | S | **Getting 24+ fps at 8-bit on the quad rig (video playback architecture).**<br>*Card rate is the limit:* one card is about 2.4 MB/s however many cogs read it. Cogs help by cutting the bytes per frame or by reading two sources at once.<br>*Options, rig at 8-bit (calculated):*<br>- Stream frame sets (128 KB): 18.3 fps.<br>- **Stream 24-bit RGB (98 KB) and convert on the P2: 24.4 fps, lossless**, with almost no margin.<br>- **YUV 4:2:0 (48 KB) plus a decode cog: about 48 fps**, with colour at half resolution as in standard video.<br>- Change-only compression plus a decode cog: depends on content.<br>- **A second microSD card** on an add-on with its own reader cog: **about 49 fps for lossless RGB.** Stephen, 2026-10-03: "2nd sd card is easy".<br>- SD high-speed mode, if the driver supports it: possibly about 2× per card (unverified).<br>*Files:* one contiguous file per clip, so frame n is at n × size and needs no directory lookup, with a header holding geometry, depth and rate. A file per image suits slideshows. Many per-frame files cost an open each (a linear FAT directory search) and break up long reads.<br>*Cogs:* reader(s) SD → PSRAM, then [decoder], then converter (F10, about 7 ms per frame) into the hidden frame set, then the refresh cog, plus the PSRAM driver's cog. | F16, F19, F25; Stephen's SD figure 2,400 KB/s | calculated | lossless 8-bit video at 24-30 fps on the quad with margin (two cards) | Medium-large (playback pipeline) | 3-4 cogs | all |

### What the source documents got wrong

| Old claim | Status today |
|---|---|
| "8-bit cannot reach 60 Hz even with all optimizations" (Sprint-Performance-Upgrade, Finding 5) | **Refuted** by F2. The claim assumed the repeated-shift method. |
| "Remove WAITX: +35%" | It runs the chips past their rated clock. The legal gain is F3's +14%. |
| "Streamer output: 10-20%" | The streamer can't shift faster than the chip's clock limit. Its value is the freed cog and longer chains (F5). |
| "HyperRAM: 0% refresh" | Correct for refresh. Its value is in slideshows and animation (F16). |
| About 47 calls per pixel (DRAW-PATH plan) | Now 36. Colour (27 calls) dominates, not geometry. The plan's colour table and run primitives are still open (F12, F13). |

### Design rule for every finding: one cog owns each pin

Every cog's pin direction and output are OR'd together. A second cog that touches a
pin, even only to drive it low, takes control of that pin away from its owner (F20 is
an instance of this). So:
- F2's OE smart pin, and F3/F5's CLK smart pin and streamer pins, belong to the
  refresh cog that owns the adapter.
- A converter cog (F11) and a PSRAM cog (F19) must never write an adapter pin.
- Start-up code in cog 0 must release every pin it set before handing the pin to
  another cog.
- The HUB75 driver already follows this rule. After starting the refresh cog,
  `start()` releases cog 0's hold on the address, colour and control pins with
  `pinclear` (`isp_hub75_rgb3bit.spin2`, after the `COGINIT` near :518). The PSRAM
  driver's `pinl(49)` (F20) is the one place the rule is broken.

## 5. Ranking: the best wins, not all of them

**Refresh:**
1. **F2, OE-weighted planes**, with **F24** (brightness as OE time). Every chip gains
   3-13×, and the rig reaches 67-77 Hz at 8-bit. This is the one change that moves
   the goal from impossible to met. F24 keeps full colour depth at any brightness
   and lowers average current.
2. **F3, a faster shift clock.** +7% to +14% for a small change, within the chips' ratings; it needs a rig check.
3. *Optional:* F5, the streamer. Take it only if longer chains per adapter are
   wanted. It is not a rate gain.

**One frame and back-to-back frames:**
1. **F9, connect the double buffer.** It fixes the tearing and makes the switch
   gap-free, and the RAM is already spent.
2. **F10, a MERGEB converter.** About 3× faster commit.
3. **F12 + F13, a colour table and run primitives.** The draw gets about 3× faster
   or more, and fills, text and BMP gain most.
4. *Later, if needed:* F11, the converter in its own cog.

**Slideshow:**
1. **F16, pre-converted frame sets staged in PSRAM**, swapped through F9. It uses Stephen's PSRAM driver (F19), after the possible pin fault (F20) and the CS-low time (F21) are settled.
2. F12 + F13 cover the BMP-file fallback.

**Not recommended:**
- 360 MHz for refresh (F4).
- The LUT double buffer with a loader cog (F6).
- Running the chips above their rated clock.

## 6. Not read, and why

- The FM6126A Chinese datasheet, FM6126B (unsupported), and the row-driver PDFs (TC7258, TC7262, RUC7258). They don't bear on column timing.
- The DP5125D and GS6238S have no datasheets in the repo.
- The SD drivers' source and their measured throughput. Stephen wrote OBEX 5404 and 5405, so his figures are the authority.
- `REF-23MB/PsramGraphics.spin2` was read only for how it uses the mailbox. The HDMI driver in `REF-23MB/` was not read.

## 7. Open questions

- **Q1 (answered: B):** each display gets a target refresh rate in `hwPanelConfig`, defaulting to 60 Hz. At startup the driver chooses the largest brightness setting (the smallest j) that meets it.
- **Q2:** Does the MBI5124GP accept shifted data while lit? No dual-latch text was found (p.2, p.12).
- **Q3:** Is the 20 ns minimum CLK pulse (behind F3's 14-clock floor) stated in each chip's dynamic table? It needs a visual read of the tables the extraction garbled (FM6126A, MBI5124GP).
- **Q4 (answered):** microSD shares the boot flash's pins (P58-P61). No conflict.
- **Q5:** The 23.9 MHz shift clock has to be shown on the rig: level shifters, ribbon length, and a four-panel chain.
- **Repo docs to correct, from the chip survey:**
  - ICN2037: the maximum clock is 30 MHz (`ChipCharacteristicsMatrix.md` says 20), and the minimum OE is 40 ns (`DOCs/ICN2037/README.md` says 60).
  - MBI5124GP OE is 50/60/70 ns, against the matrix's 45/55/65.
  - The FM6124 minimum OE (30 ns) is missing.
  - The ICN2038S is listed as "Init Required: No", but it has the same register commands as the FM6126A.
  - These are punch-list material. The punch-list item "ICN2037 20 vs 30 MHz" closes as 30 MHz.
