# ICN2037 Technical Reference

## Overview

The ICN2037 is a 16-channel constant current LED sink driver with dual latch, manufactured by Chipone Technology (Beijing) Co., Ltd. This document provides implementation-critical specifications for driving HUB75 LED panels using this chip.

**Document Sources:**
- `ICN2037_datasheet_EN_2017_V2.0.pdf` - Primary datasheet (V2.0, Nov 2017)
- `ICN2037-timing.pdf` - Supplementary timing diagrams
- `hub75-adaptor-v1.4-schematic.pdf` - P2 Eval HUB75 Adapter Board schematic
- [TI SN74HCT244 Datasheet](https://www.ti.com/lit/ds/symlink/sn74hct244.pdf) - Level shifter specifications

---

## 1. ICN2037 Pin Functions

| Pin | Name | Function |
|-----|------|----------|
| 1 | GND | Power Ground |
| 2 | SIN | Serial data input |
| 3 | CLK | Clock input - data shifts on **rising edge** |
| 4 | LE | Latch Enable - edge triggered |
| 5-20 | OUT0-OUT15 | Constant current outputs (active LOW sink) |
| 21 | OE | Output Enable - **ACTIVE LOW** |
| 22 | SOUT | Serial data output to next IC |
| 23 | R-EXT | External resistor for current setting |
| 24 | VDD | Power supply (3.3V-5V) |

### Critical Signal Polarities

| Signal | Active State | Description |
|--------|-------------|-------------|
| **OE** | **LOW** | Outputs ON when OE=LOW; Outputs OFF when OE=HIGH |
| **LE** | **HIGH** | Data transfers to latch when LE=HIGH; Data held when LE=LOW |
| **CLK** | Rising Edge | Data shifts into register on rising edge |

---

## 2. Timing Specifications

### 2.1 ICN2037 Timing Parameters

*Sources: ICN2037_datasheet_EN_2017_V2.0.pdf (pages 7-8), ICN2037-timing.pdf (page 2)*

| Parameter | Symbol | Min | Typ | Max | Unit | Notes |
|-----------|--------|-----|-----|-----|------|-------|
| **Clock Frequency** | FCLK | - | - | 30 | MHz | Datasheet max; see calculation below |
| **Clock Pulse Width** | twCLK | 20 | - | - | ns | High or Low state |
| **Latch Pulse Width** | twLE | 20 | - | - | ns | LE=HIGH duration |
| **OE Pulse Width** | twOE | **60** | - | - | ns | Min enable/disable time |
| **Data Setup Time** | tSETUP1/2 | 5 | - | - | ns | SIN stable before CLK rising |
| **Data Hold Time** | tHOLD1/2 | 5 | - | - | ns | SIN stable after CLK rising |
| **Clock Rise/Fall Time** | tr/tf | - | - | 500 | ns | Maximum allowed |

**Note:** The timing PDF clarifies OE minimum pulse width is **60ns** (not 40ns). This is critical for proper blanking.

### 2.2 Propagation Delays

*Source: ICN2037_datasheet_EN_2017_V2.0.pdf, page 9*

| Parameter | Symbol | Min | Typ | Max | Unit |
|-----------|--------|-----|-----|-----|------|
| OE→OUT0 (enable) | tpLH3 | - | 32 | 46 | ns |
| OE→OUT1 (disable) | tpHL3 | - | 45 | 49 | ns |
| CLK→SOUT | tpHL | - | 32 | 35 | ns |
| Output Rise Time | tor | - | 30 | 35 | ns |
| Output Fall Time | tof | - | 45 | 50 | ns |

### 2.3 Minimum Clock Period Calculation

*Source: ICN2037-timing.pdf (page 2, annotated diagram)*

```
Minimum CLK period = 2 × twCLK = 2 × 20ns = 40ns
Maximum CLK frequency = 1 / 40ns = 25 MHz

Note from timing PDF: "CLK: 2x 20ns = 40 ns = 25 MHz"
This confirms 25 MHz as the practical maximum.
```

The timing PDF explicitly calculates 25 MHz as the maximum, despite the datasheet listing 30 MHz. Use 20-25 MHz for reliable operation.

---

## 3. Signal Chain Timing Budget

### 3.1 74HCT244 Level Shifter Specifications

*Source: [TI SN74HCT244 Datasheet](https://www.ti.com/lit/ds/symlink/sn74hct244.pdf), [Nexperia 74HCT244 Datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT244.pdf)*

The P2 Eval HUB75 Adapter Board uses two 74HCT244 octal buffers to level-shift P2's 3.3V signals to 5V for the HUB75 interface.

| Parameter | Symbol | Min | Typ | Max | Unit |
|-----------|--------|-----|-----|-----|------|
| Supply Voltage | VCC | 4.5 | 5.0 | 5.5 | V |
| Propagation Delay | tpd | - | 11-13 | 22 | ns |
| Enable Time | ten | - | 15 | 30 | ns |
| Disable Time | tdis | - | 15 | 25 | ns |
| Transition Time | tt | - | 5 | 12 | ns |
| **Effective Max Frequency** | - | - | - | ~45 | MHz |

### 3.2 Total Signal Path Delay

```
P2 Pin → 74HCT244 → HUB75 Cable → ICN2037

Worst-case delays:
  74HCT244 propagation:     22 ns (max)
  Cable delay (~30cm):       2 ns (estimated)
  ICN2037 setup margin:      5 ns
  ─────────────────────────────────
  Total one-way delay:      29 ns

For 20 MHz clock (50ns period):
  Available margin = 50ns - 29ns = 21ns  ✓ ADEQUATE

For 30 MHz clock (33ns period):
  Available margin = 33ns - 29ns = 4ns   ⚠ TIGHT
```

### 3.3 Panel Support Chip Timing

The signal path doesn't end at the HUB75 cable - panel support chips add additional propagation delays before signals reach the ICN2037.

#### 3.3.1 74HC245 Bus Transceiver (Data Path)

*Source: [Nexperia 74HC245 Datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT245.pdf)*

The 74HC245TS on the 128×64 panel buffers data signals and enables daisy-chain output:

| Parameter | Symbol | Typ @ 5V | Max @ 4.5V | Unit | Notes |
|-----------|--------|----------|------------|------|-------|
| **Propagation Delay** | tpd | 7 | 18 | ns | Data and CLK path |
| Enable Time | ten | 11 | 30 | ns | From OE active |
| Disable Time | tdis | 15 | 30 | ns | To OE inactive |
| Transition Time | tt | 5 | 12 | ns | Rise/fall |

**Critical observation**: At 5V (typical panel operation), typical delay is only 7ns. Worst-case is 18ns.

#### 3.3.2 74HC04 Hex Inverter (Signal Conditioning)

*Source: [TI SN74HC04 Datasheet](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf), [Nexperia 74HC04 Datasheet](https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf)*

The 74HC04D provides signal conditioning (likely CLK buffering, OE inversion):

| Parameter | Symbol | Typ @ 5V | Max @ 4.5V | Unit | Notes |
|-----------|--------|----------|------------|------|-------|
| **Propagation Delay** | tpd | 7 | 17 | ns | Per gate |
| Transition Time | tt | 5 | 15 | ns | Rise/fall |

**Note**: If CLK passes through the inverter, add this delay. If used for other signals (OE, addresses), timing is less critical since those change at row rate, not clock rate.

#### 3.3.3 Row Driver ICs (Address Path Only)

**RUC7258D** (Ruichips) / **TC7262BJ** (Fuman): These are 8-channel row drivers with anti-ghosting features.

| Parameter | Typ | Max | Unit | Notes |
|-----------|-----|-----|------|-------|
| Estimated tpd | 15 | 40 | ns | Based on similar parts |

**Important**: Row drivers are NOT in the CLK/data critical path. They only need to complete row switching before OE goes LOW. Address lines change at ~20-60 kHz (row rate), not 20 MHz (CLK rate), so row driver timing is not the limiting factor.

### 3.4 Complete Signal Path Timing

The full timing budget must account for all chips in the signal path:

```
P2 Pin → 74HCT244 (adapter) → HUB75 Cable → 74HC245 (panel) → ICN2037

                    WORST CASE              TYPICAL
  ┌─────────────┐
  │ P2 Output   │      0 ns                   0 ns
  └─────┬───────┘
        ↓
  ┌─────────────┐
  │ 74HCT244    │     22 ns                  13 ns   (adapter level shifter)
  └─────┬───────┘
        ↓
  ┌─────────────┐
  │ HUB75 Cable │      2 ns                   2 ns   (~30cm cable)
  └─────┬───────┘
        ↓
  ┌─────────────┐
  │ 74HC245     │     18 ns                   7 ns   (panel buffer)
  └─────┬───────┘
        ↓
  ┌─────────────┐
  │ ICN2037     │      5 ns                   5 ns   (setup time)
  └─────────────┘
        ═══════════════════════════════════════
  TOTAL ONE-WAY:      47 ns                  27 ns
```

**If CLK passes through 74HC04 instead of 74HC245:**
```
  Add 74HC04:         17 ns (max)             7 ns (typ)
  TOTAL ONE-WAY:      49 ns                  27 ns  (approximately same)
```

### 3.5 Revised Maximum Frequency Analysis

| Scenario | One-Way Delay | CLK Period Required | Max Frequency |
|----------|---------------|---------------------|---------------|
| **Worst-case (cold start)** | 47 ns | 94 ns | **10.6 MHz** |
| **Typical @ 25°C** | 27 ns | 54 ns | **18.5 MHz** |
| **Conservative margin** | 35 ns | 70 ns | **14.3 MHz** |

**Key finding**: When including panel support chips, the worst-case timing budget suggests a more conservative clock frequency than the ICN2037 datasheet implies.

### 3.6 Recommended Operating Frequency (Final)

| Application | Recommended CLK | Notes |
|-------------|-----------------|-------|
| **Safe (all conditions)** | **15 MHz** | Works at temperature extremes |
| **Standard** | 20 MHz | Good margin at room temperature |
| **Maximum** | 25 MHz | Datasheet limit, minimal margin |

**Important**: The "30 MHz max" from the ICN2037 datasheet does NOT account for panel support chips. Real-world panels with 74HC245 buffers should use ≤20 MHz for reliable operation.

---

## 4. Dual Latch Operation

*Source: ICN2037-timing.pdf (page 1)*

The ICN2037 features a dual latch architecture for higher refresh rates:

```
SIN → [16-bit Shift Register (reg1)] → SOUT
              ↓
       [16-bit Latch (latch1)]
              ↓
       [16-bit Output Register (reg2)]
              ↓
       [16-bit Output Driver] → OUT0-OUT15
```

### 4.1 Standard Operation Sequence

1. **Shift in data**: Clock 16 bits into shift register (SIN/CLK)
2. **Latch data**: Pulse LE HIGH to transfer to latch
3. **Enable outputs**: Set OE LOW to enable LED outputs
4. **Overlap**: Can shift next row's data while displaying current row

### 4.2 Pipelined Operation (High Refresh Rate)

The timing PDF details how to overlap data transfer with display for maximum refresh:

| Step | Action | OE State | Notes |
|------|--------|----------|-------|
| 1 | Transfer data(A), pulse LE | HIGH (off) | Panel blanked during transfer |
| 2 | OE→LOW, display data(A) | LOW (on) | Outputs enabled |
| 3 | While displaying A, transfer data(B) | LOW (on) | **Overlap** |
| 4 | Pulse LE to latch B, start transfer C | LOW (on) | B ready in latch1 |
| 5 | OE→HIGH (blank), register B, OE→LOW | HIGH→LOW | Switch to B |
| 6 | Display B, complete transfer C | LOW (on) | Continue pipeline |
| 7 | Repeat from step 4 | - | Continuous |

**Key insight**: Data can be transmitted AND latched while OE=HIGH (panel off). The "(panel is off)" annotations in the timing diagram show blanking periods.

### 4.3 Timing Diagram

```
        ┌─────────16 clocks─────────┐
CLK     ─┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬┴┬─────────────
SIN     ═╪D15╪D14╪...╪D1╪D0╪════════════════════════
LE      ────────────────────────────┐┌──────────────
                                    └┘ (20ns+ pulse)
OE      ────────────────────────────────┐┌──────────
                                        └┘ (60ns+ blank)
OUT     ════════════════════════════════╪ NEW DATA ╪
```

**Critical timing**: OE blanking pulse must be ≥60ns for proper row switching.

---

## 5. HUB75 Interface Mapping

### 5.1 P2 Eval HUB75 Adapter Pin Assignment

*Source: hub75-adaptor-v1.4-schematic.pdf*

| HUB75 Signal | 74HCT244 Output | P2 Pin (J2) | Function |
|--------------|-----------------|-------------|----------|
| R1 | U1-1Y1 | p8+1 | Red data, upper half |
| G1 | U1-1Y0 | p8+0 | Green data, upper half |
| B1 | U1-1Y3 | p8+3 | Blue data, upper half |
| R2 | U1-1Y2 | p8+2 | Red data, lower half |
| G2 | U1-2Y0 | p8+5 | Green data, lower half |
| B2 | U1-2Y3 | p8+4 | Blue data, lower half |
| A | U2-1A2 | p0+2 | Row address bit 0 |
| B | U2-2A2 | p0+4 | Row address bit 1 |
| C | U2-2A3 | p0+5 | Row address bit 2 |
| D | U2-2A0 | p0+7 | Row address bit 3 |
| E | U2-2A1 | p0+6 | Row address bit 4 |
| CLK | U2-1A0 | p0+3 | Pixel clock |
| LAT/STB | U2-1A3 | p0+1 | Latch strobe |
| OE | U2-1A1 | p0+0 | Output enable |

### 5.2 Panel Geometry for 128x64 Panels

| Parameter | Value | Notes |
|-----------|-------|-------|
| Panel Width | 128 pixels | |
| Panel Height | 64 pixels | |
| Scan Rate | 1/32 | 32 rows, address lines A-E |
| ICN2037 chips per row | 8 | 128 pixels / 16 channels |
| Bits per row (one color) | 128 | |
| Bits per row (RGB) | 384 | 128 × 3 colors |

### 5.3 Addressing

For a 1/32 scan panel with 64 rows:
- Address lines: A, B, C, D, E (5 bits = 32 addresses)
- Each address drives 2 rows simultaneously (upper/lower half)
- Upper half: rows 0-31 via R1/G1/B1
- Lower half: rows 32-63 via R2/G2/B2

---

## 6. Panels Using ICN2037

This section documents the specific LED panel models that use the ICN2037 chip family, along with their supporting chipsets.

### 6.1 Panel: P2-1515-128X64-32S-S2 (128×64)

**Panel Identification:**
| Field | Value |
|-------|-------|
| Model | P2-1515-128X64-32S-S2 |
| Serial/Batch | 2210BP201-88-60 |
| Pixel Pitch | 2mm (P2) |
| LED Type | SMD1515 |
| Resolution | 128×64 pixels (8,192 total) |
| Scan Mode | 1/32 scan (32S) |

**On-Board Chipset:**

| Chip | Designator | Qty | Function | Key Specifications |
|------|------------|-----|----------|-------------------|
| **ICN2037BP** | - | 16 | LED column driver | 16-channel constant current sink, dual latch, max 30MHz, ±2.5% accuracy |
| **74HC245TS** | U1, U2, U4 | 3 | Bus transceiver | Octal 3-state bidirectional, TSSOP package, buffers input + daisy-chain output |
| **74HC04D** | U5 | 1 | Hex inverter | 6 inverters for signal conditioning/buffering |
| **RUC7258D** | - | 2 | Row driver | Ruichips 8-channel blanking control, 2.8A max, anti-ghosting |

**Panel Geometry:**
```
┌─────────────────────────────────────────┐
│              128 pixels                 │
│  ┌───────────────────────────────────┐  │
│  │ Upper half (rows 0-31)            │  │ 32 rows
│  │ Driven by R1/G1/B1                │  │
│  ├───────────────────────────────────┤  │
│  │ Lower half (rows 32-63)           │  │ 32 rows
│  │ Driven by R2/G2/B2                │  │
│  └───────────────────────────────────┘  │
│              64 rows total              │
└─────────────────────────────────────────┘
```

**ICN2037BP Arrangement:**
- 8 chips per row × 2 rows (RGB) = 16 ICN2037BP chips total
- 128 pixels ÷ 16 channels = 8 chips per color per half-panel

**Chip Detail Sources:**
- [74HC245 Datasheet (Nexperia)](https://assets.nexperia.com/documents/data-sheet/74HC_HCT245.pdf)
- [74HC04 Datasheet (TI)](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf)
- [RUC7258 Info (Sekorm)](https://en.sekorm.com/doc/1468121.html)

---

### 6.2 Panel: P2-2020210240-200 (64×64 Cube)

**Panel Identification:**
| Field | Value |
|-------|-------|
| Model | P2-2020210240-200 |
| Label | E506652 DCHY-M |
| Serial Numbers | S210350H00127, S210350H00112, etc. (6 panels) |
| Pixel Pitch | 2mm (P2) |
| Resolution | 64×64 pixels (4,096 total) |
| Scan Mode | 1/32 scan |

**On-Board Chipset:**

| Chip | Function | Key Specifications |
|------|----------|-------------------|
| **ICN2037BP** | LED column driver | 16-channel constant current sink, dual latch |
| **MW245B** | Bus transceiver | Sunmoon 3-state octal transceiver, ESD >8KV |
| **TC7262BJ** | Row driver | Fuman 8-channel with anti-ghosting, 2.5A/120mΩ |

**Note:** These 64×64 panels use a different supporting chipset (MW245B + TC7262BJ) than the 128×64 panels, which is the same chipset used on GS6238S (Cyan) panels.

**Chip Detail Sources:**
- [MW245 Datasheet](https://datasheet4u.com/datasheet-pdf/Sunmoon/MW245/pdf.php?id=1328898)
- [TC7262 Datasheet](https://www.alldatasheet.net/datasheet-pdf/pdf/1147196/FUMAN/TC7262.html)

---

### 6.3 Common Characteristics

Both panel types share these ICN2037-specific characteristics:

| Characteristic | Value | Notes |
|----------------|-------|-------|
| Address Lines | ABCDE (5) | 32 row addressing |
| Scan Rate | 1/32 | Full scan |
| Max Clock | 20 MHz | Wide pulse recommended |
| **R/B Swap** | **Yes** | Red and Blue channels physically swapped |
| G/B Swap | No | |
| Wide Clock Pulse | **Yes** | `CLK_WIDE_PULSE` flag |
| Init Required | No | Works immediately at power-up |
| Latch Style | Enclosed | Latch at end of data |

**Driver Flags:**
```spin2
CHIP_MANUAL_SPEC | CLK_WIDE_PULSE | RB_SWAP
```

---

## 7. Driver Configuration Mapping

### 7.1 Required Driver Constants

Based on ICN2037 specifications, the following driver configuration values should be used:

| Driver Constant | Recommended Value | Reason |
|-----------------|-------------------|--------|
| `CHIP_TYPE` | `CHIP_ICN2037` | Identifies chip family |
| `ADDR_LINES` | 5 (ABCDE) | 1/32 scan requires 5 address lines |
| `CLK_FREQ` | 20-25 MHz | Conservative timing margin |
| `LATCH_STYLE` | Standard | No special init sequence needed |
| `OE_POLARITY` | Active LOW | OE=0 enables outputs |
| `LATCH_POLARITY` | Active HIGH | LE pulse HIGH to latch |
| `CLK_EDGE` | Rising | Data shifts on CLK rising edge |

### 7.2 Chip Family Compatibility

The ICN2037 is compatible with:
- **ICN2037BP** - Same chip, different package option
- **ICN2038S** - Similar, may have minor timing differences

### 7.3 Features to Enable

| Feature | Enable? | Notes |
|---------|---------|-------|
| Pre-charge (ghosting reduction) | Built-in | ICN2037 handles internally |
| Dual latch | Built-in | Use for higher refresh |
| Special init sequence | NO | Not required (unlike FM6126A) |

---

## 8. Observed Symptoms vs. Expected Behavior

### Current Issues (from testing):

| Symptom | Expected | Observed | Likely Cause |
|---------|----------|----------|--------------|
| Clock speed | 20 MHz | 833 kHz | Clock generation ~24× too slow |
| LAT/OE | Proper sequencing | Incorrect | Control signal timing wrong |
| Display | Correct orientation | Upside down | Coordinate transform issue |
| Refresh | Continuous | 103ms bursts | PWM loop not continuous |

### Signal Requirements Checklist:

- [ ] CLK: 20-25 MHz, clean edges
- [ ] SIN: Valid data 5ns before CLK rising edge
- [ ] LE: 20ns+ pulse after last CLK of row
- [ ] OE: LOW during display, HIGH during row switch (blanking)
- [ ] Address: Stable before OE goes LOW

---

## 9. References

### Primary Sources (Local)
1. **ICN2037 Datasheet** - `ICN2037_datasheet_EN_2017_V2.0.pdf` (Chipone, V2.0 Nov 2017)
2. **ICN2037 Timing Summary** - `ICN2037-timing.pdf` (supplementary)
3. **HUB75 Adapter Schematic** - `hub75-adaptor-v1.4-schematic.pdf` (Iron Sheep Productions)
4. **Chip Characteristics Matrix** - `../ChipCharacteristicsMatrix.md` (panel/chipset catalog)
5. **Author Test Configurations** - `../AuthorTestConfigurations.md` (panel test documentation)

### External Datasheets
6. **74HCT244 Datasheet** - [Texas Instruments](https://www.ti.com/lit/ds/symlink/sn74hct244.pdf)
7. **74HCT244 Datasheet** - [Nexperia](https://assets.nexperia.com/documents/data-sheet/74HC_HCT244.pdf)
8. **74HC245 Datasheet** - [Nexperia](https://assets.nexperia.com/documents/data-sheet/74HC_HCT245.pdf)
9. **74HC04 Datasheet** - [Texas Instruments](https://www.ti.com/lit/ds/symlink/sn74hc04.pdf)
10. **RUC7258 Info** - [Sekorm](https://en.sekorm.com/doc/1468121.html)
11. **MW245 Datasheet** - [Datasheet4U](https://datasheet4u.com/datasheet-pdf/Sunmoon/MW245/pdf.php?id=1328898)
12. **TC7262 Datasheet** - [AllDatasheet](https://www.alldatasheet.net/datasheet-pdf/pdf/1147196/FUMAN/TC7262.html)

---

*Document generated: 2025-01-06*
*Driver version target: v3.x+*
