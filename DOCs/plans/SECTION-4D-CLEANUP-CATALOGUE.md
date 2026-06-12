# §4d Post-Reconciliation Functional Cleanup -- Findings Catalogue

**Sprint:** source-reconciliation (build 3.0.3) | **Task:** «#10» §4d | **Date:** 2026-06-11
**Method:** 8 parallel audit agents, all 28 merged `.spin2` files, three dimensions
(D1 unused params/returns/locals, D2 dead/simplifiable, D3 doc-comment completeness).
**Status:** APPLIED 2026-06-12 (see "APPLICATION RESULTS" at end). Signed off by Stephen.

**Baseline:** 28/28 compile clean, 0 warnings (pnut-ts v1.55.0). Baseline binary
sha256 captured in `/tmp/baseline.sha256` (28 `.bin`).

**Behavior-proof model (GOLD retired):**
- *Comment-only / doc-only* changes (D3 adds, commented-scaffolding removal) -> `.bin`
  stays **byte-identical** -> prove via sha256 == baseline.
- *Dead-code / unused-local removal* (D1, dead DAT/PRI) -> `.bin` legitimately
  **shrinks/changes** -> byte-identity does NOT apply; proof is (a) verified zero
  references + (b) clean 0-warn recompile. Runtime behavior unchanged because the
  removed entity was never read/reached.

---

## TOP-LEVEL CROSS-FINDINGS (read first)

### X1. The 4 NEW develop demos are CLEAN on D1 -- stale heuristic flags do NOT apply
The 2026-06-06 heuristic seeds (`demoIndex`, `bDidDemo`, `pnlIdx` in multi2x2panel;
`demoIndex` in numberPanels/quadPanel; `scrollerID`/`startTime` in numberPanels
`idPanelsInChain`) **do not exist** in the current merged source:
- `demo_hub75_multi2x2panel.spin2`: `main()` has NO `| locals`; `testPanelOrientation()`
  is `| centerRow, centerCol, circleRadius` (all used). No `pnlIdx`.
- `demo_hub75_numberPanels.spin2`: `idPanelsInChain()` is `| maxPanels, panelIndex`
  (both used). No `scrollerID`/`startTime`. The restyle-agent claim was FALSE for current source.
- `demo_hub75_quadPanel.spin2`: `main()` has NO locals. No `demoIndex`.
- `test_hub75_pin_identify.spin2`: confirmed clean.
**D1 net for all four NEW files: ZERO.** No interim `@local <name> - unused` tags remain.

### X2. panel.spin2 PWM-dump family -- CONFLICTS with task #9 (DEBUG_MASK), DO NOT DELETE here
Agent flagged these as dead PRIs to remove: `dumpBufferHeads`, `dumpFrameAddrs`,
`dumpFrameSet`, `dumpFrame` (+ disabled debug block 684-692, VARs `bDumpOnce`/`nPassCt`,
DAT `frame0Msg`/`frame1Msg`). **BUT task #9 (DEBUG_MASK phase 1) explicitly plans to
PRESERVE this exact family under `DEBUG[DBG_PWM]`/`DEBUG[DBG_BUFFER]` channel gating.**
RECOMMENDATION: **EXCLUDE the panel PWM-dump family from §4d deletion.** Let #9 decide
(channelize vs cut). Only the genuinely-orphaned, non-dump dead DAT in panel.spin2
(`testValue`, `testValueMsg`, `msgScrnHd`) is §4d-safe.

### X3. Config-template commented blocks are INTENTIONAL -- keep
hwBufferAccess (2nd/3rd adapter chains), hwBuffers (2nd/3rd adapter accessors),
hwPanelConfig (AUTHORs-configuration catalog 216-444), hwGeometry (11 brace-disabled
hardware templates), anlyCheck (test-toggle brace markers): all are deliberate
user-selectable templates, NOT merge cruft. **Keep all.** Not cleanup targets.

### X4. "Focused-test brace blocks" + uncalled demo-helper PRIs are an INTENTIONAL demo library
demo_hub75_color / colorPad / multi2x2panel / quadPanel / scroll contain many uncalled
PRI demo helpers and brace-disabled focused-test blocks, switched on by hand. This is a
documented demo-authoring pattern, not develop dead code. **Recommend KEEP** (decision C1).

