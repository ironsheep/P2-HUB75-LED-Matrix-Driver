# Diagram briefs: THEOPS Figures 1-3 for the 4.0.0 driver

**Date:** 2026-10-09 · **Task:** «#111» · **For:** Stephen, redrawing `hub75-driver-diagrams.graffle` (pages 1 and 2) and replacing `images/BitDepths.png`.

Every term below is a [THEOPS glossary](../../THEOPS.md#glossary) term, with its glossary meaning. Use the words as written there; the glossary is the one place they are defined.

---

## Figure 1: "Panel Arrangement and nomenclature" (`images/hub75-driver-board-layout.png`, graffle page 1)

**Where:** THEOPS.md, *Configuring the driver*. **Reader:** someone about to write their wiring sentences.

### What is out of date

- **Panels are numbered `[1]`..`[4]`.** v4 has two numberings, and the figure must show both: **cable position** `C0`, `C1`, ... (along the ribbon, from the adapter) and **panel position** `P0`, `P1`, ... (reading order as the viewer sees it). They differ whenever the cable does not enter at the top-left.
- **"Data IN / Data OUT" arrows.** In v4 the thing that matters is the **adapter** and where the ribbon goes, so the cable path is the arrow.
- **No panel rotation.** In v4 every panel carries an **arrow** (`ARROW_UP`, `ARROW_DOWN`, ...), its panel rotation.
- **Only full rectangles.** v4 has **cells**, and a cell can be empty (an L shape).
- **Its NOTE says "determining hardware driver values"**: panels per row and column, which no longer exist. The values the user writes now are sentences.
- "Display Rows / Columns" and "Panel Rows / Columns" are still right; keep them.

### The mental image

> **One display is a grid of cells, as the viewer sees it from the front. Each panel sits in a cell, carries an arrow saying which way it is turned, and has two names: where it is on the cable (C) and where it is in reading order (P).**

The reader should come away knowing that they name panels by the **cable** when they write sentences, and the driver numbers them by **reading order** when they draw.

### What to draw

Use **the rig**: a 2x2 in Z order from the bottom-left, Wiring Guide example 3. This is the case where C and P differ, which is the whole lesson. Front view:

```
                 Display Columns 256
   ┌───────────────────────────────────────┐
   ┌──────────────────┐ ┌──────────────────┐   ─┐
   │  C2        P0    │→│  C3        P1    │    │
   │       ▼          │ │       ▼          │    │  Display
   └──────────────────┘ └──────────────────┘    │  Rows 128
          ↑ ribbon back to the left edge         │
   ┌──────────────────┐ ┌──────────────────┐    │
   │  C0        P2    │→│  C1        P3    │    │
   │       ▼          │ │       ▼          │    │
   └──────────────────┘ └──────────────────┘   ─┘
     ↑
   ADAPTER (HUB75_ADAPTER_1 → display DISP0_)
```

Elements, each labelled with its glossary word:

1. **Adapter** at `C0`, labelled `HUB75_ADAPTER_1 → DISP0_` ("adapter *k* drives display *k*-1").
2. **The ribbon path** C0 → C1 → (back along the back) → C2 → C3. This replaces Data IN/OUT.
3. In each panel: its **cable position** (C*n*), its **panel position** (P*n*), and its **arrow** (all ▼ here: the rig hangs upside down, so `ARROW_DOWN`).
4. **Display coordinates origin**: a dot at the display's top-left, labelled `(0,0)`, with row ↓ and column → arrows.
5. **Panel coordinates origin** on one panel, at its top-left *as the viewer sees it*: `(0,0)` in panel coordinates.
6. Brackets: **Panel Columns 128 / Panel Rows 64**, **Display Columns 256 / Display Rows 128** (the existing styling works).
7. A caption box with the four **sentences** for this picture (example 3), so the reader sees picture → sentences:
   ```
   DISP0_C0 = FIRST_PANEL | ARROW_DOWN
   DISP0_C1 = RIGHT_OF | C0 | ARROW_DOWN
   DISP0_C2 = ABOVE | C0 | ARROW_DOWN
   DISP0_C3 = RIGHT_OF | C2 | ARROW_DOWN
   ```

**Second panel group (replaces the 4x 32x32 row):** a small **L shape** (example 6), to show a **cell** with no panel. Three cells up the left side, one to the right of the bottom, and the two empty cells drawn dashed and labelled **cell (no panel)**. Its P numbers run in reading order over the filled cells only: `P0`=C3 top, `P1`=C2, `P2`=C0, `P3`=C1.

### What to leave out

- **Buffer slots.** They are internal (glossary: "configuration and drawing never use them"). They belong in Figure 2 if anywhere.
- **Display rotation.** It is one more frame on top. If you want it, add it as a separate small inset ("display hung turned 90°: `ROT_RIGHT_90`, origin is the top-left *as mounted*"), not in the main picture.
- **The cube.** It has its own section and `DOCs/source/p2-Cube-Layout.graffle`.

---

## Figure 2: "Data flow: image generation" (`images/hub75-driver-data-flow.jpg`, graffle page 2)

**Where:** THEOPS.md, *Notes on driver internals*. **Reader:** someone who wants to know how a drawing call becomes light.

### What is out of date

- **Box 1's note:** "(1) adjusted by overall brightness, (2) gamma corrected, (3) converted to an N-bit PWM index". Brightness is **no longer applied at write**: it is /OE time in the refresh cog. The write does one **color table** read per channel (gamma if enabled, then the depth). The current caption already apologises for this.
- **"Screen buffer is (Display rows × columns) pixels".** It is **panels in use × panel pixels**, stored **panel by panel in buffer-slot order**, not as one display raster. An L shape reserves nothing for its empty cells.
- **"list of PWM buffers".** Now **two frame sets** per adapter. The commit converts into the one **not on display** and posts it; the refresh cog takes the post at its next frame start.
- **The PWM byte detail.** "(Panel rows × columns)/2" is per display now (panels × panel pixels / 2), one byte per column clock, `%00 B2 G2 R2 B1 G1 R1`. The bit layout itself is still right.
- **No startup step.** The **cell address tables**, built once at `display.start()` from the wiring sentences, are now how every drawing call finds its pixels.
- **No scrolling path.** Scrolling regions now move their last frame in the screen buffer.

### The mental image

> **Three stores, two writers, one reader.** Drawing calls write corrected 24-bit color into the **screen buffer** at addresses looked up in the **cell address tables**. A **commit** turns the screen buffer into the idle **frame set** and posts it. The **refresh cog** shows one frame set continuously and swaps to a posted one only at a frame start, so the panels never show half an image.

Two time scales: **startup** (left, once) and **every frame** (right, forever), with the user's draw/commit loop in between.

### What to draw

Left to right, four columns:

```
 STARTUP (once)        DRAWING (your loop)          COMMIT                 REFRESH COG (forever)
 ──────────────        ───────────────────          ──────                 ─────────────────────
 wiring sentences      display call                 commitScreen-          take posted set
 DISPn_C0..C15         (text, line, box,            ToPanelSet()           at frame start
      │                 circle, BMP, scroll)             │                 read brightness
      ▼                     │                            ▼                      │
 display.start()            │ address lookup        convert screen         for each row address
  · check sentences    ┌────▼────────────┐          buffer into the        for each bit plane
  · derive grid ──────►│ cell address    │          IDLE frame set         (MSB first):
  · build tables       │ tables          │               │                 shift row, latch,
  · build color table  └────┬────────────┘          post it ──────────►    pulse /OE 2^k units
      │                     │ color table read                                  │
      ▼                     ▼ (gamma, depth)                                    ▼
 ┌───────────┐        ┌───────────────────┐       ┌──────────────┐        HUB75 → panels
 │color table│        │  SCREEN BUFFER    │──────►│ FRAME SET A  │◄─ on display
 └───────────┘        │  3 bytes/pixel    │       │ FRAME SET B  │◄─ idle (commit writes here)
                      │  panel by panel   │       └──────────────┘
                      └───────────────────┘
```

Elements:

1. **Wiring sentences → `display.start()`**: checks, derives the grid, builds the **cell address tables** and the adapter's **color table**, starts the refresh cog. Mark it "once".
2. **Display call** → **address lookup** (cell address tables) → **color table read** (one per channel: gamma if on, then depth) → **screen buffer**. Annotate: "runs, glyph blocks, lines and circles written in PASM".
3. **Screen buffer** annotation: "3 bytes per pixel (R, G, B) at every depth; panels in use × panel pixels; stored panel by panel".
4. Optional side loop on the screen buffer: **scroll step** "moves its last frame one pixel, draws only the new edge".
5. **Commit** → writes the **idle frame set** → **post**.
6. **Two frame sets**, A and B, one marked *on display* and one *idle*, with a swap arrow labelled "taken at the next frame start".
7. **Frame set** detail (reuse your grey panel): *one frame per bit plane, plane 0 = MSB first; each frame one byte per column clock, `%00 B2 G2 R2 B1 G1 R1`; size = panels × panel pixels / 2 per plane*.
8. **Refresh cog** box: take post → for each row address → for each bit plane: shift, latch, **/OE pulse 2^k units**. Then a side input: **brightness** (`setBrightness()`, 0-256) → shortens the /OE pulse; the slot, and so the refresh rate, stays the same.
9. Output: **HUB75 → panels** (keep your vertical HUB75 box).

### What to leave out

- Converter names (`convertRowPairs()`), `MERGEB`, the four-column grouping. That is Theory of Operations detail.
- The window watch and dirty marking. The one-line scroll annotation is enough at this level.

---

## Figure 3: "Creating a full color frame" (`images/BitDepths.png`)

**Where:** THEOPS.md, below the PWM frame-set paragraph. **Reader:** someone who wants to see the bit planes being lit.

### What is out of date

The capture shows the **old method**: for each color frame, a burst of many equal "single frames". v4 shows **each bit plane once per row address** and lights it for **2^k units of /OE**. The equal-spaced "Single Frame" ticks no longer happen, and the "nBit PWM" trace no longer means what it did. The figure is a logic-analyzer capture, so it is best **re-captured**, not drawn.

### The mental image

> **One refresh = every row address once; at each row address, every bit plane once, MSB first, each lit for twice as long as the next.**

```
 one refresh ───────────────────────────────────────────────────────────────►
 row addr 0                        row addr 1                     ...  row addr S-1
 ├ plane0 ████████ ├ p1 ████ ├ p2 ██ ├ p3 █ ├ plane0 ████████ ├ p1 ████ ...
     /OE 8 units       4         2       1      (4-bit shown)
```

### What to capture (instrument build, `test_hub75_rates.spin2`)

The instrument build has the refresh cog mark its progress on P8-P11 (`isp_hub75_instrument.spin2`). The adapter must be on P16-P31 or P32-P47: an adapter at P0 owns those pins, and the strobes are not driven. Suggested traces, one capture per depth (8, 5, 4, 3, as now):

| Trace | Shows |
|---|---|
| P9, frame start | one refresh (the period = the refresh rate) |
| P10, row start | each row address |
| P11, plane latch | each plane loaded, so N per row address |
| /OE (active low) | the lit time: pulses of 2^(N-1), ..., 2, 1 units |

Zoom so one capture shows **one row address** with all N /OE pulses visibly halving, plus a second zoom-out showing one whole refresh. Label the depth under each, as now. The 3-bit cursor annotation (period and frequency) is worth keeping, on the frame-start trace.

The caption text above the figure already says the right thing: "each plane's lit time is its power-of-2 weight".

---

## Terms used, for the labels

| Say | Not |
|---|---|
| adapter (`HUB75_ADAPTER_1`) | card, chain, HUB75 board (in labels) |
| display (`DISP0_`) | screen, panel set |
| cable position `C0` | panel [1], wire order |
| panel position `P0` | panel index, panel number |
| cell (and an empty cell) | grid slot |
| arrow / panel rotation | per-panel ROT |
| display rotation (as mounted) | rotation (unqualified) |
| bit plane, plane 0 = MSB | PWM buffer *n*, PWM index |
| frame set (two per adapter, one on display, one idle) | list of PWM buffers |
| cell address tables | geometry, wire map |
| color table | gamma/brightness step |
| refresh cog | panel driver, backend |
| commit / post | write PWM buffer |
