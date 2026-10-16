# HUB75 Driver - refresh rates and signal timings (v4)

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | [Driver Details](THEOPS.md) | [Configuration Guide](DOCs/WiringGuide.md) | Refresh Rates | [Change Log](ChangeLog.md)

NOTE: this page is for the version 4 driver (4.0.0 and later). The earlier pages are kept as history: [Software Ver1.x Timings](HUB75-Driver-SWver1.md) | [Software Ver0.x Timings](HUB75-Driver-SWver0.md)

## Intent

This page shows what the version 4 driver puts on the HUB75 lines, and what refresh rate, lit share and commit time it reaches on each panel the author has, at every colour depth. The settings that shape these signals are chosen for you by the chip type you set in **isp\_hub75\_hwPanelConfig.spin2**; each chip's starting configuration is in the [Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md), and how the refresh method chooses its timing is in [Driver Details](THEOPS.md#refresh-method).

On this page:

- [The v4 signals](#the-v4-signals) - one refresh, one row address, the latch shapes, brightness
- [How to read the tables](#how-to-read-the-tables)
- [Driver configuration by chip type](#driver-configuration-by-chip-type-sw-ver-4x-timings) - the measured figures for each panel

## The v4 signals

Version 4 shows each bit plane of the image **once** per row address and lights it for a time weighted by its bit, by pulsing /OE. One refresh is every row address shown with every plane; the refresh rate is how often that repeats, the figure the earlier pages called the video frame rate.

The pictures below are logic-analyzer captures from the author's bench, P2 at 335 MHz, adapter on P16-P31. They use the same colours as the earlier pages:

#### LEGEND

| Signal | Color |
|-----|-----|
| CLK | Red |
| LATCH | Green |
| OE! | White |
| ADDR | Yellow |

### One refresh

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S1)                 |
|      one whole refresh: FM6124 64x32, 8-bit, 16 row          |
|      addresses, each with its 8 planes                       |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 1: One refresh, FM6124 64x32 at 8-bit (85.3 Hz, 11.7 ms)**

The address lines step through every row address once. At each address the eight planes go out back to back, so /OE shows a burst of eight pulses per address, longest first. Nothing waits between addresses or between refreshes: the next refresh's first plane shifts in while the last plane of this one is still lit.

### One row address

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S2)                 |
|      one row address: FM6124 64x32, 8-bit, 8 planes          |
|      weighted 128:64:32:16:8:4:2:1                            |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 2: One row address, FM6124 64x32 at 8-bit (0.73 ms)**

For each plane, from the most significant down, the driver loads the plane's row, shifts it into the panel, latches it and pulses /OE for 2^k units inside a slot of 2^k units. The next plane loads and shifts **while the current one is lit**, so CLK bursts sit under the long /OE pulses. Only when a slot is shorter than the time to shift a row does /OE go dark between planes; that is what lowers the lit share on a long chain (see [ICN2037](#driver-chip-icn2037-four-128x64-panels-2-x-2)).

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S5)                 |
|      one row address: FM6124 64x32, 3-bit, 3 planes          |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 3: One row address, FM6124 64x32 at 3-bit (21 us)**

At 3-bit a row address has three planes, lit for 4, 2 and 1 units, instead of 255 units at 8-bit. That is why the shallow colour depths refresh so much faster.

### The latch shapes

Each chip latches its row one of two ways. The driver picks the way from the chip type; the flags behind it (`LAT_STYLE_OFFSET`, `LAT_POSN_OVERLAP`) are named in the [Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#latch-timing-styles). In both, the panel is dark (/OE off) before LATCH rises and before the row address changes: a latch never happens while a row is lit.

#### Latch at end, enclosed

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S3)                 |
|      latch at end, enclosed: FM6124 64x32, zoomed            |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 4: Latch at end, enclosed (FM6124, ICN2037, ICN2038S, MBI5124GP)**

Every column of the row clocks in and CLK goes low. The driver waits until the previous plane is dark, sets the row address, pulses LATCH, waits a short settle gap, and then /OE lights the new plane.

A third form, latch at end **offset**, is the same with no settle gap: /OE lights as soon as LATCH falls. The driver supports it, but no chip it knows uses it.

#### Overlapped latch

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S6)                 |
|      overlapped latch: FM6126A 64x32, zoomed                 |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 5: Overlapped latch (FM6126A, GS6238S, DP5125D)**

All but the last 3 columns clock in. The driver waits until the previous plane is dark, raises LATCH, clocks the last 3 columns with LATCH high, drops LATCH, sets the row address, and then /OE lights the new plane.

