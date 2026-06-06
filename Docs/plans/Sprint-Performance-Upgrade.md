# Sprint: HUB75 Driver Performance Upgrade

## Executive Summary: What Actually Improves Refresh Rate

**Bottom Line:** The display refresh rate is fundamentally limited by BCM (Binary Coded Modulation) timing. Most hardware features provide marginal gains. The table below shows actual impact on refresh rate.

### Refresh Rate Impact Summary

| Optimization | Complexity | Additional COGs | Refresh Rate Improvement |
|--------------|------------|-----------------|--------------------------|
| **Reduce to 5-bit color** | Low | 0 | **+720%** (4.9→40 Hz) |
| **Reduce to 6-bit color** | Low | 0 | **+300%** (4.9→20 Hz) |
| Remove WAITX delays | Low | 0 | **+35%** (if panel tolerates) |
| **OE/LAT/Addr timing** | Low | 0 | **+4-8%** (experimental) |
| RFBYTE FIFO inner loop | Low | 0 | **+14%** |
| LUT double-buffer | Medium | +1 | **+1.6%** |
| HyperRAM pre-computed | Medium | +1 | **0%** (same BCM timing) |
| Smart PIN CLK | Medium | 0 | **~5%** (frees CPU cycles) |
| Streamer output | High | 0 | **~10-20%** (if feasible) |

### Achievable Refresh Rates by Configuration

| Color Depth | Current | +RFBYTE | +No WAITX | +All Optimizations |
|-------------|---------|---------|-----------|-------------------|
| **8-bit** | 4.9 Hz | 5.6 Hz | 6.6 Hz | **7.9 Hz** |
| **7-bit** | 9.8 Hz | 11.2 Hz | 13.3 Hz | **15.9 Hz** |
| **6-bit** | 19.8 Hz | 22.5 Hz | 26.7 Hz | **32.0 Hz** |
| **5-bit** | 40.2 Hz | 45.7 Hz | 54.3 Hz | **65.1 Hz** ✓ |
| **4-bit** | 83.3 Hz | 94.3 Hz | 112 Hz | **135 Hz** ✓ |

✓ = Meets 60 Hz flicker-free threshold

### Key Conclusions

1. **Color depth reduction is the only way to achieve 60+ Hz**
   - 8-bit cannot reach 60 Hz even with all optimizations (max ~8 Hz)
   - 5-bit with optimizations reaches 65 Hz (usable)
   - 4-bit with optimizations reaches 135 Hz (excellent)

2. **Hardware features help marginally with refresh rate**
   - LUT double-buffer: +1.6% (but adds determinism and enables other optimizations)
   - HyperRAM: 0% refresh improvement (but enables pre-computed animation)
   - These are valuable for other reasons, not raw refresh rate

3. **Best ROI optimizations for refresh rate**
   - First: Reduce color depth to 5-bit or 6-bit
   - Second: Test removing WAITX delays (+35% if panel tolerates)
   - Third: Optimize OE/LAT/Address timing (potential +5-15%)
   - Fourth: RFBYTE FIFO inner loop (+14%)

4. **Temporal dithering can recover perceived color quality**
   - Display 5-bit color but alternate patterns to simulate higher depth
   - Human eye averages the result, perceiving more colors

---

## Multi-COG Architecture Strategy

With 8 COGs available, dedicating 2-3 to the display driver enables significant architectural improvements. Here's the analysis of COG allocation strategies:

### Current Architecture (1 COG)

```
┌─────────────────────────────────────────────────────────────┐
│                      COG 0 (Display Driver)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PWM Convert │→ │ Load Subpage│→ │ Output Pins │ → Panels│
│  │   24.7ms    │  │  sequential │  │   BCM loop  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  Problems:                                                  │
│  • Display pauses during PWM conversion                     │
│  • Sequential subpage loads add overhead                    │
│  • Single COG does everything = bottleneck                  │
└─────────────────────────────────────────────────────────────┘
```

### Recommended: 3-COG Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         3-COG Display Pipeline                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COG 0: PWM Frame Generator                                             │
│  ┌──────────────────────────────────────┐                              │
│  │ Screen Buffer → PWM Frames           │                              │
│  │ • Runs continuously in background    │                              │
│  │ • Writes to HUB RAM double-buffer    │                              │
│  │ • 24.7ms conversion runs PARALLEL    │                              │
│  │   with display output                │                              │
│  └──────────────────────────────────────┘                              │
│                    ↓ HUB RAM (PWM double-buffer)                       │
│                                                                         │
│  COG 1: LUT Loader (even COG for LUT sharing)                          │
│  ┌──────────────────────────────────────┐                              │
│  │ HUB RAM → LUT (ping-pong buffers)    │                              │
│  │ • SETQ2 + RDLONG bulk transfers      │                              │
│  │ • Writes to own LUT                  │──┐                           │
│  │ • Auto-mirrors to COG 2 via SETLUTS  │  │ LUT Sharing               │
│  │ • Always stays ahead of display      │  │ (automatic)               │
│  └──────────────────────────────────────┘  │                           │
│                                             ↓                           │
│  COG 2: Display Driver (odd COG for LUT sharing)                       │
│  ┌──────────────────────────────────────┐                              │
│  │ LUT → HUB75 Pins                     │                              │
│  │ • SETLUTS #1 receives COG 1 writes   │                              │
│  │ • RDLUT for 3-cycle deterministic    │                              │
│  │ • Pure display loop - NO waiting     │                              │
│  │ • BCM timing is sole constraint      │ → HUB75 Panels               │
│  └──────────────────────────────────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### COG Allocation Benefits

