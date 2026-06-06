# GS6238S - LED Column Driver Chip

**Manufacturer:** Unknown (Chinese)

## Description
16-channel LED column driver used in HUB75 RGB LED matrix panels.

## Key Characteristics
- Green/Blue swap required (driver handles automatically)
- 1/16 scan rate
- ABCD address lines
- Offset latch style with overlap positioning
- No initialization sequence required

## Datasheet Status
**No public datasheet available.** This chip appears to be a Chinese LED driver with limited documentation.

## Known Usage
- Cyan label panels - P2.5-16S-V1.0 (S210164-M00739)
- 64×32 resolution panels

## References
- [SmartMatrix Community Discussion](https://community.pixelmatix.com/t/64x32-panel-from-aliexpress-gs6238s/925)
- [PxMatrix Issue #269](https://github.com/2dom/PxMatrix/issues/269)

## Driver Flags
```spin2
CHIP_MANUAL_SPEC | LAT_STYLE_OFFSET | LAT_POSN_OVERLAP | GB_SWAP
```
