# Spin2 Authoring Guide

Mandatory coding standards for all `.spin2` source files targeting the Parallax Propeller 2 with the pnut-ts compiler and VS Code Spin2 extension. Every rule in this document is a hard requirement. Code that violates any rule MUST be corrected before it is committed.

Language keywords: **MUST**, **NEVER**, **REQUIRED**, **FORBIDDEN**.

---

## Part 1 — Language Rules

These rules address Spin2 language constraints and pnut-ts compiler behavior. Violations cause silent bugs, compilation failures, or hardware faults.

### 1.1 ASCII Only — No Unicode

pnut-ts is an ASCII-only compiler. Unicode characters in code, strings, and method signatures cause silent corruption or compile errors.

**FORBIDDEN characters in code, strings, and signatures:**

| Character | Name | Replace with |
|-----------|------|-------------|
| `\u2014` (em dash) | Em dash | `-` (hyphen-minus) |
| `\u2013` (en dash) | En dash | `-` (hyphen-minus) |
| `\u2018` `\u2019` | Curly single quotes | `'` (apostrophe) |
| `\u201C` `\u201D` | Curly double quotes | `"` (straight quote) |
| `\u2026` | Ellipsis | `...` (three periods) |
| Any codepoint > 127 | Non-ASCII | ASCII equivalent |

**Exception — Unicode box-drawing and line-drawing characters in comments:**

Unicode box-drawing characters (U+2500-U+257F) and block elements (U+2580-U+259F) ARE permitted inside comments (`'`, `''`, `{ }`, `{{ }}`) for diagrams, tables, and visual layouts. These characters make architectural diagrams and data structure illustrations significantly more readable.

```spin2
' Permitted — box-drawing in a comment
{ Parameter Block Layout:
  +----------+---------+---------+---------+---------+
  | pb_cmd   | pb_p0   | pb_p1   | pb_p2   | pb_p3   |
  +----------+---------+---------+---------+---------+

  +-----------+     +----------+     +----------+
  | Caller    | --> | Worker   | --> | Hardware |
  | (any cog) |     | (cog N)  |     | (SPI)    |
  +-----------+     +----------+     +----------+
}
```

Box-drawing characters MUST NOT appear in executable code, string literals, constant names, variable names, or method signatures — only in comments.

### 1.2 Operator Confusion: `>=` vs `=>`

`>=` is greater-than-or-equal. `=>` is the case-range separator. Confusing them is a common error that compiles without warning but produces wrong behavior.

```spin2
' CORRECT — comparison
if status >= 0

' WRONG — this is a case range, not a comparison
if status => 0
```

MUST: Always use `>=` for comparisons. Only use `=>` inside `case` range expressions.

### 1.3 Case-Insensitive Name Collisions

Spin2 identifiers are case-insensitive. A local variable, return variable, or method name that matches a built-in or another method causes a silent collision.

**Known hazards:**

| Avoid | Conflicts with | Use instead |
|-------|---------------|-------------|
| `cogId` | Built-in `COGID` | `workerCog`, `myCogId` |
| `bool` | Reserved in pnut-ts v1.52+ | `bExists`, `bValid`, `bAvail` |
| `string` | Built-in `STRING()` | `pStr`, `pText`, `textBuf` |
| `send` | Built-in `SEND` | `sendData`, `transmit` |

**Also avoid** (not a collision, but a naming-quality rule): `result` as a return variable name — see Rule 2.3.

MUST: Before naming any identifier, verify it does not collide (case-insensitively) with Spin2 built-ins, PASM2 instructions, or existing PUB method names in the same file.

### 1.4 No Method Overloading

Spin2 does not support method overloading. Method names MUST be unique regardless of parameter count.

```spin2
' FORBIDDEN — two methods named "open" with different signatures
PUB open(device, pFilename, mode) : handle
PUB open(device, pFilename) : handle      ' compile error

' REQUIRED — distinct names
PUB open(device, pFilename, mode) : handle
PUB openRead(device, pFilename) : handle
```

### 1.5 Local Variables Cannot Shadow PUB Methods

A local variable with the same name as any PUB method in the file produces undefined behavior. The compiler does not warn.

MUST: Choose local variable names that do not match any PUB or PRI method name in the file.

### 1.6 Local Variables Cannot Shadow DAT or VAR Names

A local variable (parameter, return variable, or `|` local) in a PUB or PRI method MUST NOT reuse the name of any `DAT` or `VAR` declaration in the same file. The compiler will generate an error when both exist — the local eclipses the DAT/VAR name, making the outer variable unreachable within that method.

NEVER create this collision. Always choose distinct names.

```spin2
VAR
    LONG  sectorCount

' FORBIDDEN — local eclipses the VAR declaration
PUB readFile(pFilename) : status | sectorCount    ' compile error: name collision

' REQUIRED — distinct local name
PUB readFile(pFilename) : status | localSectorCount
```

This rule applies equally to `DAT` names:

```spin2
DAT
    apiLock   LONG  -1

' FORBIDDEN — local eclipses DAT
PRI acquireLock() : status | apiLock               ' compile error

' REQUIRED — distinct name
PRI acquireLock() : status | lockAttempt
```

### 1.7 Pointer Semantics Differ From C

Spin2 pointers behave differently from C/C++ pointers in several counterintuitive ways. Agents coming from other languages MUST understand these distinctions to avoid silent bugs. For full details, see `DOCs/procedures/internals/Pointer-Usage-Guide.md` and `DOCs/procedures/internals/Addressing-Usage-Guide.md`.

#### Dereferencing requires type brackets, not `*`

Spin2 has no `*` dereference operator. To read or write the value a pointer points to, use `BYTE[ptr]`, `WORD[ptr]`, or `LONG[ptr]`:

```spin2
PUB example() | ^BYTE ptr
    ptr := @buffer              ' assign address TO the pointer
    BYTE[ptr] := $FF            ' write through the pointer (dereference)
    value := BYTE[ptr]          ' read through the pointer (dereference)
```

#### `[ptr]` dereferences, bare `ptr` is the pointer itself

For struct pointers and general value access, square brackets `[ptr]` access the VALUE at the address. Without brackets, `ptr` is the raw pointer (the address).

```spin2
' VALUE operations (dereference — acts on what ptr points to)
[ptr]++                         ' increment the value AT the address
[ptr]--                         ' decrement the value AT the address
[ptr]~                          ' clear the value AT the address to 0
temp := [ptr]                   ' read entire structure at address
[ptr] := temp                   ' write entire structure at address

' POINTER operations (acts on the pointer/address itself)
ptr++                           ' advance pointer by element size
ptr--                           ' move pointer back by element size
ptr := @buffer                  ' change what the pointer points to
```

This is the critical distinction: `[ptr]++` and `ptr++` do completely different things. The first increments the data in memory. The second advances the address.

#### Struct pointers use `.` not `->`

Spin2 has no `->` operator. Struct pointer member access uses dot notation, which implicitly dereferences:

```spin2
CON
    STRUCT point(x, y)

VAR
    ^point ptr

PUB example()
    ptr := @myPoint
    ptr.x := 100                ' writes through pointer (like C's ptr->x)
    ptr.y := 200                ' no special syntax needed for dereference
```

This means `.` serves double duty — it accesses members on both direct struct variables and struct pointers. There is no syntactic distinction between `myPoint.x` (direct) and `ptr.x` (through pointer).

#### `@` vs `@@` — relative vs absolute addresses

In runtime code (PUB/PRI methods), `@variable` returns an absolute hub address and can be used directly. But in `DAT` sections, `@label` stores an object-relative offset. To use a DAT-stored address at runtime, convert it with `@@`:

