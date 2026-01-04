# Author's Test Panel Configurations

This document catalogs all panel configurations the author has tested, as documented in `isp_hub75_hwPanelConfig.spin2`.

## Configuration Summary Table

| Config | Panel Model | Color Label | Size | Chip | Addr | Pin Base | Multi-Panel | Notes |
|--------|-------------|-------------|------|------|------|----------|-------------|-------|
| 1-3 | P3-6432-121-16s-D1.0 | **Pink** | 64×32 | FM6126A | ABCD | P16-P31 | **Multi-panel OK** | Requires init sequence |
| 4 | P3-6432-121-16s-D1.0 | **Orange** | 64×32 | FM6124 | ABCD | P16-P31 | Untested | Hackerbox panel |
| 5-6 | P2-2020210240-200 | - | 64×64 | ICN2037 | ABCDE | P16-P31 | **Multi-panel OK** | R/B swapped |
| 7 | P4-1921-8S-vV2.0 | **Green** | 64×32 | MBI5124GP | ABC | P16-P31 | Untested | 1/8 scan |
| 8 | P4-1921-8S-vV2.0 | **Green** | 64×32 | MBI5124GP | ABC | P32-P47 | Untested | 1/8 scan, alt pins |
| 9 | P2.5-16S-V1.0 | **Cyan** | 64×32 | GS6238S | ABCD | P16-P31 | Untested | G/B swapped |
| 10 | P2-2020210240-200 | - | 64×64 | ICN2037 | ABCDE | P16-P31 | **Multi-panel OK** | P2 Cube FLAT, R/B swapped |
| 11 | P2-2020210240-200 | - | 128×64 | ICN2037 | ABCDE | P16-P31 | **Multi-panel OK** | LARGE panels, R/B swapped |

### Color Label Quick Reference

| Color | Chip | Notes |
|-------|------|-------|
| **Pink** | FM6126A | 64×32, multi-panel tested |
| **Orange** | FM6124 | 64×32, Hackerbox |
| **Green** | MBI5124GP | 64×32, 1/8 scan |
| **Cyan** | GS6238S | 64×32, G/B swapped |

## Detailed Configuration Documentation

---

### Configuration 1-3: FM6126A 64×32 Panels

**Panel Model:** P3-6432-121-16s-D1.0 (pink labels)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: 1/16 (16 address lines)
- Half-panel: 1,024 pixels each (top: R1/G1/B1, bottom: R2/G2/B2)
- Driver Chip: FM6126A
- Address Lines: ABCD (4 lines)
- Max Clock: 30MHz (16.5ns hi/16.5ns lo)

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
```

**Multi-Panel Status:** ❌ Single panel only (requires initialization sequence)

---

### Configuration 4: FM6124 64×32 Panels (Hackerbox)

**Panel Model:** P3-6432-2121-16S-D1.0 (orange labels)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: 1/16
- Driver Chip: FM6124 (from Hackerbox kit)
- Address Lines: ABCD (4 lines)
- Max Clock: 30MHz

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6124
PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
```

**Multi-Panel Status:** ❌ Single panel only

---

### Configuration 5-6: ICN2037 64×64 Panels

**Panel Model:** P2-2020210240-200

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Scan: 1/32 (32 address lines)
- Half-panel: 2,048 pixels each
- Driver Chip: ICN2037
- Address Lines: ABCDE (5 lines)
- Max Clock: 20MHz (25ns hi/25ns lo)
- Color Note: **Red/Blue swapped** (driver handles automatically)

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains**

---

### Configuration 7: MBI5124GP 64×32 Panels (P16-P31)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: **1/8 scan** (special addressing)
- Driver Chip: MBI5124GP
- Address Lines: ABC (3 lines)
- Max Clock: 20MHz

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_MBI5124GP
PANEL_ADDR_LINES = hwEnum.ADDR_ABC
```

**Multi-Panel Status:** ❌ Single panel only (1/8 scan complexity)

---

### Configuration 8: MBI5124GP 64×32 Panels (P32-P47)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

Same as Configuration 7 but using alternate pin group.

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P32_P47
PANEL_DRIVER_CHIP = hwEnum.CHIP_MBI5124GP
PANEL_ADDR_LINES = hwEnum.ADDR_ABC
```