| Benefit | 1-COG (Current) | 3-COG Pipeline |
|---------|-----------------|----------------|
| PWM conversion | Blocks display (24.7ms stutter) | Parallel (no stutter) |
| Subpage transfer | In display loop (+1.6% overhead) | Background (0% overhead) |
| Display timing | Variable (HUB contention) | Deterministic (LUT only) |
| Screen update rate | Limited by conversion | Can update every frame |
| Animation smoothness | Stutters on update | Smooth continuous |

### What Multi-COG Does NOT Improve

**Raw refresh rate is unchanged** - BCM timing still dominates:
- 3-COG at 8-bit: Still ~5 Hz (same BCM math)
- 3-COG at 5-bit: Still ~40 Hz base rate

**But it improves:**
- Eliminates conversion stutter (smooth animation)
- Reduces jitter (deterministic LUT access)
- Enables higher screen UPDATE rate (not refresh rate)
- Foundation for future optimizations

### Alternative: 2-COG Simplified Architecture

If COG budget is tight, a 2-COG version:

```
COG 0: PWM Generator + LUT Loader (combined)
  • Converts screen → PWM when needed
  • Continuously loads LUT for display COG

COG 1: Display Driver
  • SETLUTS #1 for LUT sharing
  • Pure display output loop
```

This still eliminates the transfer overhead during display but doesn't fully parallelize PWM conversion.

### 4-COG Architecture with HyperRAM

For pre-computed animation playback:

```
COG 0: HyperRAM Driver
  • Streams pre-computed PWM frames from 32MB HyperRAM
  • 80 MB/s bandwidth = 1.6ms per 128KB frame

COG 1: PWM Generator (for real-time content)
  • Only used when displaying dynamic content
  • Can be idle during animation playback

COG 2: LUT Loader
  • Ping-pong LUT buffer management
  • Feeds display COG continuously

COG 3: Display Driver
  • Pure BCM output loop
  • Deterministic timing
```

### COG Budget Summary

| Configuration | Display COGs | Available for App | Best For |
|---------------|--------------|-------------------|----------|
| Current | 1 | 7 | Simple applications |
| 2-COG Pipeline | 2 | 6 | Good balance |
| 3-COG Pipeline | 3 | 5 | Smooth animation |
| 4-COG + HyperRAM | 4 | 4 | Pre-rendered content |

**Recommendation:** Start with 3-COG pipeline:
- COG 0: PWM Generator
- COG 1: LUT Loader (even COG)
- COG 2: Display Driver (odd COG, paired with COG 1)

This leaves 5 COGs for application code (USB, serial, user logic, etc.)

### Implementation Priority

1. **Phase 1:** Separate PWM conversion to dedicated COG
   - Eliminates 24.7ms display stutter
   - Immediate improvement in animation smoothness

2. **Phase 2:** Add LUT loader COG with sharing
   - Eliminates transfer overhead
   - Deterministic display timing

3. **Phase 3:** Integrate HyperRAM (optional)
   - For pre-computed animation applications
   - Adds one more COG

---

## Overview

This sprint focuses on improving the refresh rate of the HUB75 LED Matrix Driver to eliminate visible flashing. The current implementation at 8-bit color depth produces refresh rates of approximately 2-5 Hz, far below the 60+ Hz needed for flicker-free viewing.

---

## Current Performance Baseline

### Measured Parameters (from driver logs)

| Parameter | Value |
|-----------|-------|
| System Clock | 335 MHz |
| Cycles/bit (data shifting) | 16 |
| Color Depth | 8-bit |
| Panel Configuration | 2x2 grid (4 panels) |
| Display Resolution | 256x128 pixels |
| Chain Columns | 512 (4 × 128) |
| Scan Rows | 32 (1/32 scan) |
| PWM Frame Size | 16,384 bytes |
| COG Buffer Size | 512 bytes |
| Subpages per Frame | 32 |

### BCM (Binary Coded Modulation) Timing

| Color Depth | BCM Weights | Total Time Units | Estimated Refresh Rate |
|-------------|-------------|------------------|------------------------|
| **8-bit** | 128+64+32+16+8+4+2+1 | **255** | 2-5 Hz |
| **7-bit** | 64+32+16+8+4+2+1 | **127** | 4-10 Hz |
| **6-bit** | 32+16+8+4+2+1 | **63** | 8-20 Hz |
| **5-bit** | 16+8+4+2+1 | **31** | 16-41 Hz |
| **4-bit** | 8+4+2+1 | **15** | 33-85 Hz |
| **3-bit** | 4+2+1 | **7** | 73-182 Hz |

### Current Data Path

```
24-bit Screen Buffer (HUB RAM: 98,304 bytes)
         │
         ▼ [PASM2 inline: convertScreen2PWM - 24,742 µs]
PWM Frame Buffers (HUB RAM: 131,072 bytes for 2 framesets)
         │
         ▼ [SETQ + RDLONG block transfer]
COG Buffer (512 bytes = 128 longs)
         │
         ▼ [REP loop: ALTGB + GETBYTE + SETBYTE + WAITX]
GPIO Pins (16 pins: 6 RGB + 5 ADDR + CLK + LAT + OE + 2 spare)
         │
         ▼
HUB75 Panel Hardware
```

### Critical Inner Loop (Current Implementation)

```pasm
' Inner loop: 7 instructions = 14 base cycles (with WAITX D=0)
' + waitCyclesLow + waitCyclesHigh = cycles for target panel freq
' At 335 MHz → 20 MHz: 16 cycles (waitLo=1, waitHi=1)

rep     @eobytes, colCtrMax         ' REP for entire row
altgb   byteOffset, pCogBffrIncr    ' 2 cycles: setup byte fetch
getbyte colorByte, 0-0, #0-0        ' 2 cycles: get color byte
drvl    pinLedCLK                   ' 2 cycles: CLK low
setbyte OUTA, colorByte, #3         ' 2 cycles: output RGB data
waitx   waitCyclesLow               ' 2+N cycles: data setup time
drvh    pinLedCLK                   ' 2 cycles: CLK high
waitx   waitCyclesHigh              ' 2+M cycles: clock high time
eobytes
```

