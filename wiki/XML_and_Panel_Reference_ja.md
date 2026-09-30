# XML and Panel Reference

このページは、ScalableUI の XML / RRO を読むためのクイックリファレンスです。

基準: 2026-10-01の [AAOS17 Source Snapshot](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aaos17_source_snapshot_2026-10-01_ja.md) と、2026年9月更新の公式panel / variant / transition reference。

## 1. Source上の実装モデル

Android17 source 確認済みのモデル:

```text
Panel definition
  -> PanelConfigReader
  -> StateManager.reloadPanelState(...)
  -> TaskPanel / DecorPanel / SysUIPanel
  -> RootTaskStack / Surface / Window State
```

`TaskPanel` は `TaskView` / `RemoteCarTaskView` ではありません。`RootTaskStack` based implementation です。

## 2. 主な file

RRO 側:

```text
res/values/config.xml
res/values/strings.xml
res/values/integers.xml
res/values/dimens.xml
res/xml/*.xml
res/layout/*.xml
```

SystemUI 側:

```text
packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/
```

Android17 で特に見る class:

- `PanelConfigReader`
- `StateManager`
- `PanelTransitionCoordinator`
- `PanelAutoTaskStackTransitionHandlerDelegate`
- `EventDispatcher`
- `TaskPanel`
- `SysUIPanel`

## 3. `window_states`

ScalableUI が読む panel 定義の一覧です。

```xml
<array name="window_states">
    <item>@xml/map_panel</item>
    <item>@xml/media_panel</item>
    <item>@xml/panel_app_grid</item>
</array>
```

Android17 の `PanelConfigReader.loadFromXml()` は、この配列を読み、`XmlModelLoader.createPanelState(...)` で `PanelState` を生成します。

製品側では`config_enableScalableUI=true`だけでなく、公式implement資料が要求する`android.software.car.splitscreen_multitasking` featureと、競合するlegacy windowing / split-screen機能が無効であることも確認します。

## 4. `config_default_activities`

固定 panel と初期 Activity の紐付けです。

```xml
<string-array name="config_default_activities" translatable="false">
    <item>map_panel;com.android.car.mapsplaceholder/.MapsPlaceholderActivity</item>
</string-array>
```

これは Activity を panel に直接貼るという意味ではありません。実装上は TaskPanel / task を介して表示されます。

## 5. Panel XML

代表的な属性:

```xml
<TaskPanel
    id="map_panel"
    defaultVariant="@id/opened"
    role="@string/map_componentName"
    displayId="0">
    ...
</TaskPanel>
```

AAOS branch によって XML root tag の期待値が異なる場合があります。AAOS15 LTS3 では `<Panel>` root が必要だった評価記録があります。Android17 作業では対象 source の parser に合わせて確認してください。

## 6. Variant

`Variant` は panel の状態です。

主な要素:

- `Bounds`
- `Layer`
- `Visibility`
- `Alpha`
- `Corner`
- `Insets`
- focus policy
- `SafeBounds`
- `Background`

例:

```xml
<Variant id="@+id/opened">
    <Layer layer="@integer/app_panel_layer"/>
    <Visibility isVisible="true"/>
    <Bounds left="0" top="0" right="100%" bottom="100%"/>
</Variant>
```

連続drag / resizeでは`KeyFrameVariant`を使い、0..100の`framePosition`にvariantを割り当てて、0..1のfractionからvisual propertyを補間できます。これはScalableUI標準部品ですが、pointer入力、Map gestureとの競合、reorder policy、永続化は別設計です。

## 7. TaskBehavior

`TaskPanel`では新規task launch policyを定義できます。

```xml
<TaskBehavior newTaskLaunchPolicy="REPARENT_TO_SOURCE"/>
```

公式に記載される値は`DEFAULT`、`REMAIN_IN_SOURCE`、`REPARENT_TO_SOURCE`です。これは新規taskのlaunch root behaviorであり、任意の既存taskをユーザー操作でPanel間移動する汎用editorではありません。

## 8. Transition

event から variant へ遷移する定義です。

```xml
<Transition
    fromVariant="@id/closed"
    onEvent="show_app_grid"
    toVariant="@id/opened"/>
```

よく扱う event:

- `_System_TaskOpenEvent`
- `_System_TaskCloseEvent`
- `_System_OnHomeEvent`
- `show_app_grid`
- `close_app_grid`
- `maximize_panel`
- `restore_home`

event 名や token schema は PoC / project custom になる場合があります。本格適用では送信元制限、permission、spoofing 対策も必要です。

## 9. Layer

重なり順です。

考え方:

```text
background < fixed panels < decor / controls < app_panel < panel_app_grid < priority overlay
```

All Apps を常に前面にしたい場合は、XML の layer だけでなく、Window State、input、focus、outside tap、system bar / HUN との重なりも確認します。

## 10. Window State と Surface

Android17 の ScalableUI README では次の区別が明確です。

| 種別 | 例 | 主な扱い |
| --- | --- | --- |
| Window State | visibility, bounds, position, Z-order, app launch / close / resize | WM transition |
| Surface | alpha, scale, translation, crop | direct Surface animation |

panel 最大化や task routing は Window State 寄りです。scrim fade や見た目だけの dismiss animation は Surface 寄りにできる可能性があります。

## 11. `panel_app_grid` と `app_panel`

`panel_app_grid`:

- All Apps 用 panel
- 中央 floating 表示や fullscreen-ish overlay の候補
- 再タップ / outside tap dismiss を設計する

`app_panel`:

- 固定 panel 以外の通常 app の表示先
- Settings など集中操作したい app の逃がし先
- Home 復帰時に直前 layout を戻す対象

## 12. Runtime panel generation

Android17 source には `StateManager.addState(...)` と `reloadPanelState(...)` が存在します。

ただし、任意panelの追加UI、geometry、並べ替えpolicy、永続化、app pickerはScalableUI標準だけでは完結しません。drag previewは`KeyFrameVariant`やSurface transactionを使えますが、end-to-end editorはPoC/customとして扱います。

## 13. 参照

- [AAOS17 Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aaos17_scalableui_source_verification_ja.md)
- [AOSP Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aosp_source_verification_ja.md)
- [WindowManager Flow](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/architecture/scalableui_window_manager_flow_ja.md)
