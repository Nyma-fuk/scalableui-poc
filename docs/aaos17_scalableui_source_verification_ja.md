# AAOS17 ScalableUI Source Verification

この文書は、AAOS17 / Android 17 `android-17.0.0_r1` workspace の source を正として、ScalableUI 関連記述の整合性を確認した結果をまとめる。

対象 source tree:

```text
/home/y-fuk/work/android17-r1
```

重要な前提:

- この repository の docs は正ではない。正は AAOS/AOSP source code である。
- Android17 では ScalableUI 本体は存在するが、我々の `declarative-multipanel` PoC product/RRO が AOSP 標準に入ったわけではない。
- ScalableUI の `TaskPanel` 表示経路は `TaskView` / `RemoteCarTaskView` そのものではない。

## Executive Summary

Android17 の ScalableUI 関連記述は、大枠では現在の整理と整合する。ただし、次の表現は補正が必要である。

| 観点 | 判定 | 補正 |
| --- | --- | --- |
| ScalableUI は CarSystemUI 側の HMI framework | Correct | Android17 source の README に明記されている |
| Panel にアプリを表示する | Partially Correct | 実装上は `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` |
| TaskPanel は TaskView / RemoteCarTaskView である | Incorrect | Android17 source では別経路 |
| Runtime panel generation は標準機能として完結する | Partially Correct | `StateManager.addState()` は存在するが、標準初期化は XML/DCF reload |
| Android17 では PoC 専用 product を作る | Incorrect | 現在のPoC workflowでは標準 `sdk_car_x86_64-trunk_staging-userdebug` に PoC 差分を重ねる |
| `BasePanel -> SysUIPanel` は確認済み rename と言い切る | Unverified | Android17 source が `SysUIPanel` を使うことは確認済み。Android16 比較 tree が現時点でローカル未存在のため、rename 断定は避ける |

## Claim: ScalableUI は AAOS SystemUI 内の framework である

### Related AOSP Components

- `PanelAutoTaskStackTransitionHandlerDelegate`
- `PanelTransitionCoordinator`
- `EventDispatcher`
- `TaskPanel`
- `DecorPanel`
- `SysUIPanel`

### Evidence

- `README.md`: ScalableUI は Android Automotive SystemUI の framework であり、panel / system window の presentation と behavior を管理する abstraction layer と説明している。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/README.md`
- `PanelAutoTaskStackTransitionHandlerDelegate.handleRequest(...)`: WM transition request から `Event` を計算し、`EventDispatcher.getTransaction(...)` と `PanelTransitionCoordinator.createAutoTaskStackTransaction(...)` へつなぐ。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java`
- `EventDispatcher.executeEvents(...)`: `StateManager` から `PanelTransaction` を取得し、`PanelTransitionCoordinator.startTransition(...)` を呼ぶ。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/EventDispatcher.java`

### Evaluation

Correct

### Reason

Android17 source 上で ScalableUI は通常アプリ用 toolkit ではなく、CarSystemUI / WMShell / WindowManager transition と接続する SystemUI 側 framework として実装されている。

## Claim: Panel にアプリを表示する

### Related AOSP Components

- `TaskPanel`
- `SysUIPanel`
- `RootTaskStack`
- `AutoTaskStackController`
- `AutoTaskStackControllerImpl`
- `ShellTaskOrganizer`

### Evidence

- `TaskPanel`: `RootTaskStack based implementation of a Panel` として定義され、`TaskPanel extends SysUIPanel` である。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`
- `TaskPanel.init(...)`: `AutoTaskStackController.createRootTaskStack(...)` を呼び、panel 用 root task stack を作る。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`
- `AutoTaskStackControllerImpl.createRootTaskStack(...)`: `TaskCreationParams.Builder()` を作り、`ShellTaskOrganizer.createTask(params, listener)` を呼ぶ。
  - `packages/services/Car/libs/car-wm-shell-lib/src/com/android/wm/shell/automotive/AutoTaskStackControllerImpl.kt`
- `ShellTaskOrganizer.createTask(...)`: `TaskCreationParams` に基づき task を作成する。
  - `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/ShellTaskOrganizer.java`

### Evaluation

Partially Correct

### Reason

ユーザー向けに「Panel にアプリを表示する」と言うことは可能だが、実装説明では `Panel -> Activity` ではなく、`Panel -> TaskPanel -> RootTaskStack / Task -> Activity` と書く必要がある。

## Claim: TaskPanel は TaskView / RemoteCarTaskView である

### Related AOSP Components

- `TaskPanel`
- `TaskView`
- `TaskViewRootTask`
- `RemoteCarTaskView`
- `RemoteCarTaskViewServerImpl`
- `CarLauncherViewModel`

### Evidence

- `TaskPanel` は `RootTaskStack` と `AutoTaskStackController` を使う。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`
- `TaskView` は `SurfaceView that can display a task` として実装され、`TaskViewTaskController` と連携する。
  - `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/taskview/TaskView.java`
- `TaskViewRootTask` は TaskView の root task 情報を表す interface である。
  - `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/taskview/TaskViewRootTask.kt`
- `RemoteCarTaskView` / `ControlledRemoteCarTaskView` / `RemoteCarRootTaskView` は `packages/services/Car/car-lib` 側に存在し、CarLauncher など別経路で利用される。
  - `packages/services/Car/car-lib/src/android/car/app/RemoteCarTaskView.java`
  - `packages/apps/Car/Launcher/app/src/com/android/car/carlauncher/CarLauncherViewModel.java`
- `RemoteCarTaskViewServerImpl` は CarSystemUI の remote task view server 実装であり、ScalableUI `TaskPanel` の親クラスではない。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/taskview/RemoteCarTaskViewServerImpl.java`

### Evaluation

Incorrect

### Reason

Android17 では TaskView / RemoteCarTaskView 経路も存在するが、ScalableUI `TaskPanel` の実体ではない。ScalableUI 側の panelized app 表示は root task stack / AutoTaskStack 経路で説明する。

## Claim: Panel 定義は XML から読み込まれる

### Related AOSP Components

- `PanelConfigReader`
- `XmlModelLoader`
- `PanelStateDocLoader`
- `PanelConfigReadStateMonitor`
- `StateManager`

### Evidence

- `PanelConfigReader.init()`: `PanelPool` を clear し、`PanelType` に応じて `DecorPanel` / `SysUIPanel` / `TaskPanel` factory を選ぶ。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- `PanelConfigReader.loadConfig()`: `Flag.ScalableUiDesignCompose` が有効なら DCF、そうでなければ XML を読み、`StateManager.reloadPanelState(panelStates)` を呼ぶ。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- `PanelConfigReader.loadFromXml()`: `R.array.window_states` を走査し、`XmlModelLoader.createPanelState(xmlResId)` で `PanelState` を生成する。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- `PanelConfigReader.reloadConfig(Configuration)`: configuration context を作り直して config を読み直す。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`

### Evaluation

Correct

### Reason

Android17 でも XML による panel state 定義は標準経路として存在する。ただし、読み込みは `addState()` を個別に積む説明より、`reloadPanelState(...)` による map reload として説明する方が正確である。

## Claim: Runtime panel generation は ScalableUI 標準機能として完結する

### Related AOSP Components

- `StateManager`
- `PanelConfigReader`
- `PanelPool`

### Evidence

- `StateManager.addState(PanelState)`: `PanelState` を map に追加し、`applyState(...)` 後に `PanelPool.getOrCreatePanel(...).init()` を呼ぶ。
  - `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java`
- `StateManager.reloadPanelState(Map<String, PanelState>)`: 既存構成と一致する場合は panel を更新し、一致しない場合は `PanelPool.clearPanels()` 後に panel state を再作成する。
  - `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java`
- `PanelConfigReader.loadConfig()`: 標準初期化では XML/DCF から panel state map を作り、`StateManager.reloadPanelState(...)` に渡す。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`

### Evaluation

Partially Correct

### Reason

`StateManager.addState()` は存在するため、runtime 追加の下回りとして使える可能性はある。ただし Android17 の標準 config flow は XML/DCF reload であり、任意 panel の UI、geometry、永続化、app picker、policy まで含む runtime panel generation は PoC/OEM custom と分類する。

## Claim: Transition は Window State と Surface を分けて扱う

### Related AOSP Components

- `PanelTransitionCoordinator`
- `PanelTransaction`
- `AutoSurfaceTransaction`
- `AutoTaskStackController`

### Evidence

- `README.md`: Window State は WindowManager 管理の visibility / size / position / Z-order、Surface は alpha / scale / translation / crop と説明する。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/README.md`
- `PanelTransitionCoordinator.startTransition(...)`: `PanelTransaction.hasWindowChanges()` が true の場合は `AutoTaskStackController.startTransition(...)` 経由、shell transition が発生しない場合は `startDirectAnimation(...)` に落とす。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelTransitionCoordinator.java`
- `PanelTransitionCoordinator.startDirectAnimation(...)`: WM transition を伴わない animation を直接実行する。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelTransitionCoordinator.java`

### Evaluation

Correct

### Reason

Android17 では、All Apps overlay、dismiss、maximize、Home restore を、WM change が必要なものと Surface animation で足りるものに分けて設計する必要がある。

## Claim: Launcher が Panel 管理主体である

### Related AOSP Components

- `CarLauncher`
- `CarLauncherViewModel`
- `RemoteCarTaskView`
- `CarSystemUI`
- `PanelConfigReader`
- `PanelAutoTaskStackTransitionHandlerDelegate`

### Evidence

- `CarLauncherViewModel` は `ControlledRemoteCarTaskView` を生成し、launcher 側の map card などに使う。
  - `packages/apps/Car/Launcher/app/src/com/android/car/carlauncher/CarLauncherViewModel.java`
- ScalableUI の panel config 読み込みは `PanelConfigReader` が CarSystemUI 側で行う。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- ScalableUI の WM transition bridge は `PanelAutoTaskStackTransitionHandlerDelegate` が担う。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java`

### Evaluation

Incorrect

### Reason

Launcher は HOME / AppGrid / RemoteCarTaskView 経路を持つが、ScalableUI panel 管理主体ではない。ScalableUI の主体は CarSystemUI と WMShell / WindowManager 側である。

## Claim: Android17 PoC は標準 AAOS target へ差分を重ねる

### Related AOSP Components

- `device/generic/car/sdk_car_x86_64.mk`
- `device/generic/car/AndroidProducts.mk`
- `packages/services/Car/car_product/scalableui_declarative_multipanel`

### Evidence

- 現在の local Android17 workspace では `sdk_car_x86_64.mk` が `car_scalableui_declarative_multipanel.mk` を inherit している。
  - `device/generic/car/sdk_car_x86_64.mk`
- `AndroidProducts.mk` には PoC 専用 `sdk_car_scalableui_declarative_multipanel_x86_64` target を追加しない方針で整理している。
  - `device/generic/car/AndroidProducts.mk`
- PoC package set は `car_scalableui_declarative_multipanel.mk` に集約され、launcher module は Android17 の DEWD `StubCarLauncher` と衝突しないよう `ScalableUiStubCarLauncher` とする。
  - `packages/services/Car/car_product/scalableui_declarative_multipanel/car_scalableui_declarative_multipanel.mk`
  - `packages/services/Car/car_product/scalableui_declarative_multipanel/apps/StubCarLauncher/Android.bp`
  - `packages/services/Car/car_product/dewd/apps/StubCarLauncher/Android.bp`

### Evaluation

Correct

### Reason

これは AOSP 標準機能の主張ではなく、この PoC の Android17 移植方針である。RAM制約下で Soong graph を重くしないため、標準 `sdk_car_x86_64-trunk_staging-userdebug` を維持し、PoC 差分を product package/RRO として重ねる。

## Incorrect / Risky Assumptions To Avoid

- `Panel -> Activity` と直接説明する。
- `TaskPanel == TaskView` または `TaskPanel == RemoteCarTaskView` と説明する。
- `StateManager.addState()` があるため runtime panel generation が量産標準機能として完成している、と説明する。
- `WindowContainerTransaction.reparent()` の存在だけで、ScalableUI 標準が Panel 間 task migration を提供すると説明する。
- Android17 に上げれば `declarative-multipanel` PoC product/RRO が自動的に入る、と説明する。
- Android17 source だけを見て、Android16 からの rename / added を断定する。比較対象 checkout がない場合は「Android17 source では存在する」と表現する。

## Documentation Updates Required

この検証結果に基づき、以下の文書では Android17 向け説明をこの文書へリンクする。

- `README.md`
- `docs/README_ja.md`
- `docs/android17_scalableui_delta_ja.md`
- `docs/android17_as_is_scalableui_migration_plan_ja.md`
- `docs/aaos_app_layer_scalableui_scope_ja.md`
- `docs/scalableui_window_manager_flow_ja.md`