**Current bottleneck:** 16 cycles per pixel × 512 columns = 8,192 cycles per row

---

## Research Areas

### Area 1: Code Optimization (Existing Data Paths)

**Goal:** Reduce cycle count in critical loops without hardware changes

#### 1.1 Inner Loop Optimization

- [ ] Analyze if `ALTGB + GETBYTE` can be replaced with faster sequence
- [ ] Investigate using `RFBYTE` with FIFO instead of COG buffer access
- [ ] Consider unrolling loop for specific column counts
- [ ] Evaluate removing WAITX if panel can handle faster clock

#### 1.2 PWM Frame Generation Optimization

- [ ] Profile `convertScreen2PWM` (currently 24,742 µs)
- [ ] Investigate parallel processing across multiple COGs
- [ ] Consider pre-computing PWM frames for static content
- [ ] Evaluate incremental updates (only changed pixels)

#### 1.3 Buffer Transfer Optimization

- [ ] Current: `SETQ + RDLONG` for 128-long block transfers
- [ ] Investigate larger subpage sizes to reduce transfer overhead
- [ ] Consider double-buffering strategies
- [ ] Evaluate LUT RAM for faster access patterns

#### 1.4 BCM Weight Optimization

- [ ] Investigate non-binary weighted PWM (e.g., S-PWM, GCLK schemes)
- [ ] Consider interleaved frame display to reduce flicker perception
- [ ] Evaluate dithering at lower bit depths to simulate higher depths

---

### Area 2: P2 Streamer (FIFO/DMA Engine)

**Goal:** Offload data movement to hardware DMA for zero CPU overhead

#### 2.1 Streamer Architecture

The P2 Streamer is an NCO-driven DMA engine with these capabilities:
- Per-COG independent streamer
- 32-bit NCO for precise timing control
- Zero CPU overhead during streaming
- Hub-to-pins modes with 1/2/4/8/16/32-bit widths
- RGB format conversion modes (8/16/24-bit)

#### 2.2 Relevant Streamer Modes

| Mode | Description | Potential Use |
|------|-------------|---------------|
| 4-7 | Hub FIFO → Pins directly | Stream RGB data to output pins |
| 8-10 | Hub with RGB conversion | Auto-convert 24-bit to panel format |
| 11-12 | Pins → Hub | Potential for input capture |

#### 2.3 Research Tasks

- [ ] Investigate Mode 4/5 for direct hub-to-pin streaming
- [ ] Evaluate `XINIT`/`XCONT` for seamless command chaining
- [ ] Determine if 6-bit RGB data can be streamed directly
- [ ] Analyze NCO frequency settings for panel clock generation
- [ ] Consider using streamer for CLK generation while CPU handles data

#### 2.4 Streamer Code Pattern (Reference)

```pasm
' Setup FIFO for reading
rdfast  #0, pwm_buffer_address    ' Initialize FIFO

' Configure streamer frequency
setxfrq ##pixel_freq              ' Set pixel clock rate

' Start streaming to pins
xinit   ##mode_config, #0         ' Begin DMA transfer

' Wait for completion
waitxfi                           ' Zero overhead wait
```

#### 2.5 Pin Group Mapping

Streamer uses 8-pin groups:
- Group 2: Pins 16-23 (includes RGB1, RGB2 data pins)
- Group 3: Pins 24-31 (includes ADDR, CLK, LAT, OE)

**Challenge:** HUB75 pins span two groups; may need coordination

---

### Area 3: Memory Architecture Options

**Goal:** Optimize memory access patterns and utilize available RAM

#### 3.1 Memory Resources Available

| Memory Type | Size | Access Speed | Current Use |
|-------------|------|--------------|-------------|
| COG RAM | 512 longs (2KB) | 1 cycle | Display buffer (128 longs) |
| LUT RAM | 512 longs (2KB) | 1 cycle | Unused |
| HUB RAM | 512 KB | 8+ cycles | Screen + PWM buffers |
| External PSRAM | 32 MB | Variable | Unused |

#### 3.2 LUT RAM Opportunities

- [ ] Use LUT for color lookup tables (gamma correction)
- [ ] Store one complete PWM row in LUT for faster access
- [ ] Consider LUT for address generation patterns
- [ ] Evaluate `SETQ2 + RDLONG` for hub-to-LUT bulk transfer

#### 3.3 COG RAM Optimization

- [ ] Current COG buffer: 128 longs (512 bytes)
- [ ] Remaining COG space: ~380 longs available
- [ ] Consider larger COG buffer to reduce subpage overhead
- [ ] Evaluate storing timing constants in registers vs memory

#### 3.4 External HyperRAM (32 MB) - P2-EC32MB Module

> **Full details:** See [PSRAMExpansion.md](../PSRAMExpansion.md) for comprehensive documentation.

The P2-EC32MB Edge module includes 32MB of **HyperRAM** - fast external volatile RAM using the HyperBus interface.

**HyperRAM Specifications:**
- Capacity: 32 MB (256 Mbit)
- Interface: HyperBus (8-bit, faster than SPI)
- Transfer rate: **1 long every 4 clocks (~80 MB/s at 320MHz)**
- Latency: ~1µs minimum per transaction
- Page size: 1KB (page crossing adds overhead)
- COG requirement: 1 dedicated COG for PSRAM driver

**Performance Analysis for LED Matrix:**

| Metric | Value | Analysis |
|--------|-------|----------|
| Transfer rate | 80 MB/s | Excellent for bulk transfers |
| PWM frameset size | 128 KB | Transfer time: ~1.6 ms |
| Frame rate potential | 625 frames/sec | Far exceeds display refresh needs |
| Latency | ~1 µs | Acceptable for pre-loading, not inner loop |

