# TwoPanelRROSafeBounds ScalableUI Demo Analysis

## 位置づけ

map_panel を常時表示し、app_panel を task open で前面表示する 2 panel 構成。

- Source: `packages/apps/Car/References/scalable-ui/codelab/TwoPanelRROSafeBounds`
- 種別: `codelab`
- Build module: `TwoPanelRROSafeBounds`

## 全体構成

```mermaid
flowchart TB
    Display[Display]
    Display --> app_panel["TaskPanel: app_panel<br/>default @id/closed"]
    Display --> map_panel["TaskPanel: map_panel<br/>default @id/opened"]
```

TaskPanel は 2 個、DecorPanel は 0 個、SystemWindow は 0 個確認できる。

## Panel 一覧

| Panel | 種類 | defaultVariant | role | controller | variants | keyframes | source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `app_panel` | `TaskPanel` | `@id/closed` | `@string/default_config` | `-` | `@+id/opened`, `@+id/closed` | - | `packages/apps/Car/References/scalable-ui/codelab/TwoPanelRROSafeBounds/res/xml/app_panel.xml` |
| `map_panel` | `TaskPanel` | `@id/opened` | `@array/nav_components` | `-` | `@+id/map_base`, `@+id/opened`, `@+id/closed` | - | `packages/apps/Car/References/scalable-ui/codelab/TwoPanelRROSafeBounds/res/xml/map_panel.xml` |

## 画面イメージ

```text
+--------------------------------------------------+
| map_panel            | app_panel                         |
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
| `app_panel` | `-` | `_System_TaskOpenEvent(panelId=panel_app_grid)` | `@id/closed` |
| `app_panel` | `-` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/opened` |
| `app_panel` | `-` | `_System_OnHomeEvent` | `@id/closed` |
| `map_panel` | `-` | `_System_OnHomeEvent` | `@id/opened` |

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

比較的容易。RRO module を build して overlay enable すれば構成確認しやすい。ただし default Activity の存在と ScalableUI 有効化は確認する。

想定手順:

1. `source build/envsetup.sh` と `lunch sdk_car_x86_64-trunk_staging-userdebug` を実行する。
2. `m TwoPanelRROSafeBounds` で RRO module を build する。複数 module がある場合は `TwoPanelRROSafeBounds` を確認する。
3. image に含める場合は `PRODUCT_PACKAGES += <module>` に追加する。手動確認なら APK を install して `cmd overlay enable --user 0 <package>` を実行する。
4. `cmd overlay list`、logcat、`dumpsys window`、screenshot で overlay と panel state を確認する。
5. system bar / immersive / user 10 などを扱う sample は、必要な user に overlay を有効化して SystemUI を restart する。


## Source files

- `packages/apps/Car/References/scalable-ui/codelab/TwoPanelRROSafeBounds/res/xml/app_panel.xml`
- `packages/apps/Car/References/scalable-ui/codelab/TwoPanelRROSafeBounds/res/xml/map_panel.xml`
