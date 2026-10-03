# Multi-Panel Configuration Guide

This guide explains the hardware and memory side of configuring the P2 HUB75 LED Matrix Driver for multi-panel displays: the adapter pins, the driver chip, the panel size, the colour depth and the memory a display needs.

**Where the panels are, how they are cabled and which way they hang** is described by the wiring sentences, and that is covered in the [Wiring Guide](WiringGuide.md): the sentence grammar, filling in a config from the identify screen, display rotation, the cube, the driver limits per panel type, every startup message, and seven worked examples (a row of 4, two panels, a 2x2 in Z order, a 2x2 serpentine, 3 across by 2 down, an L shape and the cube).

## Configuration File

All panel configuration is done in `isp_hub75_hwPanelConfig.spin2`. Each HUB75 adapter (up to 3) has its own set of `DISPn_*` constants.

## Configuration Steps

### Step 1: Hardware Connection

```spin2
' (1) describe the panel connections, addressing and chips
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Pin Groups:**
| Constant | Pins |
|----------|------|
| `PIN_GROUP_P0_P15` | P0-P15 |
| `PIN_GROUP_P16_P31` | P16-P31 |
| `PIN_GROUP_P32_P47` | P32-P47 |

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

### Step 3: Color Depth

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

### Step 4: Panel Layout, Cabling and Rotation

Describe the layout with the wiring sentences (`DISPn_C0` ... `DISPn_C15`), and say how the whole display hangs with `DISPn_ROTATION`. Both are covered, with worked examples, in the [Wiring Guide](WiringGuide.md).

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

How many panels one adapter can drive, per panel type, is in the [Wiring Guide's driver limits](WiringGuide.md#driver-limits).

## Chip Multi-Panel Support

**IMPORTANT:** Not all driver chips have been tested in multi-panel configurations.

| Chip | Color Label | Multi-Panel Support | Notes |
|------|-------------|---------------------|-------|
| **FM6126A** | Pink | ✅ Tested | Tested in chains |
| **ICN2037** | - | ✅ Full support | Tested in chains and 2D grids |
| **ICN2038S** | - | ⚠️ Expected | Similar to ICN2037 |
| FM6124 | Orange | ⚠️ Untested | Similar to FM6126A |
| MBI5124GP | Green | ⚠️ Untested | 1/8 scan |
| GS6238S | Cyan | ⚠️ Untested | |
| DP5125D | - | ⚠️ Untested | May work |

For multi-panel displays, verified chips are **FM6126A (Pink)** and **ICN2037**.

## Troubleshooting

### Display is flashing or unstable
- Check the startup picture: the number of panels it shows must equal the number of panels you have cabled
- Check that chip type matches your panels (ICN2037 for multi-panel)
- Ensure panel dimensions match physical panels (columns × rows)

### Startup stops with a `HUB75:` message
- A wiring sentence is wrong. Every message the driver can print is listed, with its cause, in the [Wiring Guide](WiringGuide.md#startup-messages).

### Pixels appear on wrong panel, or the panels are in the wrong order
- Run the identify program and compare the `P` labels with where the panels hang; the [Wiring Guide](WiringGuide.md#filling-in-your-config-from-the-identify-screen) explains how to read it and correct the sentences

### Colors are wrong
- Some chips swap R/B or G/B - check chip documentation
- The driver handles known chip color swaps automatically

### Display is upside down or mirrored
- If one panel's content is turned, correct its arrow word; if the whole display is turned, set `DISP0_ROTATION` to how the display hangs. Both are explained in the [Wiring Guide](WiringGuide.md#display-rotation)

### Out of memory errors
- Reduce color depth (8-bit → 5-bit saves ~40%)
- Reduce panel count
- Check total pixel count against memory limits

### Panel dimensions: Columns vs Rows
- `MAX_PANEL_COLUMNS` = horizontal pixel count (width)
- `MAX_PANEL_ROWS` = vertical pixel count (height)
- Common sizes: 64×32, 64×64, 128×64
- A 128×64 panel is 128 pixels wide and 64 pixels tall (landscape)

## API Usage

Once configured, the display appears as a single logical surface:

```spin2
' Draw at display coordinates (0,0 = top-left of entire display)
pixels.drawPixelAtRC(chainIndex, row, column, color.cRed)

' Draw on a specific panel (0,0 = top-left of that panel)
display.fillPanel(panelIndex, color.cGreen)
display.setCursorOnPanel(line, column, panelIndex)
```

The coordinate translation happens automatically - you draw to the logical display, and the driver maps to the correct physical panel and buffer location. Panel indexes are panel positions: `0` is the top-left panel as the display hangs, numbered in reading order.
