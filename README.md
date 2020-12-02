# HUB75 LED Matrix Driver for Propeller 2

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

[![GitHub Release][releases-shield]][releases]

**<= This is a work in progress =>**

**This P2 HUB75 driver is built to work with the P2 Eval HUB75 Adapter which will soon be available from [Parallax.com Store](https://www.parallax.com/product-category/propeller-2/)**

The P2 HUB75 Driver is available from a couple of sources:

- [The P2 Object Exchange](https://github.com/parallaxinc/propeller/tree/master/libraries/community/p2) as "ISP HUB75 Matrix"
- From this repository from the [Releases page](https://github.com/ironsheep/p2-LED-Matrix-Driver/releases)

## Additional Documents

- This README has been repurposed to reflect the current state of the driver as currently released
- Moved initial readme content to the [HardwareTurnon](HardwareTurnon.md) document
- Added the [Driver Details](THEOPS.md) document to provide more detail about the driver and driver-configuration
- Added a [Change Log](ChangeLog.md) to capture notes about each release of the dirver

## Current Project state

What's working today with the current driver:

- Single panel support working well, up to 2048 leds (64x32)
- PWM'ing images to achieve reasonable color
- Displaying text in both 5x7 and 8x8 fonts
- Initial version of scrolling text - will get more performant in future updates (right to left scroll only)
- Basic color pixel placement at row, column
- Basic drawing primitives
- Loading and displaying images from .bmp files (that are identically sized to your panel)

**NOTE:** *With every update we post we also update the [ChangeLog](ChangeLog.md). It will have the most up-to-date driver code/feature status.*


## Driver Setup and Configuration

Once you haave the driver downloaded and the source files added to your project you will first need to configure the driver by modifying the following values in the file **isp\_hub75_hwGeometry.spin2**:

| Name            | Default | Description |
|-----------------|-------------|-------------|
| `ADAPTER_BASE_PIN` | PINS\_P16_P31 |  Identify which pin-group your HUB75 board is connected |
| `PANEL_DRIVER_CHIP` | CHIP_UNKNOWN | in most cases UNKNOWN will work. Some specialized panels need a specific driver chip (e.g., those using the FM6126A) |
| `MAX_PANEL_COLUMNS` | {none} | The number of LEDs in each row of your panel ( # pixels-wide) |
| `MAX_PANEL_ROWS` | {none} | The number of LEDs in each column of your panel ( # pixels-high) |

*The easiest way to do this would be to find an example configuration in that file, copy it and modify it to describe your hardware set up. Makgin sure, of course that the others are commented out.*

Once we support multiple panels then the following will also have to be configured:

| Name            | Default | Description |
|-----------------|-------------|-------------|
| `MAX_PANELS` | 1 | **NOTE:** Currently only 1 in supported in the initial release |
| `MAX_DISPLAY_COLUMNS` | {none} | The number of LEDs in each row of your multi-panel display |
| `MAX_DISPLAY_ROWS` | {none} | The number of LEDs in each column of your multi-panel display |

**NOTE:** once we get to multi-panel display there may also be configuration values for decribing the organization of the panels in more detail than the above setting describe.  We'll see...

Once these values are set correctly, according to your own hardware set up, then you should be able to compile your code and run.

More detail can be found in [Driver Introduction & Configuration](THEOPS.md)

## Writing display code for your panels

As soon are you are configured you will want to make pixels light up on your panel(s)!

There are a couple of demos which you can review then copy and paste from.  These are:

| DEMO Program    |  Purpose |
|-----------------|-------------|
| isp\_hub75_demoColor.spin2 | presents the color features of the panel driver, displays a .bmp file |
| isp\_hub75_demoText.spin2 | presents the text and scrolling features of the panel driver |
| isp\_hub75_demo7seg.spin2 | presents a technique for doing multi-step animations using the panel driver |

**NOTE:** these demo's are built for a 64x32 panel. You may have to modify them to run on your panel.

Once you have a sense for what these demo's do and how, writing your own display code should be very easy and initially maybe even a copy-n-paste effort from the demo source to your own display code.

Please enjoy and let me know if there are features you want to see in this driver!


## BACKGROUND: HUB75 RGB LED Matrix Panels

There are many RGB LED matrices available. This driver is built specifically for **HUB75** driven matrices which are usually found in sizes ranging from 16x16 to 64x64 and ranging in horizontal/vertical spacing form 1.5mm (P1.5) to 8mm (P8) between individual LEDs.  The version I'm developing with is actually a P3 64x32 Matrix which I originally bought from Amazon. The specific ones I'm using are no longer avail. but the are many others.  

Example 32x64 panels:

- [Sparkfun 64x32 P4](https://www.sparkfun.com/products/14718) 
- [Adafruit 64x32 P3](https://www.adafruit.com/product/2279)
- [Adafruit - flexible 64x32 P4](https://www.adafruit.com/product/3826)
- [Amazon - flexible 64x32 P4](https://www.amazon.com/Digital-Flexible-Special-P4-256x128mm-RGB-Full/dp/B07F87CM6Y)
- [Amazon 64x32 P5](https://www.amazon.com/Pixels-Indoor-SMD2121-320x160mm-320160mm/dp/B07SDMWX9R)
- [Amazon 64x32 P4](https://www.amazon.com/NovaeLED-Display-100000hrs-Bright-Colored-Picture/dp/B07LFJD5GY) good price for two identical panels

These panels expect to receive six lines of serial color data, a clock signal indicating when to latch the color data, a latch signal indicating that a whole rows of color data should be sent to the LEDs,a set of address lines (A, B, C, and D) identifying which row should be displayed and an output-enable signal causing an addressed row of LEDs to be driven.

While the 64x32 Matrices all appear to be similar the manufacturing of them has been rapid and varied. For us this means that a HUB75 panel can have very different Integrated Circuits (ICs) on the panel driving the LEDs. With these IC changes comes the need alter the signals sent to the panels so that the ICs your panel uses understands the input signals.

In general i'm finding so far that there are 3 or 4 commmon choices for ICs used on the panels. One GitHub user **Piotr Esden-Tempski**  offers  doc's for some of the panels [esden/led-panel-docs](https://github.com/esden/led-panel-docs) showing images of the panels, schematics and datasheets for the ICs used on the panel. (*I'm planning on contributing my schematic and various finds to his repo as a Pull request before this project is completed.*) There are many more that he does not have but this is a good reference.

![Hub75 Panels](images/example-panels.png)

**Example Panels** backside of 64x32 p3 and 64x64 p2 panels with cables for power and data.

## ## BACKGROUND: Project goals

Overall: Let's see what performance we can achieve by driving from the Propeller 2 directly! 

But let's be more specific:

| Goal               | Sub-goal  | Description |
| ------------------ | --------- | ----------------------------------------------------------------------- |
| Video Frame Rates  | -  | Better than 30fps of gamma corrected 24bit color frames for at least 2x2 64x32 LED panels |
| Understand system demand | -  | Study overall system performance so we know how this will behave with various peripherals and panel configurations |
| - | Use P2 internal ram resources|  Study driver use of COG Registers, LUT RAM, and HUB RAM |
| - | w/P2 Eval HyperRAM  |  Will we need, can we benefit from using HyperRAM / External RAM? |
| - | w/uSD Storage  | What is our performace displaying images / video directly from the P2 uSD card? |
| - | w/Receiving image data from RPi  | Is the RPi SPI interface sufficient to keep our panels streaming video? |
| Reusable Driver | - | Ensure driver can be configured for (1) single panel size, (2) organization of multi-panel chains, and (3) the various panel chip-sets which require different clocking styles (within practical limits: *all panels must use the same chip-set*) |
| long-term | - | Can we drive multiple panel chains - we have 64 GPIO pins on the P2... we should easily be able to connect 3 HUB75 adapters. Can we drive them all at video frame rates?  What is our limitation here? |

**NOTE:** Initial turn-on of the pasm2 driver code (1st draft reasonably performant code, not the fastest possible) shows that I'm getting a 1000fps rate with 3 bit color.  This will be derated by PWM especially as we get a much better PWM in place more usefully handling brightness control.

Remember, this is without yet tuning the driver for best performance based on what the chip can do.  Based on the limits of the panel chipset, for the panels on this project, I should be able to drive the panel itself faster than I am in the 1st draft code.  So, there's room to get better here.

----

If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep)

----

## Credits

- I was encouraged by published work by **Rayman** (found on the [Parallax Forums](https://forums.parallax.com/categories/propeller-2-multicore-microcontroller)) where he wrote initial propeller v1 spin/pasm code to demonstrate how to drive his matrix panel. I found [the article](http://www.rayslogic.com/propeller/Programming/AdafruitRGB/AdafruitRGB.htm) linked to from the AdaFruit website.

## License

Copyright © 2020 Iron Sheep Productions, LLC. All rights reserved.<br />
Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-S%20M%20Moraco%20%40ironsheepbiz-blue.svg?style=for-the-badge

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765

[releases-shield]: https://img.shields.io/github/release/ironsheep/p2-LED-Matrix-Driver.svg?style=for-the-badge

[releases]: https://github.com/ironsheep/p2-LED-Matrix-Driver/releases
