# Peridot UEFI bring-up: firmware audit gate

The HakiOS `mkxnuimg.py` flow is a useful architectural reference:
Android boot image -> BootShim -> UEFI firmware volume -> XNU loader -> XNUP payload.
Its checked-in Redwood profile is not a Peridot profile. In particular, its
`FD_BASE=0x9FD00000`, `FD_SIZE=0x200000` and `PAYLOAD_BASE=0xF0000000`
values must not be copied to SM8635 without evidence from Peridot's own boot chain.

## Current Peridot evidence

- Device: Redmi Turbo 3 / peridot / SM8635.
- Read-only firmware dumps are available on the device: `abl_a.img`, `xbl_a.img` and `xbl_config_a.img`.
- ABL string scanning found an FVH-like marker and an MZ marker, but that alone does not identify a complete UEFI FD or prove that the candidate PE image belongs to the active boot firmware.
- XBL config contains Qualcomm UEFI memory-map naming strings; these are not numeric memory reservations and cannot safely be used as addresses.

## Mandatory gates before building an Android boot image

1. Parse and validate FV headers and PE/COFF headers with bounded offsets.
2. Identify which FV is the active UEFI firmware and which PE modules it contains.
3. Extract actual Peridot UEFI memory reservations and boot handoff contract from the device firmware; do not infer addresses from Redwood.
4. Build a Peridot-specific BootShim and prove its load ranges do not overlap Android/UEFI reserved memory.
5. Package the XNU loader and payload using the proven Peridot contract.
6. Validate Android boot image header, kernel compression, DTB placement, sizes, hashes and all load ranges.
7. Only then consider a non-flashing `fastboot boot` test with a verified recovery path.

`fw/tools/audit-uefi-firmware.py` performs only the first structural scan. It is not a firmware extractor, FD builder, or bootability test.

**Safety:** this project must not flash `boot`, `vendor_boot`, `init_boot`, `dtbo`, `xbl` or `abl`. No candidate image is approved for device testing until every gate above passes.