# HUB75 LED Matrix Driver for Propeller 2

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

[![GitHub Release][releases-shield]][releases]

**<= This is a work in progress =>**

There are many RGB LED matrices available. This drivers is built specifically for [HUB75]() driven matrices which are usually found in sizes ranging from 16x16 to 64x64 and ranging in horizontal/vertical spacing form 2mm (P2) to 8mm (P8) between individual LEDs.  The version i'm developing with is actually a P3 64x32 Matrix which I originally bought from Amazon. The specific ones I'm using are no longer avail. but the are many others.  

Example 32x64 panels:

- [Sparkfun 64x32 P4](https://www.sparkfun.com/products/14718) 
- [Adafruit 64x32 P3](https://www.adafruit.com/product/2279)
- [Adafruit - flexible 64x32 P4](https://www.adafruit.com/product/3826)
- [Amazon - flexible 64x32 P4](https://www.amazon.com/Digital-Flexible-Special-P4-256x128mm-RGB-Full/dp/B07F87CM6Y)
- [Amazon 64x32 P5](https://www.amazon.com/Pixels-Indoor-SMD2121-320x160mm-320160mm/dp/B07SDMWX9R)
- [Amazon 64x32 P4](https://www.amazon.com/NovaeLED-Display-100000hrs-Bright-Colored-Picture/dp/B07LFJD5GY) good price for two identical panels

These panels are receive serial data, clock signal signalling when to latch the data bits, a latch signal signalling that a whole rows of data should be sent to the LEDs a set of address lines (A, B, C, and D) idenitfying which row should be displayed and an output-enable signal causing an addressed row LEDs to be driven.

While the 64x32 Matrices all appear to be similar the manufacturing of them has been rapid and varied. For us this means that a HUB75 panel can have very different Integrated Circuits (ICs) on the panel driving the LEDs. With these IC changes comes the need alter the signals sent to the panels so that the ICs your panel uses understands the input signals.

In general i'm finding so far that there are 3 or 4 commmon choices for ICs used on the panels. One GitHub user "Piotr Esden-Tempski"  offers  doc's for some of the panels [esden/led-panel-docs](https://github.com/esden/led-panel-docs) showing images of the panels, schematics and datasheets for the ICs used on the panel. (*I'm planning on contributing my schematic and various finds to his repo as a Pull request before this project is completed.*) There are many more that he does not have but this is a good reference.


## My Panel

The panels I'm using are marked with **P3-6432-121-16s-D1.0**  Which tell us that it is 64w x 32h (6432) and 16 addressed lines (16s).  This board uses FM6126A driver chips and TC7258EN chips for line address decoding. Lastly is uses 74HC245s to buffer the incoming signals and forward them to the output conector.  The FM6126A requires that we latch the data very differently in that instead of latching after the stream of bits for a line, we set the latch during the last 3 bits of each line. (per the Datasheet)  Additionally, the FM6126A requires initialization of two registers before it runs as a normal panel. This was quite the discovery as the Chinese Datasheet says the two registers exist but doesn't provide detail. Finding details and implementing the initialization was an effort of blending what I saw in posts which showed various forms of coce and other posts describing their reverse engineering of the same effort. But, it's all working, so I'm past this!

![MyPanel](https://user-images.githubusercontent.com/540005/96038418-53a70b80-0e24-11eb-93fe-7af0301d349e.jpg)

## Current Project state

I've made wonderful advances in this past week.

Things now working are:

- Loading and displaying images from .bmp files
- PWMing images to achieve 24-bit color
- Displaying text in both 5x7 and 8x8 fonts

![Working 24-bit color](https://user-images.githubusercontent.com/540005/96498745-b4aa5700-1209-11eb-996d-6e3b6089b578.jpg)

Here you can see a demonstration of the 24bit color. Of course these panels are amazingly bright. I'm running here at ~50% brightness and it's still overwhelming the camera in a lighted room.

Up next: 

- Rapid display of sequences of frames.
- This will be for drawing animations, scrolling text, and even display of video when we get that far.
- I've even some fun animated clocks coming (sorry, I'm been doing software clocks of many, many, forms for a long time.)

## Development Environment

Here we see my P2 Eval board with flying leads going to a splitter board I hand made so I can feed the panel and watch the signals with a Logic Analyzer.

![WorkBench](https://user-images.githubusercontent.com/540005/96038234-13478d80-0e24-11eb-9f1e-623a94d56024.jpg)

## Project goals

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

**NOTE:** Initial turn-on of the pasm2 driver code (1st draft reasonably performant code, not the fastest possible) shows that I'm getting a 400fps rate with 3 bit color.  So far this means that before tuning we might be able to get 50fps of 24bit color for single panel.  For a 4x4 panel this means we might get 12.5fps to 33fps depending upon our color depth.  

Remember, this is without yet tuning the driver for best performance based on what the chip can do.  Based on the limits of the panel chipset, for the panels on this project, I should be able to drive the panel itself around 1.7x faster than I am in the 1st draft code.  So, there's room to get better here.


### Next Environment Upgrade

Since the project goals are going to be speed related, I'm going to need a better than flying leads to get to my higher speeds... so I'm building this Eval Adapter board:

![P2 Eval Adapter](https://user-images.githubusercontent.com/540005/96038186-062a9e80-0e24-11eb-8299-f5e8fcb03460.png)

On this board you see 3.3v to 5v level shifters. I found that at higher speeds the clock, latch and OEb signals were falling below the signal threshold. This was a great exercise in Logic Analyzer use as I had originally set my input thresholds for 3.3v signals and of course they looked perfectly timed.  When I couldn't get reliable shifting and latching a had the thought that I'm dealing with 5v logic on the panels. Silly me, I had the LA configured for the output logic form, not the panel form of signal. So I switched to 5v threshold and then immediately saw that I was not at all clocking cleanly. quickly interposed the level shifer pcb that I had laying around and all the signals snapped to, as I really needed to see!  I was back in the land of the code I write now drives the signals I expect...  whew!

## Up Next, Cascaded Panels

The next panel configuration i'm planning on playting with is daisy-chaining 4 of these panels so I can play with larger images. Here you see three more panels waiting for the fourth to be moved from the bench to join them.

![2x2 Panels Daisy-Chained](https://user-images.githubusercontent.com/540005/96038541-818c5000-0e24-11eb-8789-b1d77364fd7d.jpg)

## Credits

- I was encouraged by published work by **Rayman** (found on the [Parallax Forumns](https://forums.parallax.com/categories/propeller-2-multicore-microcontroller)) where he wrote initial propeller v1 spin/pasm code to demonstrate how to drive his matrix panel. I found the article linked to from the AdaFruit website I think.  When I run accross it again, I'll add the link here.

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
