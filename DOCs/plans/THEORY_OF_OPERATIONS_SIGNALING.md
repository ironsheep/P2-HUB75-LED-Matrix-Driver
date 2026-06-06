# HUB75 Signaling Theory of Operations

## Deep Analysis of `isp_hub75_rgb3bit.spin2`

**Document Purpose:** Detailed instruction-by-instruction analysis of the HUB75 signaling code, focusing on LAT, OE, CLK, ADDR, and RGB line control.

**Analysis Date:** January 2025
**Target Hardware:** ICN2037-based panels (current config: 2x2 grid of 128x64 panels)

---

## 1. System Clock Configuration

From `demo_hub75_quadPanel.spin2`:
```spin
CLK_FREQ = 335_000_000    ' 335 MHz system clock
_clkfreq = CLK_FREQ
```

**Timing Constants:**
- System clock period: 1/335MHz = **2.985 ns**
- Standard PASM2 instruction: 2 clock cycles = **5.97 ns**
- Expected inner loop (8 instructions × 2 cycles): 16 cycles = **47.76 ns**
- Expected clock frequency: 1/47.76ns ≈ **20.9 MHz**

**Observed Problem:**
- Measured clock: **830 kHz**
- Measured period: 1/830kHz = **1.2 μs = 1200 ns**
- Clock cycles per bit at 335 MHz: 1200ns / 2.985ns = **402 cycles**
- Ratio: 402/16 = **~25x slower than expected**

---

## 2. Pin Assignment Architecture

### 2.1 HUB75 Connector Pin Layout (from base pin)

| Offset | Pin Function | Direction |
|--------|--------------|-----------|
| +0     | CLK          | Output    |
| +1     | OE (active low) | Output |
| +2     | LATCH        | Output    |
| +3     | ADDR_A       | Output    |
| +4     | ADDR_B       | Output    |
| +5     | ADDR_C       | Output    |
| +6     | ADDR_D       | Output    |
| +7     | ADDR_E       | Output    |
| +8     | R1           | Output    |
| +9     | G1           | Output    |
| +10    | B1           | Output    |
| +11    | R2           | Output    |
| +12    | G2           | Output    |
| +13    | B2           | Output    |
| +14    | SPARE_1      | -         |
| +15    | SPARE_2      | -         |

### 2.2 Pin Groups (defined in Spin2 `start()`)

```spin
pnlRowAddrPins  := pnlLedPinA ADDPINS 4    ' A-E address lines (pins +3 to +7)
pnlColorPins    := pnlLedPinR1 ADDPINS 5   ' R1,G1,B1,R2,G2,B2 (pins +8 to +13)
pnlControlPins  := pnlLedPinCLK ADDPINS 2  ' CLK,OE,LAT (pins +0 to +2)
```

### 2.3 Pin Masks (PASM2 DAT section)

For pins P16-P31 (DISP0_ADAPTER_BASE_PIN = PINS_P16_P31) with ADDR_ABCDE:

```pasm
maskAllPins := %00000000_00111111_11111111_00000000   ' All 14 HUB75 pins
maskAddr    := %00000000_00000000_11111000_00000000   ' Address A-E (bits 19-23)
maskRgb12   := %00000000_00111111_00000000_00000000   ' RGB1+RGB2 (bits 24-29)
```

**Bit positions within the 32-bit OUTA/OUTB register:**
- CLK:    bit 16
- OE:     bit 17
- LATCH:  bit 18
- ADDR_A: bit 19
- ADDR_B: bit 20
- ADDR_C: bit 21
- ADDR_D: bit 22
- ADDR_E: bit 23
- R1:     bit 24
- G1:     bit 25
- B1:     bit 26
- R2:     bit 27
- G2:     bit 28
- B2:     bit 29

---

## 3. Control Flags Analysis

### 3.1 Flag Definitions (from `isp_hub75_hwEnums.spin2`)

```spin
#$100, LAT_STYLE_OFFSET      ' $0100 - Latch pulse position variant
#$200, LAT_POSN_OVERLAP      ' $0200 - Latch overlaps with data clocking
#$400, INIT_PANEL_REQUIRED   ' $0400 - Panel needs initialization sequence
#$800, CLK_WIDE_PULSE        ' $0800 - Clock needs wider pulse (slower)
#$1000, RB_SWAP              ' $1000 - Red/Blue channels swapped
#$2000, SCAN_4               ' $2000 - 1/4 scan panel (vs 1/16 or 1/32)
#$4000, GB_SWAP              ' $4000 - Green/Blue channels swapped
```

