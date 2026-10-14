# P2 HUB75 LED Matrix Driver - Troubleshooting

A Parallax Propeller v2 driver for HUB75 RGB LED matrix panels, single or multi-panel. Something looks wrong? Find the symptom here, then follow the link to the page that explains the fix.

![Project Maintenance][maintenance-shield]
[![License][license-shield]](../LICENSE)

On this Page:

- [Before you start](#before-you-start) - the two things to look at first
- [The panel is dark](#the-panel-is-dark) - nothing lights, or only some panels light
- [The colours are wrong](#the-colours-are-wrong) - red, green and blue swapped
- [Ghosting or repeated rows](#ghosting-or-repeated-rows) - the picture shows twice, or every other band is dark
- [The picture flickers](#the-picture-flickers) - flashing or unstable
- [Startup stops with a HUB75 message](#startup-stops-with-a-hub75-message) - the driver named a mistake
- [The panels are in the wrong order or turned](#the-panels-are-in-the-wrong-order-or-turned) - content on the wrong panel, upside down or mirrored
- [Out of memory](#out-of-memory) - the compiler says the program does not fit

Additional pages:

- [README](../README.md) - the project overview
- [Wiring Guide](WiringGuide.md) - the display block, the panel list, the identify screen, the limits and every startup message
- [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md) - each panel type's scan, colour swaps and test status
- [Driver Details](../THEOPS.md) - how the driver works

### Pages: [README](../README.md) | [Hardware Turn-on](../HardwareTurnon.md) | [Driver Details](../THEOPS.md) | [Wiring Guide](WiringGuide.md) | Troubleshooting | [Change Log](../ChangeLog.md)

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!

> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](../images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Before you start

Each entry below is a symptom, its likely cause and the fix, with a link to where the fix is explained. This page points; it does not repeat the messages or settings, so the pages it links to stay the one place that states them.

1. **Run the identify program**, `demo_hub75_numberPanels.spin2`. It labels every panel with its cable position, its panel position and an arrow, and most of the entries below are told apart by what it shows ([how to read it](WiringGuide.md#filling-in-your-config-from-the-identify-screen)).
2. **Read the startup lines** the driver prints before it starts the panels. The number of panels in the picture must equal the number of panels you have cabled ([what a good config prints](WiringGuide.md#what-a-good-config-prints)).

## The panel is dark

- **Cause: the adapter's pin group is not the one the adapter is plugged into.** Fix: set `DISPn_ADAPTER_BASE_PIN` to the connector pair you used ([the display block](WiringGuide.md#the-display-block)). A value that is not one of the three pin groups stops startup with a message ([startup messages](WiringGuide.md#startup-messages)).
- **Cause: the chip setting does not match the panel.** The chip setting carries what the driver does for that panel (the matrix's *Init Req* and *Latch Style* columns). Fix: use the canned name for your panel's chip ([Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)).
- **Cause: only some panels light.** The panel list names fewer panels than are cabled. Fix: compare the startup picture with the wall and the identify labels ([the procedure](WiringGuide.md#the-procedure)).
- **Cause: the brightness is set to 0.** `display.setBrightness(0)` turns the panels off. Fix: set a value from 1 to 256 ([brightness](WiringGuide.md#brightness)).

## The colours are wrong

- **Cause: the panel swaps red and blue, or green and blue.** Some chips do; the matrix lists them in its *R/B Swap* and *G/B Swap* columns. Fix: use the canned chip name, which sets the swap, or add the `RB_SWAP` or `GB_SWAP` flag to a `CHIP_MANUAL_SPEC` setting ([the chip](WiringGuide.md#the-display-block)). The demo `demo_hub75_colorPad.spin2` shows each colour patch above its name, so a wrong swap is easy to see.

## Ghosting or repeated rows

- **Cause: the scan setting does not match the panel.** Scan follows how the panel is built, not which column-driver chip it uses. A picture shown twice, one copy above the other, means the panel lights four rows at once and needs the `SCAN_4` flag; every other horizontal band dark means it lights two rows at once and must not have it. Fix: change the chip setting (or use `CHIP_MANUAL_SPEC` with the flags that fit), not the panel list ([the matrix's scan note](ChipCharacteristicsMatrix.md#quick-reference-matrix), [step 6 of the procedure](WiringGuide.md#the-procedure)).

## The picture flickers

- **Cause: the number of panels, the chip setting or the panel size does not describe the hardware.** Fix: check that the startup picture shows as many panels as you have cabled, that the chip setting matches your panels ([Quick Reference Matrix](ChipCharacteristicsMatrix.md#quick-reference-matrix)) and that `DISPn_PANEL_COLUMNS` and `DISPn_PANEL_ROWS` are one panel's width and height ([the display block](WiringGuide.md#the-display-block)).
- **Cause: the refresh rate is low.** A long chain and a deep colour depth both lower it, and a rate that cannot reach the target prints a notice at startup. Fix: see [the refresh rate](WiringGuide.md#refresh-rate) for what the target does and the rates measured, and [the driver limits](WiringGuide.md#driver-limits) for how many panels one adapter can drive.

## Startup stops with a HUB75 message

- **Cause: a panel sentence or a display setting is wrong.** Every message the driver can print is listed with its cause. Fix: find the message in [the startup messages](WiringGuide.md#startup-messages) and correct the sentence or setting it names. The messages name a panel as `DISPn Ck`, where `k` is its place in the panel list counting from 0.

## The panels are in the wrong order or turned

- **Cause: pixels appear on the wrong panel, or the panels are in the wrong order.** A `ROW_` or `COL_` word places a panel wrongly. Fix: run the identify program and compare the `P` labels with where the panels hang ([filling in your config](WiringGuide.md#filling-in-your-config-from-the-identify-screen)).
- **Cause: the display is upside down or mirrored.** One panel's content is turned when its `TOP_` word is wrong. A whole display hung another way after it was identified needs the mounting override instead. Fix: correct the `TOP_` word, or set the override ([display rotation](WiringGuide.md#display-rotation)).

## Out of memory

- **Cause: the buffers do not fit in the 512 KB of hub RAM.** The compiler reports `Program requirement exceeds 512KB hub RAM`. Fix: lower the colour depth, use fewer panels, or build without DEBUG, which leaves more room; the sizes are worked out in [Hub RAM](WiringGuide.md#hub-ram).

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
