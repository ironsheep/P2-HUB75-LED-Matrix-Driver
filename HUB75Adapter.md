# HUB75e Adapter Board for the P2 Ecosystem

![Project Maintenance][maintenance-shield]

## Product Description

The P2 Eval HUB75 adapter board provides a simple means by which one can connect and drive a HUB75 RGB LED Matrix panel or a small number of HUB75 Matrix panels daisy-chained together.

### Ovieview

This  HUB75 add-on board (#65032) is designed for use with Propeller 2 development board 2×6 accessory headers. Its dual 2×6 pass-through sockets stack on top of a pair of accessory headers on the P2 Eval Board (64000). It is also compatible with a P2 Edge Module Breadboard (#64020) or P2 Edge Mini Breakout Board (#64019) with a P2 Edge Module (#P2-EC) installed.

### Features

- Provides 3.3v to 5V level shifting for all signals at the HUB75 Connector
- Supports HUB75 panels which use A-B-C, A-B-C-D and A-B-C-D-E Address lines
- Perfect for use with the [ISP HUB75 Driver](https://github.com/parallaxinc/propeller/tree/master/libraries/community/p2/All/isp_hub75_matrix) found in the P2 Object Exchange (OBEX)


### Specifications

- Voltage : +3.3 VDC (supplied by P2-ES Eval Board)
- Voltage : +5 VDC (supplied by P2-ES Eval Board)
- Maximum clock rate : 30 MHz (200 MB/s, limited by the level shifter I/Cs)
- Form factor: dual 2×6-pin female passthrough headers with 0.1″ spacing
- PCB dimensions: 1.9 x 2.8 in (48 x 71 mm)


## Downloads & Resources

### Downloads

- [Latest HUB75 driver build](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/releases) (GitHub release)
- [Hub75 Adapter Board v1.4 Schematic](images/hub75-adaptor-v1.4-schematic.pdf)

### Resource Links

- [Driver documentation & help with initial driver configuration](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/blob/main/THEOPS.md) (GitHub)
- [Use of the HUB75 v1.4 Optional Connectors](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver/blob/main/HUB75-brd-config.md) (GitHub)
- [The driver project](https://github.com/ironsheep/p2-HUB75-LED-Matrix-Driver) (GitHub)


----

If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep)

----

## License

Copyright © 2020 Iron Sheep Productions, LLC. All rights reserved.<br />
Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765

[releases-shield]: https://img.shields.io/github/release/ironsheep/p2-LED-Matrix-Driver.svg?style=for-the-badge

[releases]: https://github.com/ironsheep/p2-LED-Matrix-Driver/releases
