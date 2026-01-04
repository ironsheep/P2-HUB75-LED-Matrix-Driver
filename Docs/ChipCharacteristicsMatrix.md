# HUB75 Driver Chip Characteristics Matrix

This document provides a comprehensive matrix of all driver chip characteristics needed for proper panel control.

## Quick Reference Matrix

| Chip | Color | Addr Lines | Scan | R/B Swap | G/B Swap | Wide CLK | Init Req | Latch Style | Multi-Panel |
|------|-------|------------|------|----------|----------|----------|----------|-------------|-------------|
| **FM6126A** | Pink | ABCD | 1/16 | - | - | - | **Yes** | Offset+Overlap | ✅ Tested |
| **FM6124** | Orange | ABCD | 1/16 | - | - | - | - | Standard | ⚠️ Untested |
| **FM6124C** | - | ABCDE | 1/32 | - | - | - | - | Standard | ⚠️ Untested |
| **ICN2037/BP** | - | ABCDE | 1/32 | **Yes** | - | **Yes** | - | Enclosed | ✅ Tested |
| **ICN2038S** | - | ABCDE | 1/8 | - | - | **Yes** | - | Enclosed | N/A (single) |
| **MBI5124GP** | Green | ABC | 1/8 | - | - | - | **Yes** | Enclosed | ⚠️ Untested |
| **GS6238S** | Cyan | ABCD | 1/16 | - | **Yes** | - | - | Offset+Overlap | ⚠️ Untested |
| **DP5125D** | - | ABC | 1/8 | - | - | - | - | Offset+Overlap | ⚠️ Untested |

**Notes:**
- ICN2037BP is the same chip as ICN2037 in SSOP24-P-150 package
- Supporting chipsets vary by panel (see detailed sections below)

---

## Detailed Chip Documentation

### FM6126A (Pink Labels)

**Panel Model:** P3-6432-121-16s-D1.0

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCD (4) | 16 row addressing |
| Scan Rate | 1/16 | Standard scan |
| Max Clock | 30 MHz | 16.5ns hi/16.5ns lo |
| R/B Swap | No | |
| G/B Swap | No | |
| Wide Clock Pulse | No | |
| Init Required | **Yes** | Special power-up sequence |
| Latch Style | Offset | |
| Latch Position | Overlap | |
| Multi-Panel | **Tested** | Works in chains |

**On-Board Chips:**
| Chip | Function | Details |
|------|----------|---------|
| FM6126A | LED column driver | 16-channel dual-buffer constant current output, max 30MHz clock, requires init sequence, has built-in color balance |
| 74HC245C | Bus transceiver | Octal 3-state bidirectional transceiver, 2V-6V, 9ns propagation delay, enables daisy-chain pass-through |
| TC7258EN | Row driver | 8-channel line scanning blanking control, integrates 74HC138 decoder + 8 power tubes (2.5A, 130mΩ), anti-burn protection |

