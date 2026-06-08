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

### 4-1. RRO の先にある code path

root PoC の実行経路は、実質次の 4 段階に分かれます。

```text
RRO XML
  -> XmlModelLoader / PanelStateXmlParser
  -> StateManager + PanelPool
  -> EventDispatcher + PanelTransitionCoordinator
  -> TaskPanel / DecorPanel + AutoTaskStackController
```

もう少し AAOS の実ファイルに寄せると次の通りです。

```text
CarSystemUIScalableUiPocRRO
  res/values/config.xml
  res/xml/*.xml
      |
      v
CarWMShellModule
  - config_enableScalableUI を見て初期化可否を決める
      |
      v
ScalableUIWMInitializer
  - PanelConfigReader.init()
  - ActionConfigReader.init()
  - PanelAutoTaskStackTransitionHandlerDelegate.init()
  - ScalableUiPocRuntimeLayoutController.init()
      |
      v
PanelConfigReader
  - R.array.window_states を順に読む
  - XmlModelLoader.createPanelState()
      |
      v
PanelStateXmlParser
  - Panel / Variant / Transition / Controller metadata を parse
      |
      v
StateManager.addState()
  - PanelPool から panel instance を取得
  - applyState() で BasePanel へ反映
  - panel.init()
      |
      +--> TaskPanel.init()
      |      - RootTaskStack 作成
      |      - default/persistent activity を設定
      |
      +--> DecorPanel.init()
             - Decor view / controller を作成
             - AutoDecor を display に attach
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

### 5-1. root PoC で何が「正」なのか

現在の root PoC は、**split layout を XML transition で持つ設計ではありません**。

正確には次の役割分担です。

```text
RRO XML
  - panel が存在すること
  - fixed app / launch-root panel があること
  - grip controller が event を出すこと

ScalableUiPocRuntimeLayoutController
  - widthRatio / heightRatio を保持
  - safe area を考慮した bounds を決める
  - 6 panel の runtime bounds を更新する
```

つまり root PoC の split state の source of truth は `ScalableUiPocRuntimeLayoutController` です。
このため、2026-06-07 時点では root PoC の `map/calendar/radio/grip/background` XML を
`opened` 1 variant に簡素化し、動的 split は code 側に一本化しています。

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

## 9. Dynamic Workspace 追補: SOLID refactor 後の責務境界

`dynamic-workspace` は、固定 XML slot を増やすのではなく、runtime model から panel を追加・削除・移動・resize する PoC である。
AAOS15 LTS5 / AAOS17 へ持ち出す際は、ScalableUI 本体への変更と PoC runtime を分けて見る。

```text
AAOS ScalableUI / WMShell への薄い接続
  |
  +-- CarWMComponent / CarWMShellModule
  |     WorkspaceRuntimeLayoutController を DI へ接続する
  |
  +-- SystemEventHandler
  |     workspace command broadcast を runtime controller へ渡す
  |
  +-- PanelAutoTaskStackTransitionHandlerDelegate
  |     TARGET_PANEL_ID / data URI から task を panel へ route する
  |
  +-- TaskPanelInfoRepository / TaskPanel / DecorPanelControllerBase
        runtime 生成 panel や surface 更新に必要な最小拡張

PoC 固有 runtime
  |
  +-- WorkspaceRuntimeLayoutController
  |     command/model/orchestration の入口
  |
  +-- WorkspaceModelStore
  |     Settings.Secure に panel list / width / viewport offset を保存
  |
  +-- WorkspaceGeometry
  |     bounds 計算、system bar 回避、grip/header/toolbar/viewport の位置決定
  |
  +-- WorkspacePanelStateController
  |     StateManager.addState、Variant runtime bounds、BasePanel surface 更新
  |
  +-- WorkspaceTaskRouter
        panel 用 app launch、picker launch、TaskPanel role 設定
```

### 9-1. 移植時に優先して見る場所

- まず `WorkspaceRuntimeLayoutController` の public entrypoint は維持する。
- AAOS の API 差が出やすいのは `WorkspacePanelStateController` の `StateManager` / `PanelPool` / `BasePanel.update(...)` 周辺。
- layout 仕様変更は `WorkspaceGeometry` に閉じる。
- app routing policy 変更は `WorkspaceTaskRouter` と `PanelAutoTaskStackTransitionHandlerDelegate` に閉じる。
- HMI の見た目や操作は demo app / decor view 側へ寄せ、ScalableUI core への変更を増やさない。

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

### 6-3. 外部記事と公開 PoC を踏まえた理解の更新

2026-06 時点では、次の外部情報も合わせて見ると ScalableUI の理解がかなり立体的になります。

- Medium: `Scalable UI in Android Automotive OS: The Panel Controller`
- ProAndroidDev: `Scalable UI in AAOS: From UI Embedding to System Window Orchestration`
- GitHub: `passenger6/MultiPanelLandscapeRRO`

この 3 つを踏まえると、ScalableUI は次の 3 層で理解するとズレが少ないです。

```text
[層1: 素の ScalableUI]
  - panel
  - variant
  - transition
  - event
  - TaskPanel / DecorPanel

[層2: PanelController による拡張]
  - XML だけで足りない runtime policy
  - focus追従
  - surface 操作
  - panel 間 coordination

[層3: product / PoC 固有の補助実装]
  - runtime layout helper
  - launcher/app routing policy
  - persistence
  - emulator 向け安定化
