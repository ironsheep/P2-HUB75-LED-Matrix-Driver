# Draw-Path Performance Sprint Plan

> **Superseded (2026-10-02):** never executed. Its ground is covered, re-checked against the 4.0.0 code, by [FRAME-RATE-SPRINT-PLAN.md](../FRAME-RATE-SPRINT-PLAN.md) and the [frame-rate study](../../analysis/2026-10-02-FRAME-RATE-STUDY.md). Several numbers and conclusions here no longer hold.

**Status:** Planned (not started). Execution gated on close-out of the
SOURCE-RECONCILIATION sprint (3.0.3) — see *Relationship to Outstanding
Work* below. Build number is set at `sprint-start`, not here.

**One-line charter:** Remove the per-pixel cross-object method-call
explosion that the multi-panel/rotation generalization introduced into
the Spin2 drawing path, restoring near-reference draw speed for the
common single-panel case while keeping every generalized feature intact.

---

## Origin & Problem Statement

A user reported a drawing-performance regression. Root-cause analysis
compared a reference build
(`DOCs/REF-NO-COMMIT/hub75_random_pixels_xmas_tree_1.0-2025-12-10/`,
the Francis Bauer "random pixels / xmas tree" demo riding on the older
single-panel driver) against the current unified driver.

The current per-pixel write path recomputes the **entire** panel
geometry, rotation, buffer address, and color-depth configuration from
scratch on every pixel, through a deep tree of cross-object Spin2 method
calls. Spin2 is interpreted; method-call dispatch dominates runtime.

### Measured structural delta (method invocations per pixel)

Reference `drawPixelAtRCwithRGB`
(`…/isp_hub75_screenUtils.spin2:37`):

- Clamp via compile-time CONs (folded, no call)
- Offset `((row*COLS)+col)*BYTES` — constants, inline
- `screen.screenAddress()` → 1 call
- 3 × `color.correctedSingleColor()` → ~2 calls each → 6
- **≈ 9 method invocations / pixel**

Current `drawPixelAtRCwithRGB`
(`driver/isp_hub75_screenUtils.spin2:56`):

| Hot-path call | Invocations (incl. nested `ptrTableEntry`) |
|---|---|
| `displaySizeInPixels` (`isp_hub75_hwBufferAccess.spin2:342`) | 2 |
| `panelRotation` (`:430`) | 2 |
| `displayToPanelCoords` (`:739`) → `panelSizeInPixels` + `displaySizeInPanels` | 5 |
| `panelPixelOffset` (`:781`) → `panelSizeInPixels` + `bytesPerColor` + `wireOrderForPanel`→`maxPanels` + `panelRotationAt`→`maxPanels` | 13 |
| `displayBufferAddress` (`:480`) | 2 |
| 3 × `correctedSingleColor` (`isp_hub75_colorUtils.spin2:109`) → each `colorAtDesiredBitWidth` (`:284`) → `colorDepth` + `pwmFrameCount`→`colorDepth` | 21 |
| `rgbForCValue` + outer dispatch | 2 |
| **Total** | **≈ 47 method invocations / pixel** |

That is **~5× the interpreter dispatch overhead per pixel**, plus extra
divides/mods (`displayToPanelCoords:766-779`), `case` evaluation, and a
clamp+compare+`@@` indirection inside **every** `ptrTableEntry` call
(`isp_hub75_hwBufferAccess.spin2:969`).

### Why this matters everywhere

Every public drawing primitive — text, lines, rectangles, BMP, clears —
funnels through `pixels.drawPixelAtRC`
(`driver/isp_hub75_display.spin2:289, 998, 1029, 1182, 1233`). The
regression is paid by the entire API, and most visibly by full-screen
fills (the random-pixel path) and the many horizontal runs in shapes
and text.

### What is legitimate vs. incidental

The generalization genuinely added: up to 3 chains, horizontal/vertical/
2-D-grid layouts, display-level **and** per-panel rotation, wire-order
remapping, runtime-selectable color depth. The reference hardcoded a
single panel as compile-time constants. **None of that requires per-pixel
recomputation.** Every one of the ~47 calls returns a value that is
**invariant for a chain across an entire draw operation** — they are
re-derived pixel after pixel from a table that never changes mid-draw.
That recomputation is the entire incidental cost, and where this sprint
operates.

### Key code-research findings (verified, drive the design)

1. **Chain config is write-once at init.** The chain descriptor table is
   written only by `configure()` (`:264-266`), `setWireConfig()`
   (`:289-290`), and `setBufferPointers()` (`:310-312`) — all startup.
   Geometry/rotation/buffer-address are static after bring-up → safely
   cacheable.