---

## CLASS A -- behavior-neutral, byte-identical, low-risk (recommend APPLY)

These touch only comments / commented-out scaffolding / doc blocks. `.bin` stays
identical -> sha256 == baseline proves no behavior change.

### A1. D3 -- missing doc comments (add `''`/`'` blocks; byte-identical)
| File | Line | Method | PUB/PRI | Action |
|------|------|--------|---------|--------|
| isp_hub75_colorUtils | 99 | correctedColor | PUB | add `@param nChainIdx,color` + `@returns` |
| isp_hub75_colorUtils | 109 | correctedSingleColor | PUB | add `@param nChainIdx,led,colorValue` + `@returns` |
| isp_hub75_colorUtils | 284 | colorAtDesiredBitWidth | PUB | add `@param nChainIdx,hex8bit` + `@returns` |
| demo_hub75_multi2x2panel | 89 | placeClock | PUB | add `''` doc block |
| demo_hub75_multi2x2panel | 100 | placeDigit | PUB | add `''` doc + `@param rowOffset,colOffset` |
| demo_hub75_multi2x2panel | 254 | demoPanelFillColors | PRI | add `'` doc block |
| demo_hub75_multi2x2panel | 267 | demoRandomPanelColors | PRI | add `'` doc + `@local` tags |
| demo_hub75_multi2x2panel | 279 | demoColorPanels | PRI | add `'` doc block |
| demo_hub75_multi2x2panel | 306 | demoTopBottomScroll | PRI | add `'` doc + `@local scrollerID` |
| demo_hub75_multi2x2panel | 358 | demoPanelColors | PRI | add `'` doc + `@local` tags |
| demo_hub75_multi2x2panel | 396 | showDuration | PRI | add `'` doc + `@param`/`@local` |
| demo_hub75_multi2x2panel | 244 | waitSec | PRI | add `@param countSeconds` (has `'`) |
| demo_hub75_multi2x2panel | 249 | wait1000thSecs | PRI | add `@param count` (has `'`) |
Note: depends on C1/C2 -- if uncalled PRIs in multi2x2panel are CUT, their doc-adds are moot.

### A2. D2 -- commented-out scaffolding removal (byte-identical)
High-confidence "real disabled code / stray comment" removals (NOT config templates):
| File | Lines | What |
|------|-------|------|
| isp_hub75_display | 705 | orphaned `'offsetToTextOnPanel(...)` (helper does not exist) |
| isp_hub75_colorUtils | 104-106 | disabled `'return`/`'adjustedColor:=...` block |
| isp_hub75_colorUtils | 314-318 | block-commented `{...'}` referencing nonexistent `didShow[]` |
| isp_hub75_colorUtils | 227, 290 | commented `'debug(...)` lines |
| isp_hub75_colorUtils | 330, 347 | stray `'{`/`' }` delimiters wrapping the LIVE gamma table |
| isp_hub75_screenUtils | 48-52 | commented `CREDWHTBLU` elseif branch (unimplemented special color) |
| isp_hub75_display_bmp | 155 | commented `'hub75Bffrs.dbgMemDump(...)` |
| isp_hub75_display_bmp | 86,108,129-136,139,143,147,151,153 | `XYZZYpnl`-tagged commented debug |
| isp_hub75_fonts | 124-125 | commented `'if asciiByte==$20`/`'debug` |
| isp_hub75_scrollingText | 650-651,687-690,712-715 | commented `debugCount` debug scaffolding |
| isp_hub75_rgb3bit | 36,42 | stray `'{`/`'}` around LIVE `MTX_LA_XTRA_PINS_*` constants |
| isp_hub75_rgb3bit | 298-320 | brace-disabled old `MTX_LED_*` pin defs (superseded) |
| isp_hub75_rgb3bit | 372-376, 1166-1169 | commented time-constant calcs + DAT decls |
| isp_hub75_rgb3bit | 540-561 | brace-disabled test-mask block |
| isp_hub75_hwBufferAccess | 950 | stray `' returns` mid-method |
| isp_hub75_hwBufferAccess | 996-997 | redundant restatement of 994-995 |
| demo_hub75_color | 58,60,142-154,159 | `'repeat`/`'debug`/alt-dispatch scaffolding |
| demo_hub75_color | 802,853 | stray `' repeat  ' hold here!` trailers |
| demo_hub75_color | 1191 | commented alt `'bmpFile1 FILE` |
| demo_hub75_colorPad | 54,56,142-161 | `'repeat`/`'debug`/alt-dispatch scaffolding |
| demo_hub75_colorPad | 790,841 | stray `' repeat  ' hold here!` trailers |
| demo_hub75_multiPanel | 70-72,89,95-101,163,222-236,252-254 | scaffolding + dead instrumentation |
| demo_hub75_numberPanels | 50,53,99,119-121 | `'repeat`/`'debug`/dead scaffolding |
| demo_hub75_quadPanel | 67,70,141,181,186-195 | `'repeat`/`'debug`/dead scaffolding |
| demo_hub75_7seg | 56,130-157 | `'debug` + disabled transitional-demo `{...}` block |
| demo_hub75_text | 53,72-73,86,89-119 | `'repeat`/alt-config/dead instrumentation |
| demo_hub75_scroll | 67-126 | alt-config/`'repeat`/dead instrumentation |
| (all demos) | ~21 | commented `' DEBUG_PIN = 0` (cosmetic; optional) |
Note: project house style KEEPS many `' debug(...)` trace lines deliberately. Only the
clearly-orphaned blocks above are flagged; the routine inline `' debug(...)` convention
in display.spin2 etc. is NOT touched.

