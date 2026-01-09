# P2 HUB75 LED Matrix Driver Repair Plan
## Sprint: 2×2 Panel Support

**Created:** 2025-01-06
**Status:** In Progress

---

## Current Configuration

- **Demo:** Multi 2x2 Panel Driver (`demo_hub75_multi2x2panel.spin2`)
- **Panels:** 128×64 landscape-oriented LED panels
- **Arrangement:** 2×2 grid forming display panel
- **Chip:** ICN2037 (confirmed from datasheet)

---

## Phase 1: Observed Symptoms

### Symptom 1: Display Orientation Inverted
- **Observation:** Entire panel displays upside down
- **Impact:** Visual output is inverted from expected orientation
- **Status:** NEEDS FIX

### Symptom 2: Color Data Burst Pattern (Flashing)
- **Observation:** RGB data on HUB75 lines is emitted in bursts
- **Pattern:** 103ms bursts of activity followed by 103ms of no output
- **Impact:** Panel flashes instead of displaying stable image
- **Status:** NEEDS FIX

### Symptom 3: Clock Speed Incorrect
- **Observation:** HUB75 clock line running at 833 kHz
- **Expected:** 20 MHz (per ICN2037 datasheet: max 30 MHz)
- **Impact:** Data clocking is ~24x slower than expected
- **Status:** ✅ FIXED (2025-01-06)
- **Fix:** Implemented clock-frequency-independent timing with WAITX. Now confirmed 20 MHz on logic analyzer.

### Symptom 4: Latch and Output Enable Incorrect
- **Observation:** LAT (latch) and OE (output enable) lines not being driven correctly
- **Expected:**
  - OE: ACTIVE LOW (LOW=outputs ON)
  - LE/LAT: ACTIVE HIGH (pulse HIGH to latch)
- **Impact:** Data not being latched into shift registers properly; output not enabled correctly
- **Status:** ⚠️ PARTIAL FIX (2025-01-06)
- **Fix Applied:** Restored `drvh pinLedOE` before inter-subframe gap. LAT and OE now "look more normal" on logic analyzer. Further investigation needed.

### Symptom 5: Address Lines (Working Correctly)
- **Observation:** Address lines functioning properly
- **Details:**
  - A line: 20 kHz square wave, 50% duty cycle
  - B, C, D, E lines: Properly derived/squared off from A line
- **Status:** NO ACTION NEEDED

### Symptom 6: Potential Regression from Code Modifications
- **Observation:** Code has been modified from v3.0.2 release
- **Baseline:** Version 3.0.2 (last released version)
- **Known Working in v3.0.2:** 1×6 cube orientation (1D panel arrangements)
- **NOT Working in v3.0.2:** 2×2 panel arrangement (new functionality being added)
- **Risk:** Modifications may have broken existing behavior while adding 2D support
- **Status:** NEEDS AUDIT

---

## Panel Orientation System (Three-Tier Model)

### Tier 1: Wire Order
- Electrical sequence of panels in HUB75 daisy chain
- Panel 1 → Panel 2 → ... → Panel N
- Single HUB75 connector feeds all panels in series

### Tier 2: Physical LED Panel Rotation
- Each individual panel can be rotated independently (0°, 90°, 180°, 270°)
- Applied when mechanically assembling panels into display
- Accounts for cable routing and physical mounting constraints

### Tier 3: Display Rotation
- Final orientation of entire assembled display panel
- Rotates whole logical display
- Independent of individual panel wiring or rotation

### Coordinate Transform Pipeline
```
Application coordinates
        ↓
Display Rotation (whole display)
        ↓
Map to individual panel
        ↓
Panel Rotation (per-panel)
        ↓
Wire order (daisy chain position)
        ↓
Physical HUB75 output
```

---

## Phase 2: Research Tasks

### Task A: Panel Chip Technical Documentation [COMPLETED]
- **Goal:** Create Markdown README for ICN2037 chip
- **Deliverable:** `Docs/ICN2037/README.md`
- **Status:** COMPLETED 2025-01-06
- **Key Findings:**
  - ICN2037 max clock: 30 MHz (datasheet), 25 MHz (practical max from timing PDF)
  - OE is ACTIVE LOW
  - LE pulse must be 20ns+ HIGH
  - Data setup time: 5ns before CLK rising edge
  - 74HCT244 (adapter): +22ns max propagation delay
  - **Panel support chips (128×64):**
    - 74HC245TS: +18ns max (7ns typ) - data/CLK buffer
    - 74HC04D: +17ns max (7ns typ) - signal conditioning
    - RUC7258D: Row driver, NOT in CLK path
  - **Complete signal chain: 47ns worst-case, 27ns typical**
  - **Recommended CLK: 15-20 MHz** (accounting for full signal path)

### Task B: Code Audit Against v3.0.2
- **Goal:** Identify all modifications since v3.0.2 release
- **Approach:**
  1. Compare current code against v3.0.2
  2. Document all differences
  3. Evaluate each change for correctness and potential side effects
- **Intent:** Not to revert, but to focus debugging on suspicious changes
- **Status:** PENDING

### Task C: Research Approaches for Each Symptom
- **Status:** PENDING (awaiting code audit)

### Task D: Verify Control Signal Polarity (74HC04 Investigation)
- **Goal:** Determine if control signals (OE, LAT, CLK) are being inverted by the 74HC04 (U5) on the panel
- **Background:**
  - The 128×64 panel has a 74HC04 hex inverter (U5) in the signal path
  - Without a schematic, we don't know which signals route through it
  - If OE or LAT pass through the inverter, our driver polarity may need adjustment
- **Approach:**
  1. First, implement correct polarities per ICN2037 datasheet (OE=active LOW, LAT=active HIGH)
  2. If panel doesn't respond correctly, experiment with inverted control signals
  3. Document which polarity combination works for this panel type
- **Fallback:** If polarity issues persist, try all 4 combinations of OE/LAT inversion
- **Status:** PENDING (verify after basic timing fixes)

---

## Phase 3: Implementation Plan

### Critical Files to Examine

| File | Purpose | Priority |
|------|---------|----------|
| `isp_hub75_rgb3bit.spin2` | Low-level PASM2 driver, CLK/LAT/OE generation | HIGH |
| `isp_hub75_panel.spin2` | Screen buffer → PWM conversion | HIGH |
| `isp_hub75_hwPanelConfig.spin2` | Panel configuration constants | MEDIUM |
| `isp_hub75_screenUtils.spin2` | Coordinate transforms, orientation | MEDIUM |
| `isp_hub75_hwBufferAccess.spin2` | Buffer management | MEDIUM |

### Likely Root Causes by Symptom

| Symptom | Probable Location | Investigation Focus |
|---------|-------------------|---------------------|
| Clock 833 kHz | `isp_hub75_rgb3bit.spin2` | PASM2 clock generation loop timing |
| LAT/OE wrong | `isp_hub75_rgb3bit.spin2` | Signal polarity, timing sequence |
| 103ms bursts | `isp_hub75_panel.spin2` | PWM loop, buffer handoff |
| Upside down | `isp_hub75_screenUtils.spin2` | Coordinate mapping, rotation |

---

## Hardware Reference Summary

### ICN2037 Critical Specs (from technical reference)

| Parameter | Value | Source |
|-----------|-------|--------|
| Max CLK Frequency | 30 MHz | Datasheet p7 |
| Min CLK Pulse Width | 20 ns | Datasheet p8 |
| Min LE Pulse Width | 20 ns | Datasheet p8 |
| Min OE Pulse Width | 40-60 ns | Datasheet p8 |
| Data Setup Time | 5 ns | Datasheet p8 |
| Data Hold Time | 5 ns | Datasheet p8 |
| OE Polarity | **ACTIVE LOW** | Datasheet p3 |
| LE Polarity | **ACTIVE HIGH** | Datasheet p3 |

### Signal Chain Timing (Complete)

```
P2 (3.3V) → 74HCT244 → HUB75 Cable → 74HC245 → ICN2037
            (adapter)                 (panel)

WORST CASE:  22ns    +     2ns     +   18ns   + 5ns = 47ns
TYPICAL:     13ns    +     2ns     +    7ns   + 5ns = 27ns
```

**Maximum CLK Frequency (accounting for panel support chips):**
| Scenario | One-Way Delay | Max CLK |
|----------|---------------|---------|
| Worst-case | 47 ns | 10.6 MHz |
| Typical | 27 ns | 18.5 MHz |
| Conservative | 35 ns | 14.3 MHz |

---

## Progress Log

| Date | Task | Status |
|------|------|--------|
| 2025-01-06 | Document symptoms | COMPLETE |
| 2025-01-06 | Create ICN2037 technical reference | COMPLETE |
| 2025-01-06 | Research 74HCT244 timing | COMPLETE |
| 2025-01-06 | Research panel support chip timing (74HC245, 74HC04, RUC7258D) | COMPLETE |
| 2025-01-06 | Complete signal chain timing analysis | COMPLETE |
| 2025-01-06 | Code audit: isp_hub75_rgb3bit.spin2 | COMPLETE |
| 2025-01-06 | Code audit: isp_hub75_panel.spin2 | COMPLETE |
| 2025-01-06 | Code audit: isp_hub75_screenUtils.spin2 | COMPLETE |
| 2025-01-06 | Code audit: isp_hub75_hwBufferAccess.spin2 | COMPLETE |
| 2025-01-06 | Code audit: isp_hub75_hwPanelConfig.spin2 | COMPLETE |
| 2025-01-06 | Code audit: Synthesis and change correlation | COMPLETE |
| 2025-01-06 | Symptom research: Clock speed (833 kHz) | COMPLETE |
| 2025-01-06 | Symptom research: LAT/OE timing | COMPLETE |
| 2025-01-06 | Symptom research: Burst pattern (103ms) | COMPLETE |
| 2025-01-06 | Symptom research: Display orientation | COMPLETE |
| 2025-01-06 | Symptom research: Control signal polarity (74HC04) | COMPLETE |
| 2025-01-06 | Fix clock speed (20 MHz achieved) | ✅ COMPLETE |
| 2025-01-06 | Restore OE disable before subframe gap | ✅ COMPLETE |
| - | Fix LAT/OE timing (further investigation) | IN PROGRESS |
| - | Fix display orientation | PENDING |
| - | Fix burst pattern (flashing) | PENDING |
| - | Fix visual symptoms (see Phase 4) | PENDING |

---

## Notes

- Address line behavior (working correctly at 20 kHz) suggests the underlying timing infrastructure exists
- The problem is specifically in: data output rate, clock generation, control signal sequencing
- Symptoms could be: regressions breaking 1×N support, issues in new 2D support, or both
- Technical reference created: `Docs/ICN2037/README.md`

---

## Phase 4: Visual Symptoms (Post-Timing Fix)

**Observed:** 2025-01-06 (after clock fix to 20 MHz)

With correct 20 MHz clock timing now in place, the following visual anomalies are observed on the display. These are separate issues that may require different fixes.

### Visual Symptom A: Display Still Flashing
- **Observation:** Display continues to flash (from original Symptom 2)
- **Status:** NEEDS FIX
- **Likely Cause:** See Symptom H below - MSB frame is black

### Visual Symptom H: MSB PWM Frame (2^7) is Black
- **Observation:**
  - LA instrumentation (pinLAXT_10) triggers at start of each PWM frame transition
  - Frame 0 (2^7 weight = 128 repetitions): RGB1 and RGB2 are BLACK
  - Frames 1-7 (2^6 through 2^0): RGB1 and RGB2 have full color data
- **Verification Method:** LA trigger on pinLAXT_10 confirms frame boundaries; RGB data observed during each frame period
- **Impact:**
  - 2^7 frame accounts for 50% of display time (128 out of 255 time units)
  - Display alternates: BLACK (~100ms) → COLOR (~100ms) → BLACK → COLOR...
  - This is the **primary cause of visible flashing** at ~5 Hz, 50% duty cycle
- **Status:** NEEDS FIX - CRITICAL
- **Likely Cause:**
  - PWM buffer generation not populating MSB bit-plane
  - Or frame indexing error (frame 0 pointing to wrong/empty buffer)
  - Or bit extraction logic inverted (MSB extracted incorrectly)

### Visual Symptom B: Panel Position/Label Mismatch (Lower Half)
- **Observation:**
  - Lower-left panel (wire chain position 0): Shows GREEN, labeled as "1" instead of "0"
  - Lower-right panel (wire chain position 1): Shows BLUE, labeled as "0" instead of "1"
- **Expected:** Wire position 0 should be labeled "0", position 1 should be labeled "1"
- **Status:** NEEDS FIX
- **Likely Cause:** Wire order table incorrect, or display-to-wire mapping swapped for lower panels

### Visual Symptom C: Panel Colors (Upper Half Correct)
- **Observation:**
  - Upper-left panel: Shows RED, labeled as "2" (CORRECT)
  - Upper-right panel: Shows MAGENTA, labeled as "3" (CORRECT)
- **Status:** NO ACTION NEEDED (confirms upper panels wire order is correct)

### Visual Symptom D: Yellow Squares in Wrong Corner
- **Observation:** Yellow squares appear in BOTTOM-RIGHT corner of each panel
- **Expected:** Based on demo code, squares should likely be in a different position
- **Status:** NEEDS FIX
- **Likely Cause:** Panel rotation issue, coordinate transform error

### Visual Symptom E: Arrows Pointing Wrong Direction
- **Observation:** All arrows on panels are pointing DOWN
- **Expected:** Arrows should be pointing UP
- **Status:** NEEDS FIX
- **Likely Cause:** Y-axis inversion, panel rotation 180° off

### Visual Symptom F: Center Square Split Incorrectly
- **Observation:**
  - A square intended to be centered across all 4 panels is split wrong
  - Half appears at TOP CENTER of the two top panels
  - Other half appears at BOTTOM-LEFT of green panel and BOTTOM-RIGHT of blue panel
- **Expected:** Square should be centered at the intersection of all 4 panels
- **Status:** NEEDS FIX
- **Likely Cause:** Display-wide coordinate mapping error, possibly Y-axis flip combined with panel ordering issue

### Visual Symptom G: Half-Moon Circle (Should Be Full Circle)
- **Observation:** Only a half-moon arc visible at TOP of red (upper-left) panel
- **Expected:** Full circle centered around all 4 panels (at display center)
- **Status:** NEEDS FIX
- **Likely Cause:** Same coordinate mapping issue as Symptom F - display center is being mapped incorrectly

### Timing Measurements (LA Verified)

**Clock Timing:**
| Parameter | Measured | Expected | Status |
|-----------|----------|----------|--------|
| Clock frequency | 20.83 MHz | 20 MHz | ✅ GOOD |
| Clock duty cycle | 66% | 50-66% | ✅ GOOD |

**Post-Row Latch Sequence:**
| Phase | Duration | Notes |
|-------|----------|-------|
| OE HIGH (with enclosed LATCH) | 128 ns | Outputs disabled |
| LATCH HIGH pulse | 48 ns | Data latched |
| OE LOW | 32 ns | Brief enable |
| OE HIGH | 160 ns | Outputs disabled |
| Then OE LOW → next row | - | Outputs enabled for display |

**Frame Timing:**
| Parameter | Measured | Calculated | Status |
|-----------|----------|------------|--------|
| Single PWM frame scan | 806 µs | ~800 µs | ✅ MATCH |
| Full 8-bit PWM frame set | 205 ms | 205.5 ms | ✅ MATCH |
| Effective refresh rate | ~4.9 Hz | - | ⚠️ Causes visible flicker |

**PWM Frame Weighting Verified:**
- LA trigger (pinLAXT_10) confirms frame transitions
- Binary weighting: 128, 64, 32, 16, 8, 4, 2, 1 repetitions per frame
- Total: 255 scans per full frame set

### Analysis Summary

| Symptom | Category | Root Cause Hypothesis |
|---------|----------|----------------------|
| A (Flashing) | PWM Data | MSB frame (2^7) is black (see H) |
| B (Labels swapped) | Wire Order | Wire table for lower panels |
| D (Squares wrong corner) | Orientation | Panel rotation or Y-flip |
| E (Arrows down) | Orientation | Y-axis inverted |
| F (Split square) | Coordinates | Display-wide Y mapping + panel order |
| G (Half circle) | Coordinates | Same as F |
| H (MSB black) | PWM Data | Buffer gen or frame indexing |

**Key Insight:** Symptoms D, E, F, and G all suggest a **Y-axis inversion** issue at the display level. The lower panels (B) having swapped labels suggests an additional **wire order issue** specifically for the bottom row of panels.

**Critical Issue:** Symptom H (MSB frame black) is causing 50% of display time to be black, which is the primary cause of visible flashing.

