# Magic-Number Triage — §4c Conformance Wave 4

**Sprint:** source-reconciliation (build 3.0.3) · **Date:** 2026-06-07 · **Status:** DRIVER FILES APPLIED + VERIFIED. Demos pending.

**Sign-off (Stephen, 2026-06-07):** (1) B aggressiveness = FULL STRICT; (2) include category C = YES;
(3) audit demos = YES (lenient tier); (4) anomalies = FIX BOTH NOW (`36`/comment + remove `<>10` debug check).

## Apply + verification record (driver/library files)

13 files refactored (incl. the two test utilities). All 28 files compile clean (`-d`).

**Behavior-preservation proven by before/after BINARY comparison** (GOLD retired; this is the stronger
check). Method: compile every top-level entry point with AND without `-d`, sha256 the `.bin`, compare
each edited file in isolation (clean base + one edited file) against the pre-edit commit (fd87ac6).

- **12 of 13 files: byte-IDENTICAL** non-debug binaries -> provably pure value-preserving refactors:
  anlyCheck, test_hub75_pin_identify, display_bmp, fonts, panel, rgb3bit, screenUtils, hwBufferAccess,
  scrollingText, 7seg, segment, colorUtils (after refinement, see below).
- **colorUtils initially +8 bytes**: pnut-ts folds all-literal constant arithmetic (`(255*100)/60`,
  `5*60`) to an immediate, but computes the inline named-CON form at runtime (same result, more code).
  RESOLVED by moving the HSV constant arithmetic into CON *definitions* (`HUE_SEXTANT_1..5`,
  `HUE_FRACT_SCALE`) which fold at definition time -> now byte-IDENTICAL and fully named.
  LESSON: single-CON operands (`x & CHANNEL_MASK`) fold fine; multi-operand CON arithmetic *inline in
  code* does not -- put pure-constant arithmetic in CON definitions, not in statements.