### 3.2 Chip-Specific Flag Combinations

| Chip | Flags | Notes |
|------|-------|-------|
| **ICN2037** | `CLK_WIDE_PULSE \| RB_SWAP` | Current config |
| ICN2038S | `CLK_WIDE_PULSE \| SCAN_4` | 1/4 scan variant |
| FM6126A | `LAT_STYLE_OFFSET \| LAT_POSN_OVERLAP \| INIT_PANEL_REQUIRED` | Overlapped latch |
| FM6124 | (none) | Basic timing |
| MBI5124GP | `LAT_END_ENCL \| SCAN_4 \| INIT_PANEL_REQUIRED` | Requires init |
| DP5125D | `LAT_STYLE_OFFSET \| LAT_POSN_OVERLAP \| SCAN_4` | 1/4 scan |
| GS6238S | `LAT_STYLE_OFFSET \| LAT_POSN_OVERLAP \| GB_SWAP` | G/B swapped |

### 3.3 Flag Interpretation in Driver (lines 257-275)

```spin
driverFlags := dvrConfig & $ff00
modeOverlapDAT := (driverFlags & hwEnum.LAT_POSN_OVERLAP) <> 0 ? True : False
modeLatchEnclosed := (driverFlags & hwEnum.LAT_STYLE_OFFSET) <> 0 ? False : True
bInitPanel := (driverFlags & hwEnum.INIT_PANEL_REQUIRED) <> 0 ? True : False
modeSlowCLK := (driverFlags & hwEnum.CLK_WIDE_PULSE) <> 0 ? True : False
bSwapRB := (driverFlags & hwEnum.RB_SWAP) > 0 ? True : False
bScan_1_4 := (driverFlags & hwEnum.SCAN_4) > 0 ? True : False
```

**For ICN2037 (CHIP_ICN2037 = CLK_WIDE_PULSE | RB_SWAP):**
- `modeOverlapDAT = FALSE` → Uses `wrLatchAtEnd` routine
- `modeLatchEnclosed = TRUE` → Latch enclosed timing
- `bInitPanel = FALSE` → No initialization sequence
- `modeSlowCLK = TRUE` → **WIDE CLOCK PULSE REQUESTED**
- `bSwapRB = TRUE` → Red/Blue swapped in software
- `bScan_1_4 = FALSE` → Standard 1/32 scan

---

## 4. Driver Initialization (lines 796-824)

### 4.1 Port Selection

```pasm
' Configure A vs B port based on pin group
or      modeUsePortA, modeUsePortA  wz
if_nz   setd    dirInst1of2, #DIRA      ' Use DIRA for P0-P31
if_nz   setd    outInst1of3, #OUTA      ' Use OUTA for P0-P31
if_z    setd    dirInst1of2, #DIRB      ' Use DIRB for P32-P63
if_z    setd    outInst1of3, #OUTB      ' Use OUTB for P32-P63
```

### 4.2 Byte Position Selection

```pasm
or      bSetLowPins, bSetLowPins  wz    ' Q: using low 16 bits?
if_nz   SETR    outInst2of3, #%1000110_01   ' setbyte #1 (bits 8-15)
if_z    SETR    outInst2of3, #%1000110_11   ' setbyte #3 (bits 24-31)
or      bSetMidPins, bSetMidPins  wz    ' Q: using middle 16 bits?
if_nz   SETR    outInst2of3, #%1000110_10   ' setbyte #2 (bits 16-23)
```

For P16-P31: Uses byte #2 (bits 16-23) for RGB data output.

### 4.3 Data Rotation Direction

```pasm
or      modeDatRotLeft, modeDatRotLeft   wz
if_nz   SETR    rotInstr1of2,#%0000001_00   ' ROR instruction
if_z    SETR    rotInstr1of2,#%0000000_00   ' ROL instruction
```

### 4.4 Latch Mode Selection (CRITICAL)

```pasm
or      modeOverlapDAT, modeOverlapDAT   wz
if_nz   SETR    jmpInstr1of1,#%0000000_00   ' NOP (use wrLineLatchOvlp)
if_nz   SETD    jmpInstr1of1,##0            ' NOP
' If modeOverlapDAT is FALSE, jmpInstr1of1 remains as JMP #wrLatchAtEnd
```

**For ICN2037:** `modeOverlapDAT = FALSE`, so the jump instruction at line 1015 remains:
```pasm
jmpInstr1of1    jmp     #wrLatchAtEnd
```

This selects the `wrLatchAtEnd` routine (lines 1076-1128).

---

## 5. Main Signaling Loop: `wrLatchAtEnd` (lines 1076-1128)

This is the active routine for ICN2037 panels. Let me analyze it instruction by instruction.

### 5.1 Loop Structure Overview

```
wrLatchAtEnd
    ├── Initialize byteOffset = 0
    │
    └── wrLineLatchAtEnd (outer loop - iterates until buffer exhausted)
        │
        ├── clkNONextByte
        │   └── REP loop (colCtrMax iterations = 256 for 2x128 chain)
        │       ├── altgb + getbyte (fetch pixel byte)
        │       ├── drvl CLK (clock low)
        │       ├── setbyte OUTA (output RGB data)
        │       ├── nop (data settle time)
        │       ├── drvh CLK (clock high - rising edge latches data)
        │       ├── nop (clock high extension)
        │       └── nop (clock high extension)
        │
        ├── Post-row operations
        │   ├── waitx #2
        │   ├── drvl CLK (final clock low)
        │   ├── drvh OE (disable output)
        │   ├── Update address
        │   ├── call emitAddr
        │   ├── drvh LATCH
        │   ├── waitx #3
        │   ├── Conditional OE/LATCH sequence
        │   └── waitx #3
        │
        └── Loop back if more rows
```

### 5.2 Instruction-by-Instruction Analysis of Inner Loop

```pasm
clkNONextByte
                rep     @eobytes, colCtrMax
```
**REP Instruction:**
- Sets up hardware repeat block
- `colCtrMax` = 256 (for 2×128 panel chain)
- Instructions from here to `eobytes` label execute `colCtrMax` times
- **NO BRANCH OVERHEAD** - hardware repeat is zero-overhead

```pasm
                altgb   byteOffset, pCogBffrIncr
```
**ALTGB (Alternate Get Byte):**
- Cycles: **2**
- Modifies the D field of the NEXT instruction (getbyte)
- `byteOffset` is added to the base register address
- `pCogBffrIncr` = `cogBuffer + $200` where:
  - `cogBuffer` = base COG address of pixel buffer
  - `$200` = bit 9 set = **auto-increment flag**
- After execution, `byteOffset` is incremented by 1

```pasm
                getbyte colorByte, 0-0, #0-0
```
**GETBYTE:**
- Cycles: **2**
- Extracts one byte from a COG register into `colorByte`
- The `0-0` placeholders are modified by preceding ALTGB
- Result: `colorByte` contains 6 bits of pixel data: `00_RGB2_RGB1`

```pasm
                drvl    pinLedCLK            ' falling edge in prep for rising...
```
**DRVL (Drive Low):**
- Cycles: **2**
- Sets pin to output mode and drives LOW
- CLK goes LOW (preparing for rising edge)

```pasm
outInst2of3     setbyte OUTA, colorByte, #3         ' modded to byte 1 or byte 3
```
**SETBYTE:**
- Cycles: **2**
- Writes `colorByte` to byte position #2 of OUTA (for P16-P31)
- This places RGB data on pins 24-29 (R1,G1,B1,R2,G2,B2)
- **Note:** The `#3` is modified at startup to `#2` for P16-P31 pin group

```pasm
                nop
```
**NOP:**
- Cycles: **2**
- Data settle time before clock rising edge
- Allows RGB data to stabilize on pins

```pasm
                drvh    pinLedCLK            ' rising edge - 15nSec pulse at 335 MHz
```
**DRVH (Drive High):**
- Cycles: **2**
- Sets pin to output mode and drives HIGH
- **RISING EDGE** - This is when shift registers in panel latch the RGB data
- Comment says "15nSec pulse" but at 335MHz, 2 cycles = 5.97ns

```pasm
                nop     ' new extend clock pulse x1
```
**NOP:**
- Cycles: **2**
- Extends clock HIGH time

