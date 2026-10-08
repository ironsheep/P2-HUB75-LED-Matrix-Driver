# Wiring Guide

How to tell the driver where your panels are, which way they hang, and how they are cabled: the wiring sentences, the identify screen that confirms them, display rotation, the cube, the limits of the driver, every message the driver prints when a sentence is wrong, and seven worked examples.

Pages: [README](../README.md) | [Driver Details (THEOPS)](../THEOPS.md) | [Multi-Panel Configuration](MultiPanelConfiguration.md)

Within this page:

- [Words used here](#words-used-here)
- [The wiring sentences](#the-wiring-sentences) - the grammar: three forms, four kinds of word, five rules
- [Filling in your config from the identify screen](#filling-in-your-config-from-the-identify-screen)
- [Display rotation](#display-rotation) - how the whole display hangs, and how to turn an image
- [The cube](#the-cube) - six panels as one object
- [Driver limits](#driver-limits) - how many panels per adapter, by panel type
- [Startup messages](#startup-messages) - what the driver prints, every mistake it catches
- [Seven worked examples](#seven-worked-examples)

## Words used here

This page uses the terms defined in the [glossary](../THEOPS.md#glossary), and only those: **adapter**, **display**, **display coordinates**, **panel position** (`P0`, `P1`, ... in reading order), **cable position** (`C0` is the panel the adapter plugs into), **panel rotation**, **display rotation**, **wiring**, **face** and **cube orientation**. Read the glossary once if any of them is new to you.

The short version: a **cable position** names a piece of hardware and never changes; a **panel position** names a place on the display as the viewer sees it. The wiring sentences are what connect the two.

## The wiring sentences

Wiring is described in `isp_hub75_hwPanelConfig.spin2`, one sentence per cable position: `DISPn_C0` through `DISPn_C15`, where `n` is the display (adapter 1 drives `DISP0`). Each sentence describes the panel at that cable position: where it sits next to a panel already described, and which way its arrow points.

A sentence is a few words joined with `|`:

```
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_DOWN
```

Read it aloud: "C1 sits to the right of C0, and its arrow points down."

### Three forms

Every sentence is exactly one of these:

| Form | Used for |
|---|---|
| `FIRST_PANEL \| arrow` | `C0`, and only `C0` |
| `direction \| neighbour \| arrow` | every other panel in use |
| `NO_PANEL` | every unused cable position |

### Four kinds of word

Each word is written with the `hwEnum.` prefix (`hwEnum.RIGHT_OF`).

| Kind | Words | Meaning |
|---|---|---|
| direction | `ABOVE`, `BELOW`, `LEFT_OF`, `RIGHT_OF` | where this panel sits relative to its neighbour: `ABOVE` means this panel is above the neighbour |
| neighbour | `C0` ... `C15` | the cable position of the panel this one sits next to |
| arrow | `ARROW_UP`, `ARROW_DOWN`, `ARROW_LEFT`, `ARROW_RIGHT` | the way the arrow the identify screen draws on this panel points, which is the panel's own up as it hangs (its panel rotation) |
| marker | `FIRST_PANEL`, `NO_PANEL` | `FIRST_PANEL` marks the panel the adapter plugs into; `NO_PANEL` marks an unused cable position |

A sentence uses at most one word of each kind. The panel shapes are `SHAPE_FLAT` and `SHAPE_CUBE`, set separately in `DISPn_SHAPE`; they are not part of a sentence.

### Five rules

1. **Join the words with `|` only, never `+`, and in any order.** `RIGHT_OF | C0 | ARROW_UP` and `ARROW_UP | C0 | RIGHT_OF` mean the same thing.
2. **The neighbour shares a full edge with this panel.** It may come earlier or later along the cable.
3. **Every panel connects back to `C0` through its neighbours.**
4. **No two panels share a cell.**
5. **Panels in use are numbered `C0`, `C1`, `C2` and so on with no gaps, and `NO_PANEL` comes only after the last one.**

### Why `|` and never `+`

Every word is a single bit, and the neighbour words `C0` ... `C15` are consecutive bits. Joining with `|` sets each bit without disturbing the others. Adding with `+` lets a repeated word carry into the next bit: `C2 + C2` silently becomes `C3`, and your panel quietly names the wrong neighbour. The driver catches what it can (see the [catalogue](#startup-messages)), but the surest protection is to write `|` every time. Example 2 shows exactly what happens.

### Unused cable positions, and the other adapters

Set every cable position you do not use to `hwEnum.NO_PANEL`. An adapter whose `DISPn_C0` is `NO_PANEL` has no panels: its buffers are zero length and cost no memory. You never comment code in or out to add a second or third adapter; describe its panels in its own `DISP1_` or `DISP2_` group.

### What a good config prints

When the sentences are right, the driver prints the layout it derived, at startup, before it starts the panels: the size of the display, one line of picture per grid row, and a table of where every panel went. The picture shows a cell as `[Ck a]`, where `k` is the cable position and `a` is the arrow (`^`, `v`, `<` or `>`). A cell that holds no panel prints as `  --  `. When the display has more than ten panels, single-digit cells are padded (`[C2  v]`) so the columns line up.

Each example below shows its picture. The line `cable -> panel position` is the one to keep in mind: it says which panel position each cable position ended up at.

## Filling in your config from the identify screen

The identify program, `demo_hub75_numberPanels.spin2`, draws on every panel:

- an arrow (`^`) near the top, pointing the way the panel's own up points;
- `C`*k*, the cable position of that panel;
- `P`*p*, the panel position of that panel.

Each panel also gets its own background colour, which makes the panels easy to tell apart when you describe them. Small panels (for example 64x32 with the 5x7 font) get a compact layout: the `^` and then `C2P1` on one line.

Because the `C` labels are drawn through the driver's inverse table, they are **physically correct even when your config is wrong**. A panel labelled `C2` is the panel at cable position 2. The labels tell you the truth; the sentences are what you are checking.

### The procedure

1. Describe the chip, address lines, panel size and colour depth for your panels.
2. For every panel, write `ARROW_UP`. Do not try to work out the arrows yet.
3. Looking at the **front** of your display, write each direction and neighbour: follow the ribbon from the adapter, and for each panel say which earlier panel it touches and on which side (`RIGHT_OF`, `BELOW`, ...). Leave unused cable positions `NO_PANEL`.
4. Build and run identify. The startup picture appears first; if the driver names a mistake, fix that sentence and run again (see the [catalogue](#startup-messages)).
5. Read the panels:
   - **`P` labels in reading order and every arrow up: the config is right.** Reading order is left to right along the top row, then each row below.
   - **`P` labels out of order, `C` labels where you expect them:** the directions or neighbours place panels wrongly. The `C` labels show where each cable position really is, so use them to correct the sentences.
   - **An arrow pointing another way, or text upside down:** that panel's arrow word is wrong. Write the arrow word for the direction the arrow actually points on that panel, and run again.

A fresh config with every arrow `ARROW_UP` shows each panel's native up. On a panel hung upside down, the text is upside down and the arrows point down; the labels are still in the right places, because a wrong arrow word turns a panel's content and never moves it. On the rig of example 3, a run with every arrow written `ARROW_UP` showed *"all text is upside down but C\* and P\* seem to be in correct locations ... ^ all point down"*. Changing each to `ARROW_DOWN` fixed it.

A wrong **direction** word does the opposite: it moves the `P` labels and leaves the content upright. On the same rig, describing `C1` as `ABOVE` `C0` showed *"text and arrows right side up. P\* numbers are wrong, C\* numbers correct"*.

When the identify screen is up, the driver prints `END_SESSION` and holds the image.

## Display rotation

Two things can be turned, and they are different:

| What | How you set it | Meaning |
|---|---|---|
| each panel | the arrow word in its sentence | how that one panel is hung within the display |
| the whole display | `DISPn_ROTATION` | how the assembled display is hung |

**`DISPn_ROTATION` is physical.** It says how the display is mounted, and the driver draws so the content reads upright to the person looking at it:

| Value | The display hangs |
|---|---|
| `ROT_NONE` | as the sentences describe |
| `ROT_RIGHT_90` | turned 90 degrees clockwise |
| `ROT_LEFT_90` | turned 90 degrees counter-clockwise |
| `ROT_180` | upside down |

On a flat bench rig, `ROT_RIGHT_90` therefore looks turned to the left: you are looking at the display as if it hung turned right. Set `ROT_NONE` first, verify the panels with identify, then set the rotation that matches how you hung the display. Display rotation applies to flat displays only; on a cube it is ignored (see [the cube](#the-cube)).

With the display hung at 90 or 270 degrees, the display size the driver reports is the size **as mounted**: width and height swap, and so do the text grid's columns and lines.

### Everything is in the viewer's frame

Your program never sees cables, arrows or the way the display was mounted; the wiring sentences and `DISPn_ROTATION` are translated away at startup. Drawing calls use the display as the viewer sees it:

- display coordinates start at the top-left as mounted;
- `P0` is the top-left panel as the display hangs, and panel positions run in reading order as mounted;
- in a panel-centric call, row 0 is that panel's top as the viewer sees it, and anything that runs past the panel's edge is clipped, never spilled onto a neighbour.

### Turning an image: content rotation

Turning an image is separate from mounting. The image-placing call, `placeBMP`, takes a content rotation (`ROT_NONE`, `ROT_RIGHT_90` for clockwise, `ROT_LEFT_90` or `ROT_180`). The image is turned about the centre of the display as it is placed; the part that falls off the display is simply not shown, and nothing is wrapped or moved. Placing again with another rotation re-places the picture from the source, so nothing is lost. Content rotation works for an image of any size, composes with mounting, and does not affect text or shapes you draw (a drawn display already follows the display's geometry). A cube has no face-aware image call: `placeBMP` places the image on the flat layout of the net, not carried across the folded edges.

## The cube

Six **square** panels, wired as one of the 11 nets of a cube, form a cube display. Set:

```
DISP0_SHAPE      = hwEnum.SHAPE_CUBE
DISP0_CUBE_TOP   = hwEnum.C4
DISP0_CUBE_FRONT = hwEnum.C1
```

`DISPn_CUBE_TOP` and `DISPn_CUBE_FRONT` are cable positions (`hwEnum.C0` ... `hwEnum.C15`). The front face must share an edge with the top face. Together they are the **cube orientation**; they take the place of display rotation, which is ignored on a cube. If you set a rotation anyway, the driver prints a notice and carries on (see the [catalogue](#startup-messages)).

The wiring sentences describe the panels laid flat, as a net: the sentences are the same as for any flat display, and the driver checks that they fold into a cube.

### Face names

From Top and Front the driver derives the six face names: `TOP` and `FRONT` are the two you named; `BOTTOM` is opposite the top; `BACK` is opposite the front; `LEFT` and `RIGHT` are the faces on the viewer's left and right when standing at the front.

### Up on each face

Every face is seen from outside the cube, with row 0 along the face's up edge and column 0 along its left edge. The up directions are fixed:

- on the four sides (`FRONT`, `BACK`, `LEFT`, `RIGHT`), up points toward `TOP`;
- on `TOP`, up points toward `BACK`, so that standing at `FRONT`, text on `TOP` reads correctly;
- on `BOTTOM`, up points toward `FRONT`.

These conventions do not change between releases, so anything you build on them stays valid.

### Folding

At startup the driver folds the net and works out all 12 edges, including those the flat picture does not show, and how coordinates carry across each one. The startup log prints one line per face; example 7 shows them. In each line the four edges of the face are named `N`, `E`, `S`, `W` (as the face is seen from outside, with `N` its up edge), and each entry says which face lies beyond that edge and which of its edges meets it: `N->TOP.S` on the front face says the front's top edge meets the top face's south edge.

### Drawing on faces

Face-centric calls address a pixel as (face, row, column), and the row and column may run past the edge of the face. A pixel that does is carried across the edge onto the neighbouring face, as many edges as it crosses. Face-centric calls therefore **fold**, where panel-centric calls **clip**. Lines, boxes, circles, text and scrolling all fold across every edge.

Two rules govern corners:

- **The corner gap.** A cube corner has three faces meeting, so 270 degrees of surface around the corner, not 360. A pixel past two edges of one face at once lands in the missing quarter, where there is no surface, and it is discarded. An object whose centre falls in that gap is first moved to the nearest surface point (the axis with the smaller overshoot is snapped; on a tie the column is snapped).
- **Seam placement.** An object that straddles a corner off-centre has one unavoidable seam. The driver puts the seam on the edge farthest from the object's centre.

A shape centred on a face, on an edge or on a corner is seamless while it stays within that face, that edge's span, or the three faces of that corner. A shape centred on an edge but large enough to reach the corners at the ends of the edge meets those corners' gaps.

The fold is checked without any panels attached by `test_hub75_cube_fold.spin2`, which pushes a fixed list of face coordinates through the fold and prints PASS or FAIL for each. A cube on six real panels has not yet been run on hardware.

## Driver limits

How many panels one adapter can drive depends on the panel. The hard limit for every panel type is the **refresh line buffer**: the refresh core holds one row of the whole chain, 512 column clocks. The driver checks this at startup (message in the [catalogue](#startup-messages)). Hub RAM sets a separate limit that the compiler enforces.

A display must pass all four limits, and the tightest decides:

| Limit | What sets it | Where it binds |
|---|---|---|
| Refresh line buffer | One row of the whole chain, 512 column clocks | Per adapter |
| Hub RAM | All three adapters' buffers share what is left of 512 KB | Across adapters |
| Refresh rate | The chain's column clocks, row addresses and colour depth, against `DISPn_TARGET_REFRESH_HZ` ([Refresh rate](#refresh-rate)); a display that cannot reach the target runs at its fastest rate | Per adapter |
| Pins and cogs | Each adapter takes a 16-pin group and one refresh cog | Board-wide |
| Panel width | `DISPn_MAX_PANEL_COLUMNS` must be a multiple of 4 (every common panel is: 32, 64, 80, 128); startup stops with a message otherwise | Per adapter |

**Max panels per adapter = 512 / (panel columns x scan factor)**, never more than 16 (the number of cable positions). The scan factor is 2 for chips the driver flags as quarter-scan (`SCAN_4`: ICN2038S, MBI5124GP, DP5125D) and 1 for every other chip.

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
- The ICN2038S has five address lines (which fits 1/32 scan and would give a limit of 8), but the driver flags the chip as quarter-scan, so the limit it enforces is 4.
- The ICN2038S panel is single-ended, so it cannot be chained. Multi-panel use of the FM6124 and GS6238S has not been proven on hardware, and the MBI5124GP has been run with two panels, so for those rows the number is the driver's cap, not a demonstrated working count.

### Hub RAM

One panel of P pixels at colour depth N takes **P x (3 + N) bytes**: the screen buffer (3 bytes per pixel) plus two PWM frame sets (N x P / 2 bytes each). The compiler builds all three adapters' buffers into the same program, so the buffers of every adapter share what is left of the 512 KB hub RAM.

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

`DISPn_TARGET_REFRESH_HZ` (default 60) says how fast the display should refresh. At startup the driver takes S, the clocks to shift one row of one plane (the chain's column clocks x the clocks per column), and tries T = S / 2^*j* for *j* = 0, 1, 2, ... until the predicted refresh reaches the target. T never goes below the chip's shortest /OE pulse. The smallest *j* that meets the target gives the longest T, and so the brightest picture. *j* = 0 lights every plane for its whole slot.

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

When the driver starts an adapter it decodes the sentences, checks them, and either prints the picture and tables or prints the problems and stops. Nothing is checked at compile time, so a wrong sentence compiles and then reports itself the moment the program starts.

How to read the messages:

- Every line starts `HUB75: `.
- A message about one sentence names the setting as `DISPn_Ck`. A message about the whole display names it as `DISPn`.
- In the text below, `n`, `k`, `j`, `N`, `L`, `W` and `R` stand for numbers the driver prints.
- After the last message the driver prints the summary line, then `END_SESSION`, and stops every cog.

The checks run in two passes, so one mistake does not set off a chain of others:

1. Every sentence on its own (rows 1-7, 11, 13 and 14), then the whole display (rows 10, 12, 15-18, 21 and 22). All of these are reported in one run.
2. The walk out from `C0` (rows 8 and 9), then, for a cube, the fold (rows 19 and 20). It runs only when pass 1 found nothing, because it needs well-formed sentences.

| # | Check | Exact message |
|---|---|---|
| 1 | more than one word of a kind | `HUB75: DISPn_Ck: has more than one direction word; use exactly one of ABOVE, BELOW, LEFT_OF, RIGHT_OF` |
| | | `HUB75: DISPn_Ck: has more than one neighbour word; use exactly one of C0 .. C15` |
| | | `HUB75: DISPn_Ck: has more than one arrow word; use exactly one of ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT` |
| 2 | a required word missing | `HUB75: DISPn_Ck: has no direction word; add one of ABOVE, BELOW, LEFT_OF, RIGHT_OF` |
| | | `HUB75: DISPn_Ck: has no neighbour word; add the cable position (C0 .. C15) of the panel it sits next to` |
| | | `HUB75: DISPn_Ck: has no arrow word; add one of ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT` (C0 too) |
| 3 | `FIRST_PANEL` on anything but C0 | `HUB75: DISPn_Ck: uses FIRST_PANEL, which belongs only to C0; write direction \| neighbour \| arrow` |
| 4 | C0 not `FIRST_PANEL` while panels are in use | `HUB75: DISPn_C0: must be FIRST_PANEL \| arrow, because panels are in use` |
| 5 | a panel as its own neighbour | `HUB75: DISPn_Ck: names itself as its neighbour; name the panel it sits next to` |
| 6 | the neighbour is a `NO_PANEL` | `HUB75: DISPn_Ck: names Cj as its neighbour, but that cable position is NO_PANEL` |
| 7 | a gap in the numbering | `HUB75: DISPn_Ck: is in use, but Cj before it is NO_PANEL; number the panels in use C0, C1, C2 ... with no gaps` |
| 8 | two panels in one cell | `HUB75: DISPn_Ck: sits in the same cell as Cj` |
| 9 | a panel that doesn't connect back to C0 | `HUB75: DISPn_Ck: does not connect back to C0 through its neighbours` |
| 10 | more panels than the driver limit | `HUB75: DISPn: N panels exceed the driver limit of L for panels W columns wide; one row along the cable would be R columns, and the refresh line buffer holds 512` |
| 11 | `+` where `\|` was meant, where detectable | `HUB75: DISPn_Ck: looks like + joined a word to itself and carried into the next kind of word; join the words with \| only, never +` |
| | | `HUB75: DISPn_Ck: has bits that no wiring word uses; join the words with \| only, never +` |
| 12 | starting an adapter with no panels | `HUB75: DISPn: has no panels (every DISPn_C0 .. DISPn_C15 is NO_PANEL), so its adapter cannot be started` |
| 13 | a word the form does not allow | `HUB75: DISPn_C0: takes only FIRST_PANEL and an arrow; remove its direction and neighbour words` |
| | | `HUB75: DISPn_Ck: joins NO_PANEL with other words; NO_PANEL stands alone` |
| 14 | on panels that are not square, arrows that mix sideways with upright | `HUB75: DISPn_Ck: has its arrow at right angles to C0's arrow; on panels that are not square, every arrow is ARROW_UP or ARROW_DOWN, or every arrow is ARROW_LEFT or ARROW_RIGHT` |
| 15 | a cube without exactly six panels | `HUB75: DISPn: a cube needs exactly 6 panels, but N are in use` |
| 16 | a cube of panels that are not square | `HUB75: DISPn: a cube needs square panels, but each panel is W columns x R rows (DISPn_MAX_PANEL_COLUMNS, DISPn_MAX_PANEL_ROWS)` |
| 17 | `DISPn_CUBE_TOP` / `DISPn_CUBE_FRONT` not one cable position in use | `HUB75: DISPn_CUBE_TOP: must be exactly one of C0 .. C5, the cable position of the top face` (and the same for `DISPn_CUBE_FRONT`, the front face); `HUB75: DISPn_CUBE_TOP: names Cj, but that cable position is NO_PANEL` (and for `DISPn_CUBE_FRONT`) |
| 18 | Front is the same panel as Top | `HUB75: DISPn_CUBE_FRONT: names the same panel as DISPn_CUBE_TOP; the front face is a different panel that shares an edge with the top face` |
| 19 | the panels are not one of the 11 cube nets | `HUB75: DISPn: the panels do not fold into a cube (Cj and Ck fold onto the same face); arrange the six panels as one of the 11 cube nets` |
| 20 | Front opposite Top once folded | `HUB75: DISPn_CUBE_FRONT: Cj is opposite the top face (Ck) when the panels are folded; the front face must share an edge with the top face` |
| 21 | a shape value other than flat or cube | `HUB75: DISPn: DISPn_SHAPE must be SHAPE_FLAT or SHAPE_CUBE` |
| 22 | a panel width that is not a multiple of 4 | `HUB75: DISPn: panels W columns wide (DISPn_MAX_PANEL_COLUMNS) are not supported; the width must be a multiple of 4` |
| notice | a mounting rotation on a cube (not a mistake; startup continues) | `HUB75: DISPn: DISPn_ROTATION does not apply to a cube and is ignored` |
| stop | `DISPn_ADAPTER_BASE_PIN` is not one of `PIN_GROUP_P0_P15`, `PIN_GROUP_P16_P31`, `PIN_GROUP_P32_P47` (startup aborts at this message, with no summary line) | `HUB75: configureAdapter() Invalid PinBase/PinGroup specified: [isp_hub75_hwBufferAccess.spin2] Aborted!` |
| - | summary, after any of the above | `HUB75: DISPn: K wiring problem(s) above; startup stopped` |
| notice | no refresh rate the driver can reach meets `DISPn_TARGET_REFRESH_HZ` (not a mistake; startup continues at the fastest rate) | `HUB75: DISPn: DISPn_TARGET_REFRESH_HZ = N Hz is out of reach for this display; running at N.N Hz, its fastest (j = j)` |
| notice | a panel chip with no /OE rating in the driver's table: any chip but FM6124, FM6126A, ICN2037, ICN2038S and MBI5124GP (not a mistake; startup continues) | `HUB75: DISPn: this panel chip has no /OE rating in the driver's table; the shortest /OE pulse is set to 50 ns` |
| notice | a panel chip with no clock rating in the driver's table (not a mistake; startup continues with the clock held to 20 MHz) | `HUB75: DISPn: this panel chip has no clock rating in the driver's table; the clock is held to 20 MHz` |
| stop | the /OE unit is longer than the brightness multiply's 16-bit operand (cannot happen within the driver limits; startup stops at this message, with no summary line) | `HUB75: DISPn: the /OE unit T = N clocks is longer than the brightness multiply's 16-bit operand (65535 clocks); startup stopped` |
| refusal | `showFrameSet()` given no frame set (while running, not at startup; nothing is posted) | `HUB75: DISPn: showFrameSet(NULL) refused: no frame set given; give one of this adapter's two PWM frame sets, $HHHH_HHHH or $HHHH_HHHH` |
| refusal | `showFrameSet()` given an address that is not one of the adapter's two PWM frame sets (while running; nothing is posted) | `HUB75: DISPn: showFrameSet($HHHH_HHHH) refused: not one of this adapter's two PWM frame sets, $HHHH_HHHH or $HHHH_HHHH` |

Notes on the table:

- Row 10 fires on the line-buffer limit (see [Driver limits](#driver-limits)). The converter's own limit of 16 panels cannot fire, because the wiring names at most 16 cable positions.
- Row 11 fires only where the carry is visible. Joining *different* words with `+` gives the same value as `|` and is harmless. Repeating a word inside its own kind (`C2 + C2` = `C3`) cannot be told apart from the word it carries into; rows 1-9 catch what that does to the layout, and example 2 shows one.
- Row 14 exists because a panel turned sideways fills a cell of a different shape, so mixed arrows cannot form a grid. Square panels are exempt, and `ARROW_LEFT` with `ARROW_RIGHT` (or `ARROW_UP` with `ARROW_DOWN`) is allowed. The cell size follows `C0`'s arrow.
- Every message in the worked examples below was captured from a real run of that example's config, on the P2 with no panels attached.

## Seven worked examples

Each example has the same five parts:

1. a front-view sketch with the cable route;
2. the sentences;
3. the picture the driver prints at startup;
4. what the identify screen shows when the config is right;
5. one or two common mistakes, each with the exact startup message.

In every sketch the arrow `-->` is the ribbon running from one panel to the next, and `C0` is where the adapter plugs in. The startup blocks are the driver's lines for the display, with the time stamp removed. Each block begins with the wiring line, then the picture, then one line per panel position, then the cable-to-panel table.

### Example 1: a row of 4

Four 64x32 FM6126A panels (`CHIP_FM6126A`, `ADDR_ABCD`, 64 columns x 32 rows), the adapter at the left end, the ribbon running left to right.

```
 front view

 +------+     +------+     +------+     +------+
 |  C0  | --> |  C1  | --> |  C2  | --> |  C3  |
 +------+     +------+     +------+     +------+
```

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C2 = hwEnum.RIGHT_OF | hwEnum.C1 | hwEnum.ARROW_UP
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_UP
```

The picture printed at startup:

```
HUB75: DISP0 wiring: 4 panels in a grid of 1 rows x 4 columns, 256 x 32 pixels (columns x rows)
HUB75: DISP0   [C0 ^][C1 ^][C2 ^][C3 ^]
HUB75: DISP0 P0 = C0, buffer slot 3, cell row 0 column 0, rotation 0
HUB75: DISP0 P1 = C1, buffer slot 2, cell row 0 column 1, rotation 0
HUB75: DISP0 P2 = C2, buffer slot 1, cell row 0 column 2, rotation 0
HUB75: DISP0 P3 = C3, buffer slot 0, cell row 0 column 3, rotation 0
HUB75: DISP0 cable -> panel position: C0->P0 C1->P1 C2->P2 C3->P3
```

When identify is right: the cable position and the panel position agree on every panel (`C0->P0 C1->P1 C2->P2 C3->P3`), so the four panels read `C0P0`, `C1P1`, `C2P2`, `C3P3` from left to right. The panels are small, so identify uses the compact layout: an upright `^` and the label on one line. Every arrow points up.

Common mistakes:

- **A wrong direction word.** `C2` written `LEFT_OF` `C1` instead of `RIGHT_OF` puts `C2` back in `C0`'s cell, and `C3`, which hangs off `C2`, lands in `C1`'s cell.

  ```
  DISP0_C2 = hwEnum.LEFT_OF | hwEnum.C1 | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C2: sits in the same cell as C0
  HUB75: DISP0_C3: sits in the same cell as C1
  HUB75: DISP0: 2 wiring problem(s) above; startup stopped
  ```

- **A forgotten arrow.** `C3` with no arrow word.

  ```
  DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2
  ```

  ```
  HUB75: DISP0_C3: has no arrow word; add one of ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

### Example 2: two panels

Two 64x64 ICN2037 panels (`CHIP_ICN2037`, `ADDR_ABCDE`, 64 columns x 64 rows), one above the other, the adapter at the top panel and the ribbon running down.

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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.BELOW | hwEnum.C0 | hwEnum.ARROW_UP
```

The picture printed at startup:

```
HUB75: DISP0 wiring: 2 panels in a grid of 2 rows x 1 columns, 64 x 128 pixels (columns x rows)
HUB75: DISP0   [C0 ^]
HUB75: DISP0   [C1 ^]
HUB75: DISP0 P0 = C0, buffer slot 1, cell row 0 column 0, rotation 0
HUB75: DISP0 P1 = C1, buffer slot 0, cell row 1 column 0, rotation 0
HUB75: DISP0 cable -> panel position: C0->P0 C1->P1
```

When identify is right: the top panel reads `C0` and `P0`, the bottom panel `C1` and `P1` (`C0->P0 C1->P1`), each with its arrow pointing up. Because these panels are larger, identify uses the full layout with the arrow, `C` label and `P` label stacked.

Common mistakes:

- **`FIRST_PANEL` forgotten.** `C0` is just an arrow, but the display has panels in use.

  ```
  DISP0_C0 = hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C0: must be FIRST_PANEL | arrow, because panels are in use
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **`+` instead of `|`.** `C0 + C0` is `C1`, so the neighbour word becomes the panel's own cable position.

  ```
  DISP0_C1 = hwEnum.BELOW | hwEnum.C0 + hwEnum.C0 | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C1: names itself as its neighbour; name the panel it sits next to
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

### Example 3: 2x2 in Z order from bottom-left (the rig)

Four 128x64 ICN2037 panels (`CHIP_ICN2037`, `ADDR_ABCDE`, 128 columns x 64 rows), hung upside down, so every arrow is `ARROW_DOWN`. The adapter plugs into the bottom-left panel; the ribbon runs bottom-left, bottom-right, then jumps back to the left edge for top-left and top-right: a Z.

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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_DOWN
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_DOWN
DISP0_C2 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_DOWN
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_DOWN
```

The picture printed at startup:

```
HUB75: DISP0 wiring: 4 panels in a grid of 2 rows x 2 columns, 256 x 128 pixels (columns x rows)
HUB75: DISP0   [C2 v][C3 v]
HUB75: DISP0   [C0 v][C1 v]
HUB75: DISP0 P0 = C2, buffer slot 1, cell row 0 column 0, rotation 180
HUB75: DISP0 P1 = C3, buffer slot 0, cell row 0 column 1, rotation 180
HUB75: DISP0 P2 = C0, buffer slot 3, cell row 1 column 0, rotation 180
HUB75: DISP0 P3 = C1, buffer slot 2, cell row 1 column 1, rotation 180
HUB75: DISP0 cable -> panel position: C0->P2 C1->P3 C2->P0 C3->P1
```

When identify is right: `C0` is at the bottom-left, `C1` at the bottom-right, `C2` at the top-left and `C3` at the top-right, and the `P` labels read `P0`, `P1` across the top and `P2`, `P3` across the bottom (`C0->P2 C1->P3 C2->P0 C3->P1`). Every arrow points up and the text reads upright, even though the panels hang upside down; that is what `ARROW_DOWN` is for. On the rig the observation was *"all four panels now labelled correctly"*.

Common mistakes:

- **The wrong neighbour.** `C3` described as the right of `C0` instead of the right of `C2` lands on `C1`'s cell.

  ```
  DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_DOWN
  ```

  ```
  HUB75: DISP0_C3: sits in the same cell as C1
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **Every arrow written `ARROW_UP` although the panels hang upside down.** This is not a startup message: the sentences are perfectly valid, so the driver prints a normal picture, with `^` arrows:

  ```
  HUB75: DISP0   [C2 ^][C3 ^]
  HUB75: DISP0   [C0 ^][C1 ^]
  ```

  The mistake shows only on the identify screen, where it looks like this: all the text is upside down and every `^` points down, but the `C` and `P` labels are still on the right panels. A wrong arrow word turns a panel's content; it never moves it. Change each arrow word to the direction the arrows actually point (here `ARROW_DOWN`) and run again.

### Example 4: 2x2 serpentine

Four 128x64 ICN2037 panels. The ribbon runs right along the bottom row, up to the top row, then left along the top row. The top row is hung upside down so the ribbon can turn around, so its arrows point down and the bottom row's point up.

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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C2 = hwEnum.ABOVE | hwEnum.C1 | hwEnum.ARROW_DOWN
DISP0_C3 = hwEnum.LEFT_OF | hwEnum.C2 | hwEnum.ARROW_DOWN
```

The picture printed at startup:

```
HUB75: DISP0 wiring: 4 panels in a grid of 2 rows x 2 columns, 256 x 128 pixels (columns x rows)
HUB75: DISP0   [C3 v][C2 v]
HUB75: DISP0   [C0 ^][C1 ^]
HUB75: DISP0 P0 = C3, buffer slot 0, cell row 0 column 0, rotation 180
HUB75: DISP0 P1 = C2, buffer slot 1, cell row 0 column 1, rotation 180
HUB75: DISP0 P2 = C0, buffer slot 3, cell row 1 column 0, rotation 0
HUB75: DISP0 P3 = C1, buffer slot 2, cell row 1 column 1, rotation 0
HUB75: DISP0 cable -> panel position: C0->P2 C1->P3 C2->P1 C3->P0
```

When identify is right: the top row reads `C3` `P0` then `C2` `P1`, the bottom row reads `C0` `P2` then `C1` `P3` (`C0->P2 C1->P3 C2->P1 C3->P0`). All the text is upright and every arrow points up, including the upside-down top row, whose `ARROW_DOWN` words make the driver turn its content.

Common mistakes:

- **The right word, the wrong neighbour.** `C3` is `LEFT_OF` `C1`, which is `C0`'s cell.

  ```
  DISP0_C3 = hwEnum.LEFT_OF | hwEnum.C1 | hwEnum.ARROW_DOWN
  ```

  ```
  HUB75: DISP0_C3: sits in the same cell as C0
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **A typo that names an unused position.** `C4` instead of `C2`; position 4 is `NO_PANEL`.

  ```
  DISP0_C3 = hwEnum.LEFT_OF | hwEnum.C4 | hwEnum.ARROW_DOWN
  ```

  ```
  HUB75: DISP0_C3: names C4 as its neighbour, but that cable position is NO_PANEL
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

### Example 5: 3 across x 2 down

Six 64x32 FM6126A panels (`CHIP_FM6126A`, `ADDR_ABCD`, 64 columns x 32 rows), three across and two down, all upright. The ribbon runs down the left column, across the bottom, up the middle column, across the top, and down the right column: a snake by columns.

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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.BELOW | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C2 = hwEnum.RIGHT_OF | hwEnum.C1 | hwEnum.ARROW_UP
DISP0_C3 = hwEnum.ABOVE | hwEnum.C2 | hwEnum.ARROW_UP
DISP0_C4 = hwEnum.RIGHT_OF | hwEnum.C3 | hwEnum.ARROW_UP
DISP0_C5 = hwEnum.BELOW | hwEnum.C4 | hwEnum.ARROW_UP
```

The picture printed at startup:

```
HUB75: DISP0 wiring: 6 panels in a grid of 2 rows x 3 columns, 192 x 64 pixels (columns x rows)
HUB75: DISP0   [C0 ^][C3 ^][C4 ^]
HUB75: DISP0   [C1 ^][C2 ^][C5 ^]
HUB75: DISP0 P0 = C0, buffer slot 5, cell row 0 column 0, rotation 0
HUB75: DISP0 P1 = C3, buffer slot 2, cell row 0 column 1, rotation 0
HUB75: DISP0 P2 = C4, buffer slot 1, cell row 0 column 2, rotation 0
HUB75: DISP0 P3 = C1, buffer slot 4, cell row 1 column 0, rotation 0
HUB75: DISP0 P4 = C2, buffer slot 3, cell row 1 column 1, rotation 0
HUB75: DISP0 P5 = C5, buffer slot 0, cell row 1 column 2, rotation 0
HUB75: DISP0 cable -> panel position: C0->P0 C1->P3 C2->P4 C3->P1 C4->P2 C5->P5
```

When identify is right: reading across the top row you see `C0P0`, `C3P1`, `C4P2`, and across the bottom row `C1P3`, `C2P4`, `C5P5` (`C0->P0 C1->P3 C2->P4 C3->P1 C4->P2 C5->P5`). The panels are small, so identify uses the compact layout, and every arrow points up. The `P` numbers run along the rows while the `C` numbers run along the ribbon, so the two sets of numbers disagree on four of the six panels; that is correct.

Common mistakes:

- **`FIRST_PANEL` copied onto a second panel.** `C3` written as a copy of `C0`'s line.

  ```
  DISP0_C3 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C3: uses FIRST_PANEL, which belongs only to C0; write direction | neighbour | arrow
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **A sideways arrow on non-square panels.** On panels that are not square, every arrow must be vertical or every arrow must be sideways.

  ```
  DISP0_C4 = hwEnum.RIGHT_OF | hwEnum.C3 | hwEnum.ARROW_LEFT
  ```

  ```
  HUB75: DISP0_C4: has its arrow at right angles to C0's arrow; on panels that are not square, every arrow is ARROW_UP or ARROW_DOWN, or every arrow is ARROW_LEFT or ARROW_RIGHT
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C2 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C3 = hwEnum.ABOVE | hwEnum.C2 | hwEnum.ARROW_UP
```

The picture printed at startup (a cell with no panel prints as `  --  `):

```
HUB75: DISP0 wiring: 4 panels in a grid of 3 rows x 2 columns, 128 x 192 pixels (columns x rows)
HUB75: DISP0   [C3 ^]  --  
HUB75: DISP0   [C2 ^]  --  
HUB75: DISP0   [C0 ^][C1 ^]
HUB75: DISP0 P0 = C3, buffer slot 0, cell row 0 column 0, rotation 0
HUB75: DISP0 P1 = C2, buffer slot 1, cell row 1 column 0, rotation 0
HUB75: DISP0 P2 = C0, buffer slot 3, cell row 2 column 0, rotation 0
HUB75: DISP0 P3 = C1, buffer slot 2, cell row 2 column 1, rotation 0
HUB75: DISP0 cable -> panel position: C0->P2 C1->P3 C2->P1 C3->P0
```

When identify is right: down the left column you see `C3P0`, `C2P1`, `C0P2` from top to bottom, and `C1P3` to the right of the bottom panel (`C0->P2 C1->P3 C2->P1 C3->P0`). The empty cells stay dark; panel positions count only the cells that hold a panel, so the numbers run `P0` ... `P3` with no gaps. All arrows point up, and the display is 128 x 192 pixels, the size of the whole grid including its empty cells.

Common mistakes:

- **The wrong neighbour.** `C3` written `ABOVE` `C0` instead of `ABOVE` `C2` lands on `C2`'s cell.

  ```
  DISP0_C3 = hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C3: sits in the same cell as C2
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **Two direction words.** Trying to say "diagonal" by writing two directions. A panel touches its neighbour along one full edge, so every sentence has exactly one direction word.

  ```
  DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.ABOVE | hwEnum.C0 | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0_C1: has more than one direction word; use exactly one of ABOVE, BELOW, LEFT_OF, RIGHT_OF
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

### Example 7: the cube, wired in a ring, with Top and Front

Six 64x64 ICN2037 panels (`CHIP_ICN2037`, `ADDR_ABCDE`), all upright, laid out as the cross-shaped net: the four side faces in a row (`C0` ... `C3`, the ribbon left to right), the top face above the second of them, the bottom face below it. `DISP0_CUBE_TOP` is `C4` and `DISP0_CUBE_FRONT` is `C1`.

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

The sentences:

```
DISP0_C0 = hwEnum.FIRST_PANEL | hwEnum.ARROW_UP
DISP0_C1 = hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_UP
DISP0_C2 = hwEnum.RIGHT_OF | hwEnum.C1 | hwEnum.ARROW_UP
DISP0_C3 = hwEnum.RIGHT_OF | hwEnum.C2 | hwEnum.ARROW_UP
DISP0_C4 = hwEnum.ABOVE | hwEnum.C1 | hwEnum.ARROW_UP
DISP0_C5 = hwEnum.BELOW | hwEnum.C1 | hwEnum.ARROW_UP
DISP0_SHAPE = hwEnum.SHAPE_CUBE
DISP0_CUBE_TOP = hwEnum.C4
DISP0_CUBE_FRONT = hwEnum.C1
```

The picture printed at startup. After the cable-to-panel table the driver prints the faces it derived, one line each:

```
HUB75: DISP0 wiring: 6 panels in a grid of 3 rows x 4 columns, 256 x 192 pixels (columns x rows)
HUB75: DISP0     --  [C4 ^]  --    --  
HUB75: DISP0   [C0 ^][C1 ^][C2 ^][C3 ^]
HUB75: DISP0     --  [C5 ^]  --    --  
HUB75: DISP0 P0 = C4, buffer slot 1, cell row 0 column 1, rotation 0
HUB75: DISP0 P1 = C0, buffer slot 5, cell row 1 column 0, rotation 0
HUB75: DISP0 P2 = C1, buffer slot 4, cell row 1 column 1, rotation 0
HUB75: DISP0 P3 = C2, buffer slot 3, cell row 1 column 2, rotation 0
HUB75: DISP0 P4 = C3, buffer slot 2, cell row 1 column 3, rotation 0
HUB75: DISP0 P5 = C5, buffer slot 0, cell row 2 column 1, rotation 0
HUB75: DISP0 cable -> panel position: C0->P1 C1->P2 C2->P3 C3->P4 C4->P0 C5->P5
HUB75: DISP0 cube TOP = C4 (P0, up ^): N->BACK.N E->RIGHT.N S->FRONT.N W->LEFT.N
HUB75: DISP0 cube BOTTOM = C5 (P5, up ^): N->FRONT.S E->RIGHT.S S->BACK.S W->LEFT.S
HUB75: DISP0 cube FRONT = C1 (P2, up ^): N->TOP.S E->RIGHT.W S->BOTTOM.N W->LEFT.E
HUB75: DISP0 cube BACK = C3 (P4, up ^): N->TOP.N E->LEFT.W S->BOTTOM.S W->RIGHT.E
HUB75: DISP0 cube LEFT = C0 (P1, up ^): N->TOP.W E->FRONT.W S->BOTTOM.W W->BACK.E
HUB75: DISP0 cube RIGHT = C2 (P3, up ^): N->TOP.E E->BACK.W S->BOTTOM.E W->FRONT.E
```

Reading a face line: `cube FRONT = C1 (P2, up ^)` says the front face is the panel at cable position `C1`, panel position `P2`, and its up arrow points up in the picture. Then each of the face's four edges, `N`, `E`, `S`, `W`, names the face beyond it and which of that face's edges meets this one: the front's `N` edge meets `TOP`'s `S` edge, its `E` edge meets `RIGHT`'s `W` edge, and so on. Every face line is the same kind of line, and together they list all 12 edges of the cube from both sides.

When identify is right: the identify screen shows the net exactly as the picture shows it. `C4P0` is in the top row above the second panel, `C0P1`, `C1P2`, `C2P3`, `C3P4` run across the middle, and `C5P5` is below the second panel (`C0->P1 C1->P2 C2->P3 C3->P4 C4->P0 C5->P5`). Every arrow points up. The empty cells stay dark. Identify checks the wiring of the net; it does not show the folded cube.

Common mistakes:

- **Not a cube net.** Both `C4` and `C5` placed above the ring: two panels would fold onto the same face.

  ```
  DISP0_C5 = hwEnum.ABOVE | hwEnum.C2 | hwEnum.ARROW_UP
  ```

  ```
  HUB75: DISP0: the panels do not fold into a cube (C4 and C5 fold onto the same face); arrange the six panels as one of the 11 cube nets
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

- **Front opposite Top.** `DISP0_CUBE_FRONT` set to `C5`, the face that lies opposite the top once folded. The front face must share an edge with the top face.

  ```
  DISP0_CUBE_FRONT = hwEnum.C5
  ```

  ```
  HUB75: DISP0_CUBE_FRONT: C5 is opposite the top face (C4) when the panels are folded; the front face must share an edge with the top face
  HUB75: DISP0: 1 wiring problem(s) above; startup stopped
  ```

---

*Questions about a configuration that this guide does not cover? File an issue with your sentences and the startup lines your driver printed.*
