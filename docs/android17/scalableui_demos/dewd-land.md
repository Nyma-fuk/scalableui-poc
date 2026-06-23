# DEWDLand ScalableUI Demo Analysis

## 位置づけ

landscape 向けに map、widget、app の基本 panel を配置する構成。

- Source: `packages/apps/Car/SystemUI/samples/DEWDLand`
- 種別: `systemui-sample`
- Build module: `dewd-land-res-base, DewdLandAospRRO`
- Certificate: `platform`
- Partition: `system_ext`

## 全体構成

```mermaid
flowchart TB
    Display[Display]
    Display --> app_panel["TaskPanel: app_panel<br/>default @id/closed"]
    Display --> map_panel["TaskPanel: map_panel<br/>default @id/opened"]
    Display --> widget_panel["TaskPanel: widget_panel<br/>default @id/opened"]
```

TaskPanel は 3 個、DecorPanel は 0 個、SystemWindow は 0 個確認できる。

## Panel 一覧

| Panel | 種類 | defaultVariant | role | controller | variants | keyframes | source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `app_panel` | `TaskPanel` | `@id/closed` | `@string/default_config` | `-` | `@+id/base`, `@+id/opened`, `@+id/closed`, `@+id/suw_open`, `@+id/suw_close` | - | `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/app_panel.xml` |
| `map_panel` | `TaskPanel` | `@id/opened` | `-` | `@xml/map_panel_controller` | `@+id/base`, `@+id/opened`, `@+id/closed`, `@+id/suw`, `@+id/userswitch`, `@+id/keyguard_opened` | - | `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/map_panel.xml` |
| `widget_panel` | `TaskPanel` | `@id/opened` | `-` | `@xml/widget_panel_controller` | `@+id/base`, `@+id/opened`, `@+id/closed`, `@+id/suw`, `@+id/userswitch`, `@+id/keyguard_opened` | - | `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/widget_panel.xml` |

## 画面イメージ

```text
+--------------------------------------------------+
| map/background panel                              |
|   + multiple app task panels                      |
|   + decor panels for grip / overlay / switch      |
| transitions coordinate task open, drag, and home  |
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

この demo では XML 上で 30 個の Transition が確認できる。主なものは以下。

| Panel | from | trigger | to |
| --- | --- | --- | --- |
| `app_panel` | `-` | `_System_EnterSuwEvent` | `@id/suw_close` |
| `app_panel` | `@id/suw_open` | `_System_ExitSuwEvent` | `@id/closed` |
| `app_panel` | `@id/suw_close` | `_System_ExitSuwEvent` | `@id/closed` |
| `app_panel` | `@id/suw_close` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/suw_open` |
| `app_panel` | `@id/closed` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/opened` |
| `app_panel` | `@id/opened` | `_System_TaskOpenEvent(panelId=map_panel)` | `@id/closed` |
| `app_panel` | `@id/suw_open` | `_System_TaskCloseEvent(panelId=app_panel)` | `@id/suw_close` |
| `app_panel` | `@id/opened` | `_System_OnHomeEvent` | `@id/closed` |
| `app_panel` | `@id/opened` | `_System_TaskPanelEmptyEvent(panelId=app_panel)` | `@id/closed` |
| `app_panel` | `-` | `_System_BeforeUserSwitch` | `@id/closed` |
| `map_panel` | `-` | `_System_EnterSuwEvent` | `@id/suw` |
| `map_panel` | `@id/suw` | `_System_ExitSuwEvent` | `@id/opened` |
| `map_panel` | `@id/closed` | `_System_OnHomeEvent` | `@id/opened` |
| `map_panel` | `@id/opened` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/closed` |
| `map_panel` | `@id/closed` | `_System_TaskPanelEmptyEvent(panelId=app_panel)` | `@id/opened` |
| `map_panel` | `@id/closed` | `_System_TaskOpenEvent(panelId=map_panel)` | `@id/opened` |
| `map_panel` | `-` | `_System_BeforeUserSwitch` | `@id/userswitch` |
| `map_panel` | `@id/userswitch` | `_System_UserSwitchComplete` | `@id/opened` |
| `map_panel` | `-` | `_System_KeyguardShown` | `@id/keyguard_opened` |
| `map_panel` | `@id/keyguard_opened` | `_System_KeyguardHidden` | `@id/opened` |
| `widget_panel` | `-` | `_System_EnterSuwEvent` | `@id/suw` |
| `widget_panel` | `@id/suw` | `_System_ExitSuwEvent` | `@id/opened` |
| `widget_panel` | `@id/closed` | `_System_OnHomeEvent` | `@id/opened` |
| `widget_panel` | `@id/opened` | `_System_TaskOpenEvent(panelId=app_panel)` | `@id/closed` |
| `widget_panel` | `@id/closed` | `_System_TaskPanelEmptyEvent(panelId=app_panel)` | `@id/opened` |
| `widget_panel` | `@id/closed` | `_System_TaskOpenEvent(panelId=map_panel)` | `@id/opened` |
| `widget_panel` | `-` | `_System_BeforeUserSwitch` | `@id/userswitch` |
| `widget_panel` | `@id/userswitch` | `_System_UserSwitchComplete` | `@id/opened` |
| `widget_panel` | `-` | `_System_KeyguardShown` | `@id/keyguard_opened` |
| `widget_panel` | `@id/keyguard_opened` | `_System_KeyguardHidden` | `@id/opened` |

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
2. `m DewdLandAospRRO` で RRO module を build する。複数 module がある場合は `dewd-land-res-base, DewdLandAospRRO` を確認する。
3. image に含める場合は `PRODUCT_PACKAGES += <module>` に追加する。手動確認なら APK を install して `cmd overlay enable --user 0 <package>` を実行する。
4. `cmd overlay list`、logcat、`dumpsys window`、screenshot で overlay と panel state を確認する。
5. system bar / immersive / user 10 などを扱う sample は、必要な user に overlay を有効化して SystemUI を restart する。

取り込み時に不足しやすい情報・software:

- static libs: dewd-res-common, com_android_car_scalableui_flags_lib
- flags packages: com_android_car_scalableui_flags
- required system property: car.dewd.config=land
- uses system_ext platform-signed RRO modules and DEWD resource libraries

## Source files

- `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/app_panel.xml`
- `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/map_panel.xml`
- `packages/apps/Car/SystemUI/samples/DEWDLand/res/xml/widget_panel.xml`
