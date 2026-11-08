# Peridot hardware input provenance

This folder carries the compressed copy of the active DTB extracted from the read-only `vendor_boot_a.img` supplied for the Redmi Turbo 3 (peridot).

- Source partition: Android Vendor Boot v4, DTB payload
- DTB index: 0 (the first concatenated FDT)
- Runtime selector: MSM ID `0x266`, board ID `0x08`
- GPU identity in the DTB: Adreno 735, chip ID `0x43030b00`, compatible `qcom,adreno-gpu-gen7-11-0`
- OPP table: 11 levels, initial level 10
- Uncompressed DTB SHA-256: `94f473e5bdc0255efcaeedefe423017e26d5d18fdbbc0b76504b47f0e0db36a0`

The GitHub Actions workflow decompresses this file into both expected paths:
- `fw/stock/dtb_3.dtb`
- `fw/dtb_04.dtb`

Those two filenames are legacy script inputs; they deliberately point to the same active Adreno735 DTB. DTB index 1 was checked separately and identifies Adreno732 with 9 OPP levels, so it is not used for this target.

Other inputs are fetched at build time from pinned public source revisions and kept in the ephemeral runner workspace. Proprietary GPU firmware files are not committed to this repository or uploaded as plain artifacts; the workflow verifies their SHA-256 values against `board.toml`.