```pasm
                nop     ' new extend clock pulse x2
```
**NOP:**
- Cycles: **2**
- Further extends clock HIGH time

```pasm
eobytes
```
**Label marking end of REP block**

### 5.3 Timing Calculation for Inner Loop

| Instruction | Cycles | Cumulative |
|-------------|--------|------------|
| altgb       | 2      | 2          |
| getbyte     | 2      | 4          |
| drvl CLK    | 2      | 6          |
| setbyte     | 2      | 8          |
| nop         | 2      | 10         |
| drvh CLK    | 2      | 12         |
| nop         | 2      | 14         |
| nop         | 2      | 16         |

**Total: 16 cycles per pixel clock**

At 335 MHz:
- Period per clock: 16 × 2.985ns = **47.76 ns**
- Expected frequency: 1/47.76ns = **20.9 MHz**

### 5.4 Clock Waveform Analysis

```
Cycle:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16  1  2 ...
Instr:  [altgb ][getbyt][drvl  ][setbyt][nop   ][drvh  ][nop   ][nop   ]
CLK:    ~~~~~~~~~~~~~~~|_______|~~~~~~~|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|______
                       ^               ^                       ^
                       LOW starts      HIGH starts             LOW (next iter)
```

- CLK LOW time: cycles 5-10 = 6 cycles = **17.9 ns**
- CLK HIGH time: cycles 11-16 + 1-4 of next = 10 cycles = **29.9 ns**
- Duty cycle: ~63% HIGH

---

## 6. Post-Row Operations (lines 1101-1128)

After the REP loop completes one row:

```pasm
eobytes
                waitx   #2                          ' is this doing anything?
                drvl    pinLedCLK                   ' falling edge - reset clock after end of loop
```
**WAITX #2:**
- Waits for 2+2 = 4 additional cycles
- Provides settling time

```pasm
                drvh    pinLedOE                    ' disable output (in prep for latch)
```
**Disable Output:**
- OE goes HIGH (active low, so this DISABLES LED output)
- Required before changing address to prevent ghosting

```pasm
                add     row_addr, addrValue1        ' incr address by 1
                call    #emitAddr
```
**Address Update:**
- Increment row address (cycles through 0-31 for 1/32 scan)
- `emitAddr` subroutine writes address to pins

```pasm
                drvh    pinLedLATCH
                waitx   #3  ' 2 + 3 x clk           ' let LATCH settle
```
**Latch Pulse:**
- LATCH goes HIGH to transfer shift register data to output latches
- Wait 5 cycles (15 ns) for latch to complete

```pasm
                or      modeLatchEnclosed, modeLatchEnclosed      wz
    if_z            drvl    pinLedOE
    if_z            drvl    pinLedLATCH                 ' end latch data
    if_nz           drvl    pinLedLATCH                 ' end latch data
    if_nz           waitx   #3  ' 2 + 3 x clk           ' let LATCH settle
    if_nz           drvl    pinLedOE
                waitx   #3  ' 2 + 3 x clk           ' let LATCH settle
```
**Latch Completion Sequence:**

For ICN2037 (`modeLatchEnclosed = TRUE`, so Z=0, NZ=1):
1. `drvl pinLedLATCH` - End latch pulse
2. `waitx #3` - 5 cycle delay
3. `drvl pinLedOE` - Re-enable output (OE LOW = enabled)
4. `waitx #3` - Final settling

```pasm
                cmp      byteOffset, maxPwmSubPgSzBytes wc
    if_c            jmp     #wrLineLatchAtEnd
```
**Loop Control:**
- Compare current byte offset against subpage size
- If more data remains (C=1), loop back for next row

---

## 7. Alternative Routine: `wrLineLatchOvlp` (FM6126A panels)

This routine is used when `modeOverlapDAT = TRUE`. The key difference is that LATCH is asserted during the final 3 clock cycles of each row, overlapping with data transmission.

### 7.1 Key Differences

| Aspect | wrLatchAtEnd | wrLineLatchOvlp |
|--------|--------------|-----------------|
| Latch timing | After all clocks | During last 3 clocks |
| Data fetch | altgb+getbyte | ALTS+mov+rol |
| Clock structure | REP block | REP block with conditional latch |
| Panel types | ICN2037, FM6124, etc. | FM6126A |

### 7.2 Overlapped Latch Logic (lines 1039-1041)

