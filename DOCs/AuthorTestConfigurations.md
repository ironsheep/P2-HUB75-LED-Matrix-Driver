# Author's Test Panel Configurations

This document catalogs all panel configurations the author has tested, as documented in `isp_hub75_hwPanelConfig.spin2`.

Each configuration below is shown as the `DISP0_` settings that describe it: the adapter's pin group, chip, address lines and panel size, plus the wiring sentence for each panel (`DISP0_C0` ... `DISP0_C15`; a position not shown is `hwEnum.NO_PANEL`). How the sentences work is in the [Wiring Guide](WiringGuide.md). **Scan** is written *1/S scan*, where S is the number of row addresses the address lines select, as defined in the [glossary](../THEOPS.md#scan). The **Multi-Panel** status says whether multi-panel use has been proven on hardware; how many panels one adapter can drive for each panel type is in the [driver limits table](WiringGuide.md#driver-limits).

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
| 12 | (road-sign panel) | - | 64×64 | ICN2038S | ABCDE | P0-P15 | N/A (single-ended) | Scan setting disputed (see Configuration 12) |

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
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 32
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ✅ Working in multi-panel chains (the panels need the initialization sequence). A row of four of these is [Example 1](WiringGuide.md#example-1-a-row-of-4) in the Wiring Guide; the number of panels one adapter can drive is in the [driver limits table](WiringGuide.md#driver-limits) (calculated, not yet exercised at that count).

**4.0.0 refresh core:** ✅ verified on one panel (2026-10-05) at 8-bit and 5-bit: correct image on the test patterns, refresh 85.1 Hz at 8-bit and 688.9 Hz at 5-bit; figures in the [Wiring Guide](WiringGuide.md#measured-refresh).

---

### Configuration 4: FM6124 64×32 Panels (Hackerbox)

**Panel Model:** P3-6432-2121-16S-D1.0 (orange labels)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: 1/16
- Driver Chip: FM6124 (from Hackerbox kit)
- Address Lines: ABCD (4 lines)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6124
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 32
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ❌ Single panel only; multi-panel is untested. The driver's limit for this panel type is in the [driver limits table](WiringGuide.md#driver-limits).

**4.0.0 refresh core:** ✅ verified on one panel (2026-10-05) at 8-bit and 5-bit: correct image on the test patterns, refresh 85.3 Hz at 8-bit and 694.1 Hz at 5-bit; figures in the [Wiring Guide](WiringGuide.md#measured-refresh).

---

### Configuration 5-6: ICN2037 64×64 Panels

**Panel Model:** P2-2020210240-200

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Scan: 1/32 (32 address lines)
- Half-panel: 2,048 pixels each
- Driver Chip: ICN2037
- Address Lines: ABCDE (5 lines)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped** (driver handles automatically)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 64
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains.** The number of panels one adapter can drive is in the [driver limits table](WiringGuide.md#driver-limits) (calculated).

---

### Configuration 7: MBI5124GP 64×32 Panels (P16-P31)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: **1/8 scan** (8 row addresses, so four rows lit at once: the driver flag `SCAN_4`, which uses the same converter as every other panel and places each row differently in the frame set)
- Driver Chip: MBI5124GP
- Address Lines: ABC (3 lines)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_MBI5124GP
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABC
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 32
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ❌ Single panel only (1/8 scan complexity). The 4.0.0 driver reads quarter-scan panels panel by panel for a chain, but that is proven only by a buffer-level test, not on these panels. The driver limit for this type is in the [driver limits table](WiringGuide.md#driver-limits).

**4.0.0 refresh core:** ✅ verified on one panel (2026-10-05) at 8-bit and 5-bit: correct image on the test patterns, refresh 85.4 Hz at 8-bit and 698.5 Hz at 5-bit; figures in the [Wiring Guide](WiringGuide.md#measured-refresh).

---

### Configuration 8: MBI5124GP 64×32 Panels (P32-P47)

**Panel Model:** P4-1921-8S-vV2.0 (green PCBs)

Same as Configuration 7 but using alternate pin group.

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P32_P47
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_MBI5124GP
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABC
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 32
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ❌ Single panel only (see Configuration 7; [driver limits table](WiringGuide.md#driver-limits))

---

### Configuration 9: GS6238S 64×32 Panels

**Panel Model:** P2.5-16S-V1.0 (cyan label) S210164-M00739

**Specifications:**
- Size: 64 columns × 32 rows = 2,048 pixels
- Scan: 1/16
- Driver Chip: GS6238S
- Address Lines: ABCD (4 lines)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Green/Blue swapped** (driver handles automatically)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_GS6238S
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 32
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ❌ Single panel only; multi-panel is untested. The driver's limit for this panel type is in the [driver limits table](WiringGuide.md#driver-limits).

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
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| MW245B | Bus transceiver (Sunmoon) |
| TC7262BJ | Row driver (Fuman, anti-ghosting) |

**Configuration** (the chip settings and the panel size; the cube's sentences and its Top and Front are in [Example 7](WiringGuide.md#example-7-the-cube-wired-in-a-ring-with-top-and-front) of the Wiring Guide):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 64
DISP0_SHAPE = hwEnum.SHAPE_CUBE             ' with DISP0_C0 .. DISP0_C5, DISP0_CUBE_TOP and DISP0_CUBE_FRONT
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains** (used in cube project with 6 panels). The 4.0.0 cube drawing layer is proven by its self-test only; it has not yet run on these six panels. The driver limit for this panel type is in the [driver limits table](WiringGuide.md#driver-limits).

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
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **Red/Blue swapped**

**On-Board Chips:**
| Chip | Function |
|------|----------|
| ICN2037BP | LED column driver (16-ch constant current) |
| 74HC245TS | Bus transceiver (TSSOP) |
| 74HC04D | Hex inverter (signal conditioning) |
| RUC7258D | Row driver (Ruichips) |

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P16_P31
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ✅ **Working in multi-panel chains.** This is the rig's panel type; its refresh is measured at every depth. Four of these (the rig) sit exactly at the driver's limit for this panel type: see the [driver limits table](WiringGuide.md#driver-limits).

**2×2 Grid Configuration** (the author's rig: the panels hang upside down, the adapter plugs into the bottom-left panel, and the ribbon runs along the bottom row and then the top row; every arrow is `ARROW_DOWN`):
```spin2
DISP0_MAX_PANEL_COLUMNS = 128
DISP0_MAX_PANEL_ROWS = 64
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_DOWN
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_DOWN
DISP0_C2 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_DOWN
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_DOWN
DISP0_C4 = hwEnum.NO_PANEL                  ' and so on, to DISP0_C15
```

This creates a 256×128 pixel display (32,768 total pixels). [Example 3](WiringGuide.md#example-3-2x2-in-z-order-from-bottom-left-the-rig) of the Wiring Guide works this one through.

---

### Configuration 12: ICN2038S 64×64 Panels (Road-Sign Display)

**Panel Model:** 64×64 (commercial road-sign display panel)

**Purpose:** Road-sign display application

**Panel Type:** Commercial all-weather panel, single-ended (no daisy-chain by construction)

**Specifications:**
- Size: 64 columns × 64 rows = 4,096 pixels
- Scan: **disputed** - the code sets `SCAN_4` (four rows lit at once, which would be 1/8 scan on this panel), but the five address lines (ABCDE, 32 row addresses) suggest 1/32 scan (two rows lit at once). It is an open item (`DOCs/plans/PUNCH-LIST.md`); until it is settled, this document gives no scan value for the chip.
- Driver Chip: ICN2038S
- Address Lines: ABCDE (5 lines)
- Clock and /OE ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)
- Color Note: **No color swap** (unlike ICN2037)

**Configuration** (one panel):
```spin2
DISP0_ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_P0_P15
DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2038S
DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE
DISP0_MAX_PANEL_COLUMNS = 64
DISP0_MAX_PANEL_ROWS = 64
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP     ' DISP0_C1 .. DISP0_C15 are hwEnum.NO_PANEL
```

**Multi-Panel Status:** ❌ Single panel only (no daisy-chain by design). The driver's limit for this type (which depends on the disputed scan setting) is in the [driver limits table](WiringGuide.md#driver-limits).

---

## Chip Quick Reference

| Chip | Color | Address Lines | Color Swap | Init Required | Multi-Panel |
|------|-------|---------------|------------|---------------|-------------|
| FM6126A | Pink | ABCD | None | Yes | **Yes** |
| FM6124 | Orange | ABCD | None | No | Untested |
| ICN2037 | - | ABCDE | R/B | No | **Yes** |
| ICN2038S | - | ABCDE | None | Untested | N/A (single-ended) |
| MBI5124GP | Green | ABC | None | Yes | Untested |
| GS6238S | Cyan | ABCD | G/B | No | Untested |
| DP5125D | - | ABC | None | No | Untested |

Each chip's datasheet clock and /OE ratings are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings).

---

## Driver Limits per Panel Type

How many panels one adapter can drive, for each panel type above, is in the
[Wiring Guide's driver limits table](WiringGuide.md#driver-limits), the one home of that
table: the maximum per adapter, what sets it (the refresh line buffer, for every type), the
hub RAM available, and the refresh rate. Its rows are these configurations. Every limit in it
is **calculated** from the driver's constants and none has been exercised at that panel count
on hardware except the rig's four ICN2037 128x64 panels (configuration 11). Refresh is
measured for the rig and for single FM6126A, FM6124 and MBI5124GP panels (configurations 1-4
and 7), on the same page. Configuration 12 (ICN2038S) is listed with the
code's scan setting, which is disputed (see Configuration 12).

---

## Multi-Panel Verified Configurations

The following chip/panel combinations have been verified working in multi-panel arrangements:

1. **FM6126A 64×32 (Pink)** - Tested in chains
2. **ICN2037 64×64** - Tested in chains and grids
3. **ICN2037 128×64** - Tested in chains and 2×2 grids

The following are expected to work but not yet verified:
- **ICN2038S** - Similar to ICN2037 (its scan setting is disputed; see Configuration 12)
- **FM6124 (Orange)** - Similar to FM6126A
- **DP5125D** - Untested

Not yet proven on hardware with the 4.0.0 driver: the cube on six real panels, multiple quarter-scan panels in one chain (the green MBI5124GP panels), a second adapter cabled at the same time, and any panel type other than the ICN2037 128x64. See the Known Issues in the [Change Log](../ChangeLog.md).

---

## Configuration Toggle Mechanism

**Note:** The commented configurations in the "More Hardware Setup Notes" block at the end of `isp_hub75_hwPanelConfig.spin2` are documentation examples only. They are NOT individually toggleable.

To change configuration:
1. Edit the `DISP0_*` constants directly in the "User configure" section of the first adapter's group, including its wiring sentences
2. Match the values to your hardware from the examples above
3. Recompile and flash; the startup picture and the identify screen confirm the wiring sentences (see the [Wiring Guide](WiringGuide.md))

Nothing in `isp_hub75_hwBufferAccess.spin2` or `isp_hub75_hwBuffers.spin2` is edited for a configuration change.

---

## Instrumentation Harness

The refresh rate, the share of time the panels are lit, the shift clock, the commit time and the draw time are measured from the P2's own pins, with no logic analyzer leads. The harness is compiled only when a test top file defines `HUB75_INSTRUMENT` and exports it to every object (`#DEFINE HUB75_INSTRUMENT` and `#PRAGMA EXPORTDEF HUB75_INSTRUMENT`). Without the symbol, no strobe instruction, strobe pin setup or monitor code is compiled, so release builds carry none of it. It instruments one adapter at a time.

| Top file | What it does |
|---|---|
| `test_hub75_rates.spin2` | Starts adapter 1 and the instrument, runs a fixed workload (flat fill, lines, text, BMP, each followed by a commit) and prints refresh, lit share, clock, draw time and commit time per phase. It then runs the frame-set handshake trace, the brightness steps (labelled on the panel), the tearing test with the take check, and the colour-table and row-run self-tests, each ending in PASS or FAIL |
| `test_hub75_oe_bcm.spin2` | Stand-alone check of the output-enable-weighted method with test patterns, on its own monitors |
| `test_hub75_converter.spin2` | Compares the screen-to-PWM converters byte for byte with a reference converter; needs no panels |

The color depth is a compile-time setting, so one build of `test_hub75_rates.spin2` measures one depth. Build and run it from `driver/`:

```
pnut-ts -d -l -m test_hub75_rates.spin2
pnut-term-ts -r test_hub75_rates.bin -p <port> --headless --end-marker --timeout 180
```

### Strobes

With the symbol defined, the refresh cog marks its progress with one pulse on each of four P2 pins that are not part of the HUB75 connector. Only the refresh cog drives them.

| Pin | Marks |
|---|---|
| P8 | posted set taken: the refresh cog took a newly posted PWM frame set |
| P9 | frame start |
| P10 | row start: the planes of one row address begin |
| P11 | plane latch |

### Monitor map

`isp_hub75_instrument.spin2` starts one input-only smart pin beside each signal it watches. A monitor sits up to three pins from its signal and never drives a pin. For an adapter at P16:

| Signal | Pin | Monitor | Measures |
|---|---|---|---|
| posted set taken | P8 | P5 | rises per 1 s window |
| frame start | P9 | P6 | rises per 1 s window |
| row start | P10 | P7 | rises per 1 s window |
| plane latch | P11 | P12 | rises per 1 s window |
| CLK | P16 | P13 | high clocks and periods over period-aligned windows |
| /OE | P17 | P14 | clocks low (lit) per 1 s window |
| LATCH | P18 | P15 | rises per 1 s window |

Every pin is derived from the adapter's base pin. Each signal tries the pins around it nearest-below first and takes the first that is free; a signal with no free neighbour is reported as `not monitored: jumper needed`. Refresh is the LATCH count divided by the planes and row addresses of a frame; the lit share is the /OE low time over the window.

An adapter at P0 owns P0-P13, which holds the strobe pins themselves, so there the strobes are not driven and no monitor starts. The test prints `RG3: instrument strobes P8-P11 are this adapter's own pins (base P0): strobes off` and `INSTR: monitors unavailable`, and reports only draw and commit times.

### Checks the harness makes

- **Handshake trace:** 100 commits back to back; each must convert into the frame set that is not on display. `HANDSHAKE PASS` or `FAIL`.
- **Take check:** a cog catches every rise of P8 and reads the row-address pins A-E at that moment. A take at a frame boundary finds row address 31 (the frame's last), and the takes counted must equal the commits made. `TAKE CHECK PASS` or `FAIL`. This is the tear-free acceptance, because a camera cannot tell an unlit row from a black image.
- **Resolution:** the CLK high time is measured directly; the low half is derived from the clock period, and resolves to about +/-0.5 system clock.

The logic analyzer below remains for the shape of waveforms, which the harness does not show.

## Logic Analyzer (waveform shape only)

The author's logic analyzer configuration for looking at the shape of HUB75 signals.

### Channel Mapping (16-channel LA)

| LA Channel | P2 Pin | Signal | Description |
|------------|--------|--------|-------------|
| 15 | P24 | R1 | Red data, upper half |
| 14 | P25 | G1 | Green data, upper half |
| 13 | P27 | R2 | Red data, lower half |
| 12 | P28 | G2 | Green data, lower half |
| 11 | P11 | Plane latch | Instrumentation strobe (`HUB75_INSTRUMENT` builds) |
| 10 | P10 | Row start | Instrumentation strobe |
| 9 | P9 | Frame start | Instrumentation strobe |
| 8 | P8 | Posted set taken | Instrumentation strobe |
| 7 | P19 | A | Address bit 0 (LSB) |
| 6 | P20 | B | Address bit 1 |
| 5 | P21 | C | Address bit 2 |
| 4 | P22 | D | Address bit 3 |
| 3 | P23 | E | Address bit 4 (MSB) |
| 2 | P16 | CLK | Pixel clock |
| 1 | P18 | LATCH | Row latch |
| 0 | P17 | OE | Output enable (directly active) |

### Notes

- Blue pins (B1, B2) are not monitored - R/G sufficient for color debugging
- The strobe pins (P8-P11) are directly on the P2, not on the HUB75 connector, and are driven only in a `HUB75_INSTRUMENT` build
- HUB75 signals assume `BASE_PIN = 16` (P16-P31 adapter)
- On the four-panel ICN2037 rig the column clock is 15 system clocks per column at 335 MHz, with CLK high 7 clocks (20.9 ns) and low 8 (23.9 ns) (chip ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings))

### Pin Identification Test

Use `test_hub75_pin_identify.spin2` to verify LA channel-to-pin mapping. This test outputs a 20-bit binary counter, with each bit assigned to a specific pin. Measure the frequency of each LA channel to identify which P2 pin it's connected to.

The test labels P8-P11 `LA_CMD`, `LA_FRMSET`, `LA_SAME` and `LA_NEW`; they are the pins the refresh cog uses as the strobes listed under [Strobes](#strobes).

**Test Configuration:** `BASE_PIN = 16`, `BASE_FREQ_HZ = 100_000`

#### Frequency-to-Pin Reference Table

| Frequency | Bit | P2 Pin | Signal | Description |
|-----------|-----|--------|--------|-------------|
| 100.0 kHz | 0 | P8 | LA_CMD | Instrumentation |
| 50.0 kHz | 1 | P9 | LA_FRMSET | Instrumentation |
| 25.0 kHz | 2 | P10 | LA_SAME | Instrumentation |
| 12.5 kHz | 3 | P11 | LA_NEW | Instrumentation |
| 6.25 kHz | 4 | P16 | CLK | Pixel clock |
| 3.125 kHz | 5 | P17 | OE | Output enable |
| 1.563 kHz | 6 | P18 | LATCH | Row latch |
| 781 Hz | 7 | P19 | A | Address bit 0 |
| 391 Hz | 8 | P20 | B | Address bit 1 |
| 195 Hz | 9 | P21 | C | Address bit 2 |
| 98 Hz | 10 | P22 | D | Address bit 3 |
| 49 Hz | 11 | P23 | E | Address bit 4 |
| 24 Hz | 12 | P24 | R1 | Red, upper half |
| 12 Hz | 13 | P25 | G1 | Green, upper half |
| 6 Hz | 14 | P26 | B1 | Blue, upper half |
| 3 Hz | 15 | P27 | R2 | Red, lower half |
| ~1.5 Hz | 16 | P28 | G2 | Green, lower half |
| ~0.76 Hz | 17 | P29 | B2 | Blue, lower half |
| ~0.38 Hz | 18 | P30 | SPARE1 | Unused |
| ~0.19 Hz | 19 | P31 | SPARE2 | Unused |

#### Hardware Verification

Running this test also verifies:

- **No stuck pins:** All 20 outputs toggle at their expected frequencies
- **No cross-talk:** Square waves are clean with no coupling between adjacent signals
- **P2 output integrity:** Logic analyzer inputs receive valid data from P2
- **LA input integrity:** All 16 LA channels functioning correctly

If any channel shows an unexpected frequency or no activity, check wiring and connections.

---

*Last Updated: October 2026 (driver 4.0.0)*
