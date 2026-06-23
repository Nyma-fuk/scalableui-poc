# AOSP Source Verification

この文書は、ScalableUI PoC の docs を前提にせず、AAOS15 LTS3 / AOSP ソースコードを正として確認した結果をまとめる。
Android17 固有の確認結果は [aaos17_scalableui_source_verification_ja.md](aaos17_scalableui_source_verification_ja.md) を参照する。

対象は主に次の実装である。

- `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui`
- `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui`
- `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell`
- `frameworks/base/core/java/android/window/WindowContainerTransaction.java`
- `frameworks/base/services/core/java/com/android/server/wm`
- `packages/services/Car/car_product/scalableui_declarative_multipanel`

## Executive Summary

全体評価:

- `declarative-multipanel` の固定 XML / RRO baseline は、AOSP 実装と概ね整合する。
- `TaskPanel` は Activity を直接保持する概念ではなく、root task stack / task を介して Activity を表示する。
- `RemoteCarTaskView` / `TaskView` は AAOS に存在するが、ScalableUI の `TaskPanel` 表示経路とは別である。
- runtime panel 追加、任意 panel 移動、永続化、picker、drag preview は ScalableUI 標準だけでは完結せず、PoC / custom runtime 実装として扱う。
- `WindowContainerTransaction.reparent()` は AOSP に存在するが、現在の live ScalableUI source だけでは「Panel A から Panel B へ既存 task を直接 reparent する」実装は確認できない。

一致率:

- 主要 claim 22 件中、Correct 12 / Partially Correct 6 / Unverified 3 / Incorrect 1。
- 広義の一致率は 18 / 22、約 82%。
- ただし runtime workspace 系 docs は、未適用 patch や過去 variant の記述を含むため、本格適用設計の根拠にする前に live source と再照合する必要がある。

本格適用可能性:

- 固定 panel / variant / transition / default activity routing の baseline は本格適用検討の出発点にできる。
- runtime panel generation、panel assignment persistence、task migration、multi-display、user switching、process death recovery、focus / IME は追加設計が必要。
- docs では「ScalableUI 標準」「PoC custom」「未確認」を分けて扱う。

## Architecture Mapping