```

#### 更新された理解 1: `PanelController` は確かに重要だが、このツリーではまだ理想形ではない

記事群では `PanelController` がかなり強い imperative 拡張点として描かれています。

- `DecorPanelControllerBase` / `BaseTaskPanelController`
- `PanelUpdateConsumer`
- `AutoSurfaceTransaction`
- `PanelPool`
- `TaskStackListener`

この方向性自体は現行理解に取り込んでよいです。ただし、**この checkout の実装は記事ほど整理されていません**。

記事の説明:

- controller/view は Dagger map と `@AssistedInject` で差し込む
- controller が injected dependency を受けて runtime 制御する

このツリーの現実:

- `TaskPanelController` は `Class.forName()` + reflection 生成
- `DecorPanel` の View も reflection 生成
- 今回の PoC の runtime split 制御は汎用 controller ではなく product 固有 helper で実装

根拠:

- [PanelControllerInitializer.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/controller/PanelControllerInitializer.java)
- [DecorPanelControllerBase.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/view/DecorPanelControllerBase.java)
- [ScalableUiPocRuntimeLayoutController.java](/home/y-fuk/work/android-automotiveos15-lts3/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/ScalableUiPocRuntimeLayoutController.java)

#### 更新された理解 2: `zero code` は overlay 単体の話で、製品全体ではない

`MultiPanelLandscapeRRO` は README で

- `15 panels`
- `54 states`
- `93 transitions`
- `0 lines of Java/Kotlin`

を強く打ち出しています。

ここでの `0 lines of Java/Kotlin` は、**RRO overlay 自体の話**として読むのが正確です。実際の repo には次も含まれています。

- custom `CarLauncher.apk`
- `StubCarLauncher.apk`
- `MockWidgets.apk`
- signed overlay APK

つまり、理解を更新するとこうなります。

```text
ScalableUI で zero-code に近づけるのは
  「panel/variant/transition を定義する overlay 部分」

一方で別途必要になりやすいのは
  - HOME の置き換え
  - 専用デモ/ウィジェット Activity
  - product package 構成
  - SystemUI 側の有効化と場合によっては補助コード
```

これは、今のこの PoC の PoC で

- product 追加
- RRO 追加
- Launcher launch policy 修正
- SystemUI custom helper 追加

まで入っている理由とも一致します。

#### 更新された理解 3: 「Home Activity は不要」はビジョンとしては正しいが、実装方式は複数ある

ProAndroidDev 記事では、ScalableUI の理想形として

- system 自体が launcher になる
- app が widget のように並ぶ
- 従来の monolithic launcher をやめる

という思想が前面に出ています。

これは方向性としてはかなり重要です。ただし、このツリーではそれを **100% 純粋な形では採っていません**。

この PoC では今も:

- `app_panel` を fullscreen launch-root として使う
- All Apps 経由の起動 policy を Launcher 側で補助する
- variant によっては Home app / demo app を併用する

という設計が残っています。

なので、更新後の理解としては

```text
ScalableUI は「Launcher を薄くできる」し
場合によっては「system が launcher 化する」方向に寄せられる。

ただし実際の product / PoC では
  - launcher 完全廃止
  - launcher 補助利用
  - fullscreen fallback panel 併用
の中間形も普通にあり得る。
```

#### 更新された理解 4: system bar や HUN まで ScalableUI 化するのは “できることがある” が、今の PoC はそこまでやっていない

記事では「system bars and overlays も同じ cockpit state で動かせる」というビジョンが示されています。

ここは **ScalableUI の可能性としては理解に入れてよい**です。ただし、今の root PoC では

- top bar
- bottom bar

は ScalableUI panel ではなく、通常の `TopCarSystemBar` / `BottomCarSystemBar` window です。

つまり、

- 記事のビジョン
  - bars まで含めて ScalableUI orchestrated surface に寄せる
- 現在の PoC
  - main HMI panel だけ ScalableUI
  - bars は既存 SystemUI window

という差があります。

#### 更新された理解 5: `MultiPanelLandscapeRRO` は「純 XML でどこまで行けるか」の上限に近い参考例

`MultiPanelLandscapeRRO` は、今のこの PoC の段階設計にも参考になります。

- 固定 multipanel layout
- app grid の出入り
- custom event による page flip
- panel 背後の blur / shadow 的 decor

あたりは、かなり XML 中心で構成されています。

一方で、今ユーザーが興味を持っている

- panel を grip で連続 resize
- ユーザーが好きな panel に好きな app を割り当てる
- panel state を保存して復元する

は、`MultiPanelLandscapeRRO` README から見る限り **overlay 単体の主戦場ではなく、別途 policy / code が必要になりやすい領域**です。

この整理は、この PoC で Phase 1/2/3 に分けた方針を補強しています。

```text
Phase 1:
  固定 panel + 固定 app
  -> ScalableUI 素の強みが出やすい

Phase 2:
  grip resize
  -> ScalableUI + custom runtime 制御が必要

Phase 3:
  panel ごとの app assignment
  -> product logic / persistence / routing が必要
```

#### 参照先

- Medium: [Scalable UI in Android Automotive OS: The Panel Controller](https://medium.com/@passenger6/scalable-ui-in-android-automotive-os-the-panel-controller-031e6d727c27)
- ProAndroidDev: [Scalable UI in AAOS: From UI Embedding to System Window Orchestration](https://proandroiddev.com/scalable-ui-in-aaos-from-ui-embedding-to-system-window-orchestration-dae03b335eee)
- GitHub: [passenger6/MultiPanelLandscapeRRO](https://github.com/passenger6/MultiPanelLandscapeRRO/tree/main)

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