---

## CLASS B -- behavior-affecting (`.bin` changes), genuinely-dead removal (recommend APPLY w/ verify)

`.bin` legitimately changes. Proof = verified zero refs + clean recompile; runtime
behavior unchanged (entity never read/reached).

### B1. D1 -- genuinely unused locals (shrinks stack frame)
| File | Line | Method | Identifier | Conf | Note |
|------|------|--------|-----------|------|------|
| isp_hub75_display_bmp | 70 | loadBitmap | `haveError` local | HIGH | + remove `@local haveError` doc (80) |
| isp_hub75_colorUtils | 164 | gammaCorrectedSingleColor | `pGammaTable` local | HIGH | dead assign; ties to C3 gamma decision |
| demo_hub75_color | 647 | demoTest360ColorBrightness | `red,green,blue` locals | HIGH | (PRI itself may be cut -> C1) |
| demo_hub75_colorPad | 635 | demoTest360ColorBrightness | `red,green,blue` locals | HIGH | (PRI itself may be cut -> C1) |
| demo_hub75_7seg | 180 | showSecondsDots | `red,green,blue` locals | HIGH | + remove `@local` docs 186-188 |

### B2. D1 -- unused multi-return placeholders in display.spin2 (HANDLE CAREFULLY)
| Line | Method | Identifier | Note |
|------|--------|-----------|------|
| 329 | setCursorOnPanel | `panelsPerCol` | 1st slot of `panelsPerCol,panelsPerRow := displaySizeInPanels()`; never read. Spin2 needs a target for slot 1 -- cannot just delete; must keep a discard or restructure. LOW-PRIORITY / verify. |
| 677 | scrollColoredTextOnLnOfNPanels | `offsetPixelRows` | 1st slot of `offsetPixelRows,offsetPixelColumns := offsetToPanel()`; never read here (read in sibling methods). Same multi-return constraint. |
RECOMMENDATION: defer B2 unless Stephen wants it -- the multi-return target is structurally
required; "removing" means restructuring, marginal benefit, higher risk.

