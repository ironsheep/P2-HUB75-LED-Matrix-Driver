# Author's Test Panel Configurations

This document is the record of the panels and rigs the author has tested. The settings block for each panel type, ready to copy into the user section of `isp_hub75_hwPanelConfig.spin2`, is in that chip's section of the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#detailed-chip-documentation); this page links each one. How the settings and the panel sentences work is in the [Configuration Guide](WiringGuide.md). Each panel type's scan, address lines and test status are stated once, in the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix); this page does not repeat them. How many panels one adapter can drive for each panel type is in the [driver limits table](WiringGuide.md#driver-limits). The tools the author measures with (the instrumentation harness, the logic analyzer channels, the pin identification test) are on the [Testing and Measurement](TestingAndMeasurement.md) page.

## Configuration Summary Table

| Config | Panel Model | Color Label | Size | Chip | Pin Base | Notes |
|--------|-------------|-------------|------|------|----------|-------|
| 1-3 | P3-6432-121-16s-D1.0 | **Pink** | 64×32 | FM6126A | P16-P31 | Requires init sequence |
| 4 | P3-6432-2121-16S-D1.0 | **Orange** | 64×32 | FM6124 | P16-P31 | Hackerbox panel |
| 5-6 | P2-2020210240-200 | - | 64×64 | ICN2037 | P16-P31 | R/B swapped |
| 7 | P4-1921-8S-vV2.0 | **Green** | 64×32 | MBI5124GP | P16-P31 | One panel or two chained |
| 8 | P4-1921-8S-vV2.0 | **Green** | 64×32 | MBI5124GP | P32-P47 | Alternate pins |
| 9 | P2.5-16S-V1.0 | **Cyan** | 64×32 | GS6238S | P16-P31 | G/B swapped |
| 10 | P2-2020210240-200 | - | 64×64 | ICN2037 | P16-P31 | P2 Cube FLAT, R/B swapped |
| 11 | P2-1515-128X64-32S-S2 | - | 128×64 | ICN2037 | P16-P31 | LARGE panels, R/B swapped |
| 12 | (road-sign panel) | - | 64×64 | ICN2038S | P16-P31 | Single-ended |

Scan, address lines and test status for each of these: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix).

### Color Label Quick Reference

| Color | Chip | Notes |
|-------|------|-------|
| **Pink** | FM6126A | 64×32 |
| **Orange** | FM6124 | 64×32, Hackerbox |
| **Green** | MBI5124GP | 64×32 |
| **Cyan** | GS6238S | 64×32, G/B swapped |

## Detailed Configuration Documentation

---

### Configuration 1-3: FM6126A 64×32 Panels

**Panel Model:** P3-6432-121-16s-D1.0 (pink labels)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Half-panel: 1,024 pixels each (top: R1/G1/B1, bottom: R2/G2/B2)
- Driver Chip: FM6126A
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