```spin2
DAT
    stringTable  WORD  @str0, @str1, @str2    ' object-relative offsets
    str0         BYTE  "First", 0
    str1         BYTE  "Second", 0
    str2         BYTE  "Third", 0

PUB getString(index) : pStr
    pStr := @@WORD[@stringTable][index]        ' @@ converts to hub address
```

MUST: When reading an `@`-stored address from a DAT table at runtime, always use `@@` to resolve it. Forgetting `@@` produces a broken pointer that may appear to work in some memory layouts but fails when the object loads at a different base address.

#### Receiving struct pointer returns from objects requires brackets

When a method returns a struct pointer (`^structName`) and the caller receives it through an `OBJ` reference, the compiler may interpret the return as the full structure rather than a single LONG pointer. If the struct exceeds 15 longs, this produces a compile error ("objects cannot exceed 15 longs"). The fix is to put brackets around the receiving pointer variable:

```spin2
OBJ
    sensor : "sensor_driver"

CON
    STRUCT config(rate, gain, offset, calibration, flags)

' FAILS — compiler tries to handle full struct, may exceed return limit
PUB example() | ^config pCfg
    pCfg := sensor.getConfig()          ' compile error if struct > 15 longs

' REQUIRED — brackets tell compiler to receive the pointer value (one LONG)
PUB example() | ^config pCfg
    [pCfg] := sensor.getConfig()        ' receives the pointer, not the struct
```

MUST: When receiving a struct pointer return value from an object method call, always use `[variable] := obj.method()` bracket notation on the receiving side. This forces the compiler to treat the return as a pointer (a single LONG address) rather than attempting to unpack the entire structure.

#### Typed pointers require version directive

Typed pointer syntax (`^BYTE`, `^WORD`, `^LONG`, `^structName`) requires `{Spin2_v45}` or later at the start of the source file. Without it, the compiler does not recognize the `^` syntax. Basic `@` (address-of) and `BYTE[]`/`WORD[]`/`LONG[]` (memory access) are base Spin2 and need no directive.

### 1.8 Empty String Literal `@""` Is Invalid

`@""` does not produce a valid pointer. Use a DAT variable instead.

```spin2
' FORBIDDEN
pStr := @""

' REQUIRED
DAT
  emptyStr  BYTE  0

' then use
pStr := @emptyStr
```

### 1.9 OBJ Override Limitation

An `OBJ` section `|` (pipe) override for a CON value fails silently if the parent file defines a CON with the same name. The parent's value wins without warning.

MUST: When using `OBJ` overrides, verify the overriding file does not define a CON with the same name as the value being overridden.

---

## Part 2 — Naming Rules

Clear naming prevents bugs, reduces review friction, and makes code self-documenting.

### 2.1 No Single-Letter Variable Names

Every variable name MUST describe what it holds. This applies to parameters, return values, locals, and DAT/VAR declarations.

```spin2
' FORBIDDEN
PRI scan(p, n) : r | i, c

' REQUIRED
PRI scanEntries(pEntry, maxEntries) : status | entryIdx, attrByte
```

**Exceptions:** Inline PASM2 register names follow hardware conventions (`pa`, `pb`, `ptra`). Type-prefixed short names are permitted when context is unambiguous (`pStr`, `pBuf`). `idx` is universally understood and is acceptable as a loop index when there is only one index in the method and the domain context makes the indexed collection obvious. When a method has multiple indexes, qualify each one (`entryIdx`, `byteIdx`, `sctrIdx`).

### 2.1.1 Vowel-Removal Shortening

Short variable names formed by removing vowels are permitted when the consonant skeleton is unambiguous — the reader can sound it out and recover the full word. This keeps method signatures compact without sacrificing readability.

| Full word | Shortened | Recognizable? |
|-----------|-----------|---------------|
| cluster | `clstr` | Yes |
| sector | `sctr` | Yes |
| handle | `hndl` | Yes |
| buffer | `bffr` | Yes |
| count | `cnt` | Yes |
| position | `posn` | Yes |
| fragment | `frag` | Yes (keep prefix) |
| index | `idx` | Yes (standard) |

If the shortened form is not immediately recognizable when read aloud, keep more letters. When in doubt, prefer the longer form.

### 2.1.2 Naming Register: Globals Spelled Out, Locals Shortened

Global state (DAT and VAR declarations) MUST use fully spelled-out descriptive names (`cluster_offset`, `sector_count`, `fat_sec_in_buf`). Parameters, return variables, and local variables MAY use vowel-shortened forms (`clstr`, `sctr`, `fragCnt`) for commonly used domain concepts.

This separation prevents name collisions structurally: globals and locals never share a name because they use different naming registers. A DAT variable `fsi_free_count` and a local `freeCnt` cannot collide because one is spelled out and the other is shortened.

### 2.1.3 Consistent Base Names Across Methods

When the same data concept appears in multiple methods, use the same base name everywhere. A cluster number is always `*Clstr` (e.g., `startClstr`, `nextClstr`, `currentClstr`). A sector number is always `*Sctr`. A file handle is always `*Hndl`.

Qualify with a prefix (`start`, `next`, `prev`, `new`, `current`) when disambiguation is needed, but keep the base name identical across the codebase. Never use `clus` in one method, `cluster` in another, and `c` in a third for the same concept.

### 2.1.4 Numbered Suffixes for Homogeneous Collections

When a method needs multiple variables of the same type for the same purpose (e.g., "we need three open handles to test pool exhaustion"), numbered suffixes are appropriate: `hndl1`, `hndl2`, `hndl3`.

When the variables represent *different things* that happen to be the same type, name them by purpose: `imgHndl`, `txtHndl`, `logHndl`. The test: if the handles are interchangeable (any ordering would work), number them. If swapping them would change the test's meaning, name them by role.

Single-letter-plus-digit names (`h1`, `h2`) are FORBIDDEN — they do not describe what they hold. Use at minimum the shortened base name plus digit (`hndl1`).

### 2.2 No Generic Container Names — Describe the Data

Every variable name — parameter, return value, or local — MUST describe the data it carries. A name that describes the *role of the variable* (container, holder, result, value) instead of the *data inside it* is a generic container name and is FORBIDDEN.

The test: if you removed the surrounding code and saw only the variable name, could you tell what data it holds? `sectorCount` — yes. `result` — no. `pFilename` — yes. `value` — no.

**FORBIDDEN generic container names** (in parameters, return variables, AND locals):

| Generic name | Why it fails | Name the data instead |
|-------------|-------------|----------------------|
| `result` | Says "I hold a result" — of what? | `status`, `handle`, `bytesRead` |
| `value` | Says "I hold a value" — what value? | `sectorNum`, `temperature`, `pinState` |
| `temp` | Says "I'm temporary" — what data? | `savedCluster`, `prevEntry` |
| `data` | Says "I hold data" — what data? | `cmdResponse`, `spiByteIn` |
| `ret` | Abbreviation of `result` | `status`, `errorCode` |
| `buf` | Says "I'm a buffer" — buffer of what? | `sectorBuf`, `nameBuf` |
| `info` | Says "I hold info" — what info? | `cardCapacity`, `mountState` |

**Descriptive names by category:**

| Category | Bad | Good |
|----------|-----|------|
| Loop index | `i` | `entryIdx`, `fileIdx`, `cogIdx` |
| Pointer | `p` | `pFilename`, `pBuffer`, `pEntry` |
| Counter | `n` | `byteCount`, `sectorCount` |
| Flag | `f` | `bFound`, `bMounted`, `bTimeout` |
| Status | `r` | `status`, `handle`, `bytesRead` |

This rule applies uniformly. A local variable named `result` is just as bad as a return variable named `result` — neither tells the reader what data is being carried.

