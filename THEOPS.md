# Theory of Operations:
## Hub75 RGB LED Matrix panel driver

![Project Maintenance][maintenance-shield]

On this page you'll learn what files make up the driver (and/or come with it) and what their purpose is, how to configure the dirver for your hardware, and also a bit about how the driver actually works. 

(*I expect that this file will continue to grow over time as our driver becomes more capable. -Stephen*)


### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | Driver Details | [Change Log](ChangeLog.md)

Within this page:

- [Driver Files](#driver-file-organization) - the purpose of each file found in the driver
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
| isp\_hub75_hwPanelsConfig.spin2 | USER MODIFIED configuration: compile-time constants, describe the panels attached to each hub75 adapter |
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


## Configuring the driver

To this driver the panels look like the following:

**NOTE:** keep in mind, we only support a single panel for this first release. Multi-panel is in progress and will be release shortly!

![Driver panel Setup](images/hub75-driver-board-layout.png)

**Figure 1**: Terms describing a display composed of matrix panels cabled together.

In the above image you see panels describe in terms of rows and columns, and you also see the overall display described in rows and columns but comprised of multiple panels in some arrangement.  The configuration settings following are intended to describe the geometry of your display to the driver.  The organization you describe in these settings causes the underlying driver to allocate buffer space tailored to your display and conditions the hub75 signalling to work correctly for your display. Additionally, if your panels use certain chips the signalling will be changed to conform to what those chips need to work.

Once you haave the driver source files added to your project you will first need to configure the driver by modifying the following values in the file **demo\_hub75_hwGeometry.spin2**:

| Name            | Default | Description |
|-----------------|-------------|-------------|
| `ADAPTER_BASE_PIN` | PINS\_P16_P31 |  Identify which pin-group your HUB75 board is connected |
| `PANEL_DRIVER_CHIP` | CHIP_UNKNOWN | in most cases UNKNOWN will work. Some specialized panels need a specific driver chip (e.g., those using the FM6126A) |
| `PANEL_ADDR_LINES` | {none} | The number of Address lines driving your panels (ADDR\_ABC, ADDR\_ABCD, or ADDR\_ABCDE) |

And by modifying the following values in the file **isp\_hub75_hwBuffers.spin2**:

| Name            | Default | Description |
|-----------------|-------------|-------------|
| `MAX_PANEL_COLUMNS` | {none} | The number of LEDs in each row of your panel ( # pixels-wide) |
| `MAX_PANEL_ROWS` | {none} | The number of LEDs in each column of your panel ( # pixels-high) |
| `MAX_DISPLAY_COLUMNS` | {none} | The number of LEDs in each ROW of your multi-panel display |
| `MAX_DISPLAY_ROWS` | {none} | The number of LEDs in each COLUMN of your multi-panel display |
| `COLOR_DEPTH` | {none} | The color depth you wish to display on your panels (compile-time selectable from 3-bit to 8-bit) |
| `Roataion` | {none} | The color depth you wish to display on your panels (compile-time selectable from 3-bit to 8-bit) |

**NOTE:** there will be a copy of the above constants for each HUB75 adapter card you wish to activate!

## Notes on driver internals

Here's a quick diagram you can use to gain a general understanding of how this driver operates:

![Driver Data Flow](images/hub75-driver-data-flow.jpg)

**Figure 2**: Flow of data within the driver.

Basically, this image shows that the user code draws in 24-bit color values. As these are written to the screen buffer they are translated into PWM values. When the screen is committed (the image is transferred to the display) the screen image is split out into individual PWM buffers one for each of the 16 sub-frames which together comprise one full color video frame being displayed at roughtly 60 fps.

The storage format is shown in the diagram at the various points of translation.

Another view we'll later be adding to this page is how we allocate and use memory for these buffers as our display sizes change (these sizes are what you configured before you compiled the driver.)  This is only now being decided as we begin to add the multi-panel support.

To create our rich colors we change which LEDs are powered veriy rapidly (PWM). In the latest driver versions we've added a compile-time `COLOR_DEPTH` setting which let's you specify how rich the colors are to be for your display.

This allowed us to use a PWM Frame-set which consists of one plane for each bit in the color depth. This change-over allows us to use 1/4 of the RAM needed for 4 bit color depth than we used in the prior version.  The following digram shows the constituent frames being displayed with the MSBit being displayed for the longest period and the LSBit just being displayed once! The display counts (how many times each frame is shown is simply the power of 2 value. (e.g., in 3-bit the MSBit is shown 2^2 or 4 times, while the next bit is shown 2^1 or 2 times and the LSBit is shown 1 time.

![Displaying Bit Depths](images/BitDepths.png)

**Figure 3**: Creating a full color frame.


## Driver Max panels supported

The number of panels this driver supports is based upon how the driver consumes RAM. When we exceed the size that will fit in RAM, we hit a limit message which says `[x] Object files exceed 1M bytes.`. Here's a table depicting the MAX Panels the driver currently supports in terms of panel size, number of panels and the resulting total pixel count.

| Panel Size | max panels | total pixels | Notes |
| --- | --- | --- | --- |
| 32x32 | 27 | 27,648 |
| 64x32 | 13 | 26,624 |
| 64x64 | 6 | 24,576 | our cube!
| 128x64 | 3 | 24,576 |

**NOTE**: The driver supports using 1-3 HUB75 adapters. This means you can have up to three chains of panels attached to one P2. The table above specifies how many total pixels (total panels of given goemetry) can be supported. When configuring multiple HUB75 adapters this total is now spread across all adapters.  In other words, the pixel count of all panels attached to a single P2 must not exceed the limits shown in the table.

**NOTE2**: If you have panels by different vendors  (different driving ICs) you can use multiple HUB75 cards to accomodate this. Just make sure you have all panels of a given IC type on a single chain. Put all the panels with the next IC type on the next chain, the next HUB75 adapter.  Drive all the chains from the single P2.

### Research Needed

One of my upcoming efforts is to review in detail how the driver uses RAM. I'll look into:

- using the LUTs 
- using the EDGE on board RAM 
- fine tuning how the driver allocates RAM

My hope would be that I'll find that using one or more of these approaches will increase the number of panels this driver can support.

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

Last Updated: 02 Dec 2020, 00:58 MST

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge
