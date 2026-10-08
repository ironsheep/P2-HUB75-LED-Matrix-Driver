# CHECKLIST:</BR>Convert your code from v3.x to v4.x

![Project Maintenance][maintenance-shield]

## Introduction

**In the v3.x driver** you described the layout of your panels with a handful of numbers (how many panels per row and per column, where the cable enters the grid, how it traverses it, and a rotation for each panel), you uncommented code in two more files to add a second or third adapter, and you started the driver with a sequence of calls that handed it buffer pointers.

**In the v4.x driver** you describe each panel with **one short sentence**, and you start each adapter with **one call**. The driver works out the rest (how many panels, the size of the display, the grid, where each panel sits and how it is turned), checks your sentences, and tells you exactly which sentence is wrong if one is.

This is a **breaking** change: a v3.x `isp_hub75_hwPanelConfig.spin2` and a v3.x top-level file do not compile against v4.x. Converting takes minutes. There are three jobs:

1. [Convert your panel layout settings to wiring sentences](#convert-your-panel-layout-settings)
2. [Leave the other two configuration files alone](#the-other-two-configuration-files)
3. [Change how your program starts the driver](#change-how-your-program-starts-the-driver)

Then [check your work with the identify screen](#check-your-work-with-the-identify-screen), and look at [two things that now mean something different](#two-things-that-now-mean-something-different) (rotation, and panel numbers).

All the terms used here (adapter, display, cable position, panel position, and so on) are defined once in the [glossary](THEOPS.md#glossary). The full grammar of the sentences, with seven worked examples, is in the [Wiring Guide](DOCs/WiringGuide.md); this checklist only shows you how to convert.

## Convert your panel layout settings

In **isp\_hub75_hwPanelConfig.spin2**, each adapter has a group of settings, `DISP0_`, `DISP1_` and `DISP2_`. The chip, address lines, pin group, panel size and color depth settings keep their names and meaning, but check two things: the default color depth is now 8-bit, and the panel width must be a multiple of 4 (see [What else is new](#what-else-is-new)). These v3.x settings are removed, and the table shows what replaces each:

| v3.x setting (old) | v4.x (new) |
|---|---|
| `DISPx_MAX_PANELS_PER_ROW`, `DISPx_MAX_PANELS_PER_COLUMN` | Removed. The grid is worked out from the sentences |
| `DISPx_MAX_DISPLAY_COLUMNS`, `DISPx_MAX_DISPLAY_ROWS` (if you used them) | Removed. The display size is worked out from the sentences |
| `DISPx_WIRE_ENTRY`, `DISPx_WIRE_TRAVERSE` | The direction and neighbour words of each sentence, `DISPx_C0` ... `DISPx_C15` |
| `DISP0_PANEL0_ROT` ... `DISP0_PANEL3_ROT` (per-panel rotation) | The arrow word of each sentence (`ARROW_UP`, `ARROW_DOWN`, `ARROW_LEFT`, `ARROW_RIGHT`) |
| `DISPx_ROTATION` | Kept, but it now means how the whole display is **mounted** (see [below](#two-things-that-now-mean-something-different)) |
| *(not in v3.x)* | `DISPx_SHAPE`, and for a cube `DISPx_CUBE_TOP` and `DISPx_CUBE_FRONT` |

### Write one sentence per panel

Look at the **front** of your display and number the panels along the ribbon cable from the adapter: the panel the adapter plugs into is `C0`, the next along the cable is `C1`, and so on. Then write a sentence for each:

- `C0` is `hwEnum.FIRST_PANEL | hwEnum.ARROW_UP`
- every other panel is `direction | neighbour | arrow`, for example `hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP` ("sits to the right of `C0`")
- every cable position you do not use is `hwEnum.NO_PANEL`; there are sixteen sentences in all, `DISPx_C0` through `DISPx_C15`

Join the words with `|`, never `+`. Write every arrow `ARROW_UP` to begin with; you will correct them with the identify screen.

### Converting your wire entry and traversal

If your panels were in **one row** (or one column), each panel sits next to the one before it: every sentence is `RIGHT_OF` the previous cable position (or `BELOW` it, for a column).

For a **grid**, find your old settings in the table. It shows a 2 x 2 grid; for any other grid, each panel's sentence follows the same pattern relative to the panel before it along the cable.

| Old entry, old traversal | `C0` | `C1` | `C2` | `C3` |
|---|---|---|---|---|
| top-left, rows first | `FIRST_PANEL` (top-left) | `RIGHT_OF C0` | `BELOW C0` | `RIGHT_OF C2` |
| top-left, columns first | `FIRST_PANEL` (top-left) | `BELOW C0` | `RIGHT_OF C0` | `BELOW C2` |
| top-left, serpentine rows | `FIRST_PANEL` (top-left) | `RIGHT_OF C0` | `BELOW C1` | `LEFT_OF C2` |
| top-left, serpentine columns | `FIRST_PANEL` (top-left) | `BELOW C0` | `RIGHT_OF C1` | `ABOVE C2` |
| bottom-left, rows first | `FIRST_PANEL` (bottom-left) | `RIGHT_OF C0` | `ABOVE C0` | `RIGHT_OF C2` |
| bottom-left, serpentine rows | `FIRST_PANEL` (bottom-left) | `RIGHT_OF C0` | `ABOVE C1` | `LEFT_OF C2` |

For the other corners, mirror the table: where the cable enters at the right, swap `LEFT_OF` and `RIGHT_OF`; where it enters at the bottom, swap `ABOVE` and `BELOW`. The cells hold the direction and neighbour words; add an arrow to each, and write the `hwEnum.` prefix and the `|` joins. For example, the old bottom-left, rows first setting is the Z-order 2 x 2 of the Wiring Guide's [example 3](DOCs/WiringGuide.md#example-3-2x2-in-z-order-from-bottom-left-the-rig).

If your panels left gaps in the grid (an L shape, say), you can now say so directly: the gap is simply a cell no sentence names. See the Wiring Guide's [example 6](DOCs/WiringGuide.md#example-6-an-l-shape).

### Converting your per-panel rotation

| Old value | New arrow word |
|---|---|
| `ROT_NONE` | `ARROW_UP` |
| `ROT_180` | `ARROW_DOWN` |
| `ROT_LEFT_90`, `ROT_RIGHT_90` | `ARROW_LEFT` or `ARROW_RIGHT`. Do not guess: write `ARROW_UP`, run [identify](#check-your-work-with-the-identify-screen) and write the arrow word for the way the arrow on the panel actually points |

On panels that are not square, every arrow must be `ARROW_UP` or `ARROW_DOWN`, or every arrow must be `ARROW_LEFT` or `ARROW_RIGHT`; the driver tells you if they are mixed.

### What it looks like

A two-panel v3.x display, stacked, one above the other (old settings first):

```python
    ' v3.x (old)
    DISP0_MAX_PANELS_PER_ROW = 1
    DISP0_MAX_PANELS_PER_COLUMN = 2
    DISP0_WIRE_ENTRY = hwEnum.WIRE_ENTERS_TOP_LEFT
    DISP0_WIRE_TRAVERSE = hwEnum.WIRE_ROWS_FIRST
    DISP0_ROTATION = hwEnum.ROT_NONE
```

becomes, in v4.x:

```python
    ' v4.x (new): the adapter plugs into the top panel, the ribbon runs down to the next
    DISP0_ROTATION = hwEnum.ROT_NONE
    DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
    DISP0_C1 = hwEnum.BELOW | hwEnum.C0 | hwEnum.ARROW_UP
    DISP0_C2 = hwEnum.NO_PANEL
    ' ... DISP0_C3 through DISP0_C15 are each hwEnum.NO_PANEL, one line each
    DISP0_SHAPE = hwEnum.SHAPE_FLAT
```

Set `DISP1_` and `DISP2_` the same way: an adapter you are not using has `DISPx_C0` through `DISPx_C15` all `hwEnum.NO_PANEL` and costs no memory.

## The other two configuration files

In v3.x you edited **isp\_hub75_hwBufferAccess.spin2** and **isp\_hub75_hwBuffers.spin2** to add a second or third adapter (commenting code in and out, in about nine places). **In v4.x you do not touch them.** All three adapters are always present in both files, and each is sized from the panels you describe in `isp_hub75_hwPanelConfig.spin2`.

If you edited either file for v3.x, take the v4.x copies from the release and discard your edits. They contain nothing of yours.

## Change how your program starts the driver

The v3.x startup took a handful of calls, handed the driver buffer pointers, and named the large-buffer object in your top-level file:

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display     :   "isp_hub75_display"
    user        :   "isp_hub75_hwPanelConfig"
    scrnBuffers :   "isp_hub75_hwBuffers"               ' v3.x only

PUB main() | chainIndex, cog
    ' v3.x (old)
    hub75Bffrs.configure(hub75Bffrs.HUB75_ADAPTER_1, user.DISP0_ADAPTER_BASE_PIN, user.DISP0_PANEL_DRIVER_CHIP, user.DISP0_PANEL_ADDR_LINES)
    hub75Bffrs.setWireConfig(hub75Bffrs.HUB75_ADAPTER_1, user.DISP0_WIRE_ENTRY, user.DISP0_WIRE_TRAVERSE)
    chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)
    display.setBufferPointers(chainIndex, scrnBuffers.chain0Ptrs())
    cog := display.start(chainIndex)
```

In v4.x it is one call, and your top-level file no longer names the buffers object or reads the settings itself:

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display     :   "isp_hub75_display"

PUB main() | chainIndex
    ' v4.x (new)
    chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)   ' only if you call hub75Bffrs.* methods
    display.start(hub75Bffrs.HUB75_ADAPTER_1)
```

`display.start()` reads the adapter's settings, checks your wiring sentences, derives the layout, hands the adapter its buffers and starts the driver. If a sentence is wrong, or no cog is free for the driver, it prints a `HUB75:` message and stops the program; every wiring message is listed in the Wiring Guide's [startup messages](DOCs/WiringGuide.md#startup-messages). It returns only when the driver started (the returned value is the driver's cog ID plus one, never 0 or -1), so a v3.x check of its result for failure can be taken out. The calls `configure`, `setWireConfig` and `setBufferPointers` are gone, and your program no longer calls the buffers object's pointer methods (the start call fetches the pointers by adapter).

**Adapter *k* drives display `DISP(k-1)_`**: `HUB75_ADAPTER_1` starts the display configured by `DISP0_`, `HUB75_ADAPTER_2` starts `DISP1_`, and `HUB75_ADAPTER_3` starts `DISP2_`.

## Starting a second or third adapter

Describe the second adapter's panels in the `DISP1_` group (the third's in `DISP2_`), then give each adapter its own display object and start it with its adapter ID. Nothing else changes: there is no file to edit for the buffers.

```python
OBJ
    hub75Bffrs  :   "isp_hub75_hwBufferAccess"
    display[2]  :   "isp_hub75_display"                 ' a display object for each adapter

CON
    FRONT_PANEL = 0                                     ' which display object drives which adapter
    BACK_PANEL = 1

PUB main()
    display[FRONT_PANEL].startWithId(FRONT_PANEL, hub75Bffrs.HUB75_ADAPTER_1)
    display[BACK_PANEL].startWithId(BACK_PANEL, hub75Bffrs.HUB75_ADAPTER_2)

    ' with more than one adapter, all your calls are display[FRONT_PANEL].method() or
    ' display[BACK_PANEL].method(), and each display commits its own screen to its own panels
```

`startWithId` is `start` plus an identifier that labels each adapter's debug messages. An adapter whose `DISPx_C0` is `hwEnum.NO_PANEL` cannot be started; the driver says so and stops.

## Check your work with the identify screen

Build and run **demo\_hub75\_numberPanels.spin2**, the identify screen, with every arrow written `ARROW_UP`. It labels each panel with its cable position (`C`*k*), its place in the display (`P`*p*, in reading order) and an arrow. Reading it, and fixing a sentence from what it shows, is explained step by step in the Wiring Guide's [identify section](DOCs/WiringGuide.md#filling-in-your-config-from-the-identify-screen). In short:

- `P` labels in reading order and every arrow up: your sentences are right.
- `P` labels out of order: a direction or neighbour word is wrong. The `C` labels are always where the panels really are, so use them to fix the sentence.
- An arrow pointing another way, or upside-down text: that panel's arrow word is wrong; write the one that matches the way the arrow points.

## Two things that now mean something different

### Display rotation is physical

`DISPx_ROTATION` is how the whole assembled display is **mounted**: `ROT_RIGHT_90` means the display hangs turned 90 degrees clockwise. The driver draws so that your content reads upright once it is mounted, so on a flat bench rig `ROT_RIGHT_90` looks turned to the left. At 90 and 270 degrees the display size the driver reports is the size as mounted (width and height swap, and so do the text grid's columns and lines), and it now works on displays of any shape, not only square ones. If you used a 90 degree rotation in v3.x, set `ROT_NONE`, check the panels with identify, and then set the rotation that matches how you hung the display.

To turn an **image**, use the content rotation parameter of the new image call, `bmp.placeBMP(chain, file, rotation)`; it works for an image of any size. It is not a display setting.

### Panel numbers are panel positions

Calls that name a panel (`fillPanel`, `setCursorOnPanel`, `drawPanelBox`, `drawPanelLine`, `scrollColoredTextOnLnOfNPanels` and their siblings) take a **panel position**: `P0` is the top-left panel as the display hangs, and the numbers run in reading order. In v3.x the number was the panel's place in the buffer, which for a display wired from the bottom is not the order you see: on the author's 2 x 2 rig the top-right panel was panel 0. Check any panel number your program uses against the identify screen. Panel-centric calls also now **clip** at the panel's edge instead of spilling onto a neighbour.

## If your program calls the buffers object or the manual chip flags directly

Programs that draw only through the display object need nothing here.

- **Removed from `isp_hub75_hwBufferAccess.spin2`:** `wireStart()`, `wireTraverse()`, `wireOrderForPanel()`, `displayPanelForWire()`, `needsPanelColumnSwap()`, `panelRotationAt()`, `displayToPanelCoords()`, `panelPixelOffset()` and `indexToPanel()`. `panelRotation()` is now `displayRotation()`. Where you need a panel's place, ask the layout: `positionAtDisplayPixel()`, `positionForCable()`, `offsetToPanel()`, `layoutAreaOfPanel()`.
- **Writing the screen buffer yourself.** Scrolling regions move the frame they drew last and draw only the new edge, so they must be told when something else has written the screen buffer. Anything you draw through the display object does this for you. If your program writes the screen buffer directly, call `hub75Bffrs.noteAllDrawn(chainIndex)` afterwards (or `hub75Bffrs.noteDrawn(chainIndex, topRow, leftColumn, bottomRow, rightColumn)` for one rectangle) so the scrolling regions draw again in full.
- **`CLK_WIDE_PULSE`** is removed from the manual chip flags (it had no effect). A `CHIP_MANUAL_SPEC` config that ORs it on does not compile until you take it out.
- **`demo_hub75_hwGeometry.spin2`**, the commented-out example of the v3.x settings, is gone. The [Wiring Guide](DOCs/WiringGuide.md) replaces it.

## What else is new

- **The cube.** Six square panels wired as one of the 11 cube nets, with `DISPx_SHAPE = hwEnum.SHAPE_CUBE`, form a cube display with face-centric drawing calls that carry across every edge. See [the cube](DOCs/WiringGuide.md#the-cube).
- **Driver limits.** How many panels one adapter can drive depends on the panel type: see [driver limits](DOCs/WiringGuide.md#driver-limits). The driver prints a message if your display is over the limit.
- **Default color depth is 8-bit.** A configuration that fit in hub RAM before may not fit now; the compiler reports it. Lower `DISPx_COLOR_DEPTH` or reduce the panel count.
- **Panel width must be a multiple of 4.** `DISPx_MAX_PANEL_COLUMNS` of 32, 64, 80 or 128 is fine; startup stops with a message otherwise.
- **Refresh target.** The new `DISPx_TARGET_REFRESH_HZ` (default 60) is the refresh rate you want; the driver picks the brightest timing that reaches it. See [refresh rate](DOCs/WiringGuide.md#refresh-rate).
- **Brightness is lit time.** `setBrightness()` now sets how long each bit plane is lit, so the image keeps its full color depth at any brightness.
- **Showing a frame set.** `display.showFrameSet()` shows a frame set you built yourself.

That's it. If you have converted your settings, replaced your startup calls and confirmed the panels with the identify screen, you are good to go.

I hope you continue to enjoy using this driver. As always please feel free to report issues or discuss how you are using the driver in our Matrix driver thread [P2 Driver for HUB75 LED Matrix Panels](https://forums.parallax.com/discussion/172288/p2-driver-for-HUB75-led-matrix-panels#latest). You can also file BUG reports or feature requests at the driver repository [Issues Page](https://github.com/ironsheep/p2-LED-Matrix-Driver/issues).

*See you in the Parallax Forums and on our P2 Live Forums!*

*-Stephen*

----

## License

Licensed under the MIT License. 

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge
