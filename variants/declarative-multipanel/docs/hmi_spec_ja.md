# declarative-multipanel HMI 仕様

> Source verification: この baseline は AAOS/AOSP source と照合済みです。詳細な claim 判定は [AOSP Source Verification](../../../docs/verification/aosp_source_verification_ja.md) を参照してください。

## 位置づけ

`declarative-multipanel` は、`aaos-scalable-ui-specs` の初期 scope を AAOS15 LTS3 で検証するための baseline です。

目的は、まず ScalableUI の本来の責務である「panel 宣言、variant、transition、task placement」を AAOS 上で成立させ、どこから先が custom runtime 実装になるかを切り分けることです。

実装上の基本モデル:

```text
Panel
  -> TaskPanel
  -> RootTaskStack / Task
  -> Activity
```

`RemoteCarTaskView` / `TaskView` は AAOS に存在しますが、この baseline の ScalableUI `TaskPanel` 表示経路の実体ではありません。

## 採用方針

- AAOS product は `sdk_car_x86_64.mk` を継承する
- Top bar / Bottom bar / HVAC は AAOS as-is を基本にし、この PoC では置き換えない
- ScalableUI 有効化は `CarSystemUI` RRO で行う
- system bar / app 側の insets 制御は Framework RRO で有効化する
- CarService 側には PoC 用の overlay package を追加する
- 標準 `CarLauncher` は `StubCarLauncher` で置き換え、HOME UI と ScalableUI HMI を分離する
- panel 数と geometry は XML で固定宣言する
- runtime の任意追加、自由移動、永続化はこの baseline の対象外にする

AAOS15 LTS3 では、DecorPanel-only transition や target-panel routing を安定させるため、最小限の `CarSystemUI` runtime 修正も含めています。

## HMI 構成

初期 workspace は spec 通り 3 pane です。

```text
1920x1080 display

┌────────────────────────────────────────────────────────────┐
│ AAOS top bar area                                          │
├────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────┐ ┌──────────────────────┐ │
│ │ nav_panel                     │ │ media_panel          │ │
│ │ Navigation / map activity     │ │ Media placeholder    │ │
│ │ default: MapsPlaceholder      │ └──────────────────────┘ │
│ │                               │ ┌──────────────────────┐ │
│ │                               │ │ user_slot_panel      │ │
│ │                               │ │ initially empty      │ │
│ │                               │ │ AppGrid assignment   │ │
│ └───────────────────────────────┘ └──────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│ AAOS bottom bar / HVAC area                                │
└────────────────────────────────────────────────────────────┘
```

Overlay / transition panels:

```text
panel_app_grid
  user_slot_panel に app を割り当てるための AppGrid overlay。

app_panel
  System Bar Apps など、特定 panel assignment ではない generic app launch 用。

camera_priority_panel
  camera override 用 fullscreen high-layer panel。

edit_overlay_panel
  layout edit mode を示す DecorPanel overlay。

empty_slot_hint_panel
  user_slot_panel が空であることを示す hint UI。
```

## AAOS 変更点

```text
device/generic/car
  AndroidProducts.mk
    sdk_car_scalableui_declarative_multipanel_x86_64 を lunch choice に追加

  sdk_car_scalableui_declarative_multipanel_x86_64.mk
    sdk_car_x86_64.mk を継承
    packages/services/Car/car_product/scalableui_declarative_multipanel を追加

packages/services/Car
  car_product/scalableui_declarative_multipanel/
    car_scalableui_declarative_multipanel.mk
      SystemUI RRO、Framework RRO、CarService RRO、StubCarLauncher を PRODUCT_PACKAGES に追加

    rro/CarFrameworkScalableUiDeclarativeMultipanelRRO/
      config_remoteInsetsControllerControlsSystemBars=true

    rro/CarServiceScalableUiDeclarativeMultipanelRRO/
      PoC product overlay

    rro/CarSystemUIScalableUiDeclarativeMultipanelRRO/
      config_enableScalableUI=true
      window_states に panel XML を登録
      config_default_activities で default activity を割り当て

    apps/StubCarLauncher/
      標準 CarLauncher を置き換える HOME / AppGrid / placeholder 実装

packages/apps/Car/SystemUI
  ScalableUI runtime routing fixes
    target panel routing
    DecorPanel-only transition handling
    ScalableUI initializer wiring
```

## ScalableUI 設定

`CarSystemUIScalableUiDeclarativeMultipanelRRO/res/values/config.xml`:

- `config_enableScalableUI=true`
- `config_enableClearBackStack=false`
- `config_enableSafeAreaAndToolbarPerDisplay=false`
- `window_states` に 11 panel XML を登録
- `config_default_activities` で `nav_panel` / `media_panel` / `user_slot_panel` / `camera_priority_panel` / `panel_app_grid` に初期 Activity を割り当て

`CarSystemUIScalableUiDeclarativeMultipanelRRO/res/xml/overlays.xml`:

- `config_enableScalableUI`
- `window_states`
- `config_default_activities`
- `config_appGridComponentName`
- `system_bar_app_drawer_intent`

Framework RRO:

- `config_remoteInsetsControllerControlsSystemBars=true`

## Panel 一覧

AAOS15 LTS3 では panel XML の root tag は `<Panel>` を使います。Passenger6 の Android 16 / Baklava 系 sample では `<TaskPanel>` が使われていますが、この tree の parser では `<TaskPanel>` を読むと SystemUI が起動時に落ちます。

確認した失敗例:

```text
XmlPullParserException: Expected <Panel> tag at the beginning but TaskPanel
NullPointerException ... PanelState.getId()
```

この variant の XML はすべて `<Panel id="...">` で定義します。

```text
top_bar_panel
  type: DecorPanel
  purpose: AAOS top bar area reservation
  visible in PoC: false

bottom_bar_panel
  type: DecorPanel
  purpose: AAOS bottom bar area reservation
  visible in PoC: false

hvac_panel
  type: DecorPanel
  purpose: AAOS HVAC area reservation
  visible in PoC: false

nav_panel
  type: TaskPanel
  role: com.android.car.mapsplaceholder/.MapsPlaceholderActivity
  workspace_default: 2%,5% - 58%,95%
  page_2: 2%,5% - 48%,95%
  wide: 2%,5% - 68%,95%

media_panel
  type: TaskPanel
  role: com.android.car.carlauncher/.ControlBarActivity
  workspace_default: 60%,5% - 98%,47%
  page_2: 50%,5% - 98%,47%
  narrow: 70%,5% - 98%,47%

user_slot_panel
  type: TaskPanel
  role: com.android.car.carlauncher/.EmptySlotActivity
  empty: 60%,53% - 98%,95%
  page_2: 50%,53% - 98%,95%
  narrow: 70%,53% - 98%,95%

empty_slot_hint_panel
  type: DecorPanel
  role: @layout/scalableui_empty_slot_hint
  visible: 68%,76% - 90%,88%

camera_priority_panel
  type: TaskPanel
  role: com.android.car.carlauncher/.CameraStubActivity
  camera_fullscreen: 0%,0% - 100%,100%

edit_overlay_panel
  type: DecorPanel
  role: @layout/scalableui_edit_overlay
  editing: 22%,24% - 78%,76%

panel_app_grid
  type: TaskPanel
  role: com.android.car.carlauncher/.AppGridActivity
  opened: 8%,18% - 92%,92%

app_panel
  type: TaskPanel
  role: DEFAULT
  opened: 2%,5% - 98%,95%
```

## Transition

この baseline は spec の汎用 event 名を一部 AAOS15 LTS3 で扱いやすい具体 event に展開しています。

```text
_System_TaskOpenEvent panelId=panel_app_grid
  panel_app_grid -> opened

_System_TaskOpenEvent panelId=user_slot_panel
  panel_app_grid -> closed
  app_panel -> closed
  empty_slot_hint_panel -> hidden

_System_TaskOpenEvent panelId=app_panel
  app_panel -> opened
  nav_panel -> hidden
  media_panel -> hidden
  user_slot_panel -> hidden
  panel_app_grid -> closed

switch_workspace_page_1
  nav_panel / media_panel / user_slot_panel -> workspace_default / empty

switch_workspace_page_2
  nav_panel / media_panel / user_slot_panel -> page_2

resize_panel_nav_wide
  nav_panel -> wide
  media_panel / user_slot_panel -> narrow

resize_panel_balanced
  nav_panel / media_panel / user_slot_panel -> workspace_default / empty

swap_panel_position_nav_media
  nav_panel -> swapped
  media_panel -> swapped

enter_layout_edit
  edit_overlay_panel -> editing

exit_layout_edit
  edit_overlay_panel -> hidden

enter_camera_override
  camera_priority_panel -> camera_fullscreen
  panel_app_grid / app_panel / edit_overlay_panel / empty_slot_hint_panel -> hidden or closed

exit_camera_override
  camera_priority_panel -> hidden

_System_OnHomeEvent
  workspace panels -> workspace_default / empty
  overlays -> hidden or closed
```

