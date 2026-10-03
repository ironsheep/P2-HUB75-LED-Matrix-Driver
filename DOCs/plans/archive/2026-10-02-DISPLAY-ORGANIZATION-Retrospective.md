# DISPLAY-ORGANIZATION — Retrospective

**Sprint:** DISPLAY-ORGANIZATION, 2026-10-01 to 2026-10-02.
- **Closeout:** [`2026-10-02-DISPLAY-ORGANIZATION-Sprint-Closeout.md`](2026-10-02-DISPLAY-ORGANIZATION-Sprint-Closeout.md).
- **Build:** 4.0.0, started, not tagged; it continues in later sprints.
- **Tasks:** 21 completed, none paused or superseded.
- **Plan revisions:** one agreed scope change, SC-1, rotation.

## Discovered perspectives

- **"Rotation" was two measures.** The hardware turned (mounting) and the picture turned (content). They give the same image under opposite names. The code and the glossary had disagreed silently until the bench (SC-1).
- **Content rotation is a bitmap operation, not a drawing mode.** Stephen's Q1 answer removed a whole class of reshaping problems: the surface never changes size.
- **Panel-centric drawing belongs in the viewer's frame.** Cable positions already name the hardware, so P numbering by buffer slot was a third, redundant naming (Q6).
- **Flicker follows colour, not location.** Under back-to-back binary-coded modulation, a channel whose light sits in one or two planes blinks at the full-cycle rate. That explained the C1 "hardware" flicker («#67») with a two-minute check, no panel swap.
- **On one adapter the line buffer, not hub RAM, sets every panel type's limit.** The plan had assumed RAM would bind somewhere.
- **The documented refresh figures were wrong by up to 10x.** They treated N planes as shown once each. Measuring on the P2 replaced them.

## Process insights

- **Worked:** a two-phase dispatch for the cube (design → arbiter re-derivation of five edges → implementation). The 132-case self-test passed first time, and so did the 163-case extension.
- **Worked:** "suspect the measurement first" (D2). The P9 count was impossible against the clock-time ceiling. Calibrating the counter against a known pulse train, then asking Stephen about the wire, found the flying-lead artifact in three steps.
- **Worked:** least-observation bench sheets. Buffer-readback probes and equivalence hashes (scroll HEAD vs tree) replaced most "please look" requests, and Stephen's eyes went where only eyes could judge.
- **Worked:** answering an agent's "spot-checked only" claim with a full scripted check plus a negative probe: 65/65 guide quotes verbatim, and an altered line is rejected.
- **Didn't:** closing «#77» on logs alone. A visual deliverable (black text on black cells) shipped broken until Stephen glanced at it.
- **Didn't:** the task card was read in full at 1 of 14 task starts, and a breadcrumb was skipped for one inline task («#81»). The card is not reaching the moment it exists for.
- **Friction:** the `simplify` four-agent fan-out is heavy for comment- or constant-only diffs. It was run as a documented single pass for «#81».

## Quality and efficiency observations

- **Faster than estimated:** 22 h 13 min tracked against 44 h 30 min estimated. Dispatched tasks with complete bodies (verbatim task, rulings, falsification instances) needed almost no rework.
- **Slower than it should have been:** harness bookkeeping. A shell `rm -rf` on a variable path was rightly blocked, `END_SESSION` truncated the last debug line in the log, there is no `timeout` on macOS, and four scrollers is the maximum. Each cost one rerun.
- **Rework caused by review:** «#80»'s flat-path compares broke its own D6 attention line and needed a follow-up dispatch. The attention line caught it at review, not at implementation.

## Downstream impact

- **Enables:**
  - any rectangular, L or cube layout from per-panel sentences, with one start call per adapter;
  - face-centric cube drawing;
  - measured refresh, through a calibrated smart-pin instrument that needs no driver changes;
  - the identify screen as a user's config tool;
  - a wiring guide built from captured output.
- **Destabilizes or leaves for later:**
  - every v3 config must be converted (`Checklist-v3-v4.md`);
  - panel-centric programs that numbered panels by buffer slot must renumber;
  - the cube, the green quarter-scan panels and two cabled adapters are proven only by harness until the panel sweep;
  - 5-bit-and-up shimmer remains until the plane order is interleaved.

## Methodology lessons (candidates; Stephen decides)

From `feedback_skill_evolution_candidates.md` (4 entries) and this retrospective (5 new):

| # | Lesson | Proposed home | Proposed verdict |
|---|---|---|---|
| 1 | «#68» + «#72»: planning premises missed derived quantities (the SCAN_4 chip vs its address lines; arrow mixes on non-square panels). Research should take every grammar rule and every derived quantity and ask *what input breaks it* | `sprint-plan` research step ("adversarial premise check") | Deferred → propose central edit |
| 2 | «#75»: a transform setting can be named in two frames. Research should ask *in which frame is this named, and is there a second one someone will reach for?* The agreed-scope-changes log should be a standard plan section | `sprint-plan` research + plan template (D4 already carries the in-the-moment rule) | Deferred → propose central edit |
| 3 | «#77»: a task whose deliverable is an image closed on logs alone. Closing needs one observation of the rendered output (a person, or a buffer readback) | `task-execution` §1b + `plan-to-tasks` §2 verify lines | Deferred → propose central edit |
| 4 | Task card read at 1/14 starts; breadcrumb skipped once. The trigger is prose, so it should move up a tier toward structure (e.g. `todo_start` itself echoes the card's start steps) | `task-execution` / tracking (authoring rule 7: prose → point of action → structure) | Deferred → propose central edit |
| 5 | An agent claiming "spot-checked" quoted output is a partial claim. The arbiter's check is a script over every quote, plus a negative probe that proves the checker can fail | `task-execution` §1b (verify the return) | Deferred → propose central edit |
| 6 | pnut-term-ts: a `debug()` line followed at once by `END_SESSION` may be truncated in the log. Add `waitms` before the marker. macOS has no `timeout`; use `--timeout` | `p2-dev-cycle` (tool facts) | Deferred → propose central edit |
| 7 | Bench instruments: calibrate against a known signal before trusting a count. Physical leads on the pins can ring. This *confirmed* bench rule 5 (instrument, wire, code) on a real catch | none: the rule already exists and worked | Closed-no-change (evidence for rule 5, recorded here) |
| 8 | `simplify`'s four-agent fan-out on trivial diffs | `simplify` is a built-in skill, not a central one | Closed-no-change (outside the skill set; the single-pass variant was used and disclosed) |
| 9 | Central has no human-reader documentation guide, so `DOCs/*.md` has no `CONFORMANCE_GUIDES` row | a central guide (new) | Proposal (build-sized) |

**Attention lines flagged and still broken:** «#80»'s D6 line ("the refresh-structure must not add per-pixel work on the flat path"). It was caught at the review step, not by the implementer. That is evidence for lesson 4's tier move. **Plan revisions by cause:** 1, frames / research incomplete (SC-1), which routes to lesson 2. **Attention metric:** about 0.1 card reads per task started, far under 2. The trigger is the finding (lesson 4).

## Punch-list triage

- **This sprint added 9 items.** 10 are open now: 9 active plus the `[~]` overrun. 1 was archived at closeout. The oldest is ICN2038S, found 2026-10-01 (1 day old).
- **The list is still an active-work register.** Every item names a file, a cause and a validation.
- **What this sprint made cheaper:**
  - **Interleave the bit-plane repeats:** a calibrated refresh counter (`P_COUNT_RISES`, no driver change) and a judged flicker baseline now exist, so a before/after is a 10-minute measurement.
  - **Converter per-plane hoists:** the «#76» buffer-level harness (9/10/16 half-scan, 1-3 quarter-scan) validates any converter change on the P2 with no panels.
  - **Panel-centric clip, cube fold depth, hidden home state:** the «#86» panel-frame probe, the scroll-equivalence hash and the 163-case self-test catch any behaviour change from an optimisation.
  - **ICN2037 20/30 MHz and the panel-clock item:** cheaper only once a PDF reader is installed (`brew install poppler`); then it is a five-minute read.
