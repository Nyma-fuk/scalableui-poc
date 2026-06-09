# AAOS ScalableUI / WindowManager 表示フロー

> Source verification: この文書は 2026-06-09 に AAOS/AOSP source と照合済みです。詳細な claim 判定は [AOSP Source Verification](./aosp_source_verification_ja.md) を参照してください。

このドキュメントは、`aaos-scalable-ui-specs` と `declarative-multipanel` PoC を前提に、AAOS における ScalableUI、SystemUI、WindowManager、Launcher、各 panel、各アプリ Activity の関係を整理したものです。

目的は、ScalableUI を「Launcher 内の widget 実装」ではなく、「SystemUI が WindowManager / ActivityTaskManager と連携して複数アプリ Activity を panel として orchestrate する仕組み」として理解することです。

## 全体像

```mermaid
flowchart TB
    Product[AAOS Product<br/>sdk_car_scalableui_declarative_multipanel_x86_64]
    FrameworkRRO[Framework RRO<br/>remote inset / system bar control]
    CarServiceRRO[CarService RRO<br/>PoC product overlay]
    SystemUIRRO[SystemUI RRO<br/>config_enableScalableUI<br/>window_states<br/>default_activities]
    StubLauncher[StubCarLauncher<br/>empty HOME host<br/>AppGrid / placeholders]
    CarSystemUI[CarSystemUI<br/>ScalableUI runtime]
    Parser[ScalableUI XML parser<br/>Panel / Variant / Transition]
    StateManager[Panel StateManager<br/>current variant / event dispatch]
    WM[WindowManager / Shell<br/>TaskOrganizer / DisplayArea]
    ATM[ActivityTaskManager<br/>Activity launch / task lifecycle]
    PanelTasks[Panel task containers<br/>multi-window bounds]
    Apps[Activity tasks<br/>Nav / Media / User app / Camera / AppGrid]
    Display[Physical display<br/>AAOS bars + panels]

    Product --> FrameworkRRO
    Product --> CarServiceRRO
    Product --> SystemUIRRO
    Product --> StubLauncher
    SystemUIRRO --> CarSystemUI
    FrameworkRRO --> CarSystemUI
    CarServiceRRO --> CarSystemUI
    StubLauncher --> Display
    CarSystemUI --> Parser
    Parser --> StateManager
    StateManager --> WM
    CarSystemUI --> ATM
    ATM --> Apps
    Apps --> PanelTasks
    WM --> PanelTasks
    PanelTasks --> Display
```

## 画面レイヤ

```text
┌─────────────────────────────────────────────────────────────┐
│ Physical Display 1920x1080                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ AAOS top bar area                                     │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ ScalableUI workspace                                  │  │
│  │  ┌──────────────────────────┐ ┌────────────────────┐  │  │
│  │  │ nav_panel                │ │ media_panel        │  │  │
│  │  │ Navigation / map task    │ ├────────────────────┤  │  │
│  │  │                          │ │ user_slot_panel    │  │  │
│  │  │                          │ │ empty or user app  │  │  │
│  │  └──────────────────────────┘ └────────────────────┘  │  │
│  │                                                       │  │
│  │  overlays: panel_app_grid / app_panel                 │  │
│  │  priority: camera_priority_panel / edit_overlay_panel │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ AAOS bottom bar / HVAC area                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

裏側:

StubCarLauncher
  空の HOME Activity。標準 CarLauncher UI を出さず、ScalableUI が見える土台になる。

CarSystemUI
  RRO から panel XML を読み、WindowManager / ActivityTaskManager に task 配置を依頼する。

WindowManager / Shell
  panel bounds に対応する root task stack / task surface を管理する。

各アプリ
  Launcher の widget ではなく、独立した Activity task として panel に載る。
```

## 表示までの時系列

```mermaid
sequenceDiagram
    participant Boot as System boot
    participant Product as Product packages
    participant Launcher as StubCarLauncher
    participant SysUI as CarSystemUI
    participant RRO as SystemUI RRO
    participant Parser as ScalableUI parser
    participant WM as WindowManager / Shell
    participant ATM as ActivityTaskManager
    participant App as App Activity
    participant Screen as Display

    Boot->>Product: product package list を読み込む
    Product->>Launcher: StubCarLauncher を HOME として用意
    Product->>SysUI: CarSystemUI を起動
    SysUI->>RRO: config_enableScalableUI / window_states を解決
    RRO->>Parser: panel XML を渡す
    Parser->>SysUI: PanelState / Variant / Transition を生成
    SysUI->>ATM: config_default_activities の Activity を起動
    ATM->>App: Nav / Media / EmptySlot / Camera / AppGrid Activity を生成
    SysUI->>WM: panel bounds / layer / visibility を適用
    WM->>App: Activity task を multi-window bounds に配置
    App->>Screen: 各 panel 内に描画
    Launcher->>Screen: 空の HOME 背景を提供
```