### Brightness

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S4)                 |
|      one row address at brightness 128: FM6124 64x32, 8-bit  |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 6: One row address at brightness 128 (compare with Figure 2)**

`display.setBrightness()` shortens each /OE pulse and leaves its slot as it was: at 128 every pulse is half as long, and the row, and with it the refresh rate, takes the same time. A pulse never goes below the chip's shortest /OE pulse, so the lowest settings give a floor of light rather than less (the *Lit at brightness 1* rows below). How brightness is set is in the [Configuration Guide](DOCs/WiringGuide.md#brightness).

## How to read the tables

- **Refresh** - whole images per second, measured on the P2's own LATCH and /OE pins.
- **Lit** - the share of the time /OE has the LEDs on, at brightness 256. A higher share is a brighter panel.
- **Lit at brightness 1** - the floor of light at the lowest setting.
- **Commit** - the time to turn the screen buffer into a frame set the refresh can show.
- ***j*** - how many times the driver halved the /OE unit to reach the refresh target. *j* = 0 lights every plane for its whole slot; each step halves the lit time and roughly halves the light (see [Driver Details](THEOPS.md#refresh-method)).

Each display runs at the target refresh rate (60 Hz unless `DISPn_TARGET_REFRESH_HZ` sets another) or faster, and gives the rest of the time to light: that is why the deeper colour depths sit nearest the target and the shallow ones run far above it. Below about 60 Hz a panel can be seen to flicker.

All figures: P2 at 335 MHz, the default 60 Hz target, measured with `test_hub75_rates.spin2` (see [Testing and Measurement](DOCs/TestingAndMeasurement.md)), 15 and 16 Oct 2026. Every panel's image was checked by eye on the bench. A DEBUG build prints the driver's own prediction at startup (the `MODEL` line). It agrees with these figures to within 0.3% at 7-bit and 8-bit; at shallower depths it reads high, by up to 0.7% on the latch-at-end chips and up to 2.5% on the overlapped-latch chips.

The column clock is set from the chip's limits at startup (see [Driver Details](THEOPS.md#refresh-method)). At 335 MHz it is 15 system clocks per column, 22.3 MHz, with CLK high for 7 clocks (20.9 ns) and low for 8 (23.9 ns), for every chip below except the GS6238S and the MBI5124GP. The monitors read the high half a little long, through the pin's input threshold: 21.8 to 23.9 ns at 22.3 MHz.

## Driver configuration by chip type (S/W Ver 4.x timings)

Each section gives the chip's latch shape and the other signal settings its chip type selects, then the figures measured on the author's panels. If your panel's chip is not here, see [Adding New Chip Support](DOCs/ChipCharacteristicsMatrix.md#adding-new-chip-support) and please file an issue with what you find.

### Driver Chip: FM6126A

This chip does not turn on reliably until it has been configured; the driver writes its two configuration registers at startup. ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#fm6126a-pink-labels))

- LATCH: overlapped
- START-UP CONFIGURATION: Yes
- COLOUR LINES: as wired
- SCAN: 1/16, 16 row addresses, 64 column clocks per row address per panel
- COLUMN CLOCK: 22.3 MHz; shortest /OE pulse 14 clocks (42 ns)

Signal Timings - one 64x32 panel - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 85.1 | 170.5 | 341.9 | 688.8 | 1,403.5 | 2,938.6 |
| Lit (%) | 99.6 | 99.2 | 98.7 | 97.9 | 96.5 | 94.3 |
| Lit at brightness 1 (%) | 1.4 | 1.4 | 1.4 | 1.4 | 1.4 | 1.3 |
| Commit (ms) | 0.28 | 0.27 | 0.25 | 0.23 | 0.22 | 0.20 |
| *j* | 0 | 0 | 0 | 0 | 0 | 0 |

Signal Timings - two 64x32 panels stacked, one 64x64 display - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 84.8 | 85.5 | 172.0 | 347.9 | 713.7 | 1,510.5 |
| Lit (%) | 99.1 | 99.6 | 99.3 | 98.9 | 98.1 | 96.9 |
| Lit at brightness 1 (%) | 1.4 | 0.7 | 0.7 | 0.7 | 0.7 | 0.7 |
| Commit (ms) | 0.53 | 0.50 | 0.46 | 0.43 | 0.40 | 0.36 |
| *j* | 1 | 0 | 0 | 0 | 0 | 0 |

**NOTE** *above 60 Hz at every colour depth*

---

### Driver Chip: FM6124

The simplest chip: no configuration, latch at end. ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#fm6124-orange-labels))

- LATCH: at end, enclosed
- START-UP CONFIGURATION: No
- COLOUR LINES: as wired
- SCAN: 64x32: 1/16, 16 row addresses; 64x64 (FM6124C, set as `CHIP_FM6124`): 1/32, 32 row addresses; 64 column clocks per row address
- COLUMN CLOCK: 22.3 MHz; shortest /OE pulse 11 clocks (33 ns)

Signal Timings - one 64x32 panel - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 85.3 | 170.9 | 343.5 | 694.1 | 1,420.3 | 2,992.3 |
| Lit (%) | 99.7 | 99.5 | 99.2 | 98.6 | 97.6 | 96.0 |
| Lit at brightness 1 (%) | 1.1 | 1.1 | 1.1 | 1.1 | 1.1 | 1.1 |
| Commit (ms) | 0.28 | 0.27 | 0.25 | 0.23 | 0.22 | 0.20 |
| *j* | 0 | 0 | 0 | 0 | 0 | 0 |

Signal Timings - one 64x64 panel (FM6124C) - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 84.7 | 85.5 | 171.7 | 347.0 | 710.2 | 1,496.7 |
| Lit (%) | 99.0 | 99.5 | 99.2 | 98.6 | 97.7 | 96.0 |
| Lit at brightness 1 (%) | 2.2 | 1.1 | 1.1 | 1.1 | 1.1 | 1.1 |
| Commit (ms) | 0.53 | 0.50 | 0.46 | 0.43 | 0.40 | 0.37 |
| *j* | 1 | 0 | 0 | 0 | 0 | 0 |

**NOTE** *above 60 Hz at every colour depth*

---

### Driver Chip: ICN2037 (four 128x64 panels, 2 x 2)

The author's main rig: one long chain of four panels as one 256x128 display. ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#icn2037--icn2037bp-no-color-label))

- LATCH: at end, enclosed
- START-UP CONFIGURATION: No
- COLOUR LINES: red and blue swapped (`RB_SWAP`)
- SCAN: 1/32, 32 row addresses, 512 column clocks per row address (the whole chain)
- COLUMN CLOCK: 22.3 MHz; shortest /OE pulse 21 clocks (63 ns)

```
+--------------------------------------------------------------+
|                                                              |
|                 picture is coming  (shot S9)                 |
|      one row address on the 512-column chain, 8-bit          |
|                                                              |
+--------------------------------------------------------------+
```

**FIGURE 7: One row address on the four-panel chain at 8-bit (0.44 ms)**

Shifting one plane of a 512-column row takes 7,680 system clocks. To reach 60 Hz at 8-bit the driver halves the /OE unit four times (*j* = 4), and then the shortest planes' slots are shorter than a shift: /OE sits dark while the next plane clocks in. That is why this display's lit share is 83% at 8-bit and 99% at 4-bit.

Signal Timings - four 128x64 panels, 256x128 - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 71.0 | 75.0 | 79.6 | 84.7 | 90.5 | 193.3 |
| Lit (%) | 83.0 | 87.4 | 91.9 | 96.3 | 99.6 | 99.2 |
| Lit at brightness 1 (%) | 3.6 | 1.9 | 1.0 | 0.5 | 0.3 | 0.3 |
| Commit (ms) | 4.09 | 3.82 | 3.52 | 3.26 | 3.06 | 2.77 |
| *j* | 4 | 3 | 2 | 1 | 0 | 0 |

The image is steady by eye at 5-bit to 8-bit on a full-screen colour demo; the author's words at each depth were *"steady"* (5-bit), *"steady"* (6-bit), *"no shimmering"* (7-bit) and *"colors all look steady"* (8-bit). A test build of the method showed visible flicker at 36.9 Hz and none at 65.9 Hz.

**NOTE** *above 60 Hz at every colour depth*

---

### Driver Chip: ICN2038S

A 64x64 road-sign panel, single-ended (it cannot be chained). It scans 1/16, so the driver sends each row address as two quarter-panel regions (`SCAN_4`). ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#icn2038s-no-color-label---road-sign-display-panel))

- LATCH: at end, enclosed
- START-UP CONFIGURATION: No
- COLOUR LINES: as wired
- SCAN: 1/16, 16 row addresses, 128 column clocks per row address
- COLUMN CLOCK: 22.3 MHz; shortest /OE pulse 14 clocks (42 ns)

Signal Timings - one 64x64 panel - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 84.9 | 85.6 | 172.3 | 349.3 | 718.0 | 1,524.6 |
| Lit (%) | 99.3 | 99.7 | 99.6 | 99.2 | 98.7 | 97.8 |
| Lit at brightness 1 (%) | 1.4 | 0.7 | 0.7 | 0.7 | 0.7 | 0.7 |
| Commit (ms) | 0.53 | 0.50 | 0.46 | 0.43 | 0.40 | 0.37 |
| *j* | 1 | 0 | 0 | 0 | 0 | 0 |

**NOTE** *above 60 Hz at every colour depth*

---

### Driver Chip: MBI5124GP (1/8 scan)

The panel scans 1/8: it has half the usual row addresses and clocks twice the columns per row address (`SCAN_4`). The driver writes the chip's configuration register at startup. In a chain one chip cannot hand data to the next faster than 18.9 MHz, so these panels are clocked at 18.6 MHz. ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#mbi5124gp-green-pcbs))

- LATCH: at end, enclosed
- START-UP CONFIGURATION: Yes
- COLOUR LINES: as wired
- SCAN: 1/8, 8 row addresses, 128 column clocks per row address per panel
- COLUMN CLOCK: 18.6 MHz (18 system clocks, CLK high 9 = 26.9 ns, low 9; the monitors read the high half at 27.6 to 29.7 ns); shortest /OE pulse 17 clocks (51 ns)

```
+--------------------------------------------------------------+
|                                                              |
|          picture is coming  (shot S8, optional)              |
|      one whole refresh, 1/8 scan: MBI5124GP 64x32, 8-bit     |
|                                                              |
+--------------------------------------------------------------+
```

Signal Timings - one 64x32 panel - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 71.2 | 142.8 | 287.5 | 582.8 | 1,199.1 | 2,549.3 |
| Lit (%) | 99.8 | 99.8 | 99.6 | 99.4 | 98.9 | 98.1 |
| Lit at brightness 1 (%) | 0.7 | 0.7 | 0.7 | 0.7 | 0.7 | 0.7 |
| Commit (ms) | 0.28 | 0.27 | 0.25 | 0.23 | 0.22 | 0.20 |
| *j* | 0 | 0 | 0 | 0 | 0 | 0 |

Signal Timings - two 64x32 panels chained, 128x32 - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 70.8 | 71.4 | 144.0 | 292.2 | 602.4 | 1,285.0 |
| Lit (%) | 99.4 | 99.9 | 99.8 | 99.6 | 99.4 | 98.9 |
| Lit at brightness 1 (%) | 0.7 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 |
| Commit (ms) | 0.53 | 0.50 | 0.46 | 0.43 | 0.40 | 0.37 |
| *j* | 1 | 0 | 0 | 0 | 0 | 0 |

**NOTE** *above 60 Hz at every colour depth*

---

### Driver Chip: GS6238S

Green and blue are swapped on this panel's lines (`GB_SWAP`). The chip has no clock rating in the driver's table, so the driver holds it to 20 MHz and says so at startup. ([Chip Characteristics Matrix](DOCs/ChipCharacteristicsMatrix.md#gs6238s-cyan-label))

- LATCH: overlapped
- START-UP CONFIGURATION: No
- COLOUR LINES: green and blue swapped (`GB_SWAP`)
- SCAN: 1/16, 16 row addresses, 64 column clocks per row address
- COLUMN CLOCK: 19.7 MHz (17 system clocks, CLK high 8 = 23.9 ns, low 9; the monitors read the high half at 25.0 to 27.1 ns); shortest /OE pulse 17 clocks (51 ns)

Signal Timings - one 64x32 panel - for driver v4.x:

| Colour depth | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|
| Refresh (Hz) | 75.1 | 150.5 | 302.0 | 608.8 | 1,242.3 | 2,607.7 |
| Lit (%) | 99.6 | 99.3 | 98.8 | 98.0 | 96.8 | 94.8 |
| Lit at brightness 1 (%) | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.4 |
| Commit (ms) | 0.29 | 0.27 | 0.25 | 0.24 | 0.23 | 0.21 |
| *j* | 0 | 0 | 0 | 0 | 0 | 0 |

**NOTE** *above 60 Hz at every colour depth*

---

### Not yet measured with v4

- **ICN2037 cube panels** (six 64x64 panels folded as a cube): measured when the cube is next rigged.
- **DP5125D**: no panel on hand.

----

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

----

## License

Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