### B3. D1/D2 -- dead instance VARs (write-only / never-read)
| File | Line(s) | VAR | Evidence |
|------|---------|-----|----------|
| isp_hub75_display | 107,172 | `bDidShowOnce` | written `:=FALSE` once, never read |
| isp_hub75_scrollingText | 84 | `leftBitmap` | declared only |
| isp_hub75_scrollingText | 85 | `rightBitmap` | declared only |
| isp_hub75_scrollingText | 87 | `scrollCharOffset` | declared only |
| isp_hub75_scrollingText | 89 | `remainingColumns` | declared only |
| isp_hub75_scrollingText | 90,130 | `bScrolling` | write-only |
| isp_hub75_scrollingText | 399 | `vtInsetInPix` | never referenced |
| isp_hub75_scrollingText | 101,157 | `leadingGapInPix` | write-only (from param `leadingGap`) |
| isp_hub75_scrollingText | 103,159 | `hBitmapOffsetInPix` | write-only (from param `hBitmapOffset`) |
| isp_hub75_scrollingText | 116,129,137 | `isSetup` | write-only guard, never tested |
| isp_hub75_7seg | 65 | `defaultColor` | never referenced |
| demo_hub75_multiPanel | 29,85 | `scrollPeriod` | write-only (live reads only in commented code) |
| demo_hub75_7seg | 33 | `digitVal` | referenced only in disabled block (130-157) |
Note: scrollingText params `leadingGap`/`hBitmapOffset` (setFontInfo, 141) feed only the
removed VARs -> become unused params. INTERFACE-CONSTRAINED: caller is display.spin2;
verify the call site before removing the params (decision C4).

### B4. D2 -- dead DAT data (never referenced)
| File | Lines | What | Conf |
|------|-------|------|------|
| isp_hub75_panel | 837-838,840 | `testValue`,`testValueMsg`,`msgScrnHd` (NON-dump dead DAT) | HIGH |
| demo_hub75_colorPad | 1124-1127 | `bmpFile1` FILE embed -- no consumer in this file (twin color.spin2 uses its copy) | MED-HIGH |
| demo_hub75_5x7font | 73-74 | `ROWS_PER_SCREEN_32`,`NBR_ROWS_32` CONs unused (the `_64` pair IS used) | MED |

---

## CLASS C -- DECISIONS NEEDED (do not apply without Stephen's call)

- **C1. Uncalled demo-helper PRIs / focused-test blocks** (color, colorPad, multi2x2panel,
  quadPanel, scroll). Intentional manual-activation demo library (X4). REC: **KEEP all.**
  If kept, B1's `red,green,blue` in the two `demoTest360ColorBrightness` PRIs still applies
  (clean the locals, keep the method).
- **C2. multi2x2panel under-documented uncalled PRIs.** If C1=KEEP, add the A1 doc blocks.
  If C1=CUT for multi2x2panel specifically, skip those doc-adds.
