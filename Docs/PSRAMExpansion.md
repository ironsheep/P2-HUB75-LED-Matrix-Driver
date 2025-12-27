# PSRAM Expansion for P2 HUB75 LED Matrix Driver

This document describes how PSRAM/HyperRAM on the P2-EC32MB Edge Module expands the capabilities of the LED matrix driver.

## Hardware: P2-EC32MB Edge Module

The **P2-EC32MB Edge Module** (Parallax #64032) includes:
- **32MB HyperRAM** (fast external RAM) - *Target test platform*
- 8MB Flash
- Castellated edge connector for soldering
- All 64 I/O pins accessible

This provides 64× more RAM than the P2's internal 512KB hub RAM.

> **Note:** Reference driver code is in `REF-23MB/` folder (excluded from git).

## Current Memory Limitations

### Hub RAM Constraints (512KB)

The current driver stores all buffers in hub RAM:

| Buffer | Formula | Purpose |
|--------|---------|---------|
| Screen Buffer | W × H × 3 bytes | 24-bit RGB pixels |
| PWM Frameset 1 | W × H × 0.5 × depth bytes | Binary-weighted PWM frames |
| PWM Frameset 2 | W × H × 0.5 × depth bytes | Double-buffer for smooth updates |

### Maximum Configurations (Hub RAM Only)

| Configuration | Pixels | 8-bit Memory | Status |
|---------------|--------|--------------|--------|
| 2×2 @ 128×64 | 32,768 | 196 KB | ✓ Works |
| 4×4 @ 64×64 | 65,536 | 393 KB | ✓ Tight |
| 4×4 @ 128×64 | 131,072 | 786 KB | ✗ Exceeds 512KB |
| 8×8 @ 64×64 | 262,144 | 1.5 MB | ✗ Exceeds 512KB |

## What 32MB PSRAM Enables

### 1. Massive Display Configurations

With screen buffer in PSRAM (3 bytes/pixel):
- **32MB ÷ 3 = 10.6 million pixels** theoretical maximum

| Configuration | Pixels | Screen Buffer | PWM Working Set |
|---------------|--------|---------------|-----------------|
| 4×4 @ 128×64 | 131,072 | 384 KB | Hub RAM |
| 8×4 @ 128×64 | 262,144 | 768 KB | Hub RAM |
| 8×8 @ 64×64 | 262,144 | 768 KB | Hub RAM |
| 8×8 @ 128×64 | 524,288 | 1.5 MB | Hub RAM |
| 16×8 @ 64×64 | 524,288 | 1.5 MB | Hub RAM |
| 16×16 @ 64×64 | 1,048,576 | 3.0 MB | Hub RAM |

**Practical limit:** Panel driver timing and PWM generation, not memory.

### 2. Multi-Frame Animation Storage

Store complete pre-rendered animation sequences:

| Frames | 256×128 display | 512×256 display | 1024×512 display |
|--------|-----------------|-----------------|------------------|
| 10 | 1 MB | 4 MB | 16 MB |
| 30 | 3 MB | 12 MB | — |
| 100 | 10 MB | — | — |

Benefits:
- Smooth animations without real-time rendering
- Complex graphics pre-computed offline
- Instant frame switching

### 3. Pre-Computed Graphics Assets

Store in PSRAM for instant access:
- **Fonts**: Multiple sizes, anti-aliased glyphs
- **Images**: Logos, backgrounds, sprites
- **Lookup tables**: Gamma correction, color palettes
- **Animation frames**: GIF-like sequences

### 4. Triple/Quad Buffering

Current: Double-buffered (2 PWM framesets)
With PSRAM:
- Triple buffer for tear-free animation at high frame rates
- Quad buffer for complex compositor effects
- Background preparation of next scenes

### 5. Virtual Display Paging

Store multiple complete "screens" in PSRAM:
- Instant switching between pre-rendered content
- Menu systems with pre-built pages
- Score displays with pre-rendered digits
- Multiple display modes without re-rendering

## Streamer: The P2's DMA Subsystem

The P2's streamer is a **zero-overhead DMA engine** that can dramatically improve PSRAM integration. Each COG has its own streamer.

### Streamer Capabilities

| Feature | Description |
|---------|-------------|
| **Zero CPU overhead** | Autonomous operation while COG executes other code |
| **NCO timing** | 32-bit phase accumulator for precise timing control |
| **FIFO buffering** | 19-stage buffer smooths hub RAM access |
| **RGB conversion** | Built-in RGB8/16/24 format conversion |
| **LUT staging** | 512 longs of LUT RAM available as buffer |
| **Pin output** | Direct streaming to pin groups |

### Pipeline Processing with Streamer

The streamer enables true pipelined processing:

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: PSRAM → Hub (Streamer A - autonomous)            │
│  ┌─────────┐                      ┌─────────────┐          │
│  │ PSRAM   │ ═══streamer═══════►  │ Hub Buffer  │          │
│  │ (32MB)  │     zero overhead    │ (next chunk)│          │
│  └─────────┘                      └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Stage 2: Screen → PWM (CPU processing)                    │
│  ┌─────────────┐                  ┌─────────────┐          │
│  │ Hub Buffer  │ ───CPU work────► │ PWM Frames  │          │
│  │(curr chunk) │                  │             │          │
│  └─────────────┘                  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Stage 3: PWM → Panels (Streamer B - autonomous)           │
│  ┌─────────────┐                  ┌─────────────┐          │
│  │ PWM Frames  │ ═══streamer═══►  │ HUB75 Pins  │ → Panels │
│  │(prev frames)│    zero overhead │             │          │
│  └─────────────┘                  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘

All three stages run IN PARALLEL - each processes different data!
```

### Reference PSRAM Driver Uses Streamer

The `REF-23MB/PSRAM_driver_RJA_Platform_1b.spin2` already uses streamer:

```spin2
setxfrq h40000000           ' Set 2-clock streamer timebase
xinit   cmdbit8,#$35        ' Send PSRAM command via streamer
xcont   cmdrw,#0            ' Stream data autonomously
' ... COG does other work while streamer handles transfer ...
```

### Performance Impact

| Without Streamer | With Streamer |
|------------------|---------------|
| CPU waits for each transfer | CPU works during transfer |
| Sequential processing | Pipelined parallel processing |
| ~40% utilization | ~90%+ utilization |

## LUT Sharing Between Adjacent COGs

The P2 allows adjacent COG pairs to share their 512-long (2KB) LUT RAM:
- **Pairs:** (0,1), (2,3), (4,5), (6,7)
- **SETLUTS #1:** Enables automatic write mirroring from adjacent COG
- **RDLUTS:** Read directly from neighbor's LUT

### Zero-Hub-Memory Data Handoff

```
┌─────────────────────────────────────────────────────────────────┐
│  COG 0 (PSRAM Driver)                COG 1 (HUB75 Output)       │
│  ┌─────────────────┐                 ┌─────────────────┐        │
│  │ LUT (512 longs) │══SETLUTS #1═══► │ LUT (512 longs) │        │
│  │ Writes here     │   auto-mirror   │ Reads mirrored  │        │
│  └─────────────────┘                 └─────────────────┘        │
│       ↑                                      ↓                  │
│  From PSRAM                            To HUB75 pins            │
│                                                                 │
│                  NO HUB RAM NEEDED FOR HANDOFF!                 │
└─────────────────────────────────────────────────────────────────┘
```

### LED Matrix Applications

| Use Case | How LUT Sharing Helps |
|----------|----------------------|
| **PSRAM → Panel pipeline** | PSRAM COG writes to LUT, output COG reads mirror - zero hub bandwidth |
| **Double-buffer in LUT** | Bank 0-255 for current, bank 256-511 for next, swap roles |
| **Gamma correction table** | One COG owns 256-entry table, adjacent COG reads directly |
| **Color palette lookup** | Shared palette without hub access or duplication |
| **Row buffer ping-pong** | Load next row while outputting current row |

### Double-Buffered LUT Pattern

```spin2
' COG 0: PSRAM loader - writes to its own LUT
COG0:
        wrlut   pixel_data, lut_ptr     ' Write to own LUT
        ' ... adjacent COG 1 sees this write automatically ...

' COG 1: HUB75 output - reads COG 0's LUT via mirroring
COG1:
        setluts #1                       ' Enable LUT sharing
        rdlut   pixel_data, lut_ptr      ' Reads COG 0's LUT!
        ' ... output to HUB75 pins ...
```

### Memory Hierarchy with LUT Sharing

```
┌────────────────────────────────────────────────────────────┐
│                    PSRAM (32MB)                            │
│              Large frame storage                           │
└────────────────────────────────────────────────────────────┘
                         ↓ Streamer (autonomous)
┌────────────────────────────────────────────────────────────┐
│                  Hub RAM (512KB)                           │
│            Working buffers, PWM framesets                  │
└────────────────────────────────────────────────────────────┘
                         ↓ Fast access
┌────────────────────────────────────────────────────────────┐
│  COG LUT (2KB each)     ←──SETLUTS──→    Adjacent COG LUT  │
│  - Gamma tables                          - Direct read     │
│  - Row buffers                           - No hub needed   │
│  - Ping-pong data                        - 3-cycle access  │
└────────────────────────────────────────────────────────────┘
                         ↓ Streamer (autonomous)
┌────────────────────────────────────────────────────────────┐
│                    HUB75 Panels                            │
└────────────────────────────────────────────────────────────┘
```

## Architecture Changes Required

### Current Architecture
```
┌─────────────────────────────────────────┐
│              Hub RAM (512KB)            │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │Screen Buffer│→ │PWM Framesets ×2 │   │
│  └─────────────┘  └─────────────────┘   │
│         ↓                  ↓            │
│  ┌────────────────────────────────────┐ │
│  │         PASM2 Driver (COG)         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │  HUB75 Panels │
            └───────────────┘
```

### PSRAM-Enhanced Architecture
```
┌─────────────────────────────────────────┐
│           PSRAM (32MB)                  │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │Screen Buffer│  │Animation Frames │   │
│  │  (large!)   │  │  Pre-rendered   │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
          ↓ DMA-like transfers
┌─────────────────────────────────────────┐
│              Hub RAM (512KB)            │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Line Buffer │  │PWM Working Set  │   │
│  │  (striped)  │  │(subset of frame)│   │
│  └─────────────┘  └─────────────────┘   │
│         ↓                  ↓            │
│  ┌────────────────────────────────────┐ │
│  │   PASM2 Driver (COG) + PSRAM COG   │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │  HUB75 Panels │
            └───────────────┘
```

### Key Implementation Considerations

1. **PSRAM Driver COG**: Requires 1 COG dedicated to PSRAM access
2. **Striped Transfers**: Transfer screen data in horizontal strips to hub RAM
3. **Pipeline Processing**: While driver outputs current strip, load next strip
4. **Latency**: PSRAM has ~1µs access latency (vs ~10ns for hub RAM)
5. **Bandwidth**: ~40MB/s sustained throughput sufficient for most displays

## Reference Implementation

The `REF-23MB/` folder contains a working PSRAM driver:

| File | Purpose |
|------|---------|
| `PSRAM_driver_RJA_Platform_1b.spin2` | Core PSRAM read/write driver |
| `HDMI_640x480_24bpp.spin2` | Example: Video output from PSRAM |
| `PsramGraphics.spin2` | Example: Graphics primitives with PSRAM |

### PSRAM Driver Interface

```spin2
' Start the driver (uses 1 COG)
psram.start()

' Get command pointer for this COG
ptr := psram.pointer()

' Write to PSRAM (negative count = hub → PSRAM)
long[ptr][0] := @hubBuffer      ' Hub RAM source address
long[ptr][1] := psramAddress    ' PSRAM destination (long address)
long[ptr][2] := -longCount      ' Negative = write to PSRAM

' Read from PSRAM (positive count = PSRAM → hub)
long[ptr][0] := @hubBuffer      ' Hub RAM destination address
long[ptr][1] := psramAddress    ' PSRAM source (long address)
long[ptr][2] := longCount       ' Positive = read from PSRAM

' Wait for completion
repeat while long[ptr][2]
```

### Performance Characteristics

- **Transfer rate**: 1 long every 4 clocks (~80MB/s at 320MHz)
- **Latency**: ~1µs minimum per transaction
- **Page size**: 1KB (page crossing adds overhead)
- **Multi-cog**: All 8 COGs can request transfers

## Feature Summary

| Feature | Hub RAM Only | With 32MB PSRAM |
|---------|--------------|-----------------|
| Max display size | ~65K pixels | ~1M+ pixels |
| Animation frames | 2 (double-buffer) | 100+ stored |
| Pre-rendered assets | Limited | Extensive |
| Instant scene switching | No | Yes |
| Large font libraries | No | Yes |
| COGs required | N | N+1 (PSRAM driver) |

## Recommended Use Cases

1. **Large Venue Displays**: 8×8 or larger panel grids
2. **Digital Signage**: Multiple pre-rendered pages
3. **Animation Playback**: Smooth pre-computed sequences
4. **Graphics-Heavy Applications**: Logos, images, complex fonts
5. **Interactive Displays**: Instant response with pre-rendered states

## P2KB Gap Identified

The P2 Knowledge Base is missing detailed HyperRAM/PSRAM driver documentation. This should be added to cover:
- P2 Edge Module specifications (32MB HyperRAM variant)
- PSRAM driver API and usage patterns
- Performance characteristics and optimization tips
- Multi-cog synchronization patterns