## アプリ起動から Panel 表示までの流れ

ここが ScalableUI を理解する上で一番大事です。アプリ起動そのものは `ActivityTaskManager` が扱い、ScalableUI は「起動された task をどの panel に収めるか」を決めます。

```mermaid
sequenceDiagram
    participant User as User
    participant Entry as Entry point<br/>System Bar Apps / AppGrid / HOME event
    participant Launcher as StubCarLauncher<br/>AppGridActivity
    participant ATM as ActivityTaskManager
    participant Delegate as PanelAutoTaskStackTransitionHandlerDelegate
    participant State as ScalableUI StateManager
    participant WCT as WindowContainerTransaction
    participant Shell as WindowManager / Shell
    participant Panel as TaskPanel
    participant App as App Activity task
    participant Screen as Display

    User->>Entry: app 起動操作
    Entry->>Launcher: AppGrid を開く or target panel 付き intent を作る
    Launcher->>ATM: startActivity(intent)
    ATM->>Delegate: task open transition を通知
    Delegate->>Delegate: component / TARGET_PANEL_ID / launch-root を評価
    Delegate->>Panel: 対象 TaskPanel を選ぶ
    Delegate->>State: _System_TaskOpenEvent(panelId=...)
    State->>Panel: panel variant を opened / closed / hidden へ更新
    Delegate->>WCT: panel root / bounds / launch-root 方針を transaction 化
    WCT->>Shell: transaction 適用
    Shell->>App: task bounds / layer / visibility を反映
    App->>Screen: panel 内に描画
```

同じ流れを責務で分けるとこうなります。

```text
1. ユーザー操作
   System Bar Apps、AppGrid、panel assignment UI などから app 起動要求が出る。

2. ActivityTaskManager
   Activity を起動する。
   既存 task を再利用するか、新しい task を作る。
   task lifecycle を管理する。

3. ScalableUI routing
   PanelAutoTaskStackTransitionHandlerDelegate が起動された task を見る。
   TARGET_PANEL_ID があれば、その panel を優先する。
   component を扱う固定 panel があれば、その panel を候補にする。
   どれにも当てはまらない場合は launch-root の app_panel を使う。

4. ScalableUI StateManager
   _System_TaskOpenEvent や custom event を dispatch する。
   panel XML の Transition に従って各 panel の variant を切り替える。

5. WindowManager / Shell
   WindowContainerTransaction を受け取る。
   TaskPanel の root task stack と task surface の bounds / layer / visibility を反映する。
   Surface / layer / focus / visibility を実画面へ反映する。

6. App Activity
   アプリ自身は通常の Activity として描画する。
   アプリは「自分が panel にいる」ことを基本的には知らなくてもよい。
```

このため、ScalableUI では `RemoteTaskView` 的に「View の中へ Activity を埋め込む」のではなく、Android platform 側の task を `TaskPanel` として配置します。

実装上の最短モデル:

```text
Panel
  -> TaskPanel
  -> RootTaskStack / Task
  -> Activity
```

`RemoteCarTaskView` / `TaskView` は AAOS に別経路として存在しますが、この ScalableUI `TaskPanel` 表示経路の実体ではありません。

## 起動経路ごとの Panel Routing

同じ app 起動でも、入口によって routing policy が変わります。ここを分けておかないと「Settings が Home の後ろに出る」「Calendar が意図しない panel に出る」といった不整合が起きます。

```mermaid
flowchart TB
    Launch[App launch request]
    HasTarget{TARGET_PANEL_ID<br/>or target panel URI?}
    TargetPanel[Route to requested TaskPanel<br/>ex: user_slot_panel]
    FixedRole{Component handled by<br/>fixed TaskPanel?}
    FixedPanel[Route to fixed panel<br/>ex: nav_panel default app]
    LaunchRoot{Launch-root panel exists?}
    AppPanel[Route to app_panel<br/>generic fullscreen app]
    Fallback[Fallback to platform default launch]
    Event[Dispatch _System_TaskOpenEvent<br/>panelId=selected panel]
    Wm[Apply WCT through<br/>WindowManager / Shell]
    Screen[Activity appears in panel]

    Launch --> HasTarget
    HasTarget -- yes --> TargetPanel
    HasTarget -- no --> FixedRole
    FixedRole -- yes --> FixedPanel
    FixedRole -- no --> LaunchRoot
    LaunchRoot -- yes --> AppPanel
    LaunchRoot -- no --> Fallback
    TargetPanel --> Event
    FixedPanel --> Event
    AppPanel --> Event
    Fallback --> Wm
    Event --> Wm
    Wm --> Screen
```