| docs concept | AOSP / AAOS 実装との対応 | Evaluation | 根拠 |
| --- | --- | --- | --- |
| Panel | `com.android.car.scalableui.panel.Panel` interface。bounds / layer / visibility / alpha / focus を持つ矩形管理単位。 | Correct | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/panel/Panel.java` |
| TaskPanel | AAOS15 LTS3 では `BasePanel` 系、Android17 では `SysUIPanel` 系。いずれも root task stack / task を扱い、Activity 直接ではない。 | Correct | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`, `docs/aaos17_scalableui_source_verification_ja.md` |
| DecorPanel | `AutoDecor` based implementation。layout / controller view を display に attach する。 | Correct | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/DecorPanel.java` |
| Variant | Panel の bounds / visibility / layer / alpha / focus / corner / insets などの状態。 | Correct | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/model/Variant.java` |
| Transition | event と toVariant を結び、StateManager が PanelTransaction を作る。 | Correct | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/model/Transition.java`, `StateManager.java` |
| StateManager | PanelState を保持し、event に応じて variant を変更し、Panel に状態を適用する。 | Correct | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java` |
| XML panel definition | `R.array.window_states` に列挙された XML を `PanelConfigReader` が読み込む。 | Correct | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java` |
| Workspace | AOSP 標準概念ではなく PoC HMI モデル。複数 Panel / Decor / runtime model の集合。 | Partially Correct | ScalableUI source に `Workspace` core concept はない。 |
| Assignment | 標準では `Role` / `config_default_activities`。任意 app picker assignment はPoC custom。 | Partially Correct | `AutoTaskStackHelper.java`, Stub `AppGridActivity.java` |
| Runtime Panel | `StateManager.addState()` は存在するが、任意数 panel 生成 UI / 永続化 / geometry は標準初期化経路ではない。 | Partially Correct | `StateManager.java`, `PanelConfigReader.java` |
| RemoteTaskView | ScalableUI TaskPanel の実体ではない。AAOS の RemoteCarTaskView / TaskView 経路は別に存在する。 | Incorrect if mapped to ScalableUI | `RemoteCarTaskViewServerImpl.java`, `TaskView.java`, `TaskPanel.java` |
| TaskDisplayArea | Activity launch / display area の platform 概念。Workspace と同一視しない。 | Partially Correct | `RootWindowContainer.java`, `TaskDisplayArea.java` |

## Claims

### Claim

ScalableUI は RRO から `window_states` を読み、XML の Panel / Variant / Transition を parse する。

### Related AOSP Components

- `PanelConfigReader`
- `XmlModelLoader`
- `PanelStateXmlParser`
- `StateManager`

### Evidence

- `PanelConfigReader.init()`: `R.array.window_states` を `TypedArray` として読み、`XmlModelLoader.createPanelState(xmlResId)` を呼ぶ。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- `StateManager.addState(PanelState)`: PanelState を保持し、`applyState()` 後に `PanelPool` から Panel を取得して `panel.init()` する。
  - `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java`
- `PanelStateXmlParser.parse(...)`: `<Panel>`, `<Variant>`, `<Transition>` を parse する。
  - `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/loader/xml/PanelStateXmlParser.java`

### Evaluation

Correct

### Reason

RRO XML による固定 panel 定義は ScalableUI 標準経路である。

## TaskPanel と Activity

### Claim

「Panel にアプリを表示する」は `Panel -> Activity` である。

### Related AOSP Components

- `TaskPanel`
- `AutoTaskStackController`
- `RootTaskStack`
- `ActivityOptions`
- `ShellTaskOrganizer`

### Evidence

- `TaskPanel` は `RootTaskStack based implementation of a Panel` として実装される。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`
- `TaskPanel.init()` は `mAutoTaskStackController.createRootTaskStack(getDisplayId(), getPanelId(), ...)` を呼ぶ。
  - `TaskPanel.java`
- `TaskPanel.setBaseIntent(...)` は `ActivityOptions.setLaunchRootTask(getRootStack().getRootTaskInfo().token)` を設定し、`PendingIntent` を送る。
  - `TaskPanel.java`
- task の出現は `onTaskAppeared(ActivityManager.RunningTaskInfo taskInfo, SurfaceControl leash)` で受ける。
  - `TaskPanel.java`

### Evaluation

Partially Correct

### Reason

ユーザー向け説明として「Panel にアプリを表示」は許容できるが、実装モデルは `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` である。`Panel -> Activity` と書く場合は不正確。

## Runtime Panel Generation

### Claim

ScalableUI 標準機能だけで任意数の panel を runtime 追加できる。

### Related AOSP Components

- `PanelConfigReader`
- `StateManager`
- `PanelPool`
- PoC `WorkspaceRuntimeLayoutController`
- PoC `WorkspacePanelStateController`

### Evidence

- 標準初期化は `R.array.window_states` の XML を読む。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
- `StateManager.addState(PanelState)` は存在し、runtime から呼べる API ではある。
  - `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java`
- 任意 panel の geometry、永続化、picker、drag、viewport を扱う `WorkspaceRuntimeLayoutController` 系は PoC patch 側の実装であり、現在の `declarative-multipanel` live source の標準経路ではない。
  - `<SCALABLEUI_POC_ROOT>/patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch`

### Evaluation

Partially Correct

### Reason

`StateManager.addState()` は存在するが、それだけでは標準機能としての runtime panel generation ではない。PoC / custom runtime 実装として分類する。

## App Relocation

### Claim

Panel A から Panel B への移動は relaunch ではなく reparent / task migration で実現する。

