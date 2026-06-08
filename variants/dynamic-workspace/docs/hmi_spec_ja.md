# Dynamic Workspace HMI Spec

## 目的

固定された 3 panel 構成ではなく、ユーザー操作で panel を追加・削除・並び替え・横幅変更し、panel ごとに任意の launchable app を割り当てられる HMI を検証する。

## product

- slug: `dynamic-workspace`
- lunch: `sdk_car_scalableui_dynamic_workspace_x86_64-trunk_staging-userdebug`
- RRO module: `CarSystemUIScalableUiHmiDynamicWorkspaceRRO`

## RRO が定義する panel

- `workspace_home_panel`: workspace 背景と HOME 受け口。component は `com.android.car.scalableui.hmi.home/.WorkspaceHomeActivity`。
- `app_panel`: All Apps など通常 launcher entrypoint から起動された app の fullscreen fallback panel。

動的に増減する user panel は RRO XML では定義せず、SystemUI の `WorkspaceRuntimeLayoutController` が `StateManager.addState(...)` で runtime 生成する。

## demo app 側

- `WorkspaceHomeActivity`: HOME 受け口。resume 時に SystemUI へ sync broadcast を送る。
- `WorkspaceEmptyPanelActivity`: 空 panel の placeholder。picker 起動 affordance を持つ。
- `WorkspaceAppPickerActivity`: launchable app を列挙し、選択 component を workspace model へ反映する。
- `WorkspaceRuntimeBridge`: demo app から SystemUI runtime へ command/sync broadcast を送る。

## runtime model

`Settings.Secure` の `scalableui_dynamic_workspace_model_v2` に JSON で保存する。

```json
{
  "version": 2,
  "next_panel_index": 3,
  "viewport_offset_dp": 0,
  "panels": [
    {"id": "workspace_panel_1", "component": "package/.Activity", "width_dp": 420}
  ]
}
```

## 操作

- toolbar の `Add panel`: 空 panel を追加し、picker を開く。
- panel header の `App`: その panel 用 picker を開く。
- panel header の `Close`: panel を削除する。
- header drag: panel の順序を入れ替える。
- vertical grip drag: 隣接 panel の幅を変更する。
- viewport handle drag: 画面外にはみ出た panel 群を横スクロールする。

## 評価

Windows host emulator で `-memory 6144 -cores 6 -gpu angle_indirect` を指定する。評価履歴は `docs/dynamic_workspace_notes_ja.md` を参照する。