- **C3. colorUtils gamma R/G/B tables** (`gammaRed`/`gammaGreen`/`gammaBlue`, 349/368/386 +
  three identical `case led` arms all resolving to `@gamma`). Either develop's half-wired
  per-channel-gamma feature OR dead duplication. REC: **REMOVE dead tables + collapse the
  identical case arms to one range** (cleanup), NOT wire-up (that's a feature, out of scope).
  Confirm Stephen doesn't want per-channel gamma as a feature first.
- **C4. scrollingText `setFontInfo` params `leadingGap`/`hBitmapOffset`.** Removing the dead
  VARs (B3) orphans these params. Removing params changes the caller signature in
  display.spin2. REC: remove VARs + params together, update the one call site. Verify caller.
- **C5. rgb3bit `elseif bSetMidPins` branch (476-497).** Mid-16-pin config mode; `bSetMidPins`
  never set TRUE in Spin2 -> unreachable. Could be reserved hardware mode. HARDWARE SEMANTICS
  -- Stephen owns. REC: **KEEP unless Stephen confirms mid-pin mode unsupported.**
- **C6. multiPanel `DEMO_COUNT = 3` vs case arm 4 `demoPanelFillColors` unreachable.** Bug or
  intent? Either bump count to 4 (enable fill demo) or remove arm 4 + the PRI. Needs intent.
- **C7. display_bmp `isDebugLocn` (213-222) always-FALSE dead debug hook** + `showDebug`
  usage (199-202, 210-211) + unused DAT message strings (227-233). REC: remove as dead, OR
  (overlaps #9) channelize. Defer to Stephen / #9.
- **C8. panel.spin2 PWM-dump family** (X2). DEFER to task #9 -- do NOT delete in §4d.

---

## SEQUENCING WHEN APPLYING (on sign-off)
1. Class A first (byte-identical) -> recompile -> assert sha256 == baseline for touched files.
2. Class B next, **one file at a time** -> recompile clean 0-warn after each -> record new
   sha256 (expected to differ). Per-file isolation so any breakage bisects to one file.
3. Class C only the items Stephen greenlights.
4. Full 28-file `pnut-ts -d` clean 0-warn at the end. Commit.

---

## APPLICATION RESULTS (2026-06-12)

**Decisions (Stephen):** Scope = Class A + B. Demo library = KEEP all (no PRI deletions).
Gamma (C3) = cut per-channel, keep single table + bGammaEnable opt-in + gammaPeek +
gammaPtrs + gammaCorrectedSingleColor + brightness/MSB fix. C5/C6/C7 = leave as-is.
C4 (scrollingText font-padding param plumbing) = DEFERRED (dead-end feature spanning two
files; treated like C5/C6/C7). B2 (display multi-return placeholders) = DEFERRED. C8 panel
PWM-dump family = DEFERRED to task #9.

**Outcome:** 21 files changed, +58 / -402 lines. **28/28 compile clean, 0 warnings.**

**Behavior-preservation proof:**
- Comment-only removals proven byte-NEUTRAL: isp_hub75_rgb3bit (5 comment-blocks removed),
  hwBufferAccess, hwBuffers, fonts compile to .bin BYTE-IDENTICAL to baseline (they link no
  changed object). 10/28 binaries byte-identical total.
- The other 18 binaries changed for two legitimate reasons: (a) real Class-B dead-code
  removal in the object, (b) OBJ-dependency propagation (any top-level linking colorUtils /
  display picks up those objects' changes). Verified via dependency graph, not raw sha256.
- Brace-disabled blocks confirmed truly disabled (diff shows `-{`...`-}` wrappers):
  7seg-demo transitional block, colorPad alt-dispatch. color-demo alt-dispatch was
  `'`-line-commented.
- Gamma case-collapse behavior-identical: pGammaTable was always @gamma; led-validation
  abort preserved as `if led < LED_RED or led > LED_BLUE: abort`.

**Applied by class:**
- A (doc adds): colorUtils correctedColor/correctedSingleColor/colorAtDesiredBitWidth;
  multi2x2panel placeClock/placeDigit/5 PRIs/waitSec/wait1000thSecs.
- A (commented-scaffolding removal): ~30 clusters across display, colorUtils, screenUtils,
  display_bmp, fonts, scrollingText, rgb3bit, hwBufferAccess, and all demos. House-style
  inline `' debug(...)` traces intentionally KEPT.
- B (unused locals): display_bmp.haveError; color/colorPad demoTest360ColorBrightness
  red,green,blue (+stale @local docs); 7seg-demo showSecondsDots red,green,blue;
  colorPad main demoIndex.
- B (dead VARs): display.bDidShowOnce; scrollingText leftBitmap/rightBitmap/scrollCharOffset/
  remainingColumns/bScrolling/vtInsetInPix/isSetup (7); 7seg-obj.defaultColor;
  multiPanel.scrollPeriod; 7seg-demo.digitVal.
- B (dead DAT/CON/FILE): panel testValue/testValueMsg/msgScrnHd; colorPad bmpFile1 FILE;
  5x7font ROWS_PER_SCREEN_32/NBR_ROWS_32.
- C3 gamma: removed gammaRed/gammaGreen/gammaBlue tables (~768B) + collapsed no-op case arms
  + removed dead pGammaTable local. Single gamma table + opt-in retained.

**Deferred / follow-up:**
- C4: scrollingText setFontInfo leadingGap/hBitmapOffset params + leadingGapInPix/
  hBitmapOffsetInPix VARs = dead "font cell padding" plumbing through display.spin2. (ctx key
  task_10_c4_deferred)
- B2: display setCursorOnPanel.panelsPerCol / scrollColoredTextOnLnOfNPanels.offsetPixelRows
  multi-return placeholders (structurally required; marginal).
- C8: panel PWM-dump family -> task #9 DEBUG_MASK channelization.
- C5 rgb3bit bSetMidPins branch; C6 multiPanel DEMO_COUNT; C7 display_bmp isDebugLocn -- all
  left as-is per Stephen.