`declarative-multipanel` の smoke で確認している代表例:

```text
AppGrid から Calendar を選ぶ
  -> intent に user_slot_panel target を付ける
  -> ActivityTaskManager が Calendar task を起動
  -> ScalableUI が user_slot_panel を選ぶ
  -> Calendar task が user_slot_panel bounds に表示される

System Bar Apps を開く
  -> panel_app_grid を fullscreen-ish overlay として開く
  -> workspace panel は維持
  -> AppGrid は panel_app_grid bounds に表示される

未割当の通常 app を generic 起動する
  -> fixed panel に紐づかない
  -> launch-root の app_panel を使う
  -> app_panel が開き、workspace panel は hidden になる

camera override
  -> camera_priority_panel を fullscreen high-layer に出す
  -> workspace panel 自体は hidden にしない
  -> exit_camera_override で camera panel だけ hidden に戻す
```

## ActivityTaskManager / WindowManager / ScalableUI の立ち位置

```text
ActivityTaskManager
  Activity の起動、task 作成、既存 task 再利用、task lifecycle を担当する。
  「どの Activity が生きているか」の管理者。

WindowManager / Shell
  task container、bounds、layer、focus、Surface の適用を担当する。
  「task を画面上のどこにどう置くか」の実行者。

CarSystemUI ScalableUI
  panel XML、variant、transition、routing policy を担当する。
  「HMI としてどの panel 状態にするか」の設計図兼オーケストレーター。

StubCarLauncher
  空の HOME host と AppGrid entrypoint を提供する。
  HMI の主表示主体ではなく、ScalableUI が前面で成立するための土台。
```

短く言うと、`ActivityTaskManager` が task を生み、`WindowManager / Shell` が配置し、`ScalableUI` が HMI としての panel 方針を決めます。

注意: AOSP の `WindowContainerTransaction` には `reparent()` / `reparentTasks()` が存在します。ただし、現在の live ScalableUI source だけでは「既存 task を Panel A から Panel B へ直接 reparent する」標準実装は確認できていません。panel assignment / relocation を説明するときは、標準 ScalableUI と PoC custom routing を分けて扱います。

## Panel と Activity の対応

```mermaid
flowchart LR
    subgraph SystemUI_RRO[CarSystemUI RRO]
      WindowStates[window_states]
      DefaultActivities[config_default_activities]
      Roles[role strings]
    end

    subgraph Panels[ScalableUI Panels]
      TopBar[top_bar_panel]
      BottomBar[bottom_bar_panel]
      Hvac[hvac_panel]
      NavPanel[nav_panel]
      MediaPanel[media_panel]
      UserSlot[user_slot_panel]
      EmptyHint[empty_slot_hint_panel]
      CameraPanel[camera_priority_panel]
      EditOverlay[edit_overlay_panel]
      AppGridPanel[panel_app_grid]
      AppPanel[app_panel]
    end

    subgraph Activities[Activity tasks / Decor]
      TransparentDecor[transparent DecorPanel<br/>AAOS as-is area reservation]
      NavActivity[com.android.car.mapsplaceholder<br/>.MapsPlaceholderActivity]
      MediaActivity[com.android.car.carlauncher<br/>.ControlBarActivity]
      EmptySlotActivity[com.android.car.carlauncher<br/>.EmptySlotActivity]
      UserApp[User selected app<br/>ex: Calendar]
      CameraActivity[com.android.car.carlauncher<br/>.CameraStubActivity]
      EditDecor[edit overlay layout]
      HintDecor[empty slot hint layout]
      AppGridActivity[com.android.car.carlauncher<br/>.AppGridActivity]
      GenericApp[Generic app launch<br/>app_panel]
    end

    WindowStates --> TopBar
    WindowStates --> BottomBar
    WindowStates --> Hvac
    WindowStates --> NavPanel
    WindowStates --> MediaPanel
    WindowStates --> UserSlot
    WindowStates --> EmptyHint
    WindowStates --> CameraPanel
    WindowStates --> EditOverlay
    WindowStates --> AppGridPanel
    WindowStates --> AppPanel

    DefaultActivities --> NavActivity
    DefaultActivities --> MediaActivity
    DefaultActivities --> EmptySlotActivity
    DefaultActivities --> CameraActivity
    DefaultActivities --> AppGridActivity

    Roles --> GenericApp

    TopBar --> TransparentDecor
    BottomBar --> TransparentDecor
    Hvac --> TransparentDecor
    NavPanel --> NavActivity
    MediaPanel --> MediaActivity
    UserSlot --> EmptySlotActivity
    UserSlot --> UserApp
    EmptyHint --> HintDecor
    CameraPanel --> CameraActivity
    EditOverlay --> EditDecor
    AppGridPanel --> AppGridActivity
    AppPanel --> GenericApp
```

