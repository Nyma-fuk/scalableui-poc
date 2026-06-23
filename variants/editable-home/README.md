# Editable multipanel home

## Summary

A ScalableUI-based multipanel home keeps system bars outside the managed area, keeps three managed panels open, lets the user assign any installed launchable app to each panel, and lets the user resize the panel split directly with always-visible grips.

## Product

- Product: `sdk_car_scalableui_editable_home_x86_64`
- Lunch: `sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`
- RRO: `CarSystemUIScalableUiHmiEditableHomeRRO`

## Use Cases

- multipanel home host evaluation
- direct panel resize with persistence
- user-selected panel app assignment from an installed-app picker
- system-bar-safe content area validation
- one-task-per-app panel reassignment validation

## Panels

- `home_panel_primary`: left content panel
- `home_panel_secondary_top`: right-top content panel
- `home_panel_secondary_bottom`: right-bottom content panel
- `home_panel_primary_header`: primary panel header / picker trigger
- `home_panel_secondary_top_header`: secondary top header / picker trigger
- `home_panel_secondary_bottom_header`: secondary bottom header / picker trigger
- `home_split_vertical_grip`: left-right split grip
- `home_split_horizontal_grip`: right-column top-bottom split grip
- `home_edit_overlay`: Home Edit Overlay, `3%,10% - 97%,88%`

## Apply This Variant Only

Run from the AAOS checkout root:

```bash
bash <SCALABLEUI_POC_ROOT>/scripts/apply_hmi_variant.sh editable-home
lunch sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug
```

The script applies common ScalableUI routing patches, the common demo app patch,
the runtime-variant override patch, the product patch for this variant, and the
RRO patch for this variant.

## Notes

- The managed Home content area is inset so top bar and nav bar remain visible.
- Runtime geometry is driven by `split_ratio_x` and `split_ratio_right_y` in `SharedPreferences`.
- Panel headers open a fullscreen app picker inside `app_panel`.
- Choosing an app moves the existing task to the newly selected panel instead of duplicating it.
- Home re-entry restores both assignment and split ratio.
- `HomeEditActivity` remains as a development preset tool; it is no longer the main UX for panel assignment.
- The edit overlay is a ScalableUI decor panel; the editor UI itself opens inside app_panel.

## Verification Process

`editable-home` は見た目のスクリーンショットだけで完了判定しません。次の順で確認します。

1. variant patch を適用する
2. `lunch sdk_car_scalableui_editable_home_x86_64-trunk_staging-userdebug`
3. `bash <SCALABLEUI_POC_ROOT>/scripts/build_hmi_modules.sh editable-home`
4. image まで必要なら `AAOS_IMAGE_ROOT=<AAOS_IMAGE_ROOT> bash <SCALABLEUI_POC_ROOT>/scripts/build_hmi_emulator_images.sh editable-home`
5. 起動済み emulator に対して受け入れスクリプトを実行する

```bash
bash <SCALABLEUI_POC_ROOT>/scripts/verify_editable_home_acceptance.sh
```

この script / 手動確認では次を見ます。

- `editable-home` product で起動していること
- Home 起動で 3 panel と 3 header と 2 grip が system bar を避けて表示されること
- header タップで panel 専用 app picker が出ること
- インストール済み app を選ぶと指定 panel に表示されること
- 同じ app を別 panel に選ぶと既存 task が移動すること
- 縦 grip / 横 grip のドラッグで panel 境界が連続変化すること
- `SharedPreferences` に split ratio と assignment が保存されること
- Home 再起動後も geometry / assignment が復元されること

証跡は既定で `<EVIDENCE_DIR>/editable-home-acceptance/` に出力され、`acceptance_report.md` にまとまります。