### Related AOSP Components

- `WindowContainerTransaction`
- `ShellTaskOrganizer`
- `PanelAutoTaskStackTransitionHandlerDelegate`
- `TaskPanelInfoRepository`

### Evidence

- AOSP には `WindowContainerTransaction.reparent(...)` と `reparentTasks(...)` が存在する。
  - `frameworks/base/core/java/android/window/WindowContainerTransaction.java`
- `ShellTaskOrganizer` は task appeared / changed / vanished を listener に通知する。
  - `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/ShellTaskOrganizer.java`
- live `PanelAutoTaskStackTransitionHandlerDelegate` は `TARGET_PANEL_ID` / data URI / component / launch-root から panel を選ぶが、直接 `WindowContainerTransaction.reparent(...)` を呼ぶ実装は確認できない。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java`

### Evaluation

Unverified

### Reason

AOSP の reparent 機構は存在する。PoC patch / historical docs には token reparent の記述がある。ただし現在の live source だけを根拠に「ScalableUI標準でPanel間task reparentできる」とは判断しない。

## Launcher Responsibility

### Claim

Launcher が Panel 管理主体である。

### Related AOSP Components

- `StubCarLauncher`
- `AppGridActivity`
- `CarSystemUI`
- `PanelConfigReader`
- `PanelAutoTaskStackTransitionHandlerDelegate`

### Evidence

- `StubCarLauncher` は HOME / AppGrid / placeholder Activity を提供する。
  - `packages/services/Car/car_product/scalableui_declarative_multipanel/apps/StubCarLauncher/AndroidManifest.xml`
- `AppGridActivity` は app を列挙し、必要なら `EXTRA_TARGET_PANEL_ID` を付けて `startActivity()` する。
  - `packages/services/Car/car_product/scalableui_declarative_multipanel/apps/StubCarLauncher/src/com/android/car/carlauncher/AppGridActivity.java`
- Panel XML 読み込み、PanelState 管理、routing delegate は CarSystemUI 側。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java`
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java`

### Evaluation

Incorrect

### Reason

Launcher は HOME host / AppGrid entry point / placeholder Activity であり、Panel 管理主体ではない。主体は `CarSystemUI` の ScalableUI runtime と WindowManager / ActivityTaskManager である。

## RemoteCarTaskView

### Claim

ScalableUI のアプリ埋め込み実体は RemoteTaskView / RemoteCarTaskView である。

### Related AOSP Components

- `RemoteCarTaskViewServerImpl`
- `TaskView`
- `TaskViewTaskController`
- `TaskPanel`

### Evidence

- `RemoteCarTaskViewServerImpl` は `TaskViewTaskController` を作り、remote client から task view 操作を受ける。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/taskview/RemoteCarTaskViewServerImpl.java`
- `TaskView` は `SurfaceView that can display a task`。
  - `frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/taskview/TaskView.java`
- `TaskPanel` は `RemoteCarTaskViewServerImpl` や `TaskView` を使わず、`RootTaskStack` と `AutoTaskStackController` を使う。
  - `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java`

### Evaluation

Incorrect

### Reason

RemoteCarTaskView は AAOS の別経路として存在するが、ScalableUI `TaskPanel` の実体ではない。

## Missing Considerations

対象AAOSでは docs の範囲に加えて以下を設計・検証する必要がある。

- Focus / IME / rotary / touch dispatch
- Activity lifecycle / process death / restart policy
- task persistence / recents / clear back stack
- user switching / locked user / multi-user package visibility
- multi-display / passenger display / cluster display
- display cutout / system bar / inset ownership
- Activity launchMode / taskAffinity / documentLaunchMode
- resource pressure / GPU memory / decoder / surface count
- camera / reverse gear / priority source arbitration
- permissions / privileged app boundary / hidden API dependency
- crash recovery / SystemUI restart / CarService restart
- AAOS15 LTS5 / AAOS17 API drift
