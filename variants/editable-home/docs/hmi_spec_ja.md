# Editable multipanel home Spec

## Intent

A ScalableUI-based multipanel home keeps system bars outside the managed area, keeps three non-overlapping panels open, lets the user assign any installed launchable app to any panel, and restores both assignment and split ratio on the next Home entry.

## Build Target

- `sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`

## Panel Table

| Panel | Label | Component | Left | Top | Right | Bottom | Display |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `home_panel_primary` | Home Primary | runtime-assigned app task | runtime from `split_ratio_x` | runtime | runtime | runtime | `0` |
| `home_panel_secondary_top` | Home Secondary Top | runtime-assigned app task | runtime from `split_ratio_x` / `split_ratio_right_y` | runtime | runtime | runtime | `0` |
| `home_panel_secondary_bottom` | Home Secondary Bottom | runtime-assigned app task | runtime from `split_ratio_x` / `split_ratio_right_y` | runtime | runtime | runtime | `0` |
| `home_panel_primary_header` | Primary Header | `com.android.car.scalableui.hmi.home/.PrimaryPanelHeaderActivity` | runtime | runtime | runtime | runtime | `0` |
| `home_panel_secondary_top_header` | Secondary Top Header | `com.android.car.scalableui.hmi.home/.SecondaryTopPanelHeaderActivity` | runtime | runtime | runtime | runtime | `0` |
| `home_panel_secondary_bottom_header` | Secondary Bottom Header | `com.android.car.scalableui.hmi.home/.SecondaryBottomPanelHeaderActivity` | runtime | runtime | runtime | runtime | `0` |
| `home_split_vertical_grip` | Vertical Split Grip | `com.android.car.scalableui.hmi.home/.VerticalSplitGripActivity` | runtime | runtime | runtime | runtime | `0` |
| `home_split_horizontal_grip` | Horizontal Split Grip | `com.android.car.scalableui.hmi.home/.HorizontalSplitGripActivity` | runtime | runtime | runtime | runtime | `0` |
| `home_edit_overlay` | Home Edit Overlay | `decor` | `3%` | `10%` | `97%` | `88%` | `0` |

## Routing

- `home_entry_panel` hosts `HomeActivity`, which restores saved assignments and dispatches runtime layout updates.
- Panel headers open `HomeAppPickerActivity` inside fullscreen `app_panel`.
- App selection launches with `TARGET_PANEL_ID` so the selected task is routed into the chosen panel.
- If the same component is already assigned to another panel, the existing task is moved instead of duplicated.
- `panel_app_grid` opens as the All apps overlay.
- `app_panel` is the `DEFAULT` launch-root fallback for generic apps.
- All apps remains fullscreen and does not overwrite Home assignments.

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
| Header-based assignment | user can open a picker from each panel header and choose an installed app | tap each header, confirm picker opens and selected app appears in the chosen panel | not yet runtime-verified |
| Same-app move semantics | selecting an app already used in another panel moves the existing task instead of cloning it | choose the same app from another header and confirm one task relocates | not yet runtime-verified |
| Continuous split resize | dragging vertical / horizontal grips continuously changes panel bounds | drag both grips and confirm live bounds changes | not yet runtime-verified |
| Persistence | saved split ratios and assignments survive Home re-entry / reboot | resize + assign, relaunch Home or reboot emulator, confirm restored state | not yet runtime-verified |
| Edit overlay behavior | edit UI appears only in edit mode and closes on cancel / apply | open editor, cancel, reopen, apply | partial |
| README / patch reproducibility | clean checkout can apply the generated patches and build this variant | `apply_hmi_variant.sh editable-home` + build docs | partial |

## Acceptance Workflow

`editable-home` は以下をそろえて初めて「検証済み」とみなします。

1. patch apply
2. module build
3. 必要に応じて `emu_img_zip`
4. boot 済み emulator 上で `scripts/verify_editable_home_acceptance.sh`
5. `/tmp/editable-home-acceptance/acceptance_report.md` と screenshot / dumpsys artifact を保管

自動検証 script / 手動確認が見る項目:

- product 名の一致
- 3 panel + 3 header + 2 grip の初期表示
- header からの app picker 起動
- panel assignment の反映
- same-app move semantics
- split ratio 保存
- Home 再起動後の復元

この variant については、`widget-layout-lab` の確認結果を流用せず、必ず `editable-home` 自体に対して acceptance を取ります。

## Known Gaps Against The Multipanel-Home Spec

- The Windows-side runtime verification completed so far was for `widget-layout-lab`, not for `editable-home`.
- Runtime verification on an actual emulator image is still pending for the new header / picker / continuous-resize flow.
- The runtime layout path is implemented as a dedicated SystemUI controller plus Home app broadcast bridge, not as a custom `TaskPanelController`.

## Variant Notes

- The managed Home content area is inset so top bar and nav bar remain visible.
- Split ratios are stored as `split_ratio_x` and `split_ratio_right_y`.
- Panel assignment is stored as `assignment_<panel_id>`.
- `HomeEditActivity` now acts as a development preset tool and no longer drives the main UX.
- The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.
