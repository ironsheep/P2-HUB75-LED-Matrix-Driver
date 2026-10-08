# Technical Debt - P2 HUB75 LED Matrix Driver

This document tracks known technical debt and potential future optimizations.

---

## TD-001: Wire Order Table - Preprocessor Optimization

**Status:** Retired in 4.0.0 (October 2026).

**Why retired:** the debt was the code that computed a wire-order table at startup from the two wire-pattern settings, and the idea of compiling it out for simple grids. That table, the settings and the code that built it are gone. Wiring is now described by one sentence per panel and decoded once at startup into lookup tables (see the [Wiring Guide](WiringGuide.md)), so there is no wire-order table left to optimise.

---

## TD-002: Documentation Gap - No Documentation Index

**Date Identified:** January 2025

**Current State:**

The project documentation is two groups.

**Driver and configuration (user-facing):**
- `README.md` and `THEOPS.md` - overview, driver file organization, glossary, configuration, driver internals
- `DOCs/WiringGuide.md` - the wiring sentences, driver limits, refresh rate
- `DOCs/ChipCharacteristicsMatrix.md` - per-chip ratings and behaviour
- `DOCs/AuthorTestConfigurations.md`, `DOCs/MultiPanelConfiguration.md` - panel configurations

**Reference and analysis:**
- `DOCs/TheoryOfOperations.md` - system architecture, data flow, the pixel write and screen commit paths, timing
- `HUB75-Driver-SWver0.md`, `HUB75-Driver-SWver1.md` - chip configuration and timing details of the earlier driver versions
- `DOCs/ICN2037/README.md` - chip reference with timing budgets and signal path analysis
- `DOCs/plans/archive/` - sprint plans and research, including `Sprint-2x2-Panel-Repair.md` and `THEORY_OF_OPERATIONS_SIGNALING.md`

**The Gap:**

1. **No index:** there is no `DOCs/README.md` saying what each document covers or in what order to read them. A new reader finds `README.md` and `THEOPS.md` and can miss the chip references and `DOCs/TheoryOfOperations.md`.
2. **Chip timing in several places:** `HUB75-Driver-SWver1.md`, `DOCs/ICN2037/README.md` and `DOCs/ChipCharacteristicsMatrix.md` each carry chip timing. The matrix is the one place for the datasheet clock and /OE ratings; the other two predate it.
3. **Reference material left in archived plans:** the signal-chain timing in `DOCs/plans/archive/Sprint-2x2-Panel-Repair.md` and the pin and flag analysis in `DOCs/plans/archive/THEORY_OF_OPERATIONS_SIGNALING.md` have not been extracted into a permanent document.

**Recommended Consolidation:**

1. **Create `DOCs/README.md`** as an index describing the available documentation and a recommended reading order
2. **Cross-reference** the chip timing in `HUB75-Driver-SWver1.md` and `DOCs/ICN2037/README.md` to the matrix's ratings table
3. **Extract permanent reference material** (the signal-chain timing, checked against the current refresh core) from the archived plans into a permanent document

**Trade-offs:**
- Pro: Users can find the appropriate level of detail for their needs
- Pro: One home for each fact improves maintainability
- Con: Requires time investment to consolidate
- Con: Risk of introducing inconsistencies during the merge

**Decision:**
Deferred. The wiring sentences replaced the orientation system the archived 2x2 research describes, so only its signal-chain timing material is worth extracting.

**Related Files:**
- `THEOPS.md` - Primary user-facing driver document
- `DOCs/TheoryOfOperations.md` - Detailed architecture doc
- `DOCs/ChipCharacteristicsMatrix.md` - Chip ratings
- `DOCs/ICN2037/README.md` - Chip reference doc
- `HUB75-Driver-SWver0.md`, `HUB75-Driver-SWver1.md` - Version-specific timing docs
- `DOCs/plans/archive/Sprint-2x2-Panel-Repair.md` - Research (contains extractable signal-chain timing)

---

## TD-003: Panel Routine Parameter Order Inconsistency

**Date Identified:** January 2025

