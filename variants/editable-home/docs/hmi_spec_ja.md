# Editable multipanel home Spec

## Intent

A ScalableUI-based multipanel home keeps system bars outside the managed area, lets the user choose L1/L2/L3 layouts plus per-panel apps, and restores the saved assignment on the next Home entry.

## Build Target

- `sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `home_panel_primary` | Home Primary | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `4%` | `12%` | `62%` | `84%` | `0` |
| `home_panel_secondary_top` | Home Secondary Top | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `64%` | `12%` | `96%` | `46%` | `0` |
| `home_panel_secondary_bottom` | Home Secondary Bottom | `com.android.car.scalableui.hmi.map/.MapActivity, com.android.car.scalableui.hmi.media/.MediaActivity, com.android.car.scalableui.hmi.controls/.ControlsActivity, com.android.car.scalableui.hmi.calendar/.CalendarActivity, com.android.car.scalableui.hmi.settings/.SettingsActivity, com.android.car.scalableui.hmi.gball/.GBallActivity` | `64%` | `50%` | `96%` | `84%` | `0` |
| `home_edit_overlay` | Home Edit Overlay | `decor` | `3%` | `10%` | `97%` | `88%` | `0` |

## Routing

- Fixed panels are assigned through `config_default_activities`.
- Panels with multiple component names use a ScalableUI role string-array so
  user-launched apps can be routed into the same panel.
- `panel_app_grid` opens as the All apps overlay.
- `app_panel` is the `DEFAULT` launch-root fallback for generic apps.
- The common Launcher/SystemUI patches keep the All apps launch behavior aligned
  with the base PoC.

## Validation Checklist

1. Apply the variant patches.
2. Build the lunch target.
3. Confirm every fixed panel opens.
4. Open All apps and launch a non-fixed app.
5. Press Home and confirm overlays close.

## Acceptance Matrix

| Requirement | Expected behavior | Verification | Current status |
| --- | --- | --- | --- |
| ScalableUI enabled | AAOS15 emulator boots with ScalableUI-managed home content | confirm `config_enableScalableUI=true`, boot emulator, inspect visible home content area | partial |
| Home content is panelized | top bar / nav bar stay visible, only content area is managed by ScalableUI | screenshot + `dumpsys activity top` bounds check | partial |
| L1/L2/L3 layout switch | selecting layout in editor dispatches `_Custom_HomeLayoutChanged` and visible panel bounds change | use editor UI, save, capture before/after screenshots, confirm panel bounds differ | not yet runtime-verified |
| Per-panel assignment | user can choose one whitelisted app per panel and save | use editor UI, save, confirm launched apps match selections | not yet runtime-verified |
| Duplicate assignment rejection | selecting the same component for multiple panels cannot be saved | assign same app twice, confirm Save shows rejection | not yet runtime-verified |
| Persistence | saved layout and assignments survive Home re-entry / reboot | save, relaunch Home or reboot emulator, confirm restored state | not yet runtime-verified |
| Edit overlay behavior | edit UI appears only in edit mode and closes on cancel / apply | open editor, cancel, reopen, apply | partial |
| README / patch reproducibility | clean checkout can apply the generated patches and build this variant | `apply_hmi_variant.sh editable-home` + build docs | partial |

## Acceptance Workflow

`editable-home` は以下をそろえて初めて「検証済み」とみなします。

1. patch apply
2. module build
3. 必要に応じて `emu_img_zip`
4. boot 済み emulator 上で `scripts/verify_editable_home_acceptance.sh`
5. `/tmp/editable-home-acceptance/acceptance_report.md` と screenshot / dumpsys artifact を保管

自動検証 script が見る項目:

- product 名の一致
- L2 baseline 起動
- editor 表示
- `L1` 保存による panel bounds 変化
- panel assignment の反映
- `SharedPreferences` 保存
- Home 再起動後の復元
- duplicate assignment 拒否時に prefs が変化しないこと

この variant については、`widget-layout-lab` の確認結果を流用せず、必ず `editable-home` 自体に対して acceptance を取ります。

## Known Gaps Against The Multipanel-Home Spec

- The Windows-side runtime verification completed so far was for `widget-layout-lab`, not for `editable-home`.
- `editable-home` has event names, `SharedPreferences`, and panel XML for `L1/L2/L3`, but the acceptance checks above have not yet been completed end-to-end on a shipped emulator image.
- The current RRO `config_default_activities` only declares `panel_app_grid;com.android.car.carlauncher/.AppGridActivity`. The three home task panels are populated by `HomeActivity` runtime launches, so this variant still depends on host-side launch sequencing rather than a fully verified controller-based panel population model.
- Custom `TaskPanelController` classes described in the target spec are not implemented yet. Current panel assignment is resolved by `HomeActivity` / `HomeEditActivity` launch logic instead of per-panel controller classes.

## Variant Notes

- The managed Home content area is inset so top bar and nav bar remain visible.
- HomeEditActivity stores layout id and per-panel assignment in SharedPreferences.
- Duplicate assignments are rejected when the user presses Save.
- The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.
