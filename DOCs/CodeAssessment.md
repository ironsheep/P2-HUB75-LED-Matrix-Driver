# P2 HUB75 LED Matrix Driver - Code Assessment

**Document Version:** 1.0  
**Date:** December 2024  
**Author:** Generated from codebase analysis

---

## Table of Contents

1. [Code Organization Analysis](#1-code-organization-analysis)
2. [Performance Analysis](#2-performance-analysis)
3. [Inconsistencies and Issues](#3-inconsistencies-and-issues)
4. [LUT RAM Optimization Opportunities](#4-lut-ram-optimization-opportunities)
5. [2D Panel Support Assessment](#5-2d-panel-support-assessment)
6. [Recommendations Summary](#6-recommendations-summary)

---

## 1. Code Organization Analysis

### 1.1 File Structure Evaluation

**Strengths:**
- Clear naming convention: `isp_hub75_` prefix for all driver files
- Logical separation: demos (`demo_*`), core driver (`isp_*`), configuration (`*Config`, `*Enums`)
- All driver files in single `/driver/` directory for easy inclusion

**File Categories:**

| Category | Files | Purpose |
|----------|-------|---------|
| User Configuration | `isp_hub75_hwPanelConfig.spin2`, `isp_hub75_hwBufferAccess.spin2`, `isp_hub75_hwBuffers.spin2` | User modifies these for their hardware |
| Core Driver | `isp_hub75_rgb3bit.spin2`, `isp_hub75_panel.spin2` | Low-level hardware control |
| Display API | `isp_hub75_display.spin2`, `isp_hub75_screenUtils.spin2` | User-facing graphics API |
| Utilities | `isp_hub75_colorUtils.spin2`, `isp_hub75_fonts.spin2` | Support functions |
| Optional | `isp_hub75_scrollingText.spin2`, `isp_hub75_7seg.spin2` | Extended features |
| Constants | `isp_hub75_hwEnums.spin2`, `isp_hub75_color.spin2` | Enumerations and constants |
| Demos | `demo_hub75_*.spin2` (11 files) | Example applications |

### 1.2 Module Separation Quality

**Well Separated:**
- PASM2 driver (`rgb3bit`) cleanly isolated from Spin2 code
- Color utilities separate from display logic
- Font data in dedicated file

**Could Be Improved:**
- `isp_hub75_hwBufferAccess.spin2` mixes buffer tables with geometry calculations
- Panel configuration spread across 3 files requiring coordinated changes
- Some coordinate transformation logic duplicated between `screenUtils` and `display`

### 1.3 Configuration File Design

**Current Approach:**
Three files must be modified in sync for multi-adapter support:
1. `isp_hub75_hwPanelConfig.spin2` - Panel geometry and settings
2. `isp_hub75_hwBufferAccess.spin2` - Buffer table entries
3. `isp_hub75_hwBuffers.spin2` - Buffer allocations

**Assessment:**
- Compile-time configuration is appropriate for embedded performance
- Requiring 3-file coordination is error-prone
- Well-documented with inline comments explaining each constant

---

## 2. Performance Analysis

### 2.1 Identified Bottlenecks

#### Priority 1: Pixel Clocking (CRITICAL)
**Location:** `isp_hub75_rgb3bit.spin2` lines 1087-1102

```pasm
rep @eobytes, colCtrMax         ' for each column
    altgb byteOffset, pCogBffrIncr
    getbyte colorByte, 0-0, #0-0 ' extract one byte
    drvl    pinLedCLK            ' falling edge
    setbyte OUTA, colorByte, #3  ' write color bits
    nop
    drvh    pinLedCLK            ' rising edge
    nop     
    nop                          ' extend pulse
eobytes:
    waitx   #2                   ' inter-bit gap
```

**Analysis:**
- Already highly optimized using `rep` instruction (zero-overhead loop)
- Clock pulse timing carefully tuned for panel requirements
- `nop` and `waitx` provide required setup/hold times
- **Verdict: Near-optimal; further gains unlikely without hardware changes**

#### Priority 2: HUB-to-COG Transfer (MEDIUM)
**Location:** `isp_hub75_rgb3bit.spin2` line 952

```pasm
setq    maxPwmSubPgSzLngsM1      ' setup count
_ret_   rdlong  cogBuffer, ptra++ ' bulk read with auto-increment
```

**Analysis:**
- Uses P2's block transfer capability efficiently
- COG buffer sized to 512 longs (maximum practical size)
- Hub access is 9-16 clocks depending on "egg-beater" timing
- **Verdict: Efficient; limited by P2 hub architecture**

#### Priority 3: Screen-to-PWM Conversion (LOW)
**Location:** `isp_hub75_panel.spin2` lines 287-360

**Analysis:**
- CPU-intensive bit extraction (8 bits × 3 colors × 2 halves per pixel)
- Uses inline PASM for speed (`testb` for bit extraction)
- Runs on main COG, not time-critical (done during frame prep)
- **Verdict: Acceptable; could benefit from LUT RAM optimization**

### 2.2 Current Optimizations in Place

| Optimization | Location | Benefit |
|--------------|----------|---------|
| Subpage buffering | rgb3bit | Reduces HUB transfer latency |
| `rep` instruction | rgb3bit | Zero-overhead pixel loop |
| `altgb`/`setbyte` | rgb3bit | Efficient byte operations |
| Bit-parallel output | rgb3bit | 6 color bits per instruction |
| Panel-specific code paths | rgb3bit | Avoids conditionals in hot loop |
| Double-buffering | panel | Smooth animation |
| Inline PASM | panel | Fast bit extraction |

### 2.3 Frame Rate Performance

Based on code analysis (actual measurements recommended):

| Configuration | Est. Electrical Rate | Color Depth | Est. Visible FPS |
|---------------|---------------------|-------------|------------------|
| 64×64 single | ~1000 Hz | 3-bit | ~143 fps |
| 64×64 single | ~1000 Hz | 8-bit | ~4 fps |
| 256×128 (2×2) | ~600 Hz | 5-bit | ~19 fps |
| 512×64 (4×1) | ~500 Hz | 8-bit | ~2 fps |

**Key Insight:** Color depth has the largest impact on visible frame rate.

---

## 3. Inconsistencies and Issues

### 3.1 FIXME/UNDONE Comments Catalogued

| File | Line | Comment | Issue |
|------|------|---------|-------|
| `isp_hub75_display.spin2` | 45 | `FIXME: UNDONE make this user configurable` | MAX_SCROLLING_REGIONS hardcoded to 4 |
| `isp_hub75_7seg.spin2` | 62 | `FIXME: UNDONE shouldn't this limit...` | Digit width boundary check incomplete |
| `isp_hub75_rgb3bit.spin2` | 441 | `FIXME: UNDONE issue command to driver...` | Stop command doesn't release pins |

### 3.2 Incomplete 2D Panel Support

**Symptom:** 2×2 panel configurations not working correctly

**Evidence from chk.diff:**
Code was **removed** that handled:
- `displayToPanelCoords()` - Map display x,y to panel index + local coords
- `panelToWireCoords()` - Convert panel coords to wire-order
- `mapLocationToWireOrder()` - Full coordinate translation pipeline
- `rotateWithinPanel()` - Apply per-panel rotation
- Panel wire mapping table (display order → wire order)
- Per-panel rotation table

**Recent Commits Indicate:**
- "preserve some work before we restart"
- "working on new test for quad but stopping to rework underpinnings first"
- "full chain with [2][2] still not working..."

**Root Cause Analysis:**
The existing `offsetToPanel()` method in `isp_hub75_hwBufferAccess.spin2` correctly calculates panel grid positions, but the pixel placement code in `isp_hub75_screenUtils.spin2` doesn't use it properly for 2D grids.

### 3.3 Potential Bugs

#### Bug 1: 2D Grid Coordinate Calculation
**Location:** `isp_hub75_screenUtils.spin2` - `drawPixelAtRCwithRGB()`

**Issue:** When panels are arranged in a 2D grid, the linear buffer offset calculation doesn't account for panel boundaries correctly.

**Current code assumes:**
```
offset = (row × displayWidth + column) × bytesPerColor
```

**Should be:**
```
panelIdx = (row / panelHeight) × panelsPerRow + (column / panelWidth)
localRow = row % panelHeight
localCol = column % panelWidth
panelOffset = offsetToPanel(panelIdx)
pixelOffset = (localRow × panelWidth + localCol) × bytesPerColor
finalOffset = panelOffset + pixelOffset
```

#### Bug 2: Rotation with Multi-Panel
**Location:** `isp_hub75_screenUtils.spin2`

**Issue:** Display-level rotation is applied, but this breaks multi-panel coordinate mapping. Rotation should be applied per-panel after determining which panel the pixel belongs to.

### 3.4 Code Quality Observations

**Positive:**
- Comprehensive header comments on all files
- MIT license clearly stated
- Version history in ChangeLog.md
- Good inline documentation of complex sections

**Areas for Improvement:**
- Some magic numbers without named constants
- Inconsistent spacing in some files
- Demo files have varying levels of completion
- Some commented-out code should be removed or documented

---

## 4. LUT RAM Optimization Opportunities

### 4.1 Current LUT RAM Status

**Finding: LUT RAM is completely unused by the PASM2 driver.**

Each P2 COG has:
- 512 longs (2KB) COG RAM - currently used for code + cogBuffer
- 512 longs (2KB) LUT RAM - **completely available**

LUT RAM access times:
- Read: 3 clock cycles (fixed)
- Write: 2 clock cycles (fixed)
- Compare to HUB: 9-16 clock cycles (variable, "egg-beater" dependent)

### 4.2 Optimization Opportunity 1: Gamma Correction Tables

**Current Implementation:**
Gamma correction is applied in Spin2 during pixel write, computing the lookup each time.

**Proposed Optimization:**
Pre-load gamma tables into LUT RAM at driver startup.

```
Memory requirement:
  256 entries × 3 colors × 1 byte = 768 bytes
  Fits easily in 2KB LUT RAM
  
Performance gain:
  Current: Calculate gamma in Spin2 (slow)
  Proposed: RDLUT lookup (3 cycles)
  Estimated speedup: 5-10× for color correction
```

**Implementation Sketch:**
```pasm
' At driver startup, load gamma tables to LUT
        mov     index, #0
        mov     lutAddr, #0
.loadGamma:
        rdlong  gammaVal, gammaTablePtr
        wrlut   gammaVal, lutAddr
        add     gammaTablePtr, #4
        add     lutAddr, #1
        djnz    index, #.loadGamma

' During color conversion
        rdlut   correctedRed, redValue
        rdlut   correctedGreen, greenValue  
        rdlut   correctedBlue, blueValue
```

### 4.3 Optimization Opportunity 2: Dither Patterns

**Use Case:** Improve perceived color quality at lower bit depths

**Proposed:**
Store 4×4 or 8×8 dither matrices in LUT RAM for ordered dithering.

```
Memory requirement:
  8×8 matrix × 1 byte = 64 bytes
  Multiple patterns = 256 bytes total
  
Performance gain:
  Enables better color quality at 3-5 bit depth
  Can achieve 5-bit visual quality at 3-bit memory cost
```

### 4.4 Optimization Opportunity 3: Pin Mapping Tables

**Use Case:** Support dynamic pin reassignment without recompilation

**Current:** Pin masks are computed at startup and stored in COG registers

**Proposed:** Store pin configuration tables in LUT for flexibility

### 4.5 LUT RAM Implementation Recommendation

**Priority Order:**
1. **Gamma tables** - Highest impact, straightforward implementation
2. **Dither patterns** - Good ROI for reduced color depth
3. **Pin mapping** - Nice-to-have, lower priority

**Estimated Development Effort:**
- Gamma tables: 2-4 hours
- Dither patterns: 4-8 hours
- Testing: 2-4 hours

---

## 5. 2D Panel Support Assessment

### 5.1 What Currently Exists

**Working Infrastructure:**

1. **Panel Grid Configuration** (`isp_hub75_hwPanelConfig.spin2`):
   ```spin2
   DISP0_MAX_PANELS_PER_ROW = 2      ' ✓ Supported
   DISP0_MAX_PANELS_PER_COLUMN = 2   ' ✓ Supported
   ```

2. **Grid Offset Calculation** (`isp_hub75_hwBufferAccess.spin2`):
   ```spin2
   PUB offsetToPanel(nChainIdx, nPanelIndex) : offsetPixelColumns, offsetPixelRows
       ' Correctly handles 2D grids!
       gridRow := panelIndex / pnlsPerRow
       gridColumn := panelIndex // pnlsPerRow
       offsetPixelRows := gridRow * rowsPerPnl
       offsetPixelColumns := gridColumn * colsPerPnl
   ```

3. **Display-Level Rotation** - Works for single panels

### 5.2 What's Missing

1. **Coordinate Translation in Pixel Operations**
   - `drawPixelAtRCwithRGB()` doesn't call `offsetToPanel()`
   - Linear buffer calculation ignores panel boundaries

2. **Wire Order Remapping** (not needed for Z-pattern)
   - Deleted code had: `DISP0_PANEL_WIRE_MAP = 2, 3, 0, 1`
   - For Z-pattern wiring, display order = wire order

3. **Per-Panel Rotation** (not needed for Z-pattern)
   - Deleted code had: `DISP0_PANEL_ROTATIONS = ROT_NONE, ROT_NONE, ROT_180, ROT_180`
   - Z-pattern doesn't require panel rotation

### 5.3 Z-Pattern Analysis (User's Configuration)

```
Wire order:  0 → 1
             ↓
             2 → 3

Display:     Panel 0 | Panel 1    (256×64 total)
             --------+--------
             Panel 2 | Panel 3    (256×128 total)
```

**Simplifications for Z-pattern:**
- Wire order matches display order (no remapping needed)
- No per-panel rotation required
- Only need proper coordinate translation

### 5.4 Required Code Changes

#### Change 1: Fix `drawPixelAtRCwithRGB()` in `isp_hub75_screenUtils.spin2`

**Current (broken for 2D):**
```spin2
colorOffset := (row * maxColumns + column) * bytesPerColor
```

**Required:**
```spin2
PUB drawPixelAtRCwithRGB(nChainIdx, row, column, red, green, blue) | panelIdx, localRow, localCol, panelOffset, pixelOffset
    ' Determine which panel this pixel belongs to
    panelIdx := (row / rowsPerPanel) * panelsPerRow + (column / colsPerPanel)
    
    ' Calculate local coordinates within panel
    localRow := row // rowsPerPanel   ' modulo
    localCol := column // colsPerPanel
    
    ' Get panel's base offset in buffer
    panelOffset := hub75Bffrs.offsetToPanel(nChainIdx, panelIdx)
    
    ' Calculate pixel position within panel
    pixelOffset := (localRow * colsPerPanel + localCol) * bytesPerColor
    
    ' Apply display rotation if needed (to local coordinates)
    ' ... rotation logic ...
    
    ' Write to buffer
    pScreen := hub75Bffrs.screenBufferAddress(nChainIdx)
    byte[pScreen + panelOffset + pixelOffset + 0] := correctedRed
    byte[pScreen + panelOffset + pixelOffset + 1] := correctedGreen
    byte[pScreen + panelOffset + pixelOffset + 2] := correctedBlue
```

#### Change 2: Verify Buffer Layout

The screen buffer must be organized panel-by-panel:
```
Buffer layout for 2×2 panels (256×128 total):
  [Panel 0 data: 128×64×3 bytes]
  [Panel 1 data: 128×64×3 bytes]
  [Panel 2 data: 128×64×3 bytes]
  [Panel 3 data: 128×64×3 bytes]
```

**Verify** that `isp_hub75_hwBuffers.spin2` allocates contiguous space.

#### Change 3: Update `offsetToPanel()` Return Value

Current `offsetToPanel()` returns pixel offsets, but needs to return byte offsets for direct buffer access:

```spin2
' Change return to byte offset
panelByteOffset := (panelIdx * panelPixels) * bytesPerColor
```

### 5.5 Recommendation: Fresh Implementation vs. Restore

**Assessment:** Fresh implementation is recommended.

**Rationale:**
1. Z-pattern wiring simplifies requirements significantly
2. Deleted code handled more complex cases (snake wiring, per-panel rotation)
3. Simpler code will be easier to debug and maintain
4. Core infrastructure (`offsetToPanel()`) already exists

**Implementation Steps:**
1. Add helper method `displayToPanelCoords()` in `isp_hub75_hwBufferAccess.spin2`
2. Modify `drawPixelAtRCwithRGB()` to use new helper
3. Test with `demo_hub75_quadPanel.spin2`
4. Verify with all drawing primitives (lines, boxes, text)

---

## 6. Recommendations Summary

### 6.1 High Priority

| Item | Effort | Impact |
|------|--------|--------|
| Fix 2D panel coordinate translation | 4-8 hours | Enables 2×2 panel support |
| Add `displayToPanelCoords()` helper | 2 hours | Cleaner architecture |
| Update demo_hub75_quadPanel.spin2 | 2 hours | Verification |

### 6.2 Medium Priority

| Item | Effort | Impact |
|------|--------|--------|
| Implement LUT RAM gamma tables | 4 hours | 5-10× color correction speedup |
| Consolidate configuration files | 4 hours | Easier multi-adapter setup |
| Fix FIXME comments | 2 hours | Code quality |

### 6.3 Low Priority

| Item | Effort | Impact |
|------|--------|--------|
| Add dither patterns to LUT | 8 hours | Better low-depth colors |
| Document magic numbers | 2 hours | Maintainability |
| Clean up commented code | 1 hour | Code hygiene |

### 6.4 Files to Modify

| File | Changes |
|------|---------|
| `isp_hub75_hwBufferAccess.spin2` | Add `displayToPanelCoords()`, fix `offsetToPanel()` return type |
| `isp_hub75_screenUtils.spin2` | Fix `drawPixelAtRCwithRGB()` for 2D grids |
| `isp_hub75_rgb3bit.spin2` | Add LUT RAM gamma table loading (optional) |
| `isp_hub75_hwPanelConfig.spin2` | Verify 2×2 constants |
| `demo_hub75_quadPanel.spin2` | Complete/fix for testing |

---

## Appendix: Deleted Code Reference (from chk.diff)

For reference, here are the key methods that were removed and may inform the fresh implementation:

```spin2
' These were deleted but show the intended approach:

PUB displayToPanelCoords(displayRow, displayCol) : panelIdx, localRow, localCol
    ' Map display coordinates to panel + local coordinates
    
PUB panelToWireCoords(panelIdx, localRow, localCol) : wireRow, wireCol
    ' Apply panel rotation and wire order remapping
    
PUB mapLocationToWireOrder(displayRow, displayCol) : wireRow, wireCol
    ' Complete pipeline: display coords → wire-order coords
```

The fresh implementation can be simpler since Z-pattern wiring doesn't require the rotation and remapping logic.

---

*Document generated from codebase analysis. Validate findings with actual testing.*