## Event / Transition の流れ

ScalableUI は、イベントを受けて panel の variant を切り替えます。アプリ自体を再実装するのではなく、panel の bounds、visibility、layer、focus を切り替えるのが中心です。

```mermaid
flowchart TB
    Event[Event<br/>_System_TaskOpenEvent<br/>switch_workspace_page_2<br/>resize_panel_nav_wide<br/>swap_panel_position_nav_media<br/>enter_layout_edit<br/>enter_camera_override]
    Token[Event token<br/>panelId=user_slot_panel<br/>panelId=app_panel]
    StateManager[ScalableUI StateManager]
    NavVariant[nav_panel<br/>workspace_default / page_2 / wide / swapped / hidden]
    MediaVariant[media_panel<br/>workspace_default / page_2 / narrow / swapped / hidden]
    UserVariant[user_slot_panel<br/>empty / page_2 / narrow / hidden]
    AppGridVariant[panel_app_grid<br/>opened / closed]
    AppVariant[app_panel<br/>opened / closed]
    CameraVariant[camera_priority_panel<br/>camera_fullscreen / hidden]
    EditVariant[edit_overlay_panel<br/>editing / hidden]
    WM[WindowManager applies<br/>bounds / visibility / layer]
    Screen[Screen result]

    Event --> Token
    Token --> StateManager
    StateManager --> NavVariant
    StateManager --> MediaVariant
    StateManager --> UserVariant
    StateManager --> AppGridVariant
    StateManager --> AppVariant
    StateManager --> CameraVariant
    StateManager --> EditVariant
    NavVariant --> WM
    MediaVariant --> WM
    UserVariant --> WM
    AppGridVariant --> WM
    AppVariant --> WM
    CameraVariant --> WM
    EditVariant --> WM
    WM --> Screen
```

例:

```text
_System_TaskOpenEvent panelId=user_slot_panel
  Calendar task        -> user_slot_panel bounds
  panel_app_grid       -> closed
  empty_slot_hint_panel -> hidden

_System_TaskOpenEvent panelId=app_panel
  app_panel       -> opened
  nav_panel       -> hidden
  media_panel     -> hidden
  user_slot_panel -> hidden
  panel_app_grid  -> closed

enter_camera_override
  camera_priority_panel -> camera_fullscreen
  panel_app_grid        -> closed
  app_panel             -> closed
  edit_overlay_panel    -> hidden

exit_camera_override
  camera_priority_panel -> hidden
```

`camera_override` では `nav_panel` / `media_panel` / `user_slot_panel` を hidden にしません。workspace panel を隠すと empty panel event が発火し、復帰後に黒い HOME が見えるためです。この PoC では camera を fullscreen high-layer として workspace の上に被せます。

## Launcher との関係

AAOS car product では標準 `CarLauncher` が product package に含まれ、`com.android.car.carlauncher/.CarLauncher` を HOME Activity として宣言しています。

標準 `CarLauncher` を残すと、Home card / fragment / AppGrid / control bar など Launcher 側の UI が ScalableUI HMI と干渉します。記事の Step 3 にある通り、この PoC では `StubCarLauncher` を入れて標準 Launcher を退避します。

```text
標準 CarLauncher を使う場合:

  CarLauncher Home UI
    ├─ Launcher 自身の layout / fragment / cards
    └─ ScalableUI panels

  問題:
    標準 Home UI が裏で生きる。
    Launcher 側の fragment / card 実装が ScalableUI PoC と干渉する。
    Home が crash すると、ScalableUI panel が見えていても HMI 全体として不安定。


StubCarLauncher を使う場合:

  StubCarLauncher
    └─ 空の HOME host

  CarSystemUI ScalableUI
    ├─ nav_panel              -> Navigation / map Activity task
    ├─ media_panel            -> Media placeholder Activity task
    ├─ user_slot_panel        -> EmptySlot or user-selected app task
    ├─ empty_slot_hint_panel  -> DecorPanel hint
    ├─ camera_priority_panel  -> Camera Activity task
    ├─ edit_overlay_panel     -> DecorPanel edit UI
    ├─ panel_app_grid         -> AppGrid Activity task
    └─ app_panel              -> generic app task

  狙い:
    Launcher を HMI の主役にしない。
    SystemUI / WindowManager orchestration に表示責務を寄せる。
```

## Launcher を含めた実体関係図

```mermaid
flowchart TB
    subgraph Product[AAOS Product]
      SDK[sdk_car_x86_64 base]
      CarMk[car.mk / car_system.mk<br/>CarLauncher included by default]
      PocMk[car_scalableui_declarative_multipanel.mk<br/>RRO + StubCarLauncher]
    end

    subgraph LauncherLayer[Launcher package layer]
      RealLauncher[Standard CarLauncher<br/>HOME UI + cards + fragments]
      StubLauncher[StubCarLauncher<br/>same package<br/>empty HOME host]
    end

    subgraph SystemUILayer[CarSystemUI ScalableUI]
      RRO[SystemUI RRO<br/>config_enableScalableUI<br/>window_states]
      Panels[Panel StateManager<br/>nav/media/user_slot/appgrid/app/camera/edit]
    end

    subgraph Platform[Android platform]
      ATM[ActivityTaskManager]
      WM[WindowManager / Shell]
    end

    subgraph Apps[Activity tasks]
      Nav[MapsPlaceholderActivity]
      Media[ControlBarActivity]
      Empty[EmptySlotActivity]
      UserApp[User selected app<br/>Calendar in smoke]
      Camera[CameraStubActivity]
      AppGrid[AppGridActivity]
      Generic[Generic launched app]
    end

    SDK --> CarMk
    CarMk --> RealLauncher
    PocMk --> StubLauncher
    StubLauncher -. overrides .-> RealLauncher
    PocMk --> RRO
    StubLauncher -->|HOME background only| SystemUILayer
    RRO --> Panels
    Panels --> ATM
    Panels --> WM
    ATM --> Nav
    ATM --> Media
    ATM --> Empty
    ATM --> UserApp
    ATM --> Camera
    ATM --> AppGrid
    ATM --> Generic
    WM --> Nav
    WM --> Media
    WM --> Empty
    WM --> UserApp
    WM --> Camera
    WM --> AppGrid
    WM --> Generic
```

## Google / 記事の思想に沿った責務分担

| 領域 | 役割 | ScalableUI 標準で扱うか |
| --- | --- | --- |
| Product mk | RRO / StubLauncher を image に入れる | Yes |
| Framework RRO | system bar / inset control などの基礎設定 | Yes |
| CarService RRO | product side configuration | Yes |
| SystemUI RRO | panel / variant / transition / default activity 宣言 | Yes |
| StubCarLauncher | 空の HOME host と PoC AppGrid を提供 | 必要だが ScalableUI そのものではない |
| CarSystemUI | ScalableUI runtime を起動し panel state を管理 | Yes |
| WindowManager / Shell | task container と bounds を管理 | Android platform 側 |
| ActivityTaskManager | 各 app Activity を起動し task lifecycle を管理 | Android platform 側 |
| 各アプリ | Activity として panel に表示される | アプリ側 |
| 任意 panel 追加 / 移動 / picker | runtime model と UI が必要 | Custom 実装 |

## 今回の PoC で確認した完成形

```text
Step 1: Framework / SystemUI / CarService RRO で ScalableUI を有効化
Step 2: RRO XML で spec panel と transition を宣言
Step 3: StubCarLauncher で標準 Launcher UI を退避
Step 4: nav/media/user_slot に独立 Activity task を表示
Step 5: panel_app_grid から user_slot_panel に Calendar を routing
Step 6: page / resize / swap / edit / camera event dispatch を確認
Step 7: Windows host emulator で smoke pass を取得
```

評価済み artifact:

```text
/tmp/aaos-spec-workspace-smoke-20260609-163618
```

## まだ ScalableUI だけでは足りないもの

固定 XML baseline が安定してから、次を段階的に追加します。

1. grip / controller による XML event transition
2. panel bounds preset の追加
3. 任意 app picker
4. panel add / delete / move
5. grip の連続 resize
6. runtime persistence
7. reverse gear / real camera signal 連携

この順番にすると、ScalableUI 標準の orchestration と、PoC 独自の runtime workspace 実装を混ぜずに検証できます。
