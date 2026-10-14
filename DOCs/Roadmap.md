# P2 HUB75 LED Matrix Driver - Roadmap

A Parallax Propeller v2 driver for HUB75 RGB LED matrix panels, single or multi-panel. This page lists the work planned beyond what the driver does today: larger displays on external RAM, and better color rendering.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](../LICENSE)

### Pages: [README](../README.md) | [Hardware Turn-on](../HardwareTurnon.md) | [Driver Details](../THEOPS.md) | [Configuration Guide](WiringGuide.md) | Roadmap | [Change Log](../ChangeLog.md)

On this Page:

- [What this page is](#what-this-page-is) - planned work, not shipped work
- [Larger displays with external RAM](#larger-displays-with-external-ram) - the P2-EC32MB Edge Module and what it would enable
- [Moving data without hub RAM](#moving-data-without-hub-ram) - the streamer and LUT sharing
- [Color rendering](#color-rendering) - gamma, white point, temporal dithering, scan-line uniformity
- [Conversion and refresh](#conversion-and-refresh) - a dedicated conversion cog and streamer-fed output
- [How to Contribute](#how-to-contribute) - where to send ideas and code

Additional pages:

- [README](../README.md) - the project overview
- [Configuration Guide](WiringGuide.md) - the display block, the panel list, the limits and the refresh rate
- [Driver Details](../THEOPS.md) - how the driver works today
- [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md) - each panel type's scan, colour swaps and test status

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](../images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## What this page is

Everything here is planned or under consideration; none of it is in the driver yet. What the driver does today is told in other pages, and this page links to them instead of repeating them:

- The memory the driver uses, the largest displays it can drive and the per-adapter limits are in the [Configuration Guide's driver limits](WiringGuide.md#driver-limits) and [hub RAM](WiringGuide.md#hub-ram) sections.
- The refresh method, the measured refresh rates, the commit and draw times and the clock figures are in the [Configuration Guide's refresh rate section](WiringGuide.md#refresh-rate).
- How the refresh cog reads the frame set and clocks it to the panels is in [Driver Details](../THEOPS.md#refresh-method).

Plan any animation or image work around the refresh rates stated in the Configuration Guide, not around a fixed frame rate. Images are loaded as BMP files.

## Larger displays with external RAM

The driver keeps every buffer in the P2's 512 KB of hub RAM, which bounds the display size (see the [driver limits](WiringGuide.md#driver-limits)). The **P2-EC32MB Edge Module** (Parallax #64032) carries 32 MB of HyperRAM, 8 MB of flash and breaks out all 64 I/O pins, which is 64 times the hub RAM. It is the planned test platform for the items below.

A second limit is separate from memory: one adapter's refresh cog holds one row of its whole chain in a 512-byte line buffer, so the chain width is bounded no matter how much RAM there is. Displays much larger than today's need both external RAM and a refresh cog that does not hold a whole row in cog RAM (see [streamer-fed output](#streamer-fed-output) below).

### Massive display configurations

With the screen buffer in external RAM at 3 bytes per pixel, 32 MB holds about 11 million pixels. The pixel working set for the frame being converted would stay in hub RAM. Grids such as 8 x 8 panels of 64 x 64 (262,144 pixels, 768 KB of screen buffer) or 16 x 16 panels of 64 x 64 (1,048,576 pixels, 3 MB) become memory-feasible. The practical limit then becomes the refresh rate a long chain can reach, not memory.

### Animation storage

Pre-rendered frame sequences could be held in external RAM and shown without rendering in real time. For a 256 x 128 display a frame is 96 KB, so 100 frames take about 10 MB; a 512 x 256 display needs 384 KB a frame. Loaded BMP images could be kept the same way, as logos, backgrounds and sprites.

### Stored assets

Fonts in several sizes with anti-aliased glyphs, gamma and palette lookup tables, and BMP images could sit in external RAM for instant access.

### More than two frame sets

Today the driver has two PWM frame sets: a commit converts into the one not on display. External RAM would allow a third and fourth set, for tear-free animation at high frame rates, compositor effects, and preparing the next scene in the background.

### Virtual display paging

Several complete screens held in external RAM would allow instant switching between pre-rendered content: menu systems with pre-built pages, score displays with pre-rendered digits, and several display modes without re-rendering.

### What it would cost

- One cog dedicated to the external RAM driver, so a program needs one more cog than today.
- Screen data would move to hub RAM in horizontal strips: while the refresh cog outputs the current strip, the next one loads.
- External RAM access has about 1 microsecond of latency against about 10 nanoseconds for hub RAM, so transfers are made in strips, not pixel by pixel.

## Moving data without hub RAM

Two P2 features could keep the external RAM path from competing for hub bandwidth. Neither is used by the driver today.

### Streamer pipeline

Each cog has a streamer, an autonomous engine that moves data between hub RAM, pins and the cog while the cog runs other code. Three stages could then run in parallel on different data: external RAM to hub RAM (one streamer), screen buffer to PWM frames (cog code), and PWM frames to the panels (another streamer).

### LUT sharing between adjacent cogs

The P2 lets adjacent cog pairs (0 and 1, 2 and 3, 4 and 5, 6 and 7) share their 512-long lookup RAM: one cog writes its LUT and the neighbor reads the mirrored data. A pairing of an external RAM cog with the output cog could hand rows over with no hub RAM traffic. The same mechanism could let one cog own a gamma or palette table that its neighbor reads directly, or ping-pong row buffers so the next row loads while the current one is output.

## Color rendering

### Gamma correction

Perceived brightness is not linear in the drive value. The color table the driver builds already folds in a 256-entry gamma curve, but the curve is switched off and no setting turns it on. Planned: a per-display setting to turn gamma on, and a curve chosen per panel if LED characteristics vary.

### Color balance and white point

Red, green and blue LEDs differ in efficiency, so full white can look tinted. Planned: a per-channel gain applied in the color table, so that white looks white. Some chips (the FM6126A, for one) have built-in current control that the software correction could supplement.

### Temporal dithering

At the lower color depths (3 and 4 bit), banding can show in gradients. Varying the least significant value from frame to frame would give levels between the discrete ones; for example alternating 7 and 8 reads as about 7.5. It needs a high enough refresh rate to avoid visible flicker, so it depends on the measured rates in the [Configuration Guide](WiringGuide.md#refresh-rate).

### Scan-line brightness uniformity

The refresh cog gives every row address the same timing at every brightness. Any remaining difference between scan lines would be per chip, and has to be measured on a panel before a fix is worth building.

## Conversion and refresh

### Conversion in its own cog

Screen-to-PWM conversion runs today in the main cog (the commit time is in the [Configuration Guide](WiringGuide.md#refresh-rate)). Moving it to a dedicated PASM2 cog would run it in parallel with display refresh, reduce the load on the main cog and open the way to real-time effects.

### Streamer-fed output

Using the P2's streamer to feed PWM data to the pins would reduce the load on the refresh cog, give more consistent timing and could lift the 512-column line-buffer limit. It needs significant restructuring of the refresh cog.

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](../CONTRIBUTING.md)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](../copyright) | [License](../LICENSE)

---

Last Updated: 13 Oct 2026

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