```pasm
                cmp     col_addr, colCtrLatchCt     wz  ' at last three columns?
    if_z            drvh    pinLedOE                        ' disable output
    if_z            drvh    pinLedLATCH
```

When column counter reaches `colCtrLatchCt` (= colCtrMax - 3), begin latch sequence while still clocking out final 3 pixels.

---

## 8. The `modeSlowCLK` Flag - CRITICAL FINDING

### 8.1 Flag Is Set But Not Used!

Looking at the driver initialization (lines 822-824), there's **commented-out code**:

```pasm
'                    or      modeSlowCLK, modeSlowCLK   wz
'    if_z            SETR    waitInst1of1,#%0000000_00  'make into NOP instruction
'    if_z            SETD    waitInst1of1,##0           'make into NOP instruction
```

**This code is commented out!**

The intent was:
- If `modeSlowCLK = FALSE`: Convert a WAITX instruction to NOP (fast clock)
- If `modeSlowCLK = TRUE`: Keep WAITX instruction (slow clock)

But there is **no `waitInst1of1` label** in the current signaling loops! The flag is:
1. Parsed from chip configuration ✓
2. Stored in `modeSlowCLK` variable ✓
3. **Never actually used in signaling** ✗

### 8.2 Implications

For ICN2037 panels:
- `CLK_WIDE_PULSE` flag is set
- `modeSlowCLK = TRUE`
- But the clock timing is **identical** to panels without this flag
- The ICN2037 datasheet specifies max 20 MHz clock
- Current code theoretically generates ~20.9 MHz (close enough)

**This is NOT the cause of the 830 kHz issue** - the flag being unused means the clock should still be fast, not slow.

---

## 9. Potential Causes of 830 kHz Clock

### 9.1 Hypothesis 1: System Clock Not Configured

If the P2 failed to configure its PLL and is running at RCFAST (~20 MHz internal RC):
- At 20 MHz sysclk: 16 cycles = 800 ns per bit
- Clock frequency: 1.25 MHz

Still not 830 kHz, but closer.

### 9.2 Hypothesis 2: Wrong Crystal/PLL Configuration

If using 25 MHz crystal but PLL isn't engaging:
- At 25 MHz: Clock frequency = 1.56 MHz

### 9.3 Hypothesis 3: Debug Overhead

The driver has `debug()` statements that compile in. If DEBUG_COGS includes this COG and debug output is active, it could massively slow execution. However, debug statements aren't inside the inner loop.

### 9.4 Hypothesis 4: COG Not Running the Expected Code

If `coginit()` failed silently or the COG is running different code, timing would be wrong.

### 9.5 Hypothesis 5: Measurement Error

Is the 830 kHz measurement taken:
- On the CLK pin directly?
- Using a scope with sufficient bandwidth?
- During actual panel refresh (not initialization)?

### 9.6 Hypothesis 6: Buffer Loading Dominates

The REP loop is fast, but what about time spent:
- Loading buffers from HUB RAM (`rdlong cogBuffer, ptra++`)
- Processing between subpages
- Command polling in main loop

If buffer loads are slow, the **average** clock frequency could be much lower even if instantaneous clock during the REP loop is correct.

### 9.7 Hypothesis 7: REP Not Executing As Expected

If `colCtrMax` is wrong (e.g., 0 or 1), the REP loop would barely execute:
- colCtrMax should be 256 for 2×128 chain
- If it's 1, only one clock per row → very slow effective frequency

---

## 10. Recommended Diagnostic Steps

### 10.1 Verify System Clock

Add to demo file:
```spin
debug("CLKFREQ = ", udec(clkfreq))
```

Should print 335000000. If it prints ~20000000, PLL isn't configured.

### 10.2 Verify colCtrMax

In driver startup debug output, look for:
```
RG3:  [values of rowCtrMax, colCtrMax, colCtrMaxLngs]
```

For 2×128 panel chain: colCtrMax should be 256.

### 10.3 Scope the CLK Pin Directly

- Measure CLK frequency during steady-state refresh
- Look at pulse width (should be ~30ns high, ~18ns low)
- Check for gaps between rows (expected) vs gaps within rows (unexpected)

### 10.4 Check for HUB Access Stalls

