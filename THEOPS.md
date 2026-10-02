# Theory of Operations:
## Hub75 RGB LED Matrix panel driver

![Project Maintenance][maintenance-shield]

On this page you'll learn what files make up the driver (and/or come with it) and what their purpose is, how to configure the dirver for your hardware, and also a bit about how the driver actually works. 

(*I expect that this file will continue to grow over time as our driver becomes more capable. -Stephen*)


### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | Driver Details | [Change Log](ChangeLog.md)

Within this page:

- [Driver Files](#driver-file-organization) - the purpose of each file found in the driver
- [Glossary](#glossary) - the terms every driver document uses, each defined once
- [Configuring the Driver](#configuring-the-driver) - how to describe your panels to the driver
- [Notes on Internals](#notes-on-driver-internals) - more in the internal data flow within the driver
- [Max Panels Supported](#driver-max-panels-supported) - I'm planning on buying panels. How many panels does this driver support?


## Driver file organization

The driver files consist of demo-top-level files as well as the driver itself.

### Demo/Top-Level Files

Here are the reference programs you can study when learning to display to your panel(s):

| DEMO TopLevel Files            |  Purpose |
|-----------------|-------------|
| demo\_hub75_color.spin2 | Presents the color features of the panel driver, displays a .bmp file |
| demo\_hub75_text.spin2 | Presents the text and scrolling features of the panel driver |
| demo\_hub75_7seg.spin2 | Presents a technique for doing multi-step animations using the panel driver |
| demo\_hub75_multiPanel.spin2 | Presents techniques for drawing to the various surfaces of our P2 P2 Cube |
 demo\_hub75_5x7font.spin2 | Present pages (every 10 sec) showing the latest 5x7 full character-set font |
| demo\_hub75_scroll.spin2 | Shows off the 4 supported text-scrolling directions (albeit slowly ;-)
| demo\_hub75_colorPad.spin2 | **TEST** Simple single-screen demo so you can check if Red Green Blue LEDs are configured correctly. (*color patch will match color name underneath if settings for color-swap are correct*) |


**NOTE:** these demo's are built for 64x32 panels and 64x64 panels. You may need to modify them if your panel is a different geometry.

### Driver files

The driver itself is composed of the following files (with a few extras thrown in for fun):

| group / Driver File           |  Purpose |
|-----------------|-------------|
| **- User Configuration -** | |
| demo\_hub75_hwGeometry.spin2 | USER MODIFIED configuration: compile-time constants used by demos |
| isp\_hub75_hwPanelConfig.spin2 | USER MODIFIED configuration: compile-time constants, describe the panels attached to each hub75 adapter |
| isp\_hub75_hwBufferAccess.spin2 | USER MODIFIED configuration: compile-time allocation of small tables, allocates small tables for each chain (one enabled by default, remaining two commented out) |
| isp\_hub75_hwBuffers.spin2 | USER MODIFIED configuration: compile-time allocation of small tables, allocates large buffers for each chain (one enabled by default, remaining two commented out) |
| **- Core Driver -** | |
| isp\_hub75_color.spin2 |  Core - Color constants |
| isp\_hub75_colorUtils.spin2 |  Core - Color translation routines, etc. |
| isp\_hub75_display.spin2 | Core - the drawing primitives and screen buffer |
| isp\_hub75_fonts.spin2 | Core - fonts for text support |
| isp\_hub75_hwEnums.spin2 | Core - enumerations for panel, panel connection description |
| isp\_hub75_panel.spin2 | Core - the layer translating screen buffer to PWM buffers |
| isp\_hub75_rgb3bit.spin2 | Core - the PASM Hub75 driver |
| isp\_hub75_screenUtils.spin2 | Core - non-panal drawing primitives |
| **- Extras -** | |
| isp\_hub75\_display_bmp.spin2 | **Optional** - load .bmp file content into screen buffer |
| isp\_hub75_scrollingText.spin2 | **Optional** - adds Scrolling Text |
| isp\_hub75_7seg.spin2 | **Optional** - part of 7-segment demo - a digit |
| isp\_hub75_segment.spin2 | **Optional** - part of 7-segment demo - a segment within a digit |

The structure of these files was chosen in order to (1) make it easier and less memory usage for part of the driver to access other parts and (2) make it easier for you to chose to compile the **optional** parts or not. 

Now let's see how to configure the driver.


## Glossary

Every driver document uses these terms, with exactly these meanings. Each term is defined here, and only here; other documents link to this section.

### adapter

The HUB75 adapter card. Adapter IDs are `HUB75_ADAPTER_1` through `HUB75_ADAPTER_3`, counting from 1. **Adapter *k* drives display *k*-1**: `HUB75_ADAPTER_1` drives the display configured by the `DISP0_` settings, `HUB75_ADAPTER_2` drives `DISP1_`, and `HUB75_ADAPTER_3` drives `DISP2_`.

### display

All the panels on one adapter, drawn on as one surface. Each display is configured by its own group of settings, `DISPn_`, counting from 0 (`DISP0_`, `DISP1_`, `DISP2_`).

### display coordinates

A (row, column) position on the display, with the origin (0, 0) at the top-left. For a rotated display, the origin is the top-left of the display **as mounted**: the corner the viewer sees as top-left.

### panel position

A panel's place in the display, numbered `P0`, `P1`, ... in reading order: left to right along the top row of panels, then each row below in turn, counting only the cells that hold a panel. `P0` is the top-left panel.

### panel coordinates

A (row, column) position within one panel, as the viewer sees it, with the origin (0, 0) at the panel's top-left.

### cable position

A panel's place along the ribbon cable, counted from the adapter: `C0` is the panel the adapter plugs into, `C1` is the next panel along the cable, and so on.

### buffer slot

The driver's internal order of panels within its buffers. Slot 0 is the panel at the far end of the cable, so for a display of N panels, a panel at cable position C occupies slot N-1-C. Buffer slots are used only inside the driver's mapping layer and its comments; configuration and drawing never use them.

### native coordinates

A pixel's (row, column) as the panel's own driver chips address it, before panel rotation is applied.

### panel rotation

How one panel is mounted within the display, written as the direction the panel's identify arrow points: `ARROW_UP`, `ARROW_DOWN`, `ARROW_LEFT` or `ARROW_RIGHT`. A panel whose arrow points down is mounted at 180°.

### display rotation

How the whole assembled display is mounted, set by `DISPn_ROTATION`. Display rotation applies to flat displays only; it does not apply to a cube.

### wiring

The per-panel sentences `DISPn_C0` through `DISPn_C15`, one for each cable position. Each sentence describes the panel at that cable position: where it sits relative to a panel already placed, and its panel rotation. The full grammar is in the wiring guide.

### face

One panel of a cube display, named `TOP`, `BOTTOM`, `FRONT`, `BACK`, `LEFT` or `RIGHT`. The face names are derived from the two cube orientation settings. The cube section of the wiring guide covers faces, folding and corners in full.

### cube orientation

How a cube display is mounted, set by `DISPn_CUBE_TOP` and `DISPn_CUBE_FRONT`: the cable positions of the panels that form the top face and the front face. The front face must share an edge with the top face. Cube orientation takes the place of display rotation for a cube.

### face coordinates

A (face, row, column) position on a cube display. Row and column may run past the edge of the face; a pixel that does is carried across the edge onto the neighbouring face. Each face's up direction is fixed: the four side faces' up points toward `TOP`, the top face's up points toward `BACK` (so text on the top face reads correctly when viewed from the front), and the bottom face's up points toward `FRONT`.

### scan

A panel's scan is written **1/S scan**, where S is the number of row addresses its address lines select. Each address lights several rows at once: **panel rows ÷ S**. For example:

| Panel | Address lines | Scan | Rows lit at once |
|---|---|---|---|
| 64×32 | `ADDR_ABCD` (16 addresses) | 1/16 scan | 2 |
| 64×64 | `ADDR_ABCDE` (32 addresses) | 1/32 scan | 2 |
| 64×32 | `ADDR_ABC` (8 addresses) | 1/8 scan | 4 |

Most panels light two rows at once, one fed by each set of color pins. A panel that lights **four** rows at once, such as a 64×32 1/8-scan panel, needs a different conversion from screen to panel; the driver selects that conversion when the panel's chip flags include `SCAN_4`.


## Configuring the driver

To this driver the panels look like the following:

**NOTE:** the driver supports single panels, horizontal/vertical multi-panel chains, and 2-D panel grids (e.g., a 2x2 arrangement), with per-panel rotation and configurable wire-order. Multi-panel behavior continues to be refined for some driver chips (see the [Change Log](ChangeLog.md) Known Issues).

![Driver panel Setup](images/hub75-driver-board-layout.png)

**Figure 1**: Terms describing a display composed of matrix panels cabled together.

In the above image you see panels describe in terms of rows and columns, and you also see the overall display described in rows and columns but comprised of multiple panels in some arrangement.  The configuration settings following are intended to describe the geometry of your display to the driver.  The organization you describe in these settings causes the underlying driver to allocate buffer space tailored to your display and conditions the hub75 signalling to work correctly for your display. Additionally, if your panels use certain chips the signalling will be changed to conform to what those chips need to work.

Once you haave the driver source files added to your project you will first need to configure the driver by modifying the following values in the file **isp\_hub75_hwPanelConfig.spin2** for each HUB75 adapter that you will be activating in your project:

| Name            | Default | Description |
|-----------------|-------------|-------------|
| `DISPx_ADAPTER_BASE_PIN` | PINS\_P16_P31 |  Identify which pin-group your HUB75 board is connected |
| `DISPx_PANEL_DRIVER_CHIP` | CHIP_UNKNOWN | in most cases UNKNOWN will work. Some specialized panels need a specific driver chip (e.g., those using the FM6126A) |
| `DISPx_PANEL_ADDR_LINES` | {none} | The number of Address lines driving your panels (ADDR\_ABC, ADDR\_ABCD, or ADDR\_ABCDE) See the table of [Chips Supported](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/README.md#chips-supported) for the suggested value for your panels|
| `DISPx_MAX_PANEL_COLUMNS` | {none} | The number of LEDs in each row of your panel ( # pixels-wide) |
| `DISPx_MAX_PANEL_ROWS` | {none} | The number of LEDs in each column of your panel ( # pixels-high) |
| `DISPx_MAX_DISPLAY_COLUMNS` | {none} | The number of LEDs in each ROW of your multi-panel display |
| `DISPx_MAX_DISPLAY_ROWS` | {none} | The number of LEDs in each COLUMN of your multi-panel display |
| `DISPx_COLOR_DEPTH` | {none} | The color depth you wish to display on your panels (compile-time selectable from 3-bit to 8-bit) |
| `DISPx_MAX_PANELS_PER_ROW` | 1 | Number of panels chained horizontally across the display (e.g., 2 for a 2x2 grid) |
| `DISPx_MAX_PANELS_PER_COLUMN` | 1 | Number of panels stacked vertically in the display (e.g., 2 for a 2x2 grid) |
| `DISPx_ROTATION` | ROT\_NONE | Rotation applied to the whole display: `ROT_NONE` and `ROT_180` work on all panels; `ROT_LEFT_90` / `ROT_RIGHT_90` work best on square displays |
| `DISPx_PANELn_ROT` | ROT\_NONE | Per-panel rotation for panel `n` within a grid (`ROT_NONE` / `ROT_180` / `ROT_LEFT_90` / `ROT_RIGHT_90`) |
| `DISPx_WIRE_ENTRY` | {none} | Corner where the HUB75 cable enters the panel grid (e.g., `WIRE_ENTERS_BOT_LEFT`) |
| `DISPx_WIRE_TRAVERSE` | {none} | How the cable traverses the grid (e.g., `WIRE_ROWS_FIRST`) |

**NOTE**: the DISPx_ is a place holder for DISP0\_\*, DISP1\_\* and DISP2\_\* constants indicating the 1st, 2nd, and 3rd HUB75 cards.

## Notes on driver internals

Here's a quick diagram you can use to gain a general understanding of how this driver operates:

![Driver Data Flow](images/hub75-driver-data-flow.jpg)

**Figure 2**: Flow of data within the driver.

Basically, this image shows that the user code draws in 24-bit color values. As these are written to the screen buffer they are translated into PWM values. When the screen is committed (the image is transferred to the display) the screen image is split out into individual PWM buffers one for each of the 16 sub-frames which together comprise one full color video frame being displayed at roughtly 60 fps.

The storage format is shown in the diagram at the various points of translation.

The PASM2 HUB75 driver derives its signal timing from the configured system clock (`_clkfreq`) rather than assuming a fixed frequency. This clock-frequency-independent timing means a demo can change its `_clkfreq` and the panel CLK/latch/blanking pulses continue to meet the panel's timing requirements without hand-tuning the driver.

Another view we'll later be adding to this page is how we allocate and use memory for these buffers as our display sizes change (these sizes are what you configured before you compiled the driver.)  This is only now being decided as we begin to add the multi-panel support.

To create our rich colors we change which LEDs are powered veriy rapidly (PWM). In the latest driver versions we've added a compile-time `COLOR_DEPTH` setting which let's you specify how rich the colors are to be for your display.

This allowed us to use a PWM Frame-set which consists of one plane for each bit in the color depth. This change-over allows us to use 1/4 of the RAM needed for 4 bit color depth than we used in the prior version.  The following digram shows the constituent frames being displayed with the MSBit being displayed for the longest period and the LSBit just being displayed once! The display counts (how many times each frame is shown is simply the power of 2 value. (e.g., in 3-bit the MSBit is shown 2^2 or 4 times, while the next bit is shown 2^1 or 2 times and the LSBit is shown 1 time.

![Displaying Bit Depths](images/BitDepths.png)

**Figure 3**: Creating a full color frame.

### Diagnostic build switches

The driver keeps a set of low-level diagnostic routines (PWM frame / buffer memory dumps) that are normally compiled **out** so they add zero cost to release builds. They are gated by the `DBG_PWM` preprocessor symbol and revived by passing it on the compiler command line:

```
pnut-ts -d -D DBG_PWM demo_hub75_color.spin2     # PWM-frame dump diagnostics compiled in
pnut-ts -d            demo_hub75_color.spin2     # normal build -- diagnostics absent (zero cost)
```

`-D` is global across the object tree, so a single `-D DBG_PWM` reaches `isp_hub75_panel.spin2` (the `dumpBufferHeads` / `dumpFrame*` family) and `isp_hub75_hwBufferAccess.spin2` (`dbgMemDump`). Two notes for maintainers:

- Use `#ifdef DBG_PWM` / `#endif` (conditional compilation) to gate diagnostic **methods and their call sites** -- this removes the routine scaffolding entirely. (A plain `debug()` statement already costs nothing in a non-`-d` build, so it needs no guard.)
- An in-file `#define` does **not** cross object boundaries; only command-line `-D` does. Define `DBG_PWM` on the command line, never per-file.


## Driver Max panels supported

The number of panels this driver supports is based upon how the driver consumes RAM. When we exceed the size that will fit in RAM, we hit a limit message which says `[x] Object files exceed 1M bytes.`. Here's a table depicting the MAX Panels the driver currently supports in terms of panel size, number of panels and the resulting total pixel count.

Driver v1.x and v2.x:

| Panel Size | max panels | total pixels | Notes |
| --- | --- | --- | --- |
| 32x32 | 27 | 27,648 |
| 64x32 | 13 | 26,624 |
| 64x64 | 6 | 24,576 | our cube!
| 128x64 | 3 | 24,576 |

Driver v3.x:

| Panel Size | max panels | total pixels | Notes |
| --- | --- | --- | --- |
| 32x32 | 64 | 65,536 |
| 64x32 | 32 | 65,536 |
| 64x64 | 16 | 66,536 | our cube uses 6 of these!
| 128x64 | 8 | 66,536 |
| 128x128 | 4 | 66,536 |

Generally you can make a single display out of many panels from ranging from 256x256 pixels to 2048x32 pixels or 32x2048 pixels (how high is your ceiling?). With panels ranging from p1.5 to p10 (1.5mm to 10mm led center-to-center) these displays could be quite large and of course will draw many amps of 5V. ;-)

**NOTE**: The driver supports using 1-3 HUB75 adapters. This means you can have up to three chains of panels attached to one P2. The table above specifies how many total pixels (total panels of given goemetry) can be supported. When configuring multiple HUB75 adapters this total is now spread across all adapters.  In other words, the pixel count of all panels attached to a single P2 must not exceed the limits shown in the table.

**NOTE2**: If you have panels by different vendors  (different driving ICs) you can use multiple HUB75 cards to accomodate this. Just make sure you have all panels of a given IC type on a single chain. Put all the panels with the next IC type on the next chain, the next HUB75 adapter.  Drive all the chains from the single P2.

### Research Needed

One of my upcoming efforts is to review in detail how the driver uses RAM. I'll look into:

- using the LUTs 
- using the EDGE on board RAM 
- fine tuning how the driver allocates RAM

My hope would be that I'll find that using one or more of these approaches will reduce our RAM usage even further.

## Notes on HUB75 pins used by driver

Our P2 Eval HUB75 Adapter board is built to drive up to 5 address pins (A-E) so we can drive many HUB75 panel variants.

Here's a simple diagram showing related pin groups:

![Hub75 pinout](images/hub75e_pinout.png)




---

*If you have any questions about what I've written here, file an issue and I'll respond with edits to this doc to attempt to make things more clear.*

Thanks for Reading, following along. I look forward to seeing what adaptations you come up with. Please let me know when you do!

```
Stephen M. Moraco
Lead developer
Iron Sheep Productions, LLC.
```

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

Last Updated: 15 Jan 2024 15:45 MST

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge
