# Wiring Guide

How to tell the driver which panels you have, where each one sits and which way each one's top points: the per-display settings, the panel list, the identify screen that lets you fill the list in from the wall, the mounting override, the cube, the limits of the driver, every message the driver prints when a configuration is wrong, and seven worked examples.

Pages: [README](../README.md) | [Driver Details (THEOPS)](../THEOPS.md) | [Multi-Panel Configuration](MultiPanelConfiguration.md)

Within this page:

- [Words used here](#words-used-here)
- [The configuration at a glance](#the-configuration-at-a-glance) - what you write, and the order to write it in
- [The display block](#the-display-block) - pins, chip, panel size, colour depth, derived address lines
- [The wiring sentences](#the-wiring-sentences) - the panel list: the words, the rules
- [Filling in your config from the identify screen](#filling-in-your-config-from-the-identify-screen) - the identify-first workflow
- [More displays and optional settings](#more-displays-and-optional-settings) - presence and override flags, the template blocks, the compile-error table
- [Display rotation](#display-rotation) - the mounting override, and how to turn an image
- [The cube](#the-cube) - six panels as one object
- [Driver limits](#driver-limits) - how many panels per adapter, by panel type
- [Startup messages](#startup-messages) - what the driver prints, every mistake it catches
- [Seven worked examples](#seven-worked-examples)

## Words used here

This page uses the terms defined in the [glossary](../THEOPS.md#glossary): **adapter**, **display**, **display coordinates**, **panel position** (`P0`, `P1`, ... in reading order), **cable position** (`C0` is the panel the adapter plugs into) and **face**. Three more are used the way this page defines them:

- the **panel list** is the list of panels of one display, in cable order, one `LONG` per panel;
- a **panel sentence** is one entry of that list: the words that say where the panel sits and which way its own top points;
- a panel's **top** is the edge that is up when the panel is hung the way the manufacturer drew it. The identify screen draws an arrow (`^`) near that edge.

The short version: a **cable position** names a piece of hardware and never changes (it is the panel's place in the list); a **panel position** names a place on the display as the viewer sees it. The panel list is what connects the two.

## The configuration at a glance

All configuration lives in one file, `isp_hub75_hwPanelConfig.spin2`, between the lines `USER SECTION` and `END USER SECTION`. For each HUB75 adapter you use, it holds one display:

1. **The display block**: the adapter's pin group, the panel driver chip, one panel's columns and rows, and the colour depth. Said once for the display.
2. **The panel list**: one `LONG` sentence per panel, in cable order. Each sentence says the panel's row, its column and the way its top points, all as you see them from the front of the display.

The first adapter drives `DISP0`, the second `DISP1`, the third `DISP2`. A display you do not have is not written at all; the file ships with `DISP0` filled in and a ready template for a second display (see [More displays and optional settings](#more-displays-and-optional-settings)).

The shipped `DISP0` is four ICN2037 128x64 panels in a 2 x 2 block, hung upside down ([example 3](#example-3-2x2-in-z-order-from-bottom-left-the-rig)):

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 128
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_DOWN
disp0PanelsEnd
```

You do not need to work out the panel list by hand. Cable and hang the panels as you like, write a starter list, and let the identify screen show you what to write ([the workflow](#filling-in-your-config-from-the-identify-screen)).

Your program starts each adapter with one call, `display.start(hub75Bffrs.HUB75_ADAPTER_n)`; adapter `n` drives display `DISP(n-1)`.

## The display block

Every setting name starts with the display's prefix: `DISP0_`, `DISP1_` or `DISP2_`. The block says, once for the display:

| Setting (after the prefix) | Value |
|---|---|
| `ADAPTER_BASE_PIN` | the adapter's 16-pin group: `hwEnum.PIN_GROUP_P0_P15`, `PIN_GROUP_P16_P31` or `PIN_GROUP_P32_P47` |
| `PANEL_DRIVER_CHIP` | a canned chip name, or `hwEnum.CHIP_MANUAL_SPEC` joined with flags (below) |
| `PANEL_COLUMNS`, `PANEL_ROWS` | the pixel columns and rows of **one** panel |
| `COLOR_DEPTH` | `hwEnum.DEPTH_3BIT` to `hwEnum.DEPTH_8BIT`, bits per colour channel |

Then the panel list: a `DAT` section with the label `disp0Panels` (`disp1Panels`, `disp2Panels`) before the first sentence and `disp0PanelsEnd` after the last. The number of panels is the length of the list; there is no separate count to keep in step.

**The chip.** Use the canned name for your panels: `CHIP_FM6126A`, `CHIP_FM6124`, `CHIP_ICN2037`, `CHIP_ICN2038S`, `CHIP_MBI5124GP`, `CHIP_GS6238S` or `CHIP_DP5125D`. For panels with a chip that is not listed, join `CHIP_MANUAL_SPEC` with the flags that describe it, using `|`:

```
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_MANUAL_SPEC | hwEnum.LAT_STYLE_OFFSET | hwEnum.SCAN_4
```

The flags are `LAT_STYLE_OFFSET`, `LAT_POSN_OVERLAP`, `INIT_PANEL_REQUIRED`, `RB_SWAP`, `SCAN_4` and `GB_SWAP`. The [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md) gives what each canned name stands for.

**The address lines are derived.** You never say how many row-address lines a panel has. At startup the driver computes `log2(panel rows / rows lit per address)`, where the rows lit per address are 4 for a chip with the `SCAN_4` flag (ICN2038S, MBI5124GP, DP5125D) and 2 for every other chip. The result must be 8, 16 or 32 row addresses (3, 4 or 5 lines); anything else is reported ([M4](#startup-messages)). A 64x32 FM6126A panel (32 / 2 = 16 addresses) gets 4 lines; a 128x64 ICN2037 (64 / 2 = 32) gets 5; a 64x32 MBI5124GP (32 / 4 = 8) gets 3. The scan of the ICN2038S road-sign panel is being settled at the bench; until that is recorded here, treat the address lines the driver derives for that panel as provisional.

**The depth** sets the hub RAM each pixel costs: 3 bytes of screen buffer plus one byte per bit of depth (11 bytes per pixel at 8 bits). Lower the depth only when the display does not fit ([Hub RAM](#hub-ram)).

## The wiring sentences

The panel list holds one sentence per panel, in cable order: the first sentence is the panel the adapter plugs into (`C0`), the second is the panel its ribbon goes to (`C1`), and so on. A sentence is a few words joined with `|`:

```
LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_DOWN
```

Read it aloud: "this panel is in row 1, column 0, and its top points down." Row 0 is the top row of panels and column 0 the left column, **as you see them from the front of the display**.

### The words

Each word is written with the `hwEnum.` prefix.

| Word | Meaning |
|---|---|
| `ROW_0` ... `ROW_62` | the panel's row of panels, row 0 at the top |
| `COL_0` ... `COL_62` | the panel's column of panels, column 0 at the left |
| `TOP_UP` | the panel's own top points up |
| `TOP_DOWN` | the panel's own top points down: the panel is hung upside down |
| `TOP_LEFT` | the panel's own top points left |
| `TOP_RIGHT` | the panel's own top points right |
| `CUBE_TOP` | this panel is the top face of a cube (see [the cube](#the-cube)) |
| `CUBE_FRONT` | this panel is the front face of a cube |

The `TOP_` word is the way the arrow that the identify screen draws on this panel points, read from the front. Rows and columns are numbered from the top-left; the smallest row and the smallest column you use are taken as the display's top row and left column, so a list that starts at `ROW_3` hangs the same as one that starts at `ROW_0`.

### Rules

1. **Join the words with `|` only, never `+`, and in any order.** `ROW_1 | COL_0 | TOP_DOWN` and `TOP_DOWN | COL_0 | ROW_1` mean the same thing.
2. **One of each kind.** A sentence has one `ROW_` word, one `COL_` word and one `TOP_` word. The cube marks are optional. A missing `ROW_` or `COL_` word, and a missing or doubled `TOP_` word, are reported ([M8, M9, M10](#startup-messages)).
3. **No two panels share a cell.**
4. **The panels form one piece.** Every panel shares a full edge with the rest. T, L, Z, S and plus shapes are allowed; two panels that touch only at a corner, and gaps between panels, are not ([M12](#startup-messages)). Empty cells inside the bounding box of an L or a T are fine.
5. **Non-square panels are all upright or all sideways.** On panels that are not square, every `TOP_` word is `TOP_UP` or `TOP_DOWN`, or every one is `TOP_LEFT` or `TOP_RIGHT`; a panel turned sideways fills a cell of a different shape, so the two cannot be mixed in one grid ([M13](#startup-messages)). Square panels may point any way, in any mix.

### The doubled row or column that cannot be detected

A row is one number stored in a field, not a set of separate bits. Writing two `ROW_` words with `|` sets the bits of both and gives a different row: `ROW_0 | ROW_1` is `ROW_2`, and `ROW_1 + ROW_1` is `ROW_3`. The driver cannot tell that from a panel that really is in that row. The same holds for two `COL_` words. The usual result is two panels in one cell or a panel that no longer touches the others, and those are caught ([M11, M12](#startup-messages), and the second mistake of [example 2](#example-2-two-panels)); a doubled word that happens to land on an empty cell is not.

### Why `|` and never `+`

The `TOP_` words and the cube marks are single bits. Joining with `|` sets each bit without disturbing the others. Adding with `+` lets a repeated word carry into the next bit: `TOP_UP + TOP_UP` silently becomes `TOP_DOWN`, and the panel quietly points the wrong way. The driver catches what it can (a mounting word or a stray bit in a sentence, [M7](#startup-messages); a doubled or missing `TOP_` word, [M10](#startup-messages)), but the surest protection is to write `|` every time.

### What a good config prints

When the display block and the panel list are right, the driver prints the layout it derived at startup, before it starts the panels. This is the shape of those lines (letters stand for numbers the driver prints):

```
HUB75: DISPn panels: N panels in a grid of R rows x C columns, W x H pixels (columns x rows)
HUB75: DISPn   [Ck a][Ck a] ...           one line per grid row
HUB75: DISPn Pp = Ck, buffer slot s, cell row r column c, rotation d
HUB75: DISPn cable -> panel position:
HUB75: DISPn  C0->Pp C1->Pp ...
```

- The header gives the number of panels, the grid in panels, and the size of the display in pixels.
- The grid lines show a cell as `[Ck a]`, where `k` is the cable position and `a` is the way the panel's top points (`^`, `v`, `<` or `>`). A cell that holds no panel prints as `  --`. When the display has more than ten panels, single-digit cells are padded (`[C2  v]`) so the columns line up. A line wraps at 96 characters.
- There is one `Pp = Ck` line per panel position, in reading order. `rotation d` is how many degrees (0, 90, 180 or 270) the driver turns that panel's content so it reads upright.
- The last line is the one to keep in mind: it says which panel position each cable position ended up at. The grid lines show the panels as built; the `P` lines are as mounted (they differ only when a [mounting override](#display-rotation) is set).

Each worked example below has a slot for its picture.

## Filling in your config from the identify screen

The identify program, `demo_hub75_numberPanels.spin2`, draws on every panel:

- an arrow (`^`) near the top, pointing the way the panel's own top points as it hangs;
- `C`*k*, the cable position of that panel (its place in the list);
- `P`*p*, the panel position of that panel.

Each panel also gets its own background colour, which makes the panels easy to tell apart. Small panels (for example 64x32 with the 5x7 font) get a compact layout: the `^` and then `C2P1` on one line.

Because the `C` labels are drawn through the driver's inverse table, they are **physically correct even when your panel list is wrong**. A panel labelled `C2` is the panel at cable position 2, the third sentence. The labels tell you the truth; the sentences are what you are checking.

### The procedure

1. **Cable and mount the panels as you like.** Nothing about the order of the ribbon or the way a panel hangs needs to be planned. **Mark the top edge of the frame** (the edge that is up now); you need it if you ever hang the display another way ([Display rotation](#display-rotation)).
2. **Write the display block** for your pins, chip, panel size and colour depth ([the display block](#the-display-block)).
3. **Write a starter sentence for every panel**, in cable order, with every panel in one row and its top up: `ROW_0 | COL_0 | TOP_UP`, `ROW_0 | COL_1 | TOP_UP`, `ROW_0 | COL_2 | TOP_UP`, and so on. A starter list passes every startup check except the [panel limit](#driver-limits).
4. **Build and run identify.** The startup picture appears first; if the driver names a mistake, fix that sentence and run again ([the catalogue](#startup-messages)).
5. **Copy each panel from the wall into its sentence, reading from the front.** Panel `Ck` is the `k`-th sentence (counting from 0). For each panel write the row it is in (from the top), the column it is in (from the left) and the direction its arrow points: `TOP_UP`, `TOP_DOWN`, `TOP_LEFT` or `TOP_RIGHT`.
6. **Run it again.** When the `P` labels read in order and every arrow points up, the panel list is right. If not:
   - **`P` labels out of order, `C` labels where you expect them:** a `ROW_` or `COL_` word places a panel wrongly. The `C` labels show where each cable position really is; use them to correct the sentences.
   - **An arrow pointing another way, or text upside down:** that panel's `TOP_` word is wrong. Write the word for the direction the arrow actually points on that panel, and run again.

A wrong `TOP_` word turns a panel's content and never moves it; a wrong `ROW_` or `COL_` word moves the `P` labels and leaves the content upright.

When the identify screen is up, the driver prints `END_SESSION` and holds the image.

For a cube, do the same, then mark the top and front faces ([the cube](#the-cube)).

## More displays and optional settings

Only the displays you have are described. A second or third display, and each optional setting, is switched on with one `#DEFINE` line placed next to it. The first display needs no flag. A typical configuration writes none.

| To add | Write |
|---|---|
| a second display | `#DEFINE DISP1_PRESENT`, then the `DISP1_` block and the `disp1Panels` list |
| a third display | `#DEFINE DISP2_PRESENT`, then the `DISP2_` block and the `disp2Panels` list |
| a mounting override for display *n* | `#DEFINE DISPn_ROTATED`, then `DISPn_ROTATION = hwEnum.TOP_TO_RIGHT` (or `TOP_TO_BOTTOM`, `TOP_TO_LEFT`) |
| a refresh target for display *n* | `#DEFINE DISPn_REFRESH_GIVEN`, then `DISPn_TARGET_REFRESH_HZ = <Hz>` (default 60) |

Every display not flagged present gets an empty panel list: it has no panels and its buffers cost no memory. Adapter 3 runs without adapter 2.

The template for a second display, as it ships in the file (remove the leading `'` from each line to use it, then edit it):

```
#DEFINE DISP1_PRESENT
CON
    DISP1_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P32_P47
    DISP1_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP1_PANEL_COLUMNS     = 64
    DISP1_PANEL_ROWS        = 32
    DISP1_COLOR_DEPTH       = hwEnum.DEPTH_8BIT
DAT
disp1Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
disp1PanelsEnd
```

A third display is the same block with `DISP2_`, `disp2Panels`, `disp2PanelsEnd` and `PIN_GROUP_P0_P15`.

The optional settings, as they ship (remove the leading `'` from both lines of the one you want):

```
#DEFINE DISP0_ROTATED
CON DISP0_ROTATION = hwEnum.TOP_TO_RIGHT
#DEFINE DISP0_REFRESH_GIVEN
CON DISP0_TARGET_REFRESH_HZ = 30
```

### When a `#DEFINE` and its setting do not match

The flag and the setting go together. The compiler reports a mismatch (measured with pnut-ts 1.55.8):

| You wrote | The compiler says | Where |
|---|---|---|
| the setting, without its `#DEFINE` | `Symbol is already defined (m541)` | at the setting's default, in the Defaults section below the user section |
| the `#DEFINE`, without its setting | `Expected an object constant, structure, or method` | reported in `isp_hub75_hwBufferAccess.spin2` |
| `#DEFINE DISP1_PRESENT`, without a `DISP1_` block | `Undefined symbol` | in the storage section below the defaults |

Everything below the user section is not edited.

## Display rotation

Two things can be turned, and they are different:

| What | How you set it | Meaning |
|---|---|---|
| each panel | the `TOP_` word in its sentence | which way that one panel's top points within the display |
| the whole display | the mounting override, `DISPn_ROTATION` | how the assembled display is hung now, compared with how it was built and identified |

**The mounting override is a convenience for re-hanging a built display.** The panel list describes the display as it was first built and identified, with the top edge of the frame at the top. If you later hang that display another way, you do not rewrite the list: you say where the frame's top edge now points, and the driver turns the content so it reads upright to the person looking at the display. The default needs no flag and no line:

| Word | The frame's built top edge is now at |
|---|---|
| `AS_BUILT` | where it was built: the display hangs as the list describes (the default) |
| `TOP_TO_RIGHT` | the right: the display is turned 90 degrees clockwise |
| `TOP_TO_BOTTOM` | the bottom: the display is turned 180 degrees |
| `TOP_TO_LEFT` | the left: the display is turned 90 degrees counter-clockwise |

It is set with its flag ([More displays and optional settings](#more-displays-and-optional-settings)):

```
#DEFINE DISP0_ROTATED
CON DISP0_ROTATION = hwEnum.TOP_TO_BOTTOM
```

This is why step 1 of the [procedure](#the-procedure) asks you to mark the frame's top edge: identify, then re-hang, then run identify again as the check. A value that is not one of the four words is reported ([M3](#startup-messages)). The override applies to flat displays only; on a cube it is ignored with a notice ([N1](#startup-messages)).

With the display hung at 90 or 270 degrees, the display size the driver reports is the size **as mounted**: width and height swap, and so do the text grid's columns and lines.

### Everything is in the viewer's frame

Your program never sees cables, tops or the way the display was mounted; the panel list and the override are translated away at startup. Drawing calls use the display as the viewer sees it:

- display coordinates start at the top-left as mounted;
- `P0` is the top-left panel as the display hangs, and panel positions run in reading order as mounted;
- in a panel-centric call, row 0 is that panel's top as the viewer sees it, and anything that runs past the panel's edge is clipped, never spilled onto a neighbour.

### Turning an image: content rotation

Turning an image is separate from mounting. The image-placing call, `placeBMP`, takes a content rotation (`bmp.ROT_0`, `bmp.ROT_90` for clockwise, `bmp.ROT_180` or `bmp.ROT_270` for counter-clockwise). The image is turned about the centre of the display as it is placed; the part that falls off the display is simply not shown, and nothing is wrapped or moved. Placing again with another rotation re-places the picture from the source, so nothing is lost. Content rotation works for an image of any size, composes with mounting, and does not affect text or shapes you draw (a drawn display already follows the display's geometry). A cube has no face-aware image call: `placeBMP` places the image on the flat layout of the net, not carried across the folded edges.

## The cube

Six **square** panels, laid out as one of the 11 nets of a cube, form a cube display. You do not set a shape: you **mark two panels**. `CUBE_TOP` on one sentence says that panel is the top face, and `CUBE_FRONT` on a different sentence says that panel is the front face:

```
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_TOP
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_FRONT
```

With no marks the display is flat. With both marks it is a cube, and the display must then have exactly six square panels (messages [M14 to M16](#startup-messages)). The front face must share an edge with the top face once the net is folded. The two marks together are the **cube orientation**; they take the place of the mounting override, which is ignored on a cube. If you set the override anyway, the driver prints a notice and carries on ([N1](#startup-messages)).

The other sentences describe the panels laid flat, as a net, exactly as for any flat display, and the driver checks that they fold into a cube ([M17, M18](#startup-messages)).

### Face names

From Top and Front the driver derives the six face names: `TOP` and `FRONT` are the two you marked; `BOTTOM` is opposite the top; `BACK` is opposite the front; `LEFT` and `RIGHT` are the faces on the viewer's left and right when standing at the front.

### Up on each face

Every face is seen from outside the cube, with row 0 along the face's up edge and column 0 along its left edge. The up directions are fixed:

- on the four sides (`FRONT`, `BACK`, `LEFT`, `RIGHT`), up points toward `TOP`;
- on `TOP`, up points toward `BACK`, so that standing at `FRONT`, text on `TOP` reads correctly;
- on `BOTTOM`, up points toward `FRONT`.

These conventions do not change between releases, so anything you build on them stays valid.

### Folding

At startup the driver folds the net and works out all 12 edges, including those the flat picture does not show, and how coordinates carry across each one. The startup log prints one line per face; example 7 shows their form. In each line the four edges of the face are named `N`, `E`, `S`, `W` (as the face is seen from outside, with `N` its up edge), and each entry says which face lies beyond that edge and which of its edges meets it: `N->TOP.S` on the front face says the front's top edge meets the top face's south edge.

### Drawing on faces

Face-centric calls address a pixel as (face, row, column), and the row and column may run past the edge of the face. A pixel that does is carried across the edge onto the neighbouring face, as many edges as it crosses. Face-centric calls therefore **fold**, where panel-centric calls **clip**. Lines, boxes, circles, text and scrolling all fold across every edge.

Two rules govern corners:

- **The corner gap.** A cube corner has three faces meeting, so 270 degrees of surface around the corner, not 360. A pixel past two edges of one face at once lands in the missing quarter, where there is no surface, and it is discarded. An object whose centre falls in that gap is first moved to the nearest surface point (the axis with the smaller overshoot is snapped; on a tie the column is snapped).
- **Seam placement.** An object that straddles a corner off-centre has one unavoidable seam. The driver puts the seam on the edge farthest from the object's centre.

A shape centred on a face, on an edge or on a corner is seamless while it stays within that face, that edge's span, or the three faces of that corner. A shape centred on an edge but large enough to reach the corners at the ends of the edge meets those corners' gaps.

The fold is checked without any panels attached by `test_hub75_cube_fold.spin2`, which pushes a fixed list of face coordinates through the fold and prints PASS or FAIL for each. A cube on six real panels has not yet been run on hardware.

## Driver limits

How many panels one adapter can drive depends on the panel. The hard limit for every panel type is the **refresh line buffer**: the refresh core holds one row of the whole chain, 512 column clocks. The driver checks this at startup (message [M6](#startup-messages)). Hub RAM sets a separate limit that the compiler enforces. There is no fixed cap on the number of panels beyond these: a panel list may name rows and columns up to 62.

A display must pass all five limits, and the tightest decides:

| Limit | What sets it | Where it binds |
|---|---|---|
| Refresh line buffer | One row of the whole chain, 512 column clocks | Per adapter |
| Hub RAM | The buffers of every display present share what is left of 512 KB | Across adapters |
| Refresh rate | The chain's column clocks, row addresses and colour depth, against `DISPn_TARGET_REFRESH_HZ` ([Refresh rate](#refresh-rate)); a display that cannot reach the target runs at its fastest rate | Per adapter |
| Pins and cogs | Each adapter takes a 16-pin group and one refresh cog | Board-wide |
| Panel width | `DISPn_PANEL_COLUMNS` must be a multiple of 4 (every common panel is: 32, 64, 80, 128); startup stops with a message otherwise ([M5](#startup-messages)) | Per adapter |

**Max panels per adapter = 512 / (panel columns x scan factor).** The scan factor is 2 for chips the driver flags as quarter-scan (`SCAN_4`: ICN2038S, MBI5124GP, DP5125D) and 1 for every other chip.

| Panel type | Columns | Scan factor | 512 / (columns x factor) | **Max panels per adapter** | Status |
|---|---|---|---|---|---|
| FM6126A 64x32, 1/16 scan | 64 | 1 | 8 | **8** | calculated; one panel run on the bench |
| FM6124 64x32, 1/16 scan | 64 | 1 | 8 | **8** | calculated; one panel run on the bench |
| MBI5124GP 64x32, 1/8 scan, quarter-scan conversion | 64 | 2 | 4 | **4** | calculated; two panels run on the bench |
| GS6238S 64x32, 1/16 scan | 64 | 1 | 8 | **8** | calculated |
| ICN2037 64x64, 1/32 scan | 64 | 1 | 8 | **8** | calculated |
| ICN2037 128x64, 1/32 scan | 128 | 1 | 4 | **4** | calculated; checked with 4 panels on the bench |
| ICN2038S 64x64, quarter-scan flag | 64 | 2 | 4 | **4** | calculated; see the note below |
| DP5125D, 1/8 scan, quarter-scan conversion | W | 2 | 8 for W=32, 4 for W=64, 2 for W=128 | **by width** | calculated; no panel documented |

Notes on the table:

- The 4 x 128x64 ICN2037 rig sits exactly at the limit: 4 x 128 = 512 column clocks.
- The ICN2038S has five address lines (which fits 1/32 scan and would give a limit of 8), but the driver flags the chip as quarter-scan, so the limit it enforces is 4. The scan of the ICN2038S road-sign panel is being settled at the bench; the row and its note will be updated with the result.
- The ICN2038S panel is single-ended, so it cannot be chained. Multi-panel use of the FM6124 and GS6238S has not been proven on hardware, and the MBI5124GP has been run with two panels, so for those rows the number is the driver's cap, not a demonstrated working count.

### Hub RAM

One panel of P pixels at colour depth N takes **P x (3 + N) bytes**: the screen buffer (3 bytes per pixel) plus two PWM frame sets (N x P / 2 bytes each). The compiler builds the buffers of every display that is present into the same program, so they share what is left of the 512 KB hub RAM. A display that is not present has a zero-length panel list and costs nothing. A display too big for hub RAM does not compile.

Measured with the largest demo (`demo_hub75_7seg.spin2`) and five 128x64 panels at 8-bit (450,560 bytes of buffers): built with DEBUG (`pnut-ts -d`) it fails with `Program requirement exceeds 512KB hub RAM by 8684 bytes`, so a DEBUG build leaves **441,876 bytes** for buffers; built without DEBUG it compiles (508,492 bytes in all), leaving about 466,000 bytes. Your own program's size moves these figures, so the compiler's report for your build is the authority.

Maximum panels by RAM alone, one adapter, nothing on the others (calculated from the 441,876 bytes of a DEBUG build):

| Panel | 3-bit | 4-bit | 5-bit | 6-bit | 7-bit | 8-bit |
|---|---|---|---|---|---|---|
| 64x32 | 35 | 30 | 26 | 23 | 21 | 19 |
| 64x64 | 17 | 15 | 13 | 11 | 10 | 9 |
| 128x64 | 8 | 7 | 6 | 5 | 5 | 4 |

On one adapter, RAM never sets the limit: the line buffer's cap above is at or below it in every cell (128x64 at 8-bit: both 4). RAM binds when adapters share it, for example two adapters of 4 x 128x64 at 8-bit need 8 x 90,112 = 720,896 bytes, which does not fit.

Worked examples (128x64 panels unless stated; calculated from the 441,876 bytes of a DEBUG build, except the first, which is the author's rig):

| Configuration | Hub buffers (bytes) | Fits |
|---|---|---|
| 1 adapter x 4 panels, 8-bit | 4 x 8,192 x 11 = 360,448 | yes (runs on the rig) |
| 2 adapters x 4 panels, 8-bit | 720,896 | no |
| 2 adapters x 4 panels, 4-bit | 8 x 8,192 x 7 = 458,752 | no with DEBUG (16,876 bytes over); about 7,600 bytes to spare without |
| 2 adapters x 4 panels, 3-bit | 8 x 8,192 x 6 = 393,216 | yes |
| Cube: 1 adapter x 6 panels of 64x64, 8-bit (384 of the 512 columns) | 6 x 4,096 x 11 = 270,336 | yes |

One long chain or several shorter ones:

- **One adapter, one long chain** is one large display with one image across all its panels, up to the 512-column line buffer. Its refresh falls as the chain lengthens, and it uses one refresh cog.
- **Several adapters** drive one display each, and each refreshes its own shorter chain, so faster. The content is independent per display: one image does not span adapters. Every adapter uses one refresh cog, and the hub RAM they share must hold the sum of their buffers.

### Refresh rate

This section is the one place that states how the refresh works and what it reaches. [Driver Details](../THEOPS.md#notes-on-driver-internals) and the [Theory of Operations](TheoryOfOperations.md#51-refresh-rate) describe the method briefly and link here.

#### The method

The refresh cog shows each bit plane **once** per row address. For each row address, and for each bit plane *k* from the most significant down, it loads the plane's row from hub RAM, shifts it into the panels, latches it, and lights the row by pulsing /OE for 2^*k* x L clocks inside a slot of 2^*k* x T clocks. The next plane is loaded and shifted while the current plane is lit, and the row address changes only while /OE is off.

T is the **/OE unit**. L equals T at full brightness (see [Brightness](#brightness)). One full colour cycle is every row address shown with every plane, and the refresh rate is how often it repeats.

On the author's rig the column clock is 15 system clocks per column at 335 MHz. CLK is high for 7 of them (20.9 ns) and low for 8 (23.9 ns) at every depth. The monitors read the high half a little long, through the pin's input threshold: 23.9 ns on the four-panel rig, 21.7 to 24.2 ns on single FM6126A, MBI5124GP and FM6124 panels. The driver holds each half of the pulse to at least 20 ns and the whole period to the chip's highest clock: its rating, or in a chain its chain limit when that is lower (a chip's data output feeds the next chip's data input, so the period must also cover the output delay plus the input setup time). The limits the driver uses are 30 MHz for the FM6124 and FM6126A, 28.6 MHz for the ICN2038S, 25.0 MHz for the ICN2037, 18.9 MHz for the MBI5124GP and 20 MHz for a chip with no rating in the driver's table. At 335 MHz the shortest column loop that keeps both halves at 20 ns or more is 15 system clocks (22.3 MHz), which is what every chip but the MBI5124GP runs at; the MBI5124GP runs at 18.6 MHz. The ratings are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings).

#### The target refresh rate

`DISPn_TARGET_REFRESH_HZ` (default 60; switched on with `#DEFINE DISPn_REFRESH_GIVEN`, see [More displays and optional settings](#more-displays-and-optional-settings)) says how fast the display should refresh. At startup the driver takes S, the clocks to shift one row of one plane (the chain's column clocks x the clocks per column), and tries T = S / 2^*j* for *j* = 0, 1, 2, ... until the predicted refresh reaches the target. T never goes below the chip's shortest /OE pulse. The smallest *j* that meets the target gives the longest T, and so the brightest picture. *j* = 0 lights every plane for its whole slot.

When no *j* reaches the target, the driver runs at the fastest rate the display has (the largest *j*, the colour depth) and prints the [notice](#startup-messages). On the author's rig at 8-bit, a target of 200 Hz printed `running at 165.7 Hz, its fastest (j = 8)` and the monitors measured 165.0 Hz.

A build with DEBUG prints a `REFRESH` line at startup (S, T, *j*, the chip's shortest /OE pulse in clocks and the target) and a `MODEL` line (predicted refresh and lit share). Lower the target for more light on a large display.

#### Measured refresh

Measured on the author's rig, four ICN2037 128x64 panels (512 column clocks, 1/32 scan), at the default 60 Hz target, 335 MHz. The monitors count LATCH and /OE on the P2's own pins. The lit share is the part of the time /OE holds the panels lit, at brightness 256.

| Depth | Refresh (Hz) | Lit share | *j* chosen |
|---|---|---|---|
| 3-bit | 193.3 | 99.2% | 0 |
| 4-bit | 90.5 | 99.6% | 0 |
| 5-bit | 84.7 | 96.3% | 1 |
| 6-bit | 79.6 | 91.9% | 2 |
| 7-bit | 75.0 | 87.4% | 3 |
| 8-bit | 71.0 | 83.0% | 4 |

Each figure is within 0.2% of the rate and lit share the driver predicts at startup. The image is steady by eye at 5-bit to 8-bit on a full-screen colour demo; the author's words at each depth were *"steady"* (5-bit), *"steady"* (6-bit), *"no shimmering"* (7-bit) and *"colors all look steady"* (8-bit). A test build of the method showed visible flicker at 36.9 Hz and none at 65.9 Hz.

Single 64x32 panels, one at a time on one adapter, same target and clock. Each reaches 60 Hz with every plane lit for its whole slot (*j* = 0), so it runs at its fastest rate:

| Panel | 8-bit refresh | 8-bit lit share | 5-bit refresh | 5-bit lit share | Floor at brightness 1 |
|---|---|---|---|---|---|
| FM6126A (overlapped latch) | 85.1 Hz | 99.6% | 688.9 Hz | 97.9% | 1.4% lit (40 ns) |
| FM6124 | 85.3 Hz | 99.7% | 694.1 Hz | 98.6% | 1.1% lit (30 ns) |
| MBI5124GP (1/8 scan, 128 column clocks per row address, 18.6 MHz chain clock) | 71.2 Hz | 99.8% | 582.7 Hz | 99.4% | 0.7% lit (50 ns) |

The image was correct by eye on the test patterns on all three at both depths. The MBI5124GP's figures above are at the 18.6 MHz chain-limit clock (one chip cannot hand data to the next any faster; see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings)); its test patterns were checked by eye at a faster clock, and one panel at the 18.6 MHz clock has not been looked at. Two MBI5124GP panels chained as one 128x32 display: 70.9 Hz at 8-bit (99.4% lit), 292.1 Hz at 5-bit (99.6% lit), the identify image and the scroll demo correct by eye. Other panel types follow the same rule; their figures have not been measured.

#### Brightness

`display.setBrightness(0 to 256)` scales L, the lit time inside each plane's slot, to T x b / 256. The colour values are not touched, so the image keeps its full depth at any brightness, and the row timing, and with it the refresh rate, does not change. 256 is no reduction and 0 is off (/OE never pulses).

L never goes below the chip's shortest /OE pulse, so low settings give a floor brightness rather than less. On the four-panel ICN2037 rig at 8-bit the shortest pulse is 21 clocks (60 ns) and T is 480 clocks, so settings 1 to 11 all give the same light. Measured there:

| Brightness | 256 | 128 | 1 | 0 |
|---|---|---|---|---|
| Lit share | 83.0% | 41.5% | 3.6% | 0.0% |
| Of full | 100% | 50% | 4% | 0% |

At every depth, 128 gave half of the lit share of 256 with the refresh rate unchanged. A shorter lit time means a lower average LED current; the supply draw at reduced brightness has not been measured. For sizing a supply, the author read these full-white figures from the supply while running the method's test build: 120 W for the four-panel rig (82.2% lit), and for single 64x32 panels 17.6 W (FM6126A), 39.93 W (MBI5124GP) and 14.27 W (FM6124).

#### Commit and draw time

Measured on the same four-panel rig (256x128 pixels):

| Step | 8-bit | 5-bit |
|---|---|---|
| Commit | 4.09 ms | 3.26 ms |

Drawing calls take their pixels from the cell address tables and write them in PASM (see [Theory of Operations](TheoryOfOperations.md#22-pixel-write-operation)). Measured on the same rig at 8-bit with the rates test's workload: a full-screen flat fill 4.7 ms, fanned lines 13.0 ms, lines of text 24.6 ms and a 64x32 BMP 3.8 ms. Other calls measured there: a full screen of 5x7 text 43 ms, ten diagonal lines 9.0 ms and ten circles 7.8 ms. Draw time does not depend on the colour depth: the screen buffer holds three bytes per pixel at every depth. A commit converts the screen buffer into the PWM frame set that is not on display and posts it; the refresh cog switches to it at its next frame start, so the panels never show a half-converted image (see [Theory of Operations](TheoryOfOperations.md#23-screen-commit-operation)).

## Startup messages

When the driver starts an adapter it checks the display block and the panel list, and either prints the picture and tables or prints the problems and stops. Nothing about the panel list is checked at compile time, so a wrong sentence compiles and then reports itself the moment the program starts. (A `#DEFINE` that does not match its setting is the exception: the compiler reports it, see [When a `#DEFINE` and its setting do not match](#when-a-define-and-its-setting-do-not-match).)

How to read the messages:

- Every line starts `HUB75: `.
- A message about one panel names it as `DISPn Ck`, where `k` is the panel's cable position, its place in the list counting from 0. A message about the whole display names it as `DISPn`; a message about a setting names the setting.
- In the text below, `n`, `k`, `j`, `N`, `T`, `F`, `R`, `L`, `A`, `W`, `X` and `E` stand for numbers the driver prints.
- After the last message the driver prints the summary line, then `END_SESSION`, and stops every cog.

The checks run in order, so one mistake does not set off a chain of others:

1. M1 and M2 stop the checks for that display.
2. Then the display settings: M3 and M4, then M5 and M6.
3. When M5 and M6 are clear, every sentence on its own (M7 to M10). When those are clear, the panels together: M11 (two in one cell), then M12 (one piece, only when there is no M11), and M13. The cube marks (M14 to M16) are checked when M5 and M6 are clear.
4. The fold of a cube (M17, M18) runs after the layout is built, only when M1 to M16 found nothing.

| # | Check | Exact message |
|---|---|---|
| M1 | the panel list is not whole `LONG`s | `HUB75: DISPn: the panel list is not whole LONGs; write each panel sentence with LONG` |
| M2 | the display has no panels | `HUB75: DISPn: has no panels, so its adapter cannot be started; give it a panel list (and #DEFINE DISPn_PRESENT)` |
| M3 | the mounting override is not a mounting word | `HUB75: DISPn_ROTATION: must be AS_BUILT, TOP_TO_RIGHT, TOP_TO_BOTTOM or TOP_TO_LEFT` |
| M4 | the derived row-address count is not 8, 16 or 32 | `HUB75: DISPn: panels R rows tall, lit L rows per address, need A row addresses; the driver drives 8, 16 or 32` |
| M5 | a panel width that is not a multiple of 4 | `HUB75: DISPn: panels W columns wide (DISPn_PANEL_COLUMNS) are not supported; the width must be a multiple of 4` |
| M6 | more panels than the line buffer allows | `HUB75: DISPn: N panels exceed the driver limit of L for panels W columns wide; one row along the cable would be X columns, and the refresh line buffer holds 512` |
| M7 | stray bits in a sentence: a mounting word, or words joined with `+` | `HUB75: DISPn Ck: has bits that no panel word uses (a mounting word, or words joined with +); join ROW_, COL_ and TOP_ words with \|` |
| M8 | no `ROW_` word | `HUB75: DISPn Ck: has no ROW_ word` |
| M9 | no `COL_` word | `HUB75: DISPn Ck: has no COL_ word` |
| M10 | no `TOP_` word, or more than one | `HUB75: DISPn Ck: needs exactly one of TOP_UP, TOP_DOWN, TOP_LEFT, TOP_RIGHT` |
| M11 | two panels in one cell | `HUB75: DISPn Ck: is in the same cell as Cj` |
| M12 | a panel that shares no full edge with the rest | `HUB75: DISPn Ck: shares no full edge with the panels joined to C0; the panels must form one piece` |
| M13 | on panels that are not square, tops that mix sideways with upright | `HUB75: DISPn Ck: has its top at right angles to C0's; panels that are not square are all TOP_UP or TOP_DOWN, or all TOP_LEFT or TOP_RIGHT` |
| M14 | the cube marks misused | `HUB75: DISPn: a cube marks one panel CUBE_TOP and a different panel CUBE_FRONT; found T CUBE_TOP and F CUBE_FRONT` |
| M15 | a cube without exactly six panels | `HUB75: DISPn: a cube needs exactly 6 panels, but N are in use` |
| M16 | a cube of panels that are not square | `HUB75: DISPn: a cube needs square panels, but each panel is W columns x R rows` |
| M17 | the panels are not one of the 11 cube nets | `HUB75: DISPn: the panels do not fold into a cube (Cj and Ck fold onto the same face); arrange the six panels as one of the 11 cube nets` |
| M18 | Front opposite Top once folded | `HUB75: DISPn Ck: marked CUBE_FRONT, is opposite the CUBE_TOP face (Cj) when the panels are folded; the front face must share an edge with the top face` |
| N1 | notice: a mounting override on a cube (not a mistake; startup continues) | `HUB75: DISPn: DISPn_ROTATION does not apply to a cube and is ignored` |
| End | summary, after any of M1 to M18 | `HUB75: DISPn: E problem(s) above; startup stopped` |
| stop | `DISPn_ADAPTER_BASE_PIN` is not one of `PIN_GROUP_P0_P15`, `PIN_GROUP_P16_P31`, `PIN_GROUP_P32_P47` (startup aborts at this message, with no summary line) | `HUB75: configureAdapter() Invalid PinBase/PinGroup specified: [isp_hub75_hwBufferAccess.spin2] Aborted!` |
| notice | no refresh rate the driver can reach meets `DISPn_TARGET_REFRESH_HZ` (not a mistake; startup continues at the fastest rate) | `HUB75: DISPn: DISPn_TARGET_REFRESH_HZ = N Hz is out of reach for this display; running at N.N Hz, its fastest (j = j)` |
| notice | a panel chip with no /OE rating in the driver's table: any chip but FM6124, FM6126A, ICN2037, ICN2038S and MBI5124GP (not a mistake; startup continues) | `HUB75: DISPn: this panel chip has no /OE rating in the driver's table; the shortest /OE pulse is set to 50 ns` |
| notice | a panel chip with no clock rating in the driver's table (not a mistake; startup continues with the clock held to 20 MHz) | `HUB75: DISPn: this panel chip has no clock rating in the driver's table; the clock is held to 20 MHz` |
| stop | the /OE unit is longer than the brightness multiply's 16-bit operand (cannot happen within the driver limits; startup stops at this message, with no summary line) | `HUB75: DISPn: the /OE unit T = N clocks is longer than the brightness multiply's 16-bit operand (65535 clocks); startup stopped` |
| refusal | `showFrameSet()` given no frame set (while running, not at startup; nothing is posted) | `HUB75: DISPn: showFrameSet(NULL) refused: no frame set given; give one of this adapter's two PWM frame sets, $HHHH_HHHH or $HHHH_HHHH` |
| refusal | `showFrameSet()` given an address that is not one of the adapter's two PWM frame sets (while running; nothing is posted) | `HUB75: DISPn: showFrameSet($HHHH_HHHH) refused: not one of this adapter's two PWM frame sets, $HHHH_HHHH or $HHHH_HHHH` |

Notes on the table:

- M6 fires on the line-buffer limit (see [Driver limits](#driver-limits)). There is no other cap on the number of panels.
- M7 fires on any bit that is not a panel word. A mounting word written into a sentence sets such a bit; so does a `+` that carries out of a field. A repeated word inside its own kind (`TOP_UP + TOP_UP` = `TOP_DOWN`, `ROW_1 + ROW_1` = `ROW_3`) is a valid word and cannot be told apart from one that was meant; see [the doubled row or column](#the-doubled-row-or-column-that-cannot-be-detected). M11 and M12 catch what that does to the layout when it lands on another panel's cell or away from the rest.
- M13 exists because a panel turned sideways fills a cell of a different shape, so mixed tops cannot form a grid. Square panels are exempt, and `TOP_LEFT` with `TOP_RIGHT` (or `TOP_UP` with `TOP_DOWN`) is allowed. The cell size follows `C0`'s top.
- M17 and M18 are produced by the cube layer after the layout is built, so they appear only when every earlier check passed.
- The startup picture wraps at 96 characters, so a long chain prints several lines per grid row rather than one very long line.
- The mistake messages in the worked examples below are this table's text with that example's numbers filled in, read from the driver's checks; each is confirmed on the rig at bench run B-7 (to be marked when «#139» runs).

## Seven worked examples

Each example has the same parts:

1. a front-view sketch with the cable route;
2. the display block and panel list;
3. the picture the driver prints at startup, as a marked slot;
4. what the identify screen shows when the list is right, as a marked slot;
5. one or two common mistakes, each with the exact startup message.

In every sketch the arrow `-->` is the ribbon running from one panel to the next, and `C0` is where the adapter plugs in. The startup pictures and the identify descriptions are captured from the bench, not written by hand, so each is a slot for now: examples 3 and 4 run on the author's four-panel rig; the others are produced from a scratch layout build and are labelled as such when they are filled in.

### Example 1: a row of 4

Four 64x32 FM6126A panels (`CHIP_FM6126A`, 64 columns x 32 rows), the adapter at the left end, the ribbon running left to right. The derived address count is 32 / 2 = 16 (4 lines).

```
 front view

 +------+     +------+     +------+     +------+
 |  C0  | --> |  C1  | --> |  C2  | --> |  C3  |
 +------+     +------+     +------+     +------+
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 32
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_2 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_3 | hwEnum.TOP_UP
disp0PanelsEnd
```

This is also the starter list of the [procedure](#the-procedure) for four panels in one row.

The picture printed at startup:

```
(from a scratch layout build, labelled as such — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(this example is not on the rig — to be filled by «#139» from a scratch-layout build, labelled as such)
```

Common mistakes:

- **Two panels in one cell.** `C2` written in column 0, where `C0` already is.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C2: is in the same cell as C0
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **A forgotten top.** `C3` with no `TOP_` word.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_3
  ```

  ```
  HUB75: DISP0 C3: needs exactly one of TOP_UP, TOP_DOWN, TOP_LEFT, TOP_RIGHT
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

### Example 2: two panels

Two 64x64 ICN2037 panels (`CHIP_ICN2037`, 64 columns x 64 rows), one above the other, the adapter at the top panel and the ribbon running down. The derived address count is 64 / 2 = 32 (5 lines).

```
 front view

 +------+
 |  C0  |
 +------+
    |
    v
 +------+
 |  C1  |
 +------+
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
disp0PanelsEnd
```

The picture printed at startup:

```
(from a scratch layout build, labelled as such — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(this example is not on the rig — to be filled by «#139» from a scratch-layout build, labelled as such)
```

Common mistakes:

- **A forgotten column.** `C1` with a row and a top but no `COL_` word.

  ```
  LONG    hwEnum.ROW_1 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C1: has no COL_ word
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **Two row words joined.** `ROW_0 | ROW_1` is not "rows 0 and 1": it is the single value `ROW_2`. The panel lands two rows down, leaving a gap, so it no longer shares an edge with `C0`.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C1: shares no full edge with the panels joined to C0; the panels must form one piece
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

  Had that panel landed on a free cell next to the others, nothing could have told it from a panel written there on purpose.

### Example 3: 2x2 in Z order from bottom-left (the rig)

Four 128x64 ICN2037 panels (`CHIP_ICN2037`, 128 columns x 64 rows), hung upside down, so every `TOP_` word is `TOP_DOWN`. The adapter plugs into the bottom-left panel; the ribbon runs bottom-left, bottom-right, then jumps back to the left edge for top-left and top-right: a Z. This is the list the file ships with. The derived address count is 64 / 2 = 32 (5 lines), and four panels of 128 columns sit exactly at the 512-column limit.

```
 front view  (every panel hangs upside down)

 +--------+     +--------+
 |   C2   | --> |   C3   |
 +--------+     +--------+
      ^
      |  the ribbon runs back
      |  along the back to the left edge
 +--------+     +--------+
 |   C0   | --> |   C1   |
 +--------+     +--------+
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 128
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_DOWN
disp0PanelsEnd
```

The picture printed at startup:

```
(captured on the rig at bench run B-1/B-8 — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(captured on the rig at bench run B-1/B-8 — to be filled by «#139»)
```

Common mistakes:

- **Every top written `TOP_UP` although the panels hang upside down.** This is not a startup message: the list is perfectly valid, so the driver prints a normal picture. The mistake shows only on the identify screen, where the text is upside down and every arrow points down, but the `C` and `P` labels are still on the right panels. A wrong `TOP_` word turns a panel's content; it never moves it. Change each to the direction the arrows actually point (here `TOP_DOWN`) and run again.

- **A mounting word where a top belongs.** `TOP_TO_RIGHT` is for the [mounting override](#display-rotation), not for a sentence.

  ```
  LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_TO_RIGHT
  ```

  ```
  HUB75: DISP0 C1: has bits that no panel word uses (a mounting word, or words joined with +); join ROW_, COL_ and TOP_ words with |
  HUB75: DISP0 C1: needs exactly one of TOP_UP, TOP_DOWN, TOP_LEFT, TOP_RIGHT
  HUB75: DISP0: 2 problem(s) above; startup stopped
  ```

### Example 4: 2x2 serpentine

Four 128x64 ICN2037 panels. The ribbon runs right along the bottom row, up to the top row, then left along the top row. The top row is hung upside down so the ribbon can turn around, so its tops point down and the bottom row's point up.

```
 front view  (bottom row upright, top row upside down)

 +--------+     +--------+
 | C3  v  | <-- | C2  v  |
 +--------+     +--------+
                     ^
                     |
 +--------+     +--------+
 | C0  ^  | --> | C1  ^  |
 +--------+     +--------+
```

The display block (the same as example 3) and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 128
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_DOWN
                LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_DOWN
disp0PanelsEnd
```

The picture printed at startup:

```
(captured on the rig at bench run B-1/B-8 — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(captured on the rig at bench run B-1/B-8 — to be filled by «#139»)
```

Common mistakes:

- **The right words, the wrong cell.** `C3` written in the bottom-left cell, which is `C0`'s.

  ```
  LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_DOWN
  ```

  ```
  HUB75: DISP0 C3: is in the same cell as C0
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **Two tops in one sentence.** Trying to say "upright and upside down" at once. A panel has exactly one top.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_DOWN | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C2: needs exactly one of TOP_UP, TOP_DOWN, TOP_LEFT, TOP_RIGHT
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

### Example 5: 3 across x 2 down

Six 64x32 FM6126A panels (`CHIP_FM6126A`, 64 columns x 32 rows), three across and two down, all upright. The ribbon runs down the left column, across the bottom, up the middle column, across the top, and down the right column: a snake by columns.

```
 front view

 +------+     +------+     +------+
 |  C0  |     |  C3  | --> |  C4  |
 +------+     +------+     +------+
    |            ^            |
    v            |            v
 +------+     +------+     +------+
 |  C1  | --> |  C2  |     |  C5  |
 +------+     +------+     +------+
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 32
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_2 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_2 | hwEnum.TOP_UP
disp0PanelsEnd
```

The `P` numbers run along the rows while the `C` numbers run along the ribbon, so the two sets of numbers disagree on four of the six panels; that is correct.

The picture printed at startup:

```
(from a scratch layout build, labelled as such — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(this example is not on the rig — to be filled by «#139» from a scratch-layout build, labelled as such)
```

Common mistakes:

- **A sideways top on non-square panels.** On panels that are not square, every top must be vertical or every top must be sideways.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_2 | hwEnum.TOP_LEFT
  ```

  ```
  HUB75: DISP0 C4: has its top at right angles to C0's; panels that are not square are all TOP_UP or TOP_DOWN, or all TOP_LEFT or TOP_RIGHT
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **A panel that touches only at a corner.** `C5` written in column 3, a cell beyond the right column and one row down: it meets `C4` only at a corner.

  ```
  LONG    hwEnum.ROW_1 | hwEnum.COL_3 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C5: shares no full edge with the panels joined to C0; the panels must form one piece
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

### Example 6: an L shape

Four 64x64 ICN2037 panels in an L: three up the left side and one to the right of the bottom. The two cells at the top right hold no panel. The ribbon runs from the bottom-left panel, right to its neighbour, then back to the left column and up.

```
 front view  (two cells hold no panel)

 +------+
 |  C3  |
 +------+
    ^
    |
 +------+
 |  C2  |
 +------+
    ^
    |   the ribbon: C0 --> C1, then C2 and C3
 +------+     +------+
 |  C0  | --> |  C1  |
 +------+     +------+
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_2 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_2 | hwEnum.COL_1 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_0 | hwEnum.TOP_UP
disp0PanelsEnd
```

The empty cells stay dark; panel positions count only the cells that hold a panel, so they run with no gaps. The display is the size of the whole grid including its empty cells.

The picture printed at startup (a cell with no panel prints as `  --`):

```
(from a scratch layout build, labelled as such — to be filled by «#139»)
```

What the identify screen shows when the list is right:

```
(this example is not on the rig — to be filled by «#139» from a scratch-layout build, labelled as such)
```

Common mistakes:

- **A gap in the piece.** `C3` written in column 1 of the top row: it meets `C2` only at a corner and has an empty cell between it and `C1`.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C3: shares no full edge with the panels joined to C0; the panels must form one piece
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **A forgotten row.** `C1` with a column and a top but no `ROW_` word.

  ```
  LONG    hwEnum.COL_1 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0 C1: has no ROW_ word
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

### Example 7: the cube, wired in a ring, with Top and Front

Six 64x64 ICN2037 panels (`CHIP_ICN2037`, 64 columns x 64 rows), all upright, laid out as the cross-shaped net: the four side faces in a row (`C0` ... `C3`, the ribbon left to right), the top face above the second of them, the bottom face below it. `C4` is marked `CUBE_TOP` and `C1` is marked `CUBE_FRONT`.

```
 front view  (the net, laid flat)

              +------+
              |  C4  |   top face
              +------+
                 ^
                 |
 +------+     +------+     +------+     +------+
 |  C0  | --> |  C1  | --> |  C2  | --> |  C3  |
 +------+     +------+     +------+     +------+
                 |
                 v
              +------+
              |  C5  |   bottom face
              +------+

 the ribbon runs C0 --> C1 --> C2 --> C3, then C4 and C5
 (the panels fold along their shared edges into a cube)
```

The display block and panel list:

```
CON
    DISP0_ADAPTER_BASE_PIN  = hwEnum.PIN_GROUP_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP0_PANEL_COLUMNS     = 64
    DISP0_PANEL_ROWS        = 64
    DISP0_COLOR_DEPTH       = hwEnum.DEPTH_8BIT

DAT
disp0Panels     LONG    hwEnum.ROW_1 | hwEnum.COL_0 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_FRONT
                LONG    hwEnum.ROW_1 | hwEnum.COL_2 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_1 | hwEnum.COL_3 | hwEnum.TOP_UP
                LONG    hwEnum.ROW_0 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_TOP
                LONG    hwEnum.ROW_2 | hwEnum.COL_1 | hwEnum.TOP_UP
disp0PanelsEnd
```

The picture printed at startup. After the cable-to-panel table the driver prints the faces it derived, one line each, in the order `TOP`, `BOTTOM`, `FRONT`, `BACK`, `LEFT`, `RIGHT`:

```
(from a scratch layout build, labelled as such — to be filled by «#139»)
```

The form of a face line is `HUB75: DISP0 cube FRONT = Ck (Pp, up a): N->face.edge E->face.edge S->face.edge W->face.edge`. It says the front face is the panel at cable position `k`, panel position `p`, and its up arrow `a` points as the picture shows. Then each of the face's four edges, `N`, `E`, `S`, `W`, names the face beyond it and which of that face's edges meets this one. Every face line is the same kind of line, and together they list all 12 edges of the cube from both sides.

What the identify screen shows when the list is right:

```
(this example is not on the rig — to be filled by «#139» from a scratch-layout build, labelled as such)
```

Identify checks the wiring of the net; it does not show the folded cube.

Common mistakes:

- **Not a cube net.** Both `C4` and `C5` placed above the ring: two panels would fold onto the same face.

  ```
  LONG    hwEnum.ROW_0 | hwEnum.COL_2 | hwEnum.TOP_UP
  ```

  ```
  HUB75: DISP0: the panels do not fold into a cube (C4 and C5 fold onto the same face); arrange the six panels as one of the 11 cube nets
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

- **Front opposite Top.** `CUBE_FRONT` moved to `C5`, the face that lies opposite the top once folded. The front face must share an edge with the top face.

  ```
  LONG    hwEnum.ROW_1 | hwEnum.COL_1 | hwEnum.TOP_UP
  LONG    hwEnum.ROW_2 | hwEnum.COL_1 | hwEnum.TOP_UP | hwEnum.CUBE_FRONT
  ```

  ```
  HUB75: DISP0 C5: marked CUBE_FRONT, is opposite the CUBE_TOP face (C4) when the panels are folded; the front face must share an edge with the top face
  HUB75: DISP0: 1 problem(s) above; startup stopped
  ```

---

*Questions about a configuration that this guide does not cover? File an issue with your panel list and the startup lines your driver printed.*
