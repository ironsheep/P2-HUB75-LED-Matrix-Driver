# P2 HUB75 LED Matrix Driver - Theory of Operations

**Document Version:** 2.1 (driver 4.0.0)  
**Date:** October 2026  
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
│  isp_hub75_display.spin2 - Text, graphics, scrolling, commit     │
│  isp_hub75_screenUtils.spin2 - Pixel, run and block writes       │
│  isp_hub75_scrollingText.spin2 - Text scrolling regions          │
│  isp_hub75_colorUtils.spin2 - Color table, gamma, color math     │
│  isp_hub75_fonts.spin2 - 5x7, 8x8 and dithered 5x7 font data     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    BUFFER MANAGEMENT LAYER                       │
│  isp_hub75_hwBufferAccess.spin2 - Wiring check, layout, cell     │
│     address tables, window watch                                 │
│  isp_hub75_hwBuffers.spin2 - Screen and frame set RAM            │
│  isp_hub75_hwPanelConfig.spin2 - User configuration              │
│  isp_hub75_cube.spin2 - Cube faces and edge folding              │
│  isp_hub75_hwEnums.spin2 - Constants and enumerations            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    PANEL MANAGEMENT LAYER                        │
│  isp_hub75_panel.spin2 - Screen buffer to PWM conversion         │
│  Converts 24-bit RGB to PWM frame sets                           │
│  Converts into the frame set not on display, then posts it       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    PASM2 DRIVER LAYER (Runs in dedicated COG)    │
│  isp_hub75_rgb3bit.spin2 - Real-time refresh (the refresh cog)   │
│  Clocks pixel data to panel shift registers                      │
│  Manages row addressing, latching and /OE-weighted bit planes    │
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
            │       ├── isp_hub75_hwPanelConfig.spin2
            │       │       └── isp_hub75_hwEnums.spin2
            │       ├── isp_hub75_hwBuffers.spin2
            │       └── isp_hub75_cube.spin2
            ├── isp_hub75_screenUtils.spin2
            │       ├── isp_hub75_colorUtils.spin2
            │       └── isp_hub75_fonts.spin2 (dithered pixel codec)
            ├── isp_hub75_panel.spin2
            │       ├── isp_hub75_hwBufferAccess.spin2
            │       └── isp_hub75_rgb3bit.spin2 (PASM2 refresh cog)
            ├── isp_hub75_fonts.spin2
            ├── isp_hub75_colorUtils.spin2
            ├── isp_hub75_cube.spin2
            └── isp_hub75_scrollingText.spin2[4] (four scrolling regions)

isp_hub75_display_bmp.spin2 (optional) is used by the program that loads a .bmp
```

### 1.3 Key Design Principles

1. **Separation of Concerns**: Each layer handles a specific responsibility
2. **Compile-Time Configuration**: the panel count, color depth and buffer sizes are fixed at compile time from the `DISPn_` settings, so the buffers are sized to the panels in use
3. **Tear-free commit**: a commit converts into the PWM frame set that is not on display and the refresh cog switches to it at a frame start (see 2.3)
4. **Dedicated COG Execution**: PASM2 driver runs in its own COG for deterministic timing
5. **Multi-Adapter Support**: Up to 3 independent HUB75 adapters per P2
6. **Configure by description**: you describe where each panel is and which way it points in one sentence per panel; the driver checks the sentences at startup and derives the grid, its lookup tables and the cell address tables once, so drawing only looks things up

---

## 2. Data Flow

### 2.1 Complete Data Path

```
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION: a display call (text, line, box, circle, scroll),  │
│              or screenUtils.drawPixelAtRC(chain, row, col, rgb) │
│              Uses 24-bit color values (0x000000 - 0xFFFFFF)     │
│              (row, col) are display coordinates, as mounted     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Look up the pixel's (or run's) address
                           │ in the cell address tables (2.2)
                           │ Apply color correction: one color
                           │ table read per channel (gamma, depth)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ SCREEN BUFFER (HUB RAM)                                         │
