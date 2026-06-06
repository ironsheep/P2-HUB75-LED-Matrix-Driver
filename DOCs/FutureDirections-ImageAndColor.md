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
| **System Clock** | 335 MHz |
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
- Double-buffered PWM frames (frame 1 displays while frame 2 is being built)
- Screen-to-PWM conversion runs in Spin2 with inline PASM2 for speed
- Output driver runs in dedicated PASM2 COG for timing precision

### Refresh Rate Analysis

#### Calculation Parameters (2x2 Panel Configuration)

| Parameter | Value |
|-----------|-------|
| Display Resolution | 256 x 128 pixels |
| Physical Chain | 512 columns (4 × 128) |
| Scan Rate | 1/32 (32 address lines) |
| Driver Chip | ICN2037 (20 MHz max clock) |
| Row Clock Time | 512 ÷ 20 MHz = **25.6 µs** |

#### Theoretical Refresh Rates by Color Depth

| Color Depth | Bits/Channel | Row Clocks/Frame | Frame Time | Refresh Rate | Colors |
|-------------|--------------|------------------|------------|--------------|--------|
| 3-bit | 3 | 96 | 2.46 ms | **407 Hz** | 512 |
| 4-bit | 4 | 128 | 3.28 ms | **305 Hz** | 4,096 |
| 5-bit | 5 | 160 | 4.10 ms | **244 Hz** | 32,768 |
| 6-bit | 6 | 192 | 4.92 ms | **203 Hz** | 262,144 |
| 7-bit | 7 | 224 | 5.73 ms | **175 Hz** | 2,097,152 |
| 8-bit | 8 | 256 | 6.55 ms | **153 Hz** | 16,777,216 |

**Notes:**
- These are theoretical maximums based on chip clock speed
- Actual rates may be lower due to latch timing, OE blanking, and processing overhead
- All rates exceed the 60 Hz threshold for flicker-free perception
- Even 8-bit color at 153 Hz is excellent for video and animation

#### Formula

```
Frame Time = (Color Depth × Scan Lines × Chain Columns) ÷ Clock Speed
Refresh Rate = 1 ÷ Frame Time

Example (8-bit, 256x128 display):
Frame Time = (8 × 32 × 512) ÷ 20,000,000 = 0.00655 seconds = 6.55 ms
Refresh Rate = 1 ÷ 0.00655 = 152.7 Hz
```

---

## Part 3: Future Optimization Opportunities

### Color Rendering Enhancements

#### 1. Gamma Correction

**Problem**: Human perception of brightness is non-linear. A pixel at 50% PWM does not appear half as bright as 100%.

**Solution**: Apply gamma correction lookup table during screen-to-PWM conversion.

```
Perceived Brightness = (Actual Brightness)^2.2

Example LUT approach:
- Input: 8-bit linear color (0-255)
- Output: gamma-corrected value for BCM
- Standard gamma: 2.2 (matches most content)
- Can be panel-specific if LED characteristics vary
```

**Implementation**: Add compile-time or runtime gamma LUT in `isp_hub75_colorUtils.spin2`.

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

**Trade-offs**: Requires higher refresh rate to avoid visible flicker. At 200+ Hz, works well.

#### 4. Scan-Line Brightness Uniformity

**Problem**: Due to BCM timing, some scan lines may appear brighter than others.

**Solution**: Normalize OE (output enable) timing across all bit planes.

**Implementation**: Already partially addressed in PASM2 driver timing. Can be fine-tuned per chip type.

### Performance Enhancements

#### 1. Screen-to-PWM Conversion Optimization

**Current**: Inline PASM2 in Spin2 method

**Future**: Move entire conversion to dedicated PASM2 COG
- Parallel processing with display refresh
- Reduced main COG load
- Potential for real-time effects

#### 2. 2D Panel Grid Support (In Progress)

**Current Issue**: PWM conversion assumes horizontal chain layout; 2D grids (2x2, 2x3, etc.) show repeated content.

**Fix Required**: Modify PWM conversion to read from correct display rows based on panel grid position.

#### 3. Direct DMA Feeding

**Concept**: Use P2's FIFO capabilities to stream PWM data directly to pins.

**Benefits**:
- Reduced CPU load
- More consistent timing
- Potential for higher refresh rates

**Complexity**: Requires significant driver restructuring.

---

## Part 4: Supported Panel Configurations

The driver supports multiple panel types with different characteristics:

| Chip | Max Clock | Scan | Init Required | Multi-Panel Status |
|------|-----------|------|---------------|-------------------|
| FM6126A | 30 MHz | 1/16 | Yes | Tested |
| FM6124 | 30 MHz | 1/16 | No | Untested |
| ICN2037/BP | 20 MHz | 1/32 | No | Tested |
| ICN2038S | 20 MHz | 1/8 | No | Single-ended |
| MBI5124GP | 20 MHz | 1/8 | Yes | Untested |
| GS6238S | 30 MHz | 1/16 | No | Untested |
| DP5125D | - | 1/8 | No | Untested |

### Notable Panel Configurations Tested

1. **6-Panel Cube** (64x64 × 6 panels)
   - Single horizontal chain
   - 384 × 64 effective resolution
   - Used for P2 Cube project

2. **2x2 Grid** (128x64 × 4 panels)
   - 256 × 128 effective resolution
   - Requires 2D grid PWM fix (in progress)

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

1. Current system provides **16.7M colors** at **150+ Hz** refresh
2. Future: Add **gamma correction** for perceptually linear brightness
3. Future: Add **white point calibration** for accurate color balance
4. Future: Consider **temporal dithering** for enhanced low-depth color

### Key System Specifications

| Metric | Value |
|--------|-------|
| P2 Clock | 335 MHz |
| HUB75 Clock | 20 MHz (ICN2037) |
| Display Size | 256 × 128 |
| Color Depth | 8-bit (configurable 3-8) |
| Refresh Rate | ~153 Hz @ 8-bit color |
| Color Palette | 16.7 million |
| Driver Language | PASM2 (time-critical) + Spin2 (logic) |

---

*Document generated from P2 HUB75 driver analysis - January 2025*
