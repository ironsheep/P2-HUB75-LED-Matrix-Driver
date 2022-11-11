# CHECKLIST:</BR>Convert your code from v1.x to v2.x+

![Project Maintenance][maintenance-shield]

## Introduction

In the version 1.x driver your panel settings were all in one file **isp\_hub75_hwGeometry.spin2**. You chose a configuration that specified all compile-time constants. This file was adjacent to the other driver code files and compiled into it. 

In the new v2.x and later driver you have the same **isp\_hub75_hwGeometry.spin2** file but it now has fewer settings in it, which you still have to configure. But there is now a new 2nd file **isp\_hub75_hwBuffers.spin2** which the other settings moved to. This 2nd file is named hwBuffers because this driver now support multiple HUB75 cards so buffer space (which must be compile-time allocated) has to be set up for each of the HUB75 cards you wish to support. Your work in this file has you selecting constant values once again but you also potentially have to uncomment some of the table entry and buffer allocations as well.

Let's look at making these changes and also the new form of startup the v2.x driver uses (it's much more like starting normal device object now, as you'll see.

## Step by Step

### Configure Compile-time Settings

The file **isp\_hub75_hwGeometry.spin2** needs to be adjusted to support your panel hardware.

Example v1.x form:

```python
    ADAPTER_BASE_PIN = PINS_P16_P31
    ' (1) determine what form of signalling the driver should use
    PANEL_DRIVER_CHIP = CHIP_FM6126A

    ' (2) describe the panel electrical layout
    MAX_PANEL_COLUMNS = 64
    MAX_PANEL_ROWS = 32
    PANEL_ADDR_LINES = ADDR_ABCD

    ' (3) describe the organization of panel(s)
    ' panels organization: visual layout
    '   [1][2]

    ' (4) describe the organization in numbers of panels
    MAX_PANELS_PER_ROW = 2
    MAX_PANELS_PER_COLUMN = 1

    ' (5) describe the color depth you want to support [3-8] bits per LED
    '    NOTE full 24bit color is DEPTH_8BIT
    COLOR_DEPTH = DEPTH_8BIT
```

Example v2.x form (single HUB75 adapter):

```python
    ADAPTER_BASE_PIN = hwEnum.PINs_P16_P31

   ' (1) determine what form of signalling the driver should use
    PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    PANEL_ADDR_LINES = hwEnum.ADDR_ABCD

    ' The visual organization of panel(s)
    '   [1][2]     ' one row of 2 panels
```

**NOTE** in order to reduce compile-time complexity the named constants you select from to assign are all moved into **isp\_hub75_hwEnums.spin2** The two files you are editing already have this Enums file specified as an object named `hwEnum` which is why you see these value names prefixed with `hwEnum.`

### Configure Run-time Settings

The file **isp\_hub75_hwBuffers.spin2** needs to be adjusted to support each of your HUB75 cards with a chain of 1 or more panels attached to each card. 

**NOTE:** All panels in a chain (all connected to same HUB75 card) must have the SAME hardware driver chips.

Since this file didn't exist in v1.x we are only showing an example for v2.x:

```python
    ' /-------------------------------------------
    ' |  User configure

    ' (1) describe the panel electrical layout
    DISP0_MAX_PANEL_COLUMNS = 64
    DISP0_MAX_PANEL_ROWS = 64

    ' (2) describe the organization of panel(s)
    ' panels organization: visual layout
    '   [1][2]      1 row of 2 panels
    '
    DISP0_MAX_PANELS_PER_ROW = 2
    DISP0_MAX_PANELS_PER_COLUMN = 1

    ' (3) describe the color depth you want to support [3-8] bits per LED
    '    NOTE full 24bit color is DEPTH_8BIT
    DISP0_COLOR_DEPTH = hwEnum.DEPTH_6BIT

    ' |  End User configure
    ' \-------------------------------------------
```

**NOTE** Notice the use of value names prefixed with `hwEnum.` in this file too.

### Use New form of Start up code

Example v1.x start up:

```python
OBJ

    display     : "isp_hub75_display"
    
PUB ...()

    ok := cog := display.start()   ' awaken the LED matrix driver

```

Example v2.x start up (single hub75 card):

```python
OBJ

    display     :   "isp_hub75_display"
    hub75Bffrs  :   "isp_hub75_hwBuffers"   ' run-time hardware config
    user        :   "isp_hub75_hwGeometry"  ' compile-time hardware config
    
PUB ...()

    hub75Bffrs.configure(hub75Bffrs.HUB75_ADAPTER_1, user.ADAPTER_BASE_PIN, user.PANEL_DRIVER_CHIP, user.PANEL_ADDR_LINES)
    chainIndex := hub75Bffrs.indexForHub75ChainId(hub75Bffrs.HUB75_ADAPTER_1)

    ' startup our backend COG(s)
    ok := cog := display.start(chainIndex)   ' send buffer to driver

```

Example v2.x start up (two hub75 cards):

In **isp\_hub75_hwGeometry.spin2**::

```python
    ' Constants for Panels connection to 1st HUB75 card (nickname FRONT_)
    FRONT_ADAPTER_BASE_PIN = hwEnum.PINs_P16_P31

   ' (1) determine what form of signalling the driver should use
    FRONT_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    FRONT_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD

    ' The visual organization of panel(s)
    '   [1][2]     ' one row of 2 panels (our cube is electrically 1 row)
    
    ' Constants for Panels connection to 2nd HUB75 card (nickname BACK_)    	 BACK_ADAPTER_BASE_PIN = hwEnum.PINs_P0_P15

   ' (1) determine what form of signalling the driver should use
    BACK_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037_B
    BACK_PANEL_ADDR_LINES = hwEnum.ADDR_ABCDE

    ' The visual organization of panel(s)
    '   [1][1]     ' one row of 1 panel (our cube is electrically 1 row)
```

In **top-level-file**:

```python
OBJ

    display[2]  :   "isp_hub75_display"
    hub75Bffrs  :   "isp_hub75_hwBuffers"   ' run-time hardware config
    user        :   "isp_hub75_hwGeometry"  ' compile-time hardware config
 
CON
	' which chain is connected to which pin-group
    HUB75_FRONT_PANEL = hub75Bffrs.HUB75_ADAPTER_1
    HUB75_BACK_PANEL = hub75Bffrs.HUB75_ADAPTER_2
    
    ' which display instance do we want to call FRONT and BACK
    FRONT_PANEL = 0
    BACK_PANEL = 1
    
PUB ...() | frontPanelIdx, backPanelIdx

    hub75Bffrs.configure(HUB75_FRONT_PANEL, user.FRONT_ADAPTER_BASE_PIN, user.FRONT_PANEL_DRIVER_CHIP, user.FRONT_PANEL_ADDR_LINES)
    hub75Bffrs.configure(HUB75_BACK_PANEL, user.BACK_ADAPTER_BASE_PIN,  user.BACK_PANEL_DRIVER_CHIP, user.BACK_PANEL_ADDR_LINES)

    frontPanelIdx := hub75Bffrs.indexForHub75ChainId(HUB75_FRONT_PANEL)
    backPanelIdx := hub75Bffrs.indexForHub75ChainId(HUB75_BACK_PANEL)

    ' startup our backend COG(s)
    ok := cog := display.start(0, frontPanelIdx)   ' send buffer to driver
    ok := cog := display.start(1, backPanelIdx)   ' send buffer to driver
    
    ' NOTE with multiple hub75 cards all your display.method() calls must 
    '  now be display[FRONT_PANEL].method() or display[BACK_PANEL].method() calls.

```

### Writing display code for your panels

Now that your driver is configured and you've started the driver (or drivers) the rest of the single HUB75 card display code is pretty much the same. Your existing code shouldn't change.

Of course, if when you decide to activate two or three HUB75 cards then you'll be selecting from 2-3 display object instances as shown in the "two hub75 cards" example above.

That's it. If you've followed along and updated the two files with specifics that describe your panels and you've adjusted your top-level file to start the driver in the new way then you are good to go!

I hope you continue to enjoy using this driver. As always please feel free to report issues or discuss how you are using the driver in our Matrix driver thread [P2 Driver for HUB75 LED Matrix Panels](https://forums.parallax.com/discussion/172288/p2-driver-for-hub75-led-matrix-panels#latest). You can also file BUG reports or feature requests at the driver repository [Issues Page](https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/issues).

*See you in the Parallax Forums and on our P2 Live Forums!*

*-Stephen*

----

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

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

[releases]: https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/releases
