# ScalableUI PoC Agent Guide

This repo is a public patch/documentation layer for AAOS15 ScalableUI HMI exploration. Treat generated patches as deliverables for other people to apply to clean AAOS15 checkouts.

If a local Codex skill named `scalableui-aaos-hmi` is available, use it for detailed workflow, SDK image metadata, and troubleshooting guidance.

## Source Of Truth

- Update `scripts/generate_hmi_variants.py` first for HMI variant, RRO, product, or demo app structure changes.
- Run `python3 scripts/generate_hmi_variants.py` from this repo root after generator edits.
- Keep generated patches, `variants/*/docs/hmi_spec_ja.md`, and top-level docs synchronized.

## Demo App Rules

- Demo apps must remain separate APKs/packages. Do not collapse them back into one APK with multiple Activities.
- Current core components:
  - `com.android.car.scalableui.hmi.map/.MapActivity`
  - `com.android.car.scalableui.hmi.gball/.GBallActivity`
  - `com.android.car.scalableui.hmi.widgets/.WidgetActivity`
  - `com.android.car.scalableui.hmi.panelmenu/.PanelMenuActivity`
- Do not add Google Maps screenshots or tiles to this public repo. Use synthetic/reproducible artwork unless redistributable assets are explicitly provided.

## Build And Verification

- Module build example from AAOS root:

  ```bash
  JOBS=10 workdir/scalableui-poc/scripts/build_hmi_modules.sh widget-workspace
  ```

- Emulator image build example from AAOS root:

  ```bash
  AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=10 \
    workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh widget-workspace
  ```

- Confirm APKs via `installed-files-system_ext.txt`, `product_packages.txt`, and `debugfs` on `system_ext.img`.
- `m emu_img_zip` is required for distributable emulator image zips.

## Safety

- Do not use destructive git commands.
- Do not overwrite unrelated user changes in the AAOS tree.
- Patch apply scripts must fail safely if local changes overlap.
- For Android Studio SDK distribution, keep `/mnt/f/aaos_images/systemimg.xml`, zip size/SHA1, zip `x86_64/source.properties`, and installed SDK metadata aligned.