### 2.3 Return Variables Deserve Special Attention

Return variables are the most visible part of a method's contract — they appear in hover documentation, IntelliSense, and generated API docs. A generic return variable name (`result`, `value`, `ret`) forces every caller to read the method body to understand what comes back.

Every return variable MUST be named for the specific data it represents:

| Return meaning | FORBIDDEN | REQUIRED |
|---------------|-----------|----------|
| Error/success code | `result`, `success` | `status` |
| Boolean condition | `result` | `bFound`, `bMounted`, `bValid` |
| Byte count | `result`, `value` | `bytesRead`, `bytesWritten` |
| Handle ID | `result` | `handle`, `dirHandle` |
| Pointer | `result`, `data` | `pEntry`, `pBuffer` |
| Numeric value | `result`, `value` | `sectorCount`, `freeSpace` |

**Why `success` is as bad as `result`:** A return variable named `success` presupposes the outcome — it implies the method always succeeds. But if the method can also fail, the variable carries a status code that might be *either* success or an error. Name the variable for the *category* of data it carries (`status`), not for one of its possible values (`success`). The constant `SUCCESS` is a value; `status` is the variable that holds it.

### 2.4 Object Constants: Always Use the Object Reference

When a file declares an object via `OBJ`, any constant defined by that object MUST be referenced through the object name — NEVER copied into a local `CON` block. Local copies create a second source of truth that silently drifts out of sync when the object's constant changes.

This applies to all constant categories: error codes, mode enums, device identifiers, buffer sizes, limits, bit masks, and configuration values.

```spin2
OBJ
    driver : "my_driver"

' REQUIRED — reference through the object
status := driver.mount(driver.DEV_SD)
if status == driver.E_NOT_MOUNTED
    ...
repeat idx from 0 to driver.MAX_OPEN_FILES - 1
    ...
bufSize := driver.SECTOR_SIZE

' FORBIDDEN — local copy of an object's constant
CON
    DEV_SD         = 0        ' duplicates driver.DEV_SD
    E_NOT_MOUNTED  = -20      ' duplicates driver.E_NOT_MOUNTED
    MAX_FILES      = 6        ' duplicates driver.MAX_OPEN_FILES
    SECTOR_SIZE    = 512      ' duplicates driver.SECTOR_SIZE
```

**The object IS the single source of truth.** If the object author changes `MAX_OPEN_FILES` from 6 to 8, every file that uses `driver.MAX_OPEN_FILES` picks up the change automatically. A local `CON MAX_FILES = 6` stays wrong forever until a human notices.

**This rule has no exceptions.** Even if the local file uses a constant hundreds of times, it MUST reference it through the object prefix every time. Verbosity is preferable to silent divergence.

### 2.5 Same Name = Same Description

When the same parameter name appears across multiple methods, its documentation description MUST be identical everywhere. This prevents confusion and enables automated consistency checking.

When adding a new method, check existing methods for the same parameter names and copy their descriptions verbatim.

This extends to variable naming: when the same data is passed between methods (as a return value from one becoming a parameter to another), use the same base name at both sites. If `allocateCluster()` returns `clstrNum`, the caller should receive it into `clstrNum` or `newClstr` — not `c` or `temp`.

---

## Part 3 — Code Structure

### 3.1 File Layout

Every `.spin2` file MUST begin with this minimal top-to-bottom order:

1. **Version directive** — `{Spin2_v##}` on line 1 (if the file requires a minimum compiler version)
2. **File header** — `''` doc-comment block (file name, purpose, author, dates)
3. **`#PRAGMA` / `#IFDEF` preamble** — conditional compilation setup (if any)
4. **`CON` blocks** — primary constant declarations (including `STRUCT` definitions, which live inside `CON`)
5. **`OBJ` block** — object references (if any)
6. **`DAT` preamble** — singleton state, parameter blocks, buffers
7. **`VAR` block** — per-instance variables (if any)
8. **`PUB` methods** — entire public API surface
9. **`PRI` methods** — all private implementation
10. **License block** — `CON` + `{{ }}` doc block, always last

For small files, this minimal layout is sufficient — one `CON`, one `DAT`, one `VAR`, then methods. For larger files, additional `CON`, `DAT`, and `VAR` blocks may appear later in the file when they are closely associated with a specific group of methods (see Rule 3.4). The initial layout establishes the file's foundation; later blocks provide locality for subsystem-specific state and constants.

### 3.1.1 When to Use the `{Spin2_v##}` Directive

The `{Spin2_v##}` directive declares the minimum pnut-ts compiler version a file requires. Apply these rules:

1. **If a file uses a feature introduced at version N**, the directive MUST be `{Spin2_v##}` where `##` is N or later.
2. **If a file uses multiple versioned features**, the directive MUST be the highest minimum version required across all features used.
3. **If a file uses no versioned features**, no directive is required and one MUST NOT be added.

A pin higher than necessary is misleading — it suggests the file uses features it does not. A missing pin where one is required causes compile failure. Both are silent style issues this rule prevents.

**Authoritative source for feature-to-version mappings:** the P2 Knowledge Base (P2KB) lists the Spin2 version (and PASM2 version where applicable) that introduced every feature. Query P2KB before adding or removing a directive — `p2kb_get("<feature name>")` — and use the version it reports. When the answer is not in P2KB or is ambiguous, check the current pnut-ts release notes.

**Known feature-version mappings** (extend as encountered):

| Feature | Minimum directive |
|---|---|
| Typed pointers (`^BYTE`, `^WORD`, `^LONG`, `^structName`) | `{Spin2_v45}` |

### 3.2 PUB Before PRI

All PUB methods MUST appear before all PRI methods. A reader MUST be able to see the complete public API without scrolling past implementation details.

**Within the PUB section**, place the public interface first, then subgroup by functional area. A typical ordering:

1. **Lifecycle** — `start`, `stop`, `init`, `mount`, `unmount`, status queries
2. **Core operations** — the primary read/write/open/close functionality
3. **Secondary operations** — directory navigation, metadata, enumeration
4. **Convenience helpers** — typed I/O wrappers, utility methods
5. **Legacy/compatibility** — older API methods retained for backward compatibility
6. **Diagnostics** — error reporting, debug methods, stack checking
7. **Conditionally compiled PUB sections** — `#IFDEF`-gated features, ordered from most to least commonly used

When a file has distinct functional groups (e.g., file I/O, directory ops, volume ops), keep each group's PUB methods together rather than scattering them across lifecycle stages.

**Within the PRI section**, group methods by related data access or shared function. Methods that operate on the same state or implement the same subsystem belong together:

1. **Worker/dispatch infrastructure** — cog management, command dispatch
2. **Resource management** — handle pools, buffer management, allocation
3. **Mid-level operations** — the `do_*` worker-cog implementations, grouped by the data they access (e.g., file handle methods together, directory methods together, FAT chain methods together)
4. **Device-specific logic** — protocol handling, state machines
5. **Hardware abstraction** — SPI/I2C/UART pin-level communication (always last)

The goal is locality: a reader looking at one subsystem should find all its related PRI methods in one place, not scattered across the file.

### 3.3 Conditional Compilation Discipline

When using `#PRAGMA EXPORTDEF` / `#IFDEF` blocks:

- Each `#IFDEF` block MUST keep its PUB and PRI methods self-contained within matching `#IFDEF`/`#ENDIF` guards.
- An ungated method MUST NEVER accidentally land inside a conditional block.
- When a method is called from both gated and ungated code, it MUST be ungated.
- Before placing a method inside an `#IFDEF`, verify every caller. If any caller is ungated, the method MUST be ungated.
- Auto-include dependencies (where enabling feature A requires feature B) MUST be documented in a comment at the `#PRAGMA` site.

### 3.4 DAT and VAR Block Placement

A file may have one or more `DAT` and `VAR` blocks. In a small file, a single `DAT` and/or `VAR` block placed before the methods that use it is sufficient and preferred. In larger files, additional `DAT` or `VAR` blocks may appear later when they are closely associated with a specific group of methods. If a set of methods are the only accessors for certain state, placing the `DAT` or `VAR` block immediately before those methods makes the relationship clear and keeps related code together.

There is no rule limiting the number of `DAT` or `VAR` blocks. Use as many as needed to keep state declarations close to the code that uses them. Readability and logical grouping take priority over forcing everything into one block at the top.

### 3.5 CON Block Organization

A file may have multiple `CON` blocks, but each block should contain a **group of related constants** — not one or two isolated values. Proliferating many small CON blocks with only a few constants each fragments the constant namespace and makes it harder to find where values are defined.

**Group related constants together.** Error codes belong in one block. Handle flags belong in one block. Command codes for a subsystem belong in one block. If you are about to create a new CON block with two constants, check whether they belong in an existing block first.

```spin2
' REQUIRED — related constants grouped together
CON ' ---- Error Codes ----
  {Spin2_Doc_CON}
  SUCCESS               = 0
  E_TIMEOUT             = -1
  E_BAD_RESPONSE        = -2
  E_CRC_MISMATCH        = -3
  E_IO_ERROR            = -7

' FORBIDDEN — fragmented into tiny blocks
CON ' ---- Timeout Error ----
  E_TIMEOUT             = -1

CON ' ---- Response Error ----
  E_BAD_RESPONSE        = -2

CON ' ---- CRC Error ----
  E_CRC_MISMATCH        = -3
```

In larger files, additional CON blocks placed near the methods they serve are appropriate for locality (see Rule 3.1). The guidance is: **group by relationship, not by proximity to a single method.** A CON block with command codes for an entire subsystem placed near that subsystem's methods is good organization. A CON block with a single command code placed before each individual method is fragmentation.

### 3.6 DAT vs VAR Semantics

`DAT` variables are shared across all instances of an object — they are singleton state. `VAR` variables are per-instance.

- Hardware state, cog IDs, lock IDs, and shared buffers MUST use `DAT`.
- Per-instance configuration and caller-specific state MUST use `VAR`.
- NEVER place per-instance state in `DAT` — multiple callers will silently corrupt each other.
- NEVER place singleton state in `VAR` — multiple object instances will each get independent (wrong) copies.

---

## Part 4 — Documentation

All code MUST follow the **VSCode/PNUT_TS Documentation Style** as defined in the P2 Knowledge Base (`p2kbSpin2VscodePnutDocumentationStyle`). This is the standard documentation convention for the VS Code Spin2 extension and pnut-ts compiler toolchain. The rules in this section codify and extend that standard.

Key characteristics of this style:
- Documentation appears **after** the method signature, not before it
- `''` (double apostrophe) for PUB method doc-comments (extracted to `.txt` and IntelliSense)
- `'` (single apostrophe) for PRI method docs, inline comments, and `@local` tags
- Uses `@param`, `@returns`, and `@local` tags
- Only documents elements that actually exist (no `@returns` for void methods, no `@param` when there are no parameters)

### 4.1 Comment Types and Doc-Comment Rule

Doc comments are extracted by pnut-ts to `.txt` interface documents and displayed in VS Code IntelliSense. Non-doc comments are never extracted. Only use doc comments when you want the content to appear in the external API document.

| | Line | Block |
|---|---|---|
| **Doc comment** (extracted) | `''` | `{{ }}` |
| **Non-doc comment** (not extracted) | `'` | `{ }` |

**Only three things use doc comments:**

1. **File header** — `''` (double-apostrophe)
2. **PUB method descriptions** — `''` for the description, `@param`, and `@returns` tags (but NOT `@local` — those use `'`)
3. **License footer** — `{{ }}` (double-brace) at end of file

**Everything else uses non-doc comments** — because it should not appear in the extracted API document:

- PRI method documentation — `'`
- `@local` tags on PUB methods — `'`
- CON/VAR/DAT annotations — `'`
- Inline comments — `'`
- Usage notes and descriptions after the file header — `{ }`
- Internal multi-line explanations — `{ }`

**Rules:**

- `''` MUST NOT appear on PRI methods, CON declarations, DAT/VAR lines, or inline comments — it would extract them into the API document.
- `{{ }}` MUST NOT appear anywhere except the license footer — it would extract the content into the API document.
- `@local` tags MUST always use `'` (single apostrophe), never `''`, because local variables are internal.

### 4.2 File Header

Every `.spin2` file MUST have a `''` doc-comment header block containing:

- File name
- One-line purpose statement
- Author(s) and attribution
- Email or contact
- Start date and last-updated date

If the file requires a minimum compiler version, the `{Spin2_v##}` directive MUST appear on line 1, immediately before the header block. The header then starts on line 2.

```spin2
{Spin2_v47}
'' =========================================================================================
''
''   File....... my_driver.spin2
''   Purpose.... One-sentence description of what this file does
''   Authors.... Your Name
''   E-mail..... you@example.com
''   Started.... Jan 2026
''   Updated.... 04 Mar 2026
''
'' =========================================================================================
```

If no version directive is needed, the header starts on line 1.

If the file has usage notes, general description, or configuration instructions, place them in a non-doc comment block (`{ }`) immediately after the `''` header. These are visible to the reader but do not appear in the extracted interface document.

```spin2
'' =========================================================================================
''
''   File....... my_driver.spin2
''   Purpose.... One-sentence description
''   Authors.... Your Name
''   ...
''
'' =========================================================================================

{ Description and usage notes:

   This driver provides ...

   Usage:
     1. Create an OBJ reference
     2. Call mount() with pin numbers
     3. ...
}
```

### 4.3 PUB Method Documentation

*P2KB reference: `p2kbSpin2VscodePnutDocumentationStyle`*

Every PUB method MUST have `''` doc comments immediately after the complete signature, with no blank line between the signature and the first `''`.

**Multi-line signatures:** When a signature uses line continuations (`...`), the `''` doc comments go after the final line of the signature — the line without `...`. Doc comments never appear on partial signature lines.

```spin2
PUB do_card_info() | wasMounted, card_ok,               ...
  ocr, sizeMB, spiHz, psn, mdtYear, mdtMonth,           ...
  pnm[2], p_mfr, p_type, p_spec, p_fs,                  ...
  oemBuf[3], partStart, idx, nLen
'' Display detailed card identification summary.
```

**Required structure:**

1. **Description** — one sentence starting with a verb phrase
2. **Blank `''` separator**
3. **`@param` tags** — one per parameter, in signature order
4. **`@returns` tags** — one per return variable
5. **`@local` tags** — using `'` (NOT `''`), separated from `@returns` by a blank line, and followed by a blank line before code

```spin2
PUB start(pinCS, pinMOSI, pinMISO, pinSCK) : status | curCmd
'' Start the worker cog and initialize the hardware interface.
''
'' @param pinCS - Chip select pin number
'' @param pinMOSI - Master Out Slave In pin number
'' @param pinMISO - Master In Slave Out pin number
'' @param pinSCK - Serial clock pin number
'' @returns status - SUCCESS (0) or negative error code

' Local Variables:
' @local curCmd - Command being dispatched 

    {method body}
```

**Rules:**

