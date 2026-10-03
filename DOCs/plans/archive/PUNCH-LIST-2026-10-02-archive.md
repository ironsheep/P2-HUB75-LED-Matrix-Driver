# Punch list archive, 2026-10-02

Items confirmed done, swept from `DOCs/plans/PUNCH-LIST.md` at the DISPLAY-ORGANIZATION closeout.

### Refresh-rate figures in the docs contradict the code (doc drift)

- **Found:** 2026-10-02, same survey.
- **What:** the refresh core shows bit-plane k of an N-bit frame set 2^(N-1-k) times, 2^N - 1 scans per colour cycle (`driver/isp_hub75_rgb3bit.spin2`, about :841-866). `THEOPS.md` (about :188) says "16 sub-frames ... roughly 60 fps", and `DOCs/FutureDirections-ImageAndColor.md` (about :132-169) gives 153-407 Hz, computed as N frames shown once. Calculated from the code for the rig (clock time only): 4-bit about 85 Hz, 5-bit about 41 Hz, 6-bit 20, 7-bit 10, 8-bit 5.
- **Bears on:** «#85» (bring docs up to 4.0.0) should correct both, and use Visit B's «#83» measured numbers where they exist.
- **Done:** 2026-10-02 in «#85» (`c7643a4`): `THEOPS.md` and `DOCs/FutureDirections-ImageAndColor.md` now give the rig's measured full-cycle rates and link to the wiring guide's limits; `python3 tools/check_docs.py` 0/0/0.
