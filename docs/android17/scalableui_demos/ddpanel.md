# DDPanelRRO ScalableUI Demo Analysis

## 位置づけ

nav_panel と app_panel を分け、panelId 付き task open で個別に開く構成。

- Source: `packages/apps/Car/References/scalable-ui/codelab/DDPanelRRO`
- 種別: `codelab`
- Build module: `DDPanelRRO`
- Certificate: `platform`
- Partition: `system_ext`

## 全体構成

```mermaid
flowchart TB
    Display[Display]
    Display --> app_panel["TaskPanel: app_panel<br/>default @id/closed"]
    Display --> nav_panel["TaskPanel: nav_panel<br/>default @id/closed"]
```

TaskPanel は 2 個、DecorPanel は 0 個、SystemWindow は 0 個確認できる。

## Panel 一覧

| Panel | 種類 | defaultVariant | role | controller | variants | keyframes | source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `app_panel` | `TaskPanel` | `@id/closed` | `@string/default_config` | `-` | `@+id/base`, `@+id/opened`, `@+id/closed` | - | `packages/apps/Car/References/scalable-ui/codelab/DDPanelRRO/res/xml/app_panel.xml` |
| `nav_panel` | `TaskPanel` | `@id/closed` | `-` | `@xml/map_panel_controller` | `@+id/base`, `@+id/opened`, `@+id/closed` | - | `packages/apps/Car/References/scalable-ui/codelab/DDPanelRRO/res/xml/nav_panel.xml` |

## 画面イメージ

```text
+--------------------------------------------------+
| nav_panel            | app_panel                         |
| default/opened       | closed -> opened on task  |
| Home returns base    | Home closes app panel     |
+--------------------------------------------------+
```

## 主な画面遷移とトリガー

```mermaid
flowchart LR
    Event[Event / trigger]
    State[StateManager.handleEvents]
    Tx[PanelTransaction]
    Coord[PanelTransitionCoordinator]
    WM[WMShell or AutoSurfaceTransaction]
    Panel[Panel variant update]
    Event --> State --> Tx --> Coord --> WM --> Panel
```

この demo では XML 上で 4 個の Transition が確認できる。主なものは以下。

| Panel | from | trigger | to |
| --- | --- | --- | --- |
| `app_panel` | `-` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/opened` |
| `app_panel` | `-` | `_System_OnHomeEvent` | `@id/closed` |
| `nav_panel` | `-` | `_System_TaskOpenEvent(panelId=nav_panel)` | `@id/opened` |
| `nav_panel` | `-` | `_System_OnHomeEvent` | `@id/closed` |

## Runtime の動き

```mermaid
sequenceDiagram
    participant User as User/System
    participant Event as Event source
    participant Dispatcher as EventDispatcher
    participant State as StateManager
    participant Coord as PanelTransitionCoordinator
    participant Panel as TaskPanel/DecorPanel
    participant Shell as WMShell/Surface
    User->>Event: Home, task open, drag, immersive, or custom trigger
    Event->>Dispatcher: executeEvent / executeEvents
    Dispatcher->>State: handleEvents
    State->>Coord: PanelTransaction
    Coord->>Panel: choose target variant
    Coord->>Shell: window change or surface animation
```

実際の処理経路は demo 固有 XML の Transition に従う。`TaskPanel` の bounds や visibility が変わる場合は Window State 変更になり、`DecorPanel` の alpha / overlay / grip 表示は direct surface animation 寄りに処理される。

## Source 上の実装ポイント

| 処理 | class / method | path |
| --- | --- | --- |
| XML 読み込み | `PanelConfigReader.loadConfig() / loadFromXml()` | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelConfigReader.java` |
| PanelState 生成 | `XmlModelLoader.createPanelState(int)` | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/loader/xml/XmlModelLoader.java` |
| event 評価 | `StateManager.handleEvents(...)` | `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/manager/StateManager.java` |
| transition 実行 | `PanelTransitionCoordinator.startTransition(...)` | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/PanelTransitionCoordinator.java` |
| TaskPanel root task | `TaskPanel.init()` | `packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/panel/TaskPanel.java` |
| root task 作成 | `AutoTaskStackControllerImpl.createRootTaskStack(...)` | `packages/services/Car/libs/car-wm-shell-lib/src/com/android/wm/shell/automotive/AutoTaskStackControllerImpl.kt` |

## 素の AAOS17 emulator への取り込み可否

可能。ただし RRO を build/install/enable するだけでは、参照 Activity、feature flag、required system property、system bar config の整合確認が必要。

想定手順:

1. `source build/envsetup.sh` と `lunch sdk_car_x86_64-trunk_staging-userdebug` を実行する。
2. `m DDPanelRRO` で RRO module を build する。複数 module がある場合は `DDPanelRRO` を確認する。
3. image に含める場合は `PRODUCT_PACKAGES += <module>` に追加する。手動確認なら APK を install して `cmd overlay enable --user 0 <package>` を実行する。
4. `cmd overlay list`、logcat、`dumpsys window`、screenshot で overlay と panel state を確認する。
5. system bar / immersive / user 10 などを扱う sample は、必要な user に overlay を有効化して SystemUI を restart する。

取り込み時に不足しやすい情報・software:

- static libs: com_android_car_scalableui_flags_lib
- flags packages: com_android_car_scalableui_flags
- required system property: car.ui.config=distantdisplay
- system_ext platform-signed RRO with ScalableUI flag library

## Source files

- `packages/apps/Car/References/scalable-ui/codelab/DDPanelRRO/res/xml/app_panel.xml`
- `packages/apps/Car/References/scalable-ui/codelab/DDPanelRRO/res/xml/nav_panel.xml`
