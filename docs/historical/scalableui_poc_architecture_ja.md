# ScalableUI PoC Architecture

> Source verification: この文書は Dynamic Workspace PoC の構成メモです。AAOS/AOSP 実装との照合結果は [AOSP Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aosp_source_verification_ja.md) を正とします。現在の live `declarative-multipanel` baseline には、任意数 runtime panel を生成する `WorkspaceRuntimeLayoutController` 系の実装は含まれていません。

この文書は、今回の ScalableUI PoC が AAOS のどこに何を追加し、どこまでを ScalableUI 標準で扱い、どこからを custom 実装しているかを整理するための全体図です。

## 1. 全体像

この図は `dynamic-workspace` patch 適用後の概念図です。clean baseline の `declarative-multipanel` では、中心は RRO XML と `CarSystemUI` の ScalableUI runtime routing であり、Dynamic Workspace runtime は未適用です。

```text
AAOS product
  |
  +-- device/generic/car
  |     sdk_car_scalableui_dynamic_workspace_x86_64.mk
  |
  +-- packages/services/Car
  |     Dynamic Workspace RRO
  |     ScalableUI HMI demo apps
  |
  +-- packages/apps/Car/SystemUI
  |     ScalableUI initialization
  |     task/panel routing
  |     dynamic workspace runtime
  |
  +-- packages/apps/Car/Launcher
  |     All Apps fullscreen routing hint
  |
  +-- packages/apps/Car/systemlibs/car-scalable-ui-lib
        runtime Variant override support
```

## 2. Product layer

`device/generic/car` に PoC 専用 product を追加する。

```text
sdk_car_scalableui_dynamic_workspace_x86_64.mk
  |
  +-- inherit sdk_car_x86_64.mk
  +-- inherit packages/services/Car/car_product/scalableui_hmi_dynamic_workspace/car_scalableui_hmi_dynamic_workspace.mk
```

役割:

- 既存 `sdk_car_x86_64` を壊さない
- Dewd など広い RRO 群へ依存しない
- Dynamic Workspace 用 package/RRO だけを追加する

## 3. RRO layer

`packages/services/Car/car_product/scalableui_hmi_dynamic_workspace` が Dynamic Workspace の RRO を持つ。

RRO で定義する panel:

- `workspace_home_panel`
- `app_panel`

```text
CarSystemUIScalableUiHmiDynamicWorkspaceRRO
  res/values/config.xml
    config_enableScalableUI = true
    window_states = workspace_home_panel, app_panel

  res/xml/workspace_home_panel.xml
    role = com.android.car.scalableui.hmi.home/.WorkspaceHomeActivity

  res/xml/app_panel.xml
    fullscreen fallback app panel
```

重要な設計:

- 動的 user panel は XML に列挙しない
- user panel は SystemUI runtime が `StateManager.addState(...)` で作る
- RRO は ScalableUI を有効化し、Home と fullscreen fallback の最低限だけを定義する

検証結果:

- `StateManager.addState(...)` は AOSP source に存在する
- ただし任意数 panel 生成、geometry、永続化、picker は ScalableUI 標準初期化経路ではない
- `PanelConfigReader` の標準初期化は `R.array.window_states` に列挙された XML を読む

## 4. Demo app layer

`packages/services/Car/car_product/scalableui_hmi_demo_apps` に HMI 用 demo app 群がある。

Dynamic Workspace で重要な Home demo app:

```text
ScalableUiHmiHomeDemoApp
  |
  +-- WorkspaceHomeActivity
  |     HOME 受け口。resume 時に SystemUI へ sync を送る。
  |
  +-- WorkspaceEmptyPanelActivity
  |     空 panel placeholder。Choose app affordance を出す。
  |
  +-- WorkspaceAppPickerActivity
  |     PackageManager から launchable app を列挙し、panel assignment を送る。
  |
  +-- WorkspaceRuntimeBridge
  |     ACTION_COMMAND / ACTION_SYNC broadcast を SystemUI へ送る。
  |
  +-- WorkspaceModelStore
        picker 用に現在の workspace model を読む。
```

## 5. SystemUI layer

Dynamic Workspace runtime は `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/workspace` にある。

注記: この path は `dynamic-workspace` patch 適用後の想定です。現在の live `declarative-multipanel` tree では確認できないため、AOSP 標準機能ではなく PoC custom 実装として扱います。

```text
WorkspaceRuntimeLayoutController
  |
  +-- WorkspaceModelStore
  +-- WorkspaceGeometry
  +-- WorkspacePanelStateController
  +-- WorkspaceTaskRouter
  +-- WorkspaceHeaderView / Controller
  +-- WorkspaceGripView / Controller
  +-- WorkspaceToolbarView / Controller
  +-- WorkspaceViewportHandleView / Controller
```

SOLID refactor 後の責務:

- `WorkspaceRuntimeLayoutController`: command を受け、model を更新し、反映処理を orchestration する
- `WorkspaceGeometry`: bounds 計算、system bar 回避、header/grip/toolbar/viewport の配置を決める
- `WorkspacePanelStateController`: runtime panel state 登録、Variant 更新、surface 反映を担う
- `WorkspaceTaskRouter`: assigned component を TaskPanel role に設定し、panel/picker launch を行う
- `WorkspaceModelStore`: `Settings.Secure` の JSON model を読み書きする

