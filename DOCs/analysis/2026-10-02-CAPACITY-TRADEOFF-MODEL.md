# Capacity Trade-off Model: Adapters, Panels, Depth, Refresh and PSRAM

**Status:** planning input. It goes with `2026-10-02-FRAME-RATE-STUDY.md`. After the
sprint that implements the study, the model moves into the Wiring Guide's
*Driver limits* section and replaces the tables there.
**Date:** 2026-10-02. **Build:** 4.0.0 in development.

## 1. The question

How big can one display be, and how many displays can one P2 drive, at what colour
depth and refresh rate? What changes with:
- more HUB75 adapters;
- the PSRAM on the P2-EC32MB;
- the study's refresh and buffering changes?

## 2. The four limits

A configuration must pass all four. The tightest one decides.

| # | Limit | What sets it | Where it binds |
|---|---|---|---|
| L1 | **Refresh line buffer (cog RAM)** | The refresh core holds one row of the whole chain, 512 column clocks. So one adapter's chain is at most 512 columns: 4 panels 128 wide, or 8 panels 64 wide (half that for quarter-scan chips). | **Per adapter, and so per display**, because a display is one adapter today. |
| L2 | **Hub RAM** | All three adapters' buffers are compiled into one program and share what is left of 512 KB. That is **451,564 bytes** with DEBUG on (measured, Wiring Guide). | **Across adapters.** |
| L3 | **Refresh rate** | Refresh falls as columns per chain and row addresses grow, and as colour depth rises. The goal is 60 Hz or more. | Per adapter. |
| L4 | **Pins and cogs** | Each adapter takes a 16-pin group and one refresh cog. PSRAM takes P40-P57, which removes the groups at base 32 and 48. | Board-wide. |

## 3. Memory per adapter

P is the number of pixels on the adapter and N is the colour depth.

| Buffer | Size | Today | Notes |
|---|---|---|---|
| Screen buffer (RGB content) | 3·P | hub | What drawing writes. |
| Frame set ×2 (bit-planes) | 2 × N·P/2 = N·P | hub | What the refresh cog reads. The second set exists today but isn't used (study F9). |
| **Total today** | **P·(3 + N)** | hub | Matches the Wiring Guide. |

## 4. Does PSRAM let a display hold more panels?

**Not today.** One display is one adapter, and one adapter's panel count is set by L1,
the 512-column line buffer in cog RAM. PSRAM doesn't touch cog RAM. On a single
adapter, L1 is already tighter than hub RAM in every case (Wiring Guide).

**What PSRAM does change is L2,** the RAM shared across adapters. Moving the screen
buffers (3·P each) into PSRAM leaves only the frame sets (N·P) in hub. The frame sets
must stay in hub, because the refresh cog needs them at a steady rate.

Total pixels across all adapters that hub RAM allows (calculated from 451,564 bytes):

| Depth | Today, P·(3+N) in hub | Screen buffers in PSRAM, N·P in hub | Gain |
|---|---|---|---|
| 3-bit | 75,260 px (9 × 128×64) | 150,521 px (18 × 128×64) | 2.0× |
| 4-bit | 64,509 px (7 × 128×64) | 112,891 px (13 × 128×64) | 1.75× |
| 5-bit | 56,445 px (6 × 128×64) | 90,312 px (11 × 128×64) | 1.6× |
| 6-bit | 50,173 px (6 × 128×64) | 75,260 px (9 × 128×64) | 1.5× |
| 8-bit | 41,051 px (5 × 128×64) | 56,445 px (6 × 128×64) | 1.4× |

The gain is largest at low depth, because at high depth the frame sets take most of
the memory.

**PSRAM has three costs:**
- One cog.
- The adapters at base 32 and 48. With PSRAM, at most two adapters (base 0 and 16) can run.
- Drawing into a screen buffer held in PSRAM is much slower (study F22). It needs a
  hub row-band cache: draw a band of rows in hub, then write the band out as one
  block. A display of moderate size drawn often should keep its screen buffer in hub.

**So PSRAM is the answer for:**
- two adapters at higher depth than hub alone allows;
- **double-buffered RGB content** (two screen buffers) for large displays;
- slideshow staging and pre-built animation, which is its best use.

## 5. Double buffering: which buffer, and when it pays

