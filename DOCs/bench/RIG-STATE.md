# Rig state

**Class: current state.** Written by the executing (macOS + hardware) side. It
holds one record: the rig as it is now. Replace the record when the rig changes,
and never append. Keep a prior note only if a reader would act differently for
having read it.

## Now

Not yet recorded. The executing side fills this in on its first crossing:
- which P2 board is attached and on which USB device;
- which HUB75 adapter is on which pin group;
- which panels (chip, geometry) are on each adapter;
- the power arrangement.