2. **Brightness and gamma are runtime-settable.** `setBrightness()`
   exists (`isp_hub75_colorUtils.spin2:74`); `bGammaEnable`/gamma are
   mutable DAT (`:62, :325`). A precomputed color LUT must therefore be
   **rebuildable** on those changes, not built once.
3. **All channels share one correction function.** `correctedSingleColor`
   maps an 8-bit channel value → corrected byte purely as a function of
   (chain color depth, brightness, gamma); R/G/B all use `@gamma`
   (`:114-120`). One 256-entry LUT per chain suffices today. (If
   per-channel correction is ever added, the LUT widens to 3×256 — noted
   as an assumption, not an open question.)
4. **State that must be DAT, not VAR.** Both the demo (`pixels`) and the
   display object include `isp_hub75_screenUtils` as separate instances.
   The cache and LUT describe global hardware config, so they live in
   **DAT (singleton)** to be shared across instances — consistent with
   the project's "DAT for singleton state" rule and with the existing
   singleton config table.

---

## Build & Verification Environments

This repo root is shared between a **compile-only Linux container**
(`pnut-ts` only) and a **macOS folder** with the full toolchain +
hardware. Three distinct roles apply to this sprint:

- **In-container compile gate** — every demo compiles clean, 0 warnings,
  at every step (`BUILD_COMMAND`). This is the continuous correctness
  net.
- **In-container behavior-preservation check** — for the
  behavior-preserving sections (§2 cache, §3 LUT, §4 fast-path on the
  general branch), a single-panel demo's emitted `.bin` is compared
  before/after; byte-identical proves no behavior change. The LUT's
  256-entry output is additionally proven equal to the live
  `correctedSingleColor` across all inputs/depths.
- **Live-P2 timing proof — NO HUB75 panel required (key insight).**
  HUB75 is **open-loop and write-only**: every signal (R/G/B, CLK, LAT,
  OE, ADDR A-E) is a P2→panel output and the driver never reads anything
  back. Therefore the entire draw path (§2-§5 screen-buffer fills) is
  **pure HUB-RAM writes**, panel-independent, and even the PASM2 cog
  (`isp_hub75_rgb3bit`) toggles GPIO on a fixed schedule that never waits
  on panel feedback. The §1 instrumentation can thus emit accurate
  DEBUG timing/throughput numbers from a **bare P2 on USB** (serial for
  the DEBUG stream) with **nothing connected to the HUB75 pins** — draw
  against an imaginary panel, capture counts, reflash the optimized
  build, capture again. Setup collapses from a panel-wiring session to
  "plug in a board," and a board can stay permanently attached, making
  draw-path perf a **repeatable regression gate**.
  - *Boundary:* this proves **timing**, not **visual correctness**
    (color/geometry looking right still needs real panels). This sprint
    does not depend on visual proof — correctness is covered in-container
    by the binary-equivalence checks (§2/§3/§4) and the LUT self-check
    (§3). Real-panel visual verification stays only on the reconciliation
    sprint's §5b and is out of scope here.
  - *Environment:* capture still runs on the macOS side (only it has
    `loadp2` + `pnut-term-ts` for flashing and the DEBUG terminal); the
    container remains compile-only. But the *rig* is just a bare P2.
  - Number-gathering remains a **decoupled, non-blocking step**: the
    sprint deliverable is the instrumented harness; counts are captured
    whenever convenient against both the pre-optimization (baseline) and
    post-optimization builds of the same demo.

---

## Numbered Work Packages

### 1. Timing-instrumentation harness + perf demo

**Why.** The whole sprint is a performance claim; it must be provable.
Per Stephen, the proof is self-emitting DEBUG timing output, not a
scope/analyzer session — so the numbers print themselves when the rig
is set up, and capture never blocks the code work.

**Current starting point.** No draw-timing instrumentation exists.
Demos call draw APIs and `display.commitScreenToPanelSet()` with no
elapsed-cycle capture.

**Target.**
- A compile-time-gated timing facility (CON flag, e.g.
  `ENABLE_DRAW_TIMING = FALSE` default) that wraps representative draw
  operations with `GETCT` before/after and `DEBUG`-logs elapsed cycles,
  converted to µs and to cycles-per-pixel, labeled per operation. When
  the flag is FALSE the harness compiles to **zero** emitted code so
  release builds and the binary-preservation checks are unaffected.
- A dedicated perf demo top file (e.g. `demo_hub75_drawPerf.spin2`)
  running a fixed battery against a deterministic frame: N full-screen
  solid fills, N full-screen random-pixel fills (the reported workload),
  a fixed shape draw (the xmas-tree geometry), a text render, and a
  horizontal-run rectangle fill. Each logs cycles + cycles/pixel.
