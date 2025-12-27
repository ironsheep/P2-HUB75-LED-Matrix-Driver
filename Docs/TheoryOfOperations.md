# P2 HUB75 LED Matrix Driver - Theory of Operations

**Document Version:** 1.0  
**Date:** December 2024  
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
│  isp_hub75_hwBufferAccess.spin2 - Buffer tables, geometry        │
│  isp_hub75_hwBuffers.spin2 - Screen RAM allocation               │
│  isp_hub75_hwPanelConfig.spin2 - User configuration              │
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

---

## 2. Data Flow

### 2.1 Complete Data Path

```
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION: screen.setPixelColor(x, y, r, g, b)                │
│              Uses 24-bit color values (0x000000 - 0xFFFFFF)     │
└──────────────────────────┬──────────────────────────────────────┘
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
│  Example: 256×128 @ 8-bit = 4,194,304 bytes per set             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ cmdWritePwmBuffer() - async command
                           │ PASM2 driver reads in chunks
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ PASM2 DRIVER (Running continuously in dedicated COG)            │
│                                                                  │
│  1. Read PWM subpage from HUB into COG buffer (512 longs)       │
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

When `drawPixelAtRCwithRGB(chainIdx, row, col, red, green, blue)` is called:

1. **Rotation Transform** (if configured):
   - ROT_NONE: offset = (row × maxColumns + col) × bytesPerColor
   - ROT_180: offset = ((maxRows-1-row) × maxColumns + (maxCols-1-col)) × bytesPerColor
   - ROT_90/270: Swap row/column coordinates

2. **Color Correction**:
   - Apply brightness scaling: `pwmValue = (colorValue × brightness) >> 8`
   - Apply gamma correction (optional): `pwmValue = gammaTable[pwmValue]`
   - Map to color depth: `finalValue = (pwmValue × maxPwmFrames) / 255`

3. **Buffer Write**:
   ```
   screenBuffer[offset + 0] = correctedRed
   screenBuffer[offset + 1] = correctedGreen
   screenBuffer[offset + 2] = correctedBlue
   ```

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

| Depth | Colors | PWM Frames | Relative Speed | Memory Factor |
|-------|--------|------------|----------------|---------------|
| 3-bit | 512 | 7 | Fastest | 1.0× |
| 4-bit | 4,096 | 15 | Fast | 1.0× |
| 5-bit | 32,768 | 31 | Medium | 1.0× |
| 6-bit | 262,144 | 63 | Slow | 1.5× |
| 7-bit | 2,097,152 | 127 | Slower | 1.5× |
| 8-bit | 16,777,216 | 255 | Slowest | 1.5× |

**Note**: 3-5 bit depths use 2 bytes per pixel in screen buffer; 6-8 bit depths use 3 bytes.

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
- **Format**: 512 longs (2KB)
- **Location**: COG RAM (driver's dedicated COG)
- **Access**: Internal to driver

### 4.2 Memory Calculation

For a display configuration:

```
Screen Buffer Size:
  = displayWidth × displayHeight × bytesPerColor
  = displayWidth × displayHeight × (colorDepth > 5 ? 3 : 2)

PWM Frame Size (single frame):
  = (displayWidth × displayHeight) / 2 bytes

PWM Frameset Size:
  = colorDepth × PWM_Frame_Size

Total PWM Memory:
  = 2 × PWM_Frameset_Size (double-buffered)

Total Memory Per Adapter:
  = Screen_Buffer + (2 × PWM_Frameset)
