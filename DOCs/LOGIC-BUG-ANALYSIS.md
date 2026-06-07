# Logic-Bug Analysis - HUB75 Driver

Logic defects found while auditing the unified tree during the **§4c authoring-guide
conformance pass** (source-reconciliation sprint, build 3.0.3). These are *behavior*
bugs (wrong results), distinct from style/conformance findings and from the deferred
optimizations in `TECHNICAL_DEBT.md`.

**Purpose:** so Stephen can verify each outcome when he returns to the project.
Container work is compile-only -- several fixes can only be *confirmed* by flashing
the relevant demo to real panels (macOS side, sprint task §5b). Each entry says how.

Status legend: **FIXED** (applied + compiles clean) / **PROPOSED** (needs a decision before applying).

---

## The recurring pattern: "clamp computed, raw value used"

Four of the five bugs are the same shape -- a value is clamped/bounded into a
variable, then the **raw unclamped input** is used downstream, so the clamp silently
does nothing. A full sweep of every `lo #> x <# hi` clamp site in the driver was done;
all other clamp sites correctly use their clamped result (the clamped value is either
written back to the same variable or consumed downstream).

---

### LB-1 - scrollingText.configureScrollLoopCount: scroll-count clamp bypassed

- **Status:** FIXED (commit `1c19672`)
- **File:** `isp_hub75_scrollingText.spin2` (configureScrollLoopCount)
- **Symptom:** `SCROLL_N_TIMES` with a count outside 0..10 scrolls the wrong number of times (no upper bound enforced).
- **Root cause:** computed `validCount := 0 #> count <# 10` but then assigned `scrollNbrTimes := count` (raw).
- **Fix:** assign `scrollNbrTimes := validCount`.
- **Verify on hardware:** set a scroll region to `SCROLL_N_TIMES` with count = 50; text must scroll the clamped 10 times, not 50.

### LB-2 - display.drawPanelLineOfColor: panel-index clamp bypassed

- **Status:** FIXED (commit `1c19672`)
- **File:** `isp_hub75_display.spin2` (drawPanelLineOfColor)
- **Symptom:** an out-of-range `panelIndex` is not clamped before computing the panel offset.
- **Root cause:** computed `desiredPanelIndex := 0 #> panelIndex <# maxPanels-1` but passed raw `panelIndex` to `offsetToPanel`.
- **Fix:** pass `desiredPanelIndex`.
- **Verify on hardware:** call `drawPanelLineOfColor` with `panelIndex` = maxPanels+2; line must draw on the last valid panel, not off-display.

### LB-3 - display.scrollColoredTextOnLnOfNPanels: panel-index clamp bypassed

- **Status:** FIXED (this work)
- **File:** `isp_hub75_display.spin2:716` (scrollColoredTextOnLnOfNPanels)
- **Symptom:** same class as LB-2, in the multi-panel scrolling path.
- **Root cause:** computed `boundedPanelIdx := 0 #> panelIndex <# maxPanels-1` but passed raw `panelIndex` to `offsetToPanel`.
- **Fix:** pass `boundedPanelIdx`.
- **Note:** the sibling calls in `fillPanel` and `drawPanelBoxOfColor` pass raw `panelIndex` too, but they compute *no* local clamp -- they rely on `offsetToPanel`'s own internal clamp, which is consistent and was left as-is.
- **Verify on hardware:** multi-panel scroll with an out-of-range starting panel index; scroll must land on a valid panel.

### LB-4 - hwBufferAccess.indexToPanel: wrong clamp bounds + swapped return capture

- **Status:** FIXED (this work)
- **File:** `isp_hub75_hwBufferAccess.spin2` (indexToPanel)
- **Severity note:** this PUB method currently has **no callers** -- it is a latent bug in unused public API. It was being cleaned up (a genuinely-unused local removed) when the deeper defect surfaced.
- **Symptom:** `indexToPanel(chain, panelRow, panelCol)` returns a wrong panel index for any multi-panel grid.
- **Root cause (two faults):**
  1. The panel-grid coordinates were clamped against **pixel** dimensions: `nPanelRow` (a panel-row index) was clamped to `rowsPerPnl-1` (panel pixel height, e.g. 63) and `nPanelCol` to `colsPerPnl-1` (pixel width). They should be clamped to the panel-grid size.
  2. `displaySizeInPanels()` returns `(nPanelsPerColumn, nPanelsPerRow)`, but the call captured `panelsPerRow, _ := displaySizeInPanels(...)`, placing the *column* count into a variable named `panelsPerRow` and discarding the row count -- so the row-major stride was wrong.
- **Fix:** capture both returns in the correct order and clamp to grid size:
  ```
  panelsPerColumn, panelsPerRow := displaySizeInPanels(nChainIdx)
  nBffrR := 0 #> nPanelRow <# panelsPerColumn - 1
  nBffrC := 0 #> nPanelCol <# panelsPerRow - 1
  nPanelIndex := (nBffrR * panelsPerRow) + nBffrC
  ```
  (The now-unneeded `panelSizeInPixels` call and pixel locals were removed.)
- **Verify:** when a caller is added, on a 2x2 grid `indexToPanel(c, 0,0)=0`, `(0,1)=1`, `(1,0)=2`, `(1,1)=3`.

### LB-5 - 7seg.reconfigureForDigit: out-of-bounds table read on sentinel value