- The demo ships in **two configurations** so both code paths are
  measured: a single-panel config (exercises the §4 fast path — the
  common case and the reported case) and a 2×2-grid config (exercises
  the general path). These are **compile-time geometry selections**, not
  physical panels — both run on a bare P2 with nothing wired to the
  HUB75 pins (see *Build & Verification Environments*: the draw path is
  write-only / panel-independent).

**Integration points.** Reuses the existing DEBUG infrastructure; no
public API change. The timing flag and channel naming should be chosen
to be foldable into the DEBUG_MASK follow-up (see *Relationship to
Outstanding Work*).

**Verification.** *Normal:* with flag TRUE the demo compiles and emits
well-formed labeled timing lines. *Edge:* with flag FALSE the demo
compiles and the emitted `.bin` is byte-identical to the same demo with
the harness source removed (proves zero-cost-when-off). *Error:* GETCT
wrap handles counter wrap across a long operation (use unsigned delta).

---

### 2. Chain-config cache (structural foundation)

**Why.** Removes the bulk of the ~24 geometry/address calls per pixel by
resolving the invariant chain config **once** and reading cached longs
in the hot path. This is the structural home that §3 and §4 build on.

**Current starting point.** `drawPixelAtRCwithRGB`
(`isp_hub75_screenUtils.spin2:56`) calls `displaySizeInPixels`,
`panelRotation`, `displayToPanelCoords`, `panelPixelOffset`,
`displayBufferAddress` per pixel; each walks `ptrTableEntry`
(`isp_hub75_hwBufferAccess.spin2:969`) with a clamp/compare/`@@` every
time. No per-chain memo exists.

**Target.**
- A per-chain resolved-config record in **DAT** (singleton; up to 3
  chains) holding: screen-buffer address, maxRows, maxCols,
  rotation, bytesPerColor, rowsPerPanel, colsPerPanel, panelsPerRow,
  panelsPerColumn, the color-depth-derived shift, a pointer to the §3
  color LUT, an `isSimple` flag (computed for §4), and a `valid` flag.
- A `cacheChainConfig(nChainIdx)` builder, populated at the end of the
  display start sequence after `configure()`/`setBufferPointers()`/
  `setWireConfig()` have run; plus a lazy build-on-first-use fallback
  guarded by the `valid` flag so a direct `pixels.*` caller (no display
  object) still gets a populated cache.
- The hot path reads cached fields instead of calling the accessor
  tree. The general (non-fast-path) coordinate math is preserved exactly
  (§4 decides which branch runs).

**Integration points.** `isp_hub75_screenUtils` owns the cache (it is the
hot caller and already includes `hub75Bffrs`/`colorUtils`). Builder reads
the same accessors used today, so resolved values are identical to the
live lookups. No public API change.

**Verification.** *Normal:* single-panel and 2×2 configs produce
byte-identical screen-buffer output before/after (binary check). *Edge:*
lazy fallback path (demo-only `pixels` instance with no display object)
populates correctly on first pixel. *Error:* invalid `nChainIdx` still
routes through the existing `ptrTableEntry` abort, not silent bad reads.

---

### 3. Color-correction LUT (largest single win)

**Why.** Collapses ~21 method calls/pixel (3 channels × `correctedSingleColor`
→ `colorAtDesiredBitWidth` → `colorDepth`/`pwmFrameCount`) to **3 byte
reads**.

**Current starting point.** `correctedSingleColor`
(`isp_hub75_colorUtils.spin2:109`) computes brightness×round
(`:127`), optional gamma table (`:128-129`), then
`colorAtDesiredBitWidth` (`:284`, two more accessor calls). Called 3×
per pixel from `screenUtils.drawPixelAtRCwithRGB:109-111`.

**Target.**
- A 256-entry **BYTE** LUT per chain in **DAT**, where
  `LUT[v] == correctedSingleColor(chain, anyChannel, v)` for v in 0..255
  (output already depth-shifted; entries fit a byte for all depths —
  verified: max output ≤255).
- `buildColorLut(nChainIdx)` populates it; the §2 cache holds the LUT
  pointer.
- **Rebuild triggers:** wire `buildColorLut` into `setBrightness()`
  (`:74`) and the gamma-enable path so runtime brightness/gamma changes
  re-derive the table in place (pointer stays stable, so the cache need
  not be invalidated).
- Hot path becomes `BYTE[pLut][red]`, `BYTE[pLut][green]`,
  `BYTE[pLut][blue]`.