- **display: intentional delta only** -- removed the dead `<>10` DEBUG edge-check + its orphan
  `VAR lastColumn` (anomaly #2), added `OBJ color` (for `color.CBLACK`). All value replacements
  verified correct by diff (Bresenham 2/3/2/4/10/6, dither $c000/14/3/1 use single-CON-operand inline
  arithmetic against variables, so they fold and add no code). Anomaly #1: `DITHER_BRIGHTNESS_PCT=36`
  named + misleading "50%" comment corrected.

Anomaly #3 (hard-coded chain `0` at display:242/244) left as-is: not a bug (single-chain-commit API).

---
**ORIGINAL TRIAGE (pre-apply) follows.**

Guide rule: `DOCs/policy/SPIN2-AUTHORING-GUIDE.md` §5.7 — every numeric literal with semantic
meaning must be a named `CON`. Permitted bare literals: `0` (init/zero-compare/null), `-1`
(sentinel/not-found), `4` (LONG<->byte conversion `n*4`). Driver/library files get STRICT treatment.

Triage categories:
- **A** = use a named constant that ALREADY exists (replace literal with the named reference)
- **B** = NAME ANCHOR (must-fix): semantic literal with no existing const; define a new `CON`
- **C** = name for readability (nice-to-have / borderline)
- **D** = leave (permitted bare literal, or obvious from immediate context)

**Tallies (occurrence-level, generous):** A ≈ 22 · B ≈ 200 · C ≈ 62 · D ≈ 191. Many B-findings
collapse onto a small shared constant vocabulary (see below), so the *new-constant* count is far
lower than 200. `isp_hub75_color`, `isp_hub75_hwPanelConfig`, `isp_hub75_hwEnums` are clean
(literals are all CON/enum definitions, out of scope). Demo `.spin2` files NOT yet audited (demo
tier is lenient; this wave targets the driver/library files per the §4c charter).

---

## 1. Anomalies surfaced during triage (NOT pure style — decide separately)

These are not magic-number fixes per se; triage exposed them. None is a confirmed regression.

1. **`36` brightness vs "50%" comment mismatch** — `isp_hub75_display.spin2:578` and
   `isp_hub75_scrollingText.spin2:515,581,644`: `reducedBrightnessOfCValue(rgbColor, 36)` with a
   comment saying "50% brightness". Value (36) does not match the comment (50). Either gamma makes
   36 perceptually ~50%, or the comment is stale. Worth a deliberate naming decision
   (`DITHER_BRIGHTNESS_PCT = 36`) AND a comment fix. Needs author intent.

2. **`if lastColumn <> 10` debug edge-check** — `isp_hub75_display.spin2:455`: a `DEBUG("DSP: ERROR1...")`
   guarded by a hard-coded expected end-column of 10. Looks like leftover app-specific (clock-demo?)
   scaffolding living in a driver method. Candidate for removal or DEBUG-channel gating (ties to
   follow-up #9 DEBUG_MASK), not a runtime path. Recommend remove or channelize rather than name `10`.

3. **Hard-coded chain index `0`** — `isp_hub75_display.spin2:242,244`:
   `hub75Bffrs.displayBufferAddress(0)` in the commit path. NOT a bug: `commitScreen` has no chain
   parameter and there is no `chainIndex` in scope, so `0` = first adapter chain is the only valid
   value under the current single-chain-commit API. Classify D (permitted index 0) or A
   (`hwEnum.HUB75_ADAPTER` first-index name). Multi-chain commit is a separate architectural item.

---

## 2. Proposed shared constant vocabulary (where many B-findings collapse)

### isp_hub75_colorUtils.spin2 (the densest cluster)
```
MAX_COLOR_VALUE         = 255          ' 8-bit channel full-scale
CHANNEL_MASK            = $ff          ' single 8-bit channel
RED_MASK                = $ff0000
GREEN_MASK              = $ff00
RED_SHIFT               = 16
GREEN_SHIFT             = 8            ' == BITS_PER_CHANNEL
BITS_PER_CHANNEL        = 8
FULL_BRIGHTNESS         = 256          ' "no reduction" sentinel (DAT default 256)
BRIGHTNESS_SHIFT        = 8            ' divide-by-256
BRIGHTNESS_ROUND_BIAS   = 128          ' +half-divisor for round-to-nearest
SOURCE_COLOR_BITS       = 8            ' 8-bit input depth
GAMMA_TABLE_MAX_IDX     = 255          ' 256-entry table
DEGREES_PER_CIRCLE      = 360
DEGREES_PER_HUE_SEGMENT = 60          ' 6 sextants
HUE_SEGMENT_MAX_IDX     = 59          ' 60-step segment last index
PERCENT_SCALE           = 100         ' (and PERCENT_SCALE_F = 100.0)
```
Sextant boundaries 120/180/240/300 -> expressible as `n * DEGREES_PER_HUE_SEGMENT`.

### isp_hub75_panel.spin2 + isp_hub75_rgb3bit.spin2 (PASM backend, duplicated across paths)
```
' RGB1/RGB2 plane bit values + masks (panel.spin2, used in both 8-row and 16-row PASM paths)
RGB1_RED_BIT=$01 RGB1_GREEN_BIT=$02 RGB1_BLUE_BIT=$04
RGB2_RED_BIT=$08 RGB2_GREEN_BIT=$10 RGB2_BLUE_BIT=$20
MASK_RGB1=$07  MASK_RGB2=$38  MASK_RGB12=$3F
HALF_DIVISOR=2  QUARTER_DIVISOR=4         ' scan-geometry splits
MSBIT_OF_BYTE=7  BITS_PER_BYTE=8  BYTES_PER_LONG=4
ASCII_SPACE=$20  ASCII_DIGIT_ZERO=$30  ASCII_UPPER_A=$41  MAX_DECIMAL_DIGIT=9  DECIMAL_BASE=10
' rgb3bit timing (WAITX) + scan counts — recurring protocol constants in a driver:
WAITX_SETTLE_TICKS=6  WAITX_LATCH_SETTLE_TICKS=3
FM6126_CLK_HIGH_TICKS=511  FM6126_CLK_LOW_TICKS=500  FM6126_REG_GAP_TICKS=50
ROWS_ABCDE=32 ROWS_ABCD=16 ROWS_ABC=8
PIXELS_PER_BYTE=2  LATCH_OVERLAP_COLS=3
' Plus the addr/pin bitmask + addr-value wall (rgb3bit:324-385 and DAT defaults 1024-1044),
' and the SETR/SETD self-modify encodings (%1000110_xx, %0000001_00) — see per-file table.
```

### isp_hub75_hwBufferAccess.spin2
```
PWM_FRAMES_3BIT=7 PWM_FRAMES_4BIT=15 PWM_FRAMES_5BIT=31
PWM_FRAMES_6BIT=63 PWM_FRAMES_7BIT=127 PWM_FRAMES_8BIT=255   ' = (1<<depth)-1
' line 544 chain-id/10 -> use existing hwEnum.HUB75_ADAPTER_STEP (=10)  [category A]
ENTR_ADDR_LONGS_COUNT=3
' debug-dump cosmetics (channelize under #9 instead?): DUMP_BYTES_PER_ROW=16, waits 35/85us
```

### isp_hub75_fonts.spin2
```
ASCII_FIRST_PRINTABLE=$20  ASCII_LAST_PRINTABLE=$7f   ' range bound repeated in 5 methods
FONT_5X7_WIDTH=5 FONT_5X7_HEIGHT=7 FONT_8X8A_WIDTH=7 FONT_8X8B_WIDTH=8 FONT_8X8B_HEIGHT=8
FONT_5X7_DCNDR_HEIGHT=9   (height geometry — category C)
```

### isp_hub75_display_bmp.spin2 (BMP = textbook protocol constants)
```
BMP_SIG_B=$42 BMP_SIG_M=$4d  BMP_HEADER_SIZE=54  BMP_DIB_HEADER_SIZE=40
BMP_BIT_COUNT_24=24  BMP_PLANES=1  BMP_COMPRESSION_NONE=0
BMP_BLUE_OFST=0 BMP_GREEN_OFST=1 BMP_RED_OFST=2   ' BGR byte order
' + the bytemove field-span byte counts (2/4/16/24) — name per field.
```

### isp_hub75_scrollingText.spin2 + isp_hub75_7seg.spin2 + isp_hub75_segment.spin2
```
' scrollingText dither codec (3 near-identical blocks):
DITH_BITS_PER_PIX=2  DITH_PIX_MASK=$c000  DITH_PIX_TOP_SHIFT=14  DITH_PIX_FULL=3  DITH_PIX_HALF=1
BLACK_COLOR=$000000  SPACE_CHAR=$20  DITHER_BRIGHTNESS_PCT=36   BLANK_ROW_PIX=1
' 7seg:
SEGMENTS_PER_DIGIT=7  MAX_DIGIT_VALUE=9   (loops "0 TO 6" -> SEGMENTS_PER_DIGIT-1)
' segment: lines 82-86 hard-code 3/10 where SEG_WIDTH/SEG_LENGTH already exist  [category A]
```

### Test utilities (anlyCheck, test_hub75_pin_identify)
```
anlyCheck: MAX_16PIN_VALUE=65535  MAX_CTL_VALUE=7  MAX_ADDR_VALUE=31  MAX_RGB_VALUE=7
           HOLD_DELAY_MS=1000  CYCLE_DELAY_MS=3
test_hub75_pin_identify: 15 power-of-two per-bit freq divisors (2..32768); LA_BITS_MASK=$F,
           HUB75_BITS_MASK=$FFFF, LA_BIT_COUNT=4 in main(). Cleaner as base+shift than 15 CONs.
```

---

## 3. Per-file findings (A/B/C; D summarized)

### isp_hub75_display.spin2 — A:2 B:14 C:16 D:~70
- **A:** 558, 589 `$000000` -> `color.CBLACK`.
- **B:** 154 `$AAAAAA` default text color; 316/318/320/322 font cell-padding `1`; 455 `<> 10` (see
  anomaly #2); 465/469/472 `$20` pad-space; 578 `36` dither brightness (anomaly #1); 584 `2`
  bits/px; 585 `$c000` mask + `14` shift; 588 `3` full / 589 `1` half dither codes; 714 `2` margins.
- **C:** 127/131 `-1` (NOT_FOUND/COG_FAILED), 264/297 home `0,0`, 341/342 round-half, 413/448/468
  `/2` centering, 711 `MIN_PANEL_COUNT=1`, 788 `>0` guard inconsistency, 896-941 coord-mode boolean
  flags, 1087 multi-panel-row `>1`.
- **D:** loop bases `0`, last-index `-1` idioms, clamp floors, Bresenham line/circle coefficients
  (982-1062, algorithm-inherent — kept D), booleans, hard-coded chain `0` (anomaly #3).

### isp_hub75_panel.spin2 — A:2 B:24 C:5 D:18
- **B (highlights):** 206-209/426 scan-geometry divisors 4/2/3; 218-269 & 442-495 RGB1/RGB2 bit
  values + masks duplicated across PASM init + RB/GB swap paths; 338/574 `#7` MSBIT_OF_BYTE;
  639/640 `48` dump-head bytes; 677-685 ASCII digit build ($30/$41/10/9, msg positions 3/4, $20);
  699/700 `32`/`$38` RGB2 check; 764 `1000000` ticks/usec.
- **A:** 325-329/561-569 `#0/#1/#2` color byte idx; 700 `$38` -> MASK_RGB2; 363-368 already-named regs.
- **C:** 86 DEBUG indices; 107 `waitms(1)` settle; 246 `$ffffffff` ALL_ONES; 285-301 `SHL #1` ×2.
- **D:** counter increments, loop bounds from vars, fills, commented-out dumps, test sentinels.

### isp_hub75_rgb3bit.spin2 — A:6 B:38 C:6 D:34
- **B (highlights):** 158/197-205 pin-span counts (ADDPINS 4/5/2/3); 230 `1000000` Hz/MHz;
  235-236 wait split `/2`; 278 `$ff00` driver-flags mask; **324-385 addr/pin bitmask + addr-value
  wall** (per-group × per-addr-mode, highest-priority cluster) incl scan counts 32/16/8;
  396/399 scan-4 col mult / latch overlap; 435 `16` free-cog (COGINIT); 534-535 FM6126 reg 11/12;
  557/584 `$0F` col-group mask; 585 `#9` reg12 bit; 558-603 WAITX timing (#6/#3/#511/#500/#50);
  668-678 SETR/SETD self-modify encodings; 816 `#$07` color mask; 819-825 pack shift `#3`/`#8`;
  876-898 BYTES_PER_LONG `#4` / BITS_PER_BYTE `#8`; 943 `#3` out-byte pos; 957-984 latch settle `#3`;
  1024-1044 DAT default masks/addr-values/scan-counts; 1102 `FIT 496`.
- **A:** 190-196 basePin+N -> MTX_LED offsets; 465/816 `7`/`$07` -> WHITE; 471 `<<2`/`<<1` ->
  RED_BIT/GREEN_BIT; 709-845 `#CMD_*` already named; 836 MAX_COG_BUFFER_SIZE_IN_LONGS already named.
- **C:** 250/762 `>>1` halving; 435 `+1` cog-id; 908 last-row `#1`; 948 `waitx #2` (dubious-flagged).
- **D:** PASM register names, `0`/`-1`, ×4 conversions, var operands, ORG/NOP.

### isp_hub75_screenUtils.spin2 — A:0 B:1 C:3 D:10
- **B:** 39 `6` degrees-per-column (`DEGREES_PER_COLUMN`).
- **C:** 81-83 RGB byte offsets 0/1/2.
- **D:** clamp floors, `-1`/`+1` index adjustments.

### isp_hub75_colorUtils.spin2 — A:0 B:46 C:1 D:11  (densest; collapses to §2 vocabulary)
- **B:** all channel masks/$ff/$ff00/$ff0000, shifts 8/16, 255 full-scale, 128/8/256 brightness,
  full HSV hue-wheel math (360/60/59/100, sextant boundaries 120/180/240/300), gamma idx 255.
- **C:** 281 DAT `256` FULL_BRIGHTNESS init.
- **D:** loop bounds, `-1` neighbor idx, permitted `0`, commented-out code.
- **DECISION HOTSPOT:** the HSV math is voluminous; naming every sextant literal is strict-correct
  but heavy. Option to name the core set (MAX_COLOR_VALUE/CHANNEL_MASK/shifts/PERCENT_SCALE/
  DEGREES_*) and express boundaries as `n*DEGREES_PER_HUE_SEGMENT`.

### isp_hub75_scrollingText.spin2 — A:0 B:14 C:9 D:11
- **B:** 164 `10` max-loop; 404/446 `$20` space; 478+ `$000000` (recurs, needs local BLACK_COLOR);
  515/581/644 `36` brightness (anomaly #1); dither codec 522/523/525/526 + repeats (587-593,658-664).
- **C:** 18/23 enum-base & line/char factors; 189/193/272/315/322/647/672 BLANK_ROW_PIX `1`.
- **D:** last-pixel `-1` idioms, single-bit `1<<n`, LONG<->byte rounding.

### isp_hub75_7seg.spin2 — A:0 B:7 C:6 D:8
- **B:** 25 `7` segments[]; 97/99 `9` digit clamp; 113/126/148/203 loop `0 TO 6` (SEGMENTS_PER_DIGIT-1).
- **C:** 149-177 segment-index case selectors; 153-177 layout insets/`*2`; 101 MIN_DIGIT.
- **D:** 30-39 bit-pattern DAT data table, last-index idioms, single-bit masks, `>=0` sentinel test.

### isp_hub75_segment.spin2 — A:4 B:0 C:6 D:5
- **A:** 82-86 hard-coded 3/10 -> use existing SEG_WIDTH/SEG_LENGTH (cheapest win in the sprint).
- **C:** pervasive taper-inset `0/1/2` line-geometry offsets (bounded by SEG_WIDTH); middle-seg toggle.
- **D:** last-index clamps.

### isp_hub75_display_bmp.spin2 — A:0 B:18 C:1 D:6  (all protocol constants — strong must-fix)
- **B:** $42/$4d signature; header sizes 54/40; field spans 2/4/16/24; 24-bit depth; planes=1;
  compression-none=0; BGR channel offsets 0/1/2.
- **C:** 198 DAT placeholder `10`.
- **D:** array idx 0/1, last-index idioms.

### isp_hub75_hwBufferAccess.spin2 — A:3 B:11 C:9 D:11
- **A:** 544 `/10` -> hwEnum.HUB75_ADAPTER_STEP; 570 default-frames -> PWM_FRAMES_4BIT.
- **B:** 558-568 PWM frame counts 7/15/31/63/127/255; 268/269 ENTR_ADDR_LONGS_COUNT `3`;
  847/864 dump waits 35/85us.
- **C:** 813-818 CHIP_TYPE_MASK $ff; 839-862 dump row geometry 16/15/7/10; 865 `2`ms.
- **D:** fills, clamp floors, last-index idioms, DAT >>2, commented-out.

### isp_hub75_fonts.spin2 — A:2 B:2 C:11 D:1
- **B:** $20/$7f ASCII printable-range bounds (5 methods).
- **A:** 99-143 `- $20` index base, 132 fallback-to-space -> ASCII_FIRST_PRINTABLE.
- **C:** 40-53 font width/height geometry (5/7/8/9); 123 top-skip `1`.
- **D:** null-init `0`.

### isp_hub75_anlyCheck.spin2 (test util, strict) — A:2 B:6 C:0 D:2
- **B:** 82 `65535` sweep max; 85/87 `1000`ms hold; 94 `7` ctl / 99 `31` addr / 104 `7` rgb; 111 `3`ms.
- **A:** 86 `65535` -> MAX_16PIN_VALUE; 105 `7` -> MAX_RGB_VALUE.
- **D:** all-low `0`, loop bases.

### test_hub75_pin_identify.spin2 (test util) — A:1 B:19 C:0 D:4
- **B:** 133-148 fifteen power-of-two per-bit freq divisors (2..32768); 163/164 $F/$FFFF/4 bit-split.
- **A:** 127 `15` -> HUB75 last-pin name.
- **D:** CON-def literals (out of scope), init `0`.

### Clean files
- isp_hub75_color.spin2 — only color-table CON values (out of scope).
- isp_hub75_hwPanelConfig.spin2 — only DISPn config CON knobs (intentional user config, out of scope).
- isp_hub75_hwEnums.spin2 — only enum/CON definitions (out of scope).

---

## 4. Open decisions for Stephen
1. **Aggressiveness on B:** name every semantic literal (full strict, ~200 sites) vs name the
   high-value clusters + algorithm-inherent exceptions left documented (Bresenham, possibly HSV math).
2. **Category C (readability):** include or defer? (~62 sites, lower value.)
3. **Anomalies (§1):** the `36`/"50%" comment fix; the `<> 10` debug edge-check (remove / channelize /
   name); these may route to follow-up #9 (DEBUG_MASK) rather than §4c.
4. **Demos:** audit demo `.spin2` files this wave (lenient tier) or leave for a later pass?
5. **PASM driver depth:** how deep into rgb3bit's bitmask wall + SETR self-modify encodings to name
   (these are the hardest-to-read but also the most cog-internal).
