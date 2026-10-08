# P2 HUB75 LED Matrix Driver - Code Assessment

**Document Version:** 2.0 (driver 4.0.0)  
**Date:** December 2024; brought up to the 4.0.0 driver October 2026  
**Author:** Generated from codebase analysis

> This is an assessment of the driver's structure and performance as it stands. The design it assesses is in the [Wiring Guide](WiringGuide.md), [Driver Details](../THEOPS.md) and [Theory of Operations](TheoryOfOperations.md); the measured refresh, commit and draw times are in the [Wiring Guide's refresh rate section](WiringGuide.md#refresh-rate). Open items are in `DOCs/plans/PUNCH-LIST.md` and [Technical Debt](TECHNICAL_DEBT.md).

---

## Table of Contents

1. [Code Organization Analysis](#1-code-organization-analysis)
2. [Performance Analysis](#2-performance-analysis)
3. [Findings](#3-findings)
4. [LUT RAM Opportunities](#4-lut-ram-opportunities)
5. [Recommendations Summary](#5-recommendations-summary)

---

## 1. Code Organization Analysis

### 1.1 File Structure Evaluation

**Strengths:**
- Clear naming convention: `isp_hub75_` prefix for all driver files
- Logical separation: demos (`demo_*`), test top files (`test_*`), core driver (`isp_*`), configuration (`*Config`, `*Enums`)
- All driver files in the single `driver/` directory for easy inclusion

**File Categories** (sizes are approximate line counts):

| Category | Files | Purpose |
|----------|-------|---------|
| User Configuration | `isp_hub75_hwPanelConfig.spin2` (about 350 lines) | The one file edited per hardware setup: chip, panel size, color depth, mounting, the wiring sentences, target refresh |
| Layout and buffers | `isp_hub75_hwBufferAccess.spin2` (about 2,300), `isp_hub75_hwBuffers.spin2` (about 150) | Decode and check the wiring sentences at startup, hold the layout and cell address tables; allocate the large buffers, sized from each adapter's panel count. Not edited per setup |
| Refresh and conversion | `isp_hub75_rgb3bit.spin2` (about 1,300), `isp_hub75_panel.spin2` (about 900) | The PASM2 refresh cog; the screen-to-PWM converter and frame-set hand-off |
| Display API | `isp_hub75_display.spin2` (about 1,900), `isp_hub75_screenUtils.spin2` (about 1,000), `isp_hub75_cube.spin2` (about 950) | Text, drawing, scrolling, face-centric drawing; pixel and run primitives; the cube fold |
| Utilities | `isp_hub75_colorUtils.spin2` (about 375), `isp_hub75_fonts.spin2` (about 6,100, mostly font data) | Color table and gamma; fonts |
| Optional | `isp_hub75_scrollingText.spin2`, `isp_hub75_display_bmp.spin2`, `isp_hub75_7seg.spin2`, `isp_hub75_segment.spin2`, `isp_hub75_instrument.spin2` | Scrolling regions, BMP loading, the 7-segment demo parts, measurement (compiled only with `HUB75_INSTRUMENT`) |
| Constants | `isp_hub75_hwEnums.spin2`, `isp_hub75_color.spin2` | Enumerations and color values |
| Demos | `demo_hub75_*.spin2` (11 files) | Example applications |
| Test top files | `test_hub75_*.spin2` (5 files) | Instrumented workload, converter equivalence, the OE-weighted method, cube fold, pin identification |

### 1.2 Module Separation Quality

**Well Separated:**
- The PASM2 refresh cog (`rgb3bit`) is isolated from the Spin2 code and is driven through four hub longs (command, argument, showing, brightness)
- Screen-to-PWM conversion (`panel`) is separate from drawing; the two meet at a posted PWM frame set
- Color utilities, font data and the cube layer each have their own file
- Every drawing path resolves its screen-buffer addresses through one rule (`mountedRuleAddress` in `hwBufferAccess`), so rotation and panel placement live in one place

**Could Be Improved:**
- `isp_hub75_hwBufferAccess.spin2` is the largest driver file and holds both the wiring-sentence decode and check and the lookup tables the drawing paths read at run time
- `isp_hub75_display.spin2` carries grid text, panel-centric, display-centric and face-centric drawing in one object

### 1.3 Configuration File Design

Panel configuration is one file, `isp_hub75_hwPanelConfig.spin2`. All three adapters are always present, and each adapter's buffers are sized at compile time from the panels its sentences name (`DISPn_PANEL_COUNT`), so an adapter with no panels costs no memory. The sentences are decoded and checked once at startup (`configureAdapter()` in `hwBufferAccess`), which prints the grid it found or the problems and stops.

**Assessment:**
- Compile-time sizing is appropriate for an embedded driver: a display too large for hub RAM does not compile
- Everything else about the layout is checked at startup rather than at compile time, which is what lets the sentences stay readable
- The constants are documented inline

---

## 2. Performance Analysis

### 2.1 Identified Bottlenecks

#### Priority 1: Pixel Clocking (CRITICAL)
**Location:** `isp_hub75_rgb3bit.spin2`, `shiftColumns`

```pasm
shiftColumns
        altgb   byteOffset, pCogBffrIncr        ' first byte of cogBuffer, index advances
        getbyte colorByte, 0-0, #0-0
        rep     @shiftEnd, columnsToShift
colorOutInst setbyte OUTA, colorByte, #OUT_RGB_BYTE_POS
        drvl    pinLedCLK                       ' CLK low
        altgb   byteOffset, pCogBffrIncr        ' next byte
        getbyte colorByte, 0-0, #0-0
        waitx   waitCyclesLow                   ' low time
        drvh    pinLedCLK                       ' rising edge clocks the data in
        waitx   waitCyclesHigh                  ' high time
shiftEnd
```

**Analysis:**
- One `rep` loop of 7 instructions puts out one byte (R1 G1 B1 R2 G2 B2) per column clock
- The loop's fixed cost is 14 system clocks (CLK high 6, low 8); two `waitx` extensions hold each half of the pulse to the chip's minimum (20 ns) and the whole period to the chip's maximum clock, which is its rating or, for the MBI5124GP, its chain limit
- Each pass fetches the next byte while the current one is clocked, so the fetch costs no extra time
- **Verdict: at the chip's clock limit; further gains need a different panel or chip**

#### Priority 2: HUB-to-COG Transfer (MEDIUM)
**Location:** `isp_hub75_rgb3bit.spin2`, `planeLoop`

```pasm
setq    rowLongsLessOne
rdlong  cogBuffer, planeHubAddr
```

**Analysis:**
- One block read loads a bit plane's row (one byte per column clock, 4 per long) into the cog's line buffer
- The load touches no pin, so it runs while the previous plane is still lit
- The line buffer is 512 bytes (128 longs, `hub75Bffrs.LINE_BUFFER_BYTES`), which limits one row along the cable to 512 column clocks (half that many columns for a SCAN_4 panel)
- **Verdict: efficient; the 512-byte buffer is the limit on chain length**

#### Priority 3: Screen-to-PWM Conversion (LOW)
**Location:** `isp_hub75_panel.spin2`, `convertRowPairs`

**Analysis:**
- Inline PASM2 reads four columns of top-half and bottom-half pixels at a time, spreads each pixel pair's channel bits across the planes with `MERGEB`, and writes each plane's long once
- It runs on the calling cog into the PWM frame set that is not on display, then posts the set; the refresh cog takes it at its next frame start
- The commit time is stated in the Wiring Guide
- **Verdict: acceptable; it is not on the refresh path**

#### Priority 4: Drawing Path
**Location:** `isp_hub75_screenUtils.spin2`, `isp_hub75_hwBufferAccess.spin2`

**Analysis:**
- Pixel addresses come from cell address tables built at startup, one lookup per pixel
- Straight runs (lines, boxes, glyph rows, BMP rows, fills) write through PASM run primitives (`fillRowRun`, `fillColumnRun`, `copyRowRun`); sloped lines and circles write through one plot context (`plotPacked`)
- Panel-centric sloped lines and single pixels and face-centric pixels still go one pixel at a time; see the punch list

### 2.2 Current Optimizations in Place

| Optimization | Location | Benefit |
|--------------|----------|---------|
| `rep` instruction | rgb3bit | Zero-overhead column loop |
| `altgb`/`getbyte`/`setbyte` | rgb3bit | One byte per column clock, fetched while the last is clocked |
| Bit-parallel output | rgb3bit | 6 color bits per instruction |
| OE-weighted bit planes | rgb3bit | Each plane shown once per row address, lit for 2^k units of /OE time through a smart pin |
| Row load overlapped with the lit plane | rgb3bit | The row load costs no panel time |
| Chip-specific latch paths | rgb3bit | Latch-at-end and overlapped latch need no test in the column loop |
| Two PWM frame sets | panel | A commit converts into the set not on display, so a half-converted image is never shown |
| `MERGEB` converter | panel | Four columns of every plane per write |
| Color table | colorUtils | Gamma and depth mapping are one table lookup per channel |
| Cell address tables, PASM runs, plot context | hwBufferAccess, screenUtils | Drawing takes addresses from tables and writes runs in PASM |

### 2.3 Frame Rate Performance

The refresh method, the target refresh rule (`DISPn_TARGET_REFRESH_HZ`), the measured rates by depth, the brightness floor and the commit and draw times are in the [Wiring Guide's refresh rate section](WiringGuide.md#refresh-rate). Those figures are measured on the author's rig; other configurations follow the same rule and have not been measured.

**Key Insight:** the rate depends on the chain length and the color depth, and the driver picks the brightest panel timing that reaches the target.

---

## 3. Findings

### 3.1 Comments to Resolve

No `FIXME` or `UNDONE` comments remain in `driver/*.spin2`.

### 3.2 Hard-Coded Limits

| Limit | Value | Where |
|-------|-------|-------|
| Scrolling regions | 4 | `MAX_SCROLLING_REGIONS` in `isp_hub75_display.spin2` |
| Panels one converter handles | 16 | `CONVERTER_MAX_PANELS` in `isp_hub75_hwBufferAccess.spin2` |
| One row along the cable | 512 column clocks | `LINE_BUFFER_BYTES` in `isp_hub75_hwBufferAccess.spin2` |
| Adapters | 3 | `ADAPTER_COUNT` in `isp_hub75_hwBufferAccess.spin2` |

The startup check in `configureAdapter()` enforces the panel limits and prints the limit that was exceeded. Hub RAM is the third limit and is enforced by the compiler.

### 3.3 Open Items

- The panel-centric clipping cost, the cube fold's call depth, the hidden face-home state, the brightness floor, the ICN2038S scan setting and the untested `showFrameSet()` accepted path are recorded in `DOCs/plans/PUNCH-LIST.md`
- API and demo items are in [Technical Debt](TECHNICAL_DEBT.md)

### 3.4 Code Quality Observations

**Positive:**
- Comprehensive header comments and PUB/PRI documentation on every file
- MIT license clearly stated
- Version history in ChangeLog.md
- The driver prints what it decoded and why it stopped, so wiring errors report themselves at startup

**Areas for Improvement:**
- `isp_hub75_display.spin2` and `isp_hub75_hwBufferAccess.spin2` are large objects
- The demos are written for 64x32 and 64x64 panels and need changes for other geometries

---

## 4. LUT RAM Opportunities

### 4.1 Current LUT RAM Status

**The refresh cog does not use its LUT RAM** (no `rdlut`/`wrlut` in `isp_hub75_rgb3bit.spin2`).

Each P2 cog has 512 longs (2KB) of LUT RAM next to its 512 longs of cog RAM. The refresh cog's code and registers sit in cog RAM; its line buffer is 128 longs.

LUT RAM access times:
- Read: 3 clock cycles (fixed)
- Write: 2 clock cycles (fixed)
- Compare to hub: 9-16 clock cycles (variable, "egg-beater" dependent)

### 4.2 Gamma and Color Tables

Gamma is not a per-pixel calculation. `isp_hub75_colorUtils.spin2` holds a 256-entry gamma curve and folds it, with the color-depth mapping, into one 256-byte color table per adapter (`fillColorTable()`); drawing looks a channel up in the table. The curve is off: `bGammaEnable` is FALSE and nothing in the tree sets it. LUT RAM would not speed this up, because the table is read by the Spin2 and PASM drawing code on the calling cog, not by the refresh cog.

### 4.3 Remaining Opportunity: Dither Patterns

**Use Case:** improve perceived color quality at lower bit depths

Ordered-dither matrices (a few hundred bytes) could sit in LUT RAM of a cog that does the screen-to-PWM conversion. Nothing in the driver does this, and conversion currently runs on the calling cog from hub RAM.

---

## 5. Recommendations Summary

### 5.1 Performance Candidates

| Item | Notes |
|------|-------|
| Clip panel-centric sloped lines and pixels once per call | See the punch list; not measured |
| Cheaper cube fold per face pixel | See the punch list; needs a six-panel bench to time |

### 5.2 Structure Candidates

| Item | Notes |
|------|-------|
| Split the wiring-sentence decode from the run-time tables in `hwBufferAccess` | Smaller objects; no behavior change |
| Make `MAX_SCROLLING_REGIONS` a configuration constant | Each region is a scroller object instance, so it costs hub RAM |
| One parameter order for panel-relative routines | See [Technical Debt](TECHNICAL_DEBT.md) TD-003 |

### 5.3 Files Affected

| File | Changes |
|------|---------|
| `isp_hub75_hwBufferAccess.spin2` | Split (structure candidate) |
| `isp_hub75_display.spin2` | Panel-centric clipping; parameter order; scroller limit |
| `isp_hub75_cube.spin2` | Cube fold cost |

---

*Document generated from codebase analysis. Validate findings with actual testing.*
