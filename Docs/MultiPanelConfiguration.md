# Multi-Panel Configuration Guide

This guide explains how to configure the P2 HUB75 LED Matrix Driver for multi-panel displays, including arrangements up to 4×4 panels.

## Overview

The driver supports flexible panel arrangements:
- **Horizontal chains**: 1×N panels (single row)
- **Vertical stacks**: N×1 panels (single column)
- **2D grids**: M×N panels (rows × columns)

## Configuration File

All panel configuration is done in `isp_hub75_hwPanelConfig.spin2`. Each HUB75 adapter (up to 3) has its own set of `DISPn_*` constants.

## Configuration Steps

### Step 1: Hardware Connection

```spin2
' (1) describe the panel connections, addressing and chips
DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Pin Groups:**
| Constant | Pins |
|----------|------|
| `PINS_P0_P15` | P0-P15 |
| `PINS_P8_P23` | P8-P23 |
| `PINS_P16_P31` | P16-P31 |
| `PINS_P32_P47` | P32-P47 |
| `PINS_P40_P55` | P40-P55 |

**Driver Chips:**
| Constant | Address Lines |
|----------|---------------|
| `CHIP_DP5125D`, `CHIP_MBI5124GP` | ABC (3) |
| `CHIP_FM6124`, `CHIP_FM6126A`, `CHIP_GS6238S` | ABCD (4) |
| `CHIP_ICN2037`, `CHIP_ICN2038S` | ABCDE (5) |

### Step 2: Single Panel Size

```spin2
' (2) describe the single panel physical size
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
```

Common panel sizes:
- 64×32 (2,048 pixels)
- 64×64 (4,096 pixels)
- 128×64 (8,192 pixels)

### Step 3: Panel Arrangement

```spin2
' the organization of the panels: visual layout
DISP0_MAX_PANELS_PER_ROW = 2
DISP0_MAX_PANELS_PER_COLUMN = 2
```

This creates a 2×2 grid with panels numbered in **Z-pattern** (row-major order):

```
┌─────────┬─────────┐
│ Panel 0 │ Panel 1 │
├─────────┼─────────┤
│ Panel 2 │ Panel 3 │
└─────────┴─────────┘
```

**Wire your panels in this same order:** Panel 0 → Panel 1 → Panel 2 → Panel 3

### Step 4: Color Depth

```spin2
' (3) describe the color depth you want to support [3-8] bits per LED
DISP0_COLOR_DEPTH = hwEnum.DEPTH_8BIT
```

| Depth | Colors | Bytes/Pixel | PWM Frames |
|-------|--------|-------------|------------|
| `DEPTH_3BIT` | 512 | 2 | 7 |
| `DEPTH_4BIT` | 4,096 | 2 | 15 |
| `DEPTH_5BIT` | 32,768 | 2 | 31 |
| `DEPTH_6BIT` | 262,144 | 3 | 63 |
| `DEPTH_7BIT` | 2,097,152 | 3 | 127 |
| `DEPTH_8BIT` | 16,777,216 | 3 | 255 |

### Step 5: Display Rotation (Optional)

```spin2
' (4) Apply desired rotation to entire display
DISP0_ROTATION = hwEnum.ROT_NONE
```

Options: `ROT_NONE`, `ROT_LEFT_90`, `ROT_RIGHT_90`, `ROT_180`

## Memory Requirements

The P2 has **512 KB** of hub RAM. The driver requires three buffers:

| Buffer | Size Formula |
|--------|--------------|
| Screen Buffer | `width × height × bytes_per_pixel` |
| PWM Frameset 1 | `width × height × 0.5 × color_depth` |
| PWM Frameset 2 | `width × height × 0.5 × color_depth` |

### Memory Calculator

For a display of W columns × H rows at D-bit color depth:

```
Screen Buffer = W × H × (D <= 5 ? 2 : 3) bytes
PWM Frameset = W × H × 0.5 × D bytes (×2 for double-buffer)
Total = Screen + (2 × PWM Frameset)
```

### Example Configurations

| Arrangement | Panel Size | Total Pixels | 8-bit Memory | 5-bit Memory |
|-------------|------------|--------------|--------------|--------------|
| 1×1 | 64×64 | 4,096 | 24 KB | 14 KB |
| 1×1 | 128×64 | 8,192 | 49 KB | 29 KB |
| 2×1 | 128×64 | 16,384 | 98 KB | 57 KB |
| 1×2 | 128×64 | 16,384 | 98 KB | 57 KB |
| **2×2** | **128×64** | **32,768** | **196 KB** | **115 KB** |
| 4×1 | 128×64 | 32,768 | 196 KB | 115 KB |
| 3×2 | 64×64 | 24,576 | 147 KB | 86 KB |
| 4×2 | 64×64 | 32,768 | 196 KB | 115 KB |
| 3×3 | 64×64 | 36,864 | 221 KB | 129 KB |
| **4×4** | **64×64** | **65,536** | **393 KB** | **229 KB** |
| 4×4 | 64×32 | 32,768 | 196 KB | 115 KB |

**Note:** Configurations over ~400 KB may not leave enough RAM for your application code.

### Maximum Practical Configurations

| Target | Recommended Max |
|--------|-----------------|
| 8-bit color | ~65K pixels (e.g., 4×4 @ 64×64, or 2×2 @ 128×64) |
| 5-bit color | ~110K pixels |
| 3-bit color | ~150K pixels |

## Panel Arrangement Examples

### Horizontal Chain (4×1)

```spin2
DISP0_MAX_PANELS_PER_ROW = 4
DISP0_MAX_PANELS_PER_COLUMN = 1
```

```
Wire order: 0 → 1 → 2 → 3

