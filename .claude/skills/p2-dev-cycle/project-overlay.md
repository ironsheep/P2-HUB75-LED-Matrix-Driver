# p2-HUB75-LED-Matrix-Driver overlay — p2-dev-cycle

## Augments §3 — Flash to RAM and run

This repo root is shared between two environments:

- **Linux dev container** (where Claude Code runs) — only `pnut-ts` is on
  PATH. `pnut-term-ts`, `flexspin`, `loadp2`, and any connected P2 are
  **absent**. There is no hardware here.
- **macOS folder** (same files) — full toolchain: `pnut-ts` +
  `pnut-term-ts` (DEBUG terminal) plus `flexspin` / `loadp2`, and the P2
  hardware.

Consequence: when this skill is invoked **in the container**, §3 (flash)
through §5 (diagnose runtime behavior) cannot run — there is nothing to
flash to. End the cycle after §1 Compile / §2 Pre-flash sanity, report
the compile result, and stop. Do not attempt to flash, and do not treat
the absence of `pnut-term-ts` as an error to fix. Flash-and-run and any
runtime diagnosis happen on the macOS side.

## Augments §1 — Compile

The container compiler binary is `pnut-ts` (hyphen) — invoke it directly.
The `driver/scripts/*.sh` wrappers (`compile_all.sh`, `check_reformat.sh`)
call `pnut_ts` (underscore) and `md5`, neither of which exists in the
container; they are macOS-only — do not invoke them here.

This project has 8 demo top files (`driver/demo_hub75_*.spin2`), not one.
`SPIN2_TOP_FILE` defaults to `demo_hub75_color.spin2` (the widest object
include set — the only demo pulling in the BMP handler plus colorUtils
and screenUtils). Override it per invocation to match the feature under
test.