**Key Applications:**

1. **Pre-rendered Animation Storage**
   - 32 MB ÷ 128 KB = **250 complete animation frames**
   - Transfer time per frame: 1.6 ms (allows 60+ fps animation)
   - Pre-compute complex effects offline, play back smoothly

2. **Massive Display Support**
   - Hub RAM limit: ~65K pixels
   - With HyperRAM: **1M+ pixels** feasible
   - Screen buffer in HyperRAM, PWM working set in Hub

3. **Multi-Page Display System**
   - Store multiple complete "screens"
   - Instant switching between pre-rendered content
   - Digital signage with smooth transitions

4. **Triple/Quad Buffering**
   - Current: Double-buffered in Hub RAM
   - With HyperRAM: Triple+ buffering for tear-free animation

**HyperRAM Impact on Refresh Rate:**

HyperRAM doesn't directly improve refresh rate (that's limited by BCM timing), but enables:

| Feature | Without HyperRAM | With HyperRAM |
|---------|------------------|---------------|
| Animation frames | 2 (double-buffer) | 250+ stored |
| Display size | ~65K pixels | 1M+ pixels |
| Content switching | Re-render required | Instant from storage |
| Pre-computed PWM | Not practical | Store all BCM frames |

**Refresh Rate Optimization Strategy:**

Instead of computing PWM frames in real-time (24,742 µs per conversion), pre-compute and store in HyperRAM:

```
Traditional (real-time):
Screen → [24.7ms conversion] → PWM → Display

HyperRAM (pre-computed):
[Offline: Screen → PWM stored in HyperRAM]
HyperRAM → [1.6ms transfer] → Hub → Display

Savings: 23.1 ms per frame = 93% reduction in processing overhead
```

**Pipeline Architecture (from PSRAMExpansion.md):**

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: HyperRAM → Hub (Streamer A - autonomous)         │
│  ┌─────────┐                      ┌─────────────┐          │
│  │HyperRAM │ ═══streamer═══════►  │ Hub Buffer  │          │
│  │ (32MB)  │     80 MB/s          │ (next chunk)│          │
│  └─────────┘                      └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Stage 2: Hub → Panels (Streamer B - autonomous)           │
│  ┌─────────────┐                  ┌─────────────┐          │
│  │ Hub Buffer  │ ═══streamer═══►  │ HUB75 Pins  │ → Panels │
│  │(curr chunk) │    zero overhead │             │          │
│  └─────────────┘                  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

**Combined with LUT Double-Buffer:**

HyperRAM + LUT sharing provides the complete optimization pipeline:
1. HyperRAM stores pre-computed PWM frames (eliminates 24.7ms conversion)
2. PSRAM COG streams to Hub RAM buffer
3. Loader COG transfers Hub → LUT (eliminates transfer overhead)
4. Display COG reads from LUT (deterministic 3-cycle access)

**Research Tasks:**
- [x] Document HyperRAM specifications (see PSRAMExpansion.md)
- [ ] Profile actual transfer rates with existing driver
- [ ] Implement pre-computed PWM storage strategy
- [ ] Integrate HyperRAM pipeline with display driver

#### 3.5 Block Transfer Optimization

```pasm
' Current: Transfer 128 longs from HUB to COG
setq    #127                      ' 128 longs
rdlong  cogBuffer, ptra++         ' 2 + 128 cycles

' Potential: Transfer to LUT for faster inner loop access
setq2   #127                      ' 128 longs to LUT
rdlong  0, ptra++                 ' LUT address starts at 0
```

---

### Area 4: Smart PIN Features

**Goal:** Leverage hardware PIN capabilities for faster I/O

#### 4.1 Smart PIN Overview

Each P2 pin has dedicated hardware for:
- Synchronous serial TX/RX
- PWM generation
- Frequency synthesis
- Quadrature encoding
- ADC/DAC functions

#### 4.2 Relevant Smart PIN Modes

| Mode | Name | Potential Use |
|------|------|---------------|
| %00001 | Repository | Fast output from COG register |
| %01100 | Sync TX | Hardware shift-out to panel |
| %11100 | Sync Serial TX | Clocked serial output |
| %10100 | Transition PWM | Hardware CLK generation |

#### 4.3 Research Tasks

- [ ] Investigate Sync TX mode for RGB data output
- [ ] Evaluate using Smart PIN for CLK generation (frees CPU)
- [ ] Consider PWM mode for OE control
- [ ] Analyze if LAT can be hardware-triggered

#### 4.4 Smart PIN CLK Generation

```pasm
' Configure CLK pin for hardware PWM
wrpin   ##P_PULSE | P_OE, pinLedCLK   ' Pulse mode
wxpin   ##clock_period, pinLedCLK      ' Set period
wypin   ##pulse_count, pinLedCLK       ' Start N pulses
```

**Advantage:** CPU can prepare next data while CLK runs autonomously

#### 4.5 Sync Serial TX Pattern

```pasm
' Configure pin for synchronous serial transmit
wrpin   ##P_SYNC_TX | P_OE, rgb_pin    ' Sync TX mode
wxpin   ##%0_00101, rgb_pin            ' 6-bit, MSB first
wypin   color_data, rgb_pin            ' Start transmission
```

---

### Area 5: Advanced PIN Driving Techniques

**Goal:** Maximize GPIO throughput for panel interface

#### 5.1 Current PIN Driving Method

```pasm
setbyte OUTA, colorByte, #3    ' Write 6-bit RGB to output register
drvh    pinLedCLK              ' Individual pin control
drvl    pinLedCLK
```

#### 5.2 Group PIN Operations

- [ ] Investigate `OUTL`/`OUTH` for 32-bit wide operations
- [ ] Evaluate `SETQ + MUXQ` for masked group writes
- [ ] Consider `DRVL`/`DRVH` with pin ranges
- [ ] Analyze `FLTL`/`FLTH` for tri-state control

