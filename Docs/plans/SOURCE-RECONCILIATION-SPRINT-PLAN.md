# SOURCE-RECONCILIATION — Sprint Plan

Unify the three diverged sources of the HUB75 driver into a single,
authoring-guide-compliant codebase on `main`.

## Why this sprint exists

Work was done some time ago and landed on a branch (`origin/develop`)
that drifted from `main`. Meanwhile `main` itself advanced, and a
style/authoring-guide reformatting pass was started in the working tree
but never committed. The result is three overlapping sources of truth
for the same files. This sprint reconciles them into one clean `main`.

## The three sources (established by research)

Merge-base of `main` and `develop` is **`a5bb00b`** ("Update
ChangeLog.md"). Both branches diverged from there and independently
rewrote the same core driver files.

| Source | What it carries | Magnitude vs. merge-base |
|---|---|---|
| **`main` (committed)** | 5 commits: object-hierarchy reduction, removed-unused, doc/wiring work — substantial *code* changes, not just docs | 36 files, +2,468 / −393 |
| **`main` (uncommitted)** | The in-progress authoring-guide **reformatting** pass | 23 `.spin2` files, ~10.4k lines reshaped |
| **`origin/develop`** | Forgotten **feature work**: clock-independent timing, 2×2 panel grids, per-panel rotation, 5-bit color fixes, MSB-black fix, new chip docs, new demos | 20 commits, 48 files, +12,159 / −459 |
| `origin/feature-clock1` | 2020 placeholder branch; its one commit edits `isp_hub75_binBit.spin2`, a file that no longer exists | 1 trivial commit — investigate then likely delete |

## Strategy (confirmed): features-first, restyle-last

Feature changes are *semantic* — expensive to redo, must be preserved.
Reformatting is *mechanical* — cheap to redo, expensive to merge. So:

1. **Preserve** the uncommitted reformat as a reference artifact (never
   lost), then shelve it.
2. **Merge `develop` into `main`**, resolving the genuine
   semantic-vs-semantic conflicts on the functional code (style
   ignored at this stage).
3. **Regenerate** the `.bin.GOLD` baselines from the merged,
   feature-bearing code.
4. **Re-apply the authoring-guide style pass** over the unified tree,
   GOLD-verified to prove the restyle changed zero emitted code.

This sequencing turns what would be mechanical-vs-semantic conflicts on
every file into a single, contained semantic merge followed by a clean
mechanical pass.

## The real merge map (from a trial merge — authoritative)

`git merge-tree main origin/develop` was run (working tree untouched).
**Only 10 files actually conflict**; everything else auto-merges. This
is the backbone of the file-by-file matrix in §1.

- **Conflicting (manual resolution):** `.gitignore` + 9 driver files —
  `isp_hub75_display`, `hwBufferAccess`, `panel`, `rgb3bit`,
  `scrollingText`, `colorUtils`, `display_bmp`, `7seg`, `screenUtils`.
- **Auto-merging:** all 8 demos, `segment`, `fonts`, `color`,
  `anlyCheck`, `hwBuffers`, `hwEnums`, `hwPanelConfig`, every new
  develop file, and all docs.

Effort is expressed as **complexity tiers** (Heavy / Moderate / Light /
Trivial), not time — per planning convention.

---

## §1. Phase-1 deliverable — File-by-file reconciliation analysis

The product of Phase 1 is the matrix below: for every file, its
contributing sources, the merge approach, and an effort tier. Δ columns
are line-change counts vs. merge-base (`main Δ` / `dev Δ`) and the
uncommitted `reformat Δ`. "Conflict" is from the trial merge.

### 1a. Hard merges — semantic-vs-semantic conflicts (9 driver files)

Resolve functionally first (preserve both sides' behavior); restyle in
§4. For these 9, the *current* uncommitted reformat is discarded and
re-derived on the merged code (it cannot apply to post-merge content).

| File | main Δ | dev Δ | reformat Δ | Tier | Merge approach |
|---|---|---|---|---|---|
| `isp_hub75_rgb3bit.spin2` | 87 | 228 | 1836 | **Heavy** | PASM2 cog driver — the most delicate. develop's clock-independent timing rewires the inner loop; main's hierarchy changes touch the same. Resolve line-by-line against P2KB timing semantics; verify on hardware. |
| `isp_hub75_display.spin2` | 534 | 347 | 857 | **Heavy** | Core public API. Both sides added/rewrote drawing routines (main: 2×2-grid display routines; develop: rotation + grid). Reconcile method-by-method; watch for duplicate/competing implementations of the same primitive. |
| `isp_hub75_hwBufferAccess.spin2` | 343 | 466 | 513 | **Heavy** | develop moved screen buffers out and reworked access; main also restructured. Reconcile the buffer-ownership model deliberately — this is the object boundary both sides changed. |
| `isp_hub75_panel.spin2` | 167 | 333 | 842 | **Heavy** | Screen→PWM conversion. develop's per-panel rotation/wire-order + main's changes overlap. |
| `isp_hub75_scrollingText.spin2` | 199 | 17 | 836 | **Moderate** | Mostly main-side growth; develop touched lightly. Take main's version as base, fold develop's small delta. |
| `isp_hub75_colorUtils.spin2` | 157 | 25 | 302 | **Moderate** | main-heavy; develop's 5-bit color fix must survive. |
| `isp_hub75_display_bmp.spin2` | 71 | 105 | 264 | **Moderate** | Both modest; straightforward but real overlap. |
| `isp_hub75_7seg.spin2` | 69 | 7 | 246 | **Light-Mod** | main-heavy; develop delta tiny. |
| `isp_hub75_screenUtils.spin2` | 46 | 41 | 85 | **Light-Mod** | Both small; pixel primitives. |

### 1b. Clean auto-merge, then restyle (reformat-set, develop touched)

Git merges these without conflict; the restyle in §4 is re-derived
because develop changed them post-reformat-base.

| File | main Δ | dev Δ | reformat Δ | Tier |
|---|---|---|---|---|
| `isp_hub75_fonts.spin2` | 58 | 0 | **11078** | **Moderate** (huge mechanical table realignment, no conflict) |
| `isp_hub75_segment.spin2` | 83 | 37 | 525 | Light-Mod |
| `isp_hub75_anlyCheck.spin2` | 19 | ~10 | 120 | Light |
| `isp_hub75_hwPanelConfig.spin2` | 10 | ~? | 117 | Light |
| `isp_hub75_hwBuffers.spin2` | 19 | 6 | 47 | Trivial |
| `isp_hub75_hwEnums.spin2` | 5 | ~? | 15 | Trivial |
| `demo_hub75_7seg.spin2` | 55 | 2 | 233 | Light |
| `demo_hub75_color.spin2` | 347 | 3 | 616 | Light-Mod |

### 1c. Reformat-set files develop did NOT touch — stashed reformat re-applies cleanly

For these 8, develop made no change, so the shelved reformat patch
re-applies directly after the merge (no re-derivation). Lowest-risk
restyle.

| File | reformat Δ | Tier |
|---|---|---|
| `isp_hub75_fonts.spin2` — *(see 1b; develop untouched, so its reformat also re-applies)* | 11078 | Moderate (mechanical) |
| `demo_hub75_colorPad.spin2` | 1307 | Light (re-apply) |
| `demo_hub75_multiPanel.spin2` | 363 | Trivial |
| `demo_hub75_5x7font.spin2` | 251 | Trivial |
| `demo_hub75_text.spin2` | 228 | Trivial |
| `demo_hub75_scroll.spin2` | 66 | Trivial |
| `demo_hub75_hwGeometry.spin2` | 29 | Trivial |
| `isp_hub75_color.spin2` | 64 | Trivial |

*(Note: `fonts` appears in both 1b and here only to flag it; it is one
file — develop did not touch it, so its large reformat re-applies.)*

### 1d. Pure additions from develop — just land (no main version)

| File(s) | Disposition | Tier |
|---|---|---|
| `demo_hub75_multi2x2panel.spin2`, `demo_hub75_numberPanels.spin2`, `demo_hub75_quadPanel.spin2` | New demos — land, then include in compile/restyle sweep | Light |
| `test_hub75_pin_identify.spin2` | New test top file — land (keep, OQ-2) | Light |
| `Docs/` additions: `FutureDirections-ImageAndColor.md`, `MultiPanelConfiguration.md`, `PSRAMExpansion.md`, `TheoryOfOperations.md`, `TECHNICAL_DEBT.md`, `Docs/Plans/*`, new chip dirs (`GS6238S`, `RUC7258`, `TC7262`, `MW245`, `TC7258EN`), `ICN2037/*` | Land as history/reference | Trivial |
| `driver/chk`, `driver/chk.diff` | Temp debug artifacts — **exclude** from final main (OQ-1) | Trivial |

### 1e. Trivial conflict

| File | Approach |
|---|---|
| `.gitignore` | Union the two sides' entries; reconcile against the current working-tree `.gitignore` change too. |

---

## §2. feature-clock1 investigation

Research task (not assumed delete). Confirm the branch carries nothing
salvageable before disposing.

- Inspect commit `37d932e` and the state of `isp_hub75_binBit.spin2` at
  that point; confirm the file/concept is fully superseded by today's
  `rgb3bit` driver.
- Walk the branch's reachable history for any unique content not already
  in `main`/`develop`.
- **Outcome:** either (a) confirmed vestigial → delete `origin/feature-clock1`,
  or (b) salvageable fragment found → fold it into the §3 merge.
- **Verification:** the disposition decision is recorded; if deleted, the
  deletion is intentional and noted.

**OUTCOME (2026-06-06, task «#1»): (a) confirmed vestigial — DELETED.**
`git log main..origin/feature-clock1` showed exactly one commit (`37d932e`,
2020-12-01) editing a single line of `driver/isp_hub75_binBit.spin2` — a
file that is ABSENT from `main` (removed in `fc3cd59` "remove clock demo
for now"). The branch sat 129 commits behind `main`; nothing salvageable.
Deleted with `git push origin --delete feature-clock1` (succeeded).
**Restore (if ever needed):**
`git push origin 37d932e4a8e67e9412f19d599150b8a67f197b05:refs/heads/feature-clock1`.

## §3. Execute the develop→main merge (functional only)

- Preserve the uncommitted reformat first: stash it **and** export a
  reference patch to `Docs/analysis/` (or a `wip/reformat-snapshot`
  branch) so the in-progress style work is never lost.
- Merge `origin/develop` into `main`. Auto-merging files (§1b–1e) need
  no hand work; resolve the 9 conflicts (§1a) **functionally**, ignoring
  style, preserving every feature from both sides.
- For each conflicted file, the verification case set: **normal** — file
  compiles under `pnut-ts`; **edge** — no feature from either side is
  dropped (cross-check method inventory before/after); **error** — no
  duplicate/competing implementation of the same primitive survives.
- Deliverable: a merged tree that compiles (all demos, container
  `pnut-ts`) with both sides' features present, not yet restyled.

## §4. Regenerate GOLD baselines, then restyle the unified tree

- Regenerate `*.bin.GOLD` from the merged, feature-bearing binaries
  (the old GOLD baselines predate develop's features and are now stale).
- Re-apply the authoring-guide style pass over the unified tree per
  `Docs/procedures/SPIN2-AUTHORING-GUIDE.md`:
  - §1c files: re-apply the shelved reformat patch directly.
  - §1a/§1b files: re-derive the reformat on the merged content.
- **GOLD verification** (macOS side, `check_reformat.sh`): every restyled
  file's `.bin` must md5-match its freshly-regenerated `.bin.GOLD` — the
  restyle must change **zero** emitted code. Any mismatch = a restyle that
  altered behavior = defect.
- Container-side case: all demos compile clean under `pnut-ts` (0
  warnings) at every step.

**OUTCOME (2026-06-06, task «#3», §4a — GOLD regen): DONE in container.**
Finding overturned the planned "macOS-only" placement: `.bin`/`.bin.GOLD`
are gitignored (local-only) and `pnut-ts` itself emits the `.bin`, so the
container can both regenerate AND verify GOLD using `cmp`/`sha256sum` in
place of macOS `md5`. Regenerated the full set from the merged
(pre-restyle) tree: all **28** `.spin2` compiled clean (0 warnings) and
each `.bin` was copied to its `.bin.GOLD`. This refreshes the 24 stale
baselines AND adds 4 new ones for develop's new files
(`demo_hub75_multi2x2panel`, `demo_hub75_numberPanels`,
`demo_hub75_quadPanel`, `test_hub75_pin_identify`) — giving whole-tree
restyle coverage. Self-consistency confirmed: a recompile + `cmp` pass
matched 28/28 deterministically. Baselines are NOT committed (gitignored);
they live locally to gate the §4b restyle. The macOS `check_reformat.sh`
still applies on that side (uses `md5`); §4b container verification will
use a `cmp`-based equivalent.

## §5. Documentation, ChangeLog & contribute to main

- Reconcile `ChangeLog.md` across the merge; record the unified feature
  set. Version bump decision deferred to build-wrapup but flagged
  (§OQ-4).
- Update `THEOPS.md` / `README.md` if the merged feature set (2×2 grids,
  rotation, clock-independent timing) changed documented behavior.
- Move develop's `Docs/Plans/` content down into `Docs/plans/`
  (lowercase, per OQ-3) and confirm no case-collision remains.
- Final state: one unified, compile-clean, GOLD-stable, authoring-guide-
  compliant `main`; `develop` and (pending §2) `feature-clock1`
  reconciled.
- **Hardware verification (macOS):** flash representative demos —
  `demo_hub75_color` (broadest), a 2×2-grid demo (`demo_hub75_quadPanel`
  / `multi2x2panel`), and `demo_hub75_scroll` — to confirm develop's
  features actually work in the unified build, not just compile.

---

## § Open Questions — RESOLVED

1. **OQ-1 — `driver/chk` and `driver/chk.diff`:** **Exclude** from the
   final `main` (temp debug artifacts). Dropped during the §3 merge.
2. **OQ-2 — New develop top files:** **Keep all four** —
   `demo_hub75_multi2x2panel`, `demo_hub75_numberPanels`,
   `demo_hub75_quadPanel`, `test_hub75_pin_identify` — landed and included
   in the compile/restyle sweep.
3. **OQ-3 — `Docs/` plans casing:** Standardize on **`Docs/plans/`**
   (lowercase). develop's `Docs/Plans/` content is moved down into
   `Docs/plans/` during the merge; the `PLAN_DIR` convention is unchanged.
4. **OQ-4 — Version after reconciliation:** Deferred to `build-wrapup`
   (anticipated `3.1.0` for the new 2×2-grid / rotation / timing feature
   set). ChangeLog work in §5 anticipates a minor-version bump.
5. **OQ-5 — develop's historical sprint docs** (Sprint-2x2-Panel-Repair,
   Sprint-Performance-Upgrade, THEORY_OF_OPERATIONS_SIGNALING): **Keep as
   history**, relocated into `Docs/plans/` (lowercase) per OQ-3.

All open questions resolved — research and questions passes are empty.
The plan is ready to execute (via `sprint-start`).

---

## Verification summary (case sets the sprint must prove)

- **Compile (container, every phase):** all demo top files build under
  `pnut-ts` with 0 warnings.
- **Merge integrity:** no feature from `main` or `develop` dropped;
  no duplicate competing implementations (method-inventory diff).
- **Restyle integrity (macOS GOLD):** restyled `.bin` md5-matches the
  regenerated `.bin.GOLD` — zero emitted-code change.
- **Hardware (macOS):** representative demos run correctly, exercising
  develop's headline features.

---

## Sprint start record (2026-06-06, via `sprint-start`)

The sprint was started on 2026-06-06. The following were pinned at start
(things that depend on *when* execution begins, not knowable at plan time).

### Build version

**`3.0.3`** — agreed at start. This is a **patch** bump from the `v3.0.2`
tag (ChangeLog currently heads at `[3.0.1]`, behind the tags). This
**overrides OQ-4's anticipated `3.1.0`**: the reconciliation is being
treated as consolidation/fixes rather than a new-feature minor release.
ChangeLog entry is written at `build-wrapup`.

### Working-tree audit (live re-check)

- **23 `.spin2` style-reformat edits** (the uncommitted authoring-guide
  pass) were the only blast-radius mid-edits. **Decision: snapshot branch.**
  Committed to **`wip/reformat-snapshot`** (tip `881cdef`); `main` working
  tree returned to clean. This preserves the reformat for the §4 restyle
  pass without letting it land on `main` ahead of the develop merge.
- **Untracked foundation** (`.claude/` skill harness, `.devcontainer/`,
  this plan doc, plus host-specific `.gitignore` rules). **Decision: commit
  all to main now.** Landed as two commits: `b1e5d72` (dev container +
  skill harness + gitignore rules) and `5c26090` (this plan doc). `main`
  is ahead of `origin/main` by 2 (not yet pushed).
- **Branch note (beyond plan §5):** a **local** `develop` exists, in sync
  with `origin/develop` — post-merge cleanup must delete both local and
  remote.
- **`feature-clock1`:** confirmed vestigial (1 commit editing the deleted
  `isp_hub75_binBit.spin2`, 129 commits behind `main`). §2 is a
  confirm-and-delete, not open research.

### Entry checks (recorded as the entry baseline)

- **Tracking-readiness: READY.** 0 tasks on the board; 1 stale resume
  breadcrumb (`temp_resume_2026-06-06`) pruned; auto-memory lean
  (MEMORY.md 4 lines, 2 load-bearing files). Context now empty.
- **Baseline-health: GREEN.** All 8 demo top files compile clean under
  `pnut-ts v1.55.0`, **0 warnings**, on clean `main`. No failure groups.
  **Not exercised (container limitation):** the golden-binary md5 check
  (`check_reformat.sh`, macOS-only) — GOLD verification is the §4 macOS
  step. Exit baseline at closeout asserts no regression vs. this.

---

## Section <-> task cross-reference (via `plan-to-tasks`, 2026-06-06)

Sprint tag: **`src-reconcile`**. §1 (file-by-file analysis) is already
delivered in this plan, so it carries no task. Tasks are ordered
foundational -> dependent by `seq`; declared dependencies are documentary
(stated in each task's prose), `seq` is the operational order.

| Plan § | Deliverable | Task | seq | Effort | Where |
| ------ | ----------- | ---- | --- | ------ | ----- |
| §1 | File-by-file reconciliation analysis | *(none — delivered in plan)* | — | — | — |
| §2 | Dispose vestigial `feature-clock1` | «#1» | 1 | 20m | container |
| §3 | develop->main functional merge | «#2» | 2 | 10h | container |
| §4a | Regenerate GOLD from merged tree | «#3» | 3 | 30m | container (finding: not macOS-only) |
| §4b | Re-apply/re-derive restyle, GOLD-verified | «#4» | 4 | 6h | container+macOS |
| §5a | Reconcile ChangeLog & docs | «#5» | 5 | 2h | container |
| §5b | Hardware verification | «#6» | 6 | 1h30m | macOS |
| §5c | Finalize: push main, delete `develop` | «#7» | 7 | 30m | container |