- **Status:** FIXED (this work)
- **File:** `isp_hub75_7seg.spin2:198` (reconfigureForDigit)
- **Symptom:** the **first time** a digit is shown (transitioning from the initial `DIGIT_NO_VALUE = -2`), the "from-segments" bitmask is read from `segmentsByDigit[-2]` -- two bytes *before* the table -- so the first digit's segment show/hide can be wrong (stray segments lit or missing).
- **Root cause:** `fromSegments := BYTE[@segmentsByDigit][currValue]` with no guard; `currValue` can be the sentinel `DIGIT_NO_VALUE (-2)` or `DIGIT_HIDDEN (-1)`, not just 0-9.
- **Fix:** default `fromSegments := 0` (nothing showing yet) and only index the table when `currValue >= 0`.
- **Verify on hardware:** run the 7-segment demo; the first digit drawn must render cleanly with no stray/missing segments.

---

## NOTE - multi2x2panel.placeDigit (structural, not a logic bug)

`demo_hub75_multi2x2panel.spin2` `placeDigit` had an early `return` mid-method that
made a second drawing block unreachable. Fixed for single-exit (commit `1c19672`) by
removing the `return` **and** the unreachable block, which **preserves current
behavior** (two boxes drawn). **Open question for Stephen:** was the unreachable block
the *intended* second half of the digit (i.e., should it have been *enabled* instead)?
If so, this is a demo-completion change, not a conformance fix. Visual call only.

---

## FORWARDING NAME-MATCH (consistency fix, not a logic bug)

Per the rule that interface-forwarded constants must keep the **same name** through
every layer: `isp_hub75_rgb3bit.spin2` forwarded `hwEnum.PINS_*` under renamed
identifiers `PIN_GROUP_*`. Renamed to `PINS_*` (definitions + case labels) so a
consumer sees the same constant name as the source. `hwBufferAccess` and `display`
forwarding blocks already matched. **Status: FIXED (this work).**

---

## PG-1 - Pin-group enum structure (APPLIED)

- **Status:** APPLIED (this work). Decided with Stephen: keep a stride enum and carry
  the pin range in each name (no comments needed for the names; less developer math).
  Final names: `PIN_GROUP_P0_P15`, `PIN_GROUP_P16_P31`, `PIN_GROUP_P32_P47` (stride
  16). `P48_P63` dropped (reserved pins) with a single comment by the enum explaining
  why. Touched files: `hwEnums` (enum), `rgb3bit` (forwarding defs + dispatch `case`,
  3 arms), `hwBufferAccess` (pin-base **validation** `case` -- now correctly rejects
  the previously-accepted P8_P23/P40_P55), `hwPanelConfig` + `hwGeometry` (config
  refs, also fixed a `PINs` casing typo), `anlyCheck` (its standalone local copy).
  All 28 compile clean. **Note:** valid configs are functionally unchanged (the kept
  groups keep values 0/16/32); only invalid options were removed. **Hardware-verify**
  on macOS (§5b): a card on each of the 3 groups drives correctly; an invalid pin base
  aborts with the validation message.
- **Follow-on (not done):** `rgb3bit` `bSetMidPins` is now never set TRUE (it only
  served the removed 8-offset groups). The `elseif bSetMidPins` branch and its PASM
  check are harmlessly never-taken dead logic; removing them is cog-code surgery best
  done with hardware in hand -- left for a later careful pass.
- **Domain facts (from Stephen):** P2 Eval add-on boards consume either **8 adjacent
  pins** (one header) or **16 adjacent pins** (two adjacent headers). Pin groups are
  fixed, anchored at pin 0: **8-pin groups** every 8 (P0_P7, P8_P15, ...), **16-pin
  groups** every 16 (P0_P15, P16_P31, P32_P47, P48_P63). **HUB75 boards are 16-pin
  boards.** The fourth 16-pin group, **P48_P63, lands on RESERVED P2 pins and is NOT
  usable** by HUB75. So there are exactly **three valid pin groups** -- P0_P15,
  P16_P31, P32_P47 -- and the driver supports one HUB75 card per group (up to 3 cards,
  matching the documented "up to 3 HUB75 adapters"). This is why the config files
  reject P48 ("validation will FAIL") and why P24_P39 was never offered.
- **Current state:** `isp_hub75_hwEnums.spin2` defines a 7-entry enum with stride 8:
  ```
  #0[8], PINS_P0_P15, PINS_P8_P23, PINS_P16_P31, PINS_P24_P39, PINS_P32_P47, PINS_P40_P55, PINS_P48_P63
  ```
  This mixes the valid groups with three **8-offset 16-spans** (`PINS_P8_P23`=8,
  `PINS_P24_P39`=24, `PINS_P40_P55`=40) that are not valid 16-pin mount positions, and
  it still lists the reserved `PINS_P48_P63`. The names also read as raw pin numbers --
  nothing signals "pin-group selector," and the always-16 span is spelled redundantly.
- **Proposed fix (naming + structure):** define only the three valid groups, named by a
  group prefix + base pin (span implied, value = base pin); drop the reserved P48:
  ```
  PIN_GROUP_P0   = 0     ' HUB75 card on pins P0..P15
  PIN_GROUP_P16  = 16    ' HUB75 card on pins P16..P31
  PIN_GROUP_P32  = 32    ' HUB75 card on pins P32..P47
  ```
  Then update the dependent `case` in `isp_hub75_rgb3bit.spin2` (which forwards the
  same names per the name-match rule) and the `ADAPTER_BASE_PIN = hwEnum.PIN_GROUP_*`
  references in `isp_hub75_hwPanelConfig.spin2` and `demo_hub75_hwGeometry.spin2`.
  Optional: keep a `PIN_GROUP_P48_RESERVED` sentinel only if validation should emit a
  friendly "reserved pins" message.
- **Why deferred:** coordinated rename across ~4 files that touches pin-base validation;
  also confirm whether a P48 sentinel is wanted for validation messaging. **Decision
  needed before applying.** (Supersedes the earlier `PINS_*` rename in rgb3bit, which
  was an interim name-match fix.)

---

*Generated during the source-reconciliation sprint §4c pass, 2026-06-06.*
