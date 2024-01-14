# CHECKLIST:</BR>Convert your code from v1.x to v2.x+

![Project Maintenance][maintenance-shield]

## Introduction

In the v2.x driver you have the **isp\_hub75_hwGeometry.spin2** file which you have to configure. And there was a 2nd file **isp\_hub75_hwBuffers.spin2** which contained the remaining settings. This 2nd file is named hwBuffers because this driver supports multiple HUB75 cards so buffer space (which must be compile-time allocated) has to be set up for each of the HUB75 cards you wish to support. Your work in this file had you selecting constant values once again but you also potentially had to uncomment some of the table entry and buffer allocations as well.

In the v3.x driver the file **isp\_hub75_hwGeometry.spin2** became **demo\_hub75_hwGeometry.spin2** snice it only informs the demo's about your hardware. You still modify it the same way.

The file **isp\_hub75_hwBuffers.spin2** has been split into three files with some of the content moving into **isp\_hub75_hwBufferAccess.spin2** and also **isp\_hub75_hwPanelConfig.spin2**.

This also simplifies what you have to modify. You adjust constant values in **isp\_hub75_hwPanelConfig.spin2** for each of your hub75 adapters you'll be using. In the remaining two files **isp\_hub75_hwBufferAccess.spin2** and **isp\_hub75_hwBuffers.spin2**, you simply comment-out or uncomment the code assiciated with each of the HUB75 adapters you'll be using. One is uncommented in both files by default. If you are only using one adapter then there is nothing for you to do with these files! If you are using two or three then you need to uncomment code for those adapters to be compiled-in.  The for the following at the top of each of these two files:

```python
' -----------------
' User Setup Notes:
' -----------------
'   There are three areas in this file that need adjustment to the number of hub75 
'    adapter boards you are using.
'
'   This file has ONE adapter board enabled by default.  If you are using more than one 
'    adapter board, you will need to uncomment  sections for each additional adapter board 
'    you wish to use.
'
'   The lines containing the text "2nd HUB75 adapter board" are lines which set up the
'    2nd adapter board.
'   The lines containing the text "3rd HUB75 adapter board" are lines which set up the
'    3rd adapter board.
```

Let's look at making these changes and also the making the small adjustment we need wheb starting up the new v3.x driver.

## Step by Step

### Configure Compile-time Settings DEMOs

The file **demo\_hub75_hwGeometry.spin2** needs to be adjusted to support your panel hardware.

Example v3.x form (single HUB75 adapter):

```python
    ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31

   ' (1) determine what form of signalling the driver should use
    PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    PANEL_ADDR_LINES = hwEnum.ADDR_ABCD

    ' The visual organization of panel(s)
    '   [1][2]     ' one row of 2 panels
```

### Configure Compile-time Settings - panels attached

The file **isp\_hub75_hwPanelConfig.spin2** needs to be adjusted to support each of your HUB75 cards with a chain of 1 or more panels attached to each card. 

**NOTE:** All panels in a chain (all connected to same HUB75 card) must have the SAME hardware driver chips.

```python
    ' /-------------------------------------------
    ' |  User configure        PROPOSAL!!!

    ' (1) describe the panel connections, addressing and chips
    DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
    
    ' (2) describe the single panel physical size
    DISP0_MAX_PANEL_COLUMNS = 128
    DISP0_MAX_PANEL_ROWS = 64

    ' the organization of the panels: visual layout
    '   [1]      1 row of 1 panel
    '
    DISP0_MAX_PANELS_PER_ROW = 1
    DISP0_MAX_PANELS_PER_COLUMN = 1

    ' (3) describe the color depth you want to support [3-8] bits per LED
    '    NOTE full 24bit color is hwEnum.DEPTH_8BIT
    ' .  NOTE: 3-5 bit depth is 2 bytes per pixel, while 6-8 bit depth is 3 bytes per pixel
    DISP0_COLOR_DEPTH = hwEnum.DEPTH_5BIT

    ' (4) Apply desired rotation to entire display
    DISP0_ROTATION = hwEnum.ROT_NONE

    ' |  End User configure
    ' \-------------------------------------------
    
    .
    .  - there are two more sections below here: 
    .    DISP1_* for the 2nd HUB75 chain
    .    DISP2_* for the 3rd HUB75 chain
    .
```

**NOTE** Notice the use of value names prefixed with `hwEnum.` in this file too.

### Adjust the Start up code

Example v3.x start up (two hub75 cards):

In **isp\_hub75_hwBufferAccess.spin2**::

We make sure that the code for the first two adapters is uncommented. The first was already, we actively followed the instructions at the top of the file to uncomment the code in three places for the 2nd adapter.

In **isp\_hub75_hwBuffers.spin2**::

Same as we just did in the previous file, we make sure that the code for the first two adapters is uncommented. The first was already, we actively followed the instructions at the top of the file to uncomment the code in three places for the 2nd adapter.

In **isp\_hub75_hwPanelConfig.spin2**::

```python
    ' Constants for Panels connection to 1st HUB75 card (nickname FRONT_)
    ' /-------------------------------------------
    ' |  User configure

    ' (1) describe the panel connections, addressing and chips
    DISP0_ADAPTER_BASE_PIN = hwEnum.PINS_P16_P31
    DISP0_PANEL_DRIVER_CHIP = hwEnum.CHIP_FM6126A
    DISP0_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
  
    ' (2) describe the single panel physical size
    DISP0_MAX_PANEL_COLUMNS = 64
    DISP0_MAX_PANEL_ROWS = 64

    ' the organization of the panels: visual layout
    '   [1][1]      1 row of 2 panels (128x64 rectangular display)
    '
    DISP0_MAX_PANELS_PER_ROW = 2
    DISP0_MAX_PANELS_PER_COLUMN = 1

    ' (3) describe the color depth you want to support [3-8] bits per LED
    '    NOTE full 24bit color is DEPTH_8BIT
    DISP0_COLOR_DEPTH = hwEnum.DEPTH_6BIT

    ' (4) Apply desired rotation to entire display
    DISP0_ROTATION = hwEnum.ROT_NONE
    
    ' |  End User configure
    ' \-------------------------------------------
    
    ' Constants for Panels connection to 2nd HUB75 card (nickname DISP1_) 
    ' /-------------------------------------------
    ' |  User configure

    ' (1) describe the panel connections, addressing and chips
    DISP1_ADAPTER_BASE_PIN = hwEnum.PINS_P0_P15
    DISP1_PANEL_DRIVER_CHIP = hwEnum.CHIP_ICN2037
    DISP1_PANEL_ADDR_LINES = hwEnum.ADDR_ABCD
  
    ' (2) describe the single panel physical size
    DISP1_MAX_PANEL_COLUMNS = 128
    DISP1_MAX_PANEL_ROWS = 64

    ' the organization of the panels: visual layout
    '   [1]      1 col of 2 panels (128x128 pixel square display)
    '   [1]     
    '
    DISP1_MAX_PANELS_PER_ROW = 1
    DISP1_MAX_PANELS_PER_COLUMN = 2

    ' (3) describe the color depth you want to support [3-8] bits per LED
    '    NOTE full 24bit color is DEPTH_8BIT
    DISP1_COLOR_DEPTH = hwEnum.DEPTH_6BIT

    ' (4) Apply desired rotation to entire display
    DISP1_ROTATION = hwEnum.ROT_NONE
    
    ' |  End User configure
    ' \-------------------------------------------
```

In the project **top-level-file**:

```python
OBJ

    display[2]  :   "isp_hub75_display".       ' a display object for ea. adapter
    hub75Bffrs  :   "isp_hub75_hwBuffers"      ' run-time hardware config
    user        :   "isp_hub75_hwPanelConfig"  ' compile-time hardware config
    largeBffrs  :   "isp_hub75_hwBuffers"      ' large buffers for each chain of panels

CON
	' which chain is connected to which pin-group
    HUB75_FRONT_PANEL = hub75Bffrs.HUB75_ADAPTER_1
    HUB75_BACK_PANEL = hub75Bffrs.HUB75_ADAPTER_2
    
    ' which display instance do we want to call FRONT and BACK
    FRONT_PANEL = 0
    DISP1_PANEL = 1
    
PUB ...() | frontPanelIdx, backPanelIdx

    hub75Bffrs.configure(HUB75_FRONT_PANEL, user.DISP0_ADAPTER_BASE_PIN, user.DISP0_PANEL_DRIVER_CHIP, user.DISP0_PANEL_ADDR_LINES)
    hub75Bffrs.configure(HUB75_BACK_PANEL, user.DISP1_ADAPTER_BASE_PIN,  user.DISP1_PANEL_DRIVER_CHIP, user.DISP1_PANEL_ADDR_LINES)

    frontPanelIdx := hub75Bffrs.indexForHub75ChainId(HUB75_FRONT_PANEL)
    backPanelIdx := hub75Bffrs.indexForHub75ChainId(HUB75_DISP1_PANEL)
    
    display.setBufferPointers(frontPanelIdx, largeBffrs.chain0Ptrs())
    display.setBufferPointers(backPanelIdx, largeBffrs.chain1Ptrs())

    ' startup our backend COG(s)
    ok := cog := display.start(0, frontPanelIdx)   ' send buffer to driver
    ok := cog := display.start(1, backPanelIdx)   ' send buffer to driver
    
    ' NOTE with multiple hub75 cards all your display.method() calls must 
    '  now be display[FRONT_PANEL].method() or display[DISP1_PANEL].method() calls.

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

Licensed under the MIT License. 

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep.biz-blue.svg?style=for-the-badge

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765

[releases-shield]: https://img.shields.io/github/release/ironsheep/p2-LED-Matrix-Driver.svg?style=for-the-badge

[releases]: https://github.com/ironsheep/P2-HUB75-LED-Matrix-Driver/releases