#### 5.3 Parallel Output Pattern

```pasm
' Write RGB data and toggle CLK in single operation
' Requires careful pin mapping
mov     outa_value, rgb_data
or      outa_value, clk_high_mask
mov     OUTA, outa_value          ' RGB + CLK high
andn    outa_value, clk_high_mask
mov     OUTA, outa_value          ' RGB + CLK low
```

#### 5.4 Pin Timing Considerations

- ICN2037 max clock: 20 MHz (50 ns period)
- P2 at 335 MHz: ~3 ns per cycle
- Minimum pulse width: ~15 ns (5 cycles)
- Current implementation: 16 cycles per pixel

#### 5.5 Research Tasks

- [ ] Profile actual panel clock tolerance
- [ ] Test higher clock rates with current panels
- [ ] Investigate minimum setup/hold times
- [ ] Evaluate if slower address changes allow faster data clock

---

### Area 6: OE/LAT/Address Timing Optimization

**Goal:** Reduce control signal overhead by finding minimum timing the panels actually need

#### 6.1 Current Control Signal Timing

The HUB75 protocol requires these control signals per row:

```
Per-Row Overhead (Current):
┌──────────────────────────────────────────────────────────────┐
│  [Data Shift: 512 pixels × 16 cycles = 8,192 cycles]        │
│  [OE disable]     ← Blanking start                          │
│  [Address change] ← Setup new row address (A-E pins)        │
│  [LAT pulse]      ← Latch shifted data to outputs           │
│  [OE enable]      ← Blanking end, LEDs illuminate           │
└──────────────────────────────────────────────────────────────┘

Estimated current overhead: ~70-100 cycles per row
At 32 rows × 255 BCM units: 570,240 - 816,000 cycles per frame
```

#### 6.2 Timing Parameters to Investigate

| Parameter | Datasheet Spec | Current Implementation | Test Range |
|-----------|---------------|------------------------|------------|
| **OE blanking** | ~10-50ns min | Conservative | Reduce to minimum |
| **LAT pulse width** | 10-20ns typical | ~6 cycles (~18ns) | Test 2-4 cycles |
| **Address setup** | 10-20ns before LAT | ~10 cycles | Test 4-6 cycles |
| **Address hold** | 5-10ns after LAT | ~6 cycles | Test 2-4 cycles |
| **LAT to OE delay** | Minimal | ~4 cycles | Test 2 cycles |

#### 6.3 Potential Savings

If overhead can be reduced from ~70 cycles to ~30 cycles per row:

```
Current: 70 cycles × 32 rows × 255 BCM = 571,200 cycles overhead
Optimized: 30 cycles × 32 rows × 255 BCM = 244,800 cycles overhead
Savings: 326,400 cycles per frame = ~1ms at 335 MHz
```

**Impact on refresh rate:**

| Color Depth | Current | With Timing Optimization | Improvement |
|-------------|---------|--------------------------|-------------|
| 8-bit | 4.9 Hz | ~5.1 Hz | +4% |
| 5-bit | 40.2 Hz | ~42 Hz | +4% |

The percentage improvement is modest but compounds with other optimizations.

#### 6.4 Experimental Approach

**Phase 1: Baseline Measurement**
```
1. Add logic analyzer triggers to OE, LAT, ADDR pins
2. Measure current timing with scope/analyzer
3. Document actual pulse widths and gaps
4. Identify conservative margins
```

**Phase 2: Incremental Reduction**
```
1. Reduce LAT pulse width until display glitches
2. Record minimum stable value
3. Reduce address setup time until glitches
4. Record minimum stable value
5. Reduce OE blanking duration
6. Test with various content (solid colors, patterns, gradients)
```

**Phase 3: Panel Variation Testing**
```
1. Test timing on multiple panel samples
2. Different batches may have different tolerances
3. Add safety margin to fastest panel timing
4. Document per-chip-type minimum timings
```

#### 6.5 ICN2037-Specific Considerations

From the ICN2037 datasheet:
- Max clock frequency: 20 MHz (50ns period)
- Latch setup time: typically 10-15ns
- OE response time: typically 20-30ns

**Current implementation may have 2-3x safety margin** - experimentation can find actual minimums.

#### 6.6 Latch Overlap Optimization

Some panels (FM6126A) support **overlapped latching** - latching during the last few clock cycles of data shift:

```
Standard (sequential):
[Data Shift 512 cycles]──►[Blank]──►[Latch]──►[Unblank]

Overlapped (parallel):
[Data Shift 509 cycles]──►[LAT during last 3 clocks]──►[Unblank]
                          └─ Saves ~10-20 cycles/row
```

The current driver has code paths for both - verify the optimal path is being used.

#### 6.7 Research Tasks

- [ ] Baseline measurement: Capture current OE/LAT/ADDR timing on scope
- [ ] Test LAT pulse width reduction (target: 2-4 cycles minimum)
- [ ] Test address setup time reduction (target: 4-6 cycles)
- [ ] Test OE blanking duration reduction
- [ ] Verify overlapped latch mode is working (for supported panels)
- [ ] Document minimum stable timing per chip type
- [ ] Add configurable timing parameters to driver

---

## Implementation Phases

### Phase 1: Baseline Measurement
- [ ] Add precise timing instrumentation
- [ ] Measure actual refresh rate at each color depth
- [ ] Profile each section of the data path
- [ ] Document current power consumption

### Phase 2: Quick Wins (Code Optimization)
- [ ] Reduce color depth to 5-bit for immediate improvement
- [ ] Optimize inner loop instruction sequence
- [ ] Increase COG buffer size if possible
- [ ] Remove unnecessary WAITX delays if panel tolerates