---

## Code Audit: isp_hub75_rgb3bit.spin2

**Audit Date:** 2025-01-06
**Baseline:** v3.0.2
**Status:** COMPLETED

### Summary

The PASM2 driver has undergone significant modifications to support 2D panel grids and additional pin groups. Most changes are additive (new functionality), but several changes warrant investigation as potential sources of the observed symptoms.

### Change Categories

| Category | Description | Count |
|----------|-------------|-------|
| (a) Improvement | Code cleanup, better naming, documentation | 8 |
| (b) Bug Fix | Corrections to existing behavior | 0 |
| (c) 2D Support | New functionality for panel grids | 12 |
| (d) Potentially Detrimental | Changes that could cause regressions | 3 |
| (e) Unknown Purpose | Uncertain changes needing investigation | 1 |

---

### CRITICAL CHANGES (Investigate First)

#### 1. Removed OE Disable Before Inter-Subframe Gap
**Location:** Line ~1123 (wrLatchAtEnd routine)
**Category:** (d) Potentially Detrimental

```pasm
' REMOVED:
                    drvh    pinLedOE    ' <-- THIS LINE WAS DELETED
                    '
                    ' ---  inter-subframe gap  ---
```

**Impact:** The OE (Output Enable) signal is ACTIVE LOW - `drvh` disables the LED outputs. Removing this instruction means LEDs remain illuminated during subframe transitions.

**Possible Symptoms:**
- Incorrect brightness (LEDs on when they should be off)
- Ghosting between frames
- Could contribute to the 103ms burst pattern if frame timing is affected

**Verdict:** ⚠️ **HIGH PRIORITY** - This is a direct change to OE control which is one of the observed symptoms.

---

#### 2. New Pin Conditioning in PASM Driver
**Location:** Lines 774-788 (drive_matrix entry)
**Category:** (e) Unknown Purpose / (d) Potentially Detrimental

```pasm
' ADDED:
                    wrpin   ##P_LOW_1MA, pinGrpLAXT
                    drvl    pinGrpLAXT

                    wrpin   ##P_LOW_1MA, maskAddr
                    fltl   maskAddr             ' reset any smart pin mode
                    fltl   maskRgb12            ' reset any smart pin mode
```

**Impact:** These instructions configure pin drive strength and reset smart pin modes for address and RGB data lines.

**Possible Symptoms:**
- `P_LOW_1MA` sets very low drive strength (1mA sink current)
- `fltl` floats the pins (high-impedance state) then resets smart pin mode
- **Could affect signal integrity and timing** if these pins need stronger drive

**Questions:**
1. Are maskAddr/maskRgb12 the correct pins to condition? (They are masks, not pin numbers)
2. Does `fltl` on output pins cause momentary high-Z that could glitch signals?

**Verdict:** ⚠️ **INVESTIGATE** - May affect signal quality but purpose unclear

---

#### 3. Logic Analyzer Pins Now Fixed at P8-P11
**Location:** Lines 195-198 (start method)
**Category:** (d) Potentially Detrimental

```spin2
' BEFORE (relative to adapter):
    pnlLedLA_08     := basePin + 8 + 0   ' Could be P8, P24, P40, or P56
    pnlLedLA_09     := basePin + 8 + 1
    pnlLedLA_10     := basePin + 8 + 2
    pnlLedLA_11     := basePin + 8 + 3

' AFTER (fixed):
    pnlLedLA_08     := MTX_LA_XT_P08     ' Always P8
    pnlLedLA_09     := MTX_LA_XT_P09     ' Always P9
    pnlLedLA_10     := MTX_LA_XT_P10     ' Always P10
    pnlLedLA_11     := MTX_LA_XT_P11     ' Always P11
```

**Impact:** LA debug pins are now always P8-P11 regardless of which HUB75 adapter (pin group) is in use.

**Possible Symptoms:**
- If using P0-P15 adapter: LA pins P8-P11 CONFLICT with HUB75 data pins (R1, G1, B1, B2)!
- Could cause data corruption on those specific color channels

**Verdict:** ⚠️ **CONFLICT RISK** - If DISP0 uses PINS_P0_P15, this is broken. Check current config.

---

### SIGNIFICANT CHANGES (2D Support - Core Logic)

#### 4. pwmRowSizeInLongs Calculation Changed
**Location:** Lines 147-156 (start method)
**Category:** (c) 2D Support

```spin2
' BEFORE:
    pwmRowSizeInLongs := (hub75Bffrs.maxDisplayColumns(chainIndex) + 3) / 4

' AFTER:
    maxDisplayRows, maxDisplayColumns := hub75Bffrs.displaySizeInPixels(chainIndex)
    maxPanelRows, maxPanelColumns := hub75Bffrs.panelSizeInPixels(chainIndex)
    panelCt := hub75Bffrs.maxPanels(chainIndex)
    maxChainColumns := maxPanelColumns * panelCt
    ' 2 pixels per byte, 4 bytes per long
    pwmRowSizeInLongs := ((maxChainColumns / 2) + 3) / 4
```

**Analysis:**
- Old: Based on display width (logical pixels)
- New: Based on chain width (physical pixels = panels × panel_width)
- The `/2` accounts for 2 pixels per byte (6 bits color data per byte)

**For 2×2 grid of 128×64 panels:**
| Variable | Old Value | New Value |
|----------|-----------|-----------|
| Display width | 256 | 256 |
| Chain width | N/A | 512 |
| pwmRowSizeInLongs | (256+3)/4 = 64 | ((512/2)+3)/4 = 64 |

**Verdict:** ✅ Mathematically equivalent for this case, but semantically different concept.

---

#### 5. colCtrMax Now Uses Chain Width
**Location:** Lines 384-391 (start method)
**Category:** (c) 2D Support - **CRITICAL FOR TIMING**

```spin2
' BEFORE:
    ' set width of one row
    colCtrMax := hub75Bffrs.maxDisplayColumns(chainIndex)

' AFTER:
    ' set width of one row (this is the entire chain, not the display width)
    colCtrMax := maxChainColumns
```

**Impact:** This value controls how many clock pulses are sent per row in the PASM driver.

**For 2×2 grid:**
| Variable | Old Value | New Value | Difference |
|----------|-----------|-----------|------------|
| colCtrMax | 256 | 512 | 2× more clocks per row |

**Implications:**
- Twice as many clock pulses per row → row takes 2× longer
- **Total frame time doubles** if row count stays the same
- Could explain the lower-than-expected clock frequency (833 kHz)
- Could contribute to the 103ms burst timing

**Verdict:** ⚠️ **TIMING IMPACT** - This is correct for the physical chain but changes frame timing significantly.

---

#### 6. New Pin Group Support (P8-P23, P40-P55)
**Location:** Lines 36-40 (CON), 292-306 (start method), 335-356 (mask config), 811-812 (PASM)
**Category:** (c) 2D Support

```spin2
' New pin groups:
    PIN_GROUP_P8_P23 = hwEnum.PINS_P8_P23
    PIN_GROUP_P40_P55 = hwEnum.PINS_P40_P55

' New bSetMidPins handling in case statement and mask configuration
```

**Note:** The mask configuration for bSetMidPins includes concerning comment:
```spin2
    modeDatRotLeft := TRUE    ' i've no IDEA but leaving it TRUE for now
```

**Verdict:** ⚠️ **UNCERTAIN CODE** - The author expressed uncertainty about this setting.

---

#### 7. New VAR Declarations
**Location:** Lines 94-98
**Category:** (c) 2D Support

```spin2
' ADDED:
    long    maxChainColumns
    long    maxDisplayColumns
    long    maxDisplayRows
    long    maxPanelColumns
    long    maxPanelRows
```

**Verdict:** ✅ Clean addition - separates display concept from physical chain concept.

---

### MINOR CHANGES (Low Risk)

#### 8. Method Renaming
**Category:** (a) Improvement

| Old Name | New Name |
|----------|----------|
| fillScreenNoPWM | cmdFillScreenNoPWM |
| clearPanel | cmdClearPanel |
| writeBuffer | cmdWriteBuffer |
| writePwmBuffer | cmdWritePwmBuffer |

**Verdict:** ✅ Better naming convention, no functional change.

---

#### 9. Debug Output Enhancements
**Location:** Various
**Category:** (a) Improvement

- More informative debug messages
- Added chain columns to startup debug
- Combined udec() calls

**Verdict:** ✅ Debug-only, no runtime impact.

---

#### 10. FM6126A Init Uses Chain Width
**Location:** Lines 499, 611, 617-625, 639, 674
**Category:** (c) 2D Support

```spin2
' Changed from:
    hub75Bffrs.maxDisplayColumns(chainIndex)
' To:
    maxChainColumns
```

**Verdict:** ✅ Consistent with other changes - uses physical chain width for initialization.

---

#### 11. PASM Comment Improvements
**Location:** Lines 759, 893-913
**Category:** (a) Improvement

- Added column separator comment
- Clarified "SAME PWM Frame" vs "NEW PWM Frame" comments

**Verdict:** ✅ Documentation only.

---

#### 12. Formatting/Whitespace Changes
**Location:** Throughout (Lines 312-378, 1050-1128)
**Category:** (a) Cleanup

- Aligned comments
- Removed trailing whitespace
- Minor indentation fixes

**Verdict:** ✅ No functional impact.

---

### Audit Conclusions

#### Changes Likely Contributing to Symptoms

| Symptom | Likely Cause(s) | Priority |
|---------|-----------------|----------|
| 833 kHz Clock | colCtrMax doubled → 2× more clocks per frame | HIGH |
| 103ms Bursts | Changed frame timing from colCtrMax change | MEDIUM |
| LAT/OE Wrong | Removed `drvh pinLedOE` before subframe gap | HIGH |
| Upside Down | Not in this file - check screenUtils | N/A |

#### Recommended Investigation Order

1. **Restore `drvh pinLedOE`** before inter-subframe gap (Line ~1123)
2. **Verify LA pin configuration** - check if DISP0 uses P0-P15 (conflict with P8-P11 LA pins)
3. **Review pin conditioning** - `wrpin P_LOW_1MA` and `fltl` effects on signal integrity
4. **Verify colCtrMax** is correct for the hardware configuration (chain width vs display width)

#### Changes That Are Correct (Keep)

1. New VAR declarations (maxChainColumns, etc.)
2. New pin group support (P8-P23, P40-P55)
3. Method renaming (cmd prefix)
4. Debug enhancements
5. FM6126A init using chain width

---

### Next Audit File

Continue with **isp_hub75_panel.spin2** to investigate the 103ms burst pattern (PWM loop and buffer handoff).

---

## Code Audit: isp_hub75_panel.spin2

**Audit Date:** 2025-01-06
**Baseline:** v3.0.2
**Status:** COMPLETED

### Summary

The panel driver has undergone **major restructuring** for 2D panel grid support. The most significant change is a **complete rewrite** of the `convertScreen2PWM()` routine - the core algorithm that converts 24-bit screen buffers to PWM frame data.

### Change Categories

| Category | Description | Count |
|----------|-------------|-------|
| (a) Improvement | Caching, optimization, cleanup | 4 |
| (b) Bug Fix | None identified | 0 |
| (c) 2D Support | New grid/wire handling | 6 |
| (d) Potentially Detrimental | Algorithm changes | 2 |
| (e) Unknown Purpose | None | 0 |

---

### CRITICAL CHANGES (Investigate First)

#### 1. Complete Rewrite of convertScreen2PWM()
**Location:** Lines 381-596
**Category:** (c) 2D Support + (d) Potentially Detrimental

**This is a FUNDAMENTAL rewrite of the core PWM conversion algorithm.**

##### Before (v3.0.2):
```spin2
' Simple backward pixel iteration
lPixelCtr := (lPhyRows * lPysColumns) / 2
p24bitColorTop := l24bitColorTop + p24bitScreen  ' end of top half
p24bitColorBot := p24bitColorTop + ...            ' end of bottom half

nextPixel:
    rdlong colorValue24bit, p24bitColorTop
    ' ... process top/bottom pixel pair ...
    sub p24bitColorTop, lDisplayBytesPerColor
    sub p24bitColorBot, lDisplayBytesPerColor
    djnz lPixelCtr, #nextPixel
```

##### After (current):
```spin2
' Nested row × column iteration with per-pixel offset calculation
nextScanRow:
    nextChainCol:
        ' Calculate wire panel via repeated division (8× CMPSUB)
        cmpsub tempDiv, lPanelCols wc
        if_c add wirePanel, #1
        ' ... 7 more CMPSUB iterations ...

        ' Calculate base offset: wirePanel * panelPixels * bytesPerColor
        mul wirePanelBase, lPanelPixels
        mul wirePanelBase, lDisplayBytesPerColor

        ' Calculate per-pixel offsets
        mul topPixelOffset, lPanelCols
        mul topPixelOffset, lDisplayBytesPerColor
        ' ... similar for botPixelOffset ...

        rdlong colorValue24bit, pTopPixelAddr
        djnz chainColCtr, #nextChainCol
    djnz scanRowCtr, #nextScanRow
```

##### Key Algorithmic Differences:

| Aspect | Old (v3.0.2) | New (Current) |
|--------|--------------|---------------|
| Traversal | Backward from end | Forward row×column |
| Pointer management | Simple decrement | Per-pixel offset calculation |
| Division per pixel | 0 | 8 CMPSUB operations |
| Multiplication per pixel | 0 | 4+ MUL operations |
| Screen buffer assumption | Linear | Wire-panel-major order |

##### Performance Impact Estimate:
- Extra overhead per pixel: ~40-60 cycles
- For 16,384 pixels (2×2 grid): +655K to +983K cycles
- At 300 MHz: **+2.2ms to +3.3ms per frame conversion**

**Verdict:** ⚠️ **MAJOR ALGORITHM CHANGE** - While the new algorithm is necessary for 2D grids, the overhead is substantial. However, this alone doesn't explain the 103ms burst pattern.

---

#### 2. Wire-Panel-Major Screen Buffer Layout Assumption
**Location:** Lines 390-398 (comments)
**Category:** (c) 2D Support

```spin2
' Screen buffer is in wire-panel-major order:
'   Wire panel 0: bytes 0 to (panelPixels * bytesPerColor - 1)
'   Wire panel 1: bytes (panelPixels * bytesPerColor) to (2 * panelPixels * bytesPerColor - 1)
'   etc.
' We read directly by wire position - no coordinate mapping needed!
```

**Critical Question:** Is the screen buffer actually organized this way?

The comment says "no coordinate mapping needed" because the screen buffer is assumed to be in wire order. But this means:
- The **display-side coordinate transforms** must write to the buffer in wire-panel-major order
- If `isp_hub75_screenUtils.spin2` doesn't organize data this way, the display will be scrambled

**Verdict:** ⚠️ **ARCHITECTURE ASSUMPTION** - Must verify screenUtils writes in wire-panel-major order.

---

### SIGNIFICANT CHANGES (2D Support)

#### 3. New Instance Variables
**Location:** Lines 30-41
**Category:** (c) 2D Support / (a) Improvement

```spin2
' ADDED:
    LONG    maxChainRows
    LONG    maxChainColumns
    LONG    nPanelRows
    LONG    nPanelColumns
    LONG    nPanelsPerRow
    LONG    nPanelsPerColumn
    LONG    nDisplayRows
    LONG    nDisplayColumns
    LONG    nColorDepth
    LONG    nBytesPerColor
    LONG    nPwmFrameSizeInBytes
```

**Purpose:** Cache values from `hub75Bffrs` to avoid repeated method calls during PWM conversion.

**Verdict:** ✅ Good optimization - reduces overhead in tight loops.

---

#### 4. Wire-to-Display Panel Lookup Table
**Location:** Lines 75-77 (start method), Line 662 (VAR)
**Category:** (c) 2D Support

```spin2
VAR:
    LONG    wireToDisplayPanel[16]      ' Inverse lookup: wire position -> display panel index

start():
    repeat wireIdx from 0 to panelCt - 1
        wireToDisplayPanel[wireIdx] := hub75Bffrs.displayPanelForWire(chainIndex, wireIdx)
```

**Note:** This lookup table is built but the main `convertScreen2PWM` doesn't use it - it reads directly by wire position assuming the screen buffer is already in wire order.

**Verdict:** ✅ Useful for 2D grid support, though unused in the main conversion routine.

---

#### 5. Enhanced Debug Output
**Location:** Lines 78-80, 86-87
**Category:** (a) Improvement

