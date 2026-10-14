# DOCS-REVISION — Sprint Plan

**Status:** started 2026-10-13. **Build:** 4.0.1 (Stephen, 2026-10-13: "yes A"; documentation and comments only, no behaviour or API change). **Source:** the organization study
`DOCs/analysis/2026-10-12-DOCS-ORGANIZATION-STUDY.md` (findings F1-F30, root causes R1-R5, page
set §6). Section numbers below are the plan's; `F`/`R`/`Q` numbers are the study's.

## Open Questions

None. Resolved 2026-10-13: the untracked internal documents (§7) reach Stephen's other Mac by his
own copy. Stephen: *"we [are] leaving them in the working tree untouched so i'll copy them"*.

## §0 Scope and decisions

**Scope (Stephen, 2026-10-13, "B"):** the study's reader pages: R1 the page-set moves, R2 facts
linked instead of restated, R3 homes for the journeys that have none, R4 the stale-page sweep, R5
the ICN2037 page; the tree decisions of 2026-10-12; and a voice and frame pass over the settled
set, last. **No punch-list item is taken.** All eleven active items stay on
`DOCs/plans/PUNCH-LIST.md`, declined this sprint. One consequence Stephen weighed in choosing B:
the process-documents item says to synthesize their user-useful findings *before* they stop being
published; this sprint stops publishing them (§7) and does not do that synthesis.

**Answered by Stephen (2026-10-13):**

| # | Decision | Ruling |
|---|---|---|
| A1 | Scope as above | "B" |
| A2 | A **light-weight quickstart with examples**, not a full programming guide; no public-method table | *"we scope it to a light-weight quickstart with examples, not a full guide"* |
| A3 | Images are **BMP only**; no page offers or plans another format | *"we are not going to support other image formats at this time, just .bmp"* |
| A4 | The roadmap stays public, as **one page** | "yes A" |

**Decided in planning from the tree and standing rulings.** Each is a decision Stephen can
overturn on reading this plan; none was asked (doctrine overlay, D8, 2026-10-13 instance).