```

### 4.3 Memory Examples

**Example 1: Single 64×64 panel, 5-bit color**
```
Screen Buffer:  64 × 64 × 2 = 8,192 bytes (8 KB)
PWM Frame:      (64 × 64) / 2 = 2,048 bytes
PWM Frameset:   5 × 2,048 = 10,240 bytes (10 KB)
Total:          8 KB + (2 × 10 KB) = 28 KB
```

**Example 2: 2×2 panel grid (256×128), 8-bit color**
```
Screen Buffer:  256 × 128 × 3 = 98,304 bytes (96 KB)
PWM Frame:      (256 × 128) / 2 = 16,384 bytes
PWM Frameset:   8 × 16,384 = 131,072 bytes (128 KB)
Total:          96 KB + (2 × 128 KB) = 352 KB
```

### 4.4 Buffer Table Structure

The `isp_hub75_hwBufferAccess.spin2` file maintains a table for each HUB75 adapter:

```
Entry Structure (17 LONGs per adapter):
  [0]  Screen buffer address
  [1]  PWM frameset 1 address
  [2]  PWM frameset 2 address
  [3]  Display columns (total width)
  [4]  Display rows (total height)
  [5]  Color depth (3-8)
  [6]  Bytes per color (2 or 3)
  [7]  Screen size in longs
  [8]  PWM frame size in bytes
  [9]  Rotation setting
  [10] Panel columns (single panel width)
  [11] Panel rows (single panel height)
  [12] Panels per column (vertical count)
  [13] Panels per row (horizontal count)
  [14] Panel chip type
  [15] HUB75 pin base
  [16] Address line count (ABC/ABCD/ABCDE)
```

---

## 5. Timing and Performance

### 5.1 Frame Rate Calculation

```
Panel Electrical Refresh Rate ≈ 600-1000 Hz (varies by panel)

Visible Frame Rate = Electrical_Rate / Total_PWM_Frames

Examples:
  3-bit @ 800 Hz: 800 / 7 = 114 fps
  5-bit @ 800 Hz: 800 / 31 = 26 fps
  8-bit @ 800 Hz: 800 / 255 = 3.1 fps
```

### 5.2 Timing-Critical Operations

#### Pixel Clocking (HIGHEST PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2` lines 1087-1102
- **Requirement**: 15-30 MHz clock rate depending on panel chip
- **Implementation**: Uses `rep` instruction for zero-overhead loop
- **Timing**: ~25-50ns per pixel at 335 MHz P2 clock

#### HUB-to-COG Transfer (MEDIUM PRIORITY)
- **Location**: `isp_hub75_rgb3bit.spin2` line 952
- **Method**: `setq` + `rdlong` bulk transfer with auto-increment
- **Transfer Size**: 512 longs per subpage
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
| PINS_P0_P15 | 0-15 | Available on P2 Eval |
| PINS_P8_P23 | 8-23 | Alternative grouping |
| PINS_P16_P31 | 16-31 | Primary HUB75 location |
| PINS_P32_P47 | 32-47 | Secondary HUB75 location |
| PINS_P40_P55 | 40-55 | Alternative grouping |
| PINS_P48_P63 | 48-63 | Third HUB75 location |

### 6.3 Configuration

Each adapter is configured via `DISPx_` constants in `isp_hub75_hwPanelConfig.spin2`:

```spin2
' Adapter 0 configuration
DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
DISP0_MAX_PANELS_PER_ROW = 2
DISP0_MAX_PANELS_PER_COLUMN = 2
DISP0_COLOR_DEPTH = hwEnum.DEPTH_5BIT
DISP0_ROTATION = hwEnum.ROT_NONE

' Adapter 1 configuration (if used)
DISP1_ADAPTER_BASE_PIN = hwEnum.PINS_P32_P47
...
```

### 6.4 Enabling Additional Adapters

To enable adapters beyond the first:

1. **In `isp_hub75_hwBufferAccess.spin2`**: Uncomment table entries for DISP1/DISP2
2. **In `isp_hub75_hwBuffers.spin2`**: Uncomment buffer allocations for DISP1/DISP2
3. **In `isp_hub75_hwPanelConfig.spin2`**: Configure DISP1_/DISP2_ constants

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

**Scan Modes**:
- Standard: 1/16 or 1/32 scan
- Special: 1/8 scan (MBI5124GP) - requires different row mapping

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
