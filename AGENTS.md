# ScalableUI PoC Agent Guide

This repository is the public patch and documentation layer for the AAOS ScalableUI HMI PoC. Treat patches and docs as the deliverable. The AAOS source tree is the validation workspace.

## Current Main Target

The main active PoC is `dynamic-workspace`.

Use this target when the user asks about the current ScalableUI HMI PoC unless they explicitly ask for an older/root/static variant.

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh dynamic-workspace
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh dynamic-workspace
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=8 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh dynamic-workspace
```

## Required Reading

Before implementation work, read:

1. `README.md`
2. `docs/ai_implementation_guide_ja.md`
3. `docs/scalableui_poc_architecture_ja.md`
4. `docs/dynamic_workspace_notes_ja.md`

## Source Of Truth

- `scripts/hmi_variants.sh` is the variant/product/module mapping used by build scripts.
- `variants/dynamic-workspace/` owns the Dynamic Workspace product/RRO patch.
- `common/patches/packages-services-Car/0003-add-dynamic-workspace-demo-home.patch` owns Workspace demo app additions.
- `patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch` owns SystemUI runtime/controller/routing changes.
- `docs/dynamic_workspace_notes_ja.md` owns runtime evaluation history.
- `docs/ai_implementation_guide_ja.md` owns implementation continuation guidance.

Generated HMI variant patches should normally be changed through `scripts/generate_hmi_variants.py`. Dynamic Workspace currently contains hand-maintained runtime additions that are not just generated fixed-layout XML.

## Implementation Rules

- Keep ScalableUI core changes small. Prefer product-specific runtime code under `com.android.systemui.car.wm.scalableui.workspace`.
- Preserve the SOLID split:
  - `WorkspaceRuntimeLayoutController`: command and orchestration
  - `WorkspaceGeometry`: bounds and layout calculation
  - `WorkspacePanelStateController`: StateManager, Variant, BasePanel, surface update
  - `WorkspaceTaskRouter`: app launch and panel routing
  - `WorkspaceModelStore`: persistence
- Do not collapse demo apps back into one APK. Separate packages are intentional.
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
  -avd Y-Fuk-dynamic-workspace-eval3 `
  -sysdir F:\aaos_images\dynamic-workspace\extracted\x86_64 `
  -wipe-data `
  -no-snapshot-load `
  -ports 5562,5563 `
  -memory 6144 `
  -cores 6 `
  -gpu angle_indirect
```

Capture evidence under `/tmp/<evaluation-name>/`:

- screenshots
- saved model before/after
- SystemUI PID before/after
- logcat
- summary counts for `resize_start`, `resize_update`, `resize_end`, `Slow dispatch`, fatal exceptions

## Publish Rules

When pushing to GitHub:

- Commit only `workdir/scalableui-poc` patch/docs/script changes unless the user explicitly asks to push another repository.
- Run `bash -n` for touched scripts.
- Run `git diff --check` on non-patch content.
- Generated `.patch` files can produce `+ ` blank-line warnings. Verify the underlying AAOS source with `git diff --check` before editing generated patches by hand.