- **Blank line before code is REQUIRED.** After the last documentation line (`''`, `'`, or `@local`), there MUST be a blank line before the first line of executable code. This is a VSCode/PNUT_TS style requirement.
- **No documentation for nonexistent elements.** Do not write `@param` when there are no parameters. Do not write `@returns` for void methods. Do not write `@local` when there are no local variables. Only document elements that actually exist in the signature.
- BLANK line before ' Local Variables:
- No `@local` with `''` — locals are internal, always use `'`.
- Every `@param` name MUST match a parameter in the signature.
- Every `@returns` name MUST match a return variable in the signature.
- Descriptions MUST reflect current behavior — no stale references to removed or renamed APIs.

**Void method example (no params, no returns, no locals):**

The blank `''` separator after the description is always required — even when there are no `@param`, `@returns`, or `@local` tags. This is consistent with the P2KB VSCode/PNUT_TS documentation standard, where the blank separator line is always step 2 in the documentation structure. After the last documentation line, a blank line before code is required as usual.

```spin2
PUB initialize()
'' Initialize the module to default operational state.
''

    configurePins()
    resetVariables()
```

### 4.4 PRI Method Documentation

*P2KB reference: `p2kbSpin2VscodePnutDocumentationStyle`*

PRI methods use `'` (single apostrophe) for all documentation. Same structure as PUB but nothing is extracted to the interface document.

```spin2
PRI setError(code) : codeOut | localVar
' Store error code in per-cog slot and return it for assignment chaining.
'
' @param code - Error code to store
' @returns codeOut - The same error code passed in

' Local Variables:
' @local localVar - used for ...
```

### 4.5 Block Declaration Labels

Comments on the same line as `CON`, `DAT`, `VAR`, `OBJ`, `PUB`, or `PRI` keywords appear in the VS Code Outline panel. These serve as navigation aids.

**Rules:**

- MUST use `'` (single apostrophe) — NEVER `''` on block declaration lines.
- Keep labels short and descriptive — they are navigation aids, not documentation.
- Use `---- Label ----` dash format for section separators. The three-to-four dashes surrounding the label text are **required** — VS Code Outline gathers these markers for navigation. This is the standard format, not decoration.

```spin2
' REQUIRED — short dashes around label text, gathered by VS Code Outline
CON ' ---- Error Codes ----

DAT ' ---- Singleton Control ----

VAR ' per-instance state
```

**FORBIDDEN — full-width decorative borders on block declaration lines:**

Full-width borders (`═══`, `───`, `___`, etc.) that span the line without meaningful label text are forbidden. They appear in the Outline as noise instead of useful navigation text.

```spin2
' NEVER do this — the border appears in the Outline instead of useful text
CON ' ═══════════════════════════════════════════

' ALSO FORBIDDEN — no label, just decoration
DAT ' ───────────────────────────────────────────
```

**`{Spin2_Doc_CON}` — Marking Public API Constants:**

The `{Spin2_Doc_CON}` directive identifies a CON block whose constants are part of the object's **public API**. Constants in marked blocks are exported to the generated `.txt` interface document and are the constants that consumers of the object reference via the `OBJ` prefix (e.g., `driver.SUCCESS`, `driver.E_TIMEOUT`).

**When to use `{Spin2_Doc_CON}`:**

- Error codes, status values, and named results that callers check against
- Mode enums and configuration constants that callers pass as parameters
- Buffer sizes, limits, and offsets that callers need for correct usage
- Any constant a consumer of the object must reference by name

**When NOT to use `{Spin2_Doc_CON}`:**

- Internal implementation constants (command codes, buffer offsets, bit masks used only inside the driver)
- Constants used only by PRI methods
- Constants that are meaningless outside the object's implementation

A CON block without `{Spin2_Doc_CON}` is internal — its constants do not appear in generated documentation and are not intended for external use.

**Placement:** Place the directive on the first line inside the block, NOT on the `CON` declaration line itself (which would pollute the Outline label).

```spin2
' REQUIRED — directive on first line inside the block
CON ' ---- Error Codes ----
  {Spin2_Doc_CON}
  SUCCESS           = 0
  E_TIMEOUT         = -1

' FORBIDDEN — directive on the declaration line
CON ' ---- Error Codes ----  {Spin2_Doc_CON}
  SUCCESS           = 0
```

### 4.6 CON / VAR / DAT Declaration Comments

Individual declarations use `'` (single apostrophe) comments. VS Code gives higher hover priority to a preceding comment (line above, no blank line gap) than to a trailing comment (same line).

- Use preceding comments for important descriptions.
- Use trailing comments for brief annotations.

```spin2
CON ' ---- Driver Modes ----
  ' Current operating mode of the driver
  MODE_NONE       = 0       ' not initialized
  MODE_RAW        = 1       ' raw access only
  MODE_FILESYSTEM = 2       ' full filesystem access
```

### 4.7 Enumerated Constant Groups

When a `CON` block defines an auto-numbered enumeration (`#0`, `#1`, etc.), document the group with a preceding comment block that lists every value and its meaning. This follows the VSCode/PNUT_TS style for enum documentation.

```spin2
CON ' ---- Drive States ----
  ' Motor control states for drive system:
  '  DCS_STOPPED   - Motor completely stopped, no power
  '  DCS_SPIN_UP   - Motor ramping up to target speed
  '  DCS_AT_SPEED  - Motor running at target speed
  '  DCS_SPIN_DOWN - Motor ramping down to stop
  #0, DCS_STOPPED, DCS_SPIN_UP, DCS_AT_SPEED, DCS_SPIN_DOWN
```

The group comment serves as a quick reference so the reader does not have to count offsets to determine each constant's value or purpose.

### 4.8 STRUCT Declarations

STRUCT definitions live inside CON blocks. Document each struct with a preceding comment block that lists every member, its type, and its purpose — the same pattern as enumerated constant groups (Rule 4.7). The STRUCT declaration line is the compact code form; the preceding comment is the readable reference.

```spin2
  ' CID register (16 bytes, big-endian from card):
  '  mid      - Manufacturer ID (1 byte)
  '  oid[2]   - OEM/Application ID (2 bytes)
  '  pnm[5]   - Product name (5 bytes ASCII)
  '  prv      - Product revision (1 byte, BCD)
  '  psn[4]   - Product serial number (4 bytes)
  '  mdt[2]   - Manufacturing date (2 bytes)
  '  crc      - CRC7 checksum (1 byte)
  STRUCT cid_t(BYTE mid, BYTE oid[2], BYTE pnm[5], BYTE prv, BYTE psn[4], BYTE mdt[2], BYTE crc)
```

For large structs with many members (e.g., VBR at 512 bytes), group related members in the comment:

```spin2
  ' VBR / FAT32 BPB (512 bytes, little-endian):
  '  jumpBoot[3]    - Boot jump instruction
  '  oemName[8]     - OEM name string
  '  -- BPB geometry --
  '  bytesPerSec    - Bytes per sector (always 512)
  '  secPerClus     - Sectors per cluster (power of 2)
  '  reservedSec    - Reserved sectors before FAT
  '  numFats        - Number of FAT copies (always 2)
  '  ...
  STRUCT vbr_t(BYTE jumpBoot[3], BYTE oemName[8], WORD bytesPerSec, ...)
```

### 4.9 No Horizontal Lines Inside CON Blocks

Horizontal separator lines (`═══`, `---`, `___`, etc.) inside `CON` blocks get extracted into the API document along with the constants. They clutter the generated documentation and add no value.

**FORBIDDEN inside CON blocks:**

```spin2
CON ' handle configuration
  ' ═══════════════════════════════════════════════════════════════════════════
  ' FILE HANDLE SYSTEM
  ' ═══════════════════════════════════════════════════════════════════════════
  MAX_OPEN_FILES = 6
```

**REQUIRED — use plain comments without decorative lines:**