**Integration points.** `isp_hub75_colorUtils` owns LUT storage + build
+ rebuild hooks; `screenUtils` reads `pLut` from the §2 cache. The
public color API is unchanged; `correctedSingleColor` remains for any
non-hot caller and as the LUT's reference implementation.

**Verification.** *Normal:* an in-container self-check asserts
`LUT[v] == correctedSingleColor(...)` for all 256 v across every color
depth and a brightness/gamma matrix. *Edge:* after `setBrightness` and
after gamma toggle, LUT re-matches the live function. *Error:* depth set
to an invalid value falls through to the existing default-depth behavior
in both the LUT build and the reference function (must agree).

---

### 4. Single-panel / no-rotation fast path

**Why.** The single-panel, unrotated config (the reference's case, the
xmas-tree's case, and the overwhelmingly common deployment) needs none of
`displayToPanelCoords`/`panelPixelOffset`. One branch restores the
reference's direct-offset speed while leaving the general path intact for
grids and rotation.

**Current starting point.** `drawPixelAtRCwithRGB` always runs the
rotation `case` (`:85-98`), `displayToPanelCoords` (`:102`), and
`panelPixelOffset` (`:105`), even for a lone unrotated panel.

**Target.**
- `isSimple` computed once in the §2 cache builder: true when
  `panelsPerRow == 1 and panelsPerColumn == 1` and display rotation is
  `ROT_NONE` and panel-0 per-panel rotation is `ROT_NONE`.
- When `isSimple`, compute the offset directly —
  `((rowIndex * maxCols) + colIndex) * bytesPerColor` (reference form,
  `…/isp_hub75_screenUtils.spin2:41`) — and skip the coordinate/offset
  helpers entirely. Otherwise run the existing general path (now reading
  §2-cached geometry).

**Integration points.** Pure internal branch in
`screenUtils.drawPixelAtRCwithRGB`; no API change.

**Verification.** *Normal:* single-panel config — fast path emits
byte-identical screen-buffer output to the general path (binary check
against pre-sprint code). *Edge:* 2×2-grid and any-rotation config —
`isSimple` is false, general path runs, output byte-identical to today.
*Error:* clamping of out-of-range row/col preserved on the fast branch
(same `0 #> x <# max-1` clamp).

---

### 5. Run/row-fill API (contiguous-run primitive)

**Why.** Lines, rectangle fills, and the xmas-tree's `draw_pixels` draw
many contiguous horizontal runs one pixel at a time, paying full
per-pixel dispatch on each. A run primitive computes the corrected color
once (3 LUT reads) and the start offset once, then tight-loops the inner
byte writes.

**Current starting point.** Horizontal spans are drawn pixel-by-pixel via
`drawPixelAtRC` from the display line/fill primitives
(`isp_hub75_display.spin2:289, 1182, 1233`).

**Target.**
- A public `screenUtils.fillRowRun(nChainIdx, row, colStart, colEnd,
  rgbColor)` (and a thin `display.drawHLineOfColor` wrapper, or
  horizontal-detection inside the existing line primitive). It fast-loops
  only while the run stays within a single unrotated panel row; at a
  panel boundary or under rotation it falls back to per-pixel
  `drawPixelAtRC` (still correct, just not accelerated).
- Wire the display-layer horizontal-line and rectangle-fill primitives to
  delegate to it.

**Integration points.** New public method on `screenUtils`; new/updated
public method on `display`. This is the only API-surface-adding package
— README + THEOPS document it (§6).

**Verification.** *Normal:* a run within one unrotated panel produces
byte-identical output to N `drawPixelAtRC` calls, faster. *Edge:* a run
spanning a panel boundary, and a run on a rotated panel, fall back and
still match per-pixel output. *Error:* `colStart > colEnd`, and
off-screen coordinates, clamp to the same bounds as `drawPixelAtRC`
(no out-of-buffer write).

---

### 6. Documentation & authoring-guide conformance

**Why.** Keeping project docs current is a sprint deliverable, not an
afterthought; and all new code must meet the mandatory style guide.

**Target.**
- **`ChangeLog.md`** — a new entry under this sprint's build (number set
  at `sprint-start`), stacked above the reconciliation sprint's
  `[3.0.3]`, recording the draw-path optimization, the new fill API, and
  the timing demo. Detailed authoring is owned by `build-wrapup`; the
  entry must exist and capture the headline.
- **`THEOPS.md`** (spec / theory-of-operations) — document the chain-config
  cache, the color LUT and its rebuild triggers, the single-panel fast
  path, the run-fill primitive, and the timing-instrumentation flag, in
  driver-internals terms. Explicitly cross-reference
  `DOCs/plans/Sprint-Performance-Upgrade.md` and state the axis
  distinction: **that** doc optimizes the PASM2/BCM **output/refresh**
  path; **this** sprint optimizes the Spin2 **draw/authoring** path —
  orthogonal, composable.
- **`README.md`** — document the new public `fillRowRun` /
  `drawHLineOfColor` API in the API/configuration guide, and mention the
  `demo_hub75_drawPerf.spin2` timing demo + its `ENABLE_DRAW_TIMING`
  flag.
- **Authoring-guide conformance** — all new code conforms to
  `DOCs/policy/SPIN2-AUTHORING-GUIDE.md`: single exit point, named CONs
  for LUT size / channel count / shift bias (no magic numbers),
  descriptive return-var names (never `result`), `''` PUB / `'` PRI docs
  with `@local` tags, PUB-before-PRI, file-layout order, ASCII-only. The
  new perf demo follows the demo-file conventions (own `_clkfreq` /
  `DEBUG_BAUD` CON block).

**Verification.** *Normal:* docs build/read clean and describe the
shipped behavior. *Edge:* the THEOPS cross-reference correctly
distinguishes the two performance axes so a reader does not conflate
them. *Error:* a `pnut-ts` recompile of all demos stays 0-warning after
doc/comment regeneration (comments never change emitted code).

---

## Explicitly Out of Scope (surfaced, not silently dropped)

- **3-arg `drawPixelAtRC` back-compat overload.** The reference demo
  calls `drawPixelAtRC(row, col, color)` (3 args); the current API is
  `drawPixelAtRC(nChainIdx, row, col, color)` (4 args). A convenience
  overload defaulting `nChainIdx` to chain 0 would let legacy
  single-panel sketches compile unchanged. It is an API-compatibility
  concern, not a performance one, and is **not** in this sprint's scope —
  flagged here for Stephen's awareness as a possible separate follow-up.
- **PASM2 / BCM refresh-rate work** — owned by
  `DOCs/plans/Sprint-Performance-Upgrade.md`; a different axis.

---

## Relationship to Outstanding Work (todo-mcp)

The active todo project is the **SOURCE-RECONCILIATION sprint (3.0.3)**.
§2–§4c are complete; pending are §5a (docs), §5b (hardware verify),
§5c (push origin/main + delete `develop`), and a §0-priority follow-up
(DEBUG_MASK channelization). Assessed against this plan:

| Outstanding task | Relationship | Action |
|---|---|---|
| **§5c** push unified `main`, delete `develop` | **Hard predecessor.** Per Stephen's sequencing choice, this sprint forks from the *pushed* unified main. | This sprint starts only after §5c lands. |
| **§5a** docs reconciliation (ChangeLog `[3.0.3]`, THEOPS, README) | **Same files, no content collision.** §5a documents the 3.0.3 merge; this sprint's §6 stacks a new ChangeLog entry and adds new THEOPS/README sections above it. | Do §5a first (it's a predecessor via §5c). No rework. |
| **§5b** hardware verify (merge features) | **Fully independent — and now decoupled by rig, too.** §5b needs the real HUB75 panel rig (visual feature verification). This sprint's §1 timing capture needs only a **bare P2 on USB** (HUB75 is write-only / panel-independent), so it does **not** wait on the panel rig. | No shared dependency; capture §1 numbers anytime a P2 is attached. |
| **Follow-up: DEBUG_MASK channels** | **File co-location + methodological synergy, not conflict.** DEBUG_MASK phase-1 channelizes diagnostics in `isp_hub75_panel.spin2`/`hwBufferAccess` `dbgMemDump`; this sprint adds CON-gated DEBUG **timing** output (§1). Both pursue "compile-time-gated, zero-cost-when-off DEBUG." | Name §1's timing flag/channel so it can fold into `DEBUG[DBG_TIMING]` if DEBUG_MASK lands; note the shared `{Spin2_v46}` prereq. Coordinate, don't duplicate. |

**Net:** no work package in this plan overlaps or duplicates an
outstanding todo task. The only hard coupling is sequencing — this sprint
executes after the reconciliation sprint's §5c close-out — plus two soft
synergies (batch hardware sessions; align DEBUG-gating style with the
DEBUG_MASK follow-up).

---

## Open Questions

None outstanding. The three scope decisions (which optimizations,
sequencing, proof method) were resolved with Stephen during planning;
remaining design choices (single shared LUT, DAT singleton storage,
eager-with-lazy-fallback cache population) are author decisions recorded
in the work packages above.
