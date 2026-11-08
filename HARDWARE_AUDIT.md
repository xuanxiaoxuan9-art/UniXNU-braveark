# Peridot bring-up audit

**Audit date:** 2026-11-08  
**Target device:** Redmi Turbo 3 / POCO F6, model 24069RA21C, codename `peridot`  
**Purpose:** distinguish facts from the current source package and CI logs from claims that have not yet been demonstrated on this phone.

## Verified target facts

The hardware capture supplied for this project identifies the device as Redmi Turbo 3 (`24069RA21C`), platform `pineapple` / SM8635 (Cliffs), Adreno 735. The runtime device-tree capture and boot logs identify:

- Active display panel node: `qcom,mdss_dsi_n16t_36_0f_0b_dsc_vid`; 1220 × 2712.
- Touch controller: FocalTech `focaltech_ts`, SPI device `spi1.0`, DT compatible `xiaomi,peridot-spi` / `focaltech,n16t-3683g-spi`.
- Raw touch coordinates reported by the driver: 19520 × 43392 (16× scaling).
- GPU: Adreno 735; observed GPU/GMU/SMMU bases are 0x3d00000 / 0x3d68000 / 0x3da0000.
- The supplied partition dump contains `vendor_boot_a` and `dtbo_a`; the active runtime DT selector was identified as MSM ID 0x266 / board ID 0x08.

The supplied `vendor_boot_a` v4 image was parsed read-only. Its DTB payload contains two concatenated FDTs:

- DTB index 0: SHA-256 `94f473e5bdc0255efcaeedefe423017e26d5d18fdbbc0b76504b47f0e0db36a0`; GPU node says Adreno 735, chip ID `0x43030b00`, gen7-11-0, 11 OPP levels, initial level 10.
- DTB index 1: SHA-256 `866dfb9105ebb4d2bd5ff8c1053ea45b9843a3f1f7fc20e02dbd81393f1e7401`; GPU node says Adreno 732, 9 OPP levels, initial level 8.

The runtime selector (MSM ID `0x266` / board ID `0x08`) matches DTB index 0. Re-running the repository's GPU-input derivation against DTB index 0 reproduced every committed GPU/OPP/profile field; only the source label and DTB SHA differ. This is a much stronger match than DTB index 1 and gives us a recoverable, device-matched source for both expected input filenames. The DTB contains no MAC-address, 15-digit IMEI, or 32-hex device identifier strings in the inspected payload.

The captured boot log requests `focaltech_ts_fw_TianMa.bin`; the recorded direct firmware lookup attempts include permission/not-found errors. Therefore the capture establishes the controller identity, not that a new XNU FocalTech driver or firmware path works.

## Source-package inconsistencies

The tracked repository currently contains only the workflow and `unixnu-peridot-repo.zip`. The ZIP has no `fw/` directory, yet build scripts depend on external evidence and binary inputs under `fw/`.

The packaged README and STATUS are stale or inconsistent with the supplied phone:

- They label the device “Xiaomi Pad 7 Pro”, although the supplied device is Redmi Turbo 3.
- They describe a 1840 × 2880 panel and Novatek touch, whereas the captured active panel is 1220 × 2712 and the touch controller is FocalTech.
- The board file itself notes that the Novatek driver does not match this phone and leaves `peridot-touch-drv=1` disabled. The README/STATUS do not consistently reflect that.
- The board configuration references a Xiaomi UEFI package path and external firmware workspace inputs that are not present in the checked-in ZIP. Those paths and their provenance still need validation.

These mismatches must be resolved before treating the packaged board description as authoritative.

## Run #20: what actually happened

The 2026-11-08 GitHub Actions run did **not** complete a Peridot kernel build:

1. The bootstrap build used `ARCH_CONFIGS=ARM64` and `MACHINE_CONFIGS=BCM2837`; its output path is `DEVELOPMENT_ARM64_BCM2837`. That is not a Peridot/SM8635 target build.
2. The bootstrap compile error for `(void) indices;` was removed by the existing repair step; the log shows `repair fixed=1`.
3. Archive steps 1–9 ran.
4. Archive 10 (`build-native-legacy-display.py`) stopped in `gen-peridot-gmu-source.py` with `FileNotFoundError` for `fw/android-harvest/msm-regs/a6xx.xml`.
5. The workflow never reached `peridot_defconfig` or the final kernel build.

Accordingly, Run #20 produced no validated Peridot kernel, boot image, or iOS/iPadOS boot result.

## Required build inputs (not in the checked-in ZIP)

At minimum, the current generator chain expects these files or directories from the same device/build provenance:

- `fw/stock/dtb_3.dtb`
- `fw/dtb_04.dtb`
- `fw/android-harvest/msm-regs/a6xx.xml`
- `fw/android-harvest/msm-regs/a6xx_gmu.xml`
- `fw/android-harvest/msm-drv/a6xx_gmu.c`
- `fw/android-harvest/msm-drv/a7xx_catalog.c`
- `fw/android-harvest/vendor-source/arm-smmu-qcom.c`
- `fw/gpu-firmware/gen71100_gmu.bin`
- `fw/gpu-firmware/gen71100_sqe.fw`
- `fw/gpu-firmware/gen71100_zap.mbn`

The register XML, driver source, catalog and firmware must be pinned to identified upstream/vendor revisions and checked against this specific SM8635 device. Do not manufacture XML/register values or substitute files from another phone. Proprietary firmware should not be committed to this public repository without confirming redistribution rights; CI should accept it as a separately provided input or retrieve it from an authorized source.

## Safety and next gates

- Do not run any `fastboot flash` or write to `userdata` based on the archived instructions. The existing Android partitions and user data must remain recoverable.
- First validate the source package, board identity, device-tree inputs, firmware provenance, and actual target architecture.
- Then get a clean, reproducible Peridot-specific kernel build. A successful bootstrap or a static object audit is not a boot test.
- Only after the boot chain and recovery plan are verified should a temporary, non-flashing boot experiment be considered.
- Display, FocalTech touch, UFS, power/thermal control, and GPU command submission each need independent implementation and runtime evidence.

This audit intentionally separates static compilation evidence from hardware functionality. A green CI result alone must not be reported as an iOS/iPadOS boot.