```spin2
CON ' handle configuration
  ' FILE HANDLE SYSTEM
  MAX_OPEN_FILES = 6
```

This applies to any comment inside a `CON` block. Decorative lines inside `DAT` blocks are acceptable since DAT contents are not extracted.

### 4.10 Internal Block Comments

For multi-line internal documentation (architecture diagrams, protocol descriptions, algorithm explanations), use `{ }` non-doc blocks — NEVER `{{ }}`:

```spin2
{ SPI Mode 0 Timing:
  Clock idles low, data sampled on rising edge.
  CS must be held low for entire transaction.
  Minimum 8 clock cycles between commands.
}
```

---

## Part 5 — Coding Practices

### 5.0 No Unused Parameters, Return Values, or Locals

Method signatures MUST NOT contain parameters, return variables, or local variables that are never used in the method body. Unused declarations are dead weight — they mislead readers, waste stack space, and suggest unfinished work.

```spin2
' FORBIDDEN — unused parameter and local
PRI scanDir(pPath, maxDepth) : status | entryIdx, tempBuf
    ' maxDepth is never read, tempBuf is never assigned
    ...

' REQUIRED — remove what you don't use
PRI scanDir(pPath) : status | entryIdx
    ...
```

When refactoring removes the last use of a parameter, return value, or local, remove it from the signature immediately. Do not leave it behind for hypothetical future use.

### 5.1 Return Variables MUST Be Assigned

Every declared return variable MUST be explicitly assigned a value. NEVER rely on Spin2's implicit zero initialization — it hides intent and creates fragile code.

```spin2
' REQUIRED — explicit default
PUB openFile(pFilename) : handle
    handle := -1              ' default: no handle
    ...

' FORBIDDEN — relies on implicit zero
PUB freeSpace() : sectors
    ...
    ' sectors is never assigned, silently returns 0
```

### 5.2 Single Exit Point Per Method

Methods MUST have a single exit point at the end of the method body. NEVER use early `return` statements from multiple locations.

**Rationale:** Early returns make `debug()` instrumentation impossible to trust. A `debug()` placed after an early return silently never executes. A single exit point guarantees all end-of-method instrumentation is always reached.

Use control flow (`if`/`else`, result variables, `quit` from loops) to route all paths to the method's natural end.

```spin2
' REQUIRED — single exit, all paths reach the end
PRI doOpenRead(pFilename) : status
    status := E_FILE_NOT_FOUND
    if searchDirectory(pFilename)
        status := allocateHandle()
        if status >= 0
            ...
            status := SUCCESS
    debug("  [doOpenRead] status=", sdec_(status))

' FORBIDDEN — early returns skip debug instrumentation
PRI doOpenRead(pFilename) : status
    if not searchDirectory(pFilename)
        return E_FILE_NOT_FOUND         ' debug below never runs
    status := allocateHandle()
    if status < 0
        return status                    ' debug below never runs
    ...
    debug("  [doOpenRead] status=", sdec_(status))
```

### 5.3 Exiting Loops: `quit`, Never `return`

NEVER use `return` from inside a `repeat` loop. Set the return variable and use `quit` to break the loop. For nested loops, use `quit` at each level with a guard check between levels.

```spin2
' REQUIRED — quit from loop, single exit
PRI pollForToken(pBuf) : status | timeout, data
    status := E_TIMEOUT
    timeout := getct() + clkfreq
    repeat
        data := transfer($FF)
        if data == START_TOKEN
            status := SUCCESS
            quit
        if getct() - timeout > 0
            quit
    if status == SUCCESS
        readPayload(pBuf)

' FORBIDDEN — return from inside loop
PRI pollForToken(pBuf) : status | timeout, data
    ...
    repeat
        data := transfer($FF)
        if data == START_TOKEN
            readPayload(pBuf)
            return SUCCESS                ' breaks single-exit rule
        if getct() - timeout > 0
            return E_TIMEOUT              ' breaks single-exit rule
```

For doubly-nested loops, propagate `quit` upward:

```spin2
repeat attempt from 1 to MAX_RETRIES
    repeat                                ' inner poll loop
        data := transfer($FF)
        if data == START_TOKEN
            quit
        if getct() - timeout > 0
            status := E_TIMEOUT
            quit
    if status < 0
        quit                              ' propagate error to outer loop
    ' ... process data ...
' single exit point here
```

### 5.4 API Methods Return Error Codes, Not Booleans

All PUB methods that perform operations MUST return `SUCCESS` (0) on success or a negative error code on failure. No PUB method returns `true`/`false` for operation status.

**Exception — boolean query methods:** When a PUB method checks for a single on/off or true/false condition, returning a boolean is correct. Name these methods with an `is` or `has` prefix to make the boolean intent clear:

```spin2
PUB isMounted() : bMounted
PUB isFileContiguous(pPath) : bContiguous
PUB isHighSpeedActive() : bActive
PUB hasCard() : bPresent
PUB eofHandle(handle) : bAtEnd
```

These answer yes/no questions, not operation outcomes. If the query can also fail (e.g., card not mounted), return the error code and let the caller check `error()` separately.

### 5.4.1 Boolean Precision — TRUE/FALSE Only

Boolean return values MUST be the compiler's `TRUE` (all bits set, `-1`) or `FALSE` (`0`). NEVER return `1` for true. A value of `1` is non-zero (truthy in an `if` test) but it is NOT `TRUE` — it is not the bitwise inverse of `FALSE`, and `== TRUE` will fail.

Spin2's comparison operators (`==`, `>=`, `<`, `<>`, etc.) produce correct `TRUE`/`FALSE` values. Use them directly:

```spin2
' CORRECT — comparison operator produces TRUE/FALSE
bContiguous := (fragCnt == CONTIGUOUS_FRAGMENTS)

' FORBIDDEN — returns 1, not TRUE
bContiguous := 1
```

When testing a boolean value, ALWAYS compare against `TRUE` or `FALSE` — never against `1` or `0`:

```spin2
' REQUIRED
if bMounted == TRUE
if bValid == FALSE

' FORBIDDEN — works by accident but is not semantically correct
if bMounted == 1
if bValid == 0
```

When a method returns a boolean, its name MUST signal boolean semantics with an `is`, `has`, or `b` prefix so callers know to test against `TRUE`/`FALSE`.

### 5.4.2 Named Constants Communicate Intent

Named constants MUST communicate *why* a value matters at the point of use, not just *what* the value is. The reader should understand the intent without domain knowledge of the raw number.

```spin2
' REQUIRED — intent is clear at point of use
CON
    CONTIGUOUS_FRAGMENTS = 1    ' a file with 1 fragment is contiguous

if fragCnt == CONTIGUOUS_FRAGMENTS
    ' file is contiguous

' FORBIDDEN — requires domain knowledge to understand
if fragCnt == 1
```

When a named constant represents a condition that can be expressed as a query method, prefer the method at external call sites where readability matters most. `isFileContiguous()` is more communicative than `fragCnt == CONTIGUOUS_FRAGMENTS`. However, in performance-critical paths (inside PRI worker methods, tight loops, code that avoids command dispatch overhead), use the named constant directly — it communicates the same intent without the cost of a method call. Use the constant in the *implementation*; use the wrapper method at external *call sites* where the overhead is acceptable.

### 5.5 Prefer Multiple Return Values Over Pointer Parameters

Spin2 supports up to **15 return values** per method (see P2KB `p2kbSpin2MethodDefinition`). When a method needs to return more than one piece of information, declare multiple return variables instead of passing pointer parameters to be filled in.

