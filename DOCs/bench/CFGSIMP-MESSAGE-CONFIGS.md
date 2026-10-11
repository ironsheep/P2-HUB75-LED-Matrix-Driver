# CONFIG-SIMPLIFICATION — startup-message configs (bench run B-7)

Each row is one edit to a **scratch copy** of `driver/isp_hub75_hwPanelConfig.spin2` (the shipped quad
config: DISP0, ICN2037, 128x64, four panels). Build `demo_hub75_text.spin2` with `-d` against the
edited copy, run it on the LED rig (PropPlug Parw7ukt), and record the startup lines. Each must print
its message (catalogue in `DOCs/plans/CONFIG-SIMPLIFICATION-SPRINT-PLAN.md` §4, M1-M18) and then
`HUB75: DISP0: E problem(s) above; startup stopped`. Restore the shipped file afterwards.

Only one row per build. "List" means the four `LONG` lines of `disp0Panels`.

| Msg | Edit | Expected count line |
|---|---|---|
| M1 | add a line `BYTE 0` after the last `LONG` of the list | 1 problem |
| M2 | delete all four `LONG` lines of the list (keep both labels) | 1 problem |
| M3 | add `#DEFINE DISP0_ROTATED` and `CON DISP0_ROTATION = hwEnum.ROT_90` | 1 problem |
| M4 | `DISP0_PANEL_ROWS = 48` | 1 problem |
| M5 | `DISP0_PANEL_COLUMNS = 126` | 1 problem |
| M6 | add four more sentences: `ROW_2 \| COL_0`, `ROW_2 \| COL_1`, `ROW_3 \| COL_0`, `ROW_3 \| COL_1` (each `\| hwEnum.TOP_DOWN`): 8 x 128 = 1024 columns | 1 problem |
| M7 | list entry 1 becomes `hwEnum.ROW_1 \| hwEnum.COL_1 \| hwEnum.TOP_DOWN \| hwEnum.TOP_TO_RIGHT` | 1 problem |
| M8 | list entry 1 becomes `hwEnum.COL_1 \| hwEnum.TOP_DOWN` | 1 problem |
| M9 | list entry 1 becomes `hwEnum.ROW_1 \| hwEnum.TOP_DOWN` | 1 problem |
| M10 | list entry 1 becomes `hwEnum.ROW_1 \| hwEnum.COL_1 \| hwEnum.TOP_DOWN \| hwEnum.TOP_UP` | 1 problem |
| M11 | list entry 3 becomes `hwEnum.ROW_1 \| hwEnum.COL_1 \| hwEnum.TOP_DOWN` (same cell as C1) | 1 problem |
| M12 | list entry 3 becomes `hwEnum.ROW_2 \| hwEnum.COL_2 \| hwEnum.TOP_DOWN` (corner contact only) | 1 problem |
| M13 | list entry 1: `TOP_DOWN` -> `TOP_LEFT` (128x64 panels are not square) | 1 problem |
| M14 | list entry 0 adds `\| hwEnum.CUBE_TOP` only | 1 problem |
| M15, M16 | entry 0 adds `\| hwEnum.CUBE_TOP`, entry 1 adds `\| hwEnum.CUBE_FRONT` (4 panels, not 6; 128x64 is not square) | 2 problems |
| M17, M18 | need six square panels: produce with `test_hub75_cube_fold` (it drives `foldNet` directly) or a scratch build of a 64x64 six-panel list; label any result not from the rig as such | - |
| N1 | (cube only) add `#DEFINE DISP0_ROTATED` / `CON DISP0_ROTATION = hwEnum.TOP_TO_LEFT` to a cube config | notice, startup continues |

Compile-time rows (the config header's table; measured in «#131» with pnut-ts 1.55.8, no rig needed):

| Case | Message |
|---|---|
| `CON DISP0_ROTATION = ...` written, `#DEFINE DISP0_ROTATED` missing | `Symbol is already defined (m541)` at the default's line in the Defaults section |
| `#DEFINE DISP0_ROTATED` written, setting missing | `Expected an object constant, structure, or method`, reported in the consuming object |
| `#DEFINE DISP1_PRESENT` without a DISP1 block | `Undefined symbol` at the storage line |