### Phase 3: Streamer Integration
- [ ] Prototype streamer-based data output
- [ ] Benchmark against current implementation
- [ ] Handle two-pin-group challenge
- [ ] Integrate with existing command structure

### Phase 4: Smart PIN Enhancement
- [ ] Implement hardware CLK generation
- [ ] Evaluate Sync TX for data output
- [ ] Benchmark combined streamer + smart pin approach

### Phase 5: Memory Architecture Revision
- [ ] Implement LUT-based color lookup
- [ ] Optimize buffer layout for streaming
- [ ] Consider multi-COG parallel processing

---

## Success Criteria

| Metric | Current | Target | Stretch Goal |
|--------|---------|--------|--------------|
| Refresh Rate (8-bit) | 2-5 Hz | 30 Hz | 60 Hz |
| Refresh Rate (5-bit) | 16-41 Hz | 60 Hz | 120 Hz |
| Inner Loop Cycles | 16/pixel | 8/pixel | 4/pixel |
| PWM Conversion Time | 24,742 µs | 12,000 µs | 6,000 µs |
| Visible Flicker | Severe | Minimal | None |

---

## References

### P2 Documentation
- Silicon Doc v35: Streamer section
- P2 Datasheet: Smart PIN modes
- Parallax Forums: High-speed I/O techniques

### HUB75 Panel Documentation
- ICN2037 Datasheet: Timing specifications
- FM6126A Datasheet: Initialization sequences

### Related Code
- `isp_hub75_rgb3bit.spin2`: Current PASM2 driver
- `isp_hub75_panel.spin2`: PWM buffer generation
- `isp_hub75_colorUtils.spin2`: Color processing

---

## Notes

### Observed Behavior (2026-01-07)
- Different panel colors flash at different rates due to BCM bit patterns
- Colors missing MSB (bit 7) flash more noticeably
- Mixed colors (multiple RGB channels) appear more stable
- White/gray (all channels equal) shows uniform flicker

### Key Insight
The fundamental issue is that BCM requires N time units where N is exponential in color depth. Reducing color depth has the most immediate impact on refresh rate, but sacrifices color fidelity. Hardware acceleration (streamer, smart pins) could allow maintaining high color depth with acceptable refresh rates.

---

## Research Findings (2026-01-07)

### Finding 1: FIFO + RFBYTE Can Replace ALTGB/GETBYTE

**Current approach:** `ALTGB + GETBYTE` = 4 cycles for byte extraction from COG buffer

**FIFO approach:** `RFBYTE` = 2 cycles for byte read from HUB FIFO

```pasm
' FIFO-based inner loop (potential replacement)
rdfast  #0, pwm_buffer_address    ' Initialize FIFO (2 clocks)

' Inner loop using FIFO - saves 2 cycles per pixel
rep     @eobytes, colCtrMax
rfbyte  colorByte                 ' 2 cycles: read from FIFO
drvl    pinLedCLK                 ' 2 cycles: CLK low
setbyte OUTA, colorByte, #3       ' 2 cycles: output RGB data
waitx   waitCyclesLow             ' 2+N cycles: data setup time
drvh    pinLedCLK                 ' 2 cycles: CLK high
waitx   waitCyclesHigh            ' 2+M cycles: clock high time
eobytes
```

**Impact:** Reduces inner loop from 16 to 14 cycles/pixel (12.5% improvement)

**Limitation:** FIFO reads from HUB RAM directly, eliminating COG buffer subpage overhead but requiring careful address management for BCM frames.

---

### Finding 2: Streamer Can Generate CLK While CPU Handles Data

The P2 Streamer operates independently with zero CPU overhead once started:

**Key Streamer Capabilities:**
- NCO-driven timing (32-bit phase accumulator)
- Pin group output (8 pins per group)
- Can chain commands with `XINIT`/`XCONT`/`XZERO`
- Generates events: block wrap, empty, finished, NCO rollover

**Streamer + Smart PIN Pattern (from P2KB):**
```pasm
' Parallel operation: Streamer outputs data, Smart PIN generates clock
xinit   rmode, pa            ' Start streamer outputting bits
wypin   tranp, #spi_ck       ' Start N clock transitions
waitxfi                      ' Wait for streamer completion
```

**Challenge for HUB75:** Pins span two groups:
- Group 2 (P16-P23): RGB1 R, G, B + RGB2 R, G, B
- Group 3 (P24-P31): ADDR A-E, CLK, LAT, OE

This requires coordinating two streamers or using Smart PINs for control signals while streaming data.

---

### Finding 3: LUT RAM - Major Optimization Opportunity

**LUT Specifications:**
- 512 longs (2KB) per COG
- Read: 3 cycles (RDLUT) - fixed, deterministic
- Write: 2 cycles (WRLUT)
- Block transfer: `SETQ2 + RDLONG` for bulk HUB→LUT (2 + N cycles for N longs)

**Key Feature: LUT Sharing Between Adjacent COGs**

The P2 allows even/odd COG pairs to share LUT access:
- `SETLUTS #1` enables sharing - writes from companion COG are mirrored
- COG pairs: [0,1], [2,3], [4,5], [6,7]
- When COG 1 writes to its LUT, the data appears in COG 0's LUT (if sharing enabled)

**Double-Buffer Architecture Using Two COGs:**

```
┌─────────────────────────────────────────────────────────────┐
│                    LUT Double-Buffer Pattern                │
├─────────────────────────────────────────────────────────────┤
│  COG 0 (Display Driver)         COG 1 (Data Loader)        │
│  ─────────────────────         ─────────────────────        │
│  SETLUTS #1 (enable sharing)                                │
│                                                             │
│  Phase A:                                                   │
│  ├─ RDLUT from LUT[0..255]     ├─ SETQ2 + RDLONG from HUB   │
│  ├─ Output to pins             ├─ WRLUT to LUT[256..511]    │
│  └─ (data loader fills B)      └─ (mirrored to COG 0)       │
│                                                             │
│  Phase B:                                                   │
│  ├─ RDLUT from LUT[256..511]   ├─ SETQ2 + RDLONG from HUB   │
│  ├─ Output to pins             ├─ WRLUT to LUT[0..255]      │
│  └─ (data loader fills A)      └─ (mirrored to COG 0)       │
└─────────────────────────────────────────────────────────────┘
```

**Current Architecture (Single COG):**
```
Per-frame operations:
- 32 subpages × (SETQ + RDLONG) = 32 × 130 cycles = 4,160 cycles overhead
- Display must WAIT for each HUB transfer to complete
- HUB access competes with other COGs
```

**LUT Double-Buffer Architecture (Two COGs):**
```
Per-frame operations:
- COG 0: Pure display loop - NO transfer waits
- COG 1: Continuous background loading
- Transfer overhead: ZERO during display
- Display reads from LUT: 3 cycles (deterministic)
```

**Buffer Sizing Analysis:**

| Buffer Config | Longs | Bytes | Rows | Transfers/Frame |
|---------------|-------|-------|------|-----------------|
| Current COG buffer | 128 | 512 | 4 | 32 |
| Half LUT (ping-pong) | 256 | 1024 | 8 | 16 |
| Full LUT + COG | 640 | 2560 | 20 | 6 |

**Implementation Pattern:**

```pasm
' === COG 0: Display Driver ===
setup_display
        setluts #1                      ' Enable LUT sharing from COG 1

display_loop
        ' Display from buffer A while B loads
        mov     lut_ptr, #0             ' Start of buffer A
        call    #display_buffer

        ' Display from buffer B while A loads
        mov     lut_ptr, #256           ' Start of buffer B
        call    #display_buffer
        jmp     #display_loop

display_buffer
        rep     @.end, #256             ' 256 longs in half-LUT
        rdlut   data, lut_ptr           ' 3 cycles: read from LUT
        ' ... output to pins ...
        add     lut_ptr, #1
.end
        ret

' === COG 1: Data Loader ===
loader_loop
        ' Load buffer B while A displays
        setq2   #255                    ' 256 longs
        rdlong  256, ptra               ' Load to LUT[256..511]
        ' Signal COG 0 that B is ready

        ' Load buffer A while B displays
        setq2   #255                    ' 256 longs
        rdlong  0, ptra                 ' Load to LUT[0..255]
        ' Signal COG 0 that A is ready
        jmp     #loader_loop
```

**Performance Impact:**

| Metric | Current | With LUT Double-Buffer |
|--------|---------|------------------------|
| Transfer overhead/frame | 4,160 cycles | ~0 cycles |
| HUB bandwidth contention | High | Split across 2 COGs |
| Display loop determinism | Variable | Fixed 3-cycle LUT reads |
| COG usage | 1 | 2 |

**Potential Uses (Priority Order):**

1. **Double-buffer display data** - Eliminates transfer waits (HIGH VALUE)
2. **Gamma correction table** - 256 entries per channel, single-cycle lookup
3. **Pre-computed BCM patterns** - Store bit-extracted data ready for output
4. **Address generation LUT** - Wire-order remapping without runtime calculation

**Assessment:** LUT double-buffering with a dedicated loader COG could **eliminate all HUB transfer overhead** during display. This is a significant architectural change but offers the best performance improvement for the additional COG cost. Combined with RDLUT's deterministic 3-cycle timing, this could provide substantial refresh rate improvement.

---

### Finding 3a: Refresh Rate Impact Analysis

**Timing Breakdown (Current Architecture):**
```
Per-pixel:           16 cycles (inner loop)
Per-row display:     16 × 512 columns = 8,192 cycles
Per-row overhead:    ~200 cycles (transfer + latch + address)
  - Subpage transfer (SETQ + RDLONG 128 longs): ~130 cycles
  - Latch, address change, OE control: ~70 cycles
Per-row total:       8,392 cycles
Per-BCM-unit:        8,392 × 32 rows = 268,544 cycles
```

**Refresh Rate Comparison Table:**

| Optimization | Cycles/Pixel | Cycles/BCM | 8-bit | 7-bit | 6-bit | 5-bit | 4-bit |
|--------------|--------------|------------|-------|-------|-------|-------|-------|
| **Current** | 16 | 268,544 | **4.9 Hz** | 9.8 Hz | 19.8 Hz | 40.2 Hz | 83.3 Hz |
| + LUT double-buffer | 16 | 264,384 | **5.0 Hz** | 10.0 Hz | 20.1 Hz | 40.8 Hz | 84.7 Hz |
| + RFBYTE FIFO | 14 | 231,616 | **5.7 Hz** | 11.4 Hz | 22.9 Hz | 46.7 Hz | 96.2 Hz |
| + Remove WAITX | 12 | 198,848 | **6.6 Hz** | 13.3 Hz | 26.7 Hz | 54.3 Hz | 112 Hz |
| + All optimizations | 10 | 166,080 | **7.9 Hz** | 15.9 Hz | 32.0 Hz | 65.1 Hz | 135 Hz |

**Key Observations:**

1. **LUT double-buffer alone: +1.6% improvement**
   - Transfer overhead (130 cycles/row) is only ~1.5% of row time (8,392 cycles)
   - Eliminates jitter but doesn't dramatically improve refresh rate

2. **RFBYTE FIFO: +16% improvement**
   - Saves 2 cycles per pixel (ALTGB+GETBYTE → RFBYTE)
   - More significant because it affects every pixel

3. **Remove WAITX: +16% additional improvement**
   - If panel tolerates faster clock (needs testing!)
   - Could potentially go from 16 to 12 cycles/pixel

4. **Combined optimizations: +35% improvement**
   - Best case: 7.9 Hz at 8-bit (still too slow)
   - But at 5-bit: 65 Hz (usable!)

**The Fundamental Math Problem:**

Even with all optimizations, 8-bit color cannot reach flicker-free refresh:
```
Theoretical minimum (6 cycles/pixel for CLK toggle + data):
Per-BCM-unit: 6 × 512 × 32 = 98,304 cycles
8-bit (255 units): 98,304 × 255 = 25,067,520 cycles = 74.8 ms = 13.4 Hz

Still below 30 Hz threshold for flicker-free viewing!
```

**Practical Recommendations:**

| Target Refresh | Required Color Depth | Notes |
|----------------|---------------------|-------|
| 30 Hz minimum | 6-bit (with optimizations) | Acceptable for static content |
| 60 Hz smooth | 5-bit (with optimizations) | Good for animations |
| 120 Hz flicker-free | 4-bit (with optimizations) | Best visual quality |

**LUT Double-Buffer Value Proposition:**

While LUT double-buffering only provides ~1.6% direct refresh improvement, it enables:
1. **Deterministic timing** - No variable HUB access delays
2. **Offload processing** - Loader COG can do gamma correction, wire remapping
3. **Future scalability** - Foundation for multi-COG parallel display
4. **Reduced jitter** - Smoother visual appearance even at same refresh rate

---

### Finding 4: Smart PIN Sync Serial TX Mode

**Mode %11100 - Synchronous Serial Transmit:**
- Transmits 1-32 bits synchronized with external clock
- LSB first (MSB requires REV instruction)
- Double-buffered for continuous operation
- IN flag indicates buffer ready for next data

**Configuration Pattern:**
```pasm
' Setup Sync TX for 6-bit RGB output
mode := P_SYNC_TX | P_OE | P_PLUS1_B    ' Clock from adjacent pin
wrpin   mode, rgb_pin
wxpin   #%0_00101, rgb_pin              ' Continuous, 6-bit
dirh    rgb_pin                          ' Enable

' Transmit data
wypin   rgb_data, rgb_pin               ' Load data, shifts on clock
```

**Application to HUB75:** Could potentially use Smart PIN for RGB data output, clocked by panel CLK. However, the HUB75 protocol requires parallel 6-bit output (R1,G1,B1,R2,G2,B2), not serial. This mode is better suited for SPI-like interfaces.

---

### Finding 5: Critical Timing Analysis

**Current Timing Breakdown:**
```
Per-pixel: 16 cycles = 47.8 ns @ 335 MHz
Per-row: 16 × 512 = 8,192 cycles = 24.5 µs
Per-scan-line: 8,192 × 2 (top + bottom half) = 16,384 cycles
Per-BCM-frame (bit 0): 16,384 × 32 rows = 524,288 cycles = 1.57 ms
Full 8-bit refresh: 1.57 ms × 255 = 400 ms = 2.5 Hz
```

**Target: 60 Hz requires:**
```
Total frame time: 16.67 ms
Per BCM unit: 16.67 / 255 = 65.4 µs
Per scan line: 65.4 / 32 = 2.04 µs
Per pixel: 2.04 µs / 512 = 4 ns = 1.3 cycles
```

**Conclusion:** Reaching 60 Hz at 8-bit depth is mathematically impossible with current architecture. Each pixel needs ~1.3 cycles, but we need minimum ~6 cycles for data setup and clock toggle.

**Realistic Options:**
1. **Reduce color depth to 5-bit:** 31 time units → ~41 Hz achievable
2. **Reduce color depth to 4-bit:** 15 time units → ~85 Hz achievable
3. **Multi-COG parallel:** Multiple COGs drive different panel sections

---

### Finding 6: Feasibility Assessment

| Optimization | Complexity | Impact | COGs | Recommended |
|--------------|------------|--------|------|-------------|
| Remove WAITX (test panel tolerance) | Low | -25% cycles | 0 | Test first |
| RFBYTE FIFO inner loop | Low | -12.5% cycles | 0 | Yes |
| Reduce color depth (5-bit) | Low | 8x improvement | 0 | Best ROI |
| **LUT double-buffer (2 COGs)** | **Medium** | **Eliminates transfer overhead** | **+1** | **High value** |
| Smart PIN CLK generation | Medium | Frees CPU cycles | 0 | Worth testing |
| LUT gamma correction | Medium | Better color quality | 0 | After basics |
| **HyperRAM pre-computed PWM** | **Medium** | **Eliminates 24.7ms conversion** | **+1** | **For animation** |
| Streamer data output | High | Zero CPU overhead | 0 | Complex - pin groups |
| Multi-COG panel parallel | High | 2-4x throughput | +1-3 | Major rewrite |

**HyperRAM Strategy (32MB @ 80 MB/s):**
- Pre-compute PWM frames offline or during setup
- Store 250+ complete animation frames
- Transfer time: 1.6ms per frame vs 24.7ms real-time conversion
- Best for: Animation playback, digital signage, pre-rendered content
- Not helpful for: Real-time dynamic content (still needs conversion)

**Priority Recommendations:**

**Phase A - Quick Wins (No Architecture Change):**
1. Test panel at higher clock rate (remove/reduce WAITX)
2. Implement RFBYTE FIFO to replace ALTGB/GETBYTE
3. Evaluate 5-bit color depth with temporal dithering

**Phase B - LUT Architecture (1 Additional COG):**
4. Implement LUT double-buffer with dedicated loader COG
5. Use SETLUTS for zero-copy data sharing between COGs
6. Add gamma correction table in remaining LUT space

**Phase C - Advanced (If Needed):**
7. Smart PIN CLK generation
8. Streamer integration (if pin group challenge solved)
9. Multi-COG parallel panel driving

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-07 | Claude | Initial document creation with baseline measurements |
| 2026-01-07 | Claude | Added detailed research findings from P2 Knowledge Base |
