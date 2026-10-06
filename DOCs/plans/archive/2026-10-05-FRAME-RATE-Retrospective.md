# FRAME-RATE — Retrospective

**Sprint:** FRAME-RATE, 2026-10-03 to 2026-10-05. **Closeout:**
[`2026-10-05-FRAME-RATE-Sprint-Closeout.md`](2026-10-05-FRAME-RATE-Sprint-Closeout.md).
**Build:** 4.0.0, untagged (release shaping is next).

## Discovered perspectives

- **A predicted speed from an instruction count misses the hub.** §7's "about 5 ms" counted
  instructions and ignored that every plane write of a column lands in one hub slice; the
  real cost was 16 clocks per plane, not 8. Timing a stripped scratch harness on the P2
  found it in minutes and then chose among four candidates by measurement (SC-1).
- **An instrument and the code's own model disagreed for two visits, and nobody settled it.**
  The monitor read CLK high as 23.9 ns while the driver's startup line said `high 7 low 8`;
  the docs took the monitor's number and swapped the halves. A different panel's lighter
  load (21.7 ns) exposed it.
- **A stretched pulse hides inside a mean.** The overlapped-latch path held one clock pulse
  high through the dark wait; harmless to the chip, but the mean high time (1,407 ns) made
  the 20 ns check unmeasurable on three chips until «#105» removed the pattern.
- **Deleting a mechanism closes its defects.** The line-buffer odd-half-row item, open since
  DISPLAY-ORGANIZATION, needed no panel run: «#92» removed sub-page loading.
- **A construction fact outranks a status cell** (ICN2038S single-ended); recorded as a
  project principle under D3 in `.claude/doctrine-overlay.md`.

## Process insights

- **Worked:** the pin-level take check replaced an unobservable by-eye tearing limb, and its
  negative limb was shown failing; every later visit relied on it.
- **Worked:** scratch harnesses outside the tree (converter timing, candidate comparison) let
  hardware questions be answered without touching committed code.
- **Worked:** a closeout docs sweep by a read-only agent, then fixes by a second agent, then
  the arbiter reading the diff. The read caught one wrong line the arbiter had written
  earlier (MBI5124GP init).
- **Did not work:** the task card was read at 2 of 4 task starts and 0 of 4 closes today;
  the closes were worked from memory. See methodology lessons.
- **Did not work:** a harness that printed its last result just before `END_SESSION` lost
  that line to pnut-term-ts; the same truncation had silently cut every converter-test
  verdict line since «#98». Counts arrive whole; verdict lines do not.

## Quality and efficiency observations

- Tracked 13.8 h against 82 h estimated (observational only).
- Bench time was the pacing resource: visit D waited a day for the bench supply, and the
  desk work in that gap (SC-1) became a release-quality improvement.
- 36 reader-doc items were stale at closeout despite «#102»'s rewrite; most came from tasks
  that changed behaviour after the §12 blast-radius survey was written.

## Downstream impact

- **Enables:** a 60 Hz+ display at full 8-bit colour on every bench panel; video-rate
  commits (4 ms) for animation; `showFrameSet()` and the hub-RAM model for the slideshow
  sprint; the instrument harness to measure any later performance work from the pins.
- **Destabilizes or leaves open:** `showFrameSet()`'s accepted path has never run; one rig
  run stalled with no cause found; panel widths must now be multiples of 4; the README's
  multi-panel claims rest on Stephen's word for the DP5125D.

## Methodology lessons (candidates; consumer lifecycle)

New this sprint (to append to `feedback_skill_evolution_candidates.md`):

1. **Task card not reaching its moments** (attention metric well under twice per task). The
   card is read by instruction, not forced by structure; resumes and closes were the misses.
   Candidate: move the card read up a tier, e.g. make `todo_start`/`todo_resume` and the
   close commit the triggers in `task-execution`, not prose (authoring rule 7).
2. **Blast radius computed once.** A plan's documentation survey goes stale as later tasks
   change behaviour. Candidate: `task-handoff` close adds "grep reader docs for every claim
   this task changed" as a free per-task check.
3. **A new public call needs its success path in the verify.** §3 verified `showFrameSet`'s
   NULL refusal and the commit path, never a caller-built set. Candidate: `sprint-plan`
   research — every new public method names a caller and a success-path check.
4. **Instrument vs model disagreement left standing.** Candidate (instance of D2, not a new
   rule): when a reading and the driver's own startup figure disagree, settle it before the
   number goes into a doc.
5. **Verdict lines lost to end-marker truncation.** Candidate (project overlay for test
   tops): print the verdict before the last count line, or read verdicts from counts only;
   tool fix is Stephen's.

Buffered entries, verdicts (proposed, accepted by Stephen 2026-10-05: "sounds ok"):

| Entry | Proposed verdict | Why |
|---|---|---|
| 2026-10-02 human-reader doc guide (owner Stephen) | Deferred | Still waiting on Stephen's voicing guide; release shaping is a natural moment |
| 2026-10-03 «#89» instrument semantics | Addressed | The rule (trace the observed event and idle level before relying on a channel) belongs in `sprint-plan` research; fold with lesson 4 |
| 2026-10-03 «#89» depth is compile-time | Closed-no-change (deleted) | One-off fact, now in the test's header and memory; no general rule |
| 2026-10-03 «#93» measurement premise across a core change | Addressed | Same fix as «#89» semantics: record the property a method depends on |
| 2026-10-04 «#94» unobservable by-eye acceptance | Addressed | Becomes a `sprint-plan` research check: every by-eye limb names what failure looks like and whether the observer can tell |
| 2026-10-04 «#97»/«#98»/«#99» protocol pinch | Addressed | `task-execution` §7 names the case: a paused task's verified, self-contained sub-unit may be committed as a protection point |

"Addressed" here means a central edit to propose through the generality gate; the entry is
deleted only once that edit is made or staged.

## Punch-list triage

- **Added this sprint:** 2 (`showFrameSet()` run only with NULL; brightness floor). **Open:**
  6. **Oldest:** the ICN2038S scan dispute, 2026-10-01 (4 days).
- **Made cheaper by this sprint:**
  - *Panel-centric diagonal clip* and *cube fold calls*: the instrument's stopwatches now
    time any drawing call on the P2, so each costs one scratch run to measure (the cube item
    still needs the cube).
  - *Brightness floor*: the per-plane-floor option is written down and the instrument
    measures lit share directly, so a trial is one PASM change plus one run.
  - *showFrameSet*: the test exists as a patch; what remains is one clean run and the stall
    diagnosis.
- Nothing on the list looks unwanted; none is losing to planning yet.
