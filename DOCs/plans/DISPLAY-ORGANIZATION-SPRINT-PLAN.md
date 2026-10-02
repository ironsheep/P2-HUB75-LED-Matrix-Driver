# DISPLAY-ORGANIZATION — Sprint Plan

**Status:** Started 2026-10-01. Planning concluded the same day with no open
questions. Re-opened 2026-10-02 for one agreed scope change (SC-1, content
rotation): §5b is in planning until its open questions are answered.

**Build:** **4.0.0**, agreed with Stephen at sprint start (2026-10-01). He
chose strict SemVer: the configuration format changes, so every user must
convert their config, and that is a major version. The multi-panel support
being fixed was shipped on `main` under the `[3.0.3]` changelog entry
(`bac1e33`, 2026-06-11). That release was never tagged: the latest tag,
locally and on `origin`, is `v3.0.2`.

**One-line charter:** Give the driver one honest model of how panels form a
display — a vocabulary, a wiring configuration written as sentences, one
mapping that every drawing path goes through, correct whole-display mounting
rotation and a run-time content rotation, and a cube layer whose drawings cross every edge. Fix the three latent defects
that live on the same buffer path.

**What done means:** on the 2×2 rig of 128×64 panels, the identify routine
labels every panel with its cable position (`C`) and panel position (`P`), and
shows `P0..P3` in reading order with every arrow up. The boundary test
draws cleanly across both panel seams. Every drawing path (display-centric,
panel-centric, text, scrolling, mounting rotation, content rotation) lands
where the display coordinates say. The configuration documents describe exactly what the code does. The
items that the rig cannot prove are built, checked as far as the rig allows,
and listed by name for the panel sweep (§13).

---

## Open Questions

The one question raised at plan review was answered 2026-10-01: the fold
self-test is in (§7, item 7).

Open since 2026-10-02, from SC-1 (§5b, content rotation). No task is generated
for §5b until each is answered; each is asked one at a time. Q1 and Q6 are
Stephen's calls; Q2-Q5 are researched first and asked only if the code and
the plan cannot settle them.
- **Q1.** At 90° or 270° on a non-square display, does content rotation change
  the drawing surface's shape (as mounting does), or turn the content inside
  the fixed shape and crop what falls outside?
- **Q2.** How content rotation composes with mounting rotation (mounting
  first, then content).
- **Q3.** What a change at run time does to cached sizes (the display's copied
  rows and columns, the text grid, scroller regions) and to what is already
  drawn: cleared, kept, or redrawn by the program.
- **Q4.** Whether it applies to a cube (mounting rotation does not).
- **Q5.** Its name, signature and value set (for example reusing
  `hwEnum.ROT_*`).