**Chip Detail Sources:**
- [FM6126A Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1145498/FUMAN/FM6126A.html)
- [74HC245 Datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT245.pdf)
- [TC7258EN Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1147175/FUMAN/TC7258EN.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | LAT_STYLE_OFFSET | LAT_POSN_OVERLAP | INIT_PANEL_REQUIRED
```

---

### FM6124 (Orange Labels)

**Panel Model:** P3-6432-2121-16S-D1.0 (Hackerbox)

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCD (4) | 16 row addressing |
| Scan Rate | 1/16 | Standard scan |
| Max Clock | 30 MHz | |
| R/B Swap | No | |
| G/B Swap | No | |
| Wide Clock Pulse | No | |
| Init Required | No | Simpler than FM6126A |
| Latch Style | Standard | |
| Latch Position | Standard | |
| Multi-Panel | Untested | Expected to work |

**On-Board Chips:**
| Chip | Function | Details |
|------|----------|---------|
| FM6124 | LED column driver | 16-channel dual-buffer constant current output, max 30MHz clock, no init sequence required, simpler than FM6126A |
| 74HC245C | Bus transceiver | Octal 3-state bidirectional transceiver, 2V-6V, 9ns propagation delay, enables daisy-chain pass-through |
| TC7258EN | Row driver | 8-channel line scanning blanking control, integrates 74HC138 decoder + 8 power tubes (2.5A, 130mΩ), anti-burn protection |

**Chip Detail Sources:**
- [FM6124 Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1145496/FUMAN/FM6124.html)
- [74HC245 Datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT245.pdf)
- [TC7258EN Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1147175/FUMAN/TC7258EN.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC
```

**Notes:** Simpler chip than FM6126A - no special initialization or latch timing required. Uses same bus transceiver (74HC245C) as Pink panels.

---

### FM6124C (No color label)

**Panel Model:** P3-HS23011030-600

**Panel Specifications:**
| Spec | Value |
|------|-------|
| Pixel Pitch | 3mm (P3) |
| Resolution | 64×64 pixels |
| Scan Mode | 1/32 scan |
| Interface | HUB75 |

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCDE (5) | 32 row addressing (64×64 panel) |
| Scan Rate | 1/32 | Full scan |
| Max Clock | 30 MHz | Same as FM6124 |
| R/B Swap | No | |
| G/B Swap | No | |
| Wide Clock Pulse | No | |
| Init Required | No | Same as FM6124 |
| Latch Style | Standard | |
| Latch Position | Standard | |
| Multi-Panel | Untested | Expected to work |

**On-Board Chips:**
| Chip | Function | Details |
|------|----------|---------|
| FM6124C | LED column driver | 16-channel dual-buffer constant current output, variant of FM6124, max 30MHz clock |
| 74HC245KA | Bus transceiver | Octal 3-state bidirectional transceiver, variant of 74HC245 |
| RUC7258D | Row driver | Ruichips 8-channel blanking control, built-in 3-to-8 decoder, constant charge absorption, anti-ghosting, short circuit protection (2.8A max) |

**Chip Detail Sources:**
- [FM6124 Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1145496/FUMAN/FM6124.html) (FM6124C is variant)
- [RUC7258 Info at Sekorm](https://en.sekorm.com/doc/1468121.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC
```

**Notes:**
- FM6124C is a variant of FM6124 from Fuman Electronics
- RUC7258D is manufactured by Shenzhen Ruichips Semiconductor, functionally equivalent to TC7258EN
- 74HC245KA is a variant of the standard 74HC245 bus transceiver
- This is a 64×64 panel using 5 address lines (ABCDE) for 1/32 scan

---

### ICN2037 / ICN2037BP (No color label)

**Panel Models:**
| Model | Size | Serial/Batch | Notes |
|-------|------|--------------|-------|
| P2-2020210240-200 | 64×64 | S210350H00127, etc. | Cube panels (×6), label E506652 DCHY-M |
| P2-1515-128X64-32S-S2 | 128×64 | 2210BP201-88-60 | Large panels (×4 for 2×2 grid) |

**Panel Specifications (128×64):**
| Spec | Value |
|------|-------|
| Pixel Pitch | 2mm (P2) |
| LED Type | SMD1515 |
| Resolution | 128×64 pixels |
| Scan Mode | 1/32 scan (32S) |
| Interface | HUB75 |

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCDE (5) | 32 row addressing |
| Scan Rate | 1/32 | Full scan |
| Max Clock | 20 MHz | 25ns hi/25ns lo |
| R/B Swap | **Yes** | Red and Blue swapped |
| G/B Swap | No | |
| Wide Clock Pulse | **Yes** | Slower clock required |
| Init Required | No | |
| Latch Style | Enclosed | Latch at end |
| Latch Position | Standard | |
| Multi-Panel | **Tested** | Works in chains and 2D grids |

**On-Board Chips (128×64 panels):**
| Chip | Function | Details |
|------|----------|---------|
| ICN2037BP | LED column driver | 16-channel constant current sink, dual latch for 50%+ higher refresh, 3-45mA output, ±2.5% accuracy, Noise Free™ technology |
| 74HC245TS | Bus transceiver | Octal 3-state bidirectional transceiver (TSSOP package) |
| 74HC04D | Hex inverter | 6 inverters for signal conditioning/buffering |
| RUC7258D | Row driver | Ruichips 8-channel blanking control, 2.8A max, anti-ghosting |

**On-Board Chips (64×64 Cube panels):**
| Chip | Function | Details |
|------|----------|---------|
| ICN2037BP | LED column driver | 16-channel constant current sink, dual latch, Noise Free™ technology |
| MW245B | Bus transceiver | Sunmoon 3-state octal transceiver (same as Cyan panels) |
| TC7262BJ | Row driver | Fuman 8-channel with anti-ghosting (same as Cyan panels) |

**Chip Detail Sources:**
- [ICN2037 Datasheet (Olympian LED)](https://olympianled.com/wp-content/uploads/2021/05/ICN2037_datasheet_EN_2017_V2.0.pdf)
- [74HC04 Datasheet (TI)](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf)
- [RUC7258 Info at Sekorm](https://en.sekorm.com/doc/1468121.html)
- [MW245 Datasheet](https://datasheet4u.com/datasheet-pdf/Sunmoon/MW245/pdf.php?id=1328898)
- [TC7262 Datasheet](https://www.alldatasheet.net/datasheet-pdf/pdf/1147196/FUMAN/TC7262.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | CLK_WIDE_PULSE | RB_SWAP
```

**Notes:**
- Primary chip for multi-panel displays. Tested extensively in chains and grid configurations.
- ICN2037BP is same as ICN2037 in SSOP24-P-150 package
- **128×64 panels:** Use 74HC245TS + 74HC04D + RUC7258D (Ruichips row driver)
- **64×64 Cube panels:** Use MW245B + TC7262BJ (same supporting chipset as Cyan/GS6238S panels)

---

### ICN2038S (No color label) - Road-Sign Display Panel

**Panel Model:** 64×64 (road-sign display panel)

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCDE (5) | 32 row addressing |
| Scan Rate | 1/8 | SCAN_4 flag |
| Max Clock | 20 MHz | |
| R/B Swap | No | **Different from ICN2037** |
| G/B Swap | No | |
| Wide Clock Pulse | **Yes** | |
| Init Required | No | |
| Latch Style | Enclosed | |
| Latch Position | Standard | |
| Multi-Panel | N/A | Single-ended panel (no daisy-chain by design) |

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | CLK_WIDE_PULSE | SCAN_4
```

**Notes:**
- Similar to ICN2037 but with 1/8 scan and **no R/B swap**
- SCAN_4 flag indicates special 1/8 scan pattern
- Commercial all-weather panel, single-ended construction
- Working in production road-sign display application

---

### MBI5124GP (Green PCBs)

**Panel Model:** P4-1921-8S-V2.0

**Panel Specifications:**
| Spec | Value |
|------|-------|
| Pixel Pitch | 4mm (P4) |
| LED Type | SMD1921 |
| Resolution | 64×32 pixels |
| Panel Size | 256mm × 128mm |
| Scan Mode | 1/8 scan |
| Interface | HUB75 |

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABC (3) | 8 row addressing |
| Scan Rate | 1/8 | Special scan pattern |
| Max Clock | 25 MHz | Per MBI5124 datasheet |
| R/B Swap | No | |
| G/B Swap | No | |
| Wide Clock Pulse | No | |
| Init Required | **Yes** | Special initialization |
| Latch Style | Enclosed (special) | Different from standard |
| Latch Position | End-enclosed | |
| Multi-Panel | **Untested** | Needs investigation |

**On-Board Chips:**
| Chip | Function | Details |
|------|----------|---------|
| MBI5124GP | LED column driver | 16-channel constant current (1-25mA), max 25MHz, ghosting elimination via pre-charge circuit, current accuracy ±2.5% |
| TC7258EN | Row driver | 8-channel line scanning blanking control, integrates 74HC138 decoder + 8 power tubes (2.5A, 130mΩ) |
| (Unknown) | Bus transceiver | Hidden under plastic housing - still investigating |

**Chip Detail Sources:**
- [MBI5124 Datasheet (Macroblock)](https://www.mblock.com.tw/upload/Datasheet/LED%20Driver%20IC/MBI5124/MBI5124%20Preliminary%20Datasheet_V1.01_EN.pdf)
- [MBI5124GP at LCSC](https://www.lcsc.com/product-detail/LED-Drivers_MBI5124GP_C82595.html)
- [TC7258EN Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1147175/FUMAN/TC7258EN.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | CHIP_UNK_LAT_END_ENCL | SCAN_4 | INIT_PANEL_REQUIRED
```

**Notes:**
- Uses `CHIP_UNK_LAT_END_ENCL` flag indicating special latch handling
- 1/8 scan creates complexity for multi-panel
- MBI5124 has built-in ghosting elimination (pre-charge circuit)
- Panel has both input and output HUB75 connectors (daisy-chain capable hardware)
- Some chips hidden under plastic LED housing - cannot visually identify
- **Multi-panel daisy-chain not yet working** - likely a timing/driver issue, not hardware

**Investigation Status:**
- Two panels available for testing
- Bus transceiver chip still unidentified (hidden under housing)
- Daisy-chain issue likely related to driver timing or 1/8 scan handling, not missing hardware
- May need additional timing or initialization investigation

---

### GS6238S (Cyan Label)

**Panel Model:** P2.5-16S-V1.0 (S210164-M00739)

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCD (4) | 16 row addressing |
| Scan Rate | 1/16 | Standard scan |
| Max Clock | 30 MHz | |
| R/B Swap | No | |
| G/B Swap | **Yes** | Green and Blue swapped |
| Wide Clock Pulse | No | |
| Init Required | No | |
| Latch Style | Offset | |
| Latch Position | Overlap | |
| Multi-Panel | Untested | |

**On-Board Chips:**
| Chip | Function | Details |
|------|----------|---------|
| GS6238S | LED column driver | LED driver with G/B swap characteristic |
| MW245B | Bus transceiver | Sunmoon 3-state octal bus transceiver, equivalent to 74HC245, CMOS/TTL compatible, ESD >8KV |
| TC7262BJ | Row driver | 8-channel line scanning with integrated 138 decoder + 8 power PMOS (2.5A, 120mΩ), supports 1-8 scan, anti-ghosting |

**Chip Detail Sources:**
- [MW245 Datasheet](https://datasheet4u.com/datasheet-pdf/Sunmoon/MW245/pdf.php?id=1328898)
- [TC7262 Datasheet](https://www.alldatasheet.net/datasheet-pdf/pdf/1147196/FUMAN/TC7262.html)

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | LAT_STYLE_OFFSET | LAT_POSN_OVERLAP | GB_SWAP
```

**Notes:** Uses different supporting chipset than Pink/Orange/Green panels - MW245B transceiver (Sunmoon) instead of 74HC245C, and TC7262BJ row driver instead of TC7258EN.

---

### DP5125D (No color label)

**Panel Model:** Unknown

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABC (3) | 8 row addressing |
| Scan Rate | 1/8 | Special scan pattern |
| Max Clock | Unknown | |
| R/B Swap | No | |
| G/B Swap | No | |
| Wide Clock Pulse | No | |
| Init Required | No | |
| Latch Style | Offset | |
| Latch Position | Overlap | |
| Multi-Panel | Untested | May work |

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | LAT_STYLE_OFFSET | LAT_POSN_OVERLAP | SCAN_4
```

---

## Driver Flag Reference

| Flag | Hex Value | Description |
|------|-----------|-------------|
| `LAT_STYLE_OFFSET` | $100 | Latch signal uses offset timing style |
| `LAT_POSN_OVERLAP` | $200 | Latch position overlaps with data clock |
| `INIT_PANEL_REQUIRED` | $400 | Panel requires special initialization sequence at power-up |
| `CLK_WIDE_PULSE` | $800 | Clock signal needs wider pulse (slower effective clock) |
| `RB_SWAP` | $1000 | Red and Blue color channels are physically swapped |
| `SCAN_4` | $2000 | Uses 1/8 scan pattern (4-line addressing for 8 rows) |
| `GB_SWAP` | $4000 | Green and Blue color channels are physically swapped |

---

## Chip Initialization Sequences

Some LED driver chips require special initialization sequences at power-up before they operate correctly. This section documents the known initialization requirements.

### FM6126A Initialization Sequence

The FM6126A requires initialization of two internal configuration registers before normal operation. This initialization must be performed once at power-up.

#### Register Structure

The FM6126A has at least two documented configuration registers accessed via a special latch timing mechanism:

| Register | Latch Timing | Purpose |
|----------|--------------|---------|
| REG11 | LE HIGH during last 11 CLKs | Brightness/gain settings |
| REG12 | LE HIGH during last 12 CLKs | Output enable control |

#### Register Bit Definitions

**Register 11 (Brightness/Gain):**
```
Bits:    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
         [ Lower Blank #1 ][  Intensity (6-bit)  ][ Inflection ][ LGC ][OE]
Default:  1  1  1  1  1  1  1  1  1  1  0  0  1  1  1  0  = 0xFFCE
Max Bright: 0  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  = 0x7FFF
```

**Register 12 (Output Enable):**
```
Bits:    15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
                              [OE]
Enable:   0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  = 0x0200
```

#### Simplified Init Values (Typical Use)

For 100% brightness with output enabled:
- **REG11**: Bit 0 = LOW, bits 1-15 = HIGH → `0x7FFE` or pattern `01111111 11111110`
- **REG12**: Only bit 9 = HIGH → `0x0200` or pattern `00000010 00000000`

#### Init Sequence Pseudocode

```
function FM6126A_Init(panel_width):
    # Setup
    OE = HIGH (outputs disabled)
    LATCH = LOW
    CLK = LOW

    # === Write REG11 (Brightness) ===
    for col in 0 to (panel_width - 1):
        bit_pos = col MOD 16

        # Set data: bit0=LOW, all others HIGH
        if bit_pos == 0:
            RGB_DATA = LOW (all color pins)
        else:
            RGB_DATA = HIGH (all color pins)

        # Assert LATCH during last 11 columns
        if col >= (panel_width - 11):
            LATCH = HIGH
        else:
            LATCH = LOW

        # Clock pulse
        CLK = HIGH
        wait(~30ns)
        CLK = LOW

    LATCH = LOW  # Latch data into REG11
    wait(~1us)

    # === Write REG12 (Output Enable) ===
    for col in 0 to (panel_width - 1):
        bit_pos = col MOD 16

        # Set data: only bit9=HIGH
        if bit_pos == 9:
            RGB_DATA = HIGH
        else:
            RGB_DATA = LOW

        # Assert LATCH during last 12 columns
        if col >= (panel_width - 12):
            LATCH = HIGH
        else:
            LATCH = LOW

        # Clock pulse
        CLK = HIGH
        wait(~30ns)
        CLK = LOW

    LATCH = LOW  # Latch data into REG12
    OE = LOW     # Enable outputs
```

#### Key Timing Notes

- Data is clocked to ALL RGB pins simultaneously (R1, G1, B1, R2, G2, B2)
- This configures all FM6126A chips across the panel in parallel
- Clock rate during init can be slower than normal operation
- LATCH assertion timing is critical: must be exactly 11 or 12 clocks from end
- For multi-panel chains, `panel_width` = total columns across all panels

#### References

- [rpi-rgb-led-matrix FM6126A discussion](https://github.com/hzeller/rpi-rgb-led-matrix/issues/746)
- [ESP32-HUB75-MatrixPanel-DMA implementation](https://github.com/mrcodetastic/ESP32-HUB75-MatrixPanel-DMA)
- Driver implementation: `isp_hub75_rgb3bit.spin2:resetPanelFM6126()`

---

### MBI5124 Initialization Sequence

The MBI5124 (including MBI5124GP variant) has a configuration register for ghosting elimination settings. Unlike FM6126A, it uses a different command protocol based on CLK pulses while LE is HIGH.

#### Command Protocol

The MBI5124 interprets commands based on the number of CLK rising edges while LE (Latch Enable) is HIGH:

| CLK Edges (LE=HIGH) | Command | Description |
|---------------------|---------|-------------|
| 0 | Latch Data | Transfer shift register to output latch |
| 1 | Latch Buffer | Transfer buffer data to output latch |
| **4** | **Write Config** | Write shift register data to configuration register |
| 5 | Read Config | Shift out configuration register to SDO |
| 2, 3, >5 | No Action | Reserved/unused |

#### Configuration Register (16-bit)

Different configuration values are needed for each LED color channel:

| LED Color | Binary (MSB→LSB) | Hex |
|-----------|------------------|-----|
| **Red** | `0111 1101 0110 1011` | `0x7D6B` |
| **Green** | `1111 0001 0110 1011` | `0xF16B` |
| **Blue** | `1110 1101 0110 1011` | `0xED6B` |

**Common bits across all colors:**
- Bits 0-5: `101011` = Common settings
- Bits 6-9: Variable per color

#### Pre-charge Waveform

The MBI5124's ghosting elimination works via a pre-charge circuit controlled by OE timing:
```
OE  _____|‾‾‾‾‾‾‾‾‾‾‾|_____
         Pre-charge active

OUTn _____|‾‾‾‾‾‾‾‾‾|_______
          LED current
```

#### Init Sequence Pseudocode

```
# Configuration values per LED color
CONFIG_RED   = 0x7D6B  # 0111 1101 0110 1011
CONFIG_GREEN = 0xF16B  # 1111 0001 0110 1011
CONFIG_BLUE  = 0xED6B  # 1110 1101 0110 1011

function MBI5124_Init(panel_width):
    # Each MBI5124 chip is 16 channels wide
    # Number of chips per color = panel_width / 16
    # For 64-wide panel: 4 chips per color (R, G, B = 12 chips total per half-panel)

    chips_per_color = panel_width / 16

    # Setup - disable outputs during init
    OE = HIGH (outputs disabled)
    LE = LOW
    CLK = LOW

    # === Configure RED channel driver chain ===
    # Shift config value through all RED chips in chain
    for chip in 0 to (chips_per_color - 1):
        # Shift 16 bits into this chip (and push previous chips' data forward)
        for bit in 15 downto 0:
            # Set R1 and R2 data pins to config bit value
            R1_DATA = (CONFIG_RED >> bit) AND 1
            R2_DATA = (CONFIG_RED >> bit) AND 1
            # G and B pins can be LOW during RED config
            G1_DATA = LOW
            G2_DATA = LOW
            B1_DATA = LOW
            B2_DATA = LOW

            wait(~5ns)  # Setup time
            CLK = HIGH  # Rising edge shifts data
            wait(~20ns)
            CLK = LOW
            wait(~20ns)

    # Write to configuration register - 4 CLK pulses while LE=HIGH
    LE = HIGH
    for pulse in 1 to 4:
        CLK = HIGH
        wait(~20ns)
        CLK = LOW
        wait(~20ns)
    LE = LOW  # Falling edge commits config to all RED chips

    wait(~1us)  # Delay between color configs

    # === Configure GREEN channel driver chain ===
    for chip in 0 to (chips_per_color - 1):
        for bit in 15 downto 0:
            R1_DATA = LOW
            R2_DATA = LOW
            G1_DATA = (CONFIG_GREEN >> bit) AND 1
            G2_DATA = (CONFIG_GREEN >> bit) AND 1
            B1_DATA = LOW
            B2_DATA = LOW

            wait(~5ns)
            CLK = HIGH
            wait(~20ns)
            CLK = LOW
            wait(~20ns)

    # Write config - 4 CLK pulses while LE=HIGH
    LE = HIGH
    for pulse in 1 to 4:
        CLK = HIGH
        wait(~20ns)
        CLK = LOW
        wait(~20ns)
    LE = LOW

    wait(~1us)

    # === Configure BLUE channel driver chain ===
    for chip in 0 to (chips_per_color - 1):
        for bit in 15 downto 0:
            R1_DATA = LOW
            R2_DATA = LOW
            G1_DATA = LOW
            G2_DATA = LOW
            B1_DATA = (CONFIG_BLUE >> bit) AND 1
            B2_DATA = (CONFIG_BLUE >> bit) AND 1

            wait(~5ns)
            CLK = HIGH
            wait(~20ns)
            CLK = LOW
            wait(~20ns)

    # Write config - 4 CLK pulses while LE=HIGH
    LE = HIGH
    for pulse in 1 to 4:
        CLK = HIGH
        wait(~20ns)
        CLK = LOW
        wait(~20ns)
    LE = LOW

    # Init complete - enable outputs
    OE = LOW
```

#### Alternative: All Colors Simultaneously

Since CLK and LE are shared across all color channels, you can configure all colors in parallel:

```
function MBI5124_Init_Parallel(panel_width):
    chips_per_color = panel_width / 16

    OE = HIGH
    LE = LOW
    CLK = LOW

    # Shift config values to ALL color channels simultaneously
    for chip in 0 to (chips_per_color - 1):
        for bit in 15 downto 0:
            # Each color gets its own config value on its data pins
            R1_DATA = (CONFIG_RED >> bit) AND 1
            R2_DATA = (CONFIG_RED >> bit) AND 1
            G1_DATA = (CONFIG_GREEN >> bit) AND 1
            G2_DATA = (CONFIG_GREEN >> bit) AND 1
            B1_DATA = (CONFIG_BLUE >> bit) AND 1
            B2_DATA = (CONFIG_BLUE >> bit) AND 1

            wait(~5ns)
            CLK = HIGH  # All colors shift on same clock
            wait(~20ns)
            CLK = LOW
            wait(~20ns)

    # Single config write applies to ALL color channels
    LE = HIGH
    for pulse in 1 to 4:
        CLK = HIGH
        wait(~20ns)
        CLK = LOW
        wait(~20ns)
    LE = LOW

    OE = LOW
```

**Note:** The parallel method is faster but requires that all color data pins can be set independently. Most HUB75 implementations support this.

#### Clock Phase Requirement

**Critical:** MBI5124 requires positive-edge clocking:
- Data shifts on CLK **rising edge**
- LE signal resets on CLK rising edge while HIGH
- Set `clkphase = true` in software drivers

This differs from many other HUB75 drivers that use falling-edge clocking.

#### Key Timing Specifications (from Datasheet)

| Parameter | Symbol | Min | Typ | Max | Unit |
|-----------|--------|-----|-----|-----|------|
| Clock frequency | fCLK | - | - | 25 | MHz |
| Clock pulse width | tw(CLK) | 20 | - | - | ns |
| LE pulse width | tw(L) | 20 | - | - | ns |
| OE pulse width | tw(OE) | 45 | 55 | 65 | ns |
| Setup time (SDI) | tsu(D) | 3 | - | - | ns |
| Hold time (SDI) | th(D) | 5 | - | - | ns |
| Setup time (LE) | tsu(L) | 5 | - | - | ns |
| Hold time (LE) | th(L) | 5 | - | - | ns |

#### Multi-Panel Considerations

For MBI5124 daisy-chain operation:
1. Each panel in chain must receive the init sequence
2. Configuration data shifts through SDI→SDO chain
3. All panels configured with same LE pulse (4 CLK edges)
4. May need to shift `N × 16` bits for N chips in chain
5. Clock integrity critical due to rising-edge sensitivity

#### References

- [MBI5124 Datasheet (Macroblock)](https://datasheet.lcsc.com/lcsc/1808081643_MBI-MBI5124GP-B_C256866.pdf)
- [ESP32-HUB75-MatrixPanel-DMA MBI5124 notes](https://github.com/mrcodetastic/ESP32-HUB75-MatrixPanel-DMA)
- Driver implementation: `isp_hub75_rgb3bit.spin2:resetPanelMBI5124()` (stub)

---

### Chips Without Initialization

The following chips do NOT require special initialization sequences:

| Chip | Notes |
|------|-------|
| FM6124 | Simpler variant of FM6126A, no init needed |
| FM6124C | Variant of FM6124 |
| ICN2037 / ICN2037BP | Works immediately at power-up |
| ICN2038S | Similar to ICN2037 |
| GS6238S | No init sequence |
| DP5125D | No init sequence |

These chips operate as standard shift registers - clock in data, latch, enable outputs.

---

## Scan Rate / Address Line Relationship

| Address Lines | Rows Addressed | Typical Scan | Panel Height |
|---------------|----------------|--------------|--------------|
| ABC (3) | 8 | 1/8 | 16, 32 rows |
| ABCD (4) | 16 | 1/16 | 32, 64 rows |
| ABCDE (5) | 32 | 1/32 | 64, 128 rows |

**How scan works:**
- Panel is divided into sections
- Each scan cycle displays one section
- Higher scan rate = more sections = dimmer per-cycle but higher refresh
- 1/8 scan: Display shows 1/8 of rows at a time, cycles 8x per frame
- 1/16 scan: Display shows 1/16 of rows at a time, cycles 16x per frame
- 1/32 scan: Display shows 1/32 of rows at a time, cycles 32x per frame

---

## Latch Timing Styles

### Standard Latch
- Latch signal pulses after all column data is clocked
- Used by: FM6124

### Offset + Overlap Latch
- Latch timing is offset from data
- Latch may overlap with next row's data
- Used by: FM6126A, GS6238S, DP5125D

### Enclosed Latch
- Latch signal enclosed within data timing
- Latch occurs at end of data sequence
- Used by: ICN2037, ICN2038S

### End-Enclosed (Special)
- Special handling for latch at sequence end
- May require specific timing
- Used by: MBI5124GP

---

## Multi-Panel Daisy-Chain Requirements

For successful multi-panel daisy-chaining:

1. **Data Propagation**: Each panel must cleanly pass data to the next
2. **Clock Integrity**: Clock signal must maintain integrity through chain
3. **Latch Synchronization**: All panels must latch simultaneously
4. **Initialization**: If init required, each panel may need individual init

### Known Working Configurations
- FM6126A (Pink): Chains tested
- ICN2037: Chains and 2D grids tested

### Investigation Needed
- **MBI5124GP (Green)**: Two panels not daisy-chaining
  - Possible causes:
    - Special latch timing not propagating correctly
    - 1/8 scan timing issues between panels
    - Initialization sequence needs to be per-panel
    - Clock/data signal degradation

---

## Adding New Chip Support

To add support for a new chip:

1. Identify the chip's characteristics:
   - Address lines (ABC/ABCD/ABCDE)
   - Scan rate (1/8, 1/16, 1/32)
   - Color swapping (R/B, G/B)
   - Clock requirements
   - Initialization needs
   - Latch timing style

2. Add chip constant to `isp_hub75_hwEnums.spin2`:
   ```spin2
   #0, CHIP_UNKNOWN, CHIP_MANUAL_SPEC, ..., CHIP_NEW_CHIP
   ```

3. Add flag combination to `getDriverFlags()` in `isp_hub75_hwBufferAccess.spin2`:
   ```spin2
   elseif eChipType == hwEnum.CHIP_NEW_CHIP
       desiredFlags := hwEnum.CHIP_MANUAL_SPEC | {required flags}
   ```

4. If chip needs special handling, modify the PASM driver in `isp_hub75_rgb3bit.spin2`

---

*Last Updated: December 2024*