┌────────┬────────┬────────┬────────┐
│ Panel 0│ Panel 1│ Panel 2│ Panel 3│
└────────┴────────┴────────┴────────┘
```

### Vertical Stack (1×4)

```spin2
DISP0_MAX_PANELS_PER_ROW = 1
DISP0_MAX_PANELS_PER_COLUMN = 4
```

```
Wire order: 0 → 1 → 2 → 3

┌────────┐
│ Panel 0│
├────────┤
│ Panel 1│
├────────┤
│ Panel 2│
├────────┤
│ Panel 3│
└────────┘
```

### 2×2 Grid (Z-Pattern)

```spin2
DISP0_MAX_PANELS_PER_ROW = 2
DISP0_MAX_PANELS_PER_COLUMN = 2
```

```
Wire order: 0 → 1 → 2 → 3

┌─────────┬─────────┐
│ Panel 0 │ Panel 1 │
├─────────┼─────────┤
│ Panel 2 │ Panel 3 │
└─────────┴─────────┘
```

### 3×3 Grid

```spin2
DISP0_MAX_PANELS_PER_ROW = 3
DISP0_MAX_PANELS_PER_COLUMN = 3
```

```
Wire order: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

┌─────────┬─────────┬─────────┐
│ Panel 0 │ Panel 1 │ Panel 2 │
├─────────┼─────────┼─────────┤
│ Panel 3 │ Panel 4 │ Panel 5 │
├─────────┼─────────┼─────────┤
│ Panel 6 │ Panel 7 │ Panel 8 │
└─────────┴─────────┴─────────┘
```

### 4×4 Grid

```spin2
DISP0_MAX_PANELS_PER_ROW = 4
DISP0_MAX_PANELS_PER_COLUMN = 4
```

```
Wire order: 0 → 1 → 2 → 3 → 4 → 5 → ... → 15

┌────────┬────────┬────────┬────────┐
│ Pnl 0  │ Pnl 1  │ Pnl 2  │ Pnl 3  │
├────────┼────────┼────────┼────────┤
│ Pnl 4  │ Pnl 5  │ Pnl 6  │ Pnl 7  │
├────────┼────────┼────────┼────────┤
│ Pnl 8  │ Pnl 9  │ Pnl 10 │ Pnl 11 │
├────────┼────────┼────────┼────────┤
│ Pnl 12 │ Pnl 13 │ Pnl 14 │ Pnl 15 │
└────────┴────────┴────────┴────────┘
```

## Wiring Patterns

### Default: Z-Pattern (Row-Major)

By default, the driver uses **Z-pattern wiring** where the wire order matches the display order:

```
Z-Pattern (row-major):
0 → 1 → 2 → 3
↓
4 → 5 → 6 → 7
```

**Your physical cable connections follow the panel numbering.**

### Custom Wiring: Wire Order Mapping

For other wiring patterns (serpentine, reverse, etc.), you can configure custom wire order mapping in `isp_hub75_hwBufferAccess.spin2`.

#### Serpentine Wiring Example

Serpentine wiring snakes back and forth to minimize cable lengths:

```
Serpentine 2x2:
0 → 1       Display order: 0, 1, 2, 3
    ↓       Wire order:    0, 1, 3, 2
3 ← 2       (bottom row wired right-to-left)

Serpentine 4x2:
0 → 1 → 2 → 3       Display order: 0, 1, 2, 3, 4, 5, 6, 7
            ↓       Wire order:    0, 1, 2, 3, 7, 6, 5, 4
