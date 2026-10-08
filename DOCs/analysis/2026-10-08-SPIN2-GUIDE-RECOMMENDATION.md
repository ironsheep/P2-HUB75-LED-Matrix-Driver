# Recommendation: Spin2 authoring guide, constant forwarding and enum value allocation

**For:** `central:spin2-authoring-guide` (`~/.claude/skills-docs/guides/spin2-authoring-guide.md`)
**From:** p2-LED-Matrix-Driver, the 4.0.0 full style audit (2026-10-08,
`DOCs/analysis/2026-10-08-4.0.0-STYLE-AUDIT.md`)
**Status:** recommendation for Stephen; nothing in the central guide has been changed.

## Why this is needed

The audit, read against rule 2.4 as written, flagged two patterns the driver uses on purpose:

- an interface object re-exporting another object's constants (`display.DIR_TO_LEFT =
  scroller.DIR_TO_LEFT`, `hub75Bffrs.HUB75_ADAPTER_1 = hwEnum.HUB75_ADAPTER_1`);
- enumerations whose numbering looks arbitrary and overlapping (`ADDR_*` from 2, `DEPTH_*` from 3,
  adapters at 10/20/30, rotations at `$20`).

The arbiter then recommended removing the first and renumbering the second. The project history shows
both are deliberate (traced below). Stephen's rulings (2026-10-08):

- *"In general the object that provides the control interface provides the parameter values (enums
  for constants) for that interface. They should not be divorced from each other."*
- *"If you have values, you do not want different values for the same enums coming from different
  sources, so now you begin to centralize them."*
- *"Forwarding has to be allowed and used only where appropriate."*

The guide states none of this, so the next audit makes the same mistake. Two changes close it.

## Change 1: rule 2.4 distinguishes a copied value from a forwarded name

**Current:** "any constant defined by that object MUST be referenced through the object name — NEVER
copied into a local `CON` block … This rule has no exceptions."

**Problem:** it treats `X = 10` (a copy) and `X = obj.X` (a forward) as the same act. Only the copy
can drift; the forward is how an interface object provides values that are defined behind it. Spin2
gives an object no access to its parent's constants, so a value used both by an interface object and
by an object it delegates to *must* be defined in the lower object; a program reaches it only through
a forward, or by declaring the lower object itself. Declaring it can be wasteful (here, a
`scrollingText` instance and its VAR, just to read `DIR_TO_LEFT`) and teaches programs to declare
objects they never call.

**Proposed text** (replaces the last paragraph of 2.4, and adds 2.4.1):

> **A copied value is forbidden without exception.** `MAX_FILES = 6` beside an object that defines
> `MAX_OPEN_FILES` is a second source of truth.
>
> ### 2.4.1 Forwarding: an interface provides the values of its own methods · **T1+T2**
>
> The object that provides a control interface provides the values (enumerations, status codes)
> its methods take and return. When those values are defined in an object behind the interface,
> the interface **forwards** them by reference:
>
> ```spin2
> CON ' ---- Scrolling ----
>     {Spin2_Doc_CON}
>     ' scrolling direction (forwarded from scroller, which defines them):
>     DIR_TO_LEFT    = scroller.DIR_TO_LEFT
>     DIR_TO_RIGHT   = scroller.DIR_TO_RIGHT
> ```
>
> A forward is a name, not a value: it cannot drift. Forward **only** when all three hold:
>
> 1. the forwarding object's own **PUB** methods take or return the value;
> 2. the value is defined in an object behind it, where visibility or value allocation (rule 4.7.1)
>    requires it to live;
> 3. without the forward, a caller would declare that object only to read a constant.
>
> Rules:
>
> - Forward the **whole** set the method takes, never a subset.
> - Forward from the **defining** object, never a forward of a forward.
> - Put forwards in a `{Spin2_Doc_CON}` block, with a comment naming the object that defines them.
> - Never forward inside a code base where the consumer already declares the defining object: driver
>   internals reference the owner directly.
> - Never forward a set the interface's own methods do not use. That is convenience aggregation, and
>   it divorces values from the interface that gives them meaning.
>
> *Script detects* `NAME = obj.NAME` lines; *agent judges* the three conditions.

**Applied in this project** (the rework this recommendation implies):

| Interface | Forwards | Because its methods… |
|---|---|---|
| `display` | `TEXT_FONT_*`, `DIR_*`, `SCROLL_*`, `FACE_*`, `HUB75_ADAPTER_*`, its status codes | take or return them |
| `hwBufferAccess` | `HUB75_ADAPTER_*`, `DEPTH_*`, `ROT_*` | `indexForHub75ChainId()`, `colorDepth()`, `displayRotation()` |
| `display_bmp` | content `ROT_*`, its status codes | `placeBMP()` / `fillScreenFromBMP()` |
| `panel`, `screenUtils`, `scrollingText` | nothing | internal: they declare `hwEnum` and use it directly |

## Change 2: rule 4.7 gains value allocation

**Current:** 4.7 asks only that a group comment list every value and its meaning.

**Problem:** a group's starting value can carry meaning a reader cannot see. Without a stated reason
it reads as arbitrary, and an auditor "fixes" it. In this project the audit and the arbiter both
called deliberate allocations defects.

**Proposed text** (adds 4.7.1 after 4.7):

> ### 4.7.1 Enumeration Values Are Allocated, Not Incidental · **T2**
>
> When values from different groups meet, define them once, in one place that every consumer can
> see. For a hardware description that the user's configuration file also names, that place is a
> constants-only object both include, because a configuration object cannot see the driver. Allocate
> the values on purpose, and **say in the group comment which kind of allocation the base is**:
>
> - **Quantity:** the value *is* the meaning, used in arithmetic. `#0[16], PIN_GROUP_P0_P15, …` gives
>   the base pin; `#2, ADDR_UNKNOWN, ADDR_ABC, …` makes `ADDR_ABC` = 3 address lines.
> - **Bit field:** values combined with `|` occupy disjoint bits. Within a kind of word that must
>   never be combined, one word is one bit, so combining two is detectable (`CHIP_*` in the low byte,
>   flags from `$100`; wiring words one-hot per field).
> - **Distinct identity:** two kinds of number that a caller could confuse get ranges that cannot
>   overlap. Adapter IDs are 10/20/30 so an ID is never mistaken for a chain index 0..2. Parameters
>   of the **same call** get distinct ranges, so swapped arguments are detectable: `DIR_*` from 10,
>   `SCROLL_*` from 0.
> - **Arbitrary:** start at 0 (or 1 when 0 must mean "unset"), and say so.
>
> Ranges need to be distinct only where values meet: in one call, or where two identities can be
> confused. Renumbering a deliberate base silently breaks arithmetic, bit decoding or a validation
> range. Treat it as an interface change.
>
> **Aliases** (two names for one value) are allowed only to keep existing user code compiling. Mark
> them as aliases and name the preferred form: `ROT_NONE = ROT_0 ' alias kept for v3 configs;
> prefer ROT_0`.