│  Format: 24-bit/pixel (3 bytes: R, G, B)                        │
│  Size: panels in use × panel pixels × 3 bytes                   │
│  Example: 256×128 = 98,304 bytes                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ display.commitScreenToPanelSet()
                           │ Bit extraction + PWM mapping
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PWM FRAME SETS (HUB RAM, two per adapter)                       │
│  Format: one byte per column clock (top and bottom pixel)       │
│  Frames: color_depth frames per set, one per bit plane          │
│  Size: (panels × panel pixels / 2) × color_depth bytes          │
│  Example: 256×128 @ 8-bit = 131,072 bytes per set               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ cmdWritePwmBuffer() - async command
                           │ taken by the refresh cog at a frame start
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PASM2 DRIVER (Running continuously in dedicated COG)            │
│                                                                  │
│  1. At a frame start, take the posted set; read the brightness  │
│  2. For each row address, for each bit plane (MSB first):       │
│     load the plane's row from HUB into the COG buffer          │
│  3. Clock out the row, set the row address, latch               │
│  4. Pulse /OE for 2^k × L clocks (the plane's weight)           │
│  5. Load and shift the next plane while this one is lit         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HUB75 signals
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ HUB75 PANEL                                                     │
│  - Shift registers receive 6 color bits (R1,G1,B1,R2,G2,B2)    │
│  - Row decoder selects active row (A,B,C,D,E address lines)    │
│  - Latch transfers shift register to LED drivers               │
│  - OE (output enable) sets how long each plane is lit           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Pixel Write Operation

Every drawing path (text, scrolling, lines, boxes, circles, image placement, panel-centric calls and face-centric calls) finds where a pixel goes through one rule, so every path gets the same mapping. `row` and `col` are **display coordinates as the display is mounted**, with (0, 0) at the top-left (see the [glossary](../THEOPS.md#glossary)). The panels' buffer is stored panel by panel (in buffer-slot order), not as one raster, so the rule maps each pixel to its place in it.

The rule is not worked out per draw. `hwBufferAccess` evaluates it once, at startup, into the **cell address tables** (below), and every drawing call reads its addresses from them:

- A single pixel is written by `drawPixelAtRCwithRGB(chainIdx, row, col, red, green, blue)` (or `drawPixelAtRC` with a 24-bit color) in `screenUtils`; its address is `pixelAddressAtRC(chainIdx, row, col)`, which is one lookup.
- A straight run of pixels (a line, a box row or column, a glyph row, a BMP row, a fill) is written by the run primitives `fillRowRun`, `fillColumnRun` and `copyRowRun`: they split the run where it crosses from one panel to the next and, for each panel, take the start address and the step between pixels from one `mountedPixelRun` lookup, then write the pixels in PASM. A run lands exactly where its pixels would one by one.
- A filled box in one color is written as one block per panel it covers (`fillMountedArea`, `mountedBlockRun`), rows in PASM.
- A scrolling-text glyph (or the gap after it) that lies wholly inside one panel is written as one block: one lookup for its top-left pixel and its two steps (`mountedBlockRun`), then every row in one PASM call (`copyGlyphBlock`, `copyGlyphRows`).
- A sloped line or a circle in one color is plotted pixel by pixel through one **plot context**: `plotContext` hands PASM the table addresses and sizes once per shape, and `plotPacked` writes each pixel from them in PASM.
- A fill of a rectangle in layout coordinates (`fillLayoutArea`, used by the panel fills) is written row by row as runs that take their addresses from `displayPixelAddress` directly, since layout coordinates are not placed as mounted.

The rule itself, for a pixel of the display as mounted (steps 1 to 3 are evaluated at startup, into the tables; steps 4 and 5 happen on every write):

1. **Hold to the mounted size.** The size the accessors report is the size as mounted: width and height swap when `DISPn_ROTATION` is 90 or 270 degrees.

2. **Undo the display rotation** (`mountedRuleAddress`). `DISPn_ROTATION` is physical (how the display hangs); this step turns mounted coordinates into layout coordinates, the display as its panels are laid out. `ROT_NONE` leaves them unchanged.

3. **Map to the buffer** (`displayPixelAddress`). Each step is a table lookup, built once at startup from the wiring sentences, so this step does no searching:
   - layout coordinates → the cell of the display's grid;
   - cell → panel position (a cell that holds no panel, such as the hole in an L shape, has none, and the pixel is not drawn);
   - panel position → panel coordinates (row and column within that panel, as the viewer sees it);
   - panel rotation (the panel's arrow) → native coordinates (as the panel's own chips address it);
   - panel position → buffer slot (slot = N-1-C for the panel at cable position C of N);
   - `offset = ((((slot × panelRows) + nativeRow) × panelColumns) + nativeColumn) × bytesPerColor`.

4. **Color Correction** (`colorUtils.packedCorrectedColor`, `packedCorrectedRgb`, `correctedSingleColor`): one read of the adapter's 256-entry color table per channel; the table is built at adapter start (`buildColorTable`). The table holds, for each 8-bit input, the stored value: the gamma curve if gamma is enabled (it is off unless `bGammaEnable` in `isp_hub75_colorUtils.spin2` is set), then the mapping to the color depth's bit width. A color is corrected once per call, and a run or shape is corrected once and packed (red in bits 0-7, green 8-15, blue 16-23) before its pixels are written. Brightness is not applied to the values: it is /OE time, set in the refresh core (see 5.1).

5. **Buffer Write**:
   ```
   screenBuffer[offset + 0] = correctedRed
   screenBuffer[offset + 1] = correctedGreen
   screenBuffer[offset + 2] = correctedBlue
   ```

**Evaluated once per panel, not per pixel.** Steps 1 to 3 are the rule; the drawing path does not evaluate them for every pixel. Within one panel the rule is a fixed rotation of the panel's native rows and columns, so at startup `hwBufferAccess` (`buildCellAddressTables`, after the mounted grid is built) evaluates the rule at three pixels of each cell of the mounted grid (the cell's first pixel, its right neighbour and the pixel below) and keeps the **cell address tables**: the offset of the cell's first pixel from the start of the screen buffer, the step to the pixel at its right and the step to the pixel below it. A pixel's address is then `buffer + offset + (row in cell × down step) + (column in cell × right step)`: one lookup (`mountedPixelAddress`, or `mountedPixelRun` with the steps, or `mountedBlockRun` for a block inside one cell). A cell with no panel has no offset (`NO_CELL_OFFSET`), and its pixels are not drawn. The run writes, and the rows of a glyph block, are written in PASM. The instrument build's self-test (`test_hub75_rates.spin2`) compares the tables with a frozen copy of the rule at every cell edge, and compares every run and block drawing with a pixel-by-pixel reference.

**Scrolling moves the last frame.** A display-centric scrolling region in one colour registers its window with the **window watch** in `hwBufferAccess` (`watchWindow`). Every drawing call reports the rectangle it writes (`noteDrawn`; a clear, a fill or a layout-coordinate write reports the whole display, `noteAllDrawn`), and the watch marks dirty each window that rectangle meets, except the window of the region drawing at that moment (`setDrawingOwner`). The watch holds up to 16 windows across all adapters. On a step whose scroll state is exactly one pixel on from the frame drawn last, a clean window is moved one pixel (`shiftRowLeft`, `shiftRowRight`, `shiftRowsUp`, `shiftRowsDown`, in PASM) and only the new edge column or row is drawn from the text. A dirty window, the first step, a step that wraps the text or the glyph rows, and a font change draw the whole window instead, so a step always shows what drawing the whole window would show. Setting a region's loop mode (`configureScrollLoopMode`, `configureScrollLoopCount`) draws its window again for that mode, since the mode decides what a sideways window shows past the text (the text again, or spaces in `SCROLL_ONCE_TO_CLEAR`) and the first window is drawn before the mode is set. A program that writes the screen buffer directly, past the driver's calls, calls `noteAllDrawn` afterwards. The instrument build's self-test compares every scroll case, a scroll with a box drawn over it and the buffer cleared between steps, and a left scroll whose `SCROLL_ONCE_TO_CLEAR` mode is set after it starts, with a reference that draws every step's whole window pixel by pixel.

Panel-centric calls take (panel position, panel coordinates) in the viewer's frame, clip at the panel's edge, add the panel's display offset and then enter this same path. Face-centric calls on a cube fold a pixel across the cube's edges first, then enter it too.

### 2.3 Screen Commit Operation

`display.commitScreenToPanelSet()` triggers conversion from screen buffer to PWM frames. It calls `convertScreen2PWM_14()` for a chip flagged `SCAN_4` and `convertScreen2PWM()` for every other chip (both in `isp_hub75_panel.spin2`):

1. **Wait for the previous post to be taken.** The refresh cog names the frame set it is showing in `driverShowing` at each frame start. Before converting again, the commit waits until `driverShowing` is the set it posted last (within one refresh), so the set it is about to write is never the set on display. The first commit after start has nothing to wait for.
2. **Select the PWM frame set that is not on display** (the one `driverShowing` does not name).
3. **For each group of four columns**: block-read the four top-half and four bottom-half pixels, spread each pixel pair's channel bits across the bit planes with `MERGEB`, collect the four columns' plane bytes in one long per plane, and write each plane's long once. The chip's red/blue or green/blue channel swap (`RB_SWAP`, `GB_SWAP`) is applied to each pixel's bytes on the way in (`channelOrder()`). Half-scan and quarter-scan panels share this converter; only where each row lands in the frame set differs. Panel widths are a multiple of 4 columns (checked at startup). On the author's four-panel rig a commit takes 4.09 ms at 8-bit and 3.26 ms at 5-bit.
4. **Post the converted set** to the PASM2 driver with `cmdWritePwmBuffer()`.
5. **Return immediately** - the driver takes the set at its next frame start and continues displaying asynchronously, so the panels never show a half-converted image.

`display.showFrameSet(pFrameSet)` posts a frame set the caller built, by the same rule. It accepts only one of the adapter's two sets (build into the one that is not on display) and refuses NULL and any other address with a message naming the call. The layout is in its doc comment: plane-major, most significant bit first, row-major, one byte per column clock.

---

## 3. PWM Generation Mechanism

### 3.1 Binary-Weighted Frame Technique

The driver achieves variable brightness using **binary-weighted bit planes**: it is binary-coded (bit-angle) modulation with output-enable weighting. A frame set holds one frame (bit plane) for each bit of the color depth. Each plane is shifted into the panels **once** per row address and lit for a time proportional to its bit weight, the /OE unit T times 2^*k*:

```
For 3-bit color depth (7 levels):
  Plane 0 (MSB): lit for 4 units (2²)
  Plane 1:       lit for 2 units (2¹)
  Plane 2 (LSB): lit for 1 unit  (2⁰)

For 8-bit color depth (255 levels):
  Plane 0 (MSB): lit for 128 units (2⁷)
  Plane 1:       lit for 64 units  (2⁶)
  ...
  Plane 7 (LSB): lit for 1 unit    (2⁰)
```

The unit T is chosen at startup from the target refresh rate (`DISPx_TARGET_REFRESH_HZ`); [the Wiring Guide](WiringGuide.md#refresh-rate) gives the rule and the measured results.

### 3.2 PWM Frame Format

Each plane of a frame set stores one byte per column clock, in the order the panel is shifted. The byte carries two pixels, the one in the top half of the panel and the one in the bottom half:

```
Byte layout: %00 B2 G2 R2 B1 G1 R1

  Bits 0-2: red, green, blue of the first pixel (R1 G1 B1 pins)
  Bits 3-5: red, green, blue of the second pixel (R2 G2 B2 pins)
  Bits 6-7: unused
```

The planes follow one another, plane 0 (the most significant bit) first, and within a plane the bytes are row-major.

### 3.3 Display Timing

The PASM2 driver continuously cycles through:

```
FOR each frame (take the posted frame set, read the brightness):
    FOR each row address (0 to scan_rows - 1):
        FOR each PWM plane k, most significant first:
            Load the plane's row for this address from HUB
              (while the previous plane may still be lit)
            Shift the row out, latch it, set the row address
              (the address changes only while /OE is off)
            Pulse /OE for 2^k × L clocks, inside a slot of 2^k × T
        END FOR
    END FOR
END FOR
```

L is T × brightness / 256, never below the chip's shortest /OE pulse (see 5.1).

### 3.4 Color Depth Trade-offs

| Depth | Colors | Levels (2^N - 1) | Bytes per pixel (buffers) |
|-------|--------|------------------|---------------------------|
| 3-bit | 512 | 7 | 6 |
| 4-bit | 4,096 | 15 | 7 |
| 5-bit | 32,768 | 31 | 8 |
| 6-bit | 262,144 | 63 | 9 |
| 7-bit | 2,097,152 | 127 | 10 |
| 8-bit | 16,777,216 | 255 | 11 |

**Note**: the screen buffer always uses 3 bytes per pixel, at every depth. The rest of each pixel's buffer space is the two PWM frame sets (N/2 bytes per pixel each), which is why a pixel costs 3 + N bytes in all (see 4.2). The default depth is 8-bit. The refresh rate at each depth, measured on the author's rig, is in the [Wiring Guide](WiringGuide.md#refresh-rate).

---

## 4. Buffer Architecture

### 4.1 Buffer Types

#### Screen Buffer
- **Purpose**: Holds user-drawn image in 24-bit RGB format
- **Format**: 3 bytes per pixel (R, G, B)
- **Location**: HUB RAM
- **Access**: Read/write by user code, read by panel manager

#### PWM Frame Sets (two per adapter)
- **Purpose**: Pre-computed PWM data for driver output. One set is on display while a commit converts into the other, then they trade roles
- **Format**: one byte per column clock (two pixels), one frame per color depth bit
- **Location**: HUB RAM
- **Access**: Written by panel manager (never the set on display), read by PASM2 driver

#### COG Buffer
- **Purpose**: Working buffer for PASM2 driver
- **Format**: 512 bytes (128 longs), `LINE_BUFFER_BYTES`; one row of one bit plane for the whole chain
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
  = 2 × PWM_Frameset_Size (one on display, one converted into)

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
Descriptor Structure (14 LONGs per adapter):
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
  [13] Refresh target in Hz (DISPn_TARGET_REFRESH_HZ)
```

The display's size and grid are **not** in the descriptor. The wiring sentences are decoded and checked once at startup (at most 16 cable positions per adapter), and the layout derived from them lives in lookup tables, one entry per cable or panel position, per adapter:

| Table | Maps | Used for |
|---|---|---|
| panel position (layout) → buffer slot | the panel's place in the screen buffer (slot = N-1-C) | the mapping (2.2) |
| panel position (layout) → panel rotation | the panel's arrow | the mapping (2.2) |
| cell → panel position | the display's grid; a cell with no panel has none | the mapping (2.2), and which panel holds a pixel |
| panel position (as mounted) → layout position, and its cell | display rotation applied to whole panels | panel-centric calls and `fillPanel` in the viewer's frame |
| cable position → panel position | the inverse | the identify screen's `C` and `P` labels |
| mounted cell → screen-buffer offset, right step, down step | the **cell address tables** (`mountedCellOffset`, `mountedCellRightStep`, `mountedCellDownStep`), built from the one address rule at startup; up to 72 cells per adapter | every pixel, run, block and plot (2.2) |
| watched window slot → rectangle, adapter, dirty flag | the window watch: up to 16 windows over all adapters | scrolling regions moving the last frame (2.2) |

For a cube, `isp_hub75_cube.spin2` additionally holds the edge table: for each face, which face lies beyond each edge and how coordinates carry across it.

---

## 5. Timing and Performance

### 5.1 Refresh Rate

The refresh core shows each bit plane once per row address and lights it for 2^*k* × L clocks of /OE inside a slot of 2^*k* × T clocks, where T is the /OE unit and L = T × brightness ÷ 256. The next plane is loaded and shifted while the current plane is lit, and the row address changes only while /OE is off. The refresh rate is how often every row address has been shown with every plane.

You set the rate you want with `DISPx_TARGET_REFRESH_HZ` (default 60). At startup the driver finds S, the clocks to shift one row of one plane, and picks the smallest *j* for which T = S ÷ 2^*j* (never below the chip's shortest /OE pulse) reaches the target. A smaller *j* means a longer T and a brighter picture; if no *j* reaches the target, the driver runs at its fastest rate and prints it. Brightness changes L and not T, so the refresh rate does not depend on it, and the image keeps its full color depth at any brightness; the lowest brightness is the chip's shortest /OE pulse. Startup stops with a message if T would be longer than 65,535 clocks, the limit of the cog's brightness multiply.

In the refresh cog, /OE is a smart pin in pulse mode with a one-clock base period: writing the plane's lit time (2^*k* × L clocks) to the pin starts one pulse, the pin idles blank, and the plane's slot is timed with the cog's CT1 event. Before the next plane's latch, and so before any row address change, the cog waits until the slot is over and the pulse has ended. Brightness 0 never starts a pulse. The brightness is read once per frame (one value shared by every adapter's cog).

The method, the full target rule, the clock, the measured rates by depth, the brightness floor and the commit and draw times are in the [Wiring Guide's refresh rate section](WiringGuide.md#refresh-rate). On the author's rig (four ICN2037 128x64 panels) the default target gives 71.0 Hz at 8-bit and 84.7 Hz at 5-bit.

The method is the binary-coded (bit-angle) modulation with output-enable weighting that is widely used for these panels.

### 5.2 Timing-Critical Operations

#### Pixel Clocking (HIGHEST PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2`, the column-clocking loop (`shiftColumns`)
- **Requirement**: each half of the CLK pulse at least 20 ns, and the period no shorter than the chip's highest allowed clock: its rated clock (30 MHz for FM6124, FM6126A, ICN2037 and ICN2038S; 25 MHz for the MBI5124GP; 20 MHz for a chip with no rating in the driver's table, which today are DP5125D, GS6238S and the unnamed chip types) or, when lower, its chain limit, one over the CLK-to-SDO delay plus the SDI setup time (ICN2037 25 MHz, ICN2038S 28.6 MHz, MBI5124GP 18.9 MHz); the ratings are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings). The FM6124 and FM6126A chain delays have not been read, so their rating alone applies
- **Implementation**: `shiftColumns` uses the `rep` instruction for a zero-overhead loop; its two `WAITX` extensions are set at startup (`columnLoopClocks`) from the system clock and the chip's limit
- **Timing**: on the author's rig (ICN2037), 15 system clocks per column at 335 MHz, with CLK high 7 clocks (20.9 ns) and low 8 (23.9 ns); for MBI5124GP panels at 335 MHz, 18 clocks (18.6 MHz)

#### HUB-to-COG Transfer (MEDIUM PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2`, the row load
- **Method**: `setq` + `rdlong` bulk transfer with auto-increment
- **Transfer Size**: one row of one bit plane for the whole chain, up to 128 longs (512 bytes)

#### Row Address Change (LOW PRIORITY)
- **Location**: `emitAddress` routine
- **Operations**: Set the row address pins while the panel is dark, then wait a few ticks for the address to settle

### 5.3 Performance Bottlenecks

1. **Color depth and chain length** - Each plane is shifted once per row address, so more planes or more column clocks lengthen the row; a target the display cannot reach is run at the fastest rate it has
2. **Panel Size** - Larger displays require more data transfer
3. **HUB Memory Bandwidth** - Shared with other COGs

### 5.4 Current Optimizations

1. **Row-at-a-time loading**: one row of one plane is loaded into the COG buffer, and the next plane loads and shifts while the current one is lit
2. **REP Instruction**: Zero-overhead pixel clocking loop
3. **ALTGB/SETBYTE**: Efficient indexed memory access
4. **Bit-Parallel Output**: 6 color bits output simultaneously
5. **Panel-Specific Code Paths**: Separate loops for different latch timing
6. **Color table, cell address tables and PASM writes**: correction is one table read per channel, a pixel's address is one table lookup, and lines, boxes, text rows, BMP rows and fills write a run of pixels per panel in PASM; a glyph or a filled box inside one panel is one block; sloped lines and circles plot through one plot context; scrolling text moves the last frame and draws only the new edge
7. **`MERGEB` converter**: a pixel pair's bits are spread across the planes with `MERGEB`, and four columns' plane bytes go out as one `WRLONG` per plane. The planes of a column all sit in one hub slice, so one byte write per plane would wait a full hub rotation each

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
DISP0_COLOR_DEPTH = hwEnum.DEPTH_8BIT
DISP0_ROTATION = hwEnum.ROT_NONE
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP         ' bottom-left
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP   ' bottom-right
DISP0_C2 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_UP      ' top-left
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_UP   ' top-right
' DISP0_C4 through DISP0_C15 = hwEnum.NO_PANEL, one per line: the unused cable positions
DISP0_SHAPE = hwEnum.SHAPE_FLAT
DISP0_TARGET_REFRESH_HZ = 60

' Display 1, driven by HUB75_ADAPTER_2: set every DISP1_C0 ... DISP1_C15 to
' hwEnum.NO_PANEL until it has panels
```

### 6.4 Enabling Additional Adapters

All three adapters are always present in `isp_hub75_hwBufferAccess.spin2` and `isp_hub75_hwBuffers.spin2`, and nothing in those files is edited. An adapter whose `DISPx_C0` is `NO_PANEL` has zero-length buffers and costs no memory. To use another adapter:

1. **In `isp_hub75_hwPanelConfig.spin2`**: describe the panels of `DISP1_` (second adapter) or `DISP2_` (third adapter): pin group, chip, address lines, panel size, color depth, and the wiring sentences.
2. **In your program**: give each adapter its own display object (`display[2] : "isp_hub75_display"`) and start it with its adapter ID, `display[1].startWithId(1, display.HUB75_ADAPTER_2)` (or `HUB75_ADAPTER_3`); `startWithId` is `start` plus a number that labels the adapter's debug messages. Each adapter runs its own display object and refresh COG, and each display commits its own screen buffer. Brightness is the one setting shared by all adapters.

The startup check halts with a message if a display that is started has no panels, or if the combined buffers of all three adapters do not fit hub RAM (the compiler reports the second). See the [upgrade checklist](../Checklist-v3-v4.md#starting-a-second-or-third-adapter) for the call sequence.

---

## 7. Panel Chip Support

### 7.1 Supported Chips

| Chip | Address Lines | Driver flags | Notes |
|------|---------------|--------------|-------|
| ICN2037 | ABCDE | `RB_SWAP` | P2 Cube panels |
| ICN2038S | ABCDE | `SCAN_4` | |
| FM6126A | ABCD | `LAT_STYLE_OFFSET`, `LAT_POSN_OVERLAP`, `INIT_PANEL_REQUIRED` | Register init at startup |
| FM6124 | ABCD | none | |
| DP5125D | ABC | `LAT_STYLE_OFFSET`, `LAT_POSN_OVERLAP`, `SCAN_4` | |
| GS6238S | ABCD | `LAT_STYLE_OFFSET`, `LAT_POSN_OVERLAP`, `GB_SWAP` | Green/Blue swap |
| MBI5124GP | ABC | `SCAN_4`, `INIT_PANEL_REQUIRED` | 1/8 scan; configuration-register init at startup |

The driver flags are the ones `hwBufferAccess.getDriverFlags()` gives each chip; a chip not in the table is described as `CHIP_MANUAL_SPEC` ORed with flags. The address lines are the reference list in `isp_hub75_hwPanelConfig.spin2`. Which chips and chain lengths have been run on panels is in the [Change Log](../ChangeLog.md)'s Known Issues, and each chip's datasheet clock and /OE ratings are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings).

### 7.2 Chip-Specific Features

**Latch Timing Modes**:
- **Latch at end**: Standard mode - all columns are clocked, the previous plane is waited dark, the row address is set, then LATCH is pulsed. With **enclosed** style (the default: ICN2037, ICN2038S, FM6124, MBI5124GP) a short settle gap follows LATCH before /OE lights the row; with **offset** style (`LAT_STYLE_OFFSET`) there is none
- **Latch-Overlap** (`LAT_POSN_OVERLAP`): FM6126A, GS6238S and DP5125D - LATCH is high over the last 3 columns, so all but the last 3 columns are shifted first and the row address changes after the latch

**Color Channel Swapping**:
- Some panels require Red/Blue swap or Green/Blue swap
- Configured via chip type selection; the converter applies it to each pixel's bytes while it spreads them across the bit planes

**Panel Initialization** (`INIT_PANEL_REQUIRED`; runs once in `start()`, before the refresh cog owns the pins):
- **FM6126A**: writes control registers 11 and 12 across the whole chain
- **MBI5124GP**: writes the configuration register of every chip in the chain. Each chip takes 16 bits, one per output, and each LED color has its own register value (`MBI5124_CFG_RED`, `MBI5124_CFG_GREEN`, `MBI5124_CFG_BLUE` in `isp_hub75_rgb3bit.spin2`, swapped between red and blue when the chip's channel swap applies). The value is shifted in MSB first, repeated every 16 stages along the chain (twice the panel columns for `SCAN_4`), on all three color lines at once; then LATCH is held high across four CLK rising edges (the write-configuration command)

**Scan Modes** (the [glossary](../THEOPS.md#scan) defines the term: a panel is **1/S scan**, where S is the number of row addresses its address lines select, and each address lights panel rows ÷ S rows at once):
- Standard: two rows lit at once, one fed by each set of color pins: 1/16 scan on a 64x32 panel, 1/32 scan on a 64x64 or 128x64 panel
- Special: four rows lit at once, flagged `SCAN_4` (MBI5124GP and DP5125D, 1/8 scan on a 64x32 panel) - uses the same converter as the standard scans (`convertRowPairs()`), which differs only in where each row lands in the frame set, and the refresh line holds two column clocks for every panel column
- ICN2038S: the driver flags it `SCAN_4`, but its five address lines suggest 1/32 scan; this is an open item (see the Change Log's Known Issues) and the panel's scan is **disputed** until it is settled

### 7.3 Adding New Chip Support

1. Add chip constant to `isp_hub75_hwEnums.spin2`
2. Give the chip its flags in `getDriverFlags()` in `isp_hub75_hwBufferAccess.spin2`
3. Give the chip its clock rating and shortest /OE pulse in `isp_hub75_rgb3bit.spin2` (`columnLoopClocks()` and `oeMinimumClocks()`; a chip with no rating there is held to 20 MHz and a 50 ns /OE pulse, and says so at startup), and an init routine if it needs one
4. Update `isp_hub75_panel.spin2` if a special scan pattern is required
5. Test and measure with logic analyzer

---

## Appendix: HUB75 Pin Mapping

Pins the refresh cog drives, as offsets from the adapter's first pin (`PIN_OFST_*` in `isp_hub75_rgb3bit.spin2`):

| Pin Offset | Signal | Description |
|------------|--------|-------------|
| +0 | CLK | Pixel clock |
| +1 | OE | Output enable (active low); a smart pin in pulse mode |
| +2 | LAT | Latch data |
| +3 | A | Row address bit 0 |
| +4 | B | Row address bit 1 |
| +5 | C | Row address bit 2 |
| +6 | D | Row address bit 3 (ABCD and ABCDE panels) |
| +7 | E | Row address bit 4 (ABCDE panels) |
| +8 | R1 | Red data, top half |
| +9 | G1 | Green data, top half |
| +10 | B1 | Blue data, top half |
| +11 | R2 | Red data, bottom half |
| +12 | G2 | Green data, bottom half |
| +13 | B2 | Blue data, bottom half |
| +14-15 | Not used | |

The color bits are the byte `%00 B2 G2 R2 B1 G1 R1` that each column clock writes to +8 to +13.

---

*Document generated from codebase analysis. Refer to source files for implementation details.*