**Current Implementation:**
Panel-relative routines in `isp_hub75_display.spin2` have inconsistent parameter ordering. Most have `panelIndex` as the first parameter, others have it later:

- `fillPanel(panelIndex, rgbColor)` - panel index FIRST ✓
- `homeCursorOnPanel(panelIndex)` - panel index FIRST ✓
- `drawPanelBox(panelIndex, topRow, leftColumn, width, height, filled)` - panel index FIRST ✓
- `drawPanelBoxOfColor(panelIndex, topRow, leftColumn, width, height, filled, rgbColor)` - panel index FIRST ✓
- `drawPanelLine(panelIndex, fmRow, fmColumn, toRow, toColumn)` - panel index FIRST ✓
- `setCursorOnPanel(line, column, panelIndex)` - panel index LAST ✗
- `scrollTextOnLnOfNPanels(line, panelIndex, panelCount, pZString, direction)` - panel index SECOND ✗ (so is `scrollColoredTextOnLnOfNPanels`)

**Desired Standard:**
All panel-relative routines should have `panelIndex` as their **first parameter** for consistency and API clarity. This makes it immediately clear which routines are panel-relative vs display-relative.

**Affected Routines:**
- `setCursorOnPanel(line, column, panelIndex)` → should be `setCursorOnPanel(panelIndex, line, column)`
- `scrollTextOnLnOfNPanels` and `scrollColoredTextOnLnOfNPanels`, with `panelIndex` after `line`

**Trade-offs:**
- Pro: Consistent API, easier to remember parameter order
- Pro: Clear visual distinction: panel routines start with panelIndex
- Con: Breaking change for existing code using these routines
- Con: Requires updating all call sites

**Decision:**
Deferred. Fix when doing a larger API cleanup pass. Document the standard for new routines.

**Related Files:**
- `isp_hub75_display.spin2` - Contains panel drawing routines
- `demo_hub75_quadPanel.spin2`, `demo_hub75_numberPanels.spin2`, `demo_hub75_multiPanel.spin2` - Example call sites

---

## TD-004: 7seg Demo Column Thresholds Need a Geometry Check

**Date Identified:** June 2026

**Current Implementation:**
`demo_hub75_7seg.spin2` names its display-width thresholds `WIDTH_FOR_4_DIGITS = 32`, `WIDTH_FOR_6_DIGITS = 64` and `WIDTH_FOR_8_DIGITS = 96`, with digit columns placed from `DIGIT_COLUMN_A..D` and a second-panel offset `PANEL_WIDTH = 64`. The seconds dots on the second panel are drawn when `hub75Bffrs.maxDisplayColumns(chainIndex) > WIDTH_FOR_8_DIGITS` (in `showSecondsDots()`). Each threshold lies below the left column of the next digit pair (digits C and D at 35 and 50, the second panel's digits A and B at 66 and 81, its C and D at 99 and 114), which reads as intended. The demo assumes 64-column panels, so the thresholds and `PANEL_WIDTH` are not derived from the configured panel width.

**Trade-offs:**
- Pro (fix): derive the thresholds and `PANEL_WIDTH` from the panel width (`hub75Bffrs.columnsPerPanel()`), so the demo follows a wider panel
- Con (defer): no observed misbehavior; the demo has not been run on a chain of three or more panels

**Decision:**
Deferred. Revisit when the 7seg demo is next exercised on a wide multi-panel chain.

**Related Files:**
- `demo_hub75_7seg.spin2` - the width thresholds and `PANEL_WIDTH`
- `isp_hub75_hwBufferAccess.spin2` - `maxDisplayColumns()` / `columnsPerPanel()` accessors

---

## Template for Future Entries

```
## TD-XXX: Brief Title

**Date Identified:** Month Year

**Current Implementation:**
Description of current approach.

**Potential Optimization:**
Description of possible improvement.

**Trade-offs:**
- Pro: ...
- Con: ...

**Decision:**
Status and rationale.

**Related Files:**
- file1.spin2
- file2.spin2
```
