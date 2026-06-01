# ScalableUI PoC 構成図 2026-06-01

## 1. 今回評価に使っている emulator

- AVD 名: `Y-Fuk-root-grip-clean`
- Product: `sdk_car_scalableui_x86_64`
- image source: `F:\aaos_images\root-grip-fix\x86_64`

## 2. PoC の全体像

この PoC は、AAOS 上で `ScalableUI` を有効化し、以下の HMI を固定 panel として表示する構成です。

- 左: `map_panel`
- 右上: `calendar_panel`
- 右下: `radio_panel`
- 左右境界: `decor_vertical_grip_panel`
- 右側上下境界: `decor_horizontal_grip_panel`
- fullscreen 起動用: `app_panel`
- fullscreen app grid: `panel_app_grid`

## 3. AAOS のどこを触ったか

### 3-1. 高レベルの責務分解

```text
+---------------------------------------------------------------+
| device/generic/car                                            |
|  - sdk_car_scalableui_x86_64.mk                               |
|  - AndroidProducts.mk                                         |
|                                                               |
| 役割: PoC 用 product を追加                                   |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| packages/services/Car/car_product/scalableui_poc              |
|  - car_scalableui_poc.mk                                      |
|  - rro/CarSystemUIScalableUiPocRRO/...                        |
|                                                               |
| 役割: ScalableUI を ON にする RRO と panel XML を定義         |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| packages/apps/Car/SystemUI                                    |
|  - CarWMShellModule.java                                      |
|  - ScalableUIWMInitializer.java                               |
|  - EventDispatcher.java                                       |
|  - PanelAutoTaskStackTransitionHandlerDelegate.java           |
|  - view/GripBarViewController.java                            |
|  - ScalableUiPocRuntimeLayoutController.java                  |
|                                                               |
| 役割:                                                          |
|  - ScalableUI 初期化                                           |
|  - task/panel routing                                          |
|  - grip event 受信                                             |
|  - root PoC の runtime layout 更新                            |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| packages/apps/Car/systemlibs/car-scalable-ui-lib              |
|  - loader/xml/PanelStateXmlParser.java                        |
|  - model/Variant.java                                         |
|                                                               |
| 役割:                                                          |
|  - panel/controller XML の基礎パーサ                           |
|  - runtime から Variant を上書きする土台                       |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
| packages/apps/Car/Launcher                                    |
|  - AppLaunchProvider.kt                                       |
|                                                               |
| 役割: All Apps などからの launch に                            |
|        LAUNCH_IN_APP_PANEL を付与                              |
+---------------------------------------------------------------+
```

### 3-2. 実ファイルとの対応

#### Product / build 側

- [sdk_car_scalableui_x86_64.mk](/home/y-fuk/work/android-automotiveos15-lts3/device/generic/car/sdk_car_scalableui_x86_64.mk)
- [AndroidProducts.mk](/home/y-fuk/work/android-automotiveos15-lts3/device/generic/car/AndroidProducts.mk)

#### RRO / panel 定義側

- [car_scalableui_poc.mk](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/car_scalableui_poc.mk)
- [config.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/config.xml)
- [map_panel.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/map_panel.xml)
- [calendar_panel.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/calendar_panel.xml)
- [radio_panel.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/radio_panel.xml)
- [decor_vertical_grip_panel.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_vertical_grip_panel.xml)
- [decor_horizontal_grip_panel.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_horizontal_grip_panel.xml)
- [vertical_grip_controller.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/vertical_grip_controller.xml)
- [horizontal_grip_controller.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/horizontal_grip_controller.xml)
- [poc_grip_bar_background.xml](/home/y-fuk/work/android-automotiveos15-lts3/packages/services/Car/car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/drawable/poc_grip_bar_background.xml)

#### SystemUI / ScalableUI runtime 側

- [CarWMShellModule.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/wmshell/CarWMShellModule.java)
- [ScalableUIWMInitializer.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/ScalableUIWMInitializer.java)
- [EventDispatcher.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/EventDispatcher.java)
- [PanelAutoTaskStackTransitionHandlerDelegate.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java)
- [GripBarViewController.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/view/GripBarViewController.java)
- [ScalableUiPocRuntimeLayoutController.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/ScalableUiPocRuntimeLayoutController.java)

#### ScalableUI library 側

- [PanelStateXmlParser.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/loader/xml/PanelStateXmlParser.java)
- [Variant.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/model/Variant.java)

#### Launcher 側

- [AppLaunchProvider.kt](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/Launcher/libs/appgrid/lib/src/com/android/car/carlauncher/repositories/appactions/AppLaunchProvider.kt)

## 4. 起動シーケンス