`camera_override` では workspace panel 自体を hidden にしません。workspace panel を hidden にすると empty panel event が発火し、Home event によって復帰後 workspace が黒く見えるためです。PoC では camera を fullscreen high-layer として workspace の上に被せます。

## Launcher との関係

標準 `CarLauncher` をそのまま使うと、Home UI / AppGrid / fragment が表示主体になり、ScalableUI HMI と干渉します。そのため、この baseline では同じ package name の `StubCarLauncher` を system_ext priv-app として入れ、標準 Launcher を置き換えます。

```text
com.android.car.carlauncher/.CarLauncher
  transparent HOME host
  taskAffinity=com.android.car.carlauncher.home

com.android.car.carlauncher/.ControlBarActivity
  media panel placeholder
  taskAffinity=com.android.car.carlauncher.controlbar

com.android.car.carlauncher/.EmptySlotActivity
  user slot placeholder
  taskAffinity=com.android.car.carlauncher.emptyslot

com.android.car.carlauncher/.CameraStubActivity
  camera override placeholder
  taskAffinity=com.android.car.carlauncher.camera

com.android.car.carlauncher/.AppGridActivity
  lightweight AppGrid
  taskAffinity=com.android.car.carlauncher.appgrid
```

この関係により、Launcher は HMI の表示主体ではなくなります。表示主体は `CarSystemUI` の ScalableUI runtime と WindowManager / ActivityTaskManager であり、各アプリは panel bounds に配置された独立 Activity task として表示されます。

Launcher の責務:

- HOME host として空背景を提供する
- `AppGridActivity` から target panel ID 付きで app launch する
- placeholder Activity を提供する

Panel 管理の主体:

- `CarSystemUI` の ScalableUI runtime
- `PanelConfigReader` / `StateManager` / `PanelTransitionCoordinator`
- WindowManager Shell / ActivityTaskManager の task placement

## ScalableUI だけで実現している範囲

- panel の宣言
- panel の bounds / layer / visibility / alpha / corner
- panel の default activity 割り当て
- event token による variant transition
- task を panel bounds の multi-window task として載せること
- AppGrid overlay panel の表示
- user slot への target panel routing
- generic app launch 用 `app_panel`
- camera / layout edit の overlay 的 transition

注記: AOSP には `WindowContainerTransaction.reparent(...)` が存在しますが、この baseline では任意の既存 task を Panel A から Panel B へ移す機能は対象外です。runtime panel 追加 / delete / move / persistence は custom 実装範囲です。

## custom 実装が必要な範囲

- 標準 `CarLauncher` を HMI と干渉しない Stub に置き換えること
- AppGrid から target panel ID を付けて Activity を起動すること
- AAOS15 LTS3 で DecorPanel-only transition を安定させること
- target panel routing の明確化
- ユーザー操作による panel 追加 / 削除
- drag による panel 移動
- grip による連続 resize
- ユーザーが任意 app を任意 panel に割り当てる UI
- runtime model / persistence
- reverse gear / real camera signal 連携
- resource throttling policy

## 評価済み範囲

2026-06-09 v12 smoke で以下を Windows host emulator 上で確認済みです。

- `StubCarLauncher` が system_ext に入り、標準 Launcher と置き換わる
- SystemUI / Framework / CarService overlay が有効
- `nav_panel` / `media_panel` / `user_slot_panel` が表示される
- user slot の empty hint が見える
- AppGrid から Calendar を選ぶと `user_slot_panel` bounds に routing される
- `switch_workspace_page_2` で panel bounds が変わる
- `resize_panel_nav_wide` で nav/media/user_slot の bounds が変わる
- `swap_panel_position_nav_media` で nav と media の位置が入れ替わる
- `enter_layout_edit` で `edit_overlay_panel` が表示される
- `enter_camera_override` で `camera_priority_panel` が fullscreen 表示される
- `exit_camera_override` で camera fullscreen が消え、workspace が復帰する
- System Bar Apps から fullscreen AppGrid が開く
- SystemUI / StubCarLauncher process が維持される
- recent logcat tail に `FATAL EXCEPTION` がない