In C or assembly, passing addresses of variables as "out parameters" is the only way to return multiple values. In Spin2, this pattern is unnecessary and inferior: it hides the method's outputs from the signature, prevents the compiler from managing the storage, and forces the caller to allocate and pass buffer addresses manually.

```spin2
' REQUIRED — multiple return values in the signature
PUB stats(device) : usedBlocks, freeBlocks, fileCount
'' Return usage statistics for the specified device.
''
'' @param device - Device identifier (DEV_SD or DEV_FLASH)
'' @returns usedBlocks - Number of blocks in use
'' @returns freeBlocks - Number of blocks available
'' @returns fileCount - Number of files on the device

    usedBlocks := countUsed(device)
    freeBlocks := countFree(device)
    fileCount := countFiles(device)

' Caller — clean, readable, no pointer management
used, free, files := driver.stats(driver.DEV_SD)


' FORBIDDEN — pointer "out parameters" when return values would work
PUB stats(device, pUsed, pFree, pFileCount)
    LONG[pUsed] := countUsed(device)
    LONG[pFree] := countFree(device)
    LONG[pFileCount] := countFiles(device)

' Caller — forced to manage addresses
LONG used, free, files
driver.stats(driver.DEV_SD, @used, @free, @files)
```

**When pointer parameters ARE appropriate:**

- **Large data buffers** — reading a sector into a caller-provided byte array (`pBuffer`). The data is too large for return values (which are LONGs).
- **Shared memory** — filling a caller-allocated structure or array that must persist beyond the method call.
- **PASM2 interop** — passing hub addresses to assembly code that writes results via `WRLONG`.

The test: if the values you need to return are LONGs (or can fit in LONGs) and there are 15 or fewer of them, use return variables. Use pointer parameters only when the data does not fit the return value mechanism.

### 5.6 Error Propagation: Never Overwrite Specific Errors

When a method calls a sub-operation that returns a specific error code, the caller MUST preserve that specific error. NEVER overwrite a specific error with a generic one.

```spin2
' REQUIRED — preserve the specific error from mount internals
PRI doMount() : status
    status := initializeCard()
    if status < 0
        ' status already holds E_NO_CARD, E_TIMEOUT, etc.
        ' just fall through — do not overwrite

' FORBIDDEN — destroys diagnostic information
PRI doMount() : status
    status := initializeCard()
    if status < 0
        status := E_NOT_MOUNTED           ' overwrites the real cause
```

### 5.7 Named Constants — No Magic Numbers

Every numeric literal with semantic meaning MUST be a named constant defined in a `CON` block. The constant name documents meaning at the point of use, travels with the value, and cannot drift out of sync when the value changes.

**Categories that REQUIRE named constants:**

- Command codes and status values
- Error codes
- Hardware register offsets, bit masks, and field widths
- Buffer and array sizes
- Loop bounds (including simple ones like `0 to 7`)
- Timeout values and retry counts
- Protocol constants (signatures, magic numbers, field sizes)

```spin2
' REQUIRED
CON
    MAX_COGS            = 8
    SECTOR_SIZE         = 512
    MAX_RETRIES         = 3
    INIT_TIMEOUT_MS     = 1000
    MBR_SIGNATURE       = $AA55
    MBR_SIG_OFFSET      = $1FE

repeat idx from 0 to MAX_COGS - 1
timeout := getct() + (clkfreq / 1000) * INIT_TIMEOUT_MS
if WORD[@buffer + MBR_SIG_OFFSET] <> MBR_SIGNATURE

' FORBIDDEN
repeat idx from 0 to 7
timeout := getct() + (clkfreq / 1000) * 1000
if WORD[@buffer + $1FE] <> $AA55
```

**Permitted bare literals (exceptions):**

| Value | Permitted use |
|-------|--------------|
| `0` | Initialization, zero comparison, null pointer |
| `-1` | Common sentinel or "not found" return |
| `4` | LONG-to-byte conversion (`nLongs * 4`) where the factor is inherent to P2 architecture |

Even these MUST be named if the meaning is not obvious from immediate context. When in doubt, name it.

### 5.8 Dedicated Cog Architecture Pattern

When a driver uses a dedicated worker cog (common for hardware I/O on P2):

- All hardware pin operations MUST execute inside the worker cog. PUB methods are caller-cog wrappers that send commands to the worker via a parameter block and wait for completion.
- NEVER perform SPI, I2C, UART, or other pin-level operations directly from a PUB method. The caller cog does not own the pins.
- The command dispatch pattern is: caller writes parameters to shared DAT → caller writes command code → caller waits via `WAITATN()` → worker sees command → worker executes → worker signals via `COGATN()`.
- Multi-cog access MUST be serialized with a hardware lock (`LOCKTRY`/`LOCKREL`).

```spin2
' REQUIRED — PUB wrapper sends command to worker
PUB readSector(sectorNum, pBuffer) : status
    pb_param0 := sectorNum
    pb_param1 := pBuffer
    status := sendCommand(CMD_READ_SECTOR)

' FORBIDDEN — PUB method directly touches SPI pins
PUB readSector(sectorNum, pBuffer) : status
    pinl(csPin)                           ' WRONG: caller cog does not own pins
    spiTransfer(...)
    pinh(csPin)
```

When adding a new PUB method that requires hardware access, ALWAYS: (1) define a new command code in CON, (2) add a `do_*` PRI method for the worker, (3) add the case to the worker dispatch loop, (4) write a PUB wrapper that calls `sendCommand()`.

### 5.9 Shared Bus Switching

When multiple devices share a communication bus (e.g., SPI with separate CS lines):

