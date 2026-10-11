# CONFIG-SIMPLIFICATION sprint plan (re-cut of 4.0.0)

**Goal.** The user states only the essential facts about the hardware they have, and nothing
about hardware they do not have. 4.0.0 is not yet public, so the configuration is re-cut before it
ships: code and every user-facing `.md` updated, certified on the quad (and the road-sign panel),
then re-released. Moving the tag is Stephen's.

**Done means:** every top file compiles with 0 warnings; the self-tests in `test_hub75_rates` and
`test_hub75_cube_fold` pass; the bench visit (§12) passes on the quad and settles the road-sign
scan; every document in the blast radius (below) states the new form; the 4.0.0 ChangeLog is re-cut.

**Status:** plan written 2026-10-10. Every question below is answered.

**Outgoing build: 4.0.0, re-cut** (Stephen, 2026-10-10, sprint start): the tag moves to the
re-cut commit; the ChangeLog 4.0.0 section is rewritten and re-dated.

---

## §0 Decisions (Stephen, 2026-10-10, in conversation)

Derived from first principles: what must the user say so the driver can light the display?

| # | Decision |
|---|---|
| D-1 | One display per adapter. Declared **once per display**: pins, panel type (a canned chip name; `CHIP_MANUAL_SPEC \| flags` stays as the escape hatch for unlisted hardware, and a found need becomes another canned name), panel columns and rows, colour depth. |
| D-2 | **Address lines are derived**, not declared: `log2(panel rows / rows lit per address)`, where rows lit per address is 4 with `SCAN_4`, else 2. Eleven of twelve author configs fit; the road sign (config 12) is settled at the bench (§12). |
| D-3 | **Panels are a list** in cable order, one `LONG` sentence per panel, no fixed length. The count is the list's length. No `NO_PANEL`, no `C0..C15`, no `FIRST_PANEL`, no neighbour words, no 16-panel cap. |
| D-4 | A sentence is `ROW_n \| COL_n \| TOP_x`: the panel's cell (row 0 = top, column 0 = left) and where the panel's own top points, **read from the front off the identify screen**. Fields are named so a sentence reads on its own. |
| D-5 | Orientation words: `TOP_UP`, `TOP_DOWN`, `TOP_LEFT`, `TOP_RIGHT` (replace `ARROW_*`; landscape/portrait names fail on square panels). |
| D-6 | Encoding: row and column are 6-bit fields stored as n+1 (0 means the word is missing, so it is reported); orientation is 4 one-hot bits (missing or doubled is reported); one bit each for the cube marks. A doubled `ROW`/`COL` word (`ROW_0 \| ROW_1` = `ROW_2`; `ROW_1 + ROW_1` = `ROW_3`; a row is stored as n+1 — corrected in «#136») cannot be detected in a field; this is accepted and documented (it usually lands two panels in one cell, which is caught). |
| D-7 | **Identify-first workflow**: cable and mount as you like; write starter sentences `ROW_0 \| COL_k \| TOP_UP` (always valid); run identify; copy each panel's place and arrow from the wall. The back of the panel is never part of the notation. |
| D-8 | **Cube by presence of marks**: `CUBE_TOP` and `CUBE_FRONT` on two sentences mean a cube; none means flat. `DISPn_SHAPE`, `DISPn_CUBE_TOP`, `DISPn_CUBE_FRONT` go. |
| D-9 | **Mounting rotation stays, as an optional override** for re-hanging a built display (the sentences describe it as first built and identified). Words: `AS_BUILT` (default), `TOP_TO_RIGHT`, `TOP_TO_LEFT`, `TOP_TO_BOTTOM`. The guide says to mark the frame's top edge at the first identify; identify is the check after re-hanging. |
| D-10 | v3 aliases `ROT_NONE`, `ROT_LEFT_90`, `ROT_RIGHT_90` are dropped. `ROT_*` remains only for content rotation (BMP placement). |
| D-11 | **Presence and overrides by flag**: the first display needs no flag; `#DEFINE DISP1_PRESENT` / `DISP2_PRESENT` for more; one `#DEFINE` per override used (`DISPn_ROTATED`, `DISPn_REFRESH_GIVEN`). A defaults section supplies empty values for everything not flagged. A ready template block for a second display carries its own flag line. A typical user writes zero flags. |
| D-12 | **Portable features only.** No `#INCLUDE`. Everything (user section, defaults, buffers, per-display tables) lives in `isp_hub75_hwPanelConfig.spin2`. Any pnut-ts-only feature in a driver file is guarded `#IFDEF __PNUT_TS__` (P2KB `p2kbSpin2ExternalSymbols`). No "displays fill in order" check: adapter 3 runs without adapter 2. |
| D-13 | **One piece, for v4**: every panel shares a full edge with the rest. T, L, Z, S and plus shapes are allowed; corner-only contact and gaps are not. This bounds the grid tables from the panel count. |
| D-14 | Stephen's configurations ship as ready-made example blocks in the new form. |
| D-15 | Scope: all code and all `.md`; then the quad bench; then re-release. Taken from the punch list: the ICN2038S scan item (settled at the bench). Declined this sprint: the rest of the punch list. Not in scope: the 512-byte line buffer (still caps one chain at 512 columns). |

Construction fact recorded: the road-sign panel (ICN2038S) is single-ended and cannot daisy-chain.

### Standing rulings that bear on this sprint (`.claude/doctrine-overlay.md`)

- 2026-10-08: public code is the exemplar; the style guide holds without convenience exceptions.
- 2026-10-08: find why a structure evolved before changing it (the neighbour grammar: its one-hot
  words existed to catch `+` carries; D-6 keeps that for orientation and accepts the field loss).
- 2026-10-03: assume the driver API is sufficient until a real use proves otherwise (D-9 keeps the
  override in config rather than adding a runtime rotation call).
- 2026-10-09: users' needs shape the API; demos only show it.
- 2026-10-07: when performance is in play, take the whole fix; every risk is named beside the test
  that covers it (§4 hot-path note).
- 2026-10-08: central is not edited from here; the OBEX upload is Stephen's and is not tracked.

### Premises measured (scratch compiles, pnut-ts, 2026-10-10)

| Premise | Result |
|---|---|
| A DAT list's length sizes a DAT buffer in the same object: `LONG 0[((end - start) / 4) * ...]` | compiles; empty list gives a zero-length buffer |
| A CON cannot count a DAT list | `error: Undefined symbol` (so all sizing is in DAT) |
| `#IFNDEF` around `CON` and `DAT` supplies defaults in the same file | compiles; other objects see the constant |
| Override value without its flag | `Expected a unique constant name, "#", or STRUCT (m210)` at the value (prototype); **re-measured on the real file in «#131»: `Symbol is already defined (m541)` at the default's line** (the default follows the user section) |
| Override flag without its value | `Expected an object constant, structure, or method` **in the consuming object** |
| `DISP1_PRESENT` without a DISP1 block | `Undefined symbol` at the buffer line |
| `#IFDEF __PNUT_TS__` guarded `#ERROR` | fires under pnut-ts |

### Entry baseline (measured 2026-10-10 on 6e804ba)

- All 18 top files: `pnut-ts -d -l -m <file>` exit 0, 0 warnings.
- Tree: clean except the untracked `DOCs/analysis/2026-10-09-CENTRAL-DOCTRINE-RECOMMENDATION.md`
  (commit on Stephen's word) and this plan.
- Driver DEBUG data: `demo_hub75_text` plain `.bin` 406,540 bytes, `-d` 416,028, delta **9,488**
  (`pnut-ts demo_hub75_text.spin2` then `pnut-ts -d ...`, sizes by `stat -f%z`). §4 must not raise it.
- Doc audit: clean (see Documentation Blast Radius).
- Tracking readiness (entry): 6 completed tasks archived (`tasks/archives/archive_20261010_165759.md`);
  no pending or in-progress tasks; superseded context key `resume_after_display_org` deleted;
  project-state memory superseded. Verdict: **ready**.

---

## §1 Enumerations (`driver/isp_hub75_hwEnums.spin2`)

**Why:** the words are the user's vocabulary (D-4..D-10).

**Starting point:** wiring words at `:158-225` (`C0..C15` bits 0-15, `ABOVE..RIGHT_OF` 16-19,
`ARROW_*` 20-23, `FIRST_PANEL` 24, `NO_PANEL` 25, masks 221-225); `SHAPE_*` `:232`; `ROT_*` and
aliases `:45-56`; `ADDR_*` `:110-120`; chips and flags `:60-109`.

**Target:**
- Remove `C0..C15`, `ABOVE/BELOW/LEFT_OF/RIGHT_OF`, `ARROW_*`, `FIRST_PANEL`, `NO_PANEL`, their
  LSBs and masks, `SHAPE_FLAT/SHAPE_CUBE`, and the `ROT_NONE/ROT_LEFT_90/ROT_RIGHT_90` aliases.
- Add the panel-sentence words: `ROW_0..ROW_62` (field 6 bits, value n+1), `COL_0..COL_62`,
  `TOP_UP/TOP_DOWN/TOP_LEFT/TOP_RIGHT` (one-hot), `CUBE_TOP`, `CUBE_FRONT` (one bit each), with the
  field LSBs and masks named. Bit layout: row 0-5, column 6-11, top 12-15, cube marks 16-17.
- Add the mounting words `AS_BUILT`, `TOP_TO_RIGHT`, `TOP_TO_LEFT`, `TOP_TO_BOTTOM`, as values
  disjoint from every sentence bit, so one used in a sentence is reported as "bits no word uses".
- `ADDR_*` stays as the internal quantity the refresh core uses; it is no longer a user word.
- Comment blocks rewritten for the new words (`:158-171`, `:208`).

**Conformance:** `central:spin2-authoring-guide`; `python3 tools/check_style.py`.

**Verify:** normal: the example sentences compile; edge: `ROW_62 | COL_62` fits; error: a sentence
with a mounting word in it is reported at startup (§4).

## §2 The configuration file (`driver/isp_hub75_hwPanelConfig.spin2`)

**Why:** D-1, D-3, D-11, D-12, D-14.

**Starting point:** three full DISPn blocks `:63-239`; derived constants `:243-330`
(16-term panel-count sums `:259-327`).

**Target layout, top to bottom:**
1. Header and a short how-to (identify-first, D-7; link to the Wiring Guide; the compile-error
   table from §0 "Premises measured").
2. **User section:** the DISP0 block (pins, chip, panel columns and rows, depth, then the DAT panel
   list `disp0Panels` .. `disp0PanelsEnd`) for the author's quad. A commented template block for a
   second display that carries `#DEFINE DISP1_PRESENT`. The example set (D-14) is in
   `DOCs/AuthorTestConfigurations.md` (§10), not in this file.
3. **Defaults section (not edited):** `#IFNDEF DISPn_ROTATED` gives `DISPn_ROTATION = AS_BUILT`;
   `#IFNDEF DISPn_REFRESH_GIVEN` gives 60 Hz; `#IFNDEF DISP1_PRESENT` / `DISP2_PRESENT` gives the
   absent display's constants (zero sizes) and an empty panel list.
4. **Storage section (not edited):** per display, the screen buffer and both PWM frame sets sized
   from `(dispNPanelsEnd - dispNPanels) / 4` x panel pixels; and the per-display layout tables
   (§4) sized from the same count: per-panel BYTE tables (count entries) and the grid tables
   (cells = ((N + 2) / 2) x ((N + 1) / 2), the one-piece bound, D-13).
5. Accessors: `PUB` methods returning each display's panel-list address and count, and its buffer
   and table addresses. These replace `hwBuffers.adapterPtrs` and the descriptor's size fields.

**Derived constants removed:** `DISPn_PANEL_COUNT`, `DISPn_SCRN_SIZE_IN_*`,
`DISPn_PWM_FRAME_SIZE_IN_*`, `DISPn_FRAMESET_SIZE_IN_LONGS` (sizes become DAT expressions; the
runtime sizes are computed by the accessors from the count). `DISPn_PANEL_ADDR_LINES` removed (D-2).

**Integration:** `test_hub75_oe_bcm` reads `user.DISP0_ADAPTER_BASE_PIN` at compile time
(`:110-112`); that constant stays.

**Verify:** normal: the quad config compiles and sizes buffers to 4 panels; edge: DISP1 present with
one panel; a display at 6-bit depth; error: each row of the §0 compile-error table reproduced once
in a scratch copy and its message recorded for the guide.

## §3 Retire `driver/isp_hub75_hwBuffers.spin2`

**Why:** the buffers must sit in the object that holds the list (§2). Its only consumer is
`hwBufferAccess:302` (`scrnBuffers.adapterPtrs`).

**Target:** delete the file; `hwBufferAccess` takes the addresses from the config accessors. The
guard longs (`sigFront`, `sigBack`, `sigBack1`) move with the DISP0 buffers. `BUFFER_SLOT_*` go
with the file (no other user).

**Verify:** grep shows no `hwBuffers` / `scrnBuffers` reference; every top file compiles.

## §4 Decode, checks and tables (`driver/isp_hub75_hwBufferAccess.spin2`)

**Why:** D-3..D-9, D-13; the 16-position machinery goes.

**Starting point:** `configureAdapter` `:240-309`; `checkAndDeriveLayout` `:1407`;
`checkSentences` `:1447`; `checkOneSentence` `:1504-1574`; `checkArrowAxes` `:1475`;
`checkPanelLimit` `:1594`; `checkShape`/`checkCubeFace` `:1622-1688`; `placePanels` `:1705`;
`buildLayoutTables` `:1767`; `buildMountedTables` `:1840`; `buildCellAddressTables` `:1948`;
DAT tables `:1318-1405`; `MAX_CABLE_POSITIONS` `:43`, `CONVERTER_MAX_PANELS` `:46`,
`MAX_GRID_CELLS` `:1286`; `testRelayout` `:1179-1246`; `getDriverFlags` `:1076-1105`.

**Target:**
- Read each display's panel list and count through the config accessors.
- **Pass 1, per sentence:** bits no word uses (also catches a mounting word or `+` misuse that
  sets stray bits); row missing; column missing; orientation missing or more than one.
- **Pass 2, the whole list:** two panels in one cell; panels not one piece (flood fill over
  shared edges); non-square panels turned both upright and sideways (today's `checkArrowAxes`,
  reference = the first panel in the list); panel count over the line-buffer limit; panel width not
  a multiple of 4; cube marks: zero, or exactly one `CUBE_TOP` and one `CUBE_FRONT` on different
  sentences; a cube needs 6 square panels; fold checks (unchanged in `cube.foldNet`); mounting
  override not one of the four words; derived address count not 8, 16 or 32.
- **Removed checks:** `FIRST_PANEL` rules, direction and neighbour word counts, self-neighbour,
  neighbour-is-`NO_PANEL`, the `+` carry into `ABOVE`/`ARROW_UP`, gap in numbering, connects-to-C0,
  `DISPn_SHAPE` value, "names C<j> but NO_PANEL".
- **Grid origin is normalised** (minimum row and column become 0, as `buildLayoutTables` already
  does with `minRow`/`minCol`); not an error.
- `placePanels` (the neighbour walk) is deleted; `cableCellRow/Column` are filled directly from the
  sentences.
- **Tables:** every table indexed `layoutIdx * MAX_CABLE_POSITIONS` or `* MAX_GRID_CELLS` is
  reached through the per-display table addresses from §2. `MAX_CABLE_POSITIONS`,
  `CONVERTER_MAX_PANELS` and the fixed `wiringSentences`, `cubeSettings`, `savedSentences` tables go.
  The panel limit becomes the line-buffer limit alone. `PICTURE_LINE_BYTES` is sized for the widest
  grid the line buffer allows.
- **Hot path:** `mountedPixelRun`, `mountedBlockRun`, `plotContext`, `pixelAddressAtRC` and
  `positionAtDisplayPixel` read the cell tables. Changing a direct DAT index to a table base read
  once per call must not slow drawing: measured before and after with `test_hub75_rates`'s draw
  times (the «#109» workload), and the change is redesigned if any draw time rises.
- Address lines: `addressLines()` returns the derived value (D-2); the descriptor field is filled
  at `configureAdapter` from chip flags and panel rows.
- `getDriverFlags`: MBI5124GP no longer ORs `CHIP_UNK_LAT_END_ENCL` (a chip-byte value) into its
  flags; its flags are spelled as flags only.
- Messages: the new catalogue is written to the Wiring Guide's table (§10) with exact text; the
  total `debug()` text of the startup checks does not grow (constraint from the punch-list
  footprint item; measured as the `-d` minus plain `.bin` size of `demo_hub75_text` before and
  after).
- `testRelayout(nChainIdx, pSentences, count, eMounting)` takes a panel list; it still refuses a
  cube and a second relaid adapter.

**Startup catalogue as built («#132», exact text; `n` = display, `k`/`j` = cable position, i.e. place in the list from 0).**
For the Wiring Guide («#136»); each line is produced on the rig at bench run B-7 from its scratch config.

| # | When | Message |
|---|---|---|
| M1 | list length not whole LONGs | `HUB75: DISPn: the panel list is not whole LONGs; write each panel sentence with LONG` |
| M2 | no panels | `HUB75: DISPn: has no panels, so its adapter cannot be started; give it a panel list (and #DEFINE DISPn_PRESENT)` |
| M3 | mounting override not a mounting word | `HUB75: DISPn_ROTATION: must be AS_BUILT, TOP_TO_RIGHT, TOP_TO_BOTTOM or TOP_TO_LEFT` |
| M4 | derived address count not 8/16/32 | `HUB75: DISPn: panels R rows tall, lit L rows per address, need A row addresses; the driver drives 8, 16 or 32` |
| M5 | width not a multiple of 4 | `HUB75: DISPn: panels W columns wide (DISPn_PANEL_COLUMNS) are not supported; the width must be a multiple of 4` |
| M6 | over the line-buffer limit | `HUB75: DISPn: N panels exceed the driver limit of L for panels W columns wide; one row along the cable would be X columns, and the refresh line buffer holds 512` |
| M7 | stray bits | `HUB75: DISPn Ck: has bits that no panel word uses (a mounting word, or words joined with +); join ROW_, COL_ and TOP_ words with \|` |
| M8 | no row | `HUB75: DISPn Ck: has no ROW_ word` |
| M9 | no column | `HUB75: DISPn Ck: has no COL_ word` |
| M10 | top missing or doubled | `HUB75: DISPn Ck: needs exactly one of TOP_UP, TOP_DOWN, TOP_LEFT, TOP_RIGHT` |
| M11 | two panels in one cell | `HUB75: DISPn Ck: is in the same cell as Cj` |
| M12 | not one piece | `HUB75: DISPn Ck: shares no full edge with the panels joined to C0; the panels must form one piece` |
| M13 | non-square panels mixed upright and sideways | `HUB75: DISPn Ck: has its top at right angles to C0's; panels that are not square are all TOP_UP or TOP_DOWN, or all TOP_LEFT or TOP_RIGHT` |
| M14 | cube marks misused | `HUB75: DISPn: a cube marks one panel CUBE_TOP and a different panel CUBE_FRONT; found T CUBE_TOP and F CUBE_FRONT` |
| M15 | cube not 6 panels | `HUB75: DISPn: a cube needs exactly 6 panels, but N are in use` |
| M16 | cube panels not square | `HUB75: DISPn: a cube needs square panels, but each panel is W columns x R rows` |
| M17 | net does not fold (cube.foldNet) | `HUB75: DISPn: the panels do not fold into a cube (Ca and Cb fold onto the same face); arrange the six panels as one of the 11 cube nets` |
| M18 | front opposite top (cube.foldNet) | `HUB75: DISPn Ck: marked CUBE_FRONT, is opposite the CUBE_TOP face (Cj) when the panels are folded; the front face must share an edge with the top face` |
| N1 | notice: override on a cube | `HUB75: DISPn: DISPn_ROTATION does not apply to a cube and is ignored` |
| End | after any of M1-M18 | `HUB75: DISPn: E problem(s) above; startup stopped` |

Order: M1, M2 (then nothing else for that display); M3, M4; M5/M6; only when M5/M6 are clear, M7-M10 per
sentence, then (when those are clear) M11, then M12 when no M11, and M13; M14-M16. M17/M18 run after the
layout is built, only when M1-M16 are clear. Design notes as built: the one-piece walk and the duplicate-cell
check compare the sentences directly (no grid), so a far-flung ROW/COL cannot overrun the tables; the startup
picture wraps at 96 characters instead of sizing a line for the widest grid (a 128-panel list prints several
lines rather than holding a 1.4 KB line buffer).

**Adversarial premise check (sprint-plan overlay):**
- A sentence written `LONG 0` → row and column missing, orientation missing: three messages.
- A mounting word in a sentence → bits no word uses.
- `ROW_1 + ROW_1` → `ROW_3` plus no stray bit: undetectable unless two panels share a cell;
  documented (D-6).
- The list written with `BYTE` or `WORD` instead of `LONG` → count wrong and sentences garbled:
  the per-sentence checks fire; also the list length not a multiple of 4 is reported.
- Non-square panels with one panel sideways → the axes check.
- A cube with marks on 6 square panels laid out as a cross that does not fold (an invalid net) →
  `foldNet` message.
- A grid that is one piece only through a corner → not one piece.
- A 48-row panel → derived address count is not 8, 16 or 32.
- `DISP1_PRESENT` with an empty list → "has no panels".

**Conformance:** `central:spin2-authoring-guide` (single exit, no magic numbers, `''`/`'` docs);
`python3 tools/check_style.py`.

**Verify:** normal: the quad and each author config pass and print their layouts; edge: an L, T, Z
and plus on four or five 64x32 panels (layout tables only, via `testRelayout` in `test_hub75_rates`);
error: each pass-1 and pass-2 message produced once in a scratch config with the exact text recorded.

## §5 Refresh core and the OE test take the derived address lines

**Starting point:** `driver/isp_hub75_rgb3bit.spin2:471-493` (two ladders on `ADDR_*`, `ADDR_UNKNOWN`
falls into ABC); `driver/test_hub75_oe_bcm.spin2:261-268`.

**Target:** both read the derived count from `hub75Bffrs.addressLines()`; no `ADDR_UNKNOWN` path
(the startup check guarantees 8/16/32). `oe_bcm`'s own check `rowAddressCount * scanDivisor ==
panelPixelRows` (`:288`) is now true by construction and is removed.

**Verify:** compile; on the bench every panel type shows a full picture (wrong address count shows
as repeated or missing bands).

## §6 Cube

**Target:** `checkAndDeriveLayout` finds the top and front cable positions as the list indices
carrying `CUBE_TOP`/`CUBE_FRONT`, and passes them to `cube.foldNet` unchanged (its inputs are cell
rows/columns, panel positions, top, front, face size; it never used the sentences). A mounting
override on a cube prints the existing notice. `test_hub75_cube_fold` is unchanged (it drives
`foldNet` directly) and must still pass.

## §7 Identify (`driver/demo_hub75_numberPanels.spin2`)

**Starting point:** `identifyPanels()` `:93-139`; header notes `:16-30`.

**Target:** the drawing is unchanged (C label reaches the cabled panel by buffer slot; the arrow is
turned by the declared `TOP_*`). Header and on-screen notes describe the identify-first workflow
(D-7) and the starter sentences. The program's config comment shows starter sentences.

**Verify (bench):** with starter sentences, each panel shows its cable number and an arrow to its
own top; after copying the wall into the sentences, labels read in order and every arrow points up.

## §8 Tests

- `test_hub75_rates.spin2`: `ownSentences` from the config list; `wideL`/`tallL` layouts as
  `ROW|COL` lists; arrow replacement becomes `TOP_*` replacement; `MAX_CABLE_POSITIONS` uses go;
  `hub75Bffrs.ROT_*` aliases (`:1470-1481`) renamed; add T, Z and plus layouts to the row-run test
  where the panel count allows.
- `test_hub75_converter.spin2`: comment `:141` (converter limit) updated.
- `test_hub75_oe_bcm.spin2`: §5.
- `test_hub75_cube_fold.spin2`: unchanged; must pass.

## §9 Demos and other driver objects

- Demos reference no config words (survey, 2026-10-10); only headers and comments change.
- `isp_hub75_display_bmp.spin2` content rotation keeps `ROT_*`; its re-exported aliases
  `ROT_NONE/ROT_RIGHT_90/ROT_LEFT_90` (`:27-30`) are replaced by `ROT_0/ROT_90/ROT_270` (D-10), and
  every caller updated.
- `isp_hub75_display.spin2` start() doc (`:203`) and `:1706-1707` (shape, rotation notice);
  `isp_hub75_cube.spin2` comments; `hwBufferAccess` header comment (`:20-36`).

## §10 Documentation

The **Wiring Guide is the one canonical copy** of the sentence grammar, the startup catalogue and
the worked examples. Every other document states the minimum and links to it (removes the five
duplicated copies the survey found).

- `DOCs/WiringGuide.md`: rewritten: the identify-first workflow; the sentence words and rules;
  presence and override flags with the compile-error table; mounting override and "mark the top";
  the cube marks; the one-piece rule and what it allows (T, L, Z, plus); limits (line buffer, RAM);
  the new startup catalogue with exact message text; the seven worked examples re-cut with their
  startup pictures re-captured on the bench where the rig allows (examples not runnable on the rig
  are produced by `testRelayout` in a scratch build and say so).
- `README.md`: configuration table, the three example blocks, "Updating from v3.x".
- `THEOPS.md`: file table (hwBuffers row gone), glossary (cable position, panel rotation → panel
  top, display rotation → mounting override, wiring, cube orientation), scan table, limits.
- `Checklist-v3-v4.md`: rewritten for the new form (heaviest change).
- `DOCs/AuthorTestConfigurations.md`: every configuration as a complete block in the new form
  (D-14); config 12 states single-ended and the bench-settled scan.
- `DOCs/MultiPanelConfiguration.md`, `DOCs/TheoryOfOperations.md`, `HardwareTurnon.md`,
  `DOCs/ChipCharacteristicsMatrix.md` (ICN2038S), `DOCs/PSRAMExpansion.md:40`,
  `DOCs/TECHNICAL_DEBT.md`, `DOCs/CodeAssessment.md`: their config statements.
- `CLAUDE.md` (project instructions): architecture paragraph (hwBuffers, sentences, adapters).
- Historical checklists (`Checklist-v1-v2.md`, `Checklist-v2-v3.md`) and `HUB75-Driver-SWver*.md`
  describe past versions and are not changed.

## §11 ChangeLog re-cut (`ChangeLog.md`, `central:changelog-voicing`)

The 4.0.0 section is rewritten to describe the configuration as shipped (no history of the
superseded sentence form, which never reached users): what a v3 user writes now, BREAKING items,
the one-piece and line-buffer limits, the ICN2038S result, the MBI5124GP flag fix. The release date
moves to the re-release date.

## §12 Bench visit (macOS host; dual-agent hand-off)

Earned by: §1-§9 landed and compiling. Each run names the decision it feeds.

| Run | Rig | Decides |
|---|---|---|
| B-1 | quad (4x ICN2037 128x64) with starter sentences, then identify-copied sentences | D-7 workflow works as written; sentences for the quad |
| B-2 | quad: `test_hub75_rates` full workload | no regression in refresh, commit and draw times vs the 4.0.0 baseline (§4 hot path); all self-tests PASS |
| B-3 | quad: mounting override `TOP_TO_BOTTOM` | override turns content without changing sentences |
| B-4 | road sign as `CHIP_ICN2038S` (SCAN_4, 16 addresses) | |
| B-5 | road sign as `CHIP_MANUAL_SPEC` without `SCAN_4` (32 addresses) | B-4 vs B-5: which shows a full correct picture sets `CHIP_ICN2038S`'s flags |
| B-6 | flexspin build of one demo | the label-difference sizing and `#IFNDEF` defaults are accepted (named unknown) |

Hard stops are measurement checks first: a draw-time rise in B-2 is confirmed with a second run
before §4's table access is redesigned.

## §13 Re-release

Compile all top files, 0 warnings; doc audit clean; ChangeLog re-cut; the release zip rebuilt and
checked (12 demos build from it alone, as at 4.0.0). Tag and push are Stephen's.

---

## Documentation Blast Radius

`python3 tools/check_docs.py` at plan time (2026-10-10): `ORPHAN (0)`, `DUPLICATE (0)`, `COUNT (0)`
over 23 documents and 36 sources. It does not see the grammar duplication below; that came from the
survey.

| Changed behaviour | Artifacts that describe it |
|---|---|
| Wiring sentences → panel list | WiringGuide 18-79, 81-108, 321-383, 384-877 (7 examples, their pictures and mistake transcripts); README 96-98, 137, 176-178, 194-318; THEOPS 114-116, 128, 136, 177-193; Checklist-v3-v4 18-85, 156-167, 183, 204-207; AuthorTestConfigurations 5, every block, 137, 372; MultiPanelConfiguration 5, 71-82, 162-169; TheoryOfOperations 389, 397, 476-496; HardwareTurnon 24-25; TECHNICAL_DEBT 11, 25; CodeAssessment 58; hwPanelConfig comments 29-61; hwEnums 158-208; hwBufferAccess and display docstrings |
| Address lines derived | README 170; THEOPS 168-170; hwPanelConfig 17-27; AuthorTestConfigurations blocks; MultiPanelConfiguration 19; ChipCharacteristicsMatrix ICN2038S |
| Cube by marks | README 177-178, 272-318; WiringGuide 144-187, 786-877; THEOPS 144; MultiPanelConfiguration 76-82; Checklist-v3-v4 33, 197; ChangeLog 17; AuthorTestConfigurations 216-219 |
| Mounting override words; aliases dropped | README 98, 175; WiringGuide 110-142; THEOPS 130-132; Checklist-v3-v4 32, 177; TheoryOfOperations 180-182; ChangeLog 21, 41, 64; MultiPanelConfiguration 169 |
| Presence flags (no "always present") | README 137, 161; THEOPS 67, 197; TheoryOfOperations 369, 501; CodeAssessment 35, 58; Checklist-v3-v4 85, 102; AuthorTestConfigurations 374; ChangeLog 63; WiringGuide 73 |
| hwBuffers removed | THEOPS 67; TheoryOfOperations 47, 82, 501; CodeAssessment 7; Checklist-v3-v4 115-120, 190; CLAUDE.md |
| 16-panel cap removed | THEOPS 250; TheoryOfOperations 389; WiringGuide 66-69, 379; PSRAMExpansion 40; Checklist-v3-v4 |
| Startup messages | WiringGuide catalogue 339-367 and every example's mistake transcript; HardwareTurnon 25 |
| Counts | "seven worked examples" (WiringGuide 3, 7, 384; THEOPS 177; Checklist-v3-v4 20; MultiPanelConfiguration 5); catalogue row count; README example count |
| Generated interface docs | `{Spin2_Doc_CON}` blocks in hwEnums, hwPanelConfig, hwBufferAccess |

## Named unknowns

| Unknown | Response when it resolves |
|---|---|
| ICN2038S scan | B-4/B-5 set its flags; AuthorTestConfigurations, ChipCharacteristicsMatrix, ChangeLog and the punch list record the result |
| flexspin acceptance of DAT label-difference sizing | B-6; if refused, the finding goes to Stephen with the exact error (portability is his call, D-12) |
| PNut acceptance | not runnable on either side here; the design uses only features P2KB documents for PNut v47+; stated as untested in the ChangeLog |
| Hot-path cost of table base reads | B-2 before/after; redesign in the same task if any draw time rises |
| Worked examples not buildable on the rig (cube, L, row of 4) | pictures produced via `testRelayout` / a scratch layout build and labelled as such |

## Revisions

(none)

## Tasks (sprint tag `cfgsimp`)

| Plan § | Deliverable | Task | seq |
|---|---|---|---|
| §1-§3 | New words, config form, storage in config, hwBuffers retired | «#131» | 1 |
| §4, §6 | Decode, startup checks, tables sized by N, cube marks | «#132» | 2 |
| §5 | Refresh core and OE test use derived address lines | «#133» | 3 |
| §7, §9 | v3 rotation aliases dropped; identify and demo notes | «#134» | 4 |
| §8 | Row-run test covers T, Z and plus | «#135» | 5 |
| §10 | Wiring Guide, the canonical grammar | «#136» | 6 |
| §10 | Every other user doc | «#137» | 7 |
| §12 | Bench visit B-1..B-8 | «#139» | 8 |
| §11 | ChangeLog 4.0.0 re-cut | «#138» | 9 |
| §13 | Re-release gates and hand-off | «#140» | 10 |

- **Atomic green-unit:** «#131» + «#132». The tops fail to compile between them by design.
- **Dispatch:** the project default, `arbiter-serial`. The core pair and the bench run inline;
  «#134» is task-mechanical; «#135», «#136» and «#137» are task-standard. No task is two-phase:
  the design is fixed in §0.
- **Environment:** «#131»-«#138» and «#140» need only `pnut-ts`; «#139» needs the P2 rig. The doc
  tasks («#136», «#137») run while the quad is busy. The guide's pictures and the ICN2038S result
  are filled in at «#139», so capture comes after the behaviour change.
