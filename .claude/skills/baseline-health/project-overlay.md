# p2-HUB75-LED-Matrix-Driver overlay — baseline-health

## Augments §2 — Run the full test suite

This project has no xUnit-style test suite. Its real regression check is
**golden-binary**: confirming that edits and reformatting do not change
the compiler's emitted code.

On the **macOS side**, `driver/scripts/check_reformat.sh` recompiles every
modified `.spin2` file and md5-compares each resulting `.bin` against its
committed `.bin.GOLD` baseline. A md5 mismatch is a **failure** — it means
a change altered emitted code, which during a pure-reformatting pass is a
defect, not an expected diff.

In the **Linux dev container** this check cannot run (the script uses
macOS `md5`, absent here), so `TEST_COMMAND` is compile-only — "every demo
compiles." Treat the GOLD comparison as a macOS-side health step that is
not exercised in the container, and name it explicitly as not-exercised
when handing back container results (per §3 / §7 — green never silently
means less than it says).

This check is especially load-bearing during the in-progress
style-audit reformatting pass (see `Docs/procedures/STYLE-AUDIT-STATUS.md`):
there, any GOLD drift signals an unintended code change introduced by the
reformat.