The `rdlong cogBuffer, ptra++` in `cmdDsplyNoPwmFrame` (line 952) is a **block transfer**:
```pasm
setq    maxPwmSubPgSzLngsM1
rdlong  cogBuffer, ptra++
```

SETQ+RDLONG does a burst read of N+1 longs. This could stall if:
- HUB RAM is contended
- The transfer is very large

For a 256-column row at 4 bits/pixel = 128 bytes = 32 longs per row.
Total subpage: `maxPwmSubPgSzLongs` longs.

---

## 11. Buffer Flow and Timing Overhead Analysis

### 11.1 Buffer Structure for 2×2 Grid of 128×64 Panels

**Display Geometry:**
- Total display: 256 columns × 128 rows
- Panel chain: 2 panels × 128 columns = 256 columns
- Scan type: 1/32 (32 address lines for 64-row panel)
- Rows per address: 2 (top half + bottom half)

**PWM Buffer Structure:**
- Bits per pixel in PWM frame: 4 (nibble for RGB1, nibble for RGB2)
- Bytes per scan row: 256 pixels × 1 byte/2 pixels = 128 bytes
- Actually: 256 bytes per scan row (1 byte per column: {00}{RGB2}{RGB1})
- PWM frame size: 32 addresses × 256 bytes = 8,192 bytes per PWM frame
- COG buffer size: 512 bytes = 2 scan rows

**Subpage Structure:**
- Subpages per PWM frame: 8192 / 512 = **16 subpages**
- Rows per subpage: 2 scan rows

### 11.2 Complete Frame Set Timing

For 8-bit color depth:
- PWM frames: 8
- Display count per frame (binary weighting): [4, 4, 2, 1, 1, 1, 1, 1] ≈ 15 total displays
- Total subpage displays: 16 subpages × 8 frames × (average 1.875 repeats) ≈ 240 subpage displays per frame set

### 11.3 Time Budget Per Subpage

**REP Loop (inner clocking):**
- 256 columns × 16 cycles = 4,096 cycles per scan row
- 2 scan rows per subpage × 4,096 = 8,192 cycles
- At 335 MHz: 8,192 / 335e6 = **24.5 μs** of clocking

**Post-Row Overhead (per scan row):**
```
waitx #2          = 4 cycles
drvl pinLedCLK    = 2 cycles
drvh pinLedOE     = 2 cycles
add row_addr      = 2 cycles
call emitAddr     = ~10 cycles (call + body + ret)
drvh pinLedLATCH  = 2 cycles
waitx #3          = 5 cycles
drvl pinLedLATCH  = 2 cycles
waitx #3          = 5 cycles
drvl pinLedOE     = 2 cycles
waitx #3          = 5 cycles
cmp + jmp         = 4 cycles
─────────────────────────────
Total:            ~45 cycles per row = 134 ns
```

For 2 rows: **~268 ns overhead**

**Subpage Load Overhead:**
```pasm
setq    maxPwmSubPgSzLngsM1   ' 2 cycles
rdlong  cogBuffer, ptra++     ' BURST READ: 128 longs
```

HUB burst read timing:
- Initial HUB sync: 0-7 cycles (average 3.5)
- First long: 2 cycles
- Subsequent longs: 1 cycle each (pipelined)
- Total for 128 longs: ~3.5 + 2 + 127 = **132.5 cycles = 395 ns**

**Command Loop Overhead:**
The main loop checks for commands between subpages:
```pasm
getCommand
                cmp     pwmSubPgCt, #0  wz
if_nz           jmp     #nextPwmSubpage
                cmp     fillSubPgCt, #0  wz
if_nz           jmp     #nextFill
                cmp     pwmFrameCt, #0  wz
if_nz           jmp     #nextPwmFrame
                rdlong  nxtCommand, pCommmand
                ...
```

During PWM display, most iterations take fast path: ~10 cycles = **30 ns**

### 11.4 Duty Cycle Calculation

Per subpage:
| Phase | Time |
|-------|------|
| Clock REP loop | 24.5 μs |
| Row overhead (2×) | 268 ns |
| Subpage load | 395 ns |
| Command loop | 30 ns |
| **Total** | **~25.2 μs** |

**Clock duty cycle:** 24.5 / 25.2 = **97.2%**

This means the instantaneous clock frequency during clocking should be ~20.9 MHz, but if measuring average frequency including overhead, it would be:
- 256 clocks × 2 rows = 512 clocks per subpage
- Frequency = 512 / 25.2 μs = **20.3 MHz average**