**Multi-Panel Status:** ❌ Single panel only

---

### Configuration 9: GS6238S 64×32 Panels

**Panel Model:** P2.5-16S-V1.0 (cyan label) S210164-M00739

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: 1/16
- Driver Chip: GS6238S
- Address Lines: ABCD (4 lines)
- Max Clock: 30MHz
- Color Note: **Green/Blue swapped** (driver handles automatically)

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_GS6238S
PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
```

**Multi-Panel Status:** ❌ Single panel only

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
- Address Lines: ABCDE (5 lines)
- Max Clock: 20MHz
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| MW245B | Bus transceiver (Sunmoon) |
| TC7262BJ | Row driver (Fuman, anti-ghosting) |

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains** (used in cube project with 6 panels)

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
| Scan Mode | 1/32 scan (32S) |

**Specifications:**
- Size: **128 columns × 64 rows = 8,192 pixels**
- Scan: 1/32
- Half-panel: 4,096 pixels each
- Driver Chip: ICN2037BP
- Address Lines: ABCDE (5 lines)
- Max Clock: 20MHz
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| 74HC245TS | Bus transceiver (TSSOP) |
| 74HC04D | Hex inverter (signal conditioning) |
| RUC7258D | Row driver (Ruichips) |

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains**

**2×2 Grid Configuration:**
```spin2
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
DISP0_MAX_PANELS_PER_ROW = 2
DISP0_MAX_PANELS_PER_COLUMN = 2
```

This creates a 256×128 pixel display (32,768 total pixels).

---

### Configuration 12: ICN2038S 64×64 Panels (Road-Sign Display)

**Panel Model:** 64×64 (commercial road-sign display panel)

**Purpose:** Road-sign display application

**Panel Type:** Commercial all-weather panel, single-ended (no daisy-chain by construction)

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Scan: 1/8 (SCAN_4)
- Driver Chip: ICN2038S
- Address Lines: ABCDE (5 lines)
- Max Clock: 20MHz
- Color Note: **No color swap** (unlike ICN2037)

**Configuration:**
```spin2
ADAPTER_BASE_PIN = hwEnum.PINS_P0_P15
PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2038S
PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
```

**Multi-Panel Status:** ❌ Single panel only (no daisy-chain by design)

---

## Chip Quick Reference

| Chip | Color | Address Lines | Clock | Color Swap | Init Required | Multi-Panel |
|------|-------|---------------|-------|------------|---------------|-------------|
| FM6126A | Pink | ABCD | 30MHz | None | Yes | **Yes** |
| FM6124 | Orange | ABCD | 30MHz | None | No | Untested |
| ICN2037 | - | ABCDE | 20MHz | R/B | No | **Yes** |
| ICN2038S | - | ABCDE | 20MHz | None | No | N/A (single-ended) |
| MBI5124GP | Green | ABC | 20MHz | None | Yes | Untested |
| GS6238S | Cyan | ABCD | 30MHz | G/B | No | Untested |
| DP5125D | - | ABC | - | None | No | Untested |

---

## Multi-Panel Verified Configurations

The following chip/panel combinations have been verified working in multi-panel arrangements:

1. **FM6126A 64×32 (Pink)** - Tested in chains
2. **ICN2037 64×64** - Tested in chains and grids
3. **ICN2037 128×64** - Tested in chains and 2×2 grids

The following are expected to work but not yet verified:
- **ICN2038S** - Similar to ICN2037
- **FM6124 (Orange)** - Similar to FM6126A
- **DP5125D** - Untested

---

## Configuration Toggle Mechanism

**Note:** The commented configurations in `isp_hub75_hwPanelConfig.spin2` (lines 198-426) are documentation examples only. They are NOT individually toggleable.

To change configuration:
1. Edit the `DISP0_*` constants directly in the "User configure" section (lines 38-66)
2. Match the values to your hardware from the examples above
3. Recompile and flash

---

*Last Updated: December 2024*