```text
[Product boot]
   |
   v
sdk_car_scalableui_x86_64
   |
   v
CarSystemUIScalableUiPocRRO
  - config_enableScalableUI = true
  - window_states = map/calendar/radio/grips/app_panel/...
   |
   v
CarWMShellModule
   |
   v
ScalableUIWMInitializer
   |
   +--> PanelAutoTaskStackTransitionHandlerDelegate.init()
   +--> PanelConfigReader.init()
   +--> ActionConfigReader.init()
   +--> ScalableUiPocRuntimeLayoutController.init()
```

## 5. grip drag 時の処理

```text
User drag
   |
   v
GripBarViewController.onTouch()
   |
   +--> KeyFrameEvent(layout_width_drag / layout_height_drag)
   +--> snap event(layout_width_left_wide など)
   |
   v
EventDispatcher.executeEvent()
   |
   +--> root PoC event なら
   |      ScalableUiPocRuntimeLayoutController.handleEvent()
   |         |
   |         +--> widthRatio / heightRatio 更新
   |         +--> Variant runtime bounds 更新
   |         +--> BasePanel.update()
   |         +--> AutoTaskStackController.startTransition()
   |
   +--> root PoC 以外なら通常の StateManager / Transition 経路
```

## 6. どこまでが ScalableUI 標準で、どこから custom か

### 6-1. ScalableUI 標準機能でできる範囲

```text
[ScalableUI 標準]
  - panel の宣言
  - variant / transition / keyframe の宣言
  - task/activity を panel にホスト
  - panel layering
  - grip controller から event を飛ばす
  - launch-root panel への fallback
```

具体例:

- `map_panel` / `calendar_panel` / `radio_panel` の存在そのもの
- `app_panel` を fullscreen launch-root にすること
- `Bounds` による fixed / floated layout
- `GripBarViewController` による drag event の生成

### 6-2. 今回 custom 実装した部分

```text
[custom]
  - root PoC 専用 runtime layout controller
  - system bar safe area を考慮した bounds 再計算
  - drag 中に deterministic に 3 panel を再配置するロジック
  - Settings / FallbackHome の routing 補正
  - breakpoint の軸解釈修正
  - drag event の二重発火抑止
```

つまり、**「panel を定義して app を載せる」までは ScalableUI の守備範囲**ですが、  
**「3 panel の split 比率を runtime state として持ち、毎フレーム近く再配置する」部分は今回の PoC 独自実装**です。

## 7. 今の重さの原因

重く見える主因は、drag 中に「単なる見た目の handle 移動」ではなく、実際に panel bounds と task stack bounds を何度も更新していることです。

現状の経路はこうです。

```text
1 move event
  -> KeyFrameEvent dispatch
  -> ScalableUiPocRuntimeLayoutController.handleEvent()
  -> StateManager.applyState()
  -> BasePanel.update()
  -> AutoTaskStackController.startTransition()
  -> map / calendar / radio の window bounds 変更
  -> 各 app が relayout / redraw
```

根拠になっている実装:

- [GripBarViewController.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/view/GripBarViewController.java)
- [ScalableUiPocRuntimeLayoutController.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/ScalableUiPocRuntimeLayoutController.java)

今回の修正で改善した点:

- drag event の二重送信を止めた
- 同じ ratio の再適用を止めた
- 左右 grip の breakpoint 解釈バグを直した

まだ残っている重さの本質:

- `AutoTaskStackController.startTransition()` を drag 中に細かく呼んでいる
- `calendar` や `radio` のような実アプリが毎回 relayout / redraw する

## 8. 次に効く改善案

### 案 A: drag 中は decor だけ動かし、task bounds は指を離した時だけ確定

```text
drag中
  - grip
  - 背景 panel
  - overlay preview
だけ更新

ACTION_UP
  - task bounds を 1 回だけ更新
```

長所:

- もっとも軽くなりやすい
- 実アプリの relayout 回数を激減できる

短所:

- drag 中に app コンテンツが本当には追従しない

### 案 B: task bounds 更新を間引く

```text
ACTION_MOVE ごとではなく
16ms / 32ms ごとに 1 回だけ反映
```

長所:

- 実装差分が比較的小さい

短所:

- 根本的には relayout を続けるので、重い app では限界がある

### 案 C: 固定 breakpoint だけに戻す

```text
drag中の連続 resize はやめて
NARROW / BALANCED / WIDE
COMPACT / BALANCED / TALL
だけにする
```

長所:

- 安定しやすい

短所:

- 「ユーザーが自由にサイズ変更する」体験は弱くなる

## 9. 現時点の整理

```text
ScalableUI で自然にできる:
  - panel の構成
  - panel への app 表示
  - app_panel への fullscreen launch
  - grip を event 入力として使うこと

ScalableUI だけでは足りず custom が必要:
  - 3 panel split の runtime 管理
  - smooth な continuous resize
  - heavy app を含む drag 中の性能最適化
  - FallbackHome 系 app の完全な task 意味づけ整理
```

この PoC でいちばん大事な境界は、  
**ScalableUI は「panel orchestration の土台」であって、「高性能な live-resize window manager」そのものではない** という点です。