- **Q6.** On a rotated display, does a panel-centric call's panel-local "up"
  turn with the display, or stay fixed to the panel? Raised by «#75»;
  answered after Q1-Q5, because content rotation may shape it.
  *Evidence (2026-10-02, rig, `ROT_RIGHT_90`):* the boundary test's
  panel-centric line on P0 (row 8, running off P0's right edge at `ROT_NONE`)
  came out as a full-height bar along the top panel's left edge. Stephen saw
  it and asked whether it was intended; it is not. `offsetToPanel()` returns
  layout coordinates, but the line is drawn through the mounted (rotated)
  path, so today a panel-centric call under 90/270 lands where neither answer
  to Q6 would put it. Fill is exempt: «#75» gave it a layout-direct path,
  because a fill looks the same at every rotation. Everything display-centric
  was correct (circle, crosshair, border, text).

---

## Agreed scope changes

Scope changes only by agreement between Stephen and the arbiter, reached in
conversation and recorded here at the moment it is reached. Each entry says
what changed, why, which sections and tasks it touches, and what it does
**not** admit. A change that is not in this log is drift, and is raised, not
built.

- **SC-1 — 2026-10-02 — two rotations.** *Agreed:* `DISPn_ROTATION` (the one
  config constant) is **physical**: how the display is mounted. A separate
  **content rotation** is added to the API, in this sprint. *Why:* at the
  bench, Stephen and the arbiter found two measures of "rotate right 90": the
  hardware turned (physical) and the picture turned (image-centric). On a
  fixed rig they give the same picture under opposite names, and the code
  used the image-centric name while the glossary used the physical one.
  Giving each its own home keeps one meaning per setting. *Touches:* §5
  (meaning and direction, applied in «#75»), new §5b (content rotation; a new
  task once its open questions are answered), §9 (the run-time-setter
  sentence), §12 (the guide explains both), Visit A (checks both). *Does not
  admit:* rotating an already-drawn image as a separate operation,
  per-panel content rotation, or animation between rotations.

---

## Rulings this plan rests on

All rulings are Stephen's, given on 2026-10-01 in the planning conversation.
They are quoted or closely paraphrased here.

- **Vocabulary.** Panels are numbered top-left to bottom-right in reading
  order (*panel position*). *Cable position* counts **from the adapter**: C0 is
  the panel the adapter plugs into. The driver's reversed internal order is
  called **buffer slot**. All documentation uses one glossary.
- **The rig.** The ribbon runs adapter → bottom-left → bottom-right →
  top-left → top-right; cable length sets that route. All four panels are
  mounted at 180°, and with `ROT_180` their arrows and labels are upright.
  The hardware is a P2 Edge 32MB with the adapter on P16–P31.
- **Wiring configuration is the sentence form only.** The entry/traversal
  settings and the hand-edited wire tables retire. *"We have to be very
  careful about what can be elements of the sentence and very prescriptive.
  We can't allow confusion in ordering or content."* The grammar was accepted
  as written (§2).
- **Mistakes are caught by a startup check, not at compile time.** *"Startup
  should be fine with an explicit message, so we shut down after the debug
  messages. We want to be as simple as possible."*
- **The cube is in this sprint.** *"The cube is one of our de facto standard
  shapes."* *"Objects that we draw on the cube must be able to cross all
  edges, not just the side edges."* The folding model was accepted.
  *"Pixels are physical. A corner is just three faces meeting."* 3-D
  projection and image mapping go into a **separate image-mapping sprint**.
- **Whole-display rotation is in scope.** *"I can rotate it any way I want
  to... everything drawn to the panel is consistent with that new rotation."*
- **Two rotations, two meanings (2026-10-02).** `DISPn_ROTATION`, the single
  config constant, is **physical**: how the assembled display is mounted, so
  `ROT_RIGHT_90` means the display hangs turned 90° clockwise and the driver
  draws so the content reads upright. **Content rotation** is a separate
  **API member**: the program turns its content at run time. *"We keep the
  display rotation as physical, we make sure we have the content rotation as
  an API member, and both go forward in this sprint... the single config
  constant is physical display, and the API is content."* Content rotation is
  planned in its own section; its design questions are settled there.
- **The three latent defects (§6) are in this sprint.** *"Yes, they have to
  be."* Multiple 1/4-scan panels on one adapter is a **requirement**: *"we
  need to be able to handle multiple 1/4-scan panels."* The guide must
  *"prescribe what the driver limit is for each type of panel."*
- **Adapter naming does not change.** `HUB75_ADAPTER_1..3` counts from 1 on
  purpose, and `DISP0..2` counts from 0. *"Let's not remap this for right
  now."*
- **Multi-adapter setup must get simpler.** *"The challenge for them is the
  startup init when two are cabled."*
- **Order of work.** All driver work happens on the 2×2 rig, first in this
  sprint and then in the draw-path performance sprint. After that comes a
  panel sweep, hardest panel first, and a final gate of quick tests across
  every adapter and display.
- **No black holes.** *"Once we get to a panel that we don't understand and we
  can't find a rapid solution for fixing it, we will drop that panel set and
  support just the single panel, like we have in the past."*
- **Documentation examples.** A row of 4, two panels, a 2×2 in Z order (the
  rig), a 2×2 in serpentine order, a 3-across × 2-down grid, an L shape and
  the cube. Each example has the same five parts.

## Relationship to other work

- **Precedes `DRAW-PATH-PERFORMANCE-SPRINT-PLAN.md`.** That plan optimises
  `displayToPanelCoords` and `panelPixelOffset`. This sprint replaces both
  functions, so its *Measured structural delta* (method calls per pixel) must
  be re-measured against this sprint's code before that sprint is tasked.
  Optimising first would optimise a mapping that is being thrown away.
- **Supersedes `Sprint-2x2-Panel-Repair.md`** (January 2026, still marked "In
  Progress"). Its three-tier orientation model (lines 64-96) becomes this
  plan's vocabulary. Its **wire-order** symptoms (B, D, E, F, G at lines
  266-304) are the column-swap workaround that §4 removes. Its flashing
  symptom (A, line 245) and its MSB-frame symptom (H, line 250) are not wiring
  problems, so they stay with the flicker task «#67».
- **Feeds the panel sweep** (§13). The sweep is the next plan after
  draw-path performance.
- **Feeds the future image-mapping sprint.** That sprint will pair the 3-D
  projection add-on API with mapping images onto the cube faces. It depends on
  the face coordinates and the "up" conventions that §7 fixes and documents as
  stable.

## Entry baseline (measured 2026-10-01, macOS)

| Check | Command | Result |
|---|---|---|
| Tree | `git status --short` | clean (`*.bin` and `driver/logs` are ignored, `.gitignore:66,77`) |
| Compile, 13 top files | `TEST_COMMAND` (`pnut-ts -d -l -m` over every `demo_hub75_*`, `isp_hub75_anlyCheck`, `test_hub75_pin_identify`) | 13 pass, 0 fail, 0 warnings |
| Style gate | `python3 tools/check_style.py` | exit 0; 7 checked rules all PASS; 19 T1 rules reported NOT CHECKED |
| Doc audit | `python3 tools/check_docs.py` | 21 docs, 29 sources: ORPHAN 0, DUPLICATE 0, COUNT 0 |
| Hardware | headless run of `demo_hub75_quadPanel` (`driver/logs/headless_261001-170200.log`) | download ok; the log shows `Wire order: W0->D0 W1->D1 W2->D2 W3->D3` (identity) |

### Sprint-start record (2026-10-01)

- **Build number:** 4.0.0 (see Status).
- **Working tree:** clean, except this plan file, which is new and not yet
  committed. It is committed under `DOCs/plans/`.
- **Tracking readiness (entry):**
  - **Ready.**
  - One pending task, «#67» (C1 flicker), stays outside this sprint as
    agreed in planning.
  - Shape counts over the live tasks (1): gist ≤ 60 characters 1/1; single
    tag 0/1; priority unset 0/1; `attention:` 1/1. «#67» was created before
    this plan, so that is a backlog observation.
  - Context: 32 stale keys deleted after a backup
    (`tasks/backups/project_dump_20261001_180659.json`).
    - 27 were from the January 2026 2×2-repair work. Their durable content
      is already in `Sprint-2x2-Panel-Repair.md` and
      `Sprint-Performance-Upgrade.md`.
    - 5 were this sprint's planning notes, now held by this plan.
  - Kept: `sweep_green_panel_research`, plus one live pointer,
    `sprint_resume_display_org`.
  - Auto-memory is empty.
- **Baseline health (entry), measured on macOS (the canonical environment):**
  - **The gate is a stand-in.** There is no automated test suite, so the
    compile-all sweep (`TEST_COMMAND`) is the gate, and a failure means an
    object that won't compile.
  - **Result:** 13 of 13 top files compiled, 0 failures, **0 warnings**. The
    full log was captured to a file and searched for warnings, not just its
    tail.
  - **Not swept:** `driver/isp_dummy_flash.spin2`. It is a standalone top
    file (the flash image that prints `* Hi! from FLASH *`). No file includes
    it and the sweep's file pattern doesn't match it. Compiled separately it
    is clean. Its header names a different file
    (`demo_dual_motor_rc.spin2`, "R/C driving of a two-wheeled platform").
    Stephen decided: add it to the sweep and correct the header (§10).
  - **A green compile proves nothing about behaviour.** Behaviour on hardware
    is verified in the §13 bench visits.
  - No failure groups, so there are no fix-when decisions.

## Premises measured during planning

- **The wire table is always the identity.** The startup log line above shows
  it, and the code says so: `wirePositionToGridCoords`
  (`isp_hub75_hwBufferAccess.spin2:1015`) is documented and written as an
  identity mapping. The entry/traversal settings reach only
  `needsPanelColumnSwap`.
- **The screen buffer is stored panel by panel, in buffer-slot order.**
  `panelPixelOffset` (`isp_hub75_hwBufferAccess.spin2:781`, offset =
  slot × panel bytes + …). The 1/2-scan converter reads it the same way
  (`isp_hub75_panel.spin2:464-467`).
- **Buffer slot 0 is the far end of the cable.** The data is shifted out
  slot 0 first. The table's own comment (`isp_hub75_hwBufferAccess.spin2:121-123`)
  says *"Adapter->BL->BR->TL->TR … Wire 0 = TR (far end)"*. This matches the
  observed labels: P0 appeared top-right.
- **The sentence encoding works on the P2.** A scratch prototype was compiled
  with `pnut-ts` and run headless on the rig (exit 0, `END_SESSION`). The
  results:
  - parts joined with `|` decode the same in any order;
  - a compile-time `?:` sum counts the panels in use;
  - the startup decode reported a deliberate two-direction mistake.

  Two lessons from it: `word` is a reserved name, and the decoder must count
  the neighbour bits **before** converting them with `encod`, because an empty
  field converts to C0.
- **An unused adapter's buffers can be zero length.** `LONG 0[0]` compiles,
  and a zero-length buffer adds 0 bytes, compared with 400 bytes for 100
  longs (scratch test).
- **Compile-time messages cannot be conditional.** `#error "text"` works but
  can't be tied to a value, and `#if` is not supported (*"use #ifdef or
  #ifndef"*). This is why the checks run at startup.
- **Symbol names are capped at 30 characters** (`pnut-ts`: *"Symbol exceeds
  30 characters"*). The longest name planned is `DISPn_CUBE_FRONT`.

---

## §1 Vocabulary and glossary

**Why.** The code, the comments and the docs currently use "wire",
"chain", "panel index" and "display panel" for several different things. The
order the panels lit up on the rig was taken to be the cable order, but it
was really the buffer-slot order. Every later section is written in this
vocabulary, so it comes first. Settle the standard before applying it.

**Deliverable.** One glossary section in `THEOPS.md` (the `SPEC_DOC`).
Every other document links to it rather than redefining terms.

| Term | Meaning |
|---|---|
| **adapter** | the HUB75 adapter card. IDs are `HUB75_ADAPTER_1..3` (counting from 1). **Adapter *k* drives display *k*−1.** |
| **display** | all the panels on one adapter, drawn on as one surface. Its config group is `DISPn_` (counting from 0). |
| **display coordinates** | (row, column) on the display, with the origin at the top-left. For a rotated display the origin is the top-left of the display **as mounted**. |
| **panel position** | a panel's place in the display, numbered in reading order (top-left to bottom-right, over the cells that hold a panel), `P0..` |
| **panel coordinates** | (row, column) within one panel, as the viewer sees it |
| **cable position** | a panel's place along the ribbon, counted from the adapter: `C0` is the panel the adapter plugs into |
| **buffer slot** | the driver's internal order. Slot 0 is the far end of the cable, so slot = N−1−C. Used only in the mapping layer and its comments. |
| **native coordinates** | a pixel as the panel's own chips address it, before panel rotation |
| **panel rotation** | how one panel is mounted within the display, written as the direction its identify arrow points |
| **display rotation** | how the whole assembled display is mounted (`DISPn_ROTATION`, flat displays only) |
| **wiring** | the per-panel sentences `DISPn_C0..C15` (§2) |
| **face**, **cube orientation**, **face coordinates** | the cube vocabulary (§7) |
| **scan** | one name for what the code calls `SCAN_4` / `bScan_1_4` and the docs call "1/8 scan". `AuthorTestConfigurations.md` and `ChipCharacteristicsMatrix.md` say "1/8" while the code says "1/4". The glossary picks one term, defines it by how many rows are lit at once, and every document uses it. |

**Integration.** Code comments that use the old words are rewritten in the
sections that touch that code. They are not swept separately. This includes
the `hwBufferAccess` table comments (`:111-123`) and the "W0..W3" debug
labels.

**Verify.**
- *Normal:* every term in the table appears in the glossary with exactly one
  definition.
- *Edge:* grep the docs and code comments for `wire order`, `display panel`
  and `chain position` used in the old sense. Each hit is rewritten in the
  section that owns that file, or listed under §12.
- *Error:* none. This section adds documentation only.

## §2 The sentence configuration

**Why.** Wiring is described today by two mechanisms that don't know about
each other: the entry/traversal settings and the hand-edited tables. Neither
reaches the mapping. Neither can express a missing panel or the cube. They
are replaced with one mechanism, per Stephen's ruling.

**Starting point.**
- `isp_hub75_hwPanelConfig.spin2`:
  - `DISPn_MAX_PANELS_PER_ROW` / `_PER_COLUMN` (:52-53, :122-123, :174-175);
  - `DISPn_WIRE_ENTRY` / `_TRAVERSE` (:71-72, :134-135, :186-187);
  - `DISP0_PANEL0..3_ROT` (:79-82; DISP1 and DISP2 have none);
  - the sizes derived from the bounding box (:86-104 and their DISP1/DISP2
    twins).
- `isp_hub75_hwEnums.spin2`: the `WIRE_*` enums (:122-133).

**Target.**
1. **The words**, in `isp_hub75_hwEnums.spin2`. Each kind of word occupies its
   own bits and each word is one bit, so that joining two words of the same
   kind is always detectable.
   - neighbours `C0..C15`: bits 0-15;
   - directions `ABOVE BELOW LEFT_OF RIGHT_OF`: bits 16-19;
   - arrows `ARROW_UP ARROW_DOWN ARROW_LEFT ARROW_RIGHT`: bits 20-23;
   - `FIRST_PANEL`: bit 24;
   - `NO_PANEL`: bit 25;
   - masks for each field.

   The shape words `SHAPE_FLAT` and `SHAPE_CUBE` sit in a separate enum.
2. **The settings**, per adapter, in `isp_hub75_hwPanelConfig.spin2`:
   - `DISPn_C0 .. DISPn_C15`, one sentence each;
   - `DISPn_SHAPE`;
   - `DISPn_CUBE_TOP` and `DISPn_CUBE_FRONT`, used only when `SHAPE_CUBE`
     (§7);
   - unchanged: panel size (`DISPn_MAX_PANEL_COLUMNS/ROWS`), chip, address
     lines, base pin, colour depth and `DISPn_ROTATION`.

   The grammar, which Stephen accepted as written:
   - **Three forms.**
     - `FIRST_PANEL | arrow` is for `C0` only.
     - `direction | neighbour | arrow` is for every other panel in use.
     - `NO_PANEL` is for unused positions.
   - **Five rules.**
     1. Join the words with `|` only, never `+`, in any order.
     2. The neighbour shares a full edge with this panel. It may come earlier
        or later in the cable.
     3. Every panel connects back to `C0` through its neighbours.
     4. No two panels share a cell.
     5. Panels in use are numbered `C0, C1, …` with no gaps, and `NO_PANEL`
        comes only after the last one.

   A comment block above the settings states the forms and rules, and says
   explicitly why `+` is forbidden: `C2 + C2` silently becomes `C3`.
3. **Compile-time panel count:**
   `DISPn_PANEL_COUNT = Σ (DISPn_Ck <> NO_PANEL ? 1 : 0)`. This is the only
   value computed from the sentences at compile time.
4. **Buffers sized by panel count.** These replace the bounding-box sizes at
   `isp_hub75_hwPanelConfig.spin2:94-104` and their twins.
   - `DISPn_SCRN_SIZE_IN_LONGS` = panel count × panel pixels × bytes per
     colour, rounded up.
   - `DISPn_PWM_FRAME_SIZE_IN_BYTES` = panel count × panel pixels / 2.
   - `DISPn_FRAMESET_SIZE_IN_LONGS` follows from those two.

   An adapter whose `C0` is `NO_PANEL` gets zero-length buffers.
5. **Nothing is enabled by commenting code in or out any more.** The DISP1
   and DISP2 blocks stay live permanently in all three places:
   - `isp_hub75_hwBuffers.spin2:54-57, 65-68, 94-110` (buffers and
     `chain1Ptrs` / `chain2Ptrs`);
   - `isp_hub75_hwBufferAccess.spin2:72-95, 101-102` (descriptor entries and
     their pointers);
   - the DISP1/DISP2 config groups, which default to `NO_PANEL`.
6. **Removed:**
   - `DISPn_MAX_PANELS_PER_ROW/COLUMN` (the grid is now derived at startup,
     §3);
   - `DISPn_WIRE_ENTRY/TRAVERSE` and the `WIRE_*` enums;
   - `DISP0_PANELk_ROT`;
   - the `disp0..2WireOrder` and `disp0..2PanelRots` tables and their pointer
     tables (`isp_hub75_hwBufferAccess.spin2:111-172`);
   - the descriptor fields `ENTR_WIRE_START_OFST` /
     `ENTR_WIRE_TRAVERSE_OFST`.

   Delete what is superseded in the same change.
7. **The rig's own config:**

   ```
   DISP0_C0 = FIRST_PANEL | ARROW_DOWN
   DISP0_C1 = RIGHT_OF | C0 | ARROW_DOWN
   DISP0_C2 = ABOVE | C0 | ARROW_DOWN
   DISP0_C3 = RIGHT_OF | C2 | ARROW_DOWN
   ```

   with `C4..C15` set to `NO_PANEL`. Today's `ROT_180` corresponds to
   `ARROW_DOWN`.

**Conformance.** `central:spin2-authoring-guide` applies to every `.spin2`
edit. The done condition includes `STYLE_GATE_COMMAND`
(`python3 tools/check_style.py`) and a compile of all 13 top files with zero
warnings. Note the authoring guide's rule that object constants are
referenced through their object prefix: the sentences are written
`hwEnum.RIGHT_OF | hwEnum.C0 | hwEnum.ARROW_DOWN`. This form was proven in
the prototype.

**Verify.**
- *Normal:* the rig config compiles, and `DISP0_PANEL_COUNT` = 4. Compare
  the buffer sizes in the `.map` file (`pnut-ts -m`) with the arithmetic:
  4 × 128 × 64 × 3 bytes = 98,304, which is the same as today, because the
  2×2 bounding box has no empty cells.
- *Edge:* a config with DISP1 at `NO_PANEL` produces zero-length DISP1
  buffers. Confirm the size in the `.map` file.
- *Error:* none at this layer. Mistakes in the sentences are caught in §3.

## §3 Startup: decode, check, derive, and one call per adapter

**Why.** The sentences have to become a layout. Every mistake must stop the
program with a message that names it. And starting a second adapter today
takes about nine comment edits across two files, plus four calls.

**Target.**
1. **Decode and check**, inside the adapter's startup. Each check prints one
   debug line naming the setting and the problem, then halts after all the
   messages, so several mistakes are reported in one run. The message
   catalogue is part of the deliverable and is reused in the guide's mistakes
   sections (§12). The checks:
   - more than one word of a kind;
   - a required word missing;
   - `FIRST_PANEL` on anything other than `C0`;
   - `C0` not `FIRST_PANEL` while panels are in use;
   - a panel used as its own neighbour;
   - the neighbour is a `NO_PANEL`;
   - a gap in the numbering;
   - two panels in one cell;
   - a panel that doesn't connect back to `C0`;
   - more panels than the driver limit (§11);
   - `+` used where `|` was meant, where it can be detected (bits of one kind
     carried into another kind's field);
   - starting an adapter whose config has no panels;
   - the cube settings (§7).
2. **Derive:**
   - each panel's grid cell, by walking the neighbour links out from C0;
   - the bounding box, as a grid size and a pixel size;
   - panel positions, in reading order over the cells that hold a panel;
   - two tables built once at startup:
     - panel position → buffer slot (slot = N−1−C);
     - panel position → panel rotation (from the arrow);
   - the inverse table, for identify (§8).

   The per-pixel path only looks things up in these tables. It does no
   searching, keeping per-pixel cost at or below today's (§4 verify).
3. **Print the derived picture** at startup, one line per grid row. For the
   rig:

   ```
   [C2 v][C3 v]
   [C0 v][C1 v]
   ```

4. **One call per adapter.** The demos' `configure(...)` →
   `setBufferPointers(..., chainNPtrs())` → `start(...)` sequence is folded
   into a single display start call that takes the adapter ID. The buffer
   pointers come from `hwBuffers` by adapter index, so the program never
   names `chain0Ptrs` / `chain1Ptrs`. Each adapter in use gets its own display
   object instance. `setWireConfig()` (`isp_hub75_hwBufferAccess.spin2:274`)
   is deleted.

**Two-phase.** §2 and §3 define the shape that every later section builds on,
so they are planned as **two-phase**. The first dispatch returns the encoding,
the derive tables and the message catalogue, applied to the rig config. The
arbiter reviews them before the rest is built.

**Verify.**
- *Normal:* the rig prints exactly the picture above. Panel positions
  P0..P3 = TL, TR, BL, BR, and buffer slots = 1, 0, 3, 2 respectively
  (C2, C3, C0, C1 reversed).
- *Edge:* the 7 example configs from §12, run headless with no panels
  attached, each print their expected picture. That includes the L shape (a
  hole in the bounding box) and the cube net.
- *Error:* one deliberately wrong config for each check in the catalogue.
  Each one prints its message and halts, and that message and no other is
  the one the guide quotes. These broken configs exist only in this
  verification. They are not committed as demos.

### Startup message catalogue

Written in «#72»; the wiring guide (§12) quotes these lines exactly. The
code is `checkAndDeriveLayout` and the methods below it in
`isp_hub75_hwBufferAccess.spin2`, called from `configure()`.

**How to read it.**
- Every line starts `HUB75: `.
- A message about one sentence names the setting as `DISPn_Ck`. A message
  about the whole display names it as `DISPn`.
- In the text below, `n`, `k`, `j`, `N`, `L`, `W` and `R` stand for numbers
  the driver prints.
- After the last message the driver prints the summary line, then
  `END_SESSION`, and stops every cog.

**Order.** The checks run in two passes, so that one mistake does not set off
a chain of others:
1. Every sentence on its own (rows 1-7, 11, 13 and 14), then the whole
   display (rows 10 and 12). All of these are reported in one run.
2. The walk out from C0 (rows 8 and 9). It runs only when pass 1 found
   nothing, because it needs well-formed sentences.

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
| 10 | more panels than the driver limit (§11) | `HUB75: DISPn: N panels exceed the driver limit of L for panels W columns wide; one row along the cable would be R columns, and the refresh line buffer holds 512` |
| 11 | `+` where `\|` was meant, where detectable | `HUB75: DISPn_Ck: looks like + joined a word to itself and carried into the next kind of word; join the words with \| only, never +` |
| | | `HUB75: DISPn_Ck: has bits that no wiring word uses; join the words with \| only, never +` |
| 12 | starting an adapter with no panels | `HUB75: DISPn: has no panels (every DISPn_C0 .. DISPn_C15 is NO_PANEL), so its adapter cannot be started` |
| 13 | a word the form does not allow (added in «#72») | `HUB75: DISPn_C0: takes only FIRST_PANEL and an arrow; remove its direction and neighbour words` |
| | | `HUB75: DISPn_Ck: joins NO_PANEL with other words; NO_PANEL stands alone` |
| 14 | on panels that are not square, arrows that mix sideways with upright (added at the «#72» review) | `HUB75: DISPn_Ck: has its arrow at right angles to C0's arrow; on panels that are not square, every arrow is ARROW_UP or ARROW_DOWN, or every arrow is ARROW_LEFT or ARROW_RIGHT` |
| — | summary, after any of the above | `HUB75: DISPn: K wiring problem(s) above; startup stopped` |

Notes on the table:
- **Row 10** fires on the line-buffer limit. The converter limit
  (`CONVERTER_MAX_PANELS`, 16) cannot fire today, because the wiring names
  at most 16 cable positions.
- **Row 11 fires only where the carry is visible.** Joining *different*
  words with `+` gives the same value as `|` and is harmless. Repeating a
  word inside its own kind (`C2 + C2` = `C3`) cannot be told apart from the
  word it carries into; rows 1-9 catch what that does to the layout.
- **Row 14** exists because a panel turned sideways fills a cell of a
  different shape, so mixed arrows cannot form a grid. Square panels are
  exempt, and `ARROW_LEFT` with `ARROW_RIGHT` (or `ARROW_UP` with
  `ARROW_DOWN`) is allowed. The cell size follows C0's arrow.
- The cube checks (§7) join this table in «#79».

**A config with no mistakes** prints its picture and tables instead. For the
rig:

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

A cell that holds no panel prints as `  --  `. When the display has more than
ten panels, single-digit cells are padded (`[C2  v]`) so the columns line up.

## §4 One mapping for every drawing path

**Why.** Today the display-to-physical correction lives only in
`drawDisplayPixel`'s column swap (`isp_hub75_display.spin2:1204-1230`, added
in `21166f7`). The paths that skip it come out mirrored:
- text: `placeCharBitmap` `:995`, `placeDitheredCharBitmap` `:1026`;
- every scroller pixel: `isp_hub75_scrollingText.spin2:501, 553, 567, 619,
  633, 684, 702`;
- every panel-centric call.

**Target.**
- **Display-centric drawing:** display coordinates → display rotation (§5) →
  cell → panel position (through the derived grid; empty cells are
  discarded) → panel coordinates → panel rotation → native coordinates →
  buffer slot → offset. This replaces `displayToPanelCoords` (`:739`) and
  `panelPixelOffset` (`:781`) as one path.
- **Panel-centric drawing:** (panel position, panel coordinates). Pixels
  outside the panel are **clipped** and never spill onto a neighbour. Then
  the panel's display offset is added and the pixel enters the same path.
  `offsetToPanel` (`:854`) works from the derived grid, not from
  `index / perRow`.
- **Deleted in this change:**
  - `needsPanelColumnSwap` (`:639`);
  - the swap inside `drawDisplayPixel`, and the `bUseDisplayCoords` split in
    `drawPixelInternal` (`isp_hub75_display.spin2:1168-1179`) where it only
    selects the swap;
  - `buildWireOrderFromEnums` and `wirePositionToGridCoords` (`:986-1027`);
  - `wireOrderForPanel` and `displayPanelForWire` (`:677`, `:695`), replaced
    by the derived tables;
  - `indexToPanel` (`:835`, no callers);
  - the `wireToDisplayPanel` debug table (`isp_hub75_panel.spin2:136-140, 810`).
- **`fillScreen`** (`isp_hub75_display.spin2:252-264`) fills by panel, not by
  every bounding-box pixel, so a display with holes doesn't spend time on
  cells that hold nothing.
- **Accessors.** `maxPanels` returns the panel count. The bounding-box
  accessors keep their names and meaning: the display size, rotated as in
  §5.

**Verify.**
- *Normal:*
  - On the rig, before and after, the same display-centric line, box and
    circle land in the same places. They were right before, because of the
    swap.
  - Text and scrolling that cross the vertical seam now land whole. Before,
    their halves were swapped: capture that on the bench before the change,
    to measure the negative case.
  - `fillPanel(0, …)` lights the top-left panel. Before, it lit the
    top-right one.
- *Edge:* a panel-centric line running past its panel's edge stops at the
  edge.
- *Error:* none.
- *Cost:* time one full-screen draw with `showDuration` before and after.
  Record both numbers. The draw-path performance sprint starts from them,
  and a regression is that sprint's input, not a reason to keep the old
  path.

## §5 Display rotation

**Why.** For 90° and 270°, `drawPixelAtRCwithRGB` swaps the coordinates, but
it still clamps them against the unrotated size
(`isp_hub75_screenUtils.spin2:75-93`). And no accessor reports a swapped
width and height. On the rig (256×128), a 90° rotation would write past the
display.

**Meaning (SC-1, 2026-10-02).** `DISPn_ROTATION` is **physical**: how the
assembled display is mounted. `ROT_RIGHT_90` means the display hangs turned
90° clockwise, so the driver draws the content's top along the display's
original left edge, and it reads upright once mounted. On a flat rig at the
bench, `ROT_RIGHT_90` therefore looks turned to the left. Turning the content
itself is content rotation (§5b), not this setting.

**Target.**
- `DISPn_ROTATION` (flat displays only) is applied first in the §4 path.
- The display-size accessors report the size **as mounted**: width and height
  swap for 90° and 270°. That covers `maxDisplayColumns`, `maxDisplayRows` and
  `displaySizeInPixels`.
- Clamping uses the mounted size.
- Every consumer of the size picks this up automatically, because they all
  read it through those accessors:
  - display text grid: `isp_hub75_display.spin2:182, 391-401`;
  - line clamps: `:1072-1075`;
  - scroller clip: `isp_hub75_scrollingText.spin2:128, 618-701`;
  - `segment`, `7seg`, `bmp`;
  - the `5x7font` and `7seg` demos.
- Rename `panelRotation()` (`isp_hub75_hwBufferAccess.spin2:430`) to say what
  it returns, the display rotation. Its one caller is
  `isp_hub75_screenUtils.spin2:80`.

**Verify.**
- *Normal:* on the rig, all four rotations. The boundary test (§9) is drawn
  at each one, and "top" is always the mounted top.
- *Edge:* at 90° and 270° the text grid has the swapped number of lines and
  columns. Check it in the debug output.
- *Error:* none.

## §5b Content rotation (SC-1; in planning)

**Why.** Stephen, 2026-10-02: *"we make sure we have the content rotation as
an API member, and both go forward in this sprint... the single config
constant is physical display, and the API is content."* Mounting describes
the hardware and is set once; content rotation is the program's choice at
run time, like a phone turning its screen on fixed hardware.

**Target (draft until Open Questions Q1-Q5 are answered).**
- A display API member sets the content rotation at run time, with the same
  four values as mounting.
- Content rotation composes with mounting in the one path of §4: a drawn pixel
  is turned by the content rotation, then by the mounting rotation, then
  enters the derived layout.
- The size accessors and every consumer listed in §5 follow the result,
  as they follow mounting.
- Cost: the per-pixel path still only looks things up (D6); whatever the
  rotation needs is computed when the rotation is set, not per pixel.

**Verify (draft).**
- *Normal:* the boundary test at each content rotation on the rig, at
  `ROT_NONE` mounting, then at one 90° mounting combined with a 90° content
  rotation.
- *Edge:* setting the rotation at run time after drawing; the text grid and a
  scroller region before and after.
- *Error:* an invalid value is rejected with a message.

**Not in scope:** see SC-1, *does not admit*.

## §6 Buffer and conversion fixes

**Why.** Three defects sit on the path this sprint rewrites. Stephen ruled
that they are in scope.

**F1 — the 16-panel limit.** The 1/2-scan converter
(`isp_hub75_panel.spin2:574-593`) computes `wirePanel` using eight unrolled
`CMPSUB` instructions, so the panel index caps at 8 (9 panels), while the
driver claims 16. **Target:** the panel index is correct for every panel up
to the §11 limit. The method is chosen in the task, but it must keep the
loop's cycle budget. Use the P2KB entries for `CMPSUB` and `QDIV` / the
CORDIC as the authority if a divide is considered. **Verify:**
- *Normal:* a 16-panel buffer-level check. Fill each slot with its own
  colour, run the converter, and confirm the right bit-planes in each panel's
  column range. Run it on the P2 with no panels attached.
- *Edge:* exactly 9 and exactly 10 panels, which bracket today's limit.

**F2 — multiple quarter-scan panels.** `convertScreen2PWM_14`
(`isp_hub75_panel.spin2:258-263, 360-372`) reads the buffer as one
row-major raster with chain-width stride, but the buffer is stored panel by
panel. Its `lMmaskModHalfScreen` (`:263`) also silently requires a
power-of-two size. **Target:** it reads panel by panel, the same way as the
1/2-scan path. **Verify:**
- *Normal:* a buffer-level check on the P2 with two and three quarter-scan
  panels' worth of buffer. The converted frames match what the drawing code
  wrote.
- *Edge:* a single panel, as a regression check.
- *Proof on hardware* (the green panels) belongs to the sweep (§13). The
  remap research is already recorded for it.

**F3 — every display shows adapter 0's image.** `commitScreenToPanelSet`
passes `displayBufferAddress(0)` (`isp_hub75_display.spin2:303, 305`).
**Target:** pass this display's own adapter index. **Verify:**
- *Normal:* with two adapters configured (no second adapter cabled for this
  sprint), each display object's commit uses its own buffer address. Show
  this in the debug output.
- *Proof on hardware* belongs to the sweep.

**Also in this section:**
- The PWM frame size and `pwmSubPageCount` (`isp_hub75_rgb3bit.spin2:288-291`)
  come from the chain length (panel count × panel columns), not from the
  bounding box.
- Debug lines that hard-code four panels print the actual count:
  `isp_hub75_panel.spin2:140` and `isp_hub75_hwBufferAccess.spin2:1013`
  (deleted in §4).
- `zeroFillBuffer` (`:566-577`) uses the panel-count size.

**Domain authority.** P2KB (`p2kb-mcp`) for every PASM2 instruction that is
changed or introduced, cited in the task.

## §7 The cube layer

**Why.** The cube is one of the driver's standard shapes. Drawn objects must
cross all 12 edges, and the cube's orientation is chosen the way display
rotation is.

**Target.**
1. **Settings:**
   - `DISPn_SHAPE = SHAPE_CUBE`;
   - `DISPn_CUBE_TOP` and `DISPn_CUBE_FRONT`, each a cable position;
   - Front must share an edge with Top;
   - `DISPn_ROTATION` does not apply to a cube.
2. **Checks at startup**, with messages in the §3 catalogue:
   - exactly six panels, all square;
   - the sentences describe a net that folds into a cube (one of the 11 cube
     nets);
   - Top and Front are valid and share an edge.
3. **Folding.** At startup, fold the net to derive:
   - all 12 edges, including those the flat picture doesn't show;
   - for each face, which edge meets which neighbour, and how coordinates
     transform across each edge.

   These form one edge table, built once.
4. **Face names.** `TOP BOTTOM FRONT BACK LEFT RIGHT` are derived from Top
   and Front. Each face's **up** is fixed and documented as **stable** for
   the image-mapping sprint:
   - the four sides' up points toward Top;
   - Top's up points toward Back, so that standing at Front, text on Top
     reads correctly;
   - Bottom's up points toward Front.
5. **The face-pixel layer.** Pixels are addressed in face coordinates (face,
   row, column), and row and column may run past an edge. Each pixel is
   folded across as many edges as it crosses, using the edge table, then
   enters the §4 path as (panel position, panel coordinates).
   - **Corner gap:** a pixel past two edges of one face at once lands where a
     cube corner has no surface (270° around a corner, not 360°). It is
     discarded.
   - **Seam placement:** an object that straddles a corner off-centre has one
     unavoidable seam. The driver puts it on the edge farthest from the
     object's centre.
   - A shape centred on a face, an edge or a corner is seamless.
6. **Drawing on faces.** The cube gets face-centric calls (a face plus face
   coordinates) for every primitive: pixel, line, box, circle, text, and
   scrolling.
   - They differ from panel-centric calls in one way: they **fold** where
     panel-centric calls **clip**.
   - They are thin entries into one drawing core. Each primitive is still
     implemented once, and the core is told whether to clip or fold.
   - Text scrolling around the cube is face-centric scrolling that runs off
     an edge.
7. **The fold self-test**, a new top file in `driver/`. Requested by Stephen
   on 2026-10-01 (*"yes, add it"*), in answer to the plan-review question.
   - It runs on the P2 with no panels attached.
   - It pushes a fixed list of face coordinates through the fold:
     - every edge crossing, in each direction;
     - runs across two and three faces;
     - every corner gap;
     - a circle centred exactly on a corner.
   - For each case it prints where the pixel lands and compares the result
     with an answer computed by hand and written into the file.
   - It prints one PASS/FAIL line per case and a total, then `END_SESSION`.
   - It must fail visibly on a wrong answer. Before relying on it, prove that
     by flipping one expected value: that case must report FAIL.

**Two-phase.** The face-pixel layer (5) and the drawing-core change (6) set
the shape for every cube drawing call. The first dispatch returns the edge
table, the fold and one primitive (lines) working through it. The arbiter
reviews that before the rest is built.

**Out of scope:** the 3-D projection API and image mapping. Both belong to
the image-mapping sprint, which depends on item 4 staying stable.

**Verify.**
- *Normal and edge, without panels:* the fold self-test (item 7). Every case
  passes. The corner-centred circle must give three quarter-circles meeting at
  all three edges; those edge joins were checked by hand during planning.
- *Negative:* with one expected value deliberately flipped, the self-test
  reports that case as FAIL.
- *Error:* deliberately wrong cube configs, which must produce their
  messages:
  - a non-net;
  - Front not touching Top;
  - five panels;
  - a non-square panel.
- *Proof on hardware:* the six-panel cube session in the sweep (§13).

## §8 The identify routine

**Why.** It is how a user fills in the sentences, and how they confirm them.
Stephen confirmed the design during planning.

**Target.** `demo_hub75_numberPanels.spin2` becomes the identify routine.
1. For each cable position *k*, it looks up the panel position *p* where that
   panel sits, then draws on that panel:
   - an arrow (`^`) near the top;
   - `C`*k*;
   - `P`*p*.
2. It prints `END_SESSION` once the image is up, then holds the image with
   `repeat`.
3. **Compact layout** for small panels (32×16 with the 5×7 font): `^` plus
   `C2P1` on one line. The layout is chosen from the panel size and font.
4. Each panel gets a distinct background colour, as today. That makes the
   panels easy to tell apart when describing them.

**How to read it (goes in the guide):**
- `P` labels in reading order and every arrow up: the config is right.
- `P` labels out of order: the sentences place panels wrongly. Read the `C`
  labels to fix them.
- An arrow pointing another way: that panel's arrow word is wrong, and the
  arrow shows which way.
- Because the `C`*k* labels are drawn through the inverse table, they are
  physically correct **even when the config is wrong**.

**Verify.**
- *Normal:* the rig shows C0 at bottom-left, C1 bottom-right, C2 top-left and
  C3 top-right. P0..P3 read in reading order, and all arrows point up.
- *Edge:* set all arrows to `ARROW_UP`, the "fresh config" state. The arrows
  then show each panel's native up, pointing down on the rig.
- *Negative:* a deliberately swapped sentence (C1 described `ABOVE` C0)
  produces out-of-order `P` labels, while the `C` labels stay physically
  correct.

## §9 The boundary test

**Why.** It is the visible proof that drawing crosses panel seams correctly.
Stephen asked for it.

**Target.** A new top file draws in display coordinates:
- a crosshair on the centre row and centre column;
- one box spanning all four panels;
- a circle centred on the display's centre;
- one text string across the vertical seam;
- a panel-centric line deliberately running past its panel's edge, to show
  clipping.

It also times one full draw and prints the elapsed microseconds with the
existing `showDuration` pattern. Then it prints `END_SESSION` and holds the
image.

Mounting rotation is a compile-time setting (`DISP0_ROTATION`), so the
mounting check builds and runs the test once at each of the four values.
Content rotation (§5b, SC-1) is a run-time call; the boundary test exercises
it once §5b's task lands.

The test is written **once**, after the one-call startup (§3.4) and before
the mapping change (§4). It uses the final startup call and drawing calls
whose names don't change. §2-§3 don't touch the mapping, so it can still be
run on the old mapping in Visit 0 (§13).

**Verify.**
- *Normal:* on the rig every element is continuous across both seams, at each
  of the four rotations.
- *Negative (Visit 0):* run after §3.4 and before §4 lands, it shows the text
  halves swapped and the panel-centric line on the wrong panel. That capture,
  and its full-draw time, are the "before" for §4.

## §10 Demos converted

**Target.**
- All 13 top files use the one-call-per-adapter startup (§3) and the rig's
  sentence config.
- `demo_hub75_multi2x2panel` drops `setWireConfig` (`:70`).
- The panel-index constants in `multi2x2panel` (`:51-55`), `quadPanel`
  (`:50-55`) and `multiPanel` are checked against panel positions in reading
  order.
- `numberPanels` becomes identify (§8).
- `demo_hub75_hwGeometry.spin2` (comment-only legacy) is either deleted or
  rewritten to the new config. Keep it only if it still teaches something the
  guide doesn't.
- `isp_hub75_anlyCheck` and `test_hub75_pin_identify` are checked to compile
  unchanged.
- `isp_dummy_flash.spin2` (the flash image that prints `* Hi! from FLASH *`)
  joins the compile sweep, by Stephen's decision at sprint start
  (2026-10-01):
  - add it to `TEST_COMMAND` and `BUILD_COMMAND` in
    `.claude/skill-conventions.md`, and change "13 top files" to 14 there and
    in this plan's verify lines;
  - correct its header, which currently reads `demo_dual_motor_rc.spin2` /
    "Demonstrate R/C driving of a two-wheeled platform" (copied from another
    project), to its real name and purpose.

**Verify.** All 13 top files compile with 0 warnings and the style gate
passes. Each demo that draws runs on the rig at least once in the bench visit
(§13). For each, record what it showed.

## §11 Driver limits, per panel type

**Why.** *"Prescribe what the driver limit is for each type of panel."*

**Target.** A table in the guide. Each row is a panel type (size, scan,
chip). Its columns:
- the maximum panels per adapter;
- the factor that sets that limit:
  - hub RAM: buffer plus two frame sets, by colour depth;
  - the refresh core's line buffer, `CogBuffer[256]` (`isp_hub75_rgb3bit.spin2`);
  - the converter's panel limit after F1;
  - refresh rate, measured on the bench;
- whether the number is **measured** or **calculated**.

This sprint fills:
- every calculated column for every panel type in
  `DOCs/AuthorTestConfigurations.md`;
- the measured columns for the rig's panel type. Measure the refresh rate
  at each colour depth, and the point at which flicker becomes visible,
  agreed with Stephen at the bench.

The sweep fills in the measured columns for the other types. The startup
check (§3) enforces the hard limits: RAM, line buffer and converter.

## §12 Documentation

**Deliverables.**
1. **A new wiring guide.** It replaces the wiring sections of
   `DOCs/MultiPanelConfiguration.md`, and the parts of that file that remain
   point to it.
   - **Content:**
     - the grammar (§2), stated prescriptively;
     - how to fill in a config from the identify screen (§8);
     - display rotation;
     - the cube (orientation, face names, folding, the corner rule);
     - the limits table (§11);
     - the startup message catalogue (§3).
   - **Seven worked examples**, each with the same five parts:
     1. a sketch of the front view, with the cable route;
     2. the sentences;
     3. the picture printed at startup;
     4. what the identify screen shows when the config is right;
     5. one or two common mistakes, each with its exact startup message.
   - **The seven examples:**
     1. a row of 4;
     2. two panels;
     3. a 2×2 in Z order, starting bottom-left (the rig);
     4. a 2×2 in serpentine order;
     5. 3 across × 2 down;
     6. an L shape;
     7. the cube, wired in a ring, with Top and Front set.
2. **The glossary** in `THEOPS.md` (§1).
3. **The upgrade path.** A config-conversion section, following the existing
   `Checklist-v1-v2.md` / `Checklist-v2-v3.md` pattern, that converts the
   old settings to sentences, including the adapter startup change.
4. **The changelog.** Entry voiced per `central:changelog-voicing`. The
   version number is Stephen's.
5. Everything listed in the blast radius below.

## §13 Bench visits, and what the sweep inherits

**Visit 0 — before §4 lands (the "before" pictures).** Run the boundary test
(§9) at `ROT_NONE`, after §2-§3 and before the mapping changes.
- Stephen describes what each element shows.
- Record the full-draw time it prints.
- Decides nothing new. It records the negative case that §4's verification
  compares against, from real hardware rather than from prediction.

**Visit 0 record — 2026-10-02 («#70»).**
- *Run:* `demo_hub75_boundary` at commit 6c0dc6a, `DISP0_ROTATION = ROT_NONE`, the
  rig config (all four arrows `ARROW_DOWN`). Headless:
  `pnut-term-ts --headless -r demo_hub75_boundary.bin --end-marker --timeout 30`,
  exit 0 on `END_SESSION`.
- *Full-draw time:* **287,436 µs** (log line `- elapsed boundary draw: 287_436 uSec`;
  one run).
- *What Stephen saw* (his words):
  - text: *"green text flowing off right edge then back on to left edge (wraps) - not
    crossing center seam"*;
  - red panel-0 line: *"red line top right panel"*;
  - box, circle, crosshair: *"yellow box, cyan circle, white lines correct"*.
- *Reading* (the arbiter's interpretation, not Stephen's words): the text halves are
  swapped across the vertical seam, which shows on the panels as text running off the
  right edge and resuming at the left; the panel-centric call lands on the top-right
  panel because its panel index is the buffer slot. Both match the §4 prediction, and
  the lines, box and circle land correctly through `drawDisplayPixel`'s column swap.
- *Earlier observation on the same mapping* (Stephen, 2026-10-01, `demo_hub75_quadPanel`
  after «#73»): top-right shows P0, top-left P1, bottom-right P2, bottom-left P3, all
  arrows up.

**«#74» draw time — 2026-10-02.** `demo_hub75_boundary` on the one mapping, same rig
config and `ROT_NONE`, same headless command: **197,508 µs** (log
`headless_261002-002622.log`, line 75, `- elapsed boundary draw: 197_508 uSec`; one run),
against Visit 0's 287,436 µs. A re-run of HEAD 02f96e0 in the same session printed
287,436 µs again (`headless_261002-002505.log`, line 76). The arbiter's own re-run on
the final source also printed 197,508 µs.

**«#74» on the rig — 2026-10-02.** Stephen, looking at the boundary test after the
change: *"green is now centered text, red line is now top left panel (right edge) rest
is correct"*. Against Visit 0: the seam text is whole across the vertical seam, the
panel-0 line moved from the top-right panel to the top-left one and stops at its right
edge, and the crosshair, box and circle are unchanged. Stephen then added: *"quad
panel all marks were correct"* (`demo_hub75_quadPanel`, whose log places
`fillPanel(0..3)` at (0,0), (0,128), (64,0), (64,128)), and *"red line stops at the
right edge of the top left panel"*. Panel order on the panels is therefore confirmed in
reading order after «#74»; Visit A re-checks it through identify.

**Visit A — after §1-§6 and §8.**
- Identify on the rig: the §8 normal, edge and negative cases.
- Display-centric versus panel-centric, before and after (§4).
- The full-draw timing (§4 cost).
- Decides: whether the mapping is certified on hardware.

**Visit B — after §5, §7, §9 and §10.**
- The boundary test at all four rotations.
- Every converted demo once.
- Refresh measurements for the rig's limits rows.
- The fold self-test (§7.7, no panels needed).
- Decides: whether the sprint closes.

Each visit's run sheet follows *the bench visit* rules
(`SKILLS-AUTHORING.md`).

**Built here, proven in the panel sweep** (not claimed proven by this
sprint):
- the cube on six 64×64 panels;
- multiple quarter-scan panels (F2), on the two green MBI5124GP panels.
  Remap research is saved in the `sweep_green_panel_research` context key;
- two adapters at once (F3, plus the one-call startup);
- the measured columns of the limits table for every other panel type.

The sweep runs under the **no black holes** rule.

## Documentation Blast Radius

`DOC_AUDIT_COMMAND` (`python3 tools/check_docs.py`), run 2026-10-01 at
planning:

```
Doc-drift audit (advisory) -- 21 documents, 29 .spin2 sources
ORPHAN (0)
DUPLICATE (0)
COUNT (0)
```

The audit reports no drift today. The list below is what this sprint's
changes make stale. It comes from the planning survey and was spot-checked
by reading the source.

| Artifact | Lines | What changes |
|---|---|---|
| `README.md` | 85, 112 | the feature bullets: wire order and per-panel rotation become the sentences and the cube |
| `README.md` | 136, 150-159 | the config table: `MAX_PANELS_PER_ROW/COLUMN` removed; sentences, `SHAPE` and `CUBE_*` added; the rotation note ("work best on square displays") replaced by the §5 behaviour |
| `README.md` | 183-274 | three sample configs converted to sentences |
| `THEOPS.md` | 51-52 | the file table: `hwBufferAccess` / `hwBuffers` are no longer edited by users |
| `THEOPS.md` | 77, 94-104 | the configuration rows: wire and per-panel rotation rows replaced; glossary added (§1) |
| `THEOPS.md` | 168-172 | size limits: by panel count, pointing to the limits table |
| `DOCs/MultiPanelConfiguration.md` | 18-445 (almost all) | replaced by the new guide (§12). Its per-panel rotation value table (295-316) contradicts the code (`$20..` versus `0..3`) and goes |
| `DOCs/TheoryOfOperations.md` | 105, 152-157 | the pixel pipeline rewritten to the §4 path; it already describes a raster that the code no longer uses |
| `DOCs/TheoryOfOperations.md` | 291-334 | memory examples by panel count; the descriptor table layout |
| `DOCs/TheoryOfOperations.md` | 422-443 | config example converted |
| `DOCs/TECHNICAL_DEBT.md` | 7-41 | TD-001 (wire-order table optimisation) retired: the table is gone |
| `DOCs/AuthorTestConfigurations.md` | 241-244 and the per-config blocks | configs converted; the multi-panel status column cross-references the limits table; the scan term per the glossary |
| `DOCs/ChipCharacteristicsMatrix.md` | the scan column, 14 and 244+ | scan term per the glossary |
| `Checklist-v2-v3.md` / a new upgrade checklist | — | the config conversion (§12.3) |
| `ChangeLog.md` | new entry | §12.4 |
| `CLAUDE.md` (project) | the *User Configuration Files* section | `hwBufferAccess` / `hwBuffers` are no longer per-setup edits |
| docstrings | every PUB touched in §2-§8 | renamed or re-scoped methods (`panelRotation` → display rotation; deleted wire methods); the 2×2/3×3 diagrams at `isp_hub75_display.spin2:268-271, 328-333` |
| code comments | `isp_hub75_hwBufferAccess.spin2:111-172`, `hwPanelConfig` config groups | rewritten in the vocabulary (§1) |

Not affected (checked: no wiring content): `HUB75-brd-config.md`,
`CubePix.md`, `HUB75Adapter.md`, `HUB75-Driver-SWver0/1.md`,
`HardwareTurnon.md`, `driver/README.md`.

## Dispatch

`DISPATCH_MODEL` is `arbiter-serial`, and this sprint keeps it. There are two
reasons:
- every section edits the same small set of driver files;
- the board is an exclusive resource.

Two-phase sections: **§2+§3** (the encoding, derive tables and message
catalogue) and **§7** (the edge table, fold and drawing core).

## Named unknowns

| Unknown | Response when it resolves |
|---|---|
| Whether the green panels need the remap as well as F2 | the sweep's green session. Research is saved. If it's neither understood nor fixable quickly, the no-black-holes rule applies |
| Refresh limits for panel types other than the rig's | measured in the sweep. Until then the rows say "calculated" |
| Whether the one-call startup reveals hardware ordering needs with two adapters cabled (both starting at once) | the sweep's two-adapter session |
| Cause of the C1 flicker («#67») | its own task. It could be the panel, the ribbon or the driver. It is not a wiring defect, so it does not gate this sprint |
| Per-pixel cost after §4 and §7 | measured at Visit A (§4) and handed to the draw-path performance sprint |

## Plan section ↔ task cross-reference

Every task carries the tag `disporg`. `seq` is the order of work. «#67» (the
C1 flicker) is outside this sprint and sits after it, at seq 19.

| Plan § | Deliverable | Task | seq |
|---|---|---|---|
| §1 | Glossary in THEOPS.md | «#68» | 1 |
| §2 | Sentence words and settings, buffers by panel count (two-phase: 1st) | «#71» | 2 |
| §3.1-3 | Startup decode, checks, derive, picture; driver-limit constants (two-phase: 2nd) | «#72» | 3 |
| §3.4 + §10 (startup) | One call per adapter; demo startup converted | «#73» | 4 |
| §9 | Boundary test demo (one-call startup, old mapping) | «#69» | 5 |
| §13 | Bench Visit 0 — before-pictures and draw time | «#70» | 6 |
| §4 | One mapping; swap and wire tables deleted | «#74» | 7 |
| §5 | Display rotation reports the mounted size | «#75» | 8 |
| §5b | Content rotation API (SC-1) | not yet generated: waits for Open Questions Q1-Q5 | after 8, before Visit A |
| §6 | F1, F2, F3 and chain-length frame sizes | «#76» | 9 |
| §8 | Identify routine | «#77» | 10 |
| §13 | Bench Visit A | «#78» | 11 |
| §7.1-5, §7.7 | Cube fold, edge table, face-centric lines, fold self-test (two-phase: 1st) | «#79» | 12 |
| §7.6 | Every primitive on faces (two-phase: 2nd) | «#80» | 13 |
| §10 (rest) | Demo panel constants, hwGeometry, dummy flash in the sweep | «#81» | 14 |
| §11 | Per-panel-type limits table (calculated) | «#82» | 15 |
| §13 | Bench Visit B | «#83» | 16 |
| §12.1 | Wiring guide, seven worked examples | «#84» | 17 |
| §12.2-5 + Blast Radius | Every other doc, upgrade checklist, changelog 4.0.0 | «#85» | 18 |

**Dispatch for this sprint:** `arbiter-serial`, the project default. All
sections edit the same small set of driver files, and the board is an
exclusive resource. Two-phase pairs: «#71»→«#72» and «#79»→«#80».
Environments:
- documentation and compile-only work («#68», «#71», «#81» compile, «#82»
  arithmetic, «#85») can run in either environment;
- every bench task and headless run needs the Mac.

## Revision history

- 2026-10-01 — plan written. At review the fold self-test was added (§7.7,
  Stephen's yes), which leaves no open questions.
- 2026-10-01 — revised while generating tasks.
  - §9: the boundary test is built once per `DISP0_ROTATION` value instead of
    "cycling", because rotation is compile-time only. It is written first and
    prints its draw time.
  - §13: Visit 0 added, to capture the "before" state on the unchanged driver.
  - Cause: **(2) research incomplete.** The plan assumed a runtime rotation
    setter without checking, and placed the "before" capture without
    scheduling it ahead of §4.
- 2026-10-01 — re-ordered after generating tasks, at Stephen's prompt to
  check that no task redoes finished work (`plan-to-tasks` §3a).
  - The boundary test («#69») and Visit 0 («#70») move after the one-call
    startup («#73»), so the test is written once against the final startup.
    It still runs before the mapping change.
  - The driver-limit constants are defined once in «#72», and the limits
    table («#82») only reads them. Before, «#82» reopened «#72».
  - The cube self-test («#79») registers itself in the compile sweep, and the
    sweep counts were corrected: 13, 14 with the boundary test, 15 with the
    self-test, 16 with the dummy flash file.
  - Cause: **(2) research incomplete.** The rework check was not run before
    the order was set.
- 2026-10-02 — agreed scope change **SC-1** (two rotations), recorded in the
  new *Agreed scope changes* log. `DISPn_ROTATION` is defined as physical
  mounting, and content rotation becomes a run-time API member in this
  sprint (§5b, in planning; Open Questions Q1-Q6). §9's statement that no
  run-time rotation exists is replaced. The *Agreed scope changes* section
  and its rule are new: scope changes only by recorded agreement.
  - Cause: **(2) research incomplete.** Planning took "rotation" as one
    measure; the bench showed two (the hardware turned, the picture turned).
