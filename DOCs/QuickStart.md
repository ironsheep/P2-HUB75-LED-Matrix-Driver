# P2 HUB75 LED Matrix Driver - Quick Start

A Parallax Propeller v2 driver for HUB75 RGB LED matrix panels, single or multi-panel. This page takes you from wired panels to a program that draws on them, with a few short examples to copy.

![Project Maintenance][maintenance-shield]
[![License][license-shield]](../LICENSE)

On this Page:

- [Bring up your display](#bring-up-your-display) - the five steps from a new adapter to a working display
- [Start the driver](#start-the-driver) - the objects to include and the one start call
- [Examples](#examples) - fill and pixel, text, scrolling text, a BMP image
- [Making a BMP image](#making-a-bmp-image) - the file the driver loads
- [A second adapter](#a-second-adapter) - one display object for each adapter
- [Where next](#where-next) - the demos and the doc comments

Additional pages:

- [README](../README.md) - the project overview and the table of demos
- [Wiring Guide](WiringGuide.md) - the display block, the panel list, the identify screen and every startup message
- [Troubleshooting](Troubleshooting.md) - something looks wrong? Find the symptom
- [Driver Details](../THEOPS.md) - how the driver works

### Pages: [README](../README.md) | [Hardware Turn-on](../HardwareTurnon.md) | [Driver Details](../THEOPS.md) | [Wiring Guide](WiringGuide.md) | [Troubleshooting](Troubleshooting.md) | Quick Start | [Change Log](../ChangeLog.md)

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!

> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](../images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Bring up your display

The path from a new adapter and panels to a working display is five steps. Every demo and test top file named here is in the `driver/` folder.

1. **Attach the adapter.** The [HUB75 adapter board](../HUB75-brd-config.md) plugs onto a pair of 2x6 accessory headers, one of the three 16-pin groups P0-P15, P16-P31 or P32-P47. Its pins are listed in the [adapter pinout](../HUB75-brd-config.md#hub75-adapter-board-pinout).
2. **Check the pins (optional, with a logic analyzer).** `isp_hub75_anlyCheck.spin2` is a standalone top file, not part of the driver: it drives every adapter pin so you can confirm your analyzer connections and the wiring. It takes its pin group from `MTX_LED_BASE_PIN` at the top of the file, not from the driver's configuration, and runs until you stop it. `test_hub75_pin_identify.spin2` toggles each adapter pin at its own known frequency so you can tell which analyzer lead is on which pin.
3. **Describe your hardware.** Edit `isp_hub75_hwPanelConfig.spin2`, the only file you change for a setup. For the adapter's display (`DISP0_` for the first adapter) set the pin group (`DISP0_ADAPTER_BASE_PIN`), the panel chip (`DISP0_PANEL_DRIVER_CHIP`), the panel size (`DISP0_PANEL_COLUMNS`, `DISP0_PANEL_ROWS`) and the colour depth (`DISP0_COLOR_DEPTH`); the driver works out the address lines. Then list the panels in cable order, one sentence each saying its row, its column and which way its top points. The settings and the panel list are explained in the [Wiring Guide](WiringGuide.md#the-display-block); if something looks wrong, see [Troubleshooting](Troubleshooting.md). Start with every panel in one row with its top up (`TOP_UP`) and no mounting override.
4. **Run the identify program.** `demo_hub75_numberPanels.spin2` starts the adapter with one call, `display.start(display.HUB75_ADAPTER_1)`, and draws on every panel an arrow, its cable position (`C`*k*) and its panel position (`P`*p*), each panel on its own background colour. Before the panels start, the driver checks your panel list and prints the layout it derived to the DEBUG terminal; a mistake is named by panel (`DISP0 C2: ...`) and startup stops, with the full list of messages in the [Wiring Guide](WiringGuide.md#startup-messages). When the panels read right, the `P` labels run in reading order and every arrow points up. If not, the [Wiring Guide](WiringGuide.md#filling-in-your-config-from-the-identify-screen) shows how to read the screen and correct the panel list.
5. **Run the demos.** `demo_hub75_color.spin2`, `demo_hub75_text.spin2`, `demo_hub75_scroll.spin2` and the others show the drawing calls; each sets its own clock and starts the adapter the same way.

A display of six square panels folded into a cube is configured the same way, with the top and front faces marked in the panel list; see [the cube](WiringGuide.md#the-cube).

## Start the driver

Your program is a top file. It sets the clock, names the objects it uses, and starts the adapter with one call. This one fills the display blue and leaves it lit:

```
CON
    _CLKFREQ = 335_000_000                  ' system clock
    DEBUG_BAUD = 2_000_000

OBJ
    color   : "isp_hub75_color"
    display : "isp_hub75_display"

PUB main()
    display.start(display.HUB75_ADAPTER_1)      ' start the first adapter
    display.fillScreen(color.cBlue)             ' draw into the screen buffer
    display.commitScreenToPanelSet()            ' show it on the panels
    repeat                                      ' keep the program running
```

`isp_hub75_display` is the object your program talks to. `isp_hub75_color` holds the colour names (`color.cRed`, `color.cYellow` and so on). Copy your top file next to the driver files, or into the `driver/` folder, so the compiler finds them. `display.start()` reads your configuration, checks the panel list, and starts the refresh cog.

Drawing calls change a screen buffer in hub RAM; nothing shows on the panels until you call `display.commitScreenToPanelSet()`. Draw what you want, then commit once.

## Examples

Each example below is lifted from a demo. The `OBJ` block lists every object the examples use; add the ones a method needs to your top file.

```
OBJ
    color      : "isp_hub75_color"
    pixels     : "isp_hub75_screenUtils"
    hub75Bffrs : "isp_hub75_hwBufferAccess"
    display    : "isp_hub75_display"
    bmpHandler : "isp_hub75_display_bmp"
```

### Fill and pixel

From `demo_hub75_color.spin2` (its `demoParallax()` draws the lines, `numberTheRows()` the pixels) and `demo_hub75_boundary.spin2` (the box): boxes and lines take a row and a column, a pixel takes the adapter's chain index.

```
PRI fillAndPixel() | chainIndex
    chainIndex := hub75Bffrs.indexForHub75ChainId(display.HUB75_ADAPTER_1)
    display.clearScreenBuffer()
    display.drawBoxOfColor(0, 0, 20, 10, TRUE, color.cRed)       ' top row, left column, width, height, filled
    display.drawLineOfColor(0, 0, 15, 30, color.cYellow)         ' from row, from column, to row, to column
    pixels.drawPixelAtRC(chainIndex, 5, 40, color.cWhite)        ' one pixel: row 5, column 40
    display.commitScreenToPanelSet()
```

`display.fillScreen(rgbColor)` fills the whole display, as in the program above.

### Text

From `demo_hub75_color.spin2` and `demo_hub75_text.spin2`: text is placed by line and column of the font's character grid.

```
PRI showText()
    display.clearScreenBuffer()
    display.setTextFont(display.TEXT_FONT_5X7)
    display.setColoredTextAtLnCol(0, 0, string("iron sheep"), color.cOrange)    ' line 0, column 0
    display.setColoredTextAtLnCol(1, 0, string("led matrix"), color.cWhite)     ' line 1, column 0
    display.commitScreenToPanelSet()
```

### Scrolling text

From `demo_hub75_scroll.spin2`: start a scrolling region on a text line, say how long it runs, then step it and commit in a loop.

```
DAT
    scrollMsg   BYTE    "Hello from the P2   ", 0

PRI scrollText() | scrollerID
    display.clearScreenBuffer()
    display.setTextFont(display.TEXT_FONT_5X7)
    scrollerID := display.scrollColoredTextOnLn(1, @scrollMsg, display.DIR_TO_LEFT, color.cLime)
    display.configureScrollLoopMode(scrollerID, display.SCROLL_FOREVER)
    repeat
        display.animateScroll()
        display.commitScreenToPanelSet()
        waitms(30)                                  ' the pause sets the scroll speed
```

The other directions are `display.DIR_TO_RIGHT`, `display.DIR_UP` and `display.DIR_DOWN`. `display.SCROLL_ONCE_TO_CLEAR` stops the region once the last of the text has gone by; `display.isScrollingComplete()` tells you when.

### A BMP image

From `demo_hub75_color.spin2`: the image file is part of your program, placed in a `DAT` block with `FILE`, and the loader draws it from there.

```
DAT
    bmpFile     FILE    "TstBG-Up.bmp"

PRI showBmp() | chainIndex, status
    chainIndex := hub75Bffrs.indexForHub75ChainId(display.HUB75_ADAPTER_1)
    status := bmpHandler.fillScreenFromBMP(chainIndex, @bmpFile)
    if status == bmpHandler.SUCCESS
        display.commitScreenToPanelSet()
```

`TstBG-Up.bmp` is in the `driver/` folder; use your own file name for your own image. A file the loader rejects draws nothing and returns `bmpHandler.E_BMP_NOT_24BIT`; the DEBUG terminal says so. The next section says what the loader accepts.

## Making a BMP image

BMP is the image format the driver loads. The loader (`isp_hub75_display_bmp.spin2`) accepts a file that is:

- **A BMP file.** It begins with the two bytes `BM`.
- **24 bits per pixel.** Red, green and blue, 8 bits each. A file with a palette, or with any other number of bits per pixel, is rejected.
- **Uncompressed.** The file's compression field must be zero.
- **Any size, at least one pixel wide.** The image is not scaled. It is centred on the display; where the display is larger, the rest of the display is left as it was drawn, and where the image is larger, the part that falls off the display is not drawn. For the image to fill the display exactly, make it the display's width and height in pixels.
- **Either row order.** Files that store the bottom row first (the usual) and the top row first both load.

To make one, save or export your picture from an image editor as a 24-bit, uncompressed BMP, sized to your display. Because the file is part of your program, a large image uses hub RAM; the compiler tells you if the program no longer fits ([out of memory](Troubleshooting.md#out-of-memory)).

`bmpHandler.placeBMP(chainIndex, @bmpFile, rotation)` places the same kind of file turned by `bmpHandler.ROT_0`, `ROT_90`, `ROT_180` or `ROT_270`. `fillScreenFromBMP()` is `placeBMP()` at `ROT_0`.

## A second adapter

Describe the second adapter's display in the `DISP1_` group of `isp_hub75_hwPanelConfig.spin2` (the third's in `DISP2_`): write `#DEFINE DISP1_PRESENT` (or `#DEFINE DISP2_PRESENT`) and then that display's settings and panel list. The file ships with a ready template for the second display in its comments; remove the leading `'` from each line and edit it ([the template and the other optional settings](WiringGuide.md#more-displays-and-optional-settings)). Then give each adapter its own display object and start it with its adapter ID. There is no file to edit for the buffers.

```
CON
    _CLKFREQ = 335_000_000
    DEBUG_BAUD = 2_000_000

    FRONT_PANEL = 0                         ' which display object drives which adapter
    BACK_PANEL = 1

OBJ
    color       : "isp_hub75_color"
    display[2]  : "isp_hub75_display"       ' a display object for each adapter

PUB main()
    display[FRONT_PANEL].startWithId(FRONT_PANEL, display.HUB75_ADAPTER_1)
    display[BACK_PANEL].startWithId(BACK_PANEL, display.HUB75_ADAPTER_2)

    display[FRONT_PANEL].fillScreen(color.cBlue)
    display[FRONT_PANEL].commitScreenToPanelSet()
    display[BACK_PANEL].fillScreen(color.cRed)
    display[BACK_PANEL].commitScreenToPanelSet()
    repeat
```

`startWithId` is `start` plus an identifier that labels each adapter's debug messages. With more than one adapter, every call is `display[FRONT_PANEL].method()` or `display[BACK_PANEL].method()`, and each display commits its own screen to its own panels. A display that has no panel list (no `#DEFINE DISPn_PRESENT`) cannot be started; the driver says so and stops.

## Where next

- **The demos.** The [README](../README.md#writing-display-code-for-your-panels) lists every demo and test program with what it shows. Most are built for a 64x32 panel; change the sizes they assume to match yours.
- **The calls.** Every public method of `driver/isp_hub75_display.spin2` has a doc comment above it (the lines that start with `''`) giving what it does, its parameters and what it returns. The scrolling and BMP calls are documented the same way in `driver/isp_hub75_display_bmp.spin2`.
- **Configuration.** The [Wiring Guide](WiringGuide.md) covers the display block and the panel list, and [Troubleshooting](Troubleshooting.md) covers a display that does not look right.

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