```spin2
debug("- PNL: Grid ", udec_(nPanelsPerRow), "x", udec_(nPanelsPerColumn), " panels")
debug("- PNL: Wire order: W0->D", udec_(wireToDisplayPanel[0]), ...)
debug("- PNL: PHYScols=", udec_long_(maxChainColumns), " PHYSrows=", udec_long_(maxChainRows))
```

**Verdict:** ✅ Helpful for debugging panel configuration.

---

#### 6. Runtime Measurement Enabled
**Location:** Line 700 (markEnd)
**Category:** (d) Potentially Detrimental

```spin2
' BEFORE (commented out):
    'debug("- runtime ", zstr_(message), ": ", udec_long(elapsed), " uS")

' AFTER (active):
    debug("- runtime ", zstr_(message), ": ", udec_long(elapsed), " uS")
```

**Impact:** Debug output adds latency during frame conversion. While small, in a tight refresh loop this could accumulate.

**Verdict:** ⚠️ Consider disabling for production - adds serial debug overhead.

---

### MINOR CHANGES (Low Risk)

#### 7. Method Name Updates
**Category:** (a) Improvement

```spin2
matrix.fillScreenNoPWM  →  matrix.cmdFillScreenNoPWM
matrix.writePwmBuffer   →  matrix.cmdWritePwmBuffer
```

**Verdict:** ✅ Matches rgb3bit method renaming.

---

#### 8. Cached Value Usage
**Location:** Various (convertScreen2PWM_14, dumpFrameAddrs, clearPwmFrameBuffer, etc.)
**Category:** (a) Improvement

```spin2
' BEFORE:
    hub75Bffrs.maxDisplayRows(chainIndex)
    hub75Bffrs.colorDepth(chainIndex)

' AFTER:
    maxChainRows
    nColorDepth
```

**Verdict:** ✅ Reduces method call overhead.

---

#### 9. setPanelColorBitsForRC Updates
**Location:** Lines 665-677
**Category:** (c) 2D Support

```spin2
' Changed byte index calculation:
    panelIndex := hub75Bffrs.indexToPanel(chainIndex, nBffrR, nBffrC)
    columnOffsetToPanel := panelIndex * nPanelColumns
    byteIdx := (nBffrR * columnOffsetToPanel) + nBffrC
```

**Note:** This function appears to be unused based on comment "UNUSED FOR NOW".

**Verdict:** ✅ Future-proofing for 2D support.

---

### Audit Conclusions

#### Does This File Explain the 103ms Burst Pattern?

**No, not directly.** The changes in this file affect:
- PWM conversion time (increased by ~2-3ms)
- Debug output overhead (minor)
- Buffer layout assumptions

The 103ms (~10Hz) burst pattern suggests something at a much higher level:
- Perhaps the demo application's main loop
- Or a double-buffering handoff issue
- Or interaction between Spin2 scheduling and PASM timing

#### Changes Likely Contributing to Symptoms

| Symptom | Contribution from This File |
|---------|----------------------------|
| 833 kHz Clock | None (clock is in rgb3bit) |
| 103ms Bursts | Unlikely source - conversion overhead is only ~3ms |
| LAT/OE Wrong | None (signals are in rgb3bit) |
| Upside Down | **Possibly** - screen buffer layout assumption affects output order |

#### Recommended Investigation Order

1. **Verify screen buffer layout** - Is it actually wire-panel-major as assumed?
2. **Check screenUtils** - How does it write coordinates to the buffer?
3. **Disable debug output** - Remove `markEnd()` debug call in production

#### Key Insight: Pixel Order Changed

The old algorithm processed pixels **backward** (from end to start), the new processes **forward** (row-by-row, column-by-column). Combined with the buffer layout assumption change, this could affect:
- How pixels map to PWM bytes
- The order in which data appears on the chain
- Potentially the orientation (upside down symptom)

---

### Next Audit File

Continue with **isp_hub75_screenUtils.spin2** to investigate coordinate transforms and the "upside down" symptom.

---

## Code Audit: isp_hub75_screenUtils.spin2

**Audit Date:** 2025-01-06
**Baseline:** v3.0.2
**Status:** COMPLETED

### Summary

This file has been **significantly restructured** to support 2D panel grids. The core pixel-placement logic has been abstracted - coordinate mapping is now delegated to `hub75Bffrs` methods instead of being calculated inline.

### Change Categories

| Category | Description | Count |
|----------|-------------|-------|
| (a) Improvement | Cleaner abstraction | 1 |
| (c) 2D Support | Panel-aware coordinate mapping | 3 |
| (d) Potentially Detrimental | Orientation-related | 1 |

---

### CRITICAL CHANGES (Investigate First)

#### 1. Coordinate Mapping Delegated to hub75Bffrs
**Location:** Lines 62-67
**Category:** (c) 2D Support + (d) Potentially Detrimental

##### Before (v3.0.2):
```spin2
' Each rotation case calculated colorOffset directly:
case hub75Bffrs.panelRotation(nChainIdx)
    hub75Bffrs.ROT_LEFT_90:
        pScreen := rowIndex
        rowIndex := columnIndex
        columnIndex := pScreen
        rowIndex := (hub75Bffrs.maxDisplayColumns(nChainIdx) - 1) - rowIndex
        colorOffset := ((rowIndex * hub75Bffrs.maxDisplayRows(nChainIdx)) + columnIndex) * hub75Bffrs.bytesPerColor(nChainIdx)
    ' ... similar for other cases
```

##### After (current):
```spin2
' Rotation only transforms coordinates - offset calculated elsewhere:
case hub75Bffrs.panelRotation(nChainIdx)
    hub75Bffrs.ROT_LEFT_90:
        tempIdx := rowIndex
        rowIndex := columnIndex
        columnIndex := tempIdx
        rowIndex := (maxColumns - 1) - rowIndex
    ' ... similar for other cases (NO colorOffset calculation)

' NEW: Delegate to panel-aware functions
nPanelIndex, localRow, localCol := hub75Bffrs.displayToPanelCoords(nChainIdx, rowIndex, columnIndex)
colorOffset := hub75Bffrs.panelPixelOffset(nChainIdx, nPanelIndex, localRow, localCol)
```

##### Architecture Change:

```
OLD FLOW:
  Display (row,col) → Apply Rotation → Calculate Linear Offset → Write Pixel

NEW FLOW:
  Display (row,col) → Apply Rotation → displayToPanelCoords() → panelPixelOffset() → Write Pixel
                                              ↓                        ↓
                                        [hub75Bffrs]            [hub75Bffrs]
```

**Critical Implication:** The "upside down" symptom is now likely caused by logic in `hub75Bffrs`, not in this file.

**Verdict:** ⚠️ **ARCHITECTURE SHIFT** - Must audit `displayToPanelCoords()` and `panelPixelOffset()` in hwBufferAccess.

---

#### 2. Rotation Cases No Longer Calculate Offset
**Location:** Lines 47-60
**Category:** (c) 2D Support

The rotation case blocks now ONLY transform coordinates. The offset calculation was removed because it's now handled by `panelPixelOffset()`.

**Key Question:** Does `panelPixelOffset()` correctly account for rotation? Or is rotation being applied twice/incorrectly?

**Possible Issue Scenarios:**
1. Rotation applied here, then `displayToPanelCoords` applies it again → wrong position
2. Rotation applied here, but `panelPixelOffset` assumes no rotation → wrong position
3. The order of (row, column) in the function calls doesn't match expectations

**Verdict:** ⚠️ Need to verify the contract between screenUtils and hwBufferAccess.

---

### MINOR CHANGES (Low Risk)

#### 3. Size Retrieval Consolidated
**Location:** Line 42
**Category:** (a) Improvement

```spin2
' OLD:
rowIndex := 0 #> row <# hub75Bffrs.maxDisplayRows(nChainIdx) - 1
columnIndex := 0 #> column <# hub75Bffrs.maxDisplayColumns(nChainIdx) - 1

' NEW:
maxRows, maxColumns := hub75Bffrs.displaySizeInPixels(nChainIdx)
rowIndex := 0 #> row <# maxRows - 1
columnIndex := 0 #> column <# maxColumns - 1
```

**Verdict:** ✅ Cleaner - single method call to get both dimensions.

---

#### 4. Color Correction Moved to colorUtils
**Location:** Lines 71-73
**Category:** (a) Improvement

```spin2
' OLD:
byte[pColor][0] := hub75Bffrs.correctedSingleColor(...)

' NEW:
byte[pColor][0] := colorUtils.correctedSingleColor(...)
```

**Verdict:** ✅ Better separation of concerns.

---

#### 5. Updated Date Anomaly
**Location:** Line 10
**Category:** (e) Anomaly

```spin2
' OLD:
''   Updated.... 26 Mar 2024

' NEW:
''   Updated.... 5 Nov 2022
```

**Note:** The date went BACKWARD. This suggests the change might have been from a different branch or the date wasn't updated correctly.

**Verdict:** 📝 Minor metadata issue.

---

### Audit Conclusions

#### Does This File Cause the "Upside Down" Symptom?

**Not directly, but it reveals where to look.** The coordinate mapping logic has been moved to:
- `hub75Bffrs.displayToPanelCoords()` - converts display coords to panel/local coords
- `hub75Bffrs.panelPixelOffset()` - converts panel/local coords to buffer offset

These functions in `hwBufferAccess` are now the primary suspects for orientation issues.

#### Possible Orientation Bug Locations

| Location | What Could Go Wrong |
|----------|---------------------|
| `displayToPanelCoords()` | Y-axis inverted, panel ordering wrong |
| `panelPixelOffset()` | Row offset calculation inverted |
| Wire order enumeration | Panels ordered bottom-to-top instead of top-to-bottom |
| Rotation constant | Wrong rotation value for this configuration |

#### Transform Pipeline Analysis

For a 2×2 grid, a pixel at display (row=0, col=0) should end up at:
1. After rotation: depends on rotation setting (if ROT_0, unchanged)
2. After `displayToPanelCoords`: panel=0, localRow=0, localCol=0 (for top-left panel)
3. After `panelPixelOffset`: offset=0 (first byte in buffer)

If any step inverts the row coordinate, the pixel would appear at the wrong vertical position.

#### Recommended Investigation

1. **Check rotation constant** - What value is configured in hwPanelConfig for the 2×2 setup?
2. **Trace displayToPanelCoords()** - Does it correctly map row 0 to the top panel?
3. **Trace panelPixelOffset()** - Does it correctly place row 0 at the start of the panel buffer?

---

### Next Audit File

Continue with **isp_hub75_hwBufferAccess.spin2** to investigate `displayToPanelCoords()` and `panelPixelOffset()` - the core coordinate mapping functions.

---

## Code Audit: isp_hub75_hwBufferAccess.spin2

**Audit Date:** 2025-01-06
**Baseline:** v3.0.2
**Status:** COMPLETED

### Summary

This file has undergone **major expansion** for 2D panel grid support. It introduces a complete wire order mapping system, per-panel rotation tables, and new coordinate transformation functions. This is the **primary suspect** for the orientation issue.

### Change Categories

| Category | Description | Count |
|----------|-------------|-------|
| (a) Improvement | Cleanup, consolidation | 3 |
| (c) 2D Support | Wire order, per-panel rotation, coordinate mapping | 12 |
| (d) Potentially Detrimental | Hardcoded tables, configuration complexity | 2 |

---

### CRITICAL CHANGES (Investigate First)

#### 1. Hardcoded Wire Order Table
**Location:** Lines 121-123 (DAT section)
**Category:** (d) Potentially Detrimental

```spin2
' For 2x2 grid with bottom-first wiring: BL(0)->BR(1)->TL(2)->TR(3)
' Display panel index -> wire position
disp0WireOrder      BYTE    2, 3, 0, 1, 4, 5, 6, 7, ...
```

**This is a HARDCODED wire order that assumes specific physical wiring!**

| Display Panel | Wire Position | Physical Location (assumed) |
|---------------|---------------|----------------------------|
| 0 (top-left) | 2 | TL |
| 1 (top-right) | 3 | TR |
| 2 (bottom-left) | 0 | BL |
| 3 (bottom-right) | 1 | BR |

**Critical Question:** Does this match the actual physical wiring of the 2×2 panels?

If the actual wiring is different, the display will show scrambled panel positions - which could manifest as "upside down" if top/bottom panels are swapped.

**Verdict:** ⚠️ **VERIFY PHYSICAL WIRING** - This table must match hardware.

---

#### 2. Per-Panel Rotation Table (All Zeros)
**Location:** Lines 155-157 (DAT section)
**Category:** (d) Potentially Detrimental

```spin2
disp0PanelRots      BYTE    0, 0, 0, 0, 0, 0, 0, 0, ...
```

All panels have rotation = 0 (ROT_NONE).

**Critical Question:** If panels are physically mounted rotated (common in serpentine wiring), they need per-panel rotation.

For bottom-first wiring with panels daisy-chained:
- If the cable "folds back" between rows, bottom panels may need ROT_180
- Current config assumes all panels are mounted with same orientation

**Verdict:** ⚠️ **CHECK PHYSICAL ORIENTATION** - May need per-panel rotation values.

---

#### 3. New displayToPanelCoords() Function
**Location:** Lines 492-526
**Category:** (c) 2D Support

```spin2
PUB displayToPanelCoords(nChainIdx, displayRow, displayCol) : nPanelIndex, localRow, localCol
    ' For 2D grid:
    nPanelIndex := (displayRow / rowsPerPnl) * pnlsPerRow + (displayCol / colsPerPnl)
    localRow := displayRow // rowsPerPnl
    localCol := displayCol // colsPerPnl
```

**Analysis for 2×2 grid (128×64 panels):**
- Pixel (0, 0) → Panel 0, local (0, 0) ✓
- Pixel (63, 127) → Panel 0, local (63, 127) ✓
- Pixel (64, 0) → Panel 2, local (0, 0) ✓
- Pixel (64, 128) → Panel 3, local (0, 0) ✓

**Panel grid layout (Z-pattern):**
```
Display Panel 0 | Display Panel 1
Display Panel 2 | Display Panel 3
```

**Verdict:** ✅ Logic appears correct for Z-pattern grid.

---

#### 4. New panelPixelOffset() Function
**Location:** Lines 528-568
**Category:** (c) 2D Support

```spin2
PUB panelPixelOffset(nChainIdx, nDisplayPanelIndex, localRow, localCol) : byteOffset
    ' Convert display panel → wire panel
    nWirePanelIndex := wireOrderForPanel(nChainIdx, nDisplayPanelIndex)

    ' Apply per-panel rotation
    eRotation := panelRotationAt(nChainIdx, nDisplayPanelIndex)
    ' ... rotation transforms ...

    ' Calculate buffer offset
    byteOffset := (nWirePanelIndex * panelBytes) + ((rotatedRow * colsPerPnl) + rotatedCol) * bytesPerClr
```

**Key insight:** This function applies:
1. Wire order remapping (display → physical)
2. Per-panel rotation (0°, 90°, 180°, 270°)
3. Buffer offset calculation

**The buffer is organized in wire order** - first panel in wire order gets bytes 0 to panelBytes-1.

**Verdict:** ✅ Logic appears correct, but depends on wire order table and rotation table being correct.

---

#### 5. buildWireOrderFromEnums() Function
**Location:** Lines 700-725
**Category:** (c) 2D Support

```spin2
PRI buildWireOrderFromEnums(nChainIdx)
    eStart := wireStart(nChainIdx)
    eTraverse := wireTraverse(nChainIdx)

    ' Check if using enum-based configuration (values >= $40)
    ' If using explicit grid mode (values 0-16), skip
    if eStart < hwEnum.WIRE_STARTS_TOP_LEFT or eTraverse < hwEnum.WIRE_ROWS_FIRST
        debug("HUB75: Using explicit wire order table (not enum-based)")
        return

    ' Build table from enums...
```

**Critical:** This function only runs if enum values are >= $40. Otherwise, it uses the hardcoded `disp0WireOrder` table.

**Question:** What are the current values of `DISP0_WIRE_START` and `DISP0_WIRE_TRAVERSE` in hwPanelConfig?

**Verdict:** ⚠️ Need to check hwPanelConfig to see which mode is active.

---

### SIGNIFICANT CHANGES (2D Support)

#### 6. Table Entry Extended with Wire Config
**Location:** Lines 64-89 (DAT section)
**Category:** (c) 2D Support

```spin2
' ADDED to each screen table entry:
        LONG  user.DISP0_WIRE_START, user.DISP0_WIRE_TRAVERSE
```

New fields for wire configuration stored in the chain descriptor table.

**Verdict:** ✅ Good - allows per-chain wire configuration.

---

#### 7. New setWireConfig() Method
**Location:** Lines 222-240
**Category:** (c) 2D Support