**This does NOT explain the 830 kHz observation!**

### 11.5 Critical Realization: byteOffset Not Reset Between Rows!

Looking at the loop structure more carefully:

```pasm
wrLatchAtEnd
                mov     byteOffset, #0           ' ← Only reset here!
wrLineLatchAtEnd
                rep     @eobytes, colCtrMax
                altgb   byteOffset, pCogBffrIncr ' ← Auto-increments byteOffset
                ...
eobytes
                ...
                cmp     byteOffset, maxPwmSubPgSzBytes wc
    if_c        jmp     #wrLineLatchAtEnd        ' ← Loop back WITHOUT reset!
```

`byteOffset` is only initialized to 0 at `wrLatchAtEnd`, then auto-incremented in the REP loop. After 256 iterations, `byteOffset = 256`. The code then compares against `maxPwmSubPgSzBytes` (512). Since 256 < 512, it loops back to `wrLineLatchAtEnd` for the second row, where `byteOffset` continues from 256 to 511.

**This is correct behavior** - it reads sequential bytes from the buffer.

### 11.6 The Real Mystery

The math shows that even with all overhead accounted for, the clock frequency should be ~20 MHz. The 830 kHz measurement (25x slower) cannot be explained by:
- Normal inter-row gaps
- Buffer loading time
- Command polling

**Possible explanations requiring investigation:**
1. System clock not at 335 MHz (most likely)
2. Measurement taken during initialization, not steady-state refresh
3. Scope aliasing or measurement error
4. Something blocking the COG (debug, lockups, etc.)

---

## 12. Summary of Findings

### What's Working:
1. Pin masks are correctly calculated for P16-P31
2. Control flags are parsed correctly
3. Inner loop structure is sound (8 instructions, 16 cycles)
4. Loop selects correct routine (wrLatchAtEnd) for ICN2037

### Anomalies Found:
1. **`modeSlowCLK` flag is parsed but never used** - commented out code
2. **Comments don't match code** - "256 longs" comment but 128 longs allocated
3. **Clock timing math suggests ~20.9 MHz** but 830 kHz observed

### Most Likely Cause:
The 25x slowdown (830 kHz vs 20.9 MHz) strongly suggests the **system clock is not running at 335 MHz**. A factor of ~25x slowdown could occur if:
- P2 is running at ~13.4 MHz (335/25)
- Or significant time is spent outside the REP loop that wasn't accounted for

### Next Steps:
1. Verify `clkfreq` at runtime
2. Scope the CLK pin during active refresh
3. Add timing instrumentation around the signaling loop
4. Check if debug output is slowing execution

---

## 13. Clock-Frequency-Independent Timing (Implemented)

### 13.1 Design Goals

The panel clock frequency should be fixed at approximately 20 MHz regardless of the P2 system clock frequency. This ensures:
- Consistent panel behavior across different P2 configurations
- Compliance with ICN2037 datasheet maximum clock spec (20 MHz)
- Predictable timing when sysclk is changed for other reasons

### 13.2 Implementation Approach

The inner REP loop uses `WAITX` instructions with calculated delay values instead of fixed NOPs.

**New Inner Loop Structure (7 instructions):**
```pasm
rep     @eobytes, colCtrMax
    altgb   byteOffset, pCogBffrIncr    ' 2 cycles: setup byte fetch
    getbyte colorByte, 0-0, #0-0        ' 2 cycles: get color byte
    drvl    pinLedCLK                   ' 2 cycles: CLK low
    setbyte OUTA, colorByte, #3         ' 2 cycles: output RGB data
    waitx   waitCyclesLow               ' 2+N cycles: data setup time
    drvh    pinLedCLK                   ' 2 cycles: CLK high (latches data)
    waitx   waitCyclesHigh              ' 2+M cycles: clock high time
eobytes
```

**Timing Calculation (in Spin2 start() method):**
```spin
cycles_per_bit := clkfreq / TARGET_PANEL_HZ      ' e.g., 335MHz/20MHz = 16
extra_cycles := cycles_per_bit - BASE_LOOP_CYCLES ' e.g., 16 - 14 = 2
waitCyclesLow := extra_cycles / 2                 ' e.g., 1
waitCyclesHigh := extra_cycles - waitCyclesLow    ' e.g., 1
```

