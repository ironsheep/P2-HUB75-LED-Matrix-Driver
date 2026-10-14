# P2 HUB75 LED Matrix Driver - Testing and Measurement

A Parallax Propeller v2 driver for HUB75 RGB LED matrix panels, single or multi-panel. This page lists the test programs that come with the driver, what each one prints and whether it needs panels, and the tools for measuring the driver at work: the instrumentation harness, the logic analyzer channels and the pin identification test.

![Project Maintenance][maintenance-shield]
[![License][license-shield]](../LICENSE)

On this Page:

- [The test programs](#the-test-programs) - each test top file, what it prints, and whether it needs panels
- [The instrumentation harness](#the-instrumentation-harness) - measuring refresh, lit share, clock and commit time from the P2's own pins
- [Logic analyzer](#logic-analyzer-waveform-shape-only) - the channel mapping for looking at the shape of the signals
- [Pin identification test](#pin-identification-test) - which analyzer channel is on which pin
- [Diagnostic build switches](#diagnostic-build-switches) - the `DBG_PWM` frame dumps

Additional pages:

- [README](../README.md) - the project overview and the demo programs
- [Driver Details](../THEOPS.md) - how the driver works
- [Wiring Guide](WiringGuide.md) - the display block, the panel list, the limits and every startup message
- [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md) - each panel type's scan, colour swaps and test status
- [Troubleshooting](Troubleshooting.md) - symptoms and their fixes
- [CONTRIBUTING](../CONTRIBUTING.md) - what to compile and run before you send a change

### Pages: [README](../README.md) | [Hardware Turn-on](../HardwareTurnon.md) | [Driver Details](../THEOPS.md) | [Wiring Guide](WiringGuide.md) | [Troubleshooting](Troubleshooting.md) | Testing and Measurement | [Change Log](../ChangeLog.md)

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!

> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](../images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## The test programs

These are compile entry points in `driver/`, like the demos, but they check the driver or your hardware rather than show it off. Compile each one with no warnings; run the ones your change touches. Two need no panels and no edit to `isp_hub75_hwPanelConfig.spin2`: `test_hub75_converter.spin2` and `test_hub75_cube_fold.spin2` never start the panel driver, so no cog starts and no pin is driven.

| Top file | What it does and prints | Needs panels |
|---|---|---|
| `test_hub75_converter.spin2` | Fills a screen buffer of its own with a fixed pseudo-random image, runs the driver's screen-to-PWM converters and a reference converter on it, and compares the two frame sets byte for byte. Prints one PASS or FAIL line per case (with the count of differing bytes), a total and a verdict, then `END_SESSION` | No |
| `test_hub75_cube_fold.spin2` | Folds a reference cube net and pushes fixed face coordinates through the fold, comparing each result with an answer worked out by hand. Prints one PASS or FAIL line per case and a total, then `END_SESSION` | No |
| `test_hub75_rates.spin2` | Starts adapter 1 and the instrument and runs a fixed workload (flat fill, lines, text, BMP, each followed by a commit). Prints refresh, lit share, clock, draw time and commit time per phase, then the frame-set handshake trace, the brightness steps (labelled on the panel), the tearing test with the take check, and the colour-table, row-run and scroll-oracle self-tests, each ending in PASS or FAIL. See [the instrumentation harness](#the-instrumentation-harness) | Yes, one adapter (the `DISP0_` settings) |
| `test_hub75_oe_bcm.spin2` | Stand-alone check of the output-enable-weighted refresh method the driver uses, with test patterns and its own monitors. It does not use the display driver. Prints a `MODEL` line at start and one `MON:` line a second to compare with it | Yes, one adapter (the `DISP0_` settings) |
| `test_hub75_pin_identify.spin2` | Toggles the HUB75 pins and the P8-P11 measurement pins as a binary counter so you can tell, with a logic analyzer, which pin is which. See [the pin identification test](#pin-identification-test) | No panels; an analyzer on the adapter's pins |
| `demo_hub75_boundary.spin2` | Draws once across the panel seams of a multi-panel display (a crosshair, a spanning box, a circle, text across a seam) and a panel-centric line that must stop at its panel's edge, then holds the image. You judge it by eye | Yes, a multi-panel display |
| `isp_hub75_anlyCheck.spin2` | Pin exerciser: toggles the HUB75 adapter's pins so you can verify logic analyzer connections and wiring. Not part of the driver runtime | No panels; an analyzer on the adapter's pins |

The colour check, `demo_hub75_colorPad.spin2`, and the identify screen, `demo_hub75_numberPanels.spin2`, are demos and are described in the [README](../README.md#writing-display-code-for-your-panels).

## The instrumentation harness

The refresh rate, the share of time the panels are lit, the shift clock, the commit time and the draw time are measured from the P2's own pins, with no logic analyzer leads. The harness is compiled only when a test top file defines `HUB75_INSTRUMENT` and exports it to every object (`#DEFINE HUB75_INSTRUMENT` and `#PRAGMA EXPORTDEF HUB75_INSTRUMENT`). Without the symbol, no strobe instruction, strobe pin setup or monitor code is compiled, so release builds carry none of it. It instruments one adapter at a time. The measuring code is `isp_hub75_instrument.spin2`.

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

## Logic analyzer (waveform shape only)

The author's logic analyzer configuration for looking at the shape of HUB75 signals.

### Channel mapping (16-channel analyzer)

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
- The column clock and CLK pulse widths on the four-panel ICN2037 rig are in the [Wiring Guide](WiringGuide.md#measured-refresh) (chip ratings: see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings))

## Pin identification test

Use `test_hub75_pin_identify.spin2` to verify the analyzer channel-to-pin mapping. This test outputs a 20-bit binary counter, with each bit assigned to a specific pin. Measure the frequency of each analyzer channel to identify which P2 pin it's connected to.

The test labels P8-P11 `LA_CMD`, `LA_FRMSET`, `LA_SAME` and `LA_NEW`; they are the pins the refresh cog uses as the strobes listed under [Strobes](#strobes).

**Test Configuration:** `BASE_PIN = 16`, `BASE_FREQ_HZ = 100_000`

### Frequency-to-pin reference table

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

### Hardware verification

Running this test also verifies:

- **No stuck pins:** All 20 outputs toggle at their expected frequencies
- **No cross-talk:** Square waves are clean with no coupling between adjacent signals
- **P2 output integrity:** Logic analyzer inputs receive valid data from P2
- **LA input integrity:** All 16 LA channels functioning correctly

If any channel shows an unexpected frequency or no activity, check wiring and connections.

## Diagnostic build switches

The driver keeps a set of low-level diagnostic routines (PWM frame / buffer memory dumps) that are normally compiled **out** so they add zero cost to release builds. They are gated by the `DBG_PWM` preprocessor symbol and revived by passing it on the compiler command line:

```
pnut-ts -d -D DBG_PWM demo_hub75_color.spin2     # PWM-frame dump diagnostics compiled in
pnut-ts -d            demo_hub75_color.spin2     # normal build -- diagnostics absent (zero cost)
```

`-D` is global across the object tree, so a single `-D DBG_PWM` reaches `isp_hub75_panel.spin2` (the `dumpBufferHeads` / `dumpFrame*` family) and `isp_hub75_hwBufferAccess.spin2` (`dbgMemDump`). Two notes for maintainers:

- Use `#ifdef DBG_PWM` / `#endif` (conditional compilation) to gate diagnostic **methods and their call sites** -- this removes the routine scaffolding entirely. (A plain `debug()` statement already costs nothing in a non-`-d` build, so it needs no guard.)
- An in-file `#define` does **not** cross object boundaries; only command-line `-D` does. Define `DBG_PWM` on the command line, never per-file.

`test_hub75_rates.spin2` has three more switches that corrupt a check on purpose, so you can see the check fail: `-D HUB75_CORRUPT_COLOUR_TABLE` (every colour-table case must report FAIL), `-D HUB75_CORRUPT_ROW_RUN` (every row-run case must report FAIL) and `-D HUB75_CORRUPT_PIXEL_ADDRESS` (every address-rule line must report FAIL).

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](../CONTRIBUTING.md)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](../copyright) | [License](../LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
