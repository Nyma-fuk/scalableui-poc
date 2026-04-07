# XML and Panel Reference

## 1. HMI を構成する主な file

役割ごとの file:
- `res/values/config.xml`
  - panel 一覧と default activity の割り当て
- `res/values/strings.xml`
  - component 名や role 名
- `res/values/integers.xml`
  - layer 定義
- `res/values/dimens.xml`
  - margin, gap, grip size
- `res/xml/*.xml`
  - panel 本体
- `res/layout/*.xml`
  - decor panel の view
- `res/xml/*controller*.xml`
  - grip など controller 定義

## 2. `config.xml`

最重要項目:
- `window_states`
- `config_default_activities`
- `config_untrimmable_activities`

### `window_states`

ScalableUI が生成する panel の一覧です。

例:
```xml
<array name="window_states">
    <item>@xml/map_panel</item>
    <item>@xml/calendar_panel</item>
</array>
```

ここに入っていない panel は表示構成に参加しません。

### `config_default_activities`

固定 panel と app の結び付けです。

例:
```xml
<item>radio_panel;com.android.car.radio/.RadioActivity</item>
```

## 3. `Panel` XML の見方

基本形:
```xml
<Panel id="calendar_panel" defaultVariant="@id/w50_h50" role="@string/calendar_componentName" displayId="0">
    ...
</Panel>
```

重要属性:
- `id`
  - panel 識別子
- `defaultVariant`
  - 起動時の見た目
- `role`
  - component や layout、または `DEFAULT`
- `displayId`
  - 通常は `0`
- `controller`
  - grip などの controller をぶら下げる場合に使う

## 4. `Variant`

`Variant` は panel の 1 つの状態です。

変えられるもの:
- visible / invisible
- size
- position
- layer
- corner

例:
```xml
<Variant id="@+id/w50_h50">
    <Layer layer="@integer/calendar_panel_layer"/>
    <Visibility isVisible="true"/>
    <Bounds left="50%" leftOffset="12dp" top="0" right="100%" bottom="50%" bottomOffset="12dp"/>
</Variant>
```

## 5. `Bounds`

`Bounds` は panel の表示領域です。

使う値:
- 百分率
- `dp`
- 組み合わせ

よく使うパターン:
- 左右 2 分割
  - `left="0"` `right="50%"`
- 右上
  - `left="50%"` `top="0"` `bottom="50%"`
- 右下
  - `left="50%"` `top="50%"` `bottom="100%"`
- fullscreen
  - `left="0"` `top="0"` `right="100%"` `bottom="100%"`

## 6. `Layer`

panel の重なり順です。

考え方:
- background < fixed panel < grip < fullscreen overlay

例:
- left background: `5`
- fixed panel: `10` or `20`
- grip: `40`
- app panel: `180`
- app grid: `200`

## 7. `Visibility`

表示 / 非表示です。

例:
```xml
<Visibility isVisible="false"/>
```

overlay を閉じるときによく使います。

## 8. `Corner`

panel の角丸です。

例:
```xml
<Corner radius="24dp"/>
```

map panel のようにフロート感を出したい時に使いやすいです。

## 9. `KeyFrameVariant`

drag の途中状態を作るときに使います。

例:
```xml
<KeyFrameVariant id="@+id/width_drag">
    <KeyFrame frame="0" variant="@id/left_40"/>
    <KeyFrame frame="50" variant="@id/left_50"/>
    <KeyFrame frame="100" variant="@id/left_60"/>
</KeyFrameVariant>
```

固定 layout だけなら不要です。

## 10. `Transitions`

event でどの variant に遷移するかを定義します。

例:
```xml
<Transition fromVariant="@id/left_50" onEvent="layout_width_left_wide" toVariant="@id/left_60"/>
```

イベント名の例:
- `layout_width_drag`
- `layout_width_balanced`
- `layout_height_balanced`
- `_System_TaskOpenEvent`
- `_System_TaskCloseEvent`
- `_System_OnHomeEvent`

## 11. `panel_app_grid` と `app_panel`

### `panel_app_grid`

役割:
- `All apps` の fullscreen overlay

見どころ:
- 開くイベント
- 閉じるイベント
- `app_panel` が開いたときに閉じる定義

### `app_panel`

役割:
- 固定 panel 以外の app の fullscreen 起動先

見どころ:
- `role="DEFAULT"`
- launch root panel としての扱い
- 他 panel が開いたときの close

## 12. Grip controller

grip を使う場合に必要です。

主な file:
- `vertical_grip_controller.xml`
- `horizontal_grip_controller.xml`
- `decor_vertical_grip_panel.xml`
- `decor_horizontal_grip_panel.xml`

controller で決めるもの:
- 使用する controller class
- view class
- drag event 名
- orientation
- breakpoints

## 13. `SystemUI` / `Launcher` 側の共通ロジック

panel XML だけでは決まらない部分があります。

### `PanelAutoTaskStackTransitionHandlerDelegate.java`

役割:
- activity がどの panel に routing されるかを決める

今の repo での重要点:
- 既知 panel が handle できなければ `app_panel`
- `All apps` 起動時の extra を見て `app_panel` を優先

### `AppLaunchProvider.kt`

役割:
- `All apps` から app を launch するときの intent を作る

今の repo での重要点:
- `com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL=true`

### `AppItemViewHolder.java`

役割:
- `All apps` 上の icon tap 後の UI 挙動

今の repo での重要点:
- 起動後に `AppGridActivity` を閉じる

## 14. よく変える値の一覧

変更しやすいポイント:
- 固定 panel の app
- panel の位置
- split の割合
- gap の大きさ
- overlay の開閉条件
- layer の優先順位
- grip の有無
- product 名
- variant 名

まずは `config.xml` と対象 panel XML だけで変えられる範囲から始めるのが安全です。