**Constants:**
```spin
TARGET_PANEL_HZ = 20_000_000    ' Target panel clock: 20 MHz
BASE_LOOP_CYCLES = 14           ' Minimum cycles (7 instr × 2 cycles each)
MIN_SYSCLK_HZ = 280_000_000     ' Minimum sysclk = 14 × 20 MHz
```

### 13.3 Timing Examples

| System Clock | cycles_per_bit | extra_cycles | waitLo | waitHi | Actual Panel Clock |
|--------------|----------------|--------------|--------|--------|-------------------|
| 335 MHz      | 16             | 2            | 1      | 1      | 20.9 MHz          |
| 320 MHz      | 16             | 2            | 1      | 1      | 20.0 MHz          |
| 300 MHz      | 15             | 1            | 0      | 1      | 20.0 MHz          |
| 280 MHz      | 14             | 0            | 0      | 0      | 20.0 MHz          |
| 250 MHz      | 12             | -2 (→0)      | 0      | 0      | 17.9 MHz (limited)|
| 200 MHz      | 10             | -4 (→0)      | 0      | 0      | 14.3 MHz (limited)|

### 13.4 Limitations

#### 13.4.1 Minimum System Clock Requirement

**CRITICAL: Minimum sysclk = 280 MHz for 20 MHz panel clock**

The inner loop has a minimum of 14 cycles (7 instructions × 2 cycles each). Even with `WAITX #0`, which takes 2 cycles, the minimum loop time is 14 cycles.

Panel clock frequency = sysclk / cycles_per_bit

For a 20 MHz panel clock: sysclk_min = 20 MHz × 14 = **280 MHz**

If sysclk < 280 MHz:
- The driver prints a warning at startup
- Panel clock will be faster than target but slower than would otherwise be possible
- The driver uses `waitCyclesLow = waitCyclesHigh = 0` (minimum timing)

#### 13.4.2 Granularity of Panel Clock

The panel clock can only be adjusted in integer cycle increments:

| sysclk | cycles/bit | Panel Clock |
|--------|------------|-------------|
| 280 MHz | 14 | 20.0 MHz |
| 294 MHz | 14 | 21.0 MHz (over target, 15 would give 19.6 MHz) |
| 300 MHz | 15 | 20.0 MHz |

The calculation `clkfreq / TARGET_PANEL_HZ` truncates, so the actual panel clock may be slightly higher than target (up to ~5% for edge cases).

#### 13.4.3 Phase Distribution

Extra cycles are distributed between the low and high phases:
- `waitCyclesLow = extra_cycles / 2` (data setup extension)
- `waitCyclesHigh = extra_cycles - waitCyclesLow` (clock pulse extension)

For odd `extra_cycles`, the high phase gets the extra cycle. This is intentional because:
1. Panel data sheets typically specify minimum clock high time
2. Data is already stable before CLK goes high (altgb/getbyte fetch earlier in loop)

#### 13.4.4 No Runtime Adjustment

The timing values are calculated once during `start()` initialization. Changing `clkfreq` after driver start will NOT update the panel clock frequency. To change sysclk:
1. Stop the driver
2. Reconfigure system clock
3. Restart the driver

#### 13.4.5 Does Not Apply to FM6126A Panels

The clock-independent timing is only implemented in the `wrLatchAtEnd` routine. The alternative `wrLineLatchOvlp` routine (used by FM6126A panels) still uses fixed timing. This should be extended in a future update.

### 13.5 Verification

To verify the panel clock frequency:
1. Check debug output at startup for:
   ```
   RG3:  TIMING cycles/bit=16 waitLo=1 waitHi=1
   ```
2. Measure CLK pin with oscilloscope during panel refresh
3. Expected frequency should match `clkfreq / cycles_per_bit`

If `clkfreq` is lower than expected, the panel clock will be proportionally slower. The 830 kHz observation from earlier suggests sysclk was approximately 13.3 MHz (830 kHz × 16 cycles), not the configured 335 MHz.

---

## 14. Revision History

| Date | Change |
|------|--------|
| Jan 2025 | Initial theory of operations document |
| Jan 2025 | Added clock-frequency-independent timing mechanism |
| Jan 2025 | Added missing `drvh pinLedOE` before inter-subframe gap |