```spin2
PUB setWireConfig(eHub75Chain, eWireStart, eWireTraverse)
    ' Store wire config and build wire order table from enums
    LONG[pEntry][ENTR_WIRE_START_OFST] := eWireStart
    LONG[pEntry][ENTR_WIRE_TRAVERSE_OFST] := eWireTraverse
    buildWireOrderFromEnums(nChainIdx)
```

**Verdict:** ✅ Clean API for configuring wire order.

---

#### 8. New wirePositionToGridCoords() Helper
**Location:** Lines 727-816
**Category:** (c) 2D Support

Complex function that converts wire position to grid coordinates based on:
- Start corner (TOP_LEFT, TOP_RIGHT, BOT_LEFT, BOT_RIGHT)
- Traversal pattern (ROWS_FIRST, COLS_FIRST, SERPENTINE_ROWS, SERPENTINE_COLS)

**Verdict:** ✅ Comprehensive support for various wiring patterns.

---

#### 9. New Pin Group Support
**Location:** Lines 199-207
**Category:** (c) 2D Support

```spin2
case ePinBase
    hwEnum.PINS_P0_P15:
    hwEnum.PINS_P8_P23:      ' NEW
    hwEnum.PINS_P16_P31:
    hwEnum.PINS_P32_P47:
    hwEnum.PINS_P40_P55:     ' NEW
```

**Verdict:** ✅ Matches rgb3bit pin group additions.

---

#### 10. Consolidated Size Retrieval Methods
**Location:** Lines 276-305
**Category:** (a) Improvement

```spin2
' NEW consolidated methods:
PUB displaySizeInPixels(nChainIdx) : nMaxRows, nMaxColumns
PUB displaySizeInPanels(nChainIdx) : nPanelsPerColumn, nPanelsPerRow
PUB panelSizeInPixels(nChainIdx) : nPanelRows, nPanelColumns
```

**Verdict:** ✅ Cleaner API - returns multiple values in one call.

---

#### 11. Removed Color Correction (Moved to colorUtils)
**Location:** Lines 657-699 (removed)
**Category:** (a) Improvement

```spin2
' REMOVED:
PUB correctedColor(...)
PUB correctedSingleColor(...)
PUB colorAtDesiredBitWidth(...)
```

These functions moved to `isp_hub75_colorUtils.spin2`.

**Verdict:** ✅ Better separation of concerns.

---

### Audit Conclusions

#### Root Cause Analysis: "Upside Down" Display

The orientation system has **three tiers** that must all be correct:

| Tier | Mechanism | Current State | Likely Issue? |
|------|-----------|---------------|---------------|
| 1. Wire Order | `disp0WireOrder` table | Hardcoded: 2,3,0,1 | ⚠️ **VERIFY** |
| 2. Per-Panel Rotation | `disp0PanelRots` table | All zeros | ⚠️ **POSSIBLE** |
| 3. Display Rotation | `panelRotation()` | From config | Check value |

**Most Likely Cause:** The hardcoded wire order assumes bottom-first wiring (panels 0,1 in bottom row = wire positions 2,3). If the actual wiring starts from top, the top and bottom rows would be swapped.

**Second Possibility:** If panels are physically rotated 180° in some positions (common in serpentine wiring), the per-panel rotation table needs non-zero values.

#### Recommended Verification Steps

1. **Check actual hardware wiring:**
   - Which physical panel is wire position 0? (First in daisy chain)
   - Which corner does the chain start from?
   - Does the cable fold back between rows?

2. **Check hwPanelConfig values:**
   - What is `DISP0_WIRE_START`?
   - What is `DISP0_WIRE_TRAVERSE`?
   - Are they enum values (>= $40) or explicit (< $40)?

3. **Quick Test:** Try flipping the wire order:
   - Change `disp0WireOrder` from `2,3,0,1` to `0,1,2,3` (or vice versa)
   - See if display orientation changes

#### Wire Order Cheat Sheet

| Physical Wiring | Wire Order Table |
|-----------------|------------------|
| TL→TR→BL→BR (Z-pattern) | 0,1,2,3 |
| BL→BR→TL→TR (Bottom-first Z) | 2,3,0,1 |
| TL→TR→BR→BL (Serpentine) | 0,1,3,2 |
| BL→BR→TR→TL (Bottom serpentine) | 2,3,1,0 |

---

## Code Audit: isp_hub75_hwPanelConfig.spin2

**Audit Date:** 2025-01-06
**Baseline:** v3.0.2
**Status:** COMPLETED

### Summary

This file has been updated to configure a 2×2 grid of 128×64 panels. The changes are configuration-only (no code logic changes). Two new constants were added for wire order specification. All changes appear appropriate for Config 11 hardware.

### Change Categories

| Category | Description | Count |
|----------|-------------|-------|
| (a) Configuration Update | Panel size/grid settings | 4 |
| (c) 2D Support | Wire order constants | 2 |
| (d) Improvement | Color depth upgrade | 1 |

---

### DISP0 Configuration Changes (Primary Display)

| Constant | v3.0.2 Value | Current Value | Change Type |
|----------|--------------|---------------|-------------|
| `DISP0_MAX_PANEL_COLUMNS` | 64 | **128** | (a) Config - 128×64 panels |
| `DISP0_MAX_PANEL_ROWS` | 64 | 64 | No change |
| `DISP0_MAX_PANELS_PER_ROW` | 1 | **2** | (a) Config - 2×2 grid |
| `DISP0_MAX_PANELS_PER_COLUMN` | 1 | **2** | (a) Config - 2×2 grid |
| `DISP0_COLOR_DEPTH` | DEPTH_6BIT | **DEPTH_8BIT** | (d) Full 24-bit color |
| `DISP0_ROTATION` | ROT_NONE | ROT_NONE | No change |
| `DISP0_WIRE_START` | N/A | **WIRE_STARTS_BOT_RIGHT** | (c) NEW - serpentine start |
| `DISP0_WIRE_TRAVERSE` | N/A | **WIRE_SERPENTINE_ROWS** | (c) NEW - serpentine pattern |

---

### CRITICAL ANALYSIS: Wire Order Configuration

#### Physical Wiring Described

```
Configuration says:
  WIRE_STARTS_BOT_RIGHT + WIRE_SERPENTINE_ROWS

Physical wiring path: BR → BL → TL → TR

Display panel layout (Z-pattern from top-left):
    [0][1]    ← Display panels
    [2][3]

Wire order (bottom-right start, serpentine up):
    Wire 0 = Display panel 3 (BR)
    Wire 1 = Display panel 2 (BL)
    Wire 2 = Display panel 0 (TL)
    Wire 3 = Display panel 1 (TR)
```

#### Expected vs Hardcoded Wire Order Table

| Display Panel | Expected Wire | Hardcoded Wire | Match? |
|---------------|---------------|----------------|--------|
| 0 (TL) | 2 | 2 | ✅ |
| 1 (TR) | 3 | 3 | ✅ |
| 2 (BL) | 1 | 0 | ❌ **MISMATCH** |
| 3 (BR) | 0 | 1 | ❌ **MISMATCH** |

**Expected table:** `2, 3, 1, 0`
**Hardcoded table:** `2, 3, 0, 1`

⚠️ **POTENTIAL BUG:** The hardcoded `disp0WireOrder` table in hwBufferAccess doesn't match the serpentine pattern! If `buildWireOrderFromEnums()` doesn't run correctly, panels 2 and 3 will be swapped.

#### Why This Might Not Be a Bug

The enum values are:
- `WIRE_STARTS_BOT_RIGHT` = $43
- `WIRE_SERPENTINE_ROWS` = $4A

Both values are >= $40, which means `buildWireOrderFromEnums()` SHOULD execute and override the hardcoded table. The hardcoded table may be stale/unused.

**Recommended Action:** Verify `buildWireOrderFromEnums()` runs correctly and produces the expected `2, 3, 1, 0` mapping.

---

### Configuration Verification Against Config 11

| Setting | Config 11 Spec | Current Code | Status |
|---------|----------------|--------------|--------|
| Panel model | P2-1515-128X64-32S-S2 | (matches) | ✅ |
| Panel size | 128×64 | 128×64 | ✅ |
| Chip | ICN2037BP | CHIP_ICN2037 | ✅ |
| Address lines | ABCDE | ADDR_ABCDE | ✅ |
| Pin base | P16-P31 | PINS_P16_P31 | ✅ |
| Grid | 2×2 | 2×2 | ✅ |
| Total display | 256×128 | 256×128 | ✅ |
| Color swap | R/B swapped | (handled by CHIP_ICN2037) | ✅ |

**All configuration settings match Config 11 requirements.** ✅

---

### Timing Constants Analysis

**Finding:** There are NO explicit clock frequency constants in this file.

The ICN2037 timing requirements (20 MHz max clock) must be enforced in:
- `isp_hub75_rgb3bit.spin2` (PASM2 driver) - via WAITX timing
- `CHIP_ICN2037` flag includes `CLK_WIDE_PULSE` for wider clock pulses

This file does not control clock speed. The 833 kHz issue is NOT caused by hwPanelConfig.

---

### hwEnums.spin2 Changes (Supporting Constants)

The enum file was also modified. Key additions:

| Section | New Enums | Purpose |
|---------|-----------|---------|
| (1) Pin Groups | PINS_P8_P23, PINS_P24_P39, PINS_P40_P55 | Additional adapter positions |
| (3) Rotation | ROT_0, ROT_90, ROT_180, ROT_270 | Cleaner rotation values |
| (7) Wire Start | WIRE_STARTS_TOP_LEFT, ..._BOT_RIGHT | Wire chain start corner |
| (7) Wire Traverse | WIRE_ROWS_FIRST, WIRE_SERPENTINE_* | Wire chain pattern |
| (8) Explicit Grid | PNL_NONE, PNL_FIRST | Non-rectangular layouts |
| (9) Cube Faces | FACE_TOP, FACE_FRONT, etc. | Cube display support |

These are all new 2D support features - no existing functionality was changed.

---

### Other Display Changes (DISP1, DISP2)

| Display | Change | Notes |
|---------|--------|-------|
| DISP1 | Added wire constants | Default values (TOP_LEFT, ROWS_FIRST) |
| DISP2 | Color depth 5→4 bit, wire constants | Reduced depth, added wire config |

Minor changes to secondary displays - not affecting DISP0 2×2 configuration.

---

### Audit Conclusions

#### This File Does NOT Cause:

| Symptom | Why Not This File |
|---------|-------------------|
| 833 kHz Clock | No timing constants here - clock is PASM2 |
| 103ms Bursts | No loop/timing code - configuration only |
| LAT/OE Wrong | No signal code - configuration only |

#### This File MAY Affect:

| Symptom | How It Could Contribute |
|---------|-------------------------|
| Upside Down | Wire order config defines panel mapping |
| Panel Scrambling | If wire order table is wrong, panels swap |

#### Key Verification Required

1. **Confirm physical wiring matches config:**
   - Is wire 0 actually connected to bottom-right panel?
   - Does cable serpentine up (BL→TL)?

2. **Verify buildWireOrderFromEnums() executes:**
   - Add debug statement to confirm function runs
   - Print resulting wire order table

3. **Check wire order table at runtime:**
   - Display what wireOrderForPanel() returns for each panel

#### Verdict

**Configuration is CORRECT for Config 11 hardware.** The potential issue is whether the wire order table builder in hwBufferAccess correctly interprets these settings. This is an inter-file dependency that must be verified.

---

### Next Steps

1. **Phase 1F - Synthesis** - Correlate all audit findings
2. **Verify wire order table at runtime** - Add debug to buildWireOrderFromEnums()
3. **Test physical wiring** - Confirm BR→BL→TL→TR matches reality

---

## Code Audit: Synthesis and Change Correlations

**Synthesis Date:** 2025-01-06
**Audits Completed:** 5 of 5 (1A-1E)
**Status:** COMPLETED

### Executive Summary

The codebase has undergone **significant restructuring** since v3.0.2 to support 2D panel grids. The changes span all core driver files and introduce new architectural concepts (wire order, per-panel rotation, chain vs display dimensions).

**Total Changes Identified:** 42 modifications across 5 files
**High Risk Changes:** 5
**Medium Risk Changes:** 7
**Low Risk Changes:** 30

---

### Master Change Summary Table

| # | Change Description | File(s) | Category | Risk | Related Symptoms |
|---|-------------------|---------|----------|------|------------------|
| **1** | **REMOVED `drvh pinLedOE` before subframe gap** | rgb3bit | Timing | ⚠️ HIGH | LAT/OE wrong, brightness |
| **2** | **New pin conditioning (P_LOW_1MA, fltl)** | rgb3bit | Timing | ⚠️ HIGH | Clock signal quality |
| **3** | **colCtrMax = chain width (not display)** | rgb3bit | Timing | ⚠️ HIGH | 833 kHz clock, frame timing |
| **4** | **convertScreen2PWM() complete rewrite** | panel | Architecture | ⚠️ HIGH | Orientation, data order |
| **5** | **Wire-panel-major buffer layout** | panel | Buffers | ⚠️ HIGH | Scrambled if mismatch |
| 6 | LA pins fixed at P8-P11 | rgb3bit | Config | MEDIUM | Pin conflict risk |
| 7 | pwmRowSizeInLongs calculation changed | rgb3bit | Buffers | MEDIUM | Row buffer sizing |
| 8 | Coordinate mapping to hub75Bffrs | screenUtils | Coordinates | MEDIUM | Upside down |
| 9 | Hardcoded wire order table | hwBufferAccess | Coordinates | MEDIUM | Panel swap |
| 10 | Per-panel rotation (all zeros) | hwBufferAccess | Coordinates | MEDIUM | Panel flip |
| 11 | buildWireOrderFromEnums() added | hwBufferAccess | 2D Support | LOW | - |
| 12 | displayToPanelCoords() added | hwBufferAccess | 2D Support | LOW | - |
| 13 | panelPixelOffset() added | hwBufferAccess | 2D Support | LOW | - |
| 14 | Wire config constants | hwPanelConfig | Config | LOW | - |
| 15 | Panel size 64→128 columns | hwPanelConfig | Config | LOW | - |
| 16 | Grid size 1×1→2×2 | hwPanelConfig | Config | LOW | - |
| 17 | Color depth 6→8 bit | hwPanelConfig | Config | LOW | Buffer size |
| 18 | New pin groups (P8-P23, P40-P55) | rgb3bit, hwEnums | 2D Support | LOW | - |
| 19 | Method renaming (cmd prefix) | rgb3bit | Cleanup | LOW | - |
| 20 | Size retrieval consolidation | panel, screenUtils | Cleanup | LOW | - |

---

### Cross-File Dependency Analysis

The 2D support changes created a **new data flow architecture**:

```
                    hwPanelConfig (constants)
                           │
                           ▼
    ┌─────────────────hwBufferAccess────────────────────┐
    │  Wire order table ←── buildWireOrderFromEnums()   │
    │  displayToPanelCoords() → panelPixelOffset()      │
    └───────────────────────────────────────────────────┘
           ▲                          ▲
           │                          │
    ┌──────┴──────┐            ┌──────┴──────┐
    │ screenUtils │            │    panel    │
    │ (writes to  │            │ (reads from │
    │  buffer)    │            │  buffer)    │
    └─────────────┘            └─────────────┘
                                     │
                                     ▼
                               ┌──────────┐
                               │ rgb3bit  │
                               │ (PASM2   │
                               │  output) │
                               └──────────┘
```

**Critical Dependencies:**

| Upstream | Downstream | Dependency Type | Verified? |
|----------|------------|-----------------|-----------|
| hwPanelConfig | hwBufferAccess | Wire config enums | ✅ Yes |
| hwBufferAccess | screenUtils | displayToPanelCoords() | ❓ Need verify |
| hwBufferAccess | panel | Buffer layout assumption | ❓ Need verify |
| hwBufferAccess | rgb3bit | colCtrMax via chain width | ❓ Need verify |

---

### Symptom-to-Change Correlation Matrix

| Symptom | Primary Suspect(s) | Evidence | Confidence |
|---------|-------------------|----------|------------|
| **833 kHz Clock** | #3 colCtrMax doubled | 512 clocks/row vs 256, explains 2× slower | **HIGH** |
| **LAT/OE Wrong** | #1 REMOVED OE disable | Direct change to OE control | **HIGH** |
| **103ms Bursts** | #3 + #4 combined | Double frame time + conversion overhead | **MEDIUM** |
| **Upside Down** | #8 + #9 combined | Coordinate delegation + wire order | **MEDIUM** |
| **Panel Scramble** | #5 + #9 mismatch | Buffer layout ≠ wire order | **MEDIUM** |

---

### Top 5 Most Suspicious Changes

#### 1. REMOVED `drvh pinLedOE` (rgb3bit:1123)
```pasm
' WAS:
    drvh    pinLedOE    ' <-- THIS LINE WAS DELETED
    ' inter-subframe gap
```
**Why Suspicious:** This directly controls OE, which is one of the broken symptoms. OE is ACTIVE LOW - `drvh` disables LEDs. Removing it means LEDs stay on during subframe transitions.

**Action:** Restore this line and test.

---

#### 2. Pin Conditioning with P_LOW_1MA (rgb3bit:774-788)
```spin2
wrpin   ##P_LOW_1MA, pinGrpLAXT
drvl    pinGrpLAXT
fltl    maskAddr         ' reset smart pin mode
fltl    maskRgb12        ' reset smart pin mode
```
**Why Suspicious:**
- P_LOW_1MA is very weak drive (1mA sink)
- `fltl` briefly floats output pins (high-Z)
- Applied to address AND RGB pins
- Could cause signal integrity issues at 20MHz

**Action:** Test with this section commented out.

---

#### 3. colCtrMax = maxChainColumns (rgb3bit:384-391)
```spin2
' WAS:
    colCtrMax := hub75Bffrs.maxDisplayColumns(chainIndex)  ' = 256
' NOW:
    colCtrMax := maxChainColumns  ' = 512 for 2×2 of 128-wide panels
```
**Why Suspicious:**
- Doubles the clock pulses per row
- For 2×2 grid: 4 panels × 128 cols = 512 clocks instead of 256
- This is CORRECT for the chain but changes frame timing significantly

**Analysis:** This change is **intentional and probably correct** for 2D support. However, it means the observed 833 kHz might actually be expected behavior (not a bug). Need to verify the math.

---

#### 4. convertScreen2PWM() Algorithm Rewrite (panel:381-596)
**Why Suspicious:**
- Complete rewrite of core pixel conversion
- Old: Simple backward traversal from end
- New: Nested row×col with per-pixel offset calculation
- Assumes wire-panel-major buffer layout

**Key Question:** Does screenUtils write to buffer in wire-panel-major order?

---

#### 5. Wire Order Table Mismatch (hwBufferAccess:121-123)
```spin2
' Hardcoded: 2, 3, 0, 1
' Expected for serpentine: 2, 3, 1, 0
```
**Why Suspicious:** Panels 2 and 3 are swapped in the hardcoded table versus what the serpentine pattern requires. However, `buildWireOrderFromEnums()` should override this.

**Key Question:** Does buildWireOrderFromEnums() actually run? Does it compute correctly?

---

### Incomplete Change Patterns

| Pattern | Files Involved | Issue |
|---------|---------------|-------|
| Buffer layout assumption | panel ↔ screenUtils | panel assumes wire-major, screenUtils unclear |
| Wire order | hwBufferAccess | Hardcoded table vs enum builder - which runs? |
| Debug output | panel | `markEnd()` active - adds serial overhead |
| Uncertain code | rgb3bit:335 | `modeDatRotLeft := TRUE ' i've no IDEA'` |

---

### Preliminary Hypotheses by Symptom

#### Symptom 1: 833 kHz Clock (Expected: 20 MHz)

**Hypothesis A - NOT A BUG (Most Likely):**
The 833 kHz may be the CORRECT clock frequency for the new chain width.

**Math:**
- Old: 256 columns × N rows × M bit planes = X clocks/frame
- New: 512 columns × N rows × M bit planes = 2X clocks/frame
- If frame rate stays same, clock pulses are spread over 2× more columns
- Observed ratio: 20 MHz / 833 kHz ≈ 24×

The 24× slowdown suggests something more than just 2× column doubling. Need to check:
- Is there a WAITX timing constant that's wrong?
- Is PWM depth (8-bit vs 6-bit) affecting iterations?

**Hypothesis B - BUG:**
The pin conditioning (`P_LOW_1MA`) is limiting drive strength so severely that signal transitions are slowed.

---

#### Symptom 2: LAT/OE Wrong

**Hypothesis - HIGH CONFIDENCE:**
The REMOVED `drvh pinLedOE` instruction was disabling OE (blanking LEDs) during subframe transitions. Without it:
- OE stays LOW (outputs enabled) when it should be HIGH (blanked)
- This causes incorrect output enable behavior

**Fix:** Restore the `drvh pinLedOE` instruction.

---

#### Symptom 3: 103ms Bursts (~5 Hz flash)

**Hypothesis A:**
Double frame time from colCtrMax change + 8-bit PWM (vs 6-bit) creates longer refresh cycles that interact with a timeout or blocking operation.

**Hypothesis B:**
The demo application has a blocking loop or wait that occurs every ~103ms.

**Investigation needed:** Check demo_hub75_multi2x2panel.spin2 for timing loops.

---

#### Symptom 4: Upside Down

**Hypothesis:**
The wire order configuration says `WIRE_STARTS_BOT_RIGHT` (wire starts at bottom). If `buildWireOrderFromEnums()` doesn't run correctly, or if there's a coordinate inversion in `displayToPanelCoords()`, the top and bottom could be swapped.

**Key test:** Add debug output showing wire order table after init.

---

### Synthesis Conclusions

#### Change Scope Assessment

The v3.0.2 → current changes are **not incremental bug fixes** but rather a **major architectural overhaul** for 2D panel support. This explains why multiple symptoms appeared together - the changes are interconnected.

#### Root Cause Prioritization

| Priority | Action | Expected Impact |
|----------|--------|-----------------|
| **1** | Restore `drvh pinLedOE` | Fix LAT/OE symptom |
| **2** | Verify wire order table at runtime | Fix orientation |
| **3** | Remove/disable pin conditioning | Improve signal quality |
| **4** | Verify clock math for 2×2 grid | Understand 833 kHz |
| **5** | Check demo app for 103ms timing | Find burst source |

#### Phase 2 Readiness

All Phase 1 audits are complete. We now have:
- ✅ Full change inventory (42 changes)
- ✅ Symptom-to-change correlation
- ✅ Priority ranking for fixes
- ✅ Specific code locations for each issue

**Ready to proceed with Phase 2 symptom research.**

---

## Symptom Research: Clock Speed (833 kHz vs Expected 20 MHz)

**Research Date:** 2025-01-06
**Status:** COMPLETED

### System Clock Configuration

From `demo_hub75_multi2x2panel.spin2` (lines 17-19):
```spin2
CLK_FREQ = 335_000_000                                        ' system freq as a constant 2.985 nSec
_clkfreq = CLK_FREQ                                           ' set system clock
```

**P2 System Clock: 335 MHz** (2.985 ns per cycle)

---

### Clock Generation Mechanism

The HUB75 CLK signal is generated in `isp_hub75_rgb3bit.spin2` in the `wrLatchAtEnd` routine (lines 1086-1100):

```pasm
clkNONextByte
    rep     @eobytes, colCtrMax         ' this is physical row in px
    ' write our 6 color bits
    altgb   byteOffset, pCogBffrIncr    ' 2 cycles - get byte from buffer
    getbyte colorByte, 0-0, #0-0        ' 2 cycles - extract byte
    drvl    pinLedCLK                   ' 2 cycles - CLK LOW
    setbyte OUTA, colorByte, #3         ' 2 cycles - output data
    nop                                  ' 2 cycles - data setup time
    drvh    pinLedCLK                   ' 2 cycles - CLK HIGH (rising edge)
    nop                                  ' 2 cycles - extend CLK high pulse
    nop                                  ' 2 cycles - extend CLK high pulse
eobytes
```

**Instruction Timing Analysis:**

| Instruction | Cycles | Purpose |
|-------------|--------|---------|
| altgb | 2 | Calculate buffer address |
| getbyte | 2 | Extract pixel byte |
| drvl pinLedCLK | 2 | CLK → LOW |
| setbyte OUTA | 2 | Output RGB data |
| nop | 2 | Data setup time |
| drvh pinLedCLK | 2 | CLK → HIGH (rising edge) |
| nop | 2 | Extend HIGH pulse |
| nop | 2 | Extend HIGH pulse |
| **TOTAL** | **16** | **per clock pulse** |

---

### Expected Clock Frequency Calculation

```
P2 Clock: 335 MHz
Cycles per HUB75 CLK: 16
HUB75 CLK Period: 16 / 335,000,000 = 47.8 ns
HUB75 CLK Frequency: 1 / 47.8 ns = 20.9 MHz
```

**Expected instantaneous CLK frequency: ~21 MHz** ✅ (within ICN2037 spec of 20-30 MHz)

---

### Observed vs Expected Analysis

| Metric | Expected | Observed | Ratio |
|--------|----------|----------|-------|
| CLK Frequency | 20.9 MHz | 833 kHz | **25× slower** |
| CLK Period | 47.8 ns | 1.2 µs | 25× longer |

**The 25× ratio is significant** - it suggests either:
1. A measurement artifact (average vs instantaneous)
2. The driver not running at all during measurement
3. A fundamental configuration error

---

### Key Timing Constants/Variables

| Variable | Source | Value for 2×2 Grid | Purpose |
|----------|--------|-------------------|---------|
| `CLK_FREQ` | demo file | 335 MHz | P2 system clock |
| `colCtrMax` | rgb3bit start() | 512 | Clock pulses per row |
| `rowCtrMax` | rgb3bit config | 32 | Rows per half-frame |
| `maxPwmBuffers` | hwBffrs | 8 | PWM bit planes (8-bit color) |
| `maxPwmSubPages` | rgb3bit start() | varies | Subpages per PWM frame |

---

### Possible Causes of 25× Slowdown

#### Hypothesis A: Measurement is AVERAGE, Not Instantaneous (LIKELY)

The 833 kHz may be the **average CLK frequency over the entire frame**, not the instantaneous frequency during pixel output.

**Frame timing breakdown:**
- Pixels per row: 512 (colCtrMax)
- Rows per frame half: 32
- PWM bit planes: 8
- PWM repetitions: varies (8+4+2+1×5 = 19 displays per frame)

**Clocking time per frame:**
```
Total CLK pulses = 512 cols × 32 rows × 19 displays = 311,296 clocks
Time at 21 MHz: 311,296 / 21,000,000 = 14.8 ms
```

**If total frame time is ~100-200 ms (from burst pattern), average CLK would be:**
```
311,296 / 200 ms = 1.56 MHz average
311,296 / 350 ms = 889 kHz average  ← CLOSE TO OBSERVED!
```

**Verdict:** The 833 kHz is likely the AVERAGE CLK rate, not instantaneous. This suggests the driver is spending **350ms total per frame** - most of it NOT clocking.

---

#### Hypothesis B: Pin Conditioning Affecting Signal (POSSIBLE)

Lines 785-787 in rgb3bit:
```pasm
wrpin   ##P_LOW_1MA, maskAddr         ' set weak pull-down
fltl   maskAddr                       ' reset smart pin mode
fltl   maskRgb12                      ' reset smart pin mode
```

The `P_LOW_1MA` setting provides very weak drive strength (1mA). While this is applied to address pins, not CLK, there might be cross-talk or similar pin conditioning elsewhere.

**Note:** The CLK pin (`pinLedCLK`) uses `drvh` and `drvl` which use default drive strength, NOT the P_LOW_1MA setting. So this is unlikely to directly affect CLK speed.

---

#### Hypothesis C: modeSlowCLK Not Implemented (CONFIRMED)

Lines 822-824 show commented-out slow clock code:
```pasm
'                    or      modeSlowCLK, modeSlowCLK   wz
'    if_z            SETR    waitInst1of1,#%0000000_00  'make into NOP instruction
'    if_z            SETD    waitInst1of1,##0           'make into NOP instruction
```

The `CLK_WIDE_PULSE` flag (set for ICN2037) was intended to add delays, but the implementation is **commented out**. This means:
- ICN2037 requests slow clock via flag
- Driver ignores the flag (no waitInst1of1 label exists)

**This is NOT causing slowdown** - if anything, the clock should be FASTER without the wait.

---

#### Hypothesis D: Burst Pattern Dominant (LIKELY)

The 103ms burst pattern means the driver is NOT outputting continuously. If output occurs only 50% of the time:
```
Effective average = 21 MHz × 0.5 / (number of idle periods)
```

If there are 12-13 idle periods per burst with ~50% duty:
```
21 MHz × 0.5 / 12.5 = 840 kHz  ← MATCHES OBSERVED!
```

---

### Conclusions

**Primary Finding:** The 833 kHz is likely an **average measurement** reflecting that:
1. The driver outputs CLK at ~21 MHz during active periods (CORRECT)
2. But there are **significant idle gaps** between rows, subpages, and frames
3. The total frame time is much longer than expected (~350ms instead of ~15ms)

**Root Cause:** The issue is NOT the clock loop speed. It's the **overall frame timing** being dominated by gaps and overhead.

---

### Recommended Actions

| Priority | Action | Expected Result |
|----------|--------|-----------------|
| 1 | Verify instantaneous CLK | Should be ~21 MHz |
| 2 | Measure CLK duty cycle | Should show bursts of 21 MHz |
| 3 | Profile inter-row gaps | Identify where time is spent |
| 4 | Profile inter-frame gaps | Identify blocking code |
| 5 | Check for debug() statements | Serial output adds latency |

**Key Question to Answer:** Is the 833 kHz:
- (a) The instantaneous frequency during pixel output? → BIG PROBLEM
- (b) The average over the entire frame including gaps? → Expected given burst pattern

---

### Next Research Task

Investigate the **103ms burst pattern** (Phase 2C) to understand where time is being spent between active CLK output periods. The clock loop itself appears correct (~21 MHz).

---

## Symptom Research: LAT/OE Signal Timing

**Research Date:** 2025-01-06
**Status:** COMPLETED

### ICN2037 Requirements (from Docs/ICN2037/README.md)

| Signal | Active Level | Purpose | Min Timing |
|--------|--------------|---------|------------|
| **OE** | ACTIVE LOW | Output enable (LOW=on, HIGH=blanked) | 60ns pulse width |
| **LAT/LE** | ACTIVE HIGH | Latch data (pulse HIGH to latch) | 20ns pulse width |

**Required Sequence:**
1. Blank outputs (OE HIGH) before row change
2. Clock in all row data
3. After last CLK: set LAT HIGH, change address
4. LAT LOW to latch data
5. OE LOW to enable new row outputs

---

### P2KB Instruction Timing Reference

| Instruction | Cycles | At 335 MHz | Purpose |
|-------------|--------|------------|---------|
| **DRVH** | 2 | 6 ns | Set pin HIGH |
| **DRVL** | 2 | 6 ns | Set pin LOW |
| **WAITX #N** | 2+N | (2+N) × 3 ns | Delay N+1 cycles |

---

### Current LAT/OE Sequence Analysis

#### `wrLatchAtEnd` Routine (lines 1076-1128)

**Per-Row Sequence:**

```
Line  | Instruction                  | OE State | LAT State | Notes
------|------------------------------|----------|-----------|------
1087  | rep @eobytes, colCtrMax      |   LOW    |    LOW    | Clock all pixels
1097  | drvh pinLedCLK               |   LOW    |    LOW    | Last rising edge
1101  | drvl pinLedCLK               |   LOW    |    LOW    | Final CLK LOW
1104  | drvh pinLedOE                |   HIGH   |    LOW    | Blank for address change ✅
1106-7| add/call emitAddr            |   HIGH   |    LOW    | Change row address
1109  | drvh pinLedLATCH             |   HIGH   |   HIGH    | Latch data
1110  | waitx #3                     |   HIGH   |   HIGH    | 15 ns latch settle
      | --- Enclosed mode (z) ---
1113  | drvl pinLedOE                |   LOW    |   HIGH    | Enable before unlatch
1114  | drvl pinLedLATCH             |   LOW    |    LOW    | End latch
      | --- Offset mode (nz) ---
1116  | drvl pinLedLATCH             |   HIGH   |    LOW    | End latch first
1117  | waitx #3                     |   HIGH   |    LOW    | Settle
1118  | drvl pinLedOE                |   LOW    |    LOW    | Then enable
1119  | waitx #3                     |   LOW    |    LOW    | Final settle
1123  | cmp byteOffset ...           |   LOW    |    LOW    | More rows?
1124  | jmp #wrLineLatchAtEnd        |   LOW    |    LOW    | Yes: next row
      | --- End of subframe ---
1128  | jmp #getCommand              |   LOW ❌ |    LOW    | PROBLEM: OE still LOW!
```

---

### CRITICAL BUG IDENTIFIED

