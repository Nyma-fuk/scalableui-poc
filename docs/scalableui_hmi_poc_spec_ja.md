# ScalableUI PoC HMI 仕様メモ

> Source verification: この文書は root PoC の仕様メモです。AOSP 実装と照合した境界は [AOSP Source Verification](./aosp_source_verification_ja.md) を参照してください。`TaskPanel` は Activity を直接保持せず、root task stack / task を介して Activity を表示します。

## 目的

`sdk_car_scalableui_x86_64` 上で、ScalableUI の panel 制御だけで成立する固定 HMI を作る。
今回の構成では launcher は常時表示せず、左背景 panel の上に浮く map、右側 2 枚の固定 panel、2 本の grip、加えて fullscreen overlay panel を使う。

## アプリ調査結果

### Map

左 panel には launcher が使っている map activity をそのまま使う。
component は [strings.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/strings.xml) にあるとおり、`com.android.car.carlauncher/com.android.car.carlauncher.homescreen.MapTosActivity`。

### Calendar

Calendar app の package は `com.android.calendar`、launcher activity は [packages/apps/Calendar/AndroidManifest.xml](<AAOS15_LTS3_ROOT>/packages/apps/Calendar/AndroidManifest.xml#L55) の `AllInOneActivity`。
PoC では `com.android.calendar/.AllInOneActivity` を使う。

注意点として、標準の car product に `Calendar` は明示的には入っていなかったため、PoC product 側の [car_scalableui_poc.mk](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/car_scalableui_poc.mk) で `PRODUCT_PACKAGES += Calendar` を追加している。

### Radio

Radio app は prebuilt で、apk の badging から package は `com.android.car.radio`、launchable activity は `com.android.car.radio.RadioActivity` と確認した。
PoC では `com.android.car.radio/.RadioActivity` を使う。

Radio は [packages/services/Car/car_product/build/car.mk](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/build/car.mk#L146) で `CarRadioApp` が既に product に入っている。

## 今回の HMI 構成

今回の固定 HMI は次の構成。

- `decor_left_background_panel`
  - 左半分の背景 panel
  - map をフロート表示させるための土台
- `map_panel`
  - 左背景 panel の上に重なるフロート panel
  - `MapTosActivity`
- `calendar_panel`
  - 右上 panel
  - `com.android.calendar/.AllInOneActivity`
- `radio_panel`
  - 右下 panel
  - `com.android.car.radio/.RadioActivity`
- `decor_vertical_grip_panel`
  - 左右 split を変える grip
- `decor_horizontal_grip_panel`
  - 右 column の上下 split を変える grip
- `panel_app_grid`
  - All apps 用 fullscreen overlay
- `app_panel`
  - 固定 panel 以外の起動物を全面表示する fullscreen overlay

画面イメージは次のとおり。

```text
+----------------------+----------------------+
|  left background     |    calendar_panel    |
|   +--------------+   |                      |
|   |  map_panel   |   |                      |
|   +--------------+   +----------------------+
|                      |                      |
|                      |      radio_panel     |
|                      |                      |
+----------------------+----------------------+
```

ユーザー要望の「左側 map、右上 calendar、下段 radio」を優先し、右下に radio を配置している。

`map_panel` は [map_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/map_panel.xml) で margin と `Corner` を持たせており、背景は [decor_left_background_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_left_background_panel.xml) と [scalableui_left_background_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/layout/scalableui_left_background_panel.xml) で定義している。

なお、上バー / 下バーは ScalableUI の `DecorPanel` ではない。`TopCarSystemBar` / `BottomCarSystemBar` は通常の Car SystemUI window で、ScalableUI 側はその内側の content area に panel を収める必要がある。

## Grip の仕様

### 左右 grip

vertical grip は `GripBarViewController` を使い、`rawX` を読んで左右 split を変更する。
controller は [vertical_grip_controller.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/vertical_grip_controller.xml)。

- EventId: `layout_width_drag`
- breakpoint:
  - `40%` -> `layout_width_left_narrow`
  - `50%` -> `layout_width_balanced`
  - `60%` -> `layout_width_left_wide`

`decor_left_background_panel`、`map_panel`、`calendar_panel`、`radio_panel`、`decor_vertical_grip_panel` が同時に更新される。

### 上下 grip

horizontal grip は `rawY` を読んで右 column の上下 split を変更する。
controller は [horizontal_grip_controller.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/horizontal_grip_controller.xml)。

- EventId: `layout_height_drag`
- breakpoint:
  - `35%` -> `layout_height_map_compact`
  - `50%` -> `layout_height_balanced`
  - `65%` -> `layout_height_map_tall`

`calendar_panel` / `radio_panel` / `decor_horizontal_grip_panel` が同時に更新される。

### Grip の操作仕様

GripBar の当たり判定を上げるため、PoC 側で次の変更を入れている。

- [dimens.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/dimens.xml)
  - vertical / horizontal grip のサイズを `48dp` に拡大
- [GripBarViewController.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/view/GripBarViewController.java)
  - click では breakpoint を進めず、drag handle としてのみ扱う

現在は [overlays.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/overlays.xml) で `drawable/grip_bar_background` を PoC 側の [poc_grip_bar_background.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/drawable/poc_grip_bar_background.xml) に差し替えている。見た目は dark rail + 明るい handle の少しモダンな grip を狙っている。

### runtime layout 補助

root PoC の width / height split は XML の transition だけに任せず、[ScalableUiPocRuntimeLayoutController.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/ScalableUiPocRuntimeLayoutController.java) でも補助している。

- 起動時に safe-area-aware な初期 bounds を適用する
- `layout_width_*` / `layout_height_*` event を受けると、3 panel と 2 grip の bounds を deterministic に再計算する
- `car_top_system_bar_height` / `car_bottom_system_bar_height` を使って top / bottom bar と重ならない content area を作る

これにより、`map_panel` / `calendar_panel` / `radio_panel` / grip panel が system bar に食い込まずに表示される。

## Fullscreen overlay の仕様

### All apps

[panel_app_grid.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/panel_app_grid.xml) は fullscreen overlay として定義している。

- `opened` は `0,0 - 100%,100%`
- `_System_TaskOpenEvent(panelId=panel_app_grid)` で開く
- `Home`、`close_app_grid`、`panel_app_grid` close event で閉じる
- `app_panel` が開いたときも閉じる

### Generic app panel

固定 panel 以外の activity、shortcut、widget 起動先として [app_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/app_panel.xml) を追加した。
この panel は `role="DEFAULT"` を持つ launch root panel として動く。

ScalableUI 側の routing は [PanelAutoTaskStackTransitionHandlerDelegate.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java#L202) で、既知 panel が `handles(component)` しない場合は `isLaunchRoot()` な panel にフォールバックする。
今回の PoC ではそれが `app_panel`。

そのため、固定 3 panel に属さない起動物は `panelId=app_panel` として扱われ、fullscreen overlay で前面表示される。

### All apps からの起動

`All apps` から app を起動するときは、[AppLaunchProvider.kt](<AAOS15_LTS3_ROOT>/packages/apps/Car/Launcher/libs/appgrid/lib/src/com/android/car/carlauncher/repositories/appactions/AppLaunchProvider.kt) で `com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL=true` を付ける。

ScalableUI 側では [PanelAutoTaskStackTransitionHandlerDelegate.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java) がこの extra を見て、既知 panel より先に launch root panel へ送る。また、`HOME category` を持つ task でも「いま前面にいる activity が本当に base home activity と同じか」まで確認してから Home event 扱いするようにしている。

加えて [AppItemViewHolder.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/Launcher/libs/appgrid/lib/src/com/android/car/carlauncher/recyclerview/AppItemViewHolder.java) で起動直後に `AppGridActivity` を閉じることで、overlay が前面に残って「何も表示されない」ように見える状態を避けている。

ただしこの方式は「fullscreen を優先させるヒント」であり、別 fullscreen task の増殖を保証するものではない。
高負荷 app の重複起動を避けるため、現在は `FLAG_ACTIVITY_MULTIPLE_TASK` を使わず、既存 task / Activity の再利用を優先する。既存 task relocation / reparent を行う場合は PoC custom policy として live source の `WindowContainerTransaction` 適用箇所を再確認する。

## 主な修正ファイル

- [car_scalableui_poc.mk](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/car_scalableui_poc.mk)
- [config.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/config.xml)
- [strings.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/strings.xml)
- [integers.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/integers.xml)
- [dimens.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/dimens.xml)
- [map_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/map_panel.xml)
- [decor_left_background_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_left_background_panel.xml)
- [calendar_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/calendar_panel.xml)
- [radio_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/radio_panel.xml)
- [panel_app_grid.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/panel_app_grid.xml)
- [app_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/app_panel.xml)
- [decor_vertical_grip_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_vertical_grip_panel.xml)
- [decor_horizontal_grip_panel.xml](<AAOS15_LTS3_ROOT>/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_horizontal_grip_panel.xml)
- [PanelAutoTaskStackTransitionHandlerDelegate.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java)
- [GripBarViewController.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/view/GripBarViewController.java)
- [AppLaunchProvider.kt](<AAOS15_LTS3_ROOT>/packages/apps/Car/Launcher/libs/appgrid/lib/src/com/android/car/carlauncher/repositories/appactions/AppLaunchProvider.kt)
- [AppItemViewHolder.java](<AAOS15_LTS3_ROOT>/packages/apps/Car/Launcher/libs/appgrid/lib/src/com/android/car/carlauncher/recyclerview/AppItemViewHolder.java)

## 既知の課題

- `Calendar` は PoC product 側で追加したため、別 product に patch を適用する場合は package 追加もセットで必要
- `app_panel` は launch root panel なので、固定 panel に属さない遷移は基本的に fullscreen overlay へ送られる
- fixed panel app を `All apps` から押したときも fullscreen を優先するようにしているが、app 自身の launch mode までは上書きできない
- `com.android.car.settings` のように `FallbackHome` を root に持つ package は、task 自体は `type=home` のまま fullscreen 化されることがある。ただし current PoC では behind-home にならず前面表示されるところまでは確認できている
- どの sub-activity を固定 panel に残し、どれを fullscreen overlay に送るかは今後さらに細かく調整できる
