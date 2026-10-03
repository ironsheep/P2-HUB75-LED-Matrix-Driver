# P2 HUB75 LED Matrix Driver - Theory of Operations

**Document Version:** 2.0 (driver 4.0.0)  
**Date:** December 2024; brought up to the 4.0.0 display model October 2026  
**Author:** Generated from codebase analysis

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Data Flow](#2-data-flow)
3. [PWM Generation Mechanism](#3-pwm-generation-mechanism)
4. [Buffer Architecture](#4-buffer-architecture)
5. [Timing and Performance](#5-timing-and-performance)
6. [Multi-Adapter Support](#6-multi-adapter-support)
7. [Panel Chip Support](#7-panel-chip-support)

---

## 1. System Architecture Overview

The P2 HUB75 LED Matrix Driver is a multi-layered system designed to drive HUB75 RGB LED matrix panels from the Parallax Propeller 2 microcontroller. The architecture separates concerns across distinct layers, enabling flexibility in panel configurations while maintaining real-time display performance.

### 1.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  User code calls display API methods                             │
│  (demo_hub75_*.spin2 examples)                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    DISPLAY CONTROL LAYER                         │
│  isp_hub75_display.spin2 - Text, graphics, colors                │
│  isp_hub75_screenUtils.spin2 - Pixel operations                  │
│  isp_hub75_scrollingText.spin2 - Text scrolling (optional)       │
│  isp_hub75_colorUtils.spin2 - Color conversion, gamma            │
│  isp_hub75_fonts.spin2 - 5x7 and 8x8 font data                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    BUFFER MANAGEMENT LAYER                       │
│  isp_hub75_hwBufferAccess.spin2 - Wiring check, layout, tables   │
│  isp_hub75_hwBuffers.spin2 - Screen RAM allocation               │
│  isp_hub75_hwPanelConfig.spin2 - User configuration              │
│  isp_hub75_cube.spin2 - Cube faces and edge folding              │
│  isp_hub75_hwEnums.spin2 - Constants and enumerations            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    PANEL MANAGEMENT LAYER                        │
│  isp_hub75_panel.spin2 - Screen buffer to PWM conversion         │
│  Converts 24-bit RGB to PWM frame sets                           │
│  Manages double-buffering for smooth animation                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    PASM2 DRIVER LAYER (Runs in dedicated COG)    │
│  isp_hub75_rgb3bit.spin2 - Real-time PWM output                  │
│  Clocks pixel data to panel shift registers                      │
│  Manages row addressing and timing                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    HARDWARE LAYER                                │
│  P2 GPIO pins (16 pins per HUB75 adapter)                        │
│  HUB75 panel interface signals                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Object Dependencies

```
demo_hub75_*.spin2 (top-level)
    └── isp_hub75_display.spin2
            ├── isp_hub75_hwBufferAccess.spin2
            │       └── isp_hub75_hwPanelConfig.spin2
            │               └── isp_hub75_hwEnums.spin2
            ├── isp_hub75_screenUtils.spin2
            ├── isp_hub75_panel.spin2
            │       ├── isp_hub75_hwBufferAccess.spin2
            │       └── isp_hub75_rgb3bit.spin2 (PASM2 driver)
            ├── isp_hub75_fonts.spin2
            ├── isp_hub75_colorUtils.spin2
            └── isp_hub75_scrollingText.spin2[4] (optional)
```

### 1.3 Key Design Principles

1. **Separation of Concerns**: Each layer handles a specific responsibility
2. **Compile-Time Configuration**: Panel geometry and color depth resolved at compile time for efficiency
3. **Double-Buffering**: Smooth animation through alternating PWM frame sets
4. **Dedicated COG Execution**: PASM2 driver runs in its own COG for deterministic timing
5. **Multi-Adapter Support**: Up to 3 independent HUB75 adapters per P2
6. **Configure by description**: you describe where each panel is and which way it points in one sentence per panel; the driver checks the sentences at startup and derives the grid and its lookup tables once, so drawing only looks things up

---

## 2. Data Flow

### 2.1 Complete Data Path

```
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION: screen.drawPixelAtRC(chain, row, col, rgb)         │
│              Uses 24-bit color values (0x000000 - 0xFFFFFF)     │
│              (row, col) are display coordinates, as mounted     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Map to the panel's buffer slot (2.2)
                           │ Apply color correction
                           │ (gamma, brightness)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ SCREEN BUFFER (HUB RAM)                                         │
│  Format: 24-bit/pixel (3 bytes: R, G, B)                        │
│  Size: width × height × 3 bytes                                 │
│  Example: 256×128 = 98,304 bytes                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ commitScreenToPanelSet()
                           │ Bit extraction + PWM mapping
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PWM FRAME SETS (HUB RAM, Double-buffered)                       │
│  Format: 4 bits/pixel (2 pixels per byte)                       │
│  Frames: color_depth frames per set (3-bit=7, 8-bit=255)        │
│  Size: (width × height / 2) × color_depth bytes                 │
│  Example: 256×128 @ 8-bit = 131,072 bytes per set               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ cmdWritePwmBuffer() - async command
                           │ PASM2 driver reads in chunks
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PASM2 DRIVER (Running continuously in dedicated COG)            │
│                                                                  │
│  1. Read PWM subpage from HUB into COG buffer (128 longs)       │
│  2. Clock out pixels to panel row by row                        │
│  3. Set row address, latch data, enable output                  │
│  4. Repeat for all rows, all PWM frames                         │
│  5. Loop back to display next frame set                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HUB75 signals
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ HUB75 PANEL                                                     │
│  - Shift registers receive 6 color bits (R1,G1,B1,R2,G2,B2)    │
│  - Row decoder selects active row (A,B,C,D,E address lines)    │
│  - Latch transfers shift register to LED drivers               │
│  - OE (output enable) controls LED brightness                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Pixel Write Operation

Every drawing path (text, scrolling, lines, boxes, circles, image placement, panel-centric calls and face-centric calls) ends in one pixel write, `drawPixelAtRCwithRGB(chainIdx, row, col, red, green, blue)`, so every path gets the same mapping. `row` and `col` are **display coordinates as the display is mounted**, with (0, 0) at the top-left (see the [glossary](../THEOPS.md#glossary)). The panels' buffer is stored panel by panel (in buffer-slot order), not as one raster, so the write maps each pixel to its place in it:

1. **Hold to the mounted size.** The size the accessors report is the size as mounted: width and height swap when `DISPn_ROTATION` is 90 or 270 degrees.

2. **Undo the display rotation.** `DISPn_ROTATION` is physical (how the display hangs); this step turns mounted coordinates into layout coordinates, the display as its panels are laid out. `ROT_NONE` leaves them unchanged.

3. **Map to the buffer** (`displayPixelAddress`). Each step is a table lookup, built once at startup from the wiring sentences, so the per-pixel path does no searching:
   - layout coordinates → the cell of the display's grid;
   - cell → panel position (a cell that holds no panel, such as the hole in an L shape, has none, and the pixel is not drawn);
   - panel position → panel coordinates (row and column within that panel, as the viewer sees it);
   - panel rotation (the panel's arrow) → native coordinates (as the panel's own chips address it);
   - panel position → buffer slot (slot = N-1-C for the panel at cable position C of N);
   - `offset = ((((slot × panelRows) + nativeRow) × panelColumns) + nativeColumn) × bytesPerColor`.

4. **Color Correction** (`colorUtils.correctedSingleColor`):
   - Apply brightness scaling, rounded to nearest: `value = (colorValue × brightness + 128) >> 8`
   - Apply gamma correction (optional): `value = gammaTable[value]`
   - Adjust to the color depth's bit width.

5. **Buffer Write**:
   ```
   screenBuffer[offset + 0] = correctedRed
   screenBuffer[offset + 1] = correctedGreen
   screenBuffer[offset + 2] = correctedBlue
   ```

Panel-centric calls take (panel position, panel coordinates) in the viewer's frame, clip at the panel's edge, add the panel's display offset and then enter this same path. Face-centric calls on a cube fold a pixel across the cube's edges first, then enter it too.

### 2.3 Screen Commit Operation

`commitScreenToPanelSet()` triggers conversion from screen buffer to PWM frames:

1. **Select inactive PWM frameset** (double-buffer swap)
2. **For each pixel in screen buffer**:
   - Read 24-bit RGB value
   - Extract each bit of each color channel
   - Write corresponding bit to appropriate PWM frame
3. **Issue command to PASM2 driver** to display new frameset
4. **Return immediately** - driver continues displaying asynchronously

---

## 3. PWM Generation Mechanism

### 3.1 Binary-Weighted Frame Technique

The driver achieves variable brightness using **binary-weighted PWM frames**. Each bit of the color depth represents a power-of-2 display duration:

```
For 3-bit color depth (7 visible levels):
  Frame 0 (MSB): Displayed 4× (2² times)
  Frame 1:       Displayed 2× (2¹ times)  
  Frame 2 (LSB): Displayed 1× (2⁰ times)
  
  Total cycle: 7 display periods per full PWM cycle

For 8-bit color depth (255 visible levels):
  Frame 0 (MSB): Displayed 128× (2⁷ times)
  Frame 1:       Displayed 64× (2⁶ times)
  ...
  Frame 7 (LSB): Displayed 1× (2⁰ times)
  
  Total cycle: 255 display periods per full PWM cycle
```

### 3.2 PWM Frame Format

Each PWM frame stores 4 bits per pixel (2 pixels per byte):

```
Byte layout: [Pixel1: B1 G1 R1 x] [Pixel0: B0 G0 R0 x]
             Upper nibble         Lower nibble

Each nibble contains:
  Bit 3: Blue (top half of panel)
  Bit 2: Green (top half)
  Bit 1: Red (top half)
  Bit 0: Unused (or second row half in some modes)
```

### 3.3 Display Timing

The PASM2 driver continuously cycles through:

```
FOR each PWM frame (0 to color_depth-1):
    repetitions = 2^(color_depth - 1 - frame_index)
    
    FOR repetitions times:
        FOR each row address (0 to max_rows/2 - 1):
            Clock out all pixels for this row
            Set row address lines
            Latch data to LED drivers
            Enable output for calculated duration
        END FOR
    END FOR
END FOR
```

### 3.4 Color Depth Trade-offs

| Depth | Colors | PWM Frames | Relative Speed | Bytes per pixel (buffers) |
|-------|--------|------------|----------------|---------------------------|
| 3-bit | 512 | 7 | Fastest | 6 |
| 4-bit | 4,096 | 15 | Fast | 7 |
| 5-bit | 32,768 | 31 | Medium | 8 |
| 6-bit | 262,144 | 63 | Slow | 9 |
| 7-bit | 2,097,152 | 127 | Slower | 10 |
| 8-bit | 16,777,216 | 255 | Slowest | 11 |

**Note**: the screen buffer always uses 3 bytes per pixel, at every depth. The rest of each pixel's buffer space is the two PWM frame sets (N/2 bytes per pixel each), which is why a pixel costs 3 + N bytes in all (see 4.2). How often the full color cycle repeats at each depth, measured on the author's rig, is in the [Driver Details](../THEOPS.md#notes-on-driver-internals).

---

## 4. Buffer Architecture

### 4.1 Buffer Types

#### Screen Buffer
- **Purpose**: Holds user-drawn image in 24-bit RGB format
- **Format**: 3 bytes per pixel (R, G, B)
- **Location**: HUB RAM
- **Access**: Read/write by user code, read by panel manager

#### PWM Frame Sets (×2 for double-buffering)
- **Purpose**: Pre-computed PWM data for driver output
- **Format**: 4 bits per pixel, one frame per color depth bit
- **Location**: HUB RAM
- **Access**: Written by panel manager, read by PASM2 driver

#### COG Buffer
- **Purpose**: Working buffer for PASM2 driver
- **Format**: 512 bytes (128 longs), `LINE_BUFFER_BYTES`; one sub-page of whole PWM rows
- **Location**: COG RAM (driver's dedicated COG)
- **Access**: Internal to driver

### 4.2 Memory Calculation

Buffers are sized by the **number of panels in use** (`DISPn_PANEL_COUNT`, counted from the wiring sentences), not by the display's bounding box: a display with a hole in it (an L shape) holds no memory for the hole. An adapter with no panels has zero-length buffers. For a display of `panelCount` panels of `panelColumns × panelRows` pixels:

```
Panel pixels P:
  = panelColumns × panelRows

Screen Buffer Size:
  = panelCount × P × 3 bytes  (3 bytes per pixel at every depth)

PWM Frame Size (single frame):
  = (panelCount × P) / 2 bytes

PWM Frameset Size:
  = colorDepth × PWM_Frame_Size

Total PWM Memory:
  = 2 × PWM_Frameset_Size (double-buffered)

Total Memory Per Adapter:
  = Screen_Buffer + (2 × PWM_Frameset)
  = panelCount × P × (3 + colorDepth) bytes
```

The three adapters' buffers share the P2's hub RAM; the compiler stops the build if they do not fit. How many panels that allows, per panel type, is in the [Wiring Guide's driver limits](WiringGuide.md#driver-limits).

### 4.3 Memory Examples

**Example 1: one 64×64 panel, 5-bit color**
```
Screen Buffer:  1 × 4,096 × 3 = 12,288 bytes (12 KB)
PWM Frame:      4,096 / 2 = 2,048 bytes
PWM Frameset:   5 × 2,048 = 10,240 bytes (10 KB)
Total:          12 KB + (2 × 10 KB) = 32 KB   (= 4,096 × (3 + 5))
```

**Example 2: four 128×64 panels in a 2×2 grid (256×128), 8-bit color**
```
Screen Buffer:  4 × 8,192 × 3 = 98,304 bytes (96 KB)
PWM Frame:      (4 × 8,192) / 2 = 16,384 bytes
PWM Frameset:   8 × 16,384 = 131,072 bytes (128 KB)
Total:          96 KB + (2 × 128 KB) = 352 KB   (= 32,768 × (3 + 8))
```

**Example 3: an L of three 64×64 panels (a 2×2 grid with one empty cell), 6-bit color**
```
Screen Buffer:  3 × 4,096 × 3 = 36,864 bytes (36 KB)
PWM Frame:      (3 × 4,096) / 2 = 6,144 bytes
PWM Frameset:   6 × 6,144 = 36,864 bytes (36 KB)
Total:          36 KB + (2 × 36 KB) = 108 KB   (= 12,288 × (3 + 6))
```
The bounding box would be 128×128, but the buffers hold only the three panels.

### 4.4 Buffer Table Structure

The `isp_hub75_hwBufferAccess.spin2` file maintains one descriptor for each HUB75 adapter. All three are always present, and the descriptor's buffer addresses, chip type, pin base and address lines are filled in when the adapter is started (`configureAdapter`, which the display's start call makes):

```
Descriptor Structure (13 LONGs per adapter):
  [0]  Screen buffer address
  [1]  PWM frameset 1 address
  [2]  PWM frameset 2 address
  [3]  Color depth (3-8)
  [4]  Bytes per color (3)
  [5]  Screen size in longs
  [6]  PWM frame size in bytes
  [7]  Display rotation (DISPn_ROTATION, how the display is mounted)
  [8]  Panel columns (single panel width, native)
  [9]  Panel rows (single panel height, native)
  [10] Panel chip type
  [11] HUB75 pin base
  [12] Address line count (ABC/ABCD/ABCDE)
```

The display's size and grid are **not** in the descriptor. The wiring sentences are decoded and checked once at startup, and the layout derived from them lives in lookup tables, one entry per cable or panel position, per adapter:

| Table | Maps | Used for |
|---|---|---|
| panel position (layout) → buffer slot | the panel's place in the screen buffer (slot = N-1-C) | the mapping (2.2) |
| panel position (layout) → panel rotation | the panel's arrow | the mapping (2.2) |
| cell → panel position | the display's grid; a cell with no panel has none | the mapping (2.2), and which panel holds a pixel |
| panel position (as mounted) → layout position, and its cell | display rotation applied to whole panels | panel-centric calls and `fillPanel` in the viewer's frame |
| cable position → panel position | the inverse | the identify screen's `C` and `P` labels |

For a cube, `isp_hub75_cube.spin2` additionally holds the edge table: for each face, which face lies beyond each edge and how coordinates carry across it.

---

## 5. Timing and Performance

### 5.1 Refresh Rate

The refresh core shows plane *k* of an *N*-bit frame set 2^(*N*-1-*k*) times, so one full color cycle is 2^*N* - 1 scans of the display, and each scan clocks out `rows × column clocks` columns. The refresh rate is how often the full color cycle repeats:

> refresh (Hz) = clock rate ÷ (rows × column clocks × (2^*N* - 1))

where *rows* is 8, 16 or 32 for 3, 4 or 5 address lines and *column clocks* is the number of panels along the cable × their columns (× 2 for the chips the driver flags `SCAN_4`). The panel clock is `clkfreq / 20_000_000` core cycles per column, 16 cycles at 335 MHz.

**Measured** on the author's rig (four ICN2037 128x64 panels, 512 column clocks, 1/32 scan), the full color-cycle rate was 177 Hz at 3-bit, 82 Hz at 4-bit, 40.1 Hz at 5-bit, 19.7 Hz at 6-bit, 9.6 Hz at 7-bit and 4.6 Hz at 8-bit, each a little below the formula's clock-time ceiling (182.6, 85.2, 41.2, 20.3, 10.1 and 5.0 Hz). Other panel types are calculated, not measured: see the [Wiring Guide's refresh tables](WiringGuide.md#refresh-rate), which also say what the rig looked like to the eye at each depth.

### 5.2 Timing-Critical Operations

#### Pixel Clocking (HIGHEST PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2`, the column-clocking loop
- **Requirement**: 15-30 MHz clock rate depending on panel chip
- **Implementation**: Uses `rep` instruction for zero-overhead loop
- **Timing**: ~25-50ns per pixel at 335 MHz P2 clock

#### HUB-to-COG Transfer (MEDIUM PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2`, the sub-page load
- **Method**: `setq` + `rdlong` bulk transfer with auto-increment
- **Transfer Size**: up to 128 longs (512 bytes) per sub-page
- **Timing**: ~1μs per transfer

#### Row Address Change (LOW PRIORITY)
- **Location**: `emitAddr` routine
- **Operations**: Set address pins, wait for settle
- **Timing**: ~10 clock cycles per row change

### 5.3 Performance Bottlenecks

1. **PWM Frame Count** - More color depth = slower visible frame rate
2. **Panel Size** - Larger displays require more data transfer
3. **HUB Memory Bandwidth** - Shared with other COGs

### 5.4 Current Optimizations

1. **Subpage Buffering**: Splits large PWM frames into COG-sized chunks
2. **REP Instruction**: Zero-overhead pixel clocking loop
3. **ALTGB/SETBYTE**: Efficient indexed memory access
4. **Bit-Parallel Output**: 6 color bits output simultaneously
5. **Panel-Specific Code Paths**: Separate loops for different latch timing

---

## 6. Multi-Adapter Support

### 6.1 Capability

The driver supports up to **3 independent HUB75 adapters** on a single P2:

- Each adapter uses 16 GPIO pins
- Each adapter has independent configuration (panel size, chip type, color depth)
- Each adapter runs its own PASM2 driver COG

### 6.2 Pin Group Options

| Pin Group | Pins | Typical Use |
|-----------|------|-------------|
| PIN_GROUP_P0_P15 | 0-15 | Available on P2 Eval |
| PIN_GROUP_P16_P31 | 16-31 | Primary HUB75 location |
| PIN_GROUP_P32_P47 | 32-47 | Secondary HUB75 location |

There is no group for pins 48-63: they overlap the P2's reserved pins.

### 6.3 Configuration

Adapter *k* drives display `DISP(k-1)_`, configured by `DISPx_` constants in `isp_hub75_hwPanelConfig.spin2`. The panels' layout, cabling and mounting are the wiring sentences (`DISPx_C0` ... `DISPx_C15`), `DISPx_ROTATION` and, for a cube, `DISPx_SHAPE`; see the [Wiring Guide](WiringGuide.md). A 2×2 grid of 128×64 panels on the first adapter, with the adapter plugged into the bottom-left panel and the ribbon running along the bottom row and then the top row, looks like this:

```spin2
' Display 0, driven by HUB75_ADAPTER_1
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
DISP0_COLOR_DEPTH = hwEnum.DEPTH_5BIT
DISP0_ROTATION = hwEnum.ROT_NONE
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP         ' bottom-left
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP   ' bottom-right
DISP0_C2 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_UP      ' top-left
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_UP   ' top-right

' Display 1, driven by HUB75_ADAPTER_2: set every DISP1_C0 ... DISP1_C15 to
' hwEnum.NO_PANEL until it has panels
```

### 6.4 Enabling Additional Adapters

All three adapters are always present in `isp_hub75_hwBufferAccess.spin2` and `isp_hub75_hwBuffers.spin2`, and nothing in those files is edited. An adapter whose `DISPx_C0` is `NO_PANEL` has zero-length buffers and costs no memory. To use another adapter:

1. **In `isp_hub75_hwPanelConfig.spin2`**: describe the panels of `DISP1_` (second adapter) or `DISP2_` (third adapter): pin group, chip, address lines, panel size, color depth, and the wiring sentences.
2. **In your program**: start it with its own display object, `display[1].start(hub75Bffrs.HUB75_ADAPTER_2)` (or `HUB75_ADAPTER_3`). Each adapter runs its own display object and refresh COG.

The startup check halts with a message if a display that is started has no panels, or if the combined buffers of all three adapters do not fit hub RAM (the compiler reports the second). See the [upgrade checklist](../Checklist-v3-v4.md#starting-a-second-or-third-adapter) for the call sequence.

---

## 7. Panel Chip Support

### 7.1 Supported Chips

| Chip | Address Lines | Max Clock | Multi-Panel | Notes |
|------|---------------|-----------|-------------|-------|
| ICN2037 | ABCDE | 30 MHz | Yes | P2 Cube panels |
| ICN2037BP | ABCDE | 30 MHz | Yes | Variant |
| ICN2038S | ABCDE | 30 MHz | Yes | Renamed from ICN2037_B |
| FM6126A | ABCD | 30 MHz | Yes | Requires init sequence |
| FM6124 | ABCD | 30 MHz | Single only | |
| DP5125D | ABC | TBD | Yes | |
| GS6238S | ABCD | TBD | Single only | Green/Blue swap |
| MBI5124GP | ABC | 25 MHz | Single only | 1/8 scan |

### 7.2 Chip-Specific Features

**Latch Timing Modes**:
- **Latch-After**: Standard mode - latch after all columns clocked (most panels)
- **Latch-Overlap**: FM6126A - latch overlaps with final columns

**Color Channel Swapping**:
- Some panels require Red/Blue swap or Green/Blue swap
- Configured via chip type selection

**Scan Modes** (the [glossary](../THEOPS.md#scan) defines the term: a panel is **1/S scan**, where S is the number of row addresses its address lines select, and each address lights panel rows ÷ S rows at once):
- Standard: two rows lit at once, one fed by each set of color pins: 1/16 scan on a 64x32 panel, 1/32 scan on a 64x64 or 128x64 panel
- Special: four rows lit at once, flagged `SCAN_4` (MBI5124GP and DP5125D, 1/8 scan on a 64x32 panel) - requires a different screen-to-panel conversion, and the refresh line holds two column clocks for every panel column
- ICN2038S: the driver flags it `SCAN_4`, but its five address lines suggest 1/32 scan; this is an open item (see the Change Log's Known Issues) and the panel's scan is **disputed** until it is settled

### 7.3 Adding New Chip Support

1. Add chip constant to `isp_hub75_hwEnums.spin2`
2. Update `isp_hub75_rgb3bit.spin2` with chip-specific timing if needed
3. Update `isp_hub75_panel.spin2` if special scan pattern required
4. Test and measure with logic analyzer

---

## Appendix: HUB75 Pin Mapping

Standard HUB75E pinout on P2 adapter:

| Pin Offset | Signal | Description |
|------------|--------|-------------|
| +0 | R1 | Red data, top half |
| +1 | G1 | Green data, top half |
| +2 | B1 | Blue data, top half |
| +3 | R2 | Red data, bottom half |
| +4 | G2 | Green data, bottom half |
| +5 | B2 | Blue data, bottom half |
| +6 | A | Row address bit 0 |
| +7 | B | Row address bit 1 |
| +8 | C | Row address bit 2 |
| +9 | D | Row address bit 3 |
| +10 | E | Row address bit 4 |
| +11 | CLK | Pixel clock |
| +12 | LAT | Latch data |
| +13 | OE | Output enable (active low) |
| +14-15 | Reserved | Future use |

---

*Document generated from codebase analysis. Refer to source files for implementation details.*
