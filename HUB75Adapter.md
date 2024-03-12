# HUB75e Adapter Board for the P2 Ecosystem

![Project Maintenance][maintenance-shield]

## Product Description

The P2 Eval HUB75 adapter board provides a simple means by which one can connect and drive a HUB75 RGB LED Matrix panel or a small number of HUB75 Matrix panels daisy-chained together.

### Overview

This  HUB75 add-on board (#65032) is designed for use with Propeller 2 development board 2×6 accessory headers. Its dual 2×6 pass-through sockets stack on top of a pair of accessory headers on the P2 Eval Board (64000). It is also compatible with a P2 Edge Module Breadboard (#64020) or P2 Edge Mini Breakout Board (#64019) with a P2 Edge Module (#P2-EC) installed.

### Features

- Provides 3.3v to 5v level shifting for all signals at the HUB75 Connector
- Supports HUB75 panels which use A-B-C, A-B-C-D and A-B-C-D-E Address lines
- Perfect for use with the [ISP HUB75 Driver](https://github.com/parallaxinc/propeller/tree/master/libraries/community/p2/All/isp_hub75_matrix) found in the P2 Object Exchange (OBEX)


### Specifications

- Voltage : +5 VDC (supplied by P2-ES Eval Board)
- Maximum clock rate : 70 MHz (limited by the level shifter I/Cs)  [*see note*]
- Form factor: dual 2×6-pin female passthrough headers with 0.1″ spacing
- PCB dimensions: 1.9 x 2.8 in (48 x 71 mm)

NOTE: *The I/Cs on this board were selected so that we can drive our panels as fast as they support. Hoever, our panels will likely require a much slower clock rate than this board can achieve. The maximum clock speeds for your panels will depend upon the actual chips they use.  Most of our panels are different and the manufacturers are constantly improving what the ship to us.*


## Downloads & Resources

### Downloads

- [Latest HUB75 driver build](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/releases) (GitHub release)
- [Hub75 Adapter Board v1.4 Schematic](images/hub75-adaptor-v1.4-schematic.pdf)

### Resource Links

- [Driver documentation & help with initial driver configuration](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/blob/main/THEOPS.md) (GitHub)
- [Use of the HUB75 v1.4 Optional Connectors](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/blob/main/HUB75-brd-config.md) (GitHub)
- [The driver project](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver) (GitHub)


----

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

----

## License

Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg

[releases-shield]: https://img.shields.io/github/release/ironsheep/p2-LED-Matrix-Driver.svg?style=for-the-badge

[releases]: https://github.com/ironsheep/p2-LED-Matrix-Driver/releases