| # | Decision | Basis |
|---|---|---|
| P1 | Trivially-safe fixes F2, F27, F28, F29 are made (F3 was fixed at the CONFIG-SIMPLIFICATION closeout) | factual errors; currency is a release deliverable |
| P2 | The documented start call is `display.start(display.HUB75_ADAPTER_n)` (F4, study Q1) | `isp_hub75_display.spin2:80-82` exports the names; all 11 demos start their adapter with this form (`grep -n "\.start(" driver/demo_hub75_*.spin2`); a user's program then names one object, not two |
| P3 | Troubleshooting is its own page (Q2) | its own journey; the Configuration Guide is already the longest page |
| P4 | The refresh **method** (T, j, /OE weighting, the column-clock loop) moves to THEOPS; the **target setting, measured rates and brightness** stay in the Configuration Guide (Q3) | Traced: FRAME-RATE plan (`DOCs/plans/archive/FRAME-RATE-SPRINT-PLAN.md:768`, «#102», 2026-10-05) homed method and rates together in the Guide to give them **one** home, at a time when internals were split over two pages. THEOPS becomes the single internals page here (§2), so the one-home goal holds with the method beside the other internals |
| P5 | Each chip's settings block goes to that chip's section of the Chip Matrix (Q4) | the block is per-chip fact; the Matrix is the per-chip home |
| P6 | Testing and Measurement is its own page; CONTRIBUTING links to it (Q5) | CONTRIBUTING is the pull-request process; the test tools are a contributor reference of ~130 lines today |
| P7 | No separate study of how the pages teach; that lens is part of §10 | the quickstart (A2) is the teaching page; §10 reads every page as its reader |
| P8 | Draw-time figures are **4.7 / 12.8 / 24.5 / 3.8 ms**, published in one home (F5, Q8) | measured on the current driver at bench B-2, 2026-10-10 (`DOCs/bench/RUN-NOTES.md:338-342`: fill 4,685, lines 12,776, text 24,466, BMP 3,820 us); no driver commit since touches the draw path. `ChangeLog.md:87` already carries them; `README.md:95` and `DOCs/WiringGuide.md:448` carry the older 13.0 / 24.6 |
| P9 | The Wiring Guide's heading becomes **Configuration Guide**; the file keeps the name `WiringGuide.md` (Q9) | 18 tracked files and `driver/isp_hub75_hwPanelConfig.spin2` link the filename; external links keep working |
| P10 | The merged adapter page keeps the filename `HUB75-brd-config.md` and absorbs `HUB75Adapter.md` | `HUB75-brd-config.md` has 4 inbound links (README, ICN2037, HardwareTurnon, an absolute GitHub URL in `HUB75Adapter.md:41`); `HUB75Adapter.md` has 1 |
| P11 | Retired pages are deleted, not left as "moved" stubs; every in-repo link is repointed | a stub is a page with no reader; the study's set has no place for one |
| P12 | The roadmap page is `DOCs/Roadmap.md` | A4 |

## §1 Stale facts (R4: F2, F27, F28, F29)

- **F2:** the "cube is one horizontal chain, 384 x 64" item (`DOCs/FutureDirections-ImageAndColor.md:226-229`) is deleted when that page becomes the roadmap (§3d); it is not carried.
- **F27:** `README.md:323` "We will have a P2 Eval HUB75 Adapter board for sale": it is sold; state it and link the store link already at `:9`.
- **F28 (corrected, revision 2):** no v3.0.3 was released; v3.0.2 (the last v3 tag) uses `PINS_Pxx_Pyy`, and 4.0.0 renamed them. `Checklist-v3-v4.md` is right. The wrong page is `Checklist-v2-v3.md`, whose examples (`:53,116,145`) and "v3.0.3+" note (`:87`) were moved to the new names on 2026-10-01 for a 3.0.3 that was folded into 4.0.0: restore the v3 names and point the note at the v3-v4 rename section.
- **F29:** `DOCs/WiringGuide.md:340` limits row for ICN2038S reads "4 (single-ended: one panel)". Restate from `checkPanelLimit()` (`driver/isp_hub75_hwBufferAccess.spin2:1516-1543`): 512 column clocks, `SCAN_4` counts each column twice, so a 64-column ICN2038S panel is 128 clocks and four fit along one cable.
- **Verify:** each corrected line read against its code or sibling page; `python3 tools/check_docs.py` clean.

## §2 Page set: retire, merge, re-home (R1)

The target set is study §6 as amended by §0. Moves:

a. **`DOCs/MultiPanelConfiguration.md` retires.** Its unique content goes:
   troubleshooting list (`:121-150`) → Troubleshooting (§3b); memory-by-arrangement (`:97-111`) and
   colours-per-depth (`:43-58`) tables → the Configuration Guide's limits and hub-RAM section, checked
   against `hwPanelConfig` sizing before entry; the API snippet (`:175-179`, undefined names) → not
   carried; the quickstart's examples replace it. Inbound links: `DOCs/WiringGuide.md:5`,
   `HUB75-brd-config.md:23`, `HardwareTurnon.md:24`.
b. **`DOCs/TheoryOfOperations.md` retires into `THEOPS.md`** (F9). Its unique sections (1.1-1.2,
   2.x, 3.x, 4.1, 4.4, 5.x per study §6) move to THEOPS, merged with THEOPS's own copies, not
   appended; 6.x (configuration) is dropped for links to the Guide; 7.x (chips, add a chip) goes to
   the Matrix (§4, F14); the pin appendix becomes a link to the adapter page. Inbound:
   `DOCs/WiringGuide.md:384,448` (anchors `#51-refresh-rate`, `#22-pixel-write-operation`),
   `THEOPS.md:6,208`. THEOPS keeps one title, "Driver Details" naming stops (F9).
c. **`CubePix.md` retires into `HardwareTurnon.md`** (F19): its photos join the cube checkout,
   whose text is already there (`HardwareTurnon.md:89-105` = `CubePix.md:6-20`). Inbound:
   `README.md:75`, `HardwareTurnon.md:97`.
d. **Adapter pages merge into `HUB75-brd-config.md`** (P10, F22): product description, revisions,
   connectors, pinout; one spelling, "Adapter". Inbound to `HUB75Adapter.md`:
   `HardwareTurnon.md:22`.
e. **`DOCs/AuthorTestConfigurations.md` splits** (F13): Stephen's rig record and photos stay (the
   AUTHORS page); per-panel settings blocks (`:7-341`) go to the Matrix chip sections (P5); the
   contributor tools (`:416-544`) go to Testing and Measurement (§3c).
f. **The bring-up procedure** (`HardwareTurnon.md:18-28`, F23) moves to the quickstart's first
   step; HardwareTurnon keeps the story.
g. **ChangeLog's 2020 diary** (`ChangeLog.md:194-228`, F25) moves to HardwareTurnon; the ChangeLog
   keeps release entries only (`central:changelog-voicing`).