## 6. Routing layer

app をどの panel に出すかは次の情報で決める。

```text
Intent extra:
  com.android.car.scalableui.extra.TARGET_PANEL_ID

Intent data URI:
  scalableui-hmi://panel-launch?target_panel=<panelId>
```

`PanelAutoTaskStackTransitionHandlerDelegate` はこの情報を見て、対象 task の target panel routing 方針を決める。既存 task の reparent は historical patch / PoC custom policy として扱う。

検証結果:

- `TARGET_PANEL_ID` / data URI を読む処理は live `PanelAutoTaskStackTransitionHandlerDelegate` に存在する
- AOSP の `WindowContainerTransaction.reparent(...)` は存在する
- ただし live ScalableUI source だけでは、既存 task を Panel A から Panel B へ直接 reparent する標準実装は未確認

All Apps からの通常起動は fullscreen `app_panel` を優先する。panel header / picker 経由の assignment は target panel を明示する。

## 7. Runtime model

保存先:

```text
Settings.Secure
key = scalableui_dynamic_workspace_model_v2
```

例:

```json
{
  "version": 2,
  "next_panel_index": 3,
  "viewport_offset_dp": 0,
  "panels": [
    {
      "id": "workspace_panel_1",
      "component": "com.android.car.scalableui.hmi.map/.MapActivity",
      "width_dp": 420
    }
  ]
}
```

source of truth:

- panel 数
- panel 順序
- panel width
- assigned component
- viewport offset

## 8. 操作 flow

```text
User
  |
  +-- Add panel
  |     WorkspaceToolbarView
  |       -> ACTION_COMMAND add_panel
  |       -> Runtime adds empty panel
  |       -> Picker opens fullscreen
  |
  +-- Choose app
  |     WorkspaceAppPickerActivity
  |       -> ACTION_COMMAND assign_component
  |       -> Runtime updates model
  |       -> WorkspaceTaskRouter launches component to target panel
  |
  +-- Resize grip
  |     WorkspaceGripView
  |       -> resize_start
  |       -> resize_update
  |       -> resize_end
  |
  +-- Drag header
        WorkspaceHeaderView
          -> move_start
          -> move_update
          -> move_end
```

## 9. Resize の性能設計

drag 中:

- model width は更新する
- task panel surface は更新しない
- header / toolbar / viewport も更新しない
- 操作中 grip decor のみ preview 更新する

drag end:

- model を保存する
- panel / header / grip の最終配置を反映する
- ActivityTaskManager への task-stack transition は投げない

理由:

- drag 中に app task surface を更新し続けると重い
- HOME task を task-stack transition 対象にすると activity type 変更で SystemUI が落ちるケースがあった
- Google の demo に近い「drag 中は app を逐次再描画しない」体験へ寄せるため

## 10. ScalableUI 標準と custom の境界

ScalableUI 標準:

- XML panel 宣言
- XML variant / transition
- TaskPanel / DecorPanel 管理
- panel layer / visibility / bounds
- event dispatch
- persistent activity role

PoC custom:

- runtime panel 生成
- dynamic geometry
- panel assignment persistence
- app picker
- drag preview optimization
- All Apps と panel assignment の routing 分離

追加の実装上の境界:

- `TaskPanel` は Activity を直接保持せず、root task stack / task を介して Activity を表示する
- `RemoteCarTaskView` / `TaskView` は ScalableUI `TaskPanel` の実体ではない
- `Workspace` は AOSP の `TaskDisplayArea` ではなく、PoC HMI 側の概念である

## 11. 移植時に壊れやすい場所

AAOS15 LTS5 / AAOS17 へ移植するときに優先して確認する場所:

- `WorkspacePanelStateController`
- `PanelAutoTaskStackTransitionHandlerDelegate`
- `DecorPanelControllerBase`
- `TaskPanelInfoRepository`
- `CarWMComponent` / `CarWMShellModule`
- `CarSystemUIInitializer` / `CarSysUIComponent`

移植方針:

- まず build error を API 差分として分類する
- ScalableUI core に広く手を入れず、workspace package 側で吸収できるかを見る
- Dagger graph の変更は最小限にする
- RRO XML だけで解ける問題と runtime code が必要な問題を混ぜない

## 12. 評価済み事実

2026-06-09 の評価:

- product: `sdk_car_scalableui_dynamic_workspace_x86_64`
- AVD: `Y-Fuk-dynamic-workspace-eval3`
- emulator args: `-memory 6144 -cores 6 -gpu angle_indirect`
- artifact: `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor`

結果:

- `CarSystemUI` build 成功
- `dynamic-workspace` emulator image zip build 成功
- 1回目 drag: `420dp / 420dp` から `287dp / 553dp`
- 2回目 drag: `287dp / 553dp` から `420dp / 420dp`
- SystemUI PID 維持
- fatal なし
- slow dispatch は各 drag 1件