The settings block is in the [FM6126A section](ChipCharacteristicsMatrix.md#fm6126a-pink-labels) of the Chip Characteristics Matrix.

**4.0.0 refresh core, one panel (2026-10-05):** measured refresh is in the [Configuration Guide](WiringGuide.md#measured-refresh).

---

### Configuration 4: FM6124 64×32 Panels (Hackerbox)

**Panel Model:** P3-6432-2121-16S-D1.0 (orange labels)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Driver Chip: FM6124 (from Hackerbox kit)
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

The settings block is in the [FM6124 section](ChipCharacteristicsMatrix.md#fm6124-orange-labels) of the Chip Characteristics Matrix.

**4.0.0 refresh core, one panel (2026-10-05):** measured refresh is in the [Configuration Guide](WiringGuide.md#measured-refresh).

---

### Configuration 5-6: ICN2037 64×64 Panels

**Panel Model:** P2-2020210240-200

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Half-panel: 2,048 pixels each
- Driver Chip: ICN2037
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped** (driver handles automatically)

The settings block (one panel) is in the [ICN2037 section](ChipCharacteristicsMatrix.md#icn2037--icn2037bp-no-color-label) of the Chip Characteristics Matrix.

---

### Configuration 7: MBI5124GP 64×32 Panels (P16-P31)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Driver Chip: MBI5124GP (the driver flag `SCAN_4` places each row differently in the frame set)
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

The settings block, for one panel and for two chained end to end as one 128x32 display, is in the [MBI5124GP section](ChipCharacteristicsMatrix.md#mbi5124gp-green-pcbs) of the Chip Characteristics Matrix.

**4.0.0 refresh core (one panel 2026-10-05, two chained 2026-10-07):** at the chain-limit clock; measured refresh is in the [Configuration Guide](WiringGuide.md#measured-refresh).

---

### Configuration 8: MBI5124GP 64×32 Panels (P32-P47)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

Same as Configuration 7 but using alternate pin group.

**Configuration** (one panel):
```spin2
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P32_P47
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_MBI5124GP
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 32
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
disp0PanelsEnd
```

Test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix) (the chip's runs were on the P16-P31 pins, Configuration 7). See the [driver limits table](WiringGuide.md#driver-limits).

---

### Configuration 9: GS6238S 64×32 Panels

**Panel Model:** P2.5-16S-V1.0 (cyan label) S210164-M00739

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Driver Chip: GS6238S
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Green/Blue swapped** (driver handles automatically)

The settings block is in the [GS6238S section](ChipCharacteristicsMatrix.md#gs6238s-cyan-label) of the Chip Characteristics Matrix.

---

### Configuration 10: ICN2037BP 64×64 Panels (P2 Cube)

**Panel Model:** P2-2020210240-200
**Panel Label:** E506652 DCHY-M
**Serial Numbers:** S210350H00127, S210350H00112, etc. (6 panels)

**Purpose:** P2 Cube FLAT project (6 panels forming a cube display)

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels per panel
- Total: 6 panels × 4,096 = 24,576 pixels
- Driver Chip: ICN2037BP
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| MW245B | Bus transceiver (Sunmoon) |
| TC7262BJ | Row driver (Fuman, anti-ghosting) |

**Configuration** (the six panels laid out as the cross-shaped cube net; the ribbon runs `C0` ... `C3` along the row of four, then `C4` (the top face, marked `CUBE_TOP`) and `C5`; `C1` is the front face, marked `CUBE_FRONT`. [Example 7](WiringGuide.md#example-7-the-cube-wired-in-a-ring-with-top-and-front) of the Configuration Guide works it through):
```spin2
' P2 Cube FLAT
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_FRONT
                LONG    hwEnum.ROW_1 | hwEnum.COL_2 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_3 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_TOP
                LONG    hwEnum.ROW_2 | hwEnum.COL_1 | hwEnum.TOP_UP
disp0PanelsEnd
```

What the 4.0.0 cube layer has and has not run on is in the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#not-yet-proven-on-hardware-with-400). The driver limit for this panel type is in the [driver limits table](WiringGuide.md#driver-limits).

**Notes:** These panels share the same supporting chipset (MW245B + TC7262BJ) as the Cyan (GS6238S) panels, but use ICN2037BP as the LED driver.

---

### Configuration 11: ICN2037BP 128×64 Panels (LARGE)

**Panel Model:** P2-1515-128X64-32S-S2
**Serial/Batch:** 2210BP201-88-60

**Purpose:** Author's large display panels (4 panels for 2×2 grid)

**Panel Specifications:**
| Spec | Value |
|------|-------|
| Pixel Pitch | 2mm (P2) |
| LED Type | SMD1515 |
| Resolution | 128×64 pixels |
| Scan Mode | 32S |

**Specifications:**
- Size: **128 columns × 64 rows = 8,192 pixels**
- Half-panel: 4,096 pixels each
- Driver Chip: ICN2037BP
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| 74HC245TS | Bus transceiver (TSSOP) |
| 74HC04D | Hex inverter (signal conditioning) |
| RUC7258D | Row driver (Ruichips) |

The settings block for one panel is in the [ICN2037 section](ChipCharacteristicsMatrix.md#icn2037--icn2037bp-no-color-label) of the Chip Characteristics Matrix. This is the rig's panel type; its refresh is measured at every depth. Four of these (the rig) sit exactly at the driver's limit for this panel type: see the [driver limits table](WiringGuide.md#driver-limits).

**2×2 Grid Configuration** (the author's rig: the panels hang upside down, the adapter plugs into the bottom-left panel, and the ribbon runs along the bottom row and then the top row; every top is `TOP_DOWN`):
```spin2
' the author's rig, as shipped in the file
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 128
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_DOWN    ' C0, bottom-left
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_DOWN    ' C1, bottom-right
                LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_DOWN    ' C2, top-left
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_DOWN    ' C3, top-right
disp0PanelsEnd
```

This creates a 256×128 pixel display (32,768 total pixels). [Example 3](WiringGuide.md#example-3-2x2-in-z-order-from-bottom-left-the-rig) of the Configuration Guide works this one through.

---

### Configuration 12: ICN2038S 64×64 Panels (Road-Sign Display)

**Panel Model:** 64×64 (commercial road-sign display panel)

**Purpose:** Road-sign display application

**Panel Type:** Commercial all-weather panel, single-ended (no daisy-chain by construction)

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Driver Chip: ICN2038S (the driver sets `SCAN_4` for it)
- Scan, address lines and test status: see the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **No color swap** (unlike ICN2037)

The settings block is in the [ICN2038S section](ChipCharacteristicsMatrix.md#icn2038s-no-color-label---road-sign-display-panel) of the Chip Characteristics Matrix.

---

## Chip Quick Reference

Each panel type's scan, address lines, colour swap, init requirement and test status are in the [Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix).

Each chip's datasheet clock and /OE ratings are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings).

---

## Driver Limits per Panel Type

How many panels one adapter can drive, for each panel type above, is in the
[Configuration Guide's driver limits table](WiringGuide.md#driver-limits), the one home of that
table: the maximum per adapter, what sets it (the refresh line buffer, for every type), the
hub RAM available, and the refresh rate. Its rows are these configurations. Every limit in it
is **calculated** from the driver's constants and none has been exercised at that panel count
on hardware except the rig's four ICN2037 128x64 panels (configuration 11). Refresh is
measured for the rig and for single FM6126A, FM6124 and MBI5124GP panels (configurations 1-4
and 7), on the same page.

---

## Multi-Panel Verified Configurations

Which panel types and chains have run on hardware, and what is not yet proven with the 4.0.0 driver, is stated once, in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix) and the [list under it](ChipCharacteristicsMatrix.md#not-yet-proven-on-hardware-with-400).

---

## Configuration Toggle Mechanism

The configurations are examples to copy from; none of them is a switch in the code.

To change configuration:
1. In the user section of `isp_hub75_hwPanelConfig.spin2`, replace the `DISP0_` block and its panel list with the starting block of your panel type from the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#detailed-chip-documentation), or with a rig block above (a second or third display is added with `#DEFINE DISP1_PRESENT` or `#DEFINE DISP2_PRESENT`, see the [Configuration Guide](WiringGuide.md#more-displays-and-optional-settings))
2. Match the values to your hardware
3. Recompile and flash; the startup picture and the identify screen confirm the panel list (see the [Configuration Guide](WiringGuide.md))

Nothing below the user section of `isp_hub75_hwPanelConfig.spin2`, and nothing in `isp_hub75_hwBufferAccess.spin2`, is edited for a configuration change.

---

*Last Updated: October 2026 (driver 4.0.0)*
