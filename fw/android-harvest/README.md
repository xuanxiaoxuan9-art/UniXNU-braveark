# Peridot hardware input provenance

This directory is populated by the GitHub Actions workflow from pinned public sources.
The source URLs and exact revisions are recorded here so that the generated artifacts are
reproducible. Proprietary firmware is downloaded only into the ephemeral Actions runner,
verified against the SHA-256 and byte-count pins in board.toml, and never committed.

## Register descriptions
- Mesa freedreno register database, commit
  `61b01302910401cbb4ad25555fd4c23e88d23272`
  - `msm-regs/a6xx.xml`
  - `msm-regs/a6xx_gmu.xml`

## Qualcomm driver source
- `sm8635-dev/kernel_xiaomi_sm8635`, commit
  `124567bfed3297a644bb1cb132e5f7ec2b2233cb`
  - `msm-drv/a6xx_gmu.c`
  - `msm-drv/a7xx_catalog.c` is the upstream Linux catalog below, not copied from a mismatched phone.
  - `vendor-source/arm-smmu-qcom.c`

## A7xx hardware catalog
- `torvalds/linux`, commit
  `fa4ad798f6f681031775266044ba1b0cf3c670bd`
  - `msm-drv/a7xx_catalog.c` (contains the A730 hardware clock-gating profile used by the A735 generator)

## GPU firmware (CI-only)
- `xiaomi-peridot/vendor_xiaomi_peridot`, commit
  `757618d23b3e86644b2ab1111dd8ca9dbd4cdadc`
  - `gen71100_gmu.bin`
  - `gen71100_sqe.fw`
  - `gen71100_zap.mbn`
- SHA-256 and byte lengths are verified against `[gpu.firmware_pins]` in board.toml.
- Firmware is not stored in this public repository.