7 ← 6 ← 5 ← 4       (second row reversed)
```

#### Configuring Wire Order

Edit the `disp0WireOrder` table in `isp_hub75_hwBufferAccess.spin2`:

```spin2
' Default Z-pattern (no remapping)
disp0WireOrder      BYTE    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

' Serpentine 2x2 example
disp0WireOrder      BYTE    0, 1, 3, 2, ...

' Serpentine 4x2 example
disp0WireOrder      BYTE    0, 1, 2, 3, 7, 6, 5, 4, ...

' Serpentine 4x4 example
disp0WireOrder      BYTE    0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11, 15, 14, 13, 12
```

Entry N specifies the wire position for display panel N.

### Per-Panel Rotation

With serpentine wiring, alternating rows of panels may be physically rotated 180° due to cable folding. Configure individual panel rotations in `isp_hub75_hwBufferAccess.spin2`:

```spin2
' Default: all panels upright
disp0PanelRots      BYTE    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

' Serpentine 2x2: bottom row rotated 180°
disp0PanelRots      BYTE    0, 0, 2, 2, ...

' Serpentine 4x2: second row rotated 180°
disp0PanelRots      BYTE    0, 0, 0, 0, 2, 2, 2, 2, ...
```

**Rotation values:**
| Value | Rotation |
|-------|----------|
| 0 | No rotation (ROT_NONE) |
| 1 | 90° clockwise (ROT_RIGHT_90) |
| 2 | 180° (ROT_180) |
| 3 | 90° counter-clockwise (ROT_LEFT_90) |

### Combined Example: Serpentine 2x2

For a 2x2 grid with serpentine wiring:

```
Physical layout (panels face up):
┌─────────┬─────────┐
│ Panel 0 │ Panel 1 │  ← Normal orientation
├─────────┼─────────┤
│ Panel 2 │ Panel 3 │  ← Rotated 180° (cable folds back)
└─────────┴─────────┘

Wire order: HUB75 → Panel 0 → Panel 1 → Panel 3 → Panel 2
```

Configuration:
```spin2
' Wire order: display [0,1,2,3] → wire [0,1,3,2]
disp0WireOrder      BYTE    0, 1, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

' Rotations: panels 2 and 3 are upside-down
disp0PanelRots      BYTE    0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
```

## Complete Configuration Example

Here's a complete example for a 2×2 grid of 128×64 panels:

```spin2
CON { User Panel Connection and Configuration }

' -------------------------------------------------------------------
' panel set on 1st HUB75 adapter board - DISP0_* constants
' -------------------------------------------------------------------

    ' /-------------------------------------------
    ' |  User configure

    ' (1) describe the panel connections, addressing and chips
    DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE

    ' (2) describe the single panel physical size
    DISP0_MAX_PANEL_COLUMNS = 128
    DISP0_MAX_PANEL_ROWS = 64

    ' (3) the organization of the panels: visual layout
    '   [0][1]      2 columns
    '   [2][3]      2 rows
    '
    DISP0_MAX_PANELS_PER_ROW = 2
    DISP0_MAX_PANELS_PER_COLUMN = 2

    ' (4) describe the color depth you want to support [3-8] bits per LED
    DISP0_COLOR_DEPTH = hwEnum.DEPTH_8BIT

    ' (5) Apply desired rotation to entire display
    DISP0_ROTATION = hwEnum.ROT_NONE

    ' |  End User configure
    ' \-------------------------------------------
```

This creates:
- Total display: 256×128 pixels (32,768 pixels)
- Memory usage: ~196 KB at 8-bit color
- Wire panels: 0→1→2→3 in Z-pattern

## Troubleshooting

### Pixels appear on wrong panel
- Verify wire order matches Z-pattern (row-major)
- Check `MAX_PANELS_PER_ROW` and `MAX_PANELS_PER_COLUMN` values

### Colors are wrong
- Some chips swap R/B or G/B - check chip documentation
- The driver handles known chip color swaps automatically

### Display is upside down or mirrored
- Use `DISP0_ROTATION` to rotate the entire display
- `ROT_180` flips both horizontally and vertically

### Out of memory errors
- Reduce color depth (8-bit → 5-bit saves ~40%)
- Reduce panel count
- Check total pixel count against memory limits

## API Usage

Once configured, the display appears as a single logical surface:

```spin2
' Draw at display coordinates (0,0 = top-left of entire display)
pixels.drawPixelAtRC(chainIndex, row, column, color.cRed)

' Draw on a specific panel (0,0 = top-left of that panel)
display.fillPanel(panelIndex, color.cGreen)
display.setCursorOnPanel(line, column, panelIndex)
```

The coordinate translation happens automatically - you draw to the logical display, and the driver maps to the correct physical panel and buffer location.
