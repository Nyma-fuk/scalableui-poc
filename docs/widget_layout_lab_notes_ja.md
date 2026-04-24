# Widget Layout Lab Notes

## 目的

`widget-layout-lab` は、ユーザーが提示した Widget 配置案を ScalableUI で検証するための variant です。
初期画面は Map を大きく置き、右側に Calendar / Weather の小 Widget を並べます。
右下の `Widget Layout` button を押すと、右側から picker と drop zone が現れます。

## 構成

- `widget_a_panel`: Map。初期画面では左の大きい Widget A。
- `widget_b_panel`: Calendar。初期画面では右上の Widget B。
- `widget_c_panel`: Weather。初期画面では右中段の Widget C。
- `widget_d_panel`: Media。配置パターン切替時に表示される Widget D。
- `widget_e_panel`: Tasks。stack-left パターンで表示される Widget E。
- `widget_f_panel`: Interactive Widgets。2 large / swap パターンで表示される Widget F。
- `widget_menu_button_panel`: 右下のメニューボタン。
- `widget_picker_panel`: 右から出る Widget picker。
- `widget_drop_zone_panel`: drag-and-drop 風の配置先。

## 操作

1. 初期状態では `Widget A Map`, `Widget B Calendar`, `Widget C Weather`, `Widget Layout` button が表示されます。
2. `Widget Layout` button を押すと、右側に `Widget layout` picker と中央寄りに `Drop Zone` が出ます。
3. picker の `Pattern 1: A + F`, `Pattern 1b: A + B + D`, `Pattern 2: F + A`, `Stack left + A` を押すと、ScalableUI の panel variant が切り替わります。
4. picker の Widget card を長押しして `Drop Zone` に落とすと、対応する prepared layout event が発火し、対象 Widget app が指定 panel に launch されます。

## 実装メモ

- Demo app から SystemUI へ `com.android.car.scalableui.ACTION_PANEL_EVENT` broadcast を送り、`SystemEventHandler` が `EventDispatcher` に渡します。
- ScalableUI の XML 側は `widget_layout_initial`, `widget_layout_two_large`, `widget_layout_split_three`, `widget_layout_swap`, `widget_layout_stack_left`, `widget_layout_hide_menu` を `Transition` として受けます。
- 任意座標へ完全自由配置するのではなく、AAOS emulator で安定評価しやすい prepared layout 切替として実装しています。
- 各 Widget は独立 APK として分けてあり、ScalableUI の multi-app / multi-task routing 評価に使えます。
- `widget_picker_panel` は drop zone と同時に表示するため、通常の `_System_TaskOpenEvent` では閉じません。閉じるタイミングは `widget_layout_hide_menu` または layout pattern 適用時に限定しています。

## 検証メモ

- `JOBS=10 workdir/scalableui-poc/scripts/build_hmi_modules.sh widget-layout-lab` で demo APK / RRO の module build が成功しています。
- `m -j10 CarSystemUIScalableUiHmiWidgetLayoutLabRRO CarSystemUI` で SystemUI broadcast bridge と RRO の差分 build が成功しています。
- `AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=10 workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh widget-layout-lab` で `emu_img_zip` が成功し、`/mnt/f/aaos_images/widget-layout-lab/sdk-repo-linux-system-images.zip` に保存されています。
- `debugfs` で `system_ext.img` を確認し、`CarSystemUIScalableUiHmiWidgetLayoutLabRRO` と `ScalableUiHmiCalendarDemoApp` / `ScalableUiHmiWeatherDemoApp` / `ScalableUiHmiWidgetMenuDemoApp` / `ScalableUiHmiWidgetMenuButtonDemoApp` / `ScalableUiHmiWidgetDropZoneDemoApp` の APK が含まれていることを確認しています。
