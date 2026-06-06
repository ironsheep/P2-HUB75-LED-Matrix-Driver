# RUC7258 / RUC7258D - LED Display Row Driver

**Manufacturer:** Shenzhen Ruichips Semiconductor Co., Ltd.

## Description
8-channel LED display line scanning blanking control driver with built-in 3-to-8 decoder.

## Key Specifications
- **Package:** SOP-16
- **Channels:** 8
- **Supply Voltage:** 3.3V - 5.5V
- **Max Output Current:** 2.8A
- **Features:**
  - Built-in 3-to-8 decoder
  - Constant charge absorption circuitry
  - Eliminates ghosting effects
  - Short circuit protection
  - Overcurrent protection
  - Supports up to 16S applications (cascade two chips via EN pin)

## Comparison to TC7258EN
The RUC7258D is functionally equivalent to the Fuman TC7258EN:
- Both are 8-channel row drivers
- Both integrate 138 decoder functionality
- Both have anti-ghosting features
- RUC7258D has slightly higher current (2.8A vs 2.5A)

## Datasheet Sources
Full datasheet requires registration:
- [Sekorm - RUC7258 LED Gate Driver](https://en.sekorm.com/doc/1468121.html) (863KB, 7 pages)
- [JLCPCB Parts - RUC7258D](https://jlcpcb.com/partdetail/Ruichips-RUC7258D/C18198495) (discontinued)

## Used On
- P3-HS23011030-600 (64×64 panel with FM6124C)

## Driver Compatibility
Uses same driver flags as panels with TC7258EN - no special configuration needed.
