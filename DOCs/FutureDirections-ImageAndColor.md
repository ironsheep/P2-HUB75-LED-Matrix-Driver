# Future Directions: Image Generation and Color Rendering

This document covers image generation requirements for the P2 HUB75 LED Matrix Driver and future optimization opportunities for color rendering.

---

## Part 1: Image Generation for LED Matrices

### Target Display Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Resolution** | 256 x 128 pixels | 2x2 grid of 128x64 panels |
| **Total Pixels** | 32,768 | |
| **Aspect Ratio** | 2:1 (wide) | Landscape orientation |
| **Color Depth** | 24-bit (8 bits/channel) | Configurable 3-8 bits per channel |
| **Color Space** | RGB | Direct per-pixel control |

### Image Creation Requirements

#### Resolution and Format

When creating images for this display:

1. **Exact Resolution**: Create images at exactly **256 x 128 pixels**
   - No scaling artifacts
   - Every pixel maps 1:1 to an LED
   - PNG format recommended (lossless, RGB support)

2. **Color Format**: 24-bit RGB (8 bits per channel)
   - Red: 0-255
   - Green: 0-255
   - Blue: 0-255

3. **Aspect Ratio**: 2:1 horizontal
   - Wide panoramic compositions work well
   - Vertical compositions should account for the short height (128px)

#### LED-Specific Considerations

Unlike LCD/OLED displays, LED matrices have unique characteristics that affect image appearance:

| Consideration | Recommendation |
|--------------|----------------|
| **Discrete Pixels** | Each LED is physically separate; avoid fine gradients that rely on anti-aliasing |
| **High Contrast** | LEDs produce vibrant, saturated colors; images can be slightly more contrasty |
| **Black = Off** | True black (RGB 0,0,0) means the LED is completely off; use this for dramatic effect |
| **Viewing Distance** | At typical viewing distances (1-3 meters), individual pixels blend naturally |
| **No Dithering Required** | The P2 driver uses Binary Coded Modulation (BCM) which provides smooth gradients without display-level dithering |

#### Image Content Suggestions

**Recommended Subjects:**
- Night scenes (urban, winter, starfields) - excellent contrast
- Landscapes with strong color blocks
- Abstract patterns and gradients
- Text with large fonts (8px+ height minimum)
- Geometric designs

**Avoid:**
- Fine text (under 5px height)
- Subtle low-contrast gradients
- Images relying on anti-aliased edges for clarity
- Photographs with lots of fine detail (better for larger resolutions)

### Why Dithering Is Not Required

The P2 HUB75 driver uses **Binary Coded Modulation (BCM)** for color depth, not simple on/off PWM:

```
BCM Principle:
- Each color bit (0-7) is displayed for 2^bit time units
- Bit 7 (MSB): displayed for 128 time units
- Bit 6: displayed for 64 time units
- ...
- Bit 0 (LSB): displayed for 1 time unit
- Total: 255 distinct brightness levels per color channel
```

This provides:
- **16.7 million colors** (256 R × 256 G × 256 B)
- Smooth gradients without banding
- No display-level dithering artifacts
- Human eye perceives continuous color

**Important**: If generating images externally, avoid applying dithering (Floyd-Steinberg, ordered, etc.) as the display hardware already provides sufficient color resolution. Dithering would only add noise.

---

## Part 2: Color Rendering Optimization

### Current Driver Architecture

The P2 HUB75 driver runs on the **Parallax Propeller 2** microcontroller:

| Specification | Value |
|--------------|-------|
| **System Clock** | 335 MHz (each demo sets it with `_CLKFREQ`) |
| **Cores (Cogs)** | 8 independent 32-bit cores |
| **Smart Pins** | 64 hardware-accelerated I/O pins |
| **I/O Speed** | 2 clock cycles per pin instruction |
| **Effective Pin Rate** | ~167 MHz toggle rate |
| **Assembly Language** | PASM2 for timing-critical code |
| **High-Level Language** | Spin2 for configuration/logic |

### PWM/BCM Implementation

The driver implements **Binary Coded Modulation** for color depth:

```
Screen Buffer (24-bit RGB)
         │
         ▼
   PWM Conversion (Spin2 + inline PASM2)
         │
         ▼
   PWM Frame Buffers (N buffers for N-bit depth)
         │
         ▼
   PASM2 Driver (dedicated COG)
         │
         ▼
   HUB75 Panel Hardware
```

**Current Characteristics:**
- Color depth: compile-time configurable (3-8 bits per channel)
- Two PWM frame sets: a commit converts into the set that is not on display and posts it, and the refresh cog switches to it at a frame start
- Screen-to-PWM conversion runs in Spin2 with inline PASM2 for speed
- Output driver runs in dedicated PASM2 COG for timing precision

### Refresh Rate Analysis

The refresh method (each bit plane shown once per row address and lit by /OE time), the target refresh rule, the measured rates by color depth, the brightness floor and the commit and draw times are in the [Wiring Guide's refresh rate section](WiringGuide.md#refresh-rate). Image and animation work should plan around the full-cycle refresh rates stated there, not around a fixed frame rate.

---

## Part 3: Future Optimization Opportunities

### Color Rendering Enhancements

#### 1. Gamma Correction

**Problem**: Human perception of brightness is non-linear. A pixel at 50% PWM does not appear half as bright as 100%.

**Today**: `isp_hub75_colorUtils.spin2` holds a 256-entry gamma curve and folds it into each adapter's color table (the table also does the color-depth mapping), so gamma costs nothing per pixel. The curve is off: its flag (`bGammaEnable` in `isp_hub75_colorUtils.spin2`) is FALSE and nothing in the driver sets it, so no setting you make turns it on.

**Future**: A per-display setting to turn gamma on, and a curve chosen per panel if LED characteristics vary.

#### 2. Color Balance/White Point Calibration

**Problem**: R, G, B LEDs have different efficiencies. White (255,255,255) may appear tinted.

**Solution**: Per-channel gain adjustment.

```
Calibrated_R = R × Red_Gain
Calibrated_G = G × Green_Gain
Calibrated_B = B × Blue_Gain

Typical values for 6500K white point:
- Red_Gain: 1.0
- Green_Gain: 0.85-0.95
- Blue_Gain: 0.75-0.85
```

**Implementation**: Some chips (FM6126A) have built-in current control. Software correction can supplement.

#### 3. Temporal Dithering (Advanced)

**Problem**: At lower color depths (3-4 bit), banding can be visible in gradients.

**Solution**: Vary the LSB across frames to create intermediate brightness levels.

```
4-bit color (16 levels) with temporal dithering:
- Frame N: display value 7
- Frame N+1: display value 8
- Frame N+2: display value 7
- Frame N+3: display value 8
- Perceived brightness: 7.5 (between the two discrete levels)
```

**Trade-offs**: Requires a high refresh rate to avoid visible flicker; the measured rates are in the [Wiring Guide](WiringGuide.md#refresh-rate).

#### 4. Scan-Line Brightness Uniformity

**Today**: The refresh core times each bit plane by /OE inside a fixed slot of 2^*k* x T clocks, so every row address gets the same timing at every brightness.

**Future**: Any remaining difference between scan lines would be per chip, and would need measuring on a panel before it is worth a fix.

### Performance Enhancements

#### 1. Screen-to-PWM Conversion Optimization

**Current**: Inline PASM2 in a Spin2 method, using MERGEB to build four columns per plane write; a commit takes 4.09 ms at 8-bit on the author's rig (see the [Wiring Guide](WiringGuide.md#refresh-rate)).

**Future**: Move the conversion to a dedicated PASM2 COG
- Parallel processing with display refresh
- Reduced main COG load
- Potential for real-time effects

#### 2. Direct DMA Feeding

**Concept**: Use P2's FIFO capabilities to stream PWM data directly to pins.

**Benefits**:
- Reduced CPU load
- More consistent timing
- Potential to lift the 512-column line-buffer limit

**Complexity**: Requires significant driver restructuring.

---

## Part 4: Supported Panel Configurations

The driver supports multiple panel types with different characteristics:

| Chip | Rated Max Clock | Scan | Init Required | Multi-Panel Status |
|------|-----------|------|---------------|-------------------|
| FM6126A | 30 MHz | 1/16 | Yes | Tested |
| FM6124 | 30 MHz | 1/16 | No | Single panel only |
| ICN2037/BP | 30 MHz (25.0 MHz in a chain) | 1/32 | No | Tested |
| ICN2038S | 30 MHz (28.6 MHz in a chain) | disputed (see the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md)) | Untested | Single panel; single-ended |
| MBI5124GP | 25 MHz (18.9 MHz in a chain) | 1/8 | Yes | Tested (two panels) |
| GS6238S | - (no rating in the driver's table; held to 20 MHz) | 1/16 | No | Single panel only |
| DP5125D | - (no rating in the driver's table; held to 20 MHz) | 1/8 | No | Tested |

The driver holds each half of the clock pulse to at least 20 ns, which caps every chip at 25 MHz, and holds the whole period to the chip's chain limit where that is lower (the MBI5124GP's 18.9 MHz; the ICN2037's 25.0 MHz and the ICN2038S's 28.6 MHz are at or above the pulse cap). The FM6124 and FM6126A chain limits have not been read. The ratings and the arithmetic are in the [Chip Characteristics Matrix](ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings).

### Notable Panel Configurations Tested

1. **6-Panel Cube** (64x64 × 6 panels)
   - Single horizontal chain
   - 384 × 64 effective resolution
   - Used for P2 Cube project

2. **2x2 Grid** (128x64 × 4 panels)
   - 256 × 128 effective resolution
   - Described by wiring sentences; this is the author's rig

3. **Horizontal Chains** (up to 6 panels)
   - Various panel sizes tested
   - Fully functional with current driver

---

## Summary

### For Image Generation

1. Create images at exact **256 × 128** resolution
2. Use **24-bit RGB** color
3. Save as **PNG** (lossless)
4. **No dithering required** - BCM provides smooth gradients
5. Design for high contrast and discrete pixels
6. Night scenes and bold graphics work best

### For Color Optimization

1. Current system provides **16.7M colors** at 8-bit, with a measured full color-cycle rate of **71.0 Hz** on the rig at the default 60 Hz target; 4-bit (4,096 colors) runs at 90.5 Hz
2. Future: a setting to turn on the **gamma correction** the color table already holds, for perceptually linear brightness
3. Future: Add **white point calibration** for accurate color balance
4. Future: Consider **temporal dithering** for enhanced low-depth color

### Key System Specifications

| Metric | Value |
|--------|-------|
| P2 Clock | 335 MHz |
| HUB75 Clock | 15 system clocks per column at 335 MHz, CLK high 20.9 ns and low 23.9 ns (ICN2037 rated 30 MHz) |
| Display Size | 256 × 128 |
| Color Depth | 8-bit (configurable 3-8) |
| Refresh Rate | 71.0 Hz full color cycle @ 8-bit (measured, 60 Hz target; 193.3 Hz @ 3-bit, 90.5 Hz @ 4-bit) |
| Color Palette | 16.7 million |
| Driver Language | PASM2 (time-critical) + Spin2 (logic) |

---

*Document generated from P2 HUB75 driver analysis - January 2025*
