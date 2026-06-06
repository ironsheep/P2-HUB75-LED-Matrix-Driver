# Technical Debt - P2 HUB75 LED Matrix Driver

This document tracks known technical debt and potential future optimizations.

---

## TD-001: Wire Order Table - Preprocessor Optimization

**Date Identified:** January 2025

**Current Implementation:**
The wire order configuration system uses runtime computation in `buildWireOrderFromEnums()` to generate the wire order lookup table from `WIRE_START` and `WIRE_TRAVERSE` enum settings. This approach:
- Computes the wire order table at startup via `configure()`
- Supports both enum-based configuration (rectangular grids) and explicit grid mode (non-rectangular shapes)
- Auto-detects configuration mode by checking enum value ranges ($40+ = enums, 0-16 = explicit)

**Potential Optimization:**
Using preprocessor directives (`#if`, `#ifdef`) could eliminate runtime computation for simple rectangular grid cases, saving approximately 240 bytes of code space:

- `buildWireOrderFromEnums()` function: ~120 bytes
- `wirePositionToGridCoords()` helper: ~120 bytes

**Implementation Notes:**
Both FlexProp and PNut/PNut-ts support `#if` and `#ifdef` preprocessor directives. A conditional compile approach could:
1. Pre-compute wire order tables at compile time for common configurations
2. Only include runtime computation code when explicit grid mode is detected
3. Use simple pattern: `#if DISP0_WIRE_START >= $40` to detect enum mode

**Trade-offs:**
- Pro: Saves ~240 bytes of hub RAM
- Pro: Slightly faster startup (no runtime table computation)
- Con: Adds preprocessor complexity
- Con: Less flexible for future dynamic configuration changes

**Decision:**
Deferred. Current runtime approach is simpler and the 240-byte savings is not critical. Revisit if memory pressure becomes an issue.

**Related Files:**
- `isp_hub75_hwBufferAccess.spin2` - Contains `buildWireOrderFromEnums()` and `wirePositionToGridCoords()`
- `isp_hub75_hwPanelConfig.spin2` - Contains `DISPx_WIRE_START` and `DISPx_WIRE_TRAVERSE` constants
- `isp_hub75_hwEnums.spin2` - Contains wire pattern enum definitions

---

## TD-002: Documentation Gap - Theory of Operations Consolidation

**Date Identified:** January 2025

**Current State:**

The project has two parallel sets of Theory of Operations documentation:

**User-authored (practical, user-facing):**
- `THEOPS.md` - Main theory of operations, driver architecture overview, configuration guide
- `HUB75-Driver-SWver0.md` - v0.x chip configuration and timing details
- `HUB75-Driver-SWver1.md` - v1.x updated driver settings

**Claude-generated (technically detailed, reference-oriented):**
- `Docs/TheoryOfOperations.md` - Deep dive on system architecture, data flow, PWM mechanism, buffer architecture
- `Docs/CodeAssessment.md` - Code organization analysis, performance notes, 2D support assessment
- `Docs/ICN2037/README.md` - Comprehensive chip reference with timing budgets, signal path analysis
- `Docs/plans/Sprint-2x2-Panel-Repair.md` - Research findings on refresh loop, orientation system, signal polarity

**The Gap:**

1. **Depth vs. Accessibility:** Claude-generated docs contain detailed technical analysis (timing calculations, signal path budgets, PASM2 loop tracing) that isn't reflected in user-facing docs. User docs are more approachable but lack this depth.

2. **Version Drift:** User docs reference older file names (`isp_hub75_hwGeometry.spin2`) and may not reflect current architecture changes (2D grid support, wire order enums, per-panel rotation).

3. **Fragmentation:** Related information is scattered across multiple files. For example:
   - PWM/BCM explanation partially in THEOPS.md, fully detailed in Docs/TheoryOfOperations.md
   - Chip timing in HUB75-Driver-SWver1.md AND Docs/ICN2037/README.md
   - Orientation system only documented in Sprint-2x2-Panel-Repair.md

4. **Discoverability:** New users would find THEOPS.md but miss the detailed chip references and architecture docs in Docs/ subdirectory.

**Recommended Consolidation:**

1. **Update THEOPS.md** with current file names and 2D grid support information
2. **Cross-reference** user docs to detailed Docs/ references where appropriate
3. **Extract permanent reference material** from Sprint-2x2-Panel-Repair.md (e.g., three-tier orientation system, timing calculations) into appropriate permanent docs
4. **Create Docs/README.md** index file describing available documentation and recommended reading order

**Trade-offs:**
- Pro: Unified documentation improves maintainability
- Pro: Users can find appropriate detail level for their needs
- Con: Requires time investment to consolidate
- Con: Risk of introducing inconsistencies during merge

**Decision:**
Deferred until 2x2 panel repair is complete. The Sprint plan contains valuable research that should be preserved, but consolidation should wait until the implementation validates the findings.

**Related Files:**
- `THEOPS.md` - Primary user-facing theory doc
- `HUB75-Driver-SWver0.md`, `HUB75-Driver-SWver1.md` - Version-specific timing docs
- `Docs/TheoryOfOperations.md` - Detailed architecture doc
- `Docs/CodeAssessment.md` - Code analysis doc
- `Docs/ICN2037/README.md` - Chip reference doc
- `Docs/plans/Sprint-2x2-Panel-Repair.md` - Current research (contains extractable reference material)

---

## TD-003: Panel Routine Parameter Order Inconsistency

**Date Identified:** January 2025

**Current Implementation:**
Panel-relative drawing routines in `isp_hub75_display.spin2` have inconsistent parameter ordering. Some routines have `panelIndex` as the first parameter, others have it later:

- `fillPanel(panelIndex, color)` - panel index FIRST ✓
- `setCursorOnPanel(line, col, panelIndex)` - panel index LAST ✗
- `drawPanelBoxOfColor(panelIndex, row, col, w, h, filled, color)` - panel index FIRST ✓
- `drawPanelBox(panelIndex, row, col, w, h, filled)` - panel index FIRST ✓

**Desired Standard:**
All panel-relative routines should have `panelIndex` as their **first parameter** for consistency and API clarity. This makes it immediately clear which routines are panel-relative vs display-relative.

**Affected Routines:**
- `setCursorOnPanel(line, col, panelIndex)` → should be `setCursorOnPanel(panelIndex, line, col)`
- Any other panel routines with panelIndex not in first position

**Trade-offs:**
- Pro: Consistent API, easier to remember parameter order
- Pro: Clear visual distinction: panel routines start with panelIndex
- Con: Breaking change for existing code using these routines
- Con: Requires updating all call sites

**Decision:**
Deferred. Fix when doing a larger API cleanup pass. Document the standard for new routines.

**Related Files:**
- `isp_hub75_display.spin2` - Contains panel drawing routines
- `demo_hub75_multi2x2panel.spin2` - Example call sites

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