- Device switching MUST be lazy — only reconfigure pins when the active device changes.
- After switching away from a device that uses smart pins, use `PINCLEAR()` (not `PINFLOAT()`) to fully release pins. `PINFLOAT()` only clears DIR; the WRPIN mode register survives and will interfere.
- If a shared pin serves double duty across devices (e.g., a CS pin that doubles as another device's clock), the first device may need re-initialization after the second device operates.

---

## Part 6 — Regression Tests

Tests are documentation. A developer reading a test file MUST learn the correct way to call the API.

### 6.1 All Comparisons Use Named Constants

NEVER compare against raw numeric literals in assertions. Always use the driver's named constants.

```spin2
' REQUIRED
status := driver.mount(driver.DEV_SD)
utils.evaluateSingleValue(status, @"mount(DEV_SD)", driver.SUCCESS)

' FORBIDDEN — raw 0 hides meaning
utils.evaluateSingleValue(status, @"mount(DEV_SD)", 0)
```

This applies to:
- **Status codes** — use `driver.SUCCESS`, `driver.E_FILE_NOT_FOUND`, etc.
- **Device identifiers** — use `driver.DEV_SD`, `driver.DEV_FLASH`, etc.
- **File modes** — use `driver.FILEMODE_READ`, `driver.FILEMODE_WRITE`, etc.
- **Pool limits** — use `driver.MAX_OPEN_FILES`, not raw numbers.

### 6.2 Never Redefine Driver Constants Locally

This is Rule 2.4 applied to test files. Reference the driver's constants directly via the OBJ prefix. NEVER create local copies.

```spin2
' FORBIDDEN
CON
    E_NOT_MOUNTED = -20       ' local copy that can become stale

' REQUIRED
utils.evaluateSingleValue(status, @"error check", driver.E_NOT_MOUNTED)
```

### 6.3 Assertion Method Selection

Choose the assertion that communicates intent:

| Scenario | Correct assertion | Example |
|----------|------------------|---------|
| Status code | `evaluateSingleValue` | `evaluateSingleValue(status, @"mount()", driver.SUCCESS)` |
| Boolean condition | `evaluateBool` | `evaluateBool(handle >= 0, @"valid handle", true)` |
| Exact numeric value | `evaluateSingleValue` | `evaluateSingleValue(fileSize, @"size", 1024)` |
| Non-zero check | `evaluateNotZero` | `evaluateNotZero(pLabel, @"label pointer")` |
| Value in range | `evaluateRange` | `evaluateRange(speed, @"SPI freq", 20_000_000, 26_000_000)` |
| Sub-check in series | `evaluateSubValue` | `evaluateSubValue(dataByte, @"byte[0]", $AA)` |

**Critical rule:** NEVER use `evaluateBool()` on status code return values. Status codes MUST be compared against named constants via `evaluateSingleValue()`.

`evaluateBool()` is ONLY for testing values that are already boolean (TRUE/FALSE) — either returned from a boolean method (`isMounted()`, `isFileContiguous()`) or computed as a boolean expression. Test boolean values against `TRUE` or `FALSE`, never against `1` or `0`.

```spin2
' CORRECT — method returns a boolean, test against TRUE
bContig := dfs.isFileContiguous(dfs.DEV_SD, @filename)
utils.evaluateBool(bContig, @"file is contiguous", TRUE)

' CORRECT — boolean method result tested directly
utils.evaluateBool(dfs.isMounted(dfs.DEV_SD), @"SD is mounted", TRUE)

' FORBIDDEN — mount() returns a status code, not a boolean
utils.evaluateBool(status, @"mount()", true)

' FORBIDDEN — handle >= 0 is a validity check; express intent with named constant or method
utils.evaluateBool(handle >= 0, @"handle is valid", true)

' REQUIRED — for handle validity, compare the handle value against a named constant
' or define a local boolean with an intent-communicating name
bValidHndl := (hndl >= 0)
utils.evaluateBool(bValidHndl, @"handle is valid", TRUE)
```

The goal is that assertion code reads like a statement of intent: "the handle is valid" or "the file is contiguous" — not like a numeric comparison.

### 6.4 Buffer Sizes as Named Constants

Test buffer sizes MUST be defined as named constants in the CON block, not scattered as raw numbers.

```spin2
' REQUIRED
CON
    TEST_BUF_SIZE = 512       ' one sector

DAT
    testBuf  BYTE  0[TEST_BUF_SIZE]

    bytefill(@testBuf, 0, TEST_BUF_SIZE)

' FORBIDDEN
    bytefill(@readBuffer, 0, 512)
```

When a test uses a specific size to exercise a boundary condition, add a comment explaining why:

```spin2
' Write 513 bytes to force a sector boundary crossing (512 + 1)
utils.fillBufferWithPattern(@writeBuf, SECTOR_SIZE + 1, 0)
```

### 6.5 Test Lifecycle Pattern

Every test file MUST demonstrate the recommended lifecycle in its entry method:

```spin2
PUB go() | status
    ' 1. Initialize driver (start worker cog)
    driver.init(PIN_CS, PIN_MOSI, PIN_MISO, PIN_SCK)

    ' 2. Mount device
    status := driver.mount(driver.DEV_SD)
    if status <> driver.SUCCESS
        debug("Mount failed: ", sdec_(status))
    else
        ' 3. Run tests
        runTests()

        ' 4. Unmount
        driver.unmount(driver.DEV_SD)

    ' 5. Stop and report results (always reached — single exit point)
    driver.stop()
    utils.ShowTestEndCounts()
    debug("END_SESSION")
```

### 6.6 Comment Expected Errors

When a test deliberately triggers an error condition, MUST include a comment explaining why the error is expected:

```spin2
' Opening a file before mount should fail with E_NOT_MOUNTED
status := driver.open(driver.DEV_SD, @"ANY.TXT", driver.FILEMODE_READ)
utils.evaluateSingleValue(status, @"open() before mount", driver.E_NOT_MOUNTED)

' Opening more than MAX_OPEN_FILES handles should exhaust the pool
' (handles 0 through MAX_OPEN_FILES-1 are already open from previous group)
handle := driver.open(driver.DEV_SD, @"EXTRA.TXT", driver.FILEMODE_READ)
utils.evaluateSingleValue(handle, @"pool exhaustion", driver.E_NO_FREE_HANDLE)
```

### 6.7 Tests MUST Pass

Regression tests MUST run without errors before and after any code change. A test suite with failures MUST NOT be committed. If a code change breaks a test, either the code or the test must be fixed — never ignore a failing test.

---

## Checklist

Before committing any `.spin2` file, verify:

**Language:**
- [ ] No Unicode characters anywhere in the file (ASCII only)
- [ ] No `=>` used as comparison (only `>=`)
- [ ] No identifier collisions with built-ins (case-insensitive check)
- [ ] No method name duplicates (no overloading)
- [ ] No `@""` empty string literals
- [ ] Pointer dereferences use `BYTE[ptr]`/`WORD[ptr]`/`LONG[ptr]` or `[ptr]` (not `*`)
- [ ] Struct pointer returns from OBJ methods received with `[var] := obj.method()` brackets
- [ ] DAT-stored `@` addresses resolved with `@@` at runtime
- [ ] Typed pointers (`^BYTE` etc.) only used with `{Spin2_v45}` directive present
- [ ] Stale `.obj` files deleted after editing included drivers

**Naming:**
- [ ] No single-letter variable names (except PASM2 registers)
- [ ] No generic container names (`result`, `value`, `temp`, `data`, `ret`, `buf`, `info`) — all names describe the data carried
- [ ] Return variables named for the specific data they represent
- [ ] All object constants referenced via object prefix (never copied to local CON)
- [ ] Same parameter name has identical `@param` description across all methods

**Structure:**
- [ ] PUB methods all appear before PRI methods
- [ ] Lifecycle methods appear first in PUB section
- [ ] `#IFDEF` blocks are self-contained; ungated methods are not inside conditional blocks
- [ ] `DAT` used for singleton state, `VAR` for per-instance state

**Documentation:**
- [ ] Follows VSCode/PNUT_TS Documentation Style (P2KB standard)
- [ ] Every PUB method has `''` doc comments with `@param`/`@returns`
- [ ] Every PRI method has `'` doc comments with `@param`/`@returns`/`@local`
- [ ] No `@param`/`@returns`/`@local` tags for nonexistent elements
- [ ] Blank line after documentation block, before code
- [ ] `@local` tags use `'` (never `''`)
- [ ] CON/DAT/VAR/OBJ declaration lines use `'` (never `''`)
- [ ] No `{{ }}` blocks except file header and license
- [ ] Enumerated constant groups have preceding group comment listing all values
- [ ] Block declaration labels use `---- Label ----` dash format for Outline navigation (no full-width decorative borders)

**Practices:**
- [ ] Every return variable explicitly assigned a default value
- [ ] Single exit point per method (no early `return` statements)
- [ ] `quit` used to exit loops (never `return` from inside a loop)
- [ ] API methods return `SUCCESS`/error codes, not booleans
- [ ] Multiple return values used instead of pointer out-parameters (when data fits in LONGs)
- [ ] Specific error codes preserved (never overwritten with generic errors)
- [ ] No magic numbers — all semantic literals are named constants
- [ ] Hardware operations route through the worker cog (never from caller PUB methods)

**Tests:**
- [ ] All comparisons use named driver constants (never raw numbers)
- [ ] No locally redefined driver constants
- [ ] `evaluateBool()` never used on status code return values
- [ ] Buffer sizes defined as named CON values
- [ ] Expected error tests have explanatory comments
- [ ] Test lifecycle (init/mount/test/unmount/stop) is complete
- [ ] All tests pass

---

*Spin2 Authoring Guide v1.0 -- for pnut-ts compiler and VS Code Spin2 extension*
