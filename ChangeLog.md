# Change Log

All notable changes to the HUB75 LED Matrix Driver will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for reminders on how to structure this file. Also, note that our version numbering adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Pages: [README](README.md) | [Hardware Turn-on](HardwareTurnon.md) | [Driver Details](THEOPS.md) | [Wiring Guide](DOCs/WiringGuide.md) | Change Log

## [4.0.0] 08 Oct 2026

Full 8-bit color at flicker-free refresh rates, displays of any panel layout including a cube, and a new configuration and startup call.

### New Features

- **Wiring sentences**, `DISPx_C0` to `DISPx_C15`: each panel's sentence places it beside an earlier panel and names its arrow; rows, grids and L shapes work
- **Startup check**: a wiring mistake prints one `HUB75:` line naming the setting and stops; a correct config prints the grid it derived ([messages](DOCs/WiringGuide.md#startup-messages))
- **Cube display**: `DISPx_SHAPE = hwEnum.SHAPE_CUBE` folds six square panels into a cube; `drawFacePixel()`, `drawFaceLine()`, `drawFaceBox()`, `drawFaceCircle()`, `drawFaceTextAtRC()` and `scrollFaceTextAtRC()` cross all 12 edges
- `DISPx_TARGET_REFRESH_HZ` (default 60) sets the refresh rate to aim for; a display that cannot reach it runs at its fastest rate and prints it
- `display.setBrightness()` and `display.getBrightness()` dim by lit time, so the image keeps its full color depth and refresh rate at any brightness
- Two MBI5124GP panels chain as one display; each chip's configuration register is written at start with its datasheet values
- `placeBMP(chain, file, rotation)` places an image of any size, turned by `bmp.ROT_NONE`, `bmp.ROT_RIGHT_90`, `bmp.ROT_LEFT_90` or `bmp.ROT_180`
- `drawCircle()` and `drawCircleOfColor()` draw circles
- `display.showFrameSet(pFrameSet)` shows a PWM frame set you built; it returns `display.E_FRAMESET_NULL` or `display.E_FRAMESET_FOREIGN` for an address it refuses
- **Identify screen**, `demo_hub75_numberPanels.spin2`, labels each panel with its cable position, panel position and arrow
- New demos: `demo_hub75_boundary.spin2`, `demo_hub75_quadPanel.spin2`, `demo_hub75_multi2x2panel.spin2`

### Improvements

- **Default color depth is 8-bit**, full 24-bit color; a configuration whose buffers do not fit hub RAM fails to compile
- **Drawing speed**: lines, boxes, circles, text, fills and BMPs are drawn from address tables built at startup, with the pixel writes in PASM
- **Scrolling** moves the region one place and draws only the new edge; a full-width text line steps in 1.3 ms sideways on the four-panel rig
- `commitScreenToPanelSet()` converts into the frame set not on display, so a commit never shows a mix of old and new image
- Panel timing is derived from the system clock and held to each chip's datasheet ratings ([ratings](DOCs/ChipCharacteristicsMatrix.md#datasheet-clock-and-oe-ratings))
- Buffers are sized by the panels in use, so an L-shaped display reserves no memory for its gap
- An adapter with no panels configured reserves no memory
- `fillScreenFromBMP()` returns `bmp.SUCCESS`, `bmp.E_BAD_ROTATION` or `bmp.E_BMP_NOT_24BIT`

### Bug Fixes

- With two or three adapters, each display shows its own image. Every display showed the first adapter's image; single-adapter programs were unaffected.
- `ROT_RIGHT_90` and `ROT_LEFT_90` on a non-square display draw inside it, and `maxDisplayColumns()` and `maxDisplayRows()` report the mounted size
- 3-, 4- and 5-bit color depths display correctly. 6-, 7- and 8-bit were unaffected.
- `releaseScroller(0)` releases the first scroller region
- A new scrolling region starts in the default loop mode; it no longer inherits `SCROLL_FOREVER` from a released region
- Text scrolling right with `SCROLL_ONCE_TO_CLEAR` scrolls until its region is clear, and a region wider than its text shows spaces before it
- Text scrolling sideways no longer draws a black column just right of its region
- `setColoredTextAtLnWithAlignPad()` with `ALIGN_RIGHT` places the whole padded field on the line, and `ALIGN_CENTER` pads both sides
- A 7-segment digit placed blank counts from 0 on its first increment
- `demo_hub75_7seg.spin2` on a display 32 columns wide or less keeps its text
- `demo_hub75_scroll.spin2` lays its scrollers out for the display's height; on 32 rows they no longer overlap
- `demo_hub75_multiPanel.spin2` spreads its panel colors around the whole color circle
- The refresh cog no longer pulses each adapter's R1, G1, B1 and R2 lines as timing marks
- The first start of an adapter no longer releases pin P0

### Breaking Changes

The [Update to v4.0 Checklist](Checklist-v3-v4.md) converts a v3.x program step by step.

- **BREAKING**: `DISPx_MAX_PANELS_PER_ROW` and `DISPx_MAX_PANELS_PER_COLUMN` are removed. Describe each panel in a wiring sentence, `DISPx_C0` to `DISPx_C15`; a v3.x `isp_hub75_hwPanelConfig.spin2` does not compile until converted.
- **BREAKING**: pin groups `PINS_P0_P15`, `PINS_P16_P31` and `PINS_P32_P47` are renamed `PIN_GROUP_P0_P15`, `PIN_GROUP_P16_P31` and `PIN_GROUP_P32_P47`, and `PINS_P48_P63` is removed. Update `DISPx_ADAPTER_BASE_PIN`; an old name does not compile.
- **BREAKING**: `display.start(display.HUB75_ADAPTER_1)` replaces the v3.x startup sequence. `hub75Bffrs.configure()`, `display.setBufferPointers()` and `chain0Ptrs()` to `chain2Ptrs()` are removed; your program no longer names the buffers object.
- **BREAKING**: `isp_hub75_hwBufferAccess.spin2` and `isp_hub75_hwBuffers.spin2` are never edited. Restore the release copies; a second or third adapter needs only its `DISP1_` or `DISP2_` settings.
- **BREAKING**: `DISPx_ROTATION` states how the display is mounted, and content is drawn upright as hung. A program that sets a rotation should re-check it on the panels.
- **BREAKING**: `panelsPerRow()`, `panelsPerColumn()`, `correctedColor()`, `correctedSingleColor()` and `colorAtDesiredBitWidth()` are removed from `isp_hub75_hwBufferAccess.spin2`, and `panelRotation()` is `displayRotation()`. Programs that draw through the display object need no change.
- **BREAKING**: `CLK_WIDE_PULSE` is removed; it had no effect. A config that ORs it onto `CHIP_MANUAL_SPEC` does not compile until it is taken out.
- **BREAKING**: panels must be a multiple of 4 columns wide (`DISPx_MAX_PANEL_COLUMNS`). Every common panel width is; any other stops startup with a message naming the setting.

### Performance

Measured on four ICN2037 128x64 panels (256x128 pixels) at 335 MHz, 8-bit color.

- Refresh: 71.0 Hz
- `commitScreenToPanelSet()`: 4.09 ms
- Flat fill / fanned lines / lines of text / 64x32 BMP: 4.7 / 13.0 / 24.6 / 3.8 ms

### Hardware Compatibility

- ICN2037 128x64, four panels in a 2x2: verified at every depth, 71.0 Hz at 8-bit to 193.3 Hz at 3-bit
- FM6126A 64x32: verified, 85.1 Hz at 8-bit
- FM6124 64x32: verified, 85.3 Hz at 8-bit
- MBI5124GP 64x32 (1/8 scan), two panels chained as 128x32: verified, 70.9 Hz at 8-bit
- MBI5124GP 64x32 (1/8 scan), single panel: 71.2 Hz at 8-bit

### Known Issues

- The ICN2038S scan setting is disputed: the driver sets `SCAN_4`, while its five address lines suggest 1/32 scan

## [3.0.1] 15 Jan 2024

### New chip support and new fonts

- Add support for panels using **DP5125D** chips
- Add Chips' 5x7 dithered fonts
- ICN2037_B was renamed to **ICN2038S** 
- MBI5124_8S was renamed to **MBI5124GP**
- Rearranged user configurable files in order to improve compilation under Pnut/Propeller Tool - This allows us to support many more total pixels (now 64k) in a display.

### Known Issues v3.0.1

- Multi-panel support for the MBI5124 driver chips is not yet working!
- The driver is now fast enough now that there are slight display issues with panels using the MBI5124 chips. We're looking into this.

## [2.0.0] 10 Nov 2022

### Multiple HUB75 card support

- Convert initialization: enable support for up to three hub75 cards!
- Rename demos (*now all start with demo_*)
- Add new demos: `demo_hub75_5x7font.spin2` and `demo_hub75_scroll.spin2`
- Upgrade scrolling, now supports scroll directions: `up, down, left, right`
- Added support for New Panel (*same chip as ICN2037 but slightly different setttings, new name is:* **ICN2037_B***: where colors are not swapped and scan is different*)
- Repo README's have been updated: *changed demo file names, changed how configuration is done*.


### Known Issues v2.0.0

- Multi-panel support for the FM6126A and MBI5124 driver chips is not yet working!
- The driver is now fast enough now that there are slight display issues with panels using the MBI5124 chips. We're looking into this.

## [1.0.0] 05 Apr 2022

### Better color presentation, 1/4 RAM usage

- Converted to new PWM generation mechanism allowing compile-time selection of desired display color depth of 3-bit to 8-bit/color (9 to 24bit RGB)
- Now uses 25% of RAM required by previous version for same 4-bit color depth. 
- Frees up ~300kB RAM for our P2 P2 Cube Application
- Latest timing and memory usage info posted.

![v1.x driver RAM usage](images/NewDriverRAMUse.png)

**NOTE** *SW0 means our older v0.x drivers, while SW1 means our new v1.x driver!*

### Known Issues v1.0.0

- Multi-panel support for the FM6126A and MBI5124 driver chips is not yet working!
- The driver is now fast enough now that there are slight display issues with panels using the MBI5124 chips. We're looking into this.

## [0.9.0] 2021-05-12

### The first release of P2 P2 Cube support

- The driver now works with multiple 64x64 panels using ICN_2037 Chips organized as 1 row. (The P2 P2 Cube is one row with top and bottom panels being the panels at either end of the row.)

### Known Issues v0.9.0

- Multi-panel support for the FM6126A and MBI5124 driver chips is not yet working!
- The driver is now fast enough now that there are slight display issues with panels using the MBI5124 chips. We're looking into this.

## [0.2.0] 2021-02-19

### Our first (limited) Multi-panel support

- Driver rebuilt to work with maximum display width of 1024 pixels.
- Driver now works with new 64x64 panel using ICN_2037 Chips
- Driver now works with display of 128x64 using twin 64x64 panels in series.
- Driver now supports 1/8 scan panels (**P4-1921-8S-V2.0**) using the MBI5124 driver chips

### Known Issues v0.2.0

- Multi-panel support for the FM6126A and MBI5124 driver chips is not yet working!


## [0.1.0] 2020-12-01

### Initial Release - Single Panel

- Single panel support working well, up to 2048 leds (64x32)
- PWM'ing images to achieve reasonable color
- Displaying text in both 5x7 and 8x8 fonts
- Initial version of scrolling text - will get more performant in future updates
- Basic color pixel placement at row, column
- Basic drawing primitives
- Loading and displaying images from .bmp files (that are identically sized to your panel)


## History: Progress heading toward initial release

**30 Nov 2020:** After being distracted by designing and sourcing the Eval Adapter boards I'm finally working on the driver once again.

- rundimentary scrolling text is now working
- multiple panel types are now supported (will add more as users identify the need)

**26 Nov 2020:** v1.4 PCB order placed for production run.

**16 Nov 2020:** v1.3 (green) PCB's arrived today these are better mechanical fit and have plated vias on the EVal board connectors.  This is a final form and function run before we go to production.

**20 Oct 2020:** I've made wonderful advances in this past week.

Things now working are:

- Loading and displaying images from .bmp files
- PWMing images to achieve reasonable color (initial draft)
- Displaying text in both 5x7 and 8x8 fonts

![Working 24-bit color](https://user-images.githubusercontent.com/540005/96498745-b4aa5700-1209-11eb-996d-6e3b6089b578.jpg)

Here you can see a demonstration of the 16-bit pwm color. Of course these panels are amazingly bright. I'm running here at ~50% brightness and it's still overwhelming the camera in a lighted room.


**27 Oct 2020:** More engineering and the (red) boards arrive!

This week I've been:

- Working to formally structure the code for release
- Studied gamma correction and now have a better performing table in place
- Studied PWM for the LEDs and now have a much more accurate PWM in place (colors are looking much better)
- Have been working on more tests, demos for animation rates of display
- More videos will be coming, meanwhile, have you seen these? [YouTube Playlist for Propeller Related Videos](https://www.youtube.com/playlist?list=PLkXxMjp58T0pk1dd8pH1OV7NCf-8Tbx1M)
- **Exciting!** The initial run of the Adapter PCBs arrived!
- I checked them out mechanically, soldered the parts to one, then checked it out electrically and lastly started using it!  It came up beautifully! (*See pictures and turn on description below*)