## Evidence (project history)

- `5939a31` (2022-11-10, *"upgrade driver to support multiple hub75 cards"*) created
  `isp_hub75_hwEnums.spin2` as *"Interface constants used to describe HUB75 panel connection and
  configuration"*, its sections numbered in config order. The same commit chose `#0[16]` (pin base),
  `#2` (line count), `#3` (bit depth), `#10[10]` (adapter IDs apart from chain indexes) and `#10` for
  `DIR_*` (apart from `SCROLL_*` at 0), and added the `hwBuffers` forward *"this reduces include
  complexity for demo's"*.
- `dd81849` (2020-11-30) introduced `display`'s forwards of `fonts` and `scroller` values, the day
  scrolling arrived.
- `7eba208` (2024-01-15) moved the forward into `hwBufferAccess` with the buffer split.
- `0fe8761` (2023-01-21) added rotation as `#15[5]` (15..35, overlapping adapter IDs 20/30);
  `ffcbcee` (2025-02-17) moved it to `$20` and kept `ROT_NONE` / `ROT_LEFT_90` / `ROT_RIGHT_90` as
  *"aliases for convenience"*.
- DISPLAY-ORGANIZATION plan (archived), §2: *"each kind of word occupies its own bits and each word
  is one bit, so that joining two words of the same kind is always detectable."*

## Not recommended

- **Centralizing every enumeration in one object.** It divorces values from the interfaces that give
  them meaning (Stephen's first ruling). Centralize only where values meet across objects or the
  configuration file must name them.
- **Mandatory distinct ranges across all groups.** That costs readability where values never meet,
  and it would break quantity encodings.