h. **README navigation** (F30): every kept page reachable from the README's page list.

- **Verify:** `git grep` for each retired filename returns only ChangeLog history lines and
  ignored areas; every relative link and `#anchor` in the tracked pages resolves (checked by script
  in the sprint's scratch area, not a new tool); `check_docs.py` ORPHAN 0.

## §3 New pages (R3, A2-A4)

a. **`DOCs/QuickStart.md`** — a light-weight start with worked examples (A2). From wired panels
   to a running program: the five bring-up steps (§2f); including the objects and starting one
   adapter with `display.start(display.HUB75_ADAPTER_1)` (P2); a handful of short examples, each
   copied from a demo that compiles and cited to it (fill and pixel, text, scrolling text, a BMP
   image, commit); a second adapter; then "where next": the demos table and the doc comments in
   `isp_hub75_display.spin2` for every other call. **BMP only** (A3): how to make a BMP the driver
   loads (`isp_hub75_display_bmp.spin2:99,109`; the format and size it accepts read from the
   loader, not from FutureDirections), replacing the PNG guidance (F1). The README's "Writing
   display code" section (`README.md:263-297`) becomes a short lead-in and link; its demo table
   stays in the README.
   - *Verify:* every example compiles as a top file in the scratch area (`pnut-ts -d`) on the
     committed config; names match `isp_hub75_display.spin2` PUB signatures.
b. **`DOCs/Troubleshooting.md`** (P3, F11) — symptom → cause → fix: dark panel, wrong colours,
   ghosting or repeated rows (scan), flicker, a startup message. Points into the Guide's startup
   messages and identify sections and the Matrix's scan symptoms (`ChipCharacteristicsMatrix.md:23`)
   rather than restating them.
c. **`DOCs/TestingAndMeasurement.md`** (P6, F12) — the test top files, debug switches, the
   instrument, logic analyzer, pin identify; from `THEOPS.md:45-56,230-243`,
   `AuthorTestConfigurations.md:416-544`. `CONTRIBUTING.md:22` and the README demo table link here.
d. **`DOCs/Roadmap.md`** (A4, P12, F24) — `PSRAMExpansion.md` and
   `FutureDirections-ImageAndColor.md` merged, both originals deleted. Present-tense passages
   (`PSRAMExpansion.md:17-40,236-255`) are replaced by links to their homes; the citation of the
   ignored reference driver (`:15,144,294-300`) is removed; image-making guidance goes to §3a; no
   item plans an image format other than BMP (A3); F2 dropped. Linked from the README's Pending
   Development. `tools/check_docs.py:48-49` lists the two retired files as intent pages; see Named
   unknowns.

## §4 One home per fact (R2)

Each restated fact gets one home; the other pages carry a short lead-in and a link.

| Fact | Home | Restatements to replace (study evidence) |
|---|---|---|
| Start call (F4) | QuickStart | `WiringGuide.md:60`, `README.md:139`, `Checklist-v3-v4.md:147`, `HardwareTurnon.md:25` aligned to P2 |
| Draw times (F5) | Configuration Guide, 4.7 / 12.8 / 24.5 / 3.8 ms (P8) | README `:95` lead-in links; ChangeLog `:87` already agrees |
| Add a new chip (F14) | Chip Matrix (`:644-669`) | TheoryOfOperations 7.3 dropped |
| Latch styles (F15) | Chip Matrix, one vocabulary, with the two latch figures from `HUB75-Driver-SWver1.md:44-81` | SWver0/1 become pure history and link forward |
| Clock limits (F16) | Chip Matrix ratings, one framing: "rated X MHz; the 20 ns pulse rule caps the loop at 25 MHz" | Guide, THEOPS, ICN2037, roadmap link |
| Rig clock and refresh figures (F17) | Configuration Guide | AuthorTestConfigurations, ICN2037, roadmap, README link |
| Panel background, goals (F19, F21) | README | HardwareTurnon links; one pitch range and A-E address lines, from the Matrix |
| Pin offsets (F20) | `HUB75-brd-config.md` | THEOPS `:270-278`, ICN2037 `:280-301` link |
| Release history (F26) | ChangeLog | README "Latest Updates" cut to the latest 2-3 releases |

- **Verify:** for each row, `git grep` of the fact's distinctive figure or phrase finds it on the
  home page only, plus lead-ins that link.

## §5 Refresh mechanism home (P4)

Move "The method" and the column-clock paragraph (`DOCs/WiringGuide.md:386-392`) to THEOPS's
internals, merged with `THEOPS.md:216` and TheoryOfOperations 3.x / 5.1 into one telling. The Guide
keeps "The target refresh rate", measured rates and brightness, and opens its refresh section with
one sentence and a link to the method. The "one place" sentence (`:384`) is rewritten to say what
the Guide holds.

- **Verify:** the j / T algorithm is told once (grep `2^*k*` and "T = S"); every refresh figure
  is in the Guide only.

## §6 The ICN2037 page (R5, F6)

`DOCs/ICN2037/README.md`: the recommendation table (`:208-220`, "keep to <= 20 MHz") is restated
as measurement history, leading with what the driver runs (22.3 MHz, the 25.0 MHz chain limit in
the Matrix) and linking the Matrix for the rating. The page gets the full frame (masthead, pages
bar, standard sections), per the 2026-10-12 decision; the other chip folders' READMEs stay folder
descriptions (doctrine overlay D9).

## §7 Internal documents leave the public tree (decided 2026-10-12)

The files leave the index only (`git rm --cached`); this Mac's working copies are untouched. When the other Mac pulls, git deletes its copies; Stephen copies them across himself (2026-10-13). The commit message says so, so the pull is not a surprise.

- Untrack and ignore `DOCs/plans/archive/` (17 files); `DOCs/bench/` (4 files).
- Finished analyses move to `DOCs/analysis/archive/`, ignored (the 9 tracked files and the two
  untracked ones, `2026-10-09-CENTRAL-DOCTRINE-RECOMMENDATION.md` and the study, once this plan
  closes).
- The four registers (`DOCs/TECHNICAL_DEBT.md`, `LOGIC-BUG-ANALYSIS.md`, `MAGIC-NUMBER-TRIAGE.md`,
  `CodeAssessment.md`) move to the archive, ignored.
- Kept tracked until this sprint's closeout: this plan and `DOCs/plans/PUNCH-LIST.md`.
- Not touched: `.devcontainer/`, `tools/` (2026-10-12). No history rewrite.
- Commit messages from here on carry no «#N» (2026-10-12).
- **Verify:** `git ls-files DOCs/plans/archive DOCs/bench DOCs/analysis` empty except the kept
  two; each moved file still present in this working tree; `check_docs.py` clean.

## §8 Source comments name no plan, task or sprint (decided 2026-10-12)

Eleven comments: `isp_hub75_rgb3bit.spin2:35`, `isp_hub75_instrument.spin2:20,493`,
`isp_hub75_cube.spin2:122`, `test_hub75_converter.spin2:497,663`,
`test_hub75_cube_fold.spin2:33,46`, `test_hub75_oe_bcm.spin2:16,20`, `test_hub75_rates.spin2:22`.
Each is reworded to state the fact without its provenance. Governed by
`central:spin2-authoring-guide`.

- **Verify:** re-grep `driver/*.spin2` for `«#`, `#[0-9]`, `sprint`, `plan`, `task` (the hits
  reviewed, not just counted); all 18 top files compile with 0 warnings; non-debug `.bin` sha256 of
  all 18 equal before and after (comments only); `python3 tools/check_style.py` clean.

## §9 (withdrawn, revision 1)

No bench visit. The figures are on record for the current driver (P8).

## §10 Voice and frame pass, last

Over the settled page set only, against `REF-NO-COMMIT/p2-repo-voice-guide.md` (frame §2, register
§3, page shapes §5) and the 2026-10-12 voice audit's findings. Each page also read once as its
reader would (P7): does it answer the journey's question in the study §3 table, in order, with no
prerequisite it does not link. `ChangeLog.md` against `central:changelog-voicing`.

## §11 ChangeLog

One entry under `## [4.0.1]`: documentation
reorganized, the quickstart, troubleshooting, testing and roadmap pages, retired and merged pages
named so a bookmark can be followed. Governed by `central:changelog-voicing` (class 1, §4.4: state
current truth).

## Documentation Blast Radius

This sprint changes documentation and comments only; no driver behaviour, output or API changes.

`python3 tools/check_docs.py`, 2026-10-13, at `5885055`:

```
Doc-drift audit (advisory) -- 24 documents, 35 .spin2 sources

ORPHAN (0)

DUPLICATE (0)

COUNT (0)
```

Every artifact touched is enumerated in §1-§8. Counts that change: the README's page list (§2h);
the THEOPS file-organization table is unaffected (no `.spin2` file added or removed). The
ChangeLog is in scope (§11). Docstrings: §8's eleven comments only.

## Standing rulings that bear on this sprint

- 2026-10-12 tree decisions (§7, §8, §6 frame) — todo-mcp context `session_2026-10-12_docs_study_state`.
- 2026-10-12, Stephen on the two Macs; carrier ruled 2026-10-13: he copies the untracked files himself (§7).
- 2026-10-10, process documents: synthesize before unpublishing — declined this sprint by A1.
- 2026-10-13, test platform pins are P16-P31 for every panel (§9; doctrine overlay D3).
- Doctrine overlay D9 (2026-10-12): folder READMEs describe their folder (§6).

## Named unknowns

- **`tools/check_docs.py` and the roadmap.** Its exclusion list names the two retired intent pages
  (`:48-49`). With them gone, `DOCs/Roadmap.md` is audited as a user page, and planned names in it
  may report as ORPHAN. `tools/` is not touched this sprint (2026-10-12). If the audit reports
  roadmap items, the response is a question to Stephen at that point, with the report.
- **External bookmarks** to retired pages break (P11). The ChangeLog entry (§11) names where each
  went.

## Entry baseline (2026-10-13, `5885055`)

| Gate | Result |
|---|---|
| 18 top files, `pnut-ts -d -l -m` | exit 0, 0 warnings (18 of 18) |
| `python3 tools/check_style.py` | clean (the implemented T1 rules; 27 rules not script-checked, as at the CONFIG-SIMPLIFICATION exit) |
| `python3 tools/check_docs.py` | ORPHAN 0, DUPLICATE 0, COUNT 0 |
| Tracking | board 0 tasks; context 2 keys; ready |
| Working tree | clean at `5885055`; this plan committed as the sprint's start; the two untracked analyses stay untracked (they go to the ignored archive in §7) |
| Failure groups | none; nothing deferred |

## Revisions

- **2026-10-13, revision 1 — cause 2, research incomplete.** §9's bench visit withdrawn and «#184» superseded. Stephen: *"we'll only do bench after all the other work is done. if the driver hasn't changed - why bench?"* The draw times were already measured on the current driver at B-2 (2026-10-10); the planning search looked for the millisecond strings, and the bench notes record microseconds. P8 now states the recorded figures; §4's row and «#194» carry them.
- **2026-10-13, revision 2 — cause 2, research incomplete.** §1's F28 fix moves from `Checklist-v3-v4.md` to `Checklist-v2-v3.md`. The study read the "v3.0.3+" note as fact; `git show v3.0.2:driver/isp_hub75_hwEnums.spin2` shows `PINS_P16_P31`, and no v3.0.3 tag exists.

## Dispatch

Model: `arbiter-serial` (project default). The files every task writes overlap (README, the
Configuration Guide, THEOPS, the Matrix), so no two tasks run at once. No task is two-phase: no
task's shape is a design later tasks build on. Order rules applied: the page moves come before the
one-home pass; the link sweep runs after every move; the voice and frame pass is last because it
audits every task before it.

## Section ↔ task cross-reference

| Plan § | Deliverable | Task | seq |
| ------ | ----------- | ---- | --- |
| §1 | Stale facts F27, F28, F29 (F2 in §3d) | «#182» | 1 |
| §8 | Source comments without provenance | «#183» | 2 |
| §9 | withdrawn (revision 1) | «#184» SUPERSEDED | — |
| §2b | THEOPS absorbs TheoryOfOperations | «#185» | 4 |
| §5 | Refresh method told once, in THEOPS | «#186» | 5 |
| §2a, §3b | Troubleshooting page; MultiPanelConfiguration retired | «#187» | 6 |
| §2e, §3c | Testing and Measurement; chip blocks to the Matrix | «#188» | 7 |
| §2f, §3a | QuickStart | «#189» | 8 |
| §3d | Roadmap | «#190» | 9 |
| §2c, §2g | CubePix and the 2020 diary into HardwareTurnon | «#191» | 10 |
| §2d | One adapter page | «#192» | 11 |
| §6 | ICN2037 page | «#193» | 12 |
| §4 | One home per fact | «#194» | 13 |
| §2h | README reachability; link sweep | «#195» | 14 |
| §7 | Internal documents leave the public tree | «#196» | 15 |
| §11 | ChangeLog 4.0.1 | «#197» | 16 |
| §10 | Voice and frame pass | «#198» | 17 |
