# ScalableUI PoC Agent Guide

This repository is the public patch and documentation layer for the AAOS ScalableUI HMI PoC. Treat patches and docs as the deliverable. The AAOS source tree is the validation workspace.

## Current Main Target

The main active PoC is `declarative-multipanel`.

Use this target when the user asks about the current ScalableUI HMI PoC unless they explicitly ask for an older dynamic workspace variant or comparison.

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh declarative-multipanel
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh declarative-multipanel
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=4 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh declarative-multipanel
```

## Required Reading

Before implementation work, read:

1. `README.md`
2. `variants/declarative-multipanel/docs/hmi_spec_ja.md`
3. `docs/scalableui_window_manager_flow_ja.md`
4. `variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md`

## Source Of Truth

- `scripts/hmi_variants.sh` is the variant/product/module mapping used by build scripts.
- `variants/declarative-multipanel/` owns the current clean product/RRO/StubCarLauncher patch.
- `variants/declarative-multipanel/docs/hmi_spec_ja.md` owns the active HMI specification.
- `docs/scalableui_window_manager_flow_ja.md` owns ScalableUI / WindowManager / Launcher relationship diagrams.
- `variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md` owns current runtime evaluation history.
- `scripts/verify_declarative_multipanel_smoke.sh` owns the baseline runtime smoke.

`declarative-multipanel` is hand-maintained. Do not run old generators unless you first verify they support this variant.

## Implementation Rules

- Keep the clean baseline small: product mk, SystemUI RRO, Framework RRO, and `StubCarLauncher`.
- Do not add SystemUI / Launcher runtime Java changes to the baseline unless the user explicitly moves to a dynamic phase.
- Do not assign real `CarSettings` to the fixed `settings_panel`; fixed panel uses `SettingsPanelActivity` stub so All Apps Settings can route to `app_panel`.
- Keep ScalableUI responsibilities separate from custom workspace responsibilities:
  - ScalableUI/RRO: panel declaration, variant, transition, default activity, task placement
  - StubCarLauncher: empty HOME host and lightweight AppGrid/stub panels
  - Future custom runtime: panel add/delete/move, continuous grip resize, arbitrary app picker, persistence
- Do not add Google Maps screenshots or proprietary map tiles.
- Do not use destructive git commands.
- Do not overwrite unrelated AAOS tree changes.

## Validation Rules

After any runtime-affecting change, do not stop at static analysis or module build.

Required validation:

- Build relevant modules.
- Build `emu_img_zip`.
- Launch the Windows host emulator, not only the Linux emulator, when doing visible HMI validation.
- Prefer:

```powershell
F:\Android\Sdk\emulator\emulator.exe `
  -avd Y-Fuk-dynamic-workspace-clean2 `
  -sysdir F:\aaos_images\declarative-multipanel\extracted\x86_64 `
  -wipe-data `
  -no-snapshot-load `
  -ports 5564,5565 `
  -memory 6144 `
  -cores 6 `
  -gpu angle_indirect
```

Then run:

```bash
ADB_BIN=/mnt/f/Android/Sdk/platform-tools/adb.exe \
OUT_DIR=/tmp/declarative-multipanel-smoke-$(date +%Y%m%d-%H%M%S) \
  workdir/scalableui-poc/scripts/verify_declarative_multipanel_smoke.sh emulator-5564
```

Capture evidence under `/tmp/<evaluation-name>/`:

- screenshots
- SystemUI PID before/after
- StubCarLauncher PID before/after
- overlay state
- AppGrid / Settings activity dumps
- logcat
- fatal exception count

## Publish Rules

When pushing to GitHub:

- Commit only `workdir/scalableui-poc` patch/docs/script changes unless the user explicitly asks to push another repository.
- Run `bash -n` for touched scripts.
- Run `git diff --check` on non-patch content.
- Verify AAOS source repos with `git -C packages/services/Car diff --check` and `git -C device/generic/car diff --check`.
- Generated `.patch` files can produce `+ ` blank-line warnings. Verify the underlying AAOS source before editing generated patches by hand.
