# p2 LED Matrix Driver

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

[![GitHub Release][releases-shield]][releases]

There are many RGB LED matrices available. This drivers is built specifically for [HUB75]() driven matrices which are usually found in sizes ranging from 16x16 to 64x64 and ranging in horizontal/vertical spacing form 2mm (P2) to 8mm (P8) between individual LEDs.  The version i'm testing with is actually a P3 64x32 Matrix which I originally bought from Amazon. The specific ones I'm using are no longer avail. but the are many others.  

Example 32x64 panels:

- [Sparkfun 64x32 P4](https://www.sparkfun.com/products/14718) 
- [Adafruit 64x32 P3](https://www.adafruit.com/product/2279)
- [Adafruit - flexible 64x32 P4](https://www.adafruit.com/product/3826)
- [Amazon - flexible 64x32 P4](https://www.amazon.com/Digital-Flexible-Special-P4-256x128mm-RGB-Full/dp/B07F87CM6Y)
- [Amazon 64x32 P5](https://www.amazon.com/Pixels-Indoor-SMD2121-320x160mm-320160mm/dp/B07SDMWX9R)
- [Amazon 64x32 P4](https://www.amazon.com/NovaeLED-Display-100000hrs-Bright-Colored-Picture/dp/B07LFJD5GY) good price for two identical panels

These panels are receive serial data, clock signal signalling when to latch the data bits, a latch signal signalling that a whole rows of data should be sent to the LEDs a set of address lines (A, B, C, and D) idenitfying which row should be displayed and an output-enable signal causing an addressed row LEDs to be driven.

While the 64x32 Matrixes all appear to be similar the manufacturing of them has been rapid and varied. For us this means that a HUB75 panel can have very different Integrated Circuits (ICs) on the panel driving the LEDs. With these IC changes comes the need alter the signals sent to the panels so that the ICs your panel uses understands the input signals.

In general i'm finding so far that there are 3 or 4 commmon choices for ICs used on the panels. One GitHub user "Piotr Esden-Tempski"  offers  doc's for some of the panels [esden/led-panel-docs](https://github.com/esden/led-panel-docs) showing images of the panels, schematics and datasheets for the ICs used on the panel.  There are many more that he does not have but this is a good reference.

## My Panel

![MyPanel](https://user-images.githubusercontent.com/540005/96038418-53a70b80-0e24-11eb-93fe-7af0301d349e.jpg)

## Development Environment

![WorkBench](https://user-images.githubusercontent.com/540005/96038234-13478d80-0e24-11eb-9f1e-623a94d56024.jpg)

### Next Environment Upgrade

![P2 Eval Adapter](https://user-images.githubusercontent.com/540005/96038186-062a9e80-0e24-11eb-8299-f5e8fcb03460.png)

## Up Next, Cascaded Panels

![2x2 Panels Daisy-Chained](https://user-images.githubusercontent.com/540005/96038541-818c5000-0e24-11eb-8789-b1d77364fd7d.jpg)

## Credits

- TBA

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