| What is doubled | Cost | What it buys | When it's worth it |
|---|---|---|---|
| **Frame sets** (study F9) | N·P, already allocated | A tear-free switch with no gap between frames. The panels never show a half-converted frame. | **Always.** The memory is already spent. |
| **Screen buffer (RGB)** | +3·P | Drawing frame N+1 while frame N converts. That only helps when conversion runs in its own cog (study F11). | Only with a converter cog. With the faster converter (study F10, about 5 ms on the rig), drawing then committing in sequence is usually enough. In hub it costs 98 KB on the rig, so for anything large it belongs in PSRAM. |

## 6. Refresh: how long a chain can be at 60 Hz

**Today's method** (each plane re-shifted 2^k times, 16 clocks per column, 335 MHz).
The longest chain that still refreshes at 60 Hz:

| Row addresses | 4-bit | 5-bit | 6-bit | 7-bit | 8-bit |
|---|---|---|---|---|---|
| 16 (1/16 scan) | 1,453 | 703 | 346 | 171 | 85 |
| 32 (1/32 scan) | 726 | 351 | 173 | 85 | 42 |

**With the study's OE-weighted method** (F2), with at least 80% brightness; the
second figure is with F3's 14-clock shift:

| Row addresses | 4-bit | 5-bit | 6-bit | 7-bit | 8-bit |
|---|---|---|---|---|---|
| 16 (1/16 scan) | 2,726 / 3,115 | 2,423 / 2,769 | 1,282 / 1,466 | 1,211 / 1,384 | 1,147 / 1,311 |
| 32 (1/32 scan) | 1,363 / 1,557 | 1,211 / 1,384 | 641 / 733 | 605 / 692 | 573 / 655 |

**Reading the two tables together:**
- **Today, refresh (L3) binds before the line buffer (L1)** at 5-bit and above. The
  rig's 512 columns at 1/32 scan can't reach 60 Hz above 4-bit.
- **With F2, the 512-column line buffer becomes the binding limit** in almost every
  cell. Only 1/32 scan at 7-bit and 8-bit stays close to it.
- **Lifting the line buffer is then the next lever for bigger single displays.** The
  study's F5 (the streamer reading the frame set from hub through the FIFO) removes
  the cog-RAM row limit. Chains can then grow to the 16 cable positions, and to the
  F2 table's column counts at the chosen depth.

## 7. One adapter or several

| | One adapter, long chain | Several adapters, shorter chains |
|---|---|---|
| Display size | One large display, up to L1 (512 columns today; more with F5) | One display per adapter, each smaller |
| Refresh | Falls as the chain gets longer | Each adapter refreshes its own shorter chain, so faster |
| Hub RAM | One display's P·(3+N) | **Shared**: Σ P·(3+N) across adapters must fit (L2). More adapters means less RAM each. |
| Cogs | 1 refresh cog | 1 refresh cog per adapter |
| PSRAM | Fits alongside, with no pin conflict | At most 2 adapters if PSRAM is fitted |
| Content | One image across all panels | Independent content per display. One image spanning adapters isn't supported today (study F7). |

**Worked examples** (128×64 panels, hub only, calculated):

| Configuration | Hub buffers | Fits? |
|---|---|---|
| 1 adapter × 4 panels, 8-bit | 4 × 8,192 × 11 = 360,448 | yes |
| 2 adapters × 4 panels, 8-bit | 720,896 | no |
| 2 adapters × 4 panels, 4-bit | 458,752 | no, about 7 KB over |
| 2 adapters × 4 panels, 3-bit | 393,216 | yes |
| 2 adapters × 4 panels, 6-bit, screen buffers in PSRAM | 8 × 8,192 × 6 = 393,216 | yes |
| 2 adapters × 4 panels, 8-bit, screen buffers in PSRAM | 524,288 | no |

## 8. Open points for the plan

- **A display spanning adapters** (F7) is the only way past L1 that also raises
  refresh. It's a new feature, so a scope call.
- **Frame sets in PSRAM, fed to the refresh cog row by row,** would remove hub as a
  limit for large displays. The bandwidth is enough: about 24 MB/s per adapter
  against about 335 MB/s. But it adds mailbox latency into the refresh timing and
  has never been tried here. Unproven; recorded, not recommended.
- **The 451,564-byte figure is a DEBUG build.** A release build has 468,636 bytes,
  about 4% more. Every table here uses the DEBUG figure, so the tables are
  conservative.
