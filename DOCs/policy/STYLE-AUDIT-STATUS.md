# Style Audit Status

Audit of all `driver/*.spin2` files against `SPIN2-AUTHORING-GUIDE.md`, performed 20 Mar 2026.

**Purpose:** Capture current state so we can decide what to fix in code vs. what to revise in the guide.

Legend: The **Decision** column is for you to fill in as you triage.

| Decision Value | Meaning |
|---|---|
| `FIX` | Will fix in code |
| `REVISE` | Will revise the guideline instead |
| `DEFER` | Not addressing now |
| `SKIP` | Not applicable to this codebase |
| *(blank)* | Not yet triaged |

---

## Table of Contents

- [1. Pervasive Issues](#1-pervasive-issues)
  - [1.1 Block Declaration Labels (Rule 4.5)](#11-block-declaration-labels-rule-45)
  - [1.2 PUB Method Documentation (Rule 4.3)](#12-pub-method-documentation-rule-43)
  - [1.3 PRI Method Documentation (Rule 4.4)](#13-pri-method-documentation-rule-44)
  - [1.4 Magic Numbers (Rule 5.7)](#14-magic-numbers-rule-57)
  - [1.5 File Layout Order (Rule 3.1)](#15-file-layout-order-rule-31)
- [2. Moderate Issues](#2-moderate-issues)
  - [2.1 Object Constants Copied Locally (Rule 2.4)](#21-object-constants-copied-locally-rule-24)
  - [2.2 Return Variables Not Assigned Default (Rule 5.1)](#22-return-variables-not-assigned-default-rule-51)
  - [2.3 Enum Groups Missing Group Comments (Rule 4.7)](#23-enum-groups-missing-group-comments-rule-47)
  - [2.4 PRI Methods Using '' Instead of ' (Rule 4.1)](#24-pri-methods-using--instead-of--rule-41)
  - [2.5 PUB/PRI Interleaved (Rule 3.2)](#25-pubpri-interleaved-rule-32)
  - [2.6 Non-Descriptive or Single-Letter Names (Rules 2.1, 2.2)](#26-non-descriptive-or-single-letter-names-rules-21-22)
  - [2.7 Multiple Exit Points (Rule 5.2)](#27-multiple-exit-points-rule-52)
- [3. Isolated Issues](#3-isolated-issues)
  - [3.1 File Header Mismatches (Rule 4.2)](#31-file-header-mismatches-rule-42)
  - [3.2 Code Before Doc-Comment (Rule 4.3)](#32-code-before-doc-comment-rule-43)
  - [3.3 Stale or Incorrect Documentation](#33-stale-or-incorrect-documentation)
  - [3.4 Unused Local Variables](#34-unused-local-variables)
  - [3.5 Possible Typo in Color Constant](#35-possible-typo-in-color-constant)
- [4. Undocumented Conventions in the Code](#4-undocumented-conventions-in-the-code)
  - [4.1 File Naming Convention](#41-file-naming-convention)
  - [4.2 null() Guard Method on Non-Top-Level Objects](#42-null-guard-method-on-non-top-level-objects)
  - [4.3 Variable Type-Prefix System](#43-variable-type-prefix-system)
  - [4.4 Color Constant Naming: c Prefix with camelCase](#44-color-constant-naming-c-prefix-with-camelcase)
  - [4.5 OBJ Instance Naming Convention](#45-obj-instance-naming-convention)
  - [4.6 Clock and Debug Configuration Pattern](#46-clock-and-debug-configuration-pattern)
  - [4.7 Driver Initialization Sequence](#47-driver-initialization-sequence)
  - [4.8 Startup Failure Guard Pattern](#48-startup-failure-guard-pattern)
  - [4.9 stop() Guard Pattern](#49-stop-guard-pattern)
  - [4.10 waitSec() Helper Pattern](#410-waitsec-helper-pattern)
  - [4.11 commitScreenToPanelSet() as Final Draw Call](#411-commitscreentopanelset-as-final-draw-call)
  - [4.12 chainIndex/instanceID as Standard Instance Variables](#412-chainindexinstanceid-as-standard-instance-variables)
  - [4.13 nChainIdx as Standard First Parameter](#413-nchainidx-as-standard-first-parameter)
  - [4.14 Debug Message Prefixes by Object](#414-debug-message-prefixes-by-object)
  - [4.15 DISPn_ Naming for Multi-Adapter Constants](#415-dispn_-naming-for-multi-adapter-constants)
  - [4.16 User-Configurable Section Markers](#416-user-configurable-section-markers)
  - [4.17 Block-Comment Toggle for Optional Code](#417-block-comment-toggle-for-optional-code)
  - [4.18 Bounds Clamping Idiom](#418-bounds-clamping-idiom)
  - [4.19 License Block Exact Format](#419-license-block-exact-format)
  - [4.20 Indentation: 4-Space, No Tabs](#420-indentation-4-space-no-tabs)
  - [4.21 Hex Case Convention](#421-hex-case-convention)
  - [4.22 CON Section Labels as Method-Group Dividers](#422-con-section-labels-as-method-group-dividers)
  - [4.23 DAT String Tables Format](#423-dat-string-tables-format)
  - [4.24 Gamma Table Layout Convention](#424-gamma-table-layout-convention)
  - [4.25 CMD_ Prefix for Cog Command Enums](#425-cmd_-prefix-for-cog-command-enums)
  - [4.26 VAR Block Starts with cog and chainIndex](#426-var-block-starts-with-cog-and-chainindex)
  - [4.27 hub75Bffrs as Universal Shared-State Accessor](#427-hub75bffrs-as-universal-shared-state-accessor)
  - [4.28 Inline PASM2 Structure](#428-inline-pasm2-structure)

---

## 1. Pervasive Issues

These appear in nearly every file and represent the bulk of the work.

---

### 1.1 Block Declaration Labels (Rule 4.5)

**Rule:** CON/DAT/VAR/OBJ declaration lines must use `'` (single apostrophe) for the inline label, not `{ }` (block comment). The label text appears in the VS Code Outline panel.

**Current state:** ~~Every file uses `{ }` format.~~ **FIXED 20 Mar 2026.** All 24 files updated to use `' label` format.

**Decision:** FIX (completed)

| File | Occurrences | Notes |
|------|:-----------:|-------|
| demo_hub75_color.spin2 | 7 | lines 15, 20, 47, 217, 680, 728, 906 |
| demo_hub75_text.spin2 | 4 | lines 15, 20, 127, 170 |
| demo_hub75_5x7font.spin2 | 3 | lines 15, 20, 181 |
| demo_hub75_7seg.spin2 | 4 | lines 15, 20, 24, 212 |
| demo_hub75_colorPad.spin2 | 5 | lines 15, 42, 202, 706, 843 |
| demo_hub75_hwGeometry.spin2 | 2 | lines 20, 328 |
| demo_hub75_multiPanel.spin2 | 5 | lines 15, 21, 45, 135, 246 |
| demo_hub75_scroll.spin2 | 4 | lines 15, 20, 134, 177 |
| isp_hub75_display.spin2 | 5 | lines 14, 48, 58, 89, 296 |
| isp_hub75_panel.spin2 | 5 | lines 16, 20, 25, 580, 635 |
| isp_hub75_rgb3bit.spin2 | 5 | lines 15, 19, 33, 725, 1206 |
| isp_hub75_screenUtils.spin2 | 3 | lines 14, 17, 72 |
| isp_hub75_color.spin2 | 1 | line 14 |
| isp_hub75_colorUtils.spin2 | 1 | line 14 |
| isp_hub75_fonts.spin2 | 1 | line 14 |
| isp_hub75_hwEnums.spin2 | 1 | (various CON section labels) |
| isp_hub75_hwPanelConfig.spin2 | 1 | line 18 |
| isp_hub75_hwBufferAccess.spin2 | 3+ | multiple CON/OBJ/DAT labels |
| isp_hub75_hwBuffers.spin2 | 2+ | multiple labels |
| isp_hub75_scrollingText.spin2 | 4 | lines 14, 34, 41, 45 |
| isp_hub75_display_bmp.spin2 | 3 | lines 15, 21, 167 |
| isp_hub75_7seg.spin2 | 3 | lines 14, 28, 41 |
| isp_hub75_segment.spin2 | 2 | lines 27, 43 |
| isp_hub75_anlyCheck.spin2 | 3 | lines 15, 20, 24 |

**Effort estimate:** Mechanical find/replace. Low risk.

---

### 1.2 PUB Method Documentation (Rule 4.3)

**Rule:** Every PUB method must have `''` doc-comments immediately after the signature with: (1) description, (2) blank `''` separator, (3) `@param` tags, (4) `@returns` tags, (5) blank line before code.

**Current state:** ~~Nearly every PUB method across all files is missing one or more of: `@param` tags, `@returns` tags, blank `''` separator, blank line before code.~~ **FIXED 20 Mar 2026.** All ~130 PUB methods across all 24 files now have proper `''` doc blocks with `@param`, `@returns`, `@local` tags, blank separators, and blank line before code.

**Decision:** FIX (completed)

| File | Approx PUB methods affected | Worst gaps |
|------|:---------------------------:|------------|
| isp_hub75_display.spin2 | ~40 | No method has complete tags |
| isp_hub75_hwBufferAccess.spin2 | ~30 | All accessor methods missing tags |
| isp_hub75_fonts.spin2 | ~8 | All missing; some have stale descriptions |
| isp_hub75_scrollingText.spin2 | ~10 | Missing all @param tags |
| isp_hub75_panel.spin2 | ~6 | Signature/doc separation issues too |
| isp_hub75_rgb3bit.spin2 | ~7 | Blank lines between signature and doc; empty @local descriptions |
| isp_hub75_7seg.spin2 | ~5 | All missing @param and blank-before-code |
| isp_hub75_segment.spin2 | ~7 | All missing @param and blank-before-code |
| isp_hub75_display_bmp.spin2 | 1 | Code appears *before* the doc-comment |
| isp_hub75_screenUtils.spin2 | 2 | Missing all tags |
| isp_hub75_colorUtils.spin2 | ~10 | All missing @param/@returns, no blank before code |
| isp_hub75_color.spin2 | 1 | Missing blank separator |
| isp_hub75_hwEnums.spin2 | 1 | Minor — missing blank separator on null() |
| isp_hub75_hwPanelConfig.spin2 | 1 | Minor |
| isp_hub75_hwBuffers.spin2 | 1 | Blank line between signature and doc |
| demo_hub75_color.spin2 | 1 | Missing @returns for `ok` |
| demo_hub75_text.spin2 | 1 | Missing @returns, no blank separator |
| demo_hub75_5x7font.spin2 | 1 | Missing @returns, no blank separator |
| demo_hub75_7seg.spin2 | 3 | start(), wait100thSecs(), stop() all incomplete |
| demo_hub75_colorPad.spin2 | 1 | Missing @returns for `ok` |
| demo_hub75_multiPanel.spin2 | 1 | Missing @returns for `ok` |
| demo_hub75_scroll.spin2 | 1 | Blank line between signature and first `''` |
| demo_hub75_hwGeometry.spin2 | 1 | Minor |

**Effort estimate:** Large. Every PUB method needs review and tag additions.

---

### 1.3 PRI Method Documentation (Rule 4.4)

**Rule:** Every PRI method must have `'` doc-comments (not `''`) with `@param`/`@returns`/`@local` tags.

**Current state:** ~~Almost no PRI method has structured documentation. Most have zero comments or a brief inline note.~~ **FIXED 20 Mar 2026.** All ~120 PRI methods across all 24 files now have proper `'` doc blocks with `@param`, `@returns`, `@local` tags, blank separators, and blank line before code. Also fixed 3 PRI methods that incorrectly used `''` (doc-comment) — changed to `'`.

**Decision:** FIX (completed)

| File | Approx undocumented PRI methods |
|------|:-------------------------------:|
| demo_hub75_color.spin2 | ~30 |
| demo_hub75_colorPad.spin2 | ~25 |
| demo_hub75_text.spin2 | 5 |
| demo_hub75_5x7font.spin2 | 5 |
| demo_hub75_7seg.spin2 | 4 |
| demo_hub75_multiPanel.spin2 | 6 |
| demo_hub75_scroll.spin2 | 4 |
| isp_hub75_display.spin2 | 5 |
| isp_hub75_panel.spin2 | ~12 |
| isp_hub75_rgb3bit.spin2 | 4 |
| isp_hub75_scrollingText.spin2 | 8 |
| isp_hub75_display_bmp.spin2 | 5 |
| isp_hub75_7seg.spin2 | 3 |
| isp_hub75_segment.spin2 | 6 |
| isp_hub75_hwBufferAccess.spin2 | 1 |

**Effort estimate:** Very large. ~120+ methods need documentation added.

---

### 1.4 Magic Numbers (Rule 5.7)

**Rule:** Every numeric literal with semantic meaning must be a named CON constant. Permitted bare literals: `0` (init/null), `1` (increment), `-1` (sentinel), `4` (LONG-to-byte).

**Current state:** Hundreds of violations across the codebase. Grouped by category:

**Decision:**

#### ASCII codes — `$20`, `$30`, `$7f`, `$42`, `$4d`, etc.

| File | Lines (representative) |
|------|----------------------|
| demo_hub75_color.spin2 | 232-243 |
| demo_hub75_colorPad.spin2 | 217-228 |
| demo_hub75_text.spin2 | 143-153 |
| demo_hub75_5x7font.spin2 | 81-87 |
| demo_hub75_scroll.spin2 | 150-160 |
| isp_hub75_fonts.spin2 | 77, 86, 93, 99, 106 |
| isp_hub75_display.spin2 | 330, 334, 337 |
| isp_hub75_panel.spin2 | 543-551 |
| isp_hub75_display_bmp.spin2 | 110 |
| isp_hub75_scrollingText.spin2 | 355, 387 |

#### Color values — `$AAAAAA`, `$00006F`, `$0080FF`, `$000000`

| File | Lines (representative) |
|------|----------------------|
| demo_hub75_color.spin2 | 415-468 (brightness tables) |
| demo_hub75_colorPad.spin2 | 402-448 |
| demo_hub75_7seg.spin2 | 162, 164 |
| isp_hub75_display.spin2 | 129, 383 |
| isp_hub75_scrollingText.spin2 | 405 |

#### Panel dimensions — `32`, `64`, `63`, `31` as bounds

| File | Lines (representative) |
|------|----------------------|
| demo_hub75_color.spin2 | 197, 544, 556, 586, 664-665, 699-703 |
| demo_hub75_colorPad.spin2 | 182, 526, 537-540, 567-578 |
| isp_hub75_panel.spin2 | 151-154, 591-592 |

#### Loop/timing — `repeat 20`, `waitms(1000)`, `waitSec(10)`

| File | Lines (representative) |
|------|----------------------|
| demo_hub75_color.spin2 | 69, 154, 376, 863-866 |
| demo_hub75_colorPad.spin2 | 64, 69, 139, 806, 809 |
| demo_hub75_5x7font.spin2 | 60, 115, 125, 138, 157, 165, 179 |
| demo_hub75_7seg.spin2 | 65-66, 99-102, 203 |
| demo_hub75_multiPanel.spin2 | 72-75, 114-120, 126 |
| demo_hub75_scroll.spin2 | 63 |
| demo_hub75_text.spin2 | 163, 168 |
| isp_hub75_anlyCheck.spin2 | 75, 77, 97 |

#### Color math — `255`, `360`, `60`, `100`

| File | Lines (representative) |
|------|----------------------|
| isp_hub75_colorUtils.spin2 | 46, 76, 82-103, 110-112, 120-126 |

#### Bit masks/shifts — `$ff00`, `$c000`, `$ff`, `14`, `16`, `8`

| File | Lines (representative) |
|------|----------------------|
| isp_hub75_rgb3bit.spin2 | 255, 309-343, 424, 430, 584, 592, 616 |
| isp_hub75_panel.spin2 | 594, 602 |
| isp_hub75_scrollingText.spin2 | 420, 428, 468, 476, 512, 528 |
| isp_hub75_display.spin2 | 394 |
| isp_hub75_hwBufferAccess.spin2 | 356, 371, 402, 413-438 |

#### BMP format — `54`, `24`, `3`

| File | Lines |
|------|-------|
| isp_hub75_display_bmp.spin2 | 70-91, 110, 153 |

#### Pin offsets — `basePin + 0`, `+ 1`, `+ 8`

| File | Lines |
|------|-------|
| isp_hub75_rgb3bit.spin2 | 172-196 |

**Effort estimate:** Very large. Needs a constants-definition pass first, then substitution.

---

### 1.5 File Layout Order (Rule 3.1)

**Rule:** Every file must follow: header → CON → STRUCT → DAT → OBJ → VAR → PUB → PRI → license.

**Current state:** Most files have blocks scattered among methods.

**Decision:**

| File | Issue |
|------|-------|
| demo_hub75_color.spin2 | VAR before OBJ; CON at 680, 728 inside PRI; DAT at 217, 901 inside methods |
| demo_hub75_text.spin2 | VAR before OBJ; DAT at 127 between PRI methods |
| demo_hub75_5x7font.spin2 | VAR before OBJ; CON at 66 after OBJ/VAR; DAT at 74 after PUB |
| demo_hub75_7seg.spin2 | VAR before OBJ |
| demo_hub75_colorPad.spin2 | VAR before OBJ; CON at 42, 706 out of place; DAT at 202, 838 inside methods |
| demo_hub75_multiPanel.spin2 | VAR before OBJ; CON at 45 after OBJ; DAT at 52, 135 out of order |
| demo_hub75_scroll.spin2 | VAR before OBJ; DAT at 134 after PRI methods |
| demo_hub75_hwGeometry.spin2 | OK (minor: CON at 195 after PUB, but it is hardware-notes CON) |
| isp_hub75_display.spin2 | CON at 89, 189, 424, 536 inside PUB/PRI; VAR at 296 after PUB methods |
| isp_hub75_panel.spin2 | VAR at 580 after PRI; DAT at 635 after PRI |
| isp_hub75_rgb3bit.spin2 | DAT at 725 after PUB (PASM driver — may be acceptable) |
| isp_hub75_hwPanelConfig.spin2 | OBJ before CON; CON at 195 after PUB |
| isp_hub75_hwBufferAccess.spin2 | Interleaved CON/OBJ/CON/DAT/CON/PUB |
| isp_hub75_hwBuffers.spin2 | OBJ before CON |
| isp_hub75_fonts.spin2 | DAT at 109 after PUB methods |
| isp_hub75_colorUtils.spin2 | Second DAT at 135 after PUB section |
| isp_hub75_display_bmp.spin2 | DAT at 167 after PRI methods |
| isp_hub75_scrollingText.spin2 | VAR at 314 after PRI methods start |
| isp_hub75_screenUtils.spin2 | OK |
| isp_hub75_color.spin2 | OK |
| isp_hub75_hwEnums.spin2 | OK |
| isp_hub75_7seg.spin2 | OK |
| isp_hub75_segment.spin2 | OK |
| isp_hub75_anlyCheck.spin2 | OK |

**Effort estimate:** Medium. Requires careful block relocation and recompile testing.

**Note:** The guide may need a carve-out for PASM2 DAT blocks that contain assembly code (e.g., `isp_hub75_rgb3bit.spin2` line 725). These naturally live at the end of the file, after the Spin2 PUB/PRI methods that launch the cog.

---

## 2. Moderate Issues

Found in multiple files but not universally.

---

### 2.1 Object Constants Copied Locally (Rule 2.4)

**Rule:** Constants from OBJ references must always be used via the object prefix (e.g., `hwEnum.PINS_P16_P31`), never copied into a local CON.

**Current state:** Four files copy object constants locally.

**Decision:**

| File | Lines | Constants Copied | Source Object |
|------|-------|-----------------|---------------|
| isp_hub75_display.spin2 | 20-40 | 16 constants: TEXT_FONT_*, DIR_*, SCROLL_* | `fonts`, `scroller` |
| isp_hub75_hwBufferAccess.spin2 | 34-48 | 16 constants: HUB75_ADAPTER_*, DEPTH_*, ROT_* | `hwEnum` |
| isp_hub75_rgb3bit.spin2 | 35-37 | 3 constants: PIN_GROUP_P*_P* | `hwEnum` |
| demo_hub75_hwGeometry.spin2 | 288-296 | ADAPTER_BASE_PIN, PANEL_DRIVER_CHIP, PANEL_ADDR_LINES | `hwEnum` |

**Note:** `isp_hub75_display.spin2` and `isp_hub75_hwBufferAccess.spin2` re-export these constants intentionally so that *their* consumers can use `display.TEXT_FONT_5x7` or `hub75Bffrs.DEPTH_8BIT` without needing a direct OBJ reference to the inner object. This is an API facade pattern. The guide may need to address whether re-exporting for public API purposes is an acceptable exception.

**Effort estimate:** Low if fixing; needs design decision if revising the rule.

---

### 2.2 Return Variables Not Assigned Default (Rule 5.1)

**Rule:** Every return variable must be explicitly assigned a value. Never rely on implicit zero.

**Decision:**

| File | Method | Variable | Notes |
|------|--------|----------|-------|
| demo_hub75_color.spin2 | `main()` | `ok` | Assigned conditionally |
| demo_hub75_text.spin2 | `main()` | `ok` | Assigned conditionally |
| demo_hub75_5x7font.spin2 | `main()` | `ok` | Assigned conditionally |
| demo_hub75_7seg.spin2 | `start()` | `ok` | Assigned conditionally |
| demo_hub75_colorPad.spin2 | `main()` | `ok` | Assigned conditionally |
| demo_hub75_multiPanel.spin2 | `main()` | `ok` | Assigned conditionally |
| demo_hub75_scroll.spin2 | `main()` | `ok` | Assigned conditionally |
| isp_hub75_rgb3bit.spin2 | `start()` | `ok` | No default before coginit |
| isp_hub75_panel.spin2 | `start()` | `ok` | No default before assignment |
| isp_hub75_anlyCheck.spin2 | `start()` | `ok` | **Never assigned at all** |
| isp_hub75_panel.spin2 | `clearPwmFrameBuffer()` | `pPwmFrameSet` | No default |
| isp_hub75_panel.spin2 | `getPwmFrameAddressForBit()` | `pFrameBuffer` | No default |
| isp_hub75_display_bmp.spin2 | `get24BitBMPColorForRC()` | `red, green, blue` | Implicit zero |

**Effort estimate:** Small. Add one line per method.

---

### 2.3 Enum Groups Missing Group Comments (Rule 4.7)

**Rule:** Auto-numbered enumerations (`#0`, `#1`, etc.) must have a preceding comment block listing every value and its meaning.

**Decision:**

| File | Line | Enum |
|------|------|------|
| isp_hub75_hwEnums.spin2 | 22 | `PINS_P0_P15, PINS_P16_P31, PINS_P32_P47, PINS_P48_P63` |
| isp_hub75_hwEnums.spin2 | 27 | `HUB75_ADAPTER_1, _2, _3` |
| isp_hub75_hwEnums.spin2 | 32 | `ROT_UNKNOWN, ROT_NONE, ROT_LEFT_90, ROT_RIGHT_90, ROT_180` |
| isp_hub75_hwEnums.spin2 | 38-39 | Chip type enum |
| isp_hub75_hwEnums.spin2 | 57 | Config flags enum |
| isp_hub75_hwEnums.spin2 | 65 | `ADDR_UNKNOWN, ADDR_ABC, ADDR_ABCD, ADDR_ABCDE` |
| isp_hub75_hwEnums.spin2 | 72 | `DEPTH_3BIT` through `DEPTH_8BIT` |
| isp_hub75_display.spin2 | 43 | `ALIGN_UNKNOWN, ALIGN_RIGHT, ALIGN_CENTER, ALIGN_LEFT` |
| isp_hub75_scrollingText.spin2 | 18 | Direction enum |
| isp_hub75_scrollingText.spin2 | 21 | Scroll mode enum |
| isp_hub75_segment.spin2 | 29 | Segment name enum |
| isp_hub75_segment.spin2 | 30 | Segment state enum |
| isp_hub75_colorUtils.spin2 | 16 | `LED_UNKNOWN, LED_RED, LED_GREEN, LED_BLUE` |
| isp_hub75_fonts.spin2 | 17 | Font type enum |
| isp_hub75_rgb3bit.spin2 | 65 | Command enum |
| isp_hub75_anlyCheck.spin2 | 27 | Pin group enum |
| demo_hub75_multiPanel.spin2 | 50 | Panel position enum |

**Effort estimate:** Medium. Each enum needs 3-8 lines of comment added.

---

### 2.4 PRI Methods Using `''` Instead of `'` (Rule 4.1)

**Rule:** `''` (doc-comments) must only appear on PUB methods. PRI methods and CON blocks must use `'`.

**Current state:** ~~Five occurrences across three PRI methods and two CON blocks.~~ **FIXED 20 Mar 2026.** The three PRI methods were corrected during the Fix 1.3 pass. The two CON block occurrences in `isp_hub75_hwPanelConfig.spin2` and `isp_hub75_hwBuffers.spin2` were corrected during the Fix 1.2 pass.

**Decision:** FIX (completed)

---

### 2.5 PUB/PRI Interleaved (Rule 3.2)

**Rule:** All PUB methods must appear before all PRI methods.

**Decision:**

| File | Issue |
|------|-------|
| isp_hub75_display.spin2 | PRI methods `placeCharBitmap`, `placeDitheredCharBitmap`, `offsetToTextOnPanel`, `incrCursorWithWrap` (lines 378-421) appear between PUB groups |
| demo_hub75_7seg.spin2 | PUB methods `wait100thSecs()` and `stop()` (lines 200-210) appear after PRI methods |

**Effort estimate:** Small. Move methods to correct sections.

---

### 2.6 Non-Descriptive or Single-Letter Names (Rules 2.1, 2.2)

**Decision:**

| File | Line(s) | Name | Issue | Suggested Fix |
|------|---------|------|-------|---------------|
| All 8 demo files | various | `cog` | Non-descriptive | `driverCog` or `displayCogId` |
| All 8 demo files | various | `ok` (return) | Vague | `status` or `cogId` |
| isp_hub75_display.spin2 | 629, 647 | `D` | Single-letter local | `slopeError` |
| isp_hub75_display.spin2 | 629, 647 | `x0, y0, x1, y1` | Two-letter params | Conventional for geometry — consider exemption |
| isp_hub75_scrollingText.spin2 | 394 | `a, b` | Single-letter params in `min()` | `firstValue, secondValue` |
| isp_hub75_display_bmp.spin2 | 63 | `i` | Single-letter local | `paletteEntryCount` or `headerFieldIdx` |
| isp_hub75_panel.spin2 | 28 | `bus` | Non-descriptive | `busType` or `memoryBus` |
| isp_hub75_anlyCheck.spin2 | 63 | `ctl, ctr` | Abbreviations | `ctlValue, ctrValue` |

**Note:** The `x0, y0, x1, y1` convention for line-drawing geometry parameters is standard in graphics code. The guide may want an explicit exemption for well-known geometric coordinate names.

**Effort estimate:** Small. Rename and verify no reference breakage.

---

### 2.7 Multiple Exit Points (Rule 5.2)

**Rule:** Single exit point per method. No early `return`. Use `quit` to exit loops.

**Decision:**

| File | Method | Line | Issue |
|------|--------|------|-------|
| isp_hub75_panel.spin2 | `isDebugLocn()` | 627 | `return` makes remaining code dead |
| isp_hub75_display_bmp.spin2 | `isDebugLocn()` | 163 | Superfluous bare `return` |
| demo_hub75_7seg.spin2 | `start()` | 49 | `abort` + infinite `repeat` = two termination paths |
| demo_hub75_text.spin2 | `main()` | 39 | `abort` + unreachable code after infinite `repeat` |
| demo_hub75_scroll.spin2 | `main()` | 39 | Same pattern |

**Note:** The `abort` on failed init + `repeat` forever for normal operation is a common embedded pattern. The guide may need to clarify whether `abort` on fatal error counts as an "exit point" for this rule.

**Effort estimate:** Small.

---

## 3. Isolated Issues

One-off problems found in specific files.

---

### 3.1 File Header Mismatches (Rule 4.2)

**Decision:** FIX (completed)

**FIXED 20 Mar 2026.** Both headers corrected:
- `demo_hub75_text.spin2`: filename fixed to `demo_hub75_text.spin2`, purpose text rewritten
- `demo_hub75_scroll.spin2`: "scolling" typo fixed to "scrolling"

| File | Line | Issue |
|------|------|-------|
| ~~demo_hub75_text.spin2~~ | ~~3~~ | ~~Header says `isp_hub75_demoText.spin2`, actual file is `demo_hub75_text.spin2`~~ |
| ~~demo_hub75_scroll.spin2~~ | ~~4~~ | ~~Header says "scolling" (typo for "scrolling")~~ |

---

### 3.2 Code Before Doc-Comment (Rule 4.3)

**Decision:** FIX (completed)

**FIXED 20 Mar 2026.** Corrected during the Fix 1.2 pass — doc-comment now appears immediately after the signature, before any executable code.

| File | Line | Issue |
|------|------|-------|
| ~~isp_hub75_display_bmp.spin2~~ | ~~29-32~~ | ~~`fillScreenFromBMP` has `chainIndex := nChainIdx` on line 30, *before* the `''` doc-comment on line 31~~ |

---

### 3.3 Stale or Incorrect Documentation

**Decision:** FIX (completed)

**FIXED 20 Mar 2026.** All items corrected:
- "110ths" errors in 3 files: fixed during the Fix 1.3 pass (rewrote PRI docs)
- Stale "8x8" descriptions in `isp_hub75_fonts.spin2`: fixed during the Fix 1.2 pass
- "5 seconds" comment in `demo_hub75_5x7font.spin2`: corrected to "60 seconds"
- Empty `@local` descriptions in `isp_hub75_rgb3bit.spin2`: filled in during the Fix 1.2 pass

| File | Line | Issue |
|------|------|-------|
| ~~demo_hub75_text.spin2~~ | ~~166~~ | ~~Comment says "110ths of a second" but code does 100ths (10ms)~~ |
| ~~demo_hub75_multiPanel.spin2~~ | ~~106~~ | ~~Same "110ths" error~~ |
| ~~demo_hub75_scroll.spin2~~ | ~~173~~ | ~~Same "110ths" error~~ |
| ~~isp_hub75_fonts.spin2~~ | ~~75~~ | ~~`getAddrFor5x7DithChar` doc says "8x8 (a) character bitmap"~~ |
| ~~isp_hub75_fonts.spin2~~ | ~~84~~ | ~~`getAddrFor5x7DithDcndrChar` doc says "8x8 (a) character bitmap"~~ |
| ~~demo_hub75_5x7font.spin2~~ | ~~60~~ | ~~Comment says "5 seconds" but code is `waitSec(60)`~~ |
| ~~isp_hub75_rgb3bit.spin2~~ | ~~127-133~~ | ~~`@local` tags have empty descriptions (just ` -` with no text)~~ |

---

### 3.4 Unused Local Variables

**Decision:** FIX (completed)

**FIXED 20 Mar 2026.** Removed all unused locals from method signatures and their `@local` doc tags:
- `demo_hub75_text.spin2` `main()`: removed `bitCount`, `newMask`
- `demo_hub75_5x7font.spin2` `main()`: removed `bitCount`, `newMask` (kept `vertPixelCount` which is used)
- `demo_hub75_scroll.spin2` `main()`: removed `bitCount`, `newMask`
- `demo_hub75_7seg.spin2` `start()`: removed 14 unused locals, kept `hours24` which is used

| File | Method | Unused Variables |
|------|--------|-----------------|
| ~~demo_hub75_text.spin2~~ | ~~`main()`~~ | ~~`bitCount`, `newMask`~~ |
| ~~demo_hub75_5x7font.spin2~~ | ~~`main()`~~ | ~~`bitCount`, `newMask`~~ |
| ~~demo_hub75_scroll.spin2~~ | ~~`main()`~~ | ~~`bitCount`, `newMask`~~ |
| ~~demo_hub75_7seg.spin2~~ | ~~`start()`~~ | ~~`blockX`, `blockY`, `subrow`, `subcol`, `row`, `col`, `red`, `green`, `blue`, `builtPtr`, `color3bit`, `color24bit`, `pPixColor`, `colorOffset`, `byteOffset`~~ |

---

### 3.5 Possible Typo in Color Constant

**Decision:** FIX (completed)

**FIXED 20 Mar 2026.** Changed `cTeal = $08080` to `cTeal = $008080`.

| File | Line | Issue |
|------|------|-------|
| ~~isp_hub75_color.spin2~~ | ~~30~~ | ~~`cTeal = $08080` — likely should be `$008080`~~ |

---

## Questions for Guideline Review

Based on this audit, here are patterns where the guide may need revision or clarification:

1. **Rule 2.4 (re-exporting constants):** Should an object that re-exports inner-object constants for its public API be exempt? (`isp_hub75_display.spin2` re-exports font/scroller constants so demos can use `display.TEXT_FONT_5x7`.)

2. **Rule 3.1 (PASM2 DAT placement):** Should DAT blocks containing PASM2 assembly code be explicitly permitted after PUB/PRI methods? This is standard practice for Spin2/PASM2 cog drivers.

3. **Rule 5.2 (abort as exit point):** Does `abort` on fatal init failure count as a second "exit point"? The pattern `abort` + `repeat` forever is standard for embedded main loops.

4. **Rule 2.1 (geometry names):** Should `x0, y0, x1, y1` and similar standard coordinate names be explicitly exempted for graphics/geometry methods?

5. **Rule 5.7 (magic numbers in demos):** Should demo files have a relaxed standard for magic numbers in drawing coordinates and color showcase code, where the values are inherently one-off visual layout choices?

6. **Rule 3.1 (VAR before OBJ):** Every demo file has VAR before OBJ. Is this a deliberate codebase convention that the guide should accommodate?

7. **Rule 4.5 (block label style):** Every file in the codebase uses `{ }` block comments on CON/DAT/VAR/OBJ declaration lines, not `'` as the guide prescribes. Should the guide adopt the existing convention?

8. **CON as method-group dividers:** `isp_hub75_display.spin2` uses empty CON blocks with dash-delimited labels (e.g., `CON { --- Text Handling --- }`) to visually separate groups of PUB methods. Should this be documented as an accepted pattern, or should a different separator mechanism be used?

---

## 4. Undocumented Conventions in the Code

These are patterns consistently followed across the `.spin2` source files that the authoring guide does **not** currently cover. Each is a candidate for addition to the guide.

The **Action** column is for you to fill in:

| Action Value | Meaning |
|---|---|
| `ADD` | Add this convention to the guide |
| `IGNORE` | Not worth codifying |
| *(blank)* | Not yet triaged |

---

### 4.1 File Naming Convention

Driver/library files use `isp_hub75_{component}.spin2`. Demo/example files use `demo_hub75_{feature}.spin2`. The `isp_` prefix stands for Iron Sheep Productions.

**Action:**

**Examples:**
- Driver: `isp_hub75_display.spin2`, `isp_hub75_panel.spin2`, `isp_hub75_rgb3bit.spin2`, `isp_hub75_hwEnums.spin2`
- Demo: `demo_hub75_color.spin2`, `demo_hub75_text.spin2`, `demo_hub75_scroll.spin2`
- Config: `isp_hub75_hwPanelConfig.spin2`, `isp_hub75_hwBufferAccess.spin2`, `isp_hub75_hwBuffers.spin2`

**Note:** The descriptive portion after `hub75_` sometimes uses pure lowercase (`color`, `fonts`), sometimes camelCase (`colorUtils`, `screenUtils`, `scrollingText`, `multiPanel`), and sometimes abbreviations (`rgb3bit`, `anlyCheck`). There is no strict rule for this part.

---

### 4.2 `null()` Guard Method on Non-Top-Level Objects

Every non-top-level object defines `PUB null()` as its very first PUB method with the doc-comment `'' This is not a top level object`. This prevents accidental compilation as a standalone program.

**Action:**

**Found in:** `isp_hub75_display.spin2`, `isp_hub75_panel.spin2`, `isp_hub75_rgb3bit.spin2`, `isp_hub75_screenUtils.spin2`, `isp_hub75_scrollingText.spin2`, `isp_hub75_7seg.spin2`, `isp_hub75_segment.spin2`, `isp_hub75_color.spin2`, `isp_hub75_colorUtils.spin2`, `isp_hub75_fonts.spin2`, `isp_hub75_hwEnums.spin2`, `isp_hub75_hwPanelConfig.spin2`, `isp_hub75_hwBufferAccess.spin2`, `isp_hub75_hwBuffers.spin2`, `isp_hub75_display_bmp.spin2`, `demo_hub75_hwGeometry.spin2`

---

### 4.3 Variable Type-Prefix System

Variables consistently use Hungarian-style lowercase prefixes to indicate type/purpose. The guide shows these in examples (Rule 2.2) but does not codify them as a formal convention.

**Action:**

| Prefix | Meaning | Examples |
|--------|---------|----------|
| `p` | Pointer/address | `pZString`, `pPwmFrame1`, `pScreenInMemory`, `pCharBitmap`, `pColor` |
| `b` | Boolean | `bSwapRB`, `bFontIsDithered`, `bScrolling`, `bValidStatus`, `bDumpOnce` |
| `n` | Numeric count/index | `nChainIdx`, `nMaxColumns`, `nPwmFrameSizeInLongs`, `nWidth`, `nHeight` |
| `e` | Enum value | `eHub75Chain`, `ePinBase`, `eChipType`, `eAddrLines`, `eScrollMode` |

---

### 4.4 Color Constant Naming: `c` Prefix with camelCase

24-bit RGB color constants in `isp_hub75_color.spin2` use a lowercase `c` prefix with camelCase, contrasting with the UPPER_SNAKE_CASE used for hardware/config constants.

**Action:**

**Examples:** `cBlack`, `cWhite`, `cRed`, `cLime`, `cDarkGreen`, `cOrange`, `cBlueViolet`, `cFullRed`, `cRedWhtBlu`, `cRainbow`

---

### 4.5 OBJ Instance Naming Convention

Object references use short camelCase names describing the role. When multiple files reference the same object, they always use the same short name.

**Action:**

| OBJ Name | Source File | Used In |
|----------|------------|---------|
| `hub75Bffrs` | `isp_hub75_hwBufferAccess` | all driver + demo files |
| `hwEnum` | `isp_hub75_hwEnums` | display, rgb3bit, hwPanelConfig, hwGeometry |
| `display` | `isp_hub75_display` | all demo files |
| `pixels` | `isp_hub75_screenUtils` | display, scrollingText, segment, demos |
| `colorUtils` | `isp_hub75_colorUtils` | display, scrollingText, segment, demos |
| `fonts` | `isp_hub75_fonts` | display, scrollingText |
| `color` | `isp_hub75_color` | rgb3bit, all demos |
| `user` | `isp_hub75_hwPanelConfig` | all demos |
| `scrnBuffers` | `isp_hub75_hwBuffers` | all demos |
| `panelSet` | `isp_hub75_panel` | display |
| `matrix` | `isp_hub75_rgb3bit` | panel |
| `scroller` | `isp_hub75_scrollingText` | display (array instance) |

---

### 4.6 Clock and Debug Configuration Pattern

Every top-level demo file begins with two CON blocks in the same order:

1. `CON { timing }` — defines `CLK_FREQ = 335_000_000` then `_clkfreq = CLK_FREQ`
2. `CON { DEBUG PINs }` — contains `'DEBUG_PIN = 0` (commented out), optionally `DEBUG_COGS` and `DEBUG_BAUD`

**Action:**

**Found in:** All 8 demo files, identically.

---

### 4.7 Driver Initialization Sequence

Every demo follows a 4-step startup sequence:

```spin2
hub75Bffrs.configure(hub75Bffrs.HUB75_ADAPTER_1, user.DISP0_ADAPTER_BASE_PIN, ...)
chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)
display.setBufferPointers(chainIndex, scrnBuffers.chain0Ptrs())
ok := cog := display.start(chainIndex)
```

**Action:**

**Found in:** All 7 runnable demo files (not hwGeometry).

---

### 4.8 Startup Failure Guard Pattern

After `display.start()`, every demo checks `if ok == -1`, prints `debug("- DEMO: underlying driver(s) failed!")`, and calls `abort`.

**Action:**

**Found in:** All 7 runnable demo files.

---

### 4.9 `stop()` Guard Pattern

The `stop()` method (PRI or PUB) always follows this structure: check `if cog`, call `display.stop()`, then `cog := 0`.

**Action:**

**Found in:** `demo_hub75_color.spin2`, `demo_hub75_7seg.spin2`, `demo_hub75_multiPanel.spin2`, `demo_hub75_colorPad.spin2`

---

### 4.10 `waitSec()` Helper Pattern

Every demo that needs pausing defines an identical private helper:

```spin2
PRI waitSec(countSeconds)
    repeat countSeconds
        waitms(1000)
```

Some files also define `wait100thSecs(count)` with `waitms(10)`.

**Action:**

**Found in:** 6 of 7 demo files. Could be a shared utility object instead of duplicated.

---

### 4.11 `commitScreenToPanelSet()` as Final Draw Call

Every drawing routine ends with `display.commitScreenToPanelSet()` to flush the screen buffer to the PWM hardware. This is a universal draw-then-commit pattern.

**Action:**

**Found in:** Every PRI drawing method across all demo files and driver methods that modify the display.

---

### 4.12 `chainIndex`/`instanceID` as Standard Instance Variables

Every object in the driver chain declares `LONG chainIndex` and often `LONG instanceID` as instance variables. They are assigned early in `start()` or `initialize()`.

**Action:**

**Found in:** `isp_hub75_display.spin2`, `isp_hub75_panel.spin2`, `isp_hub75_rgb3bit.spin2`, `isp_hub75_7seg.spin2`, `isp_hub75_scrollingText.spin2`, `isp_hub75_segment.spin2`, all demo files.

---

### 4.13 `nChainIdx` as Standard First Parameter

Every PUB method in `isp_hub75_hwBufferAccess.spin2` that operates on a specific adapter chain takes `nChainIdx` as its first parameter. This name is reused identically across ~30 methods and propagated through the driver stack.

**Action:**

---

### 4.14 Debug Message Prefixes by Object

Each object uses a consistent short prefix in `debug()` calls to identify the source:

**Action:**

| Object | Prefix | Example |
|--------|--------|---------|
| `isp_hub75_display.spin2` | `"DSP: "` | `debug("DSP: start() #", ...)` |
| `isp_hub75_panel.spin2` | `"- PNL: "` | `debug("- PNL: #", udec_(instanceID), ...)` |
| `isp_hub75_rgb3bit.spin2` | `"RG3: "` | `debug("RG3: #", udec_(instanceID), ...)` |
| `isp_hub75_scrollingText.spin2` | `"stx: "` | `debug("stx:initialize() ", ...)` |
| `isp_hub75_segment.spin2` | `"SEG: "` | `debug("SEG: BAD segment type!")` |
| Demo files | `"- DEMO: "` | `debug("- DEMO: underlying driver(s) failed!")` |

---

### 4.15 `DISPn_` Naming for Multi-Adapter Constants

Configuration constants use `DISP0_`, `DISP1_`, `DISP2_` prefixes for the three HUB75 adapter slots, with identical suffixes across all three sets (`_ADAPTER_BASE_PIN`, `_PANEL_DRIVER_CHIP`, `_MAX_PANEL_COLUMNS`, `_COLOR_DEPTH`, `_ROTATION`, `_SCRN_SIZE_IN_LONGS`, etc.).

**Action:**

**Found in:** `isp_hub75_hwPanelConfig.spin2` (all three sections).

---

### 4.16 User-Configurable Section Markers

Editable regions are bracketed with a distinctive visual pattern:

```spin2
' /-------------------------------------------
' |  User configure
...
' |  End User configure
' \-------------------------------------------
```

**Action:**

**Found in:** `isp_hub75_hwPanelConfig.spin2` (three instances, one per adapter).

---

### 4.17 Block-Comment Toggle for Optional Code

A `{` at start of line comments out a section. Placing `'` before it (`'{`) turns it into a line comment, re-enabling the code below. Sections include instruction text: `COMMENT-OUT THIS LINE (place tic in front of this line) if you using the Nth HUB75 adapter board`.

**Action:**

**Found in:** `isp_hub75_hwBufferAccess.spin2`, `isp_hub75_hwBuffers.spin2` (2 instances each).

---

### 4.18 Bounds Clamping Idiom

Pixel coordinates and indices are clamped using the Spin2 min/max operator pattern: `0 #> value <# max - 1`.

**Action:**

**Examples:**
- `cursorLine := 0 #> line <# maxTextLines - 1` (display)
- `fmRow := 0 #> fmRow <# hub75Bffrs.maxDisplayRows(chainIndex) - 1` (display)
- `segStartX := 0 #> column <# hub75Bffrs.maxDisplayColumns(chainIndex) - 1` (segment)
- `rowIndex := 0 #> row <# hub75Bffrs.maxDisplayRows(nChainIdx) - 1` (screenUtils)

---

### 4.19 License Block Exact Format

Every file ends with `CON { license }` followed by a `{{ }}` doc-comment block. The internal format is: two blank lines, a dashed separator, the MIT license text with "Iron Sheep Productions, LLC" copyright, then an `===` closing line.

**Action:**

**Found in:** All 24 `.spin2` files, identically formatted.

---

### 4.20 Indentation: 4-Space, No Tabs

All files use 4-space indentation for method bodies and nested blocks. CON values are indented 4 spaces from the `CON` keyword. No tabs appear anywhere.

**Action:**

---

### 4.21 Hex Case Convention

Color values and data use lowercase hex (`$ff0000`, `$ff`, `$20`). Sentinel/signature values use uppercase (`$0DF0ADDE`, `$FFFFFF`). The split is not absolute but trends this way.

**Action:**

---

### 4.22 CON Section Labels as Method-Group Dividers

`isp_hub75_display.spin2` uses empty CON blocks with dash-delimited labels to separate logical PUB method groups:

- `CON { --------------     Text Handling     -------------- }`
- `CON { --------------     Scrolling Text     -------------- }`
- `CON { --------------     Basic Graphics     -------------- }`

**Action:**

**Note:** This conflicts with Rule 3.1 (CON blocks before PUB/PRI) but serves a navigation purpose.

---

### 4.23 DAT String Tables Format

DAT-section strings use camelCase labels, `byte` type (lowercase), and explicit null termination with `,0`. OBJ instance trailing comments explain the object's role.

**Action:**

**Examples:**
- `pwmMsg  byte    "XXXfrm pwm",0` (in color, text, scroll demos)
- `lblTop byte "Top", 0` (multiPanel)
- `panelIdMessage  byte    "Pn",0` (multiPanel)

---

### 4.24 Gamma Table Layout Convention

Gamma correction tables in `isp_hub75_colorUtils.spin2` use 256 BYTE entries formatted as 16 rows of 16 values, preceded by a comment identifying the gamma curve value.

**Action:**

---

### 4.25 `CMD_` Prefix for Cog Command Enums

Command codes for cog-to-cog communication use `CMD_` prefix with `#0` auto-enumeration, where `CMD_DONE = 0` is always the "no command pending" sentinel.

**Action:**

**Found in:** `isp_hub75_rgb3bit.spin2` line 65: `#0, CMD_DONE, CMD_CLEAR, CMD_SHOW_BUFFER, CMD_FILL_COLOR, CMD_SHOW_PWM_BUFFER, CMD_STOP`

---

### 4.26 VAR Block Starts with `cog` and `chainIndex`

Every demo file's VAR block begins with `long cog` then `long chainIndex` as the first two variables. Driver objects similarly lead with `instanceID` and `chainIndex`.

**Action:**

**Found in:** All 7 demo files; `isp_hub75_display.spin2`, `isp_hub75_panel.spin2`, `isp_hub75_rgb3bit.spin2`.

---

### 4.27 `hub75Bffrs` as Universal Shared-State Accessor

Every object that needs display dimensions, buffer addresses, or configuration accesses them through `hub75Bffrs` (always this exact name), passing `chainIndex` as the first argument. This is the centralized configuration hub for the driver stack.

**Action:**

**Examples:** `hub75Bffrs.maxDisplayRows(chainIndex)`, `hub75Bffrs.maxDisplayColumns(chainIndex)`, `hub75Bffrs.displayBufferAddress(chainIndex)`, `hub75Bffrs.colorDepth(chainIndex)`, `hub75Bffrs.columnsPerPanel(chainIndex)`

---

### 4.28 Inline PASM2 Structure

Inline PASM2 within PUB/PRI methods follows: `org` / `jmp #startLabel` (skip over data) / local LONG variables / assembly code / `end`. This contrasts with DAT-section PASM which is the main cog driver.

**Action:**

**Found in:** `isp_hub75_panel.spin2` (`convertScreen2PWM_14()`, `convertScreen2PWM()`), `isp_hub75_rgb3bit.spin2` (`resetPanelFM6126()`)
