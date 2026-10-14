# P2 HUB75 LED Matrix Driver - Update to v4.0 Checklist
Convert your code from v3.x to v4.x

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | [Driver Details](THEOPS.md) | [Configuration Guide](DOCs/WiringGuide.md) | [Change Log](ChangeLog.md)

On this Page:

- [Introduction](#introduction) - what changed and the four jobs
- [Convert your panel layout settings](#convert-your-panel-layout-settings) - the settings table and the panel list
- [Rename your pin group](#rename-your-pin-group) - the three pin-group names
- [The other configuration files](#the-other-configuration-files) - what you no longer edit
- [Change how your program starts the driver](#change-how-your-program-starts-the-driver) - one call per adapter
- [Starting a second or third adapter](#starting-a-second-or-third-adapter) - a display object for each
- [Check your work with the identify screen](#check-your-work-with-the-identify-screen) - confirm the panel list
- [Two things that now mean something different](#two-things-that-now-mean-something-different) - rotation and panel numbers
- [If your program calls the buffers object](#if-your-program-calls-the-buffers-object-or-the-manual-chip-flags-directly) - removed calls and the manual chip flags
- [What else is new](#what-else-is-new) - the rest of the v4.x changes

Additional pages:

- [Configuration Guide](DOCs/WiringGuide.md) - The full grammar of the panel sentences, with seven worked examples
- [Quick Start](DOCs/QuickStart.md) - From wired panels to a running program
- [Troubleshooting](DOCs/Troubleshooting.md) - Symptom, cause and fix when a display does not look right
- [Update to v3.0 Checklist](Checklist-v2-v3.md) and [Update to v2.0 Checklist](Checklist-v1-v2.md) - the earlier conversions

## Introduction

**In the v3.x driver** you described the layout of your panels with two numbers (how many panels per row and per column), you uncommented code in two more files to add a second or third adapter, and you started the driver with a sequence of calls that handed it buffer pointers.

**In the v4.x driver** you describe each display with a few settings and a **panel list**: one short sentence per panel saying which row it is in, which column, and which way its top points. You start each adapter with **one call**. The driver works out the rest (how many panels, the address lines, the size of the display, the grid, where each panel sits and how it is turned), checks your list, and tells you exactly which sentence is wrong if one is.

This is a **breaking** change: a v3.x `isp_hub75_hwPanelConfig.spin2` and a v3.x top-level file do not compile against v4.x. Converting takes minutes. There are four jobs:

1. [Convert your panel layout settings to a panel list](#convert-your-panel-layout-settings)
2. [Rename your pin group](#rename-your-pin-group)
3. [Leave the other configuration files alone](#the-other-configuration-files)
4. [Change how your program starts the driver](#change-how-your-program-starts-the-driver)

Then [check your work with the identify screen](#check-your-work-with-the-identify-screen), and look at [two things that now mean something different](#two-things-that-now-mean-something-different) (rotation, and panel numbers).

All the terms used here (adapter, display, cable position, panel position, and so on) are defined once in the [glossary](THEOPS.md#glossary). The full grammar of the sentences, with seven worked examples, is in the [Configuration Guide](DOCs/WiringGuide.md); this checklist only shows you how to convert.

## Convert your panel layout settings

In **isp\_hub75_hwPanelConfig.spin2**, each adapter has a display, `DISP0_`, `DISP1_` and `DISP2_`. The chip and color depth settings keep their names and meaning, but check two things: the default color depth is now 8-bit, and the panel width must be a multiple of 4 (see [What else is new](#what-else-is-new)). The table shows what happens to each v3.x setting:

| v3.x setting (old) | v4.x (new) |
|---|---|
| `DISPx_MAX_PANELS_PER_ROW`, `DISPx_MAX_PANELS_PER_COLUMN` | Removed. The panel list says where each panel is; the grid is worked out from it |
| `DISPx_MAX_DISPLAY_COLUMNS`, `DISPx_MAX_DISPLAY_ROWS` (if you used them) | Removed. The display size is worked out from the panel list |
| `DISPx_MAX_PANEL_COLUMNS`, `DISPx_MAX_PANEL_ROWS` | Renamed `DISPx_PANEL_COLUMNS`, `DISPx_PANEL_ROWS` |
| `DISPx_PANEL_ADDR_LINES` (`hwEnum.ADDR_ABC`, `ADDR_ABCD` or `ADDR_ABCDE`) | Removed. The driver works the address lines out from the panel rows and the chip's scan |
| `DISPx_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31` | Kept, with the pin group renamed: `hwEnum.PIN_GROUP_P16_P31` (see [below](#rename-your-pin-group)) |
| `DISPx_PANEL_DRIVER_CHIP`, `DISPx_COLOR_DEPTH` | Kept |
| `DISPx_SCRN_SIZE_IN_BYTES`, `DISPx_SCRN_SIZE_IN_LONGS`, `DISPx_PWM_FRAME_SIZE_IN_BYTES`, `DISPx_PWM_FRAME_SIZE_IN_LONGS`, `DISPx_FRAMESET_SIZE_IN_LONGS`, `DISPx_BITS_PER_COLOR`, `DISPx_BYTES_PER_COLOR`, `DISPx_MAX_PANELS` | Removed. The buffers are sized from the length of the panel list. If your program read one, ask the driver instead (`hub75Bffrs.displaySizeInLongs()`, `hub75Bffrs.pwmFrameSizeInBytes()`) |
| `DISPx_ROTATION` (`hwEnum.ROT_NONE`, `ROT_RIGHT_90`, `ROT_LEFT_90`, `ROT_180`) | Removed as a v3.x setting, and the `ROT_NONE`, `ROT_RIGHT_90`, `ROT_LEFT_90` names with it; v4.x has an optional setting of the same name that means something else (see [below](#two-things-that-now-mean-something-different)) |
| *(not in v3.x)* | The panel list, one sentence per panel; for a cube, `CUBE_TOP` and `CUBE_FRONT` on two of its sentences |

### Write one sentence per panel

Look at the **front** of your display and number the panels along the ribbon cable from the adapter: the panel the adapter plugs into is `C0`, the next along the cable is `C1`, and so on. The panel list is a `DAT` list with one `LONG` per panel, in that order, and each sentence says where the panel is as you see it from the front, and which way its top points:

```
LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP
```

"This panel is in row 0, column 1, and its top points up." Row 0 is the top row of panels and column 0 the left column. Join the words with `|`, never `+`. Write every `TOP_` word `TOP_UP` to begin with; you will correct them with the identify screen.

### Converting your row of panels

A v3.x display is one row of panels (or one column). Each panel sits next to the one before it along the cable, so the panel list for a row is row 0 with the next column for each sentence, and for a column it is the next row in column 0:

| Panels | `C0` | `C1` | `C2` |
|---|---|---|---|
| one row, cable entering at the left | `ROW_0 \| COL_0 \| TOP_UP` | `ROW_0 \| COL_1 \| TOP_UP` | `ROW_0 \| COL_2 \| TOP_UP` |
| one column, cable entering at the top | `ROW_0 \| COL_0 \| TOP_UP` | `ROW_1 \| COL_0 \| TOP_UP` | `ROW_2 \| COL_0 \| TOP_UP` |

Write the `hwEnum.` prefix on each word. A cable that enters at the right end of a row starts at the highest column and counts down.

v4.x can also describe layouts v3.x could not: grids, serpentine cabling, panels turned within the display, and gaps (an L shape, say), where the gap is simply a cell no sentence names. The Configuration Guide's [worked examples](DOCs/WiringGuide.md#seven-worked-examples) show each.

On panels that are not square, every `TOP_` word must be `TOP_UP` or `TOP_DOWN`, or every one must be `TOP_LEFT` or `TOP_RIGHT`; the driver tells you if they are mixed.

### What it looks like

A two-panel v3.x display, side by side (old settings first):

```python
    ' v3.x (old)
    DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_MAX_PANEL_COLUMNS = 64
    DISP0_MAX_PANEL_ROWS = 32
    DISP0_MAX_PANELS_PER_ROW = 2
    DISP0_MAX_PANELS_PER_COLUMN = 1
    DISP0_COLOR_DEPTH = hwEnum.DEPTH_6BIT
```

becomes, in v4.x:

```python
    ' v4.x (new): the adapter plugs into the left panel, the ribbon runs right to the next
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 32
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_6BIT

DAT
disp0Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP
disp0PanelsEnd
```

Nothing is written for the address lines, the number of panels or the display size. The list must be bracketed by the labels `disp0Panels` (before the first sentence) and `disp0PanelsEnd` (after the last); the number of panels is the length between them.

A display you do not have is not written at all. For a second or third display see [Starting a second or third adapter](#starting-a-second-or-third-adapter).

## Rename your pin group

The pin groups are renamed, and only the three groups the adapter can use remain:

| v3.x (old) | v4.x (new) |
|---|---|
| `hwEnum.PINS_P0_P15` | `hwEnum.PIN_GROUP_P0_P15` |
| `hwEnum.PINS_P16_P31` | `hwEnum.PIN_GROUP_P16_P31` |
| `hwEnum.PINS_P32_P47` | `hwEnum.PIN_GROUP_P32_P47` |
| `hwEnum.PINS_P48_P63` | Removed: pins 48-63 overlap the P2's reserved pins |

Change `DISPx_ADAPTER_BASE_PIN` in each display you use; an old name does not compile.

## The other configuration files

In v3.x you edited **isp\_hub75_hwBufferAccess.spin2** and **isp\_hub75_hwBuffers.spin2** to add a second or third adapter (commenting code in and out, in about nine places). **In v4.x you do not touch them.** `isp_hub75_hwBuffers.spin2` is gone: the buffers of every display are held in `isp_hub75_hwPanelConfig.spin2` below its user section, each sized from the length of that display's panel list, and `isp_hub75_hwBufferAccess.spin2` is not edited.

If you edited either file for v3.x, take the v4.x copies from the release and discard your edits. They contain nothing of yours.

## Change how your program starts the driver

The v3.x startup took a handful of calls, handed the driver buffer pointers, and named `isp_hub75_hwBuffers` in your top-level file:

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display     :   "isp_hub75_display"
    user        :   "isp_hub75_hwPanelConfig"
    scrnBuffers :   "isp_hub75_hwBuffers"               ' v3.x only

PUB main() | chainIndex, cog
    ' v3.x (old)
    hub75Bffrs.configure(hub75Bffrs.HUB75_ADAPTER_1, user.DISP0_ADAPTER_BASE_PIN, user.DISP0_PANEL_DRIVER_CHIP, user.DISP0_PANEL_ADDR_LINES)
    chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)
    display.setBufferPointers(chainIndex, scrnBuffers.chain0Ptrs())
    cog := display.start(chainIndex)
```

In v4.x it is one call, and your top-level file no longer names `isp_hub75_hwBuffers` or reads the settings itself:

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display     :   "isp_hub75_display"

PUB main() | chainIndex
    ' v4.x (new)
    chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)   ' only if you call hub75Bffrs.* methods
    display.start(display.HUB75_ADAPTER_1)
```

`display.start()` reads the adapter's settings, checks your panel list, derives the layout, hands the adapter its buffers and starts the driver. If a sentence is wrong, or no cog is free for the driver, it prints a `HUB75:` message and stops the program; every message is listed in the Configuration Guide's [startup messages](DOCs/WiringGuide.md#startup-messages). It returns only when the driver started (the returned value is the driver's cog ID plus one, never 0 or -1), so a v3.x check of its result for failure can be taken out. The calls `configure` and `setBufferPointers` are gone, and your program no longer calls the buffer object's pointer methods (the start call fetches the pointers by adapter).

**Adapter *k* drives display `DISP(k-1)_`**: `HUB75_ADAPTER_1` starts the display configured by `DISP0_`, `HUB75_ADAPTER_2` starts `DISP1_`, and `HUB75_ADAPTER_3` starts `DISP2_`.

## Starting a second or third adapter

Describe the second adapter's display in the `DISP1_` group (the third's in `DISP2_`): write `#DEFINE DISP1_PRESENT` (or `#DEFINE DISP2_PRESENT`) and then that display's settings and panel list. The file ships with a ready template for the second display in its comments; remove the leading `'` from each line and edit it ([the template and the other optional settings](DOCs/WiringGuide.md#more-displays-and-optional-settings)). Then give each adapter its own display object and start it with its adapter ID. There is no file to edit for the buffers.

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display[2]  :   "isp_hub75_display"                 ' a display object for each adapter

CON
    FRONT_PANEL = 0                                     ' which display object drives which adapter
    BACK_PANEL = 1

PUB main()
    display[FRONT_PANEL].startWithId(FRONT_PANEL, display.HUB75_ADAPTER_1)
    display[BACK_PANEL].startWithId(BACK_PANEL, display.HUB75_ADAPTER_2)

    ' with more than one adapter, all your calls are display[FRONT_PANEL].method() or
    ' display[BACK_PANEL].method(), and each display commits its own screen to its own panels
```

`startWithId` is `start` plus an identifier that labels each adapter's debug messages. A display that has no panel list (no `#DEFINE DISPn_PRESENT`) cannot be started; the driver says so and stops.

## Check your work with the identify screen

Build and run **demo\_hub75\_numberPanels.spin2**, the identify screen, with every panel written `TOP_UP`. It labels each panel with its cable position (`C`*k*), its place in the display (`P`*p*, in reading order) and an arrow showing which way the panel's own top points. Reading it, and fixing a sentence from what it shows, is explained step by step in the Configuration Guide's [identify section](DOCs/WiringGuide.md#filling-in-your-config-from-the-identify-screen). In short:

- `P` labels in reading order and every arrow up: your panel list is right.
- `P` labels out of order: a `ROW_` or `COL_` word is wrong. The `C` labels are always where the panels really are, so use them to fix the sentence.
- An arrow pointing another way, or upside-down text: that panel's `TOP_` word is wrong; write the one that matches the way the arrow points.

## Two things that now mean something different

### Display rotation is a mounting override

In v3.x `DISPx_ROTATION` turned the content of the display. In v4.x a display is described as it was built, with the top edge of its frame at the top, and `DISPx_ROTATION` is an optional **mounting override**: you say where the frame's top edge now points when you hang the display another way. It is switched on with a flag:

```python
#DEFINE DISP0_ROTATED
CON DISP0_ROTATION = hwEnum.TOP_TO_RIGHT
```

The words are `AS_BUILT` (the default, no flag needed), `TOP_TO_RIGHT` (the display is turned 90 degrees clockwise), `TOP_TO_BOTTOM` (180 degrees) and `TOP_TO_LEFT` (90 degrees counter-clockwise). The driver draws so that your content reads upright once the display is mounted. At 90 and 270 degrees the display size the driver reports is the size as mounted (width and height swap, and so do the text grid's columns and lines), and it works on displays of any shape, not only square ones. If you used a rotation in v3.x, delete the line, run identify, and then add the override that matches how you hung the display ([display rotation](DOCs/WiringGuide.md#display-rotation)).

To turn an **image**, use the content rotation parameter of the new image call, `bmp.placeBMP(chain, file, rotation)` with `bmp.ROT_0`, `bmp.ROT_90`, `bmp.ROT_180` or `bmp.ROT_270`; it works for an image of any size. It is not a display setting.

### Panel numbers are panel positions

Calls that name a panel (`fillPanel`, `setCursorOnPanel`, `drawPanelBox`, `drawPanelLine`, `scrollColoredTextOnLnOfNPanels` and their siblings) take a **panel position**: `P0` is the top-left panel as the display hangs, and the numbers run in reading order. On a v3.x row of panels that is the numbering you already use, panel 0 at the left, so nothing changes. On a layout v3.x could not describe, check any panel number against the identify screen. Panel-centric calls now **clip** at the panel's edge instead of spilling onto a neighbour.

## If your program calls the buffers object or the manual chip flags directly

Programs that draw only through the display object need nothing here.

- **Removed from `isp_hub75_hwBufferAccess.spin2`:** `configure()`, `setBufferPointers()`, `panelsPerRow()`, `panelsPerColumn()`, `correctedColor()`, `correctedSingleColor()` and `colorAtDesiredBitWidth()`. `pwmFrameCount()` and the `PWM_FRAMES_3BIT` ... `PWM_FRAMES_8BIT` constants are removed too: the v4 refresh shows one frame per bit of colour depth, so call `colorDepth()` instead. `panelRotation()` is now `displayRotation()`. Where you need the layout's size or a panel's place, ask the layout: `layoutSizeAndRotation()`, `layoutAreaOfPanel()`, `positionAtDisplayPixel()`, `positionForCable()`.
- **Removed with `isp_hub75_hwBuffers.spin2`:** its `chain0Ptrs()`, `chain1Ptrs()` and `chain2Ptrs()`; `display.start()` fetches the pointers itself.
- **Writing the screen buffer yourself.** Scrolling regions move the frame they drew last and draw only the new edge, so they must be told when something else has written the screen buffer. Anything you draw through the display object does this for you. If your program writes the screen buffer directly, call `hub75Bffrs.noteAllDrawn(chainIndex)` afterwards (or `hub75Bffrs.noteDrawn(chainIndex, topRow, leftColumn, bottomRow, rightColumn)` for one rectangle) so the scrolling regions draw again in full.
- **`CLK_WIDE_PULSE`** is removed from the manual chip flags (it had no effect). A `CHIP_MANUAL_SPEC` config that ORs it on does not compile until you take it out.
- **`demo_hub75_hwGeometry.spin2`**, the commented-out example of the v3.x settings, is gone. The [Configuration Guide](DOCs/WiringGuide.md) replaces it.

## What else is new

- **The cube.** Six square panels laid out as one of the 11 cube nets, with `CUBE_TOP` on one sentence and `CUBE_FRONT` on another, form a cube display with face-centric drawing calls that carry across every edge. See [the cube](DOCs/WiringGuide.md#the-cube).
- **Driver limits.** How many panels one adapter can drive depends on the panel type: see [driver limits](DOCs/WiringGuide.md#driver-limits). The driver prints a message if your display is over the limit.
- **Default color depth is 8-bit.** A configuration that fit in hub RAM before may not fit now; the compiler reports it. Lower `DISPx_COLOR_DEPTH` or reduce the panel count.
- **Panel width must be a multiple of 4.** `DISPx_PANEL_COLUMNS` of 32, 64, 80 or 128 is fine; startup stops with a message otherwise.
- **Refresh target.** The new, optional `DISPx_TARGET_REFRESH_HZ` (default 60, switched on with `#DEFINE DISPx_REFRESH_GIVEN`) is the refresh rate you want; the driver picks the brightest timing that reaches it. See [refresh rate](DOCs/WiringGuide.md#refresh-rate).
- **Brightness is lit time.** `setBrightness()` now sets how long each bit plane is lit, so the image keeps its full color depth at any brightness.
- **Showing a frame set.** `display.showFrameSet()` shows a frame set you built yourself and returns `display.SUCCESS`, or an error code saying why it refused.
- **Image calls report what happened.** `bmp.fillScreenFromBMP()` and the new `bmp.placeBMP()` return `bmp.SUCCESS`, or `bmp.E_BAD_ROTATION` / `bmp.E_BMP_NOT_24BIT` when nothing was drawn. A v3.x call that ignores the result still compiles unchanged.
- **Spare displays have their own pins.** The templates for the second and third displays in a fresh `isp_hub75_hwPanelConfig.spin2` use pins P32-P47 and P0-P15, so enabling one never collides with `DISP0_` on P16-P31.

That's it. If you have converted your settings, replaced your startup calls and confirmed the panels with the identify screen, you are good to go.

I hope you continue to enjoy using this driver. As always please feel free to report issues or discuss how you are using the driver in our Matrix driver thread [P2 Driver for HUB75 LED Matrix Panels](https://forums.parallax.com/discussion/172288/p2-driver-for-HUB75-led-matrix-panels#latest). You can also file BUG reports or feature requests at the driver repository [Issues Page](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/issues).

*See you in the Parallax Forums and on our P2 Live Forums!*

*-Stephen*

----

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

----

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