#### Git Diff Evidence (v3.0.2 → current)

**OLD (v3.0.2):**
```pasm
                    cmp      byteOffset, maxPwmSubPgSzBytes wc
    if_c            jmp     #wrLineLatchAtEnd
                    drvh    pinLedOE          ← WAS HERE
                    '
                    ' ---  inter-subframe gap  ---
                    '
                    jmp     #getCommand
```

**NEW (current):**
```pasm
                    cmp      byteOffset, maxPwmSubPgSzBytes wc
    if_c            jmp     #wrLineLatchAtEnd
                                              ← REMOVED!
                    '
                    ' ---  inter-subframe gap  ---
                    '
                    jmp     #getCommand
```

**Impact:**
- In v3.0.2: OE was HIGH (blanked) during inter-subframe gap ✅
- In current: OE stays LOW (enabled) during inter-subframe gap ❌

This means LEDs remain ON while the driver transitions between subframes, potentially causing:
- Visible flicker or brightness anomalies
- Display of garbage data during buffer switch
- Output glitches at subframe boundaries

---

### Signal Polarity Verification

| Signal | ICN2037 Spec | Driver Implementation | Correct? |
|--------|--------------|----------------------|----------|
| OE | ACTIVE LOW | `drvh` = OFF, `drvl` = ON | ✅ Correct |
| LAT | ACTIVE HIGH | `drvh` = latch, `drvl` = unlatch | ✅ Correct |
| CLK | Rising edge | `drvl` → `drvh` sequence | ✅ Correct |

**Polarities are correct.** The issue is the **removed OE disable**, not polarity.

---

### Timing Verification

#### LAT Pulse Width
- `drvh pinLedLATCH` → `waitx #3` → `drvl pinLedLATCH`
- Timing: 2 + 5 = 7 cycles × 3 ns = 21 ns
- ICN2037 min: 20 ns
- **Meets spec** ✅ (barely)

#### OE Pulse Width (blank period)
- From `drvh pinLedOE` to `drvl pinLedOE`
- Approximately 20-30 cycles depending on mode
- ICN2037 min: 60 ns
- **Meets spec** ✅

---

### `wrLineLatchOvlp` Routine (FM6126A panels)

This routine is used for panels that overlap latching with data output. Not relevant to ICN2037 panels, which use `wrLatchAtEnd`.

---

### Additional Code Locations Affecting LAT/OE

| Location | Line | Signal | Purpose |
|----------|------|--------|---------|
| `wrCogBuffer` start | 1011 | `drvl pinLedOE` | Enable output at frame start |
| `wrLatchAtEnd` per-row | 1104 | `drvh pinLedOE` | Blank during address change |
| `wrLatchAtEnd` per-row | 1113/1118 | `drvl pinLedOE` | Re-enable after latch |
| **REMOVED** | ~1125 | `drvh pinLedOE` | Should blank at subframe end |

---

### 74HC04 Inverter Consideration

Per the panel schematic analysis, some signals may pass through the 74HC04 hex inverter. If OE passes through:
- Driver `drvh` (HIGH) → Inverter → Panel receives LOW (enabled)
- This would INVERT the polarity!

**Current evidence suggests NO inversion** - the driver uses standard HUB75 polarity (OE active LOW), which is correct for ICN2037.

However, if the panel has inverted OE:
- `drvh` would enable outputs (wrong!)
- `drvl` would disable outputs (wrong!)

**Recommendation:** Test with inverted OE if fix doesn't work.

---

### Proposed Fix

#### Priority 1: Restore Removed OE Disable

Add the removed line back to `isp_hub75_rgb3bit.spin2`:

```pasm
                    cmp      byteOffset, maxPwmSubPgSzBytes wc
    if_c            jmp     #wrLineLatchAtEnd
                    drvh    pinLedOE                    ' RESTORE: blank outputs before subframe gap
                    '
                    ' ---  inter-subframe gap  ---
                    '
                    jmp     #getCommand
```

**Location:** After line 1124, before the inter-subframe gap comment.

---

### Alternative Approaches

| Approach | Description | Risk |
|----------|-------------|------|
| **(a) Restore OE disable** | Add `drvh pinLedOE` back | LOW - proven v3.0.2 behavior |
| (b) Add to frame start | Disable OE at `getCommand` entry | MEDIUM - timing may differ |
| (c) Invert polarity | Swap all `drvh`/`drvl` for OE | HIGH - affects entire driver |

---

### Conclusions

1. **Root Cause Identified:** The `drvh pinLedOE` instruction was REMOVED from the inter-subframe gap section.

2. **Polarities are Correct:** OE active LOW, LAT active HIGH matches ICN2037 requirements.

3. **Timing Meets Spec:** LAT pulse width ~21 ns (min 20 ns), OE pulse width adequate.

4. **Simple Fix Available:** Restore the single removed line.

5. **74HC04 Inversion:** Unlikely but should be tested if fix doesn't work.

---

## Symptom Research: Burst Pattern (103ms On/Off Flashing)

**Research Date:** 2025-01-06
**Status:** COMPLETED

### Symptom Details

- **Observed:** RGB data emitted in bursts, not continuously
- **Pattern:** ~103ms of activity, then ~103ms of no output (~5 Hz flash rate)
- **Impact:** Panel flashes instead of stable display
- **Note:** This is ~10 Hz full cycle, suggesting a software loop or timing issue

---

### Refresh Loop Architecture Analysis

#### Complete Data Flow (Spin2 → PASM2)

```
demo_hub75_multi2x2panel.spin2:180
    └── display.commitScreenToPanelSet()
            └── isp_hub75_display.spin2:209-216
                    └── panelSet.convertScreen2PWM()
                            └── isp_hub75_panel.spin2:388-599
                                    ├── [INLINE PASM2] - converts 24-bit to PWM frames
                                    └── matrix.cmdWritePwmBuffer(pPwmFrameSet)
                                            └── isp_hub75_rgb3bit.spin2:478-484
                                                    ├── dvrArgument := pBuffer
                                                    ├── dvrCommand := CMD_SHOW_PWM_BUFFER
                                                    └── RETURNS IMMEDIATELY (non-blocking!)
```

**Key Finding:** The Spin2 side sends the buffer address to the PASM2 driver and returns immediately. The PASM2 driver then runs continuously in its own COG.

---

#### PASM2 Driver Loop Structure

```
drive_matrix (runs in dedicated COG):
    └── getCommand: (main loop at line 841)
            ├── Check ongoing work: pwmSubPgCt, fillSubPgCt, pwmFrameCt
            ├── rdlong nxtCommand, pCommmand  ← read command from HUB
            └── if CMD_SHOW_PWM_BUFFER:
                    └── call #cmdDsplyFrameSet
                            ├── Display frame 0: 128× (BCM MSB)
                            ├── Display frame 1: 64×
                            ├── Display frame 2: 32×
                            ├── Display frame 3: 16×
                            ├── Display frame 4: 8×
                            ├── Display frame 5: 4×
                            ├── Display frame 6: 2×
                            ├── Display frame 7: 1× (BCM LSB)
                            └── return → getCommand (loop continues)
```

**Key Finding:** The PASM loop structure is correct for continuous refresh. After `cmdDsplyFrameSet` completes, it immediately checks for the next command. If command is still `CMD_SHOW_PWM_BUFFER`, it redisplays.

---

### Expected Frame Timing Calculation

#### Configuration (from hwPanelConfig):

| Parameter | Value |
|-----------|-------|
| Display Size | 256×128 pixels (2×2 grid of 128×64 panels) |
| Color Depth | 8-bit (DEPTH_8BIT) |
| System Clock | 335 MHz |
| Chain Columns | 4 panels × 128 = 512 columns |
| Address Rows | 32 (1/32 scan for 64-row panel) |

#### COG Buffer Sizing:

```
pwmRowSizeInLongs = (512/2 + 3)/4 = 64 longs/row
pwmRowsInCogBuffer = 128/64 = 2 rows fit in COG buffer
pwmSubPageCount = 4096/128 = 32 subpages per PWM frame
```

#### Per-Row Output Time:

The REP loop in `wrLatchAtEnd` (lines 1087-1100):
```pasm
rep     @eobytes, colCtrMax         ' 512 iterations
    altgb / getbyte / drvl / setbyte / nop / drvh / nop / nop
```

- ~16 cycles per column × 3ns = 48ns/column
- 512 columns × 48ns = ~24.6µs per row
- Add address/latch overhead: ~3µs
- **Total: ~28µs per row**

#### Per Subpage Time:

- 2 rows + HUB read (~1µs for 128 longs)
- **~57µs per subpage**

#### Per PWM Frame:

- 32 subpages × 57µs = **~1.82ms per frame**

#### Full BCM Cycle (8-bit):

| Frame | BCM Weight | Time |
|-------|------------|------|
| 0 (MSB) | 128× | 233 ms |
| 1 | 64× | 116 ms |
| 2 | 32× | 58 ms |
| 3 | 16× | 29 ms |
| 4 | 8× | 14.6 ms |
| 5 | 4× | 7.3 ms |
| 6 | 2× | 3.6 ms |
| 7 (LSB) | 1× | 1.8 ms |
| **TOTAL** | **255×** | **~464ms** |

**Calculated PWM Cycle: ~464ms = ~2.2 Hz refresh rate**

---

### Critical Observation: 103ms ≈ MSB Frame Contributions

The 103ms burst pattern correlates with early PWM frames:

| PWM Frames | Cumulative Time | Match? |
|------------|-----------------|--------|
| Frame 0 (128×) | 233 ms | Too long |
| Frame 0 + 1 (64×) | ~100-110 ms | **~103ms!** |
| Frame 0 alone | 50% time | ~116 ms | Close |

**Hypothesis:** The display may be completing approximately frames 0+1 worth of BCM weighting before some reset occurs.

---

### Potential Cause Analysis

#### Cause 1: BCM Counter Issue (Unlikely)

If `pwmFrameSetCt` started at wrong value or halving logic failed:
- `shr pwmFrameSetCt, #1` divides by 2 each frame
- Starting value: `maxCtPerFrame = (255+1)/2 = 128`
- Sequence: 128 → 64 → 32 → 16 → 8 → 4 → 2 → 1

The code at lines 890-904 appears correct.

#### Cause 2: Demo Application Issue (Check Required)

Looking at `demo_hub75_multi2x2panel.spin2`:
- Line 180: `display.commitScreenToPanelSet()` - called once
- Then `waitSec(120)` - waits 120 seconds doing nothing

The demo should NOT be interfering after the initial commit.

#### Cause 3: Missing OE Disable (Documented Above)

The removed `drvh pinLedOE` could cause visible symptoms during subframe gaps, but wouldn't cause actual timing gaps in the PASM loop.

#### Cause 4: modeSlowCLK Not Implemented (CONFIRMED)

Lines 822-824 in rgb3bit are **COMMENTED OUT**:
```pasm
'                    or      modeSlowCLK, modeSlowCLK   wz
'    if_z            SETR    waitInst1of1,#%0000000_00  'make into NOP instruction
'    if_z            SETD    waitInst1of1,##0           'make into NOP instruction
```

The `CLK_WIDE_PULSE` flag is SET for ICN2037 chips but the code that would USE it is disabled. However, this would make the clock FASTER, not create gaps.

#### Cause 5: HUB Memory Contention (Unlikely)

The PASM cog reads/writes HUB memory for:
- Command polling: `rdlong nxtCommand, pCommmand` - 2 cycles
- Buffer reads: `rdlong cogBuffer, ptra++` with SETQ - ~128 cycles

These are fast operations and shouldn't cause 103ms gaps.

---

### Key Insight: The Math Doesn't Match

| Observation | Value | Expected |
|-------------|-------|----------|
| Burst on time | ~103ms | ~464ms (full cycle) |
| Burst off time | ~103ms | 0ms (continuous) |
| Implied duty cycle | 50% | 100% |

The driver SHOULD be running continuously at 100% duty. The 50% duty cycle suggests something external to the PASM loop is causing gaps.

---

### Areas NOT Yet Investigated

1. **Double-buffer swap timing** - Does `convertScreen2PWM` block the PASM driver?
   - No - `cmdWritePwmBuffer` returns immediately

2. **Debug serial output in tight loop** - Are debug() statements in the refresh path?
   - `markEnd()` in panel.spin2 outputs timing data, but only once per commit

3. **Multiple COG interference** - Is another COG affecting timing?
   - Need to check if any other COGs are started

4. **Smart pin modes** - Are pin configurations causing issues?
   - The `fltl` and `wrpin P_LOW_1MA` could affect signal integrity

---

### Conclusions

1. **The PASM driver loop structure is CORRECT** - continuous refresh should occur

2. **Expected frame timing: ~464ms per full PWM cycle** (2.2 Hz for 8-bit depth)

3. **The 103ms pattern is unexplained by code analysis** - no obvious blocking point

4. **Most likely causes:**
   - Hardware timing issue with panel (clock speed, signal integrity)
   - Subtle interaction between BCM timing and panel response
   - Panel not latching data correctly (related to removed OE disable)

5. **The 103ms on/off pattern at 50% duty suggests the issue is NOT in the core PASM timing loop** - something else is gating the output

---

### Recommended Actions

| Priority | Action | Rationale |
|----------|--------|-----------|
| 1 | **Restore `drvh pinLedOE`** before subframe gap | Ensures proper blanking during transitions |
| 2 | **Reduce color depth to 3-bit** temporarily | Reduces PWM cycle from 464ms to ~14ms for faster debugging |
| 3 | **Add LA instrumentation** at frame boundaries | Use pinLAXT_08-11 to visualize frame timing on logic analyzer |
| 4 | **Check for continuous CLK** on logic analyzer | Verify CLK runs continuously during "on" periods |
| 5 | **Verify panel responds to simple patterns** | Fill with solid color, verify no flashing |

---

### Next Research Task

Continue with **Phase 2D: Display Orientation (Upside Down)** to investigate the coordinate mapping and wire order configuration

---

## Symptom Research: Display Orientation (Upside Down)

**Research Date:** 2025-01-06
**Status:** COMPLETED

### Symptom Details

- **Observed:** Entire 2×2 panel display is inverted (upside down)
- **Expected:** Correct orientation matching physical panel arrangement
- **Impact:** Visual output unusable without correction

---

### Three-Tier Orientation System Architecture

The driver uses a three-tier system to handle panel orientation:

```
Tier 1: Wire Order
├── Maps display panel index → wire position in daisy chain
├── Configured via: DISP0_WIRE_START + DISP0_WIRE_TRAVERSE
└── Built by: buildWireOrderFromEnums() → disp0WireOrder table

Tier 2: Per-Panel Rotation
├── Individual 0°/90°/180°/270° rotation for each panel
├── Configured via: disp0PanelRots table in hwBufferAccess
└── Applied in: panelPixelOffset()

Tier 3: Display Rotation
├── Whole-display rotation
├── Configured via: DISP0_ROTATION constant
└── Applied in: screenUtils before coordinate mapping
```

---

### Current Configuration Settings

#### From hwPanelConfig.spin2:

| Setting | Value | Meaning |
|---------|-------|---------|
| `DISP0_WIRE_START` | `WIRE_STARTS_BOT_RIGHT` ($43) | Wire 0 at bottom-right |
| `DISP0_WIRE_TRAVERSE` | `WIRE_SERPENTINE_ROWS` ($4A) | Serpentine pattern up |
| `DISP0_ROTATION` | `ROT_NONE` | No whole-display rotation |

**Note:** Line 65 contains: `'DISP0_ROTATION = hwEnum.ROT_180  ' uncomment if display is upside-down`

This suggests the developer anticipated orientation issues!

#### From hwBufferAccess.spin2:

| Table | Values | Meaning |
|-------|--------|---------|
| `disp0WireOrder` | `2, 3, 0, 1, ...` | Hardcoded (may be overwritten) |
| `disp0PanelRots` | `0, 0, 0, 0, ...` | All panels: no rotation |

---

### Wire Order Analysis

#### Physical Wiring Configuration

```
Configuration: WIRE_STARTS_BOT_RIGHT + WIRE_SERPENTINE_ROWS

Physical wire path: BR(0) → BL(1) → TL(2) → TR(3)

Display panel layout (Z-pattern from top-left):
    [0=TL][1=TR]    ← Display panels (how software sees them)
    [2=BL][3=BR]

Wire order (where each display panel appears in physical chain):
    Wire 0 = Display panel 3 (BR) ← First in chain
    Wire 1 = Display panel 2 (BL)
    Wire 2 = Display panel 0 (TL)
    Wire 3 = Display panel 1 (TR) ← Last in chain
```

#### Expected Wire Order Table

For the software to correctly map display coordinates to physical panels:

```
Display Panel → Wire Position (stored in disp0WireOrder)
    [0] → 2    (TL goes to wire 2)
    [1] → 3    (TR goes to wire 3)
    [2] → 1    (BL goes to wire 1) ← Note serpentine reversal
    [3] → 0    (BR goes to wire 0) ← Note serpentine reversal

Expected table: [2, 3, 1, 0]
Hardcoded table: [2, 3, 0, 1] ← MISMATCH on entries 2,3!
```

**Important:** Since enum values >= $40, `buildWireOrderFromEnums()` SHOULD run and overwrite the hardcoded table with the correct [2, 3, 1, 0] values.

---

### Coordinate Transform Pipeline Trace

When drawing pixel at display coordinate (row, col):

```
1. screenUtils.setPanelColorBitsForRC(row, col, color)
   ├── Apply Tier 3: Display rotation (DISP0_ROTATION)
   │   └── Currently ROT_NONE → no transform
   │
   ├── hub75Bffrs.displayToPanelCoords(row, col)
   │   └── Returns: panelIndex, localRow, localCol
   │   └── For 2×2 grid: panelIndex = (row/64)*2 + (col/128)
   │       • Row 0-63 → Panel 0 or 1 (top row)
   │       • Row 64-127 → Panel 2 or 3 (bottom row)
   │
   └── hub75Bffrs.panelPixelOffset(panelIndex, localRow, localCol)
       ├── Apply Tier 1: Wire order mapping
       │   └── wireOrderForPanel(panelIndex) → wireIndex
       │
       ├── Apply Tier 2: Per-panel rotation
       │   └── panelRotationAt(panelIndex) → eRotation
       │   └── Currently all ROT_NONE → no transform
       │
       └── Calculate: byteOffset = (wireIndex * panelBytes) + localOffset
```

---

### buildWireOrderFromEnums() Verification

The function should produce this mapping:

| wirePos | gridCoords | displayIdx | Table Entry |
|---------|------------|------------|-------------|
| 0 | (1,1) = BR | 3 | table[3] = 0 |
| 1 | (1,0) = BL | 2 | table[2] = 1 |
| 2 | (0,0) = TL | 0 | table[0] = 2 |
| 3 | (0,1) = TR | 1 | table[1] = 3 |

**Final table should be: [2, 3, 1, 0]**

The debug output at line 728 should show:
```
HUB75: Wire order [disp0..3]->wire: 2, 3, 1, 0
```

If it shows `2, 3, 0, 1`, the function has a bug.

---

### Most Likely Causes of "Upside Down"

#### Cause A: Per-Panel Rotation Missing (HIGH PROBABILITY)

For serpentine wiring where the cable "folds back" between rows:
- Bottom row panels (wire 0, 1) may be physically rotated 180°
- This is common to keep input connectors accessible

**Current setting:** All panels ROT_NONE
**Likely needed:** `disp0PanelRots = [0, 0, 2, 2, ...]` (panels 2,3 rotated 180°)

If physical panels are mounted inverted but software doesn't compensate, those panels appear upside down.

#### Cause B: Display Rotation Needed (QUICK TEST)

The config file has a ready-to-use fix:
```spin2
'DISP0_ROTATION = hwEnum.ROT_180  ' uncomment if display is upside-down
```

Uncommenting this line would flip the entire display 180°.

#### Cause C: Wire Order Table Bug (CHECK DEBUG OUTPUT)

If `buildWireOrderFromEnums()` fails or has a logic error:
- Wrong table would map panels to incorrect positions
- Check debug output for "Wire order [disp0..3]->wire:" line

#### Cause D: Coordinate Inversion in convertScreen2PWM() (LESS LIKELY)

The algorithm rewrite processes pixels in a different order than v3.0.2:
- Old: Backward from end of buffer
- New: Forward row-by-row

If row indexing is inverted somewhere, top/bottom would be swapped.

---

### Diagnostic Approach

#### Step 1: Check Debug Output

Look for these lines in debug output:
```
HUB75: Built wire order table for 4 panels, start=$43 traverse=$4A
HUB75: Wire order [disp0..3]->wire: 2, 3, 1, 0  ← Should be this!
```

If second line shows `2, 3, 0, 1`, the buildWireOrderFromEnums() function is not working correctly.

#### Step 2: Quick Test - Display Rotation

In `isp_hub75_hwPanelConfig.spin2`, change line 64:
```spin2
' From:
DISP0_ROTATION = hwEnum.ROT_NONE

' To:
DISP0_ROTATION = hwEnum.ROT_180
```

If display flips correctly, the issue is simply the overall display orientation.

#### Step 3: Per-Panel Rotation Test

In `isp_hub75_hwBufferAccess.spin2`, change line 157:
```spin2
' From:
disp0PanelRots      BYTE    0, 0, 0, 0, ...

' To (if bottom row needs 180° rotation):
disp0PanelRots      BYTE    0, 0, 2, 2, ...
```

#### Step 4: Draw Test Pattern

Create a simple test pattern:
- Draw "TL" text at (0, 0)
- Draw "TR" text at (0, 128)
- Draw "BL" text at (64, 0)
- Draw "BR" text at (64, 128)

Observe which text appears where - this identifies exactly which transformation is wrong.

---

### Per-Panel Rotation Cheat Sheet

For serpentine wiring patterns:

| Wiring Pattern | Per-Panel Rotation Table |
|----------------|--------------------------|
| Z-pattern (no fold) | `0, 0, 0, 0` |
| Serpentine (cable folds at each row) | `0, 0, 2, 2` (bottom row 180°) |
| Serpentine 4x2 | `0, 0, 0, 0, 2, 2, 2, 2` |
| All panels mounted upside down | `2, 2, 2, 2` |

---

### Conclusions

1. **Configuration is intentional:** WIRE_STARTS_BOT_RIGHT + WIRE_SERPENTINE_ROWS is correct for the described wiring

2. **Wire order table should be computed correctly** by buildWireOrderFromEnums() - verify via debug output

3. **Most likely fix:** Either:
   - Set `DISP0_ROTATION = ROT_180` for whole-display flip
   - Set per-panel rotations for physical panel mounting

4. **Developer anticipated this:** The commented-out ROT_180 line suggests this is a known issue

5. **Diagnostic test pattern recommended** before making changes

---

### Recommended Actions

| Priority | Action | Rationale |
|----------|--------|-----------|
| 1 | **Check debug output** for wire order table | Verify buildWireOrderFromEnums() works |
| 2 | **Try DISP0_ROTATION = ROT_180** | Quick test for whole-display fix |
| 3 | **Draw labeled test pattern** | Identify exactly what's inverted |
| 4 | **Adjust per-panel rotation** if needed | Fix individual panel orientation |
| 5 | **Document working configuration** | Update config 11 notes |

---

### Next Research Task

Continue with **Phase 2E: Control Signal Polarity (74HC04 Investigation)** to document the polarity testing approach

---

## Symptom Research: Control Signal Polarity (74HC04 Investigation)

**Research Date:** 2025-01-06
**Status:** COMPLETED

### Background

The 128×64 panel (P2-1515-128X64-32S-S2) has a **74HC04D hex inverter** (U5) in the signal path. Without a panel schematic, we cannot determine which signals pass through it. If OE or LAT pass through the inverter, the driver polarity needs adjustment.

---

### Signal Inventory and Native Polarities

#### ICN2037 Native Signal Requirements

*Source: Docs/ICN2037/README.md*

| Signal | Active State | Description |
|--------|-------------|-------------|
| **OE** | **ACTIVE LOW** | Outputs ON when OE=LOW; OFF when OE=HIGH |
| **LE/LAT** | **ACTIVE HIGH** | Data transfers when LE=HIGH; held when LE=LOW |
| **CLK** | Rising Edge | Data shifts on rising edge |

#### Current Driver Implementation

From `isp_hub75_rgb3bit.spin2`:

| Action | Code | Line(s) |
|--------|------|---------|
| Enable output | `drvl pinLedOE` | 1011, 1061, 1113, 1118 |
| Disable output | `drvh pinLedOE` | 1040, 1104 |
| Start latch | `drvh pinLedLATCH` | 706, 734, 1041, 1109 |
| End latch | `drvl pinLedLATCH` | 705, 717, 733, 745, 1054, 1114, 1116 |

**Current driver matches ICN2037 native polarities** - OE active LOW, LAT active HIGH.

---

### 74HC04 Characteristics

*Source: TI SN74HC04 Datasheet*

| Parameter | Value |
|-----------|-------|
| Gates | 6 independent inverters |
| Propagation delay | 7ns (typ), 17ns (max) @ 5V |
| Input HIGH threshold | 3.15V @ Vcc=4.5V |
| Output drive | ±4mA @ 4.5V |

**Key Point:** The 74HC04 INVERTS any signal passing through it. A LOW input produces HIGH output, and vice versa.

---

### Likely 74HC04 Usage Patterns

Based on common LED panel design practices:

#### Most Likely: OE Inversion (HIGH PROBABILITY)

**Reason:** Panel designers may prefer OE active HIGH for:
- Level compatibility with upstream controllers
- Simpler logic (HIGH = on, LOW = off)
- Failsafe behavior (floating input = LOW = outputs off)

**If OE is inverted:**
- ICN2037 sees: OE=LOW when driver outputs HIGH
- Driver must output: ACTIVE HIGH (opposite of current)

#### Possible: CLK Buffering (MEDIUM PROBABILITY)

**Reason:** CLK needs to drive multiple ICN2037 chips (16 in this panel). A buffered/inverted clock provides:
- Clean edges with fresh drive strength
- Fan-out capability

**If CLK is inverted:**
- Data shifts on falling edge instead of rising
- May cause timing issues or require driver adjustment

#### Less Likely: LAT Inversion (LOW PROBABILITY)

**Reason:** LAT polarity rarely needs inversion, as HUB75 standard is already LAT active HIGH.

**If LAT is inverted:**
- ICN2037 sees: LE=HIGH when driver outputs LOW
- Driver must output: ACTIVE LOW (opposite of current)

---

### Systematic Test Matrix

#### Primary Test Combinations (Most Likely)

| Test # | OE Polarity | LAT Polarity | Expected Result |
|--------|-------------|--------------|-----------------|
| **1** | Normal (LOW=on) | Normal (HIGH=latch) | **Current** - should work if no inversion |
| **2** | **Inverted** (HIGH=on) | Normal (HIGH=latch) | **Try first** - most likely fix |
| **3** | Normal (LOW=on) | **Inverted** (LOW=latch) | Unlikely but possible |
| **4** | **Inverted** (HIGH=on) | **Inverted** (LOW=latch) | If both signals inverted |

#### Observable Behavior for Each Combination

| Scenario | Symptoms |
|----------|----------|
| **Both correct** | Normal display operation |
| **OE wrong only** | Display always on OR always blanked |
| **LAT wrong only** | Garbage/flickering - data never latches properly |
| **Both wrong** | Possible damage state - avoid prolonged testing |

---

### Code Modification Procedure

#### To Invert OE Polarity

In `isp_hub75_rgb3bit.spin2`, swap all `drvh`/`drvl` for `pinLedOE`:

```pasm
' Current (OE active LOW):
drvl pinLedOE    ' Enable output (OE=LOW)
drvh pinLedOE    ' Disable output (OE=HIGH)

' Inverted (OE active HIGH):
drvh pinLedOE    ' Enable output (OE=HIGH)  <- SWAP
drvl pinLedOE    ' Disable output (OE=LOW)  <- SWAP
```

**Lines to modify:** 1011, 1040, 1061, 1104, 1113, 1118

#### To Invert LAT Polarity

In `isp_hub75_rgb3bit.spin2`, swap all `drvh`/`drvl` for `pinLedLATCH`:

```pasm
' Current (LAT active HIGH):
drvh pinLedLATCH    ' Start latch pulse (LAT=HIGH)
drvl pinLedLATCH    ' End latch pulse (LAT=LOW)

' Inverted (LAT active LOW):
drvl pinLedLATCH    ' Start latch pulse (LAT=LOW)  <- SWAP
drvh pinLedLATCH    ' End latch pulse (LAT=HIGH)   <- SWAP
```

**Lines to modify:** 705, 706, 717, 733, 734, 745, 1041, 1054, 1109, 1114, 1116

---

### Recommended Testing Procedure

**IMPORTANT:** Polarity testing requires working clock signal first! Test AFTER fixing clock speed issue.

#### Step 1: Verify Clock is Working

Before polarity testing, confirm:
- Logic analyzer shows CLK at correct frequency (~20 MHz)
- Clock edges are clean
- Data shifts correctly on CLK edges

#### Step 2: Test OE Inversion First (Test #2)

1. Modify driver: Swap OE polarity (6 locations)
2. Compile and flash
3. Observe panel behavior:
   - **Improved display:** OE inversion was needed
   - **No change:** Try Test #3 or revert
   - **Worse (always on/off):** OE polarity was already correct, revert

#### Step 3: If Needed, Test LAT Inversion (Test #3)

1. Revert OE changes (if applied)
2. Modify driver: Swap LAT polarity (11 locations)
3. Compile and flash
4. Observe panel behavior:
   - **Improved display:** LAT inversion was needed
   - **No change or worse:** Revert

#### Step 4: If Needed, Test Both (Test #4)

Only if tests #2 and #3 individually failed but showed partial improvement:
1. Apply both OE and LAT inversion
2. Compile and flash
3. Observe

---

### Creating a Driver Flag for Polarity

For permanent solution, add configuration flags:

```spin2
' In isp_hub75_hwEnums.spin2:
CON
    OE_INVERTED = $100000    ' Flag for inverted OE polarity
    LAT_INVERTED = $200000   ' Flag for inverted LAT polarity

' In driver flags for 128x64 panel:
desiredFlags := hwEnum.CHIP_MANUAL_SPEC | hwEnum.CLK_WIDE_PULSE | hwEnum.RB_SWAP | hwEnum.OE_INVERTED
```

This allows per-chip-type configuration instead of manual code edits.

---

### Physical Investigation Alternative

If testing is inconclusive, physical inspection can help:

1. **Trace 74HC04 connections** on the panel PCB
2. **Follow signal paths** from HUB75 connector to ICN2037 chips
3. **Identify which gates** are used (74HC04 has 6 inverters)
4. **Document findings** for permanent driver configuration

---

### Conclusions

1. **74HC04 inverts any signal passing through it** - this is fundamental behavior

2. **Most likely scenario: OE is inverted** through the 74HC04
   - Many panels use OE active HIGH convention
   - Test OE inversion first (Test #2)

3. **Testing requires working clock** - fix clock speed issue BEFORE polarity testing

4. **Four primary test combinations** cover all OE/LAT polarity possibilities

5. **Observable symptoms guide diagnosis:**
   - Always on/off -> OE polarity issue
   - Garbage display -> LAT polarity issue

6. **Code changes are straightforward** - swap `drvh`/`drvl` for affected signal

---

### Dependency Chain

```
Fix Clock Speed -> Test Polarity -> Fix Other Issues
        |
  (clock must work to observe polarity effects)
```

---

### Recommended Test Order

| Priority | Test | Rationale |
|----------|------|-----------|
| 1 | Fix clock speed first | Required for all other testing |
| 2 | Test OE inversion | Most likely cause of issues |
| 3 | Test LAT inversion | Less likely but possible |
| 4 | Both inverted | Only if individual tests inconclusive |

---

*This research provides a systematic approach to resolve the 74HC04 polarity uncertainty. Actual testing should occur after clock speed is corrected.*

---

## Phase 5: Implementation Order (Established 2025-01-06 Evening)

### Terminology

| Term | Definition |
|------|------------|
| **Panel** | Individual 128×64 LED panel (physical hardware unit) |
| **Display** | The 2×2 grid of panels (256×128 logical pixels) |

### Physical Panel Orientation

**Key Finding:** All 4 panels in the 2×2 grid are mounted 180° rotated from the manufacturer's "standard" orientation.

**Evidence:**
- Looking at BACK of panel: INPUT connector on LEFT, arrows point UP
- Looking at FRONT of panel (LEDs facing user): INPUT should be on RIGHT for "standard" orientation
- User's setup has INPUT on LEFT when viewing FRONT → panels are 180° rotated

**Correct Approach:** Use per-panel rotation (Option A), NOT whole-display rotation (Option B).

**Reasoning:**
1. Wire order is a physical property (how cables are connected)
2. Panel mounting is a per-panel physical property
3. Per-panel rotation keeps coordinates intuitive: (0,0) = top-left of display
4. Display rotation is for viewing preference, not for fixing upside-down panels
5. Per-panel rotation generalizes to mixed orientations (e.g., serpentine wiring)

---

### Implementation Phases

#### Phase 5.1: Establish Baseline (No Rotations)
**Goal:** Confirm wire order and basic drawing work correctly

**Actions:**
- [ ] Set all panel rotations to ROT_0 (no rotation)
- [ ] Set display rotation to ROT_0 (no rotation)
- [ ] Draw to individual panels using panel-specific routines
- [ ] Label each panel by chain order (0, 1, 2, 3)
- [ ] Color each panel distinctly
- [ ] Mark corners with indicators (arrows, boxes)

**Expected Result:**
- Everything displays UPSIDE-DOWN (because panels are physically inverted)
- Chain order is CORRECT (panel 0 receives wire 0 data, etc.)
- This confirms wire order and basic drawing work

**Status:** ✅ COMPLETED (2025-01-07)

**Completion Notes:**
- Wire order identity mapping [0,1,2,3] verified working
- Physical wiring confirmed: Wire 0→TR, Wire 1→TL, Wire 2→BR, Wire 3→BL
- Panel-level drawing routines all working correctly
- Display-level drawing routines fixed (commit 21166f7):
  - Added `needsPanelColumnSwap()` for wire-routing compensation
  - Added `drawDisplayPixel()` helper for display coordinate transformation
  - Fixed circle drawing bug (row/column swap in octants)

---

#### Phase 5.2: Validate Per-Panel Rotation
**Goal:** Confirm per-panel rotation works correctly

**Actions:**
- [x] Set each panel rotation to ROT_180
- [x] Keep display rotation at ROT_0

**Expected Result:**
- Everything flips RIGHT-SIDE UP
- Chain numbers, arrows, text all readable and correct
- Panel positions unchanged (still in correct chain order)

**Status:** ✅ COMPLETED (2025-01-07)

**Completion Notes:**
- Per-panel rotation infrastructure added: DISP0_PANEL0_ROT through DISP0_PANEL3_ROT
- All panels set to ROT_180 - content displays right-side up
- Panel text, arrows, and boxes all render correctly

---

#### Phase 5.3: Fix MSB Black (2^7 Frame)
**Goal:** Eliminate flashing caused by black MSB frame

**Actions:**
- [x] Investigate why 2^7 PWM frame has no color data
- [x] Check PWM buffer generation in isp_hub75_panel.spin2
- [x] Check frame indexing in isp_hub75_rgb3bit.spin2
- [x] Verify double-buffering handoff is working
- [x] Fix the root cause

**Expected Result:**
- Flashing stops
- Full brightness restored
- All 8 PWM frames have correct color data

**Status:** ✅ COMPLETED (2026-01-08)

**Root Causes Found and Fixed:**

1. **BYTES_PER_COLOR Calculation Bug (isp_hub75_hwPanelConfig.spin2)**
   - Old formula: `BYTES_PER_COLOR = (COLOR_DEPTH * 3 + 7) / 8` gave 2 bytes for 5-bit color
   - But screen buffer always uses 3 bytes per pixel (one byte per R/G/B channel)
   - This caused pixel offset calculations to use 2-byte stride while code wrote 3 bytes
   - Result: Pixel data overlap - byte 2 of pixel N overwrote byte 0 of pixel N+1
   - Fix: Set `BYTES_PER_COLOR = 3` for all display configurations

2. **Brightness Rounding Error (isp_hub75_colorUtils.spin2)**
   - Old: `((colorValue * brightness) >> 8)` - truncates fractional bits
   - At brightness=128, max value 255 became 127 (bit 7 clear)
   - This meant MSB frame (Frame 0) was always empty at 50% brightness
   - Fix: `((colorValue * brightness + 128) >> 8)` - rounds to nearest
   - Now brightness=128 gives max value=128 (bit 7 set), MSB frame populated

**Performance Research (Sprint-Performance-Upgrade.md):**
- Analyzed refresh rate vs color depth tradeoffs
- 5-bit color enables ~40 Hz base refresh (vs ~5 Hz at 8-bit)
- Documented multi-COG architecture options for future optimization

---

#### Phase 5.4: Code Audit Review
**Goal:** Systematically address all audit findings

**Actions:**
- [ ] Review each audit finding from all files
- [ ] Decide action for each item (fix, defer, or mark OK)
- [ ] Implement fixes
- [ ] Verify fixes don't break other functionality

**Audit Items to Address:**

| File | Item | Current Status |
|------|------|----------------|
| rgb3bit | Pin Conditioning (P_LOW_1MA) | NOT ADDRESSED |
| rgb3bit | modeDatRotLeft uncertainty | NOT ADDRESSED |
| panel | convertScreen2PWM rewrite verification | NOT VERIFIED |
| panel | Wire-Panel-Major buffer assumption | NOT VERIFIED |
| screenUtils | Coordinate delegation to hwBufferAccess | NOT VERIFIED |
| hwBufferAccess | Wire order table correctness | NOT VERIFIED |
| hwBufferAccess | Per-panel rotation table | NOT VERIFIED |
| hwBufferAccess | displayToPanelCoords/panelPixelOffset | NOT VERIFIED |

**Status:** NOT STARTED

---

### Progress Tracking

| Phase | Status | Date Started | Date Completed | Notes |
|-------|--------|--------------|----------------|-------|
| 5.1 Baseline | COMPLETED | 2025-01-07 | 2025-01-07 | Display-level drawing works |
| 5.2 Panel Rotation | COMPLETED | 2025-01-07 | 2025-01-07 | Per-panel ROT_180 working |
| 5.3 MSB Black Fix | COMPLETED | 2025-01-07 | 2026-01-08 | Fixed BYTES_PER_COLOR + rounding |
| 5.4 Code Audit | NOT STARTED | - | - | - |

---

### Session Notes

**2025-01-06 Evening Session:**
- Established physical panel orientation (all 180° rotated)
- Decided on per-panel rotation approach
- Defined implementation order
- Clock timing FIXED at 20 MHz (confirmed on LA)
- OE disable before subframe gap FIXED
- Ready to begin Phase 5.1

---

**2025-01-06 Late Night Session - Phase 5.1 Progress:**

### Completed Work

1. **Enum Rename for Clarity:**
   - Changed `WIRE_STARTS_*` → `WIRE_ENTERS_*` in `isp_hub75_hwEnums.spin2`
   - "Wire enters" better describes where the adapter cable connects to the display grid
   - Updated all references in `isp_hub75_hwPanelConfig.spin2` and `demo_hub75_multi2x2panel.spin2`

2. **Wire Order Verified Working:**
   - Identity mapping `[0, 1, 2, 3]` is CORRECT - do NOT change this
   - Physical wiring confirmed: Wire 0→TR, Wire 1→TL, Wire 2→BR, Wire 3→BL
   - Panel numbers display correctly: TL:1, TR:0, BL:3, BR:2
   - The `wirePositionToGridCoords()` function produces identity mapping and is working

3. **Per-Panel Rotation Infrastructure:**
   - Added user config constants in `isp_hub75_hwPanelConfig.spin2`:
     - `DISP0_PANEL0_ROT`, `DISP0_PANEL1_ROT`, `DISP0_PANEL2_ROT`, `DISP0_PANEL3_ROT`
   - Updated `disp0PanelRots` table in `isp_hub75_hwBufferAccess.spin2` to use these constants
   - `panelRotationAt()` function retrieves per-panel rotation correctly
   - All panels set to `ROT_180` - content now displays right-side up

4. **Panel-Level Drawing Working:**
   - `fillPanel()` - fills correct panel with color ✓
   - `drawPanelBox()` / `drawPanelBoxOfColor()` - yellow boxes in TL corner of each panel ✓
   - Panel numbers and arrows display correctly ✓
   - Text on panels displays correctly ✓

5. **Documentation Added:**
   - Created `Docs/TECHNICAL_DEBT.md` with:
     - TD-001: Wire order table preprocessor optimization (deferred)
     - TD-002: Documentation consolidation (deferred)
     - TD-003: Panel routine parameter order inconsistency (deferred)
   - Updated `CLAUDE.md` with production code development guidance

### NOT YET WORKING - Display-Coordinate Drawing Routines

**Symptoms observed:**
- Orange squares (drawn with `drawBoxOfColor`): bottom half appears on top row, top half on bottom row
- White circle (drawn with `drawCircleOfColor`): top half shown at bottom of display, horizontal line at bottom (half moon), no bottom half visible
- Cyan crosshairs (drawn with `drawLineOfColor`): vertical line at left edge instead of center, horizontal line between row of panels

**Root Cause Analysis:**
- This is NOT a wire order issue - wire order is correct and must not be changed
- Panel routines work because they use `offsetToPanel(panelIndex)` which treats panelIndex as display index, then calls `drawPixelAtRC` with those display coordinates
- Display routines call `drawPixelAtRC` directly with display coordinates
- The transformation chain has an issue somewhere

**Code Flow for Display Drawing:**
```
drawBoxOfColor(row, col, w, h, filled, color)
  → drawLineOfColor(fmRow, fmCol, toRow, toCol, color)
    → pixels.drawPixelAtRC(chainIndex, row, col, color)
      → drawPixelAtRCwithRGB(chainIdx, row, col, r, g, b)
        1. Apply display-level rotation from panelRotation(nChainIdx)
        2. displayToPanelCoords(chainIdx, row, col) → panelIndex, localRow, localCol
        3. panelPixelOffset(chainIdx, panelIndex, localRow, localCol) → byteOffset
           - wireOrderForPanel() maps display panel → wire buffer
           - panelRotationAt() applies per-panel rotation
```

**Key Files to Investigate:**
1. `isp_hub75_screenUtils.spin2` lines 39-73: `drawPixelAtRCwithRGB()` - display-level rotation applied here
2. `isp_hub75_hwBufferAccess.spin2` lines 483-517: `displayToPanelCoords()` - converts display coords to panel+local
3. `isp_hub75_hwPanelConfig.spin2` line 64: `DISP0_ROTATION = hwEnum.ROT_NONE` - display-level rotation setting

**Hypothesis:**
The display-level rotation (`DISP0_ROTATION`) may need to be set to account for the physical wire layout. Currently set to `ROT_NONE`. The physical layout has display TL→wire 1→physical TL, but display coords (0,0) may be going to wrong physical position.

### Drawing Routine Inventory

**Panel-Relative Routines (WORKING):**
| Routine | File | Line | Description |
|---------|------|------|-------------|
| `fillPanel(panelIndex, color)` | isp_hub75_display.spin2 | 192 | Fill entire panel |
| `drawPanelBox(panelIndex, row, col, w, h, filled)` | isp_hub75_display.spin2 | 620 | Draw box in panel |
| `drawPanelBoxOfColor(panelIndex, row, col, w, h, filled, color)` | isp_hub75_display.spin2 | ~630 | Draw colored box in panel |
| `drawPanelLine(panelIndex, fmR, fmC, toR, toC)` | isp_hub75_display.spin2 | 703 | Draw line in panel |
| `drawPanelLineOfColor(panelIndex, fmR, fmC, toR, toC, color)` | isp_hub75_display.spin2 | ~710 | Draw colored line in panel |
| `setCursorOnPanel(line, col, panelIndex)` | isp_hub75_display.spin2 | ~250 | Set text cursor on panel |

**Display-Relative Routines (BROKEN):**
| Routine | File | Line | Description |
|---------|------|------|-------------|
| `drawBoxOfColor(row, col, w, h, filled, color)` | isp_hub75_display.spin2 | 594 | Draw box on display |
| `drawLineOfColor(fmR, fmC, toR, toC, color)` | isp_hub75_display.spin2 | 676 | Draw line on display |
| `drawCircleOfColor(ctrR, ctrC, radius, color)` | isp_hub75_display.spin2 | 766 | Draw circle on display |
| `fillScreen(color)` | isp_hub75_display.spin2 | ~180 | Fill entire display |

### Git Commit Made

Commit `fd948d2`: "Add per-panel rotation and wire order infrastructure for 2x2 grids"

Files committed:
- driver/isp_hub75_hwEnums.spin2
- driver/isp_hub75_hwPanelConfig.spin2
- driver/isp_hub75_hwBufferAccess.spin2
- driver/isp_hub75_display.spin2
- driver/isp_hub75_screenUtils.spin2
- driver/isp_hub75_panel.spin2
- driver/demo_hub75_multi2x2panel.spin2
- driver/demo_hub75_quadPanel.spin2
- driver/demo_hub75_color.spin2
- Docs/TECHNICAL_DEBT.md

---

### Saved Context Keys (for reference)

**Key: lesson_phase5_progress**
```
Phase 5.1 Progress Summary:
COMPLETED:
1. Renamed WIRE_STARTS_* to WIRE_ENTERS_* enums for clarity
2. Wire order identity table [0,1,2,3] verified working for panel routines
3. Per-panel rotation infrastructure exists and works
4. Added DISP0_PANELx_ROT constants to user config (isp_hub75_hwPanelConfig.spin2)
5. All panels set to ROT_180 - content now right-side up
6. Panel-level drawing confirmed working (yellow boxes, numbers, arrows correct)
7. Added TD-003 to TECHNICAL_DEBT.md (panel routine parameter order)
8. Updated CLAUDE.md with production code guidance
IN PROGRESS:
- Display-coordinate drawing routines broken (drawBoxOfColor, drawCircleOfColor, drawLineOfColor)
- Symptoms: row mapping inverted between top/bottom, column offset issues
Physical wiring (adapter at BL with Z-pattern):
- Wire 0→TR, Wire 1→TL, Wire 2→BR, Wire 3→BL
Panel numbers shown with identity wire order:
- TL:1, TR:0, BL:3, BR:2 (correct for wire positions)
```

**Key: lesson_phase5_status**
```
Phase 5.1 Status (2025-01-06):
COMPLETED:
1. WIRE_STARTS_* → WIRE_ENTERS_* enum rename (semantic clarity)
2. Wire order identity mapping [0,1,2,3] verified working
3. Physical wiring confirmed: Wire 0→TR, Wire 1→TL, Wire 2→BR, Wire 3→BL
4. Panel numbers display correctly: TL:1, TR:0, BL:3, BR:2
5. Per-panel rotation infrastructure working
6. User config constants: DISP0_PANEL0_ROT through DISP0_PANEL3_ROT
7. All panels set to ROT_180 - content right-side up
8. Panel-level drawing working: yellow boxes, numbers, arrows correct
NOT YET WORKING:
1. Display-coordinate drawing routines (drawBoxOfColor, drawCircleOfColor, drawLineOfColor)
   Symptoms: orange squares split wrong, circle half-moon at bottom, lines at edges not center
   Root cause: Display coords map to wrong physical positions due to wire layout
   Note: This is NOT a wire order issue - wire order is correct
KEY INSIGHT:
- Wire order is CORRECT and should NOT be changed
- The display coordinate issue is in the transformation chain, not wire order
- Panel routines work because they use wire indices directly
- Display routines fail because display coords don't account for physical layout
FILES TO INVESTIGATE:
- isp_hub75_screenUtils.spin2: drawPixelAtRCwithRGB() display-level rotation
- isp_hub75_hwBufferAccess.spin2: displayToPanelCoords()
- isp_hub75_hwPanelConfig.spin2: DISP0_ROTATION setting
```

---

**2026-01-08 Session - Phase 5.3 Completed:**

### MSB Black Frame Issue - RESOLVED

**Root Causes Found:**

1. **BYTES_PER_COLOR Bug:**
   - Formula `(COLOR_DEPTH * 3 + 7) / 8` gave 2 bytes for 5-bit color
   - Screen buffer always uses 3 bytes per pixel (one byte per R/G/B)
   - Caused pixel data overlap - corrupting adjacent pixels
   - Fix: Set BYTES_PER_COLOR = 3 for all configurations

2. **Brightness Rounding:**  
   - `((value * brightness) >> 8)` truncates, giving 127 instead of 128 at 50%
   - MSB frame (bit 7) was never set at typical brightness
   - Fix: Add rounding `((value * brightness + 128) >> 8)`

**Demo Updated:**
- Changed to primary colors (Blue, Green, Red, Magenta) for better 5-bit visibility
- White text on all panels
- Yellow panel corner boxes, Navy display corners
- White crosshairs, Cyan circle

**Performance Research:**
- Created Sprint-Performance-Upgrade.md with refresh rate analysis
- 5-bit color: ~40 Hz base refresh (vs ~5 Hz at 8-bit)
- Documented multi-COG architecture options

**Remaining in Sprint:**
- Phase 5.4: Code Audit Review (NOT STARTED)
