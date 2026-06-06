# Project skill conventions

Slot values for the central skill set. See
`~/.claude/skills-docs/SKILLS-MAINT.md` for the full schema. Optional
slots that match their documented default are omitted.

---

## Identity

```yaml
USER_NAME:           Stephen
PROJECT_NAME:        p2-HUB75-LED-Matrix-Driver
```

## Build & test

```yaml
# This repo root is shared between a compile-only Linux dev container
# (only `pnut-ts` on PATH) and a macOS folder with the full toolchain.
# These commands are written to run in the container: they compile every
# demo top file. There is no xUnit-style suite; "it all compiles" is the
# check. The driver/scripts/*.sh helpers are macOS-only (they call
# `pnut_ts` and `md5`) and are intentionally NOT used here.
BUILD_COMMAND:           cd driver && for f in demo_hub75_*.spin2; do echo "== $f =="; pnut-ts -d -l -m "$f" || exit 1; done
TEST_COMMAND:            cd driver && for f in demo_hub75_*.spin2; do echo "== $f =="; pnut-ts -d -l -m "$f" || exit 1; done
CANONICAL_TEST_TARGET:   Linux dev container, pnut-ts compile of all demos (no hardware)
```

## Build version

```yaml
BUILD_VERSION_LOCATION:  ChangeLog.md
BUILD_VERSION_KEY:        latest "## [x.y.z]" version heading
BUILD_VERSION_EXAMPLE:    3.0.1
```

## Doc paths

```yaml
# Existing docs the project already maintains:
RELEASE_NOTES_DOC:  ChangeLog.md                 # Keep-a-Changelog format, SemVer
SPEC_DOC:           THEOPS.md                     # theory of operations (closest to a spec)

# Proposed homes for sprint artifacts (created on first use; the project
# keeps reference docs under DOCs/ today, no plans/ tree yet):
PLAN_DIR:           DOCs/plans/
PLAN_ARCHIVE_DIR:   DOCs/plans/archive/
ANALYSIS_DIR:       DOCs/analysis/
PUNCH_LIST_DOC:     DOCs/plans/PUNCH-LIST.md
```

## P2 development cycle

```yaml
# Declarative path: the skill constructs raw pnut-ts / pnut-term-ts
# invocations from these slots. The driver/scripts wrappers are macOS-only
# and not pointed at here, so compile works in the container; flash/run
# only works on the macOS side.
P2_WORK_DIR:            driver

# Canonical default top file: demo_hub75_color.spin2 has the widest object
# include set (8 objects, the only demo pulling in the BMP handler plus
# colorUtils + screenUtils). Override per invocation for the other 7 demos.
SPIN2_TOP_FILE:         demo_hub75_color.spin2
```
