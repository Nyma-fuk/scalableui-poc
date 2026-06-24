# AAOS17 Codelab Three Panel 1080

AAOS17 `android-17.0.0_r1` の ScalableUI codelab ThreePanel RRO を、1920x1080 landscape emulator で実際に動くように調整した検証用 variant。

この variant は現行 PoC baseline ではなく、AAOS17 ScalableUI の As-Is 機能を UI として確認するための独立サンプルである。

## できること

| 操作 | 期待するUI | 検証結果 |
| --- | --- | --- |
| Home 表示 | `map_panel` が content area 全体に表示される | OK |
| All Apps 起動 | system bar の app grid button から `com.android.car.carlauncher/.AppGridActivity` が `app_panel` に開く | OK |
| KitchenSink 起動 | `map_panel` が左半分へ縮み、overlay なしで `kitchen_sink_panel` が右半分に表示される | OK |
| PaintBooth 起動 | `map_panel` が左半分、`paintbooth_panel` が右下に表示される | OK |
| grip tap | `paintbooth_panel` が右上へ移動し、`map_panel` が左下へ縮む | OK |
| top grip tap | `paintbooth_panel` が右下へ戻り、`map_panel` が左半分へ戻る | OK |
| Home 復帰 | app panel が閉じ、`map_panel` が content area 全体へ戻る | OK |
| `adb input swipe` による drag | DecorPanel の touch path で `_User_DragEvent_split` を発火する | 今回の入力方式では未成立 |

## 画面構成

```text
Home
+-------------------------------+
| top system bar                 |
+-------------------------------+
|                               |
| map_panel                     |
|                               |
+-------------------------------+
| bottom system bar              |
+-------------------------------+

KitchenSink
+---------------+---------------+
| map_panel     | kitchen_sink   |
|               | _panel         |
+---------------+---------------+

PaintBooth bottom
+---------------+---------------+
| map_panel     |               |
|               +---------------+
|               | paintbooth    |
|               | _panel        |
+---------------+---------------+

PaintBooth top after grip tap
+---------------+---------------+
|               | paintbooth    |
|               | _panel        |
+ map_panel ----+---------------+
| lower         |               |
+---------------+---------------+
```

## 主な調整点

- RRO package: `com.android.systemui.rro.scalableUI.threePanel1080.codelab`
- RRO module: `ThreePanel1080RRO`
- All Apps intent: `com.android.car.carlauncher/.AppGridActivity`
- `screen_height`: `1080px`
- content top: `67px`
- content bottom: `940px`
- split x: `960px`
- split y: `520px`
- offscreen closed bounds: right side outside `1920px`
- `window_states` に `decor_grip_bar_switch_task` を追加

## 実装ファイル

| ファイル | 内容 |
| --- | --- |
| `rro/ThreePanel1080RRO/res/values/config.xml` | default activity と panel XML の読み込み |
| `rro/ThreePanel1080RRO/res/values/dimens.xml` | 1920x1080 landscape 用の panel 座標 |
| `rro/ThreePanel1080RRO/res/xml/map_panel.xml` | home / split / lower の map panel 状態 |
| `rro/ThreePanel1080RRO/res/xml/kitchen_sink_panel.xml` | KitchenSink 用右半分 panel |
| `rro/ThreePanel1080RRO/res/xml/paintbooth_panel.xml` | PaintBooth 用右下 / 右上 panel |
| `rro/ThreePanel1080RRO/res/xml/decor_grip_bar_switch_task.xml` | split grip tap による PaintBooth の上下切り替え |

## ビルドと適用

標準 AAOS17 source tree の `aapt2` / platform key を使って RRO APK を作成し、install / overlay enable する。

```bash
AAOS_ROOT=<aaos-root> \
ADB_SERIAL=emulator-5564 \
scripts/install_aaos17_threepanel_1080_rro.sh
```

前提:

- `AAOS_ROOT` が AAOS17 source tree を指していること
- 対象 emulator に `android.software.car.splitscreen_multitasking` feature が存在すること
- `com.android.car.portraitlauncher`
- `com.android.car.carlauncher`
- `com.android.car.ui.paintbooth`
- `com.google.android.car.kitchensink`

`android.software.car.splitscreen_multitasking` は `ScalableUIUtils.isScalableUIEnabled()` の有効化条件である。この feature が無い image では、RRO が enabled でも `map_panel` などの panel root task は生成されない。検証用 script は `-writable-system` で起動した emulator に対しては、この feature XML を `/product/etc/permissions` に投入してから RRO を適用する。

## 検証済みの根拠

検証時は screenshot、`dumpsys activity activities`、`dumpsys window`、`logcat` を保存した。

| 項目 | 確認内容 |
| --- | --- |
| overlay | `com.android.systemui.rro.scalableUI.threePanel1080.codelab` が user 0 / user 10 で enabled |
| feature | `android.software.car.splitscreen_multitasking` が存在し、ScalableUI initializer が起動可能 |
| window states | `app_panel`, `map_panel`, `kitchen_sink_panel`, `paintbooth_panel`, `decor_split_nav_overlay`, `decor_grip_bar_switch_task` が読み込まれる |
| Home | `_System_OnHomeEvent` で `map_panel` が `Rect(0, 67 - 1920, 940)` |
| All Apps | system bar tap で `com.android.car.carlauncher/.AppGridActivity` が `app_panel` の `Rect(960, 67 - 1920, 940)` に開く |
| KitchenSink | `_System_TaskOpenEvent panelId=kitchen_sink_panel` で `map_panel` が左半分 `Rect(0, 67 - 960, 940)`、KitchenSink が右半分 `Rect(960, 67 - 1920, 940)`。Map overlay は閉じる |
| PaintBooth | `_System_TaskOpenEvent panelId=paintbooth_panel` で右下 `Rect(960, 520 - 1920, 940)` |
| grip top | `_Drag_TaskSwitchEvent_top` で PaintBooth が右上 `Rect(960, 67 - 1920, 520)` |
| grip bottom | `_Drag_TaskSwitchEvent_bottom` で PaintBooth が右下 `Rect(960, 520 - 1920, 940)` |
| Home return | `_System_OnHomeEvent` で app panels が offscreen、`map_panel` が full content に復帰 |
| process stability | final validation log に fatal crash / safe bounds error なし |

AAOS の initial user notice が前面に出る場合、検証 script は `Dismiss for now` を検出して閉じる。これは ScalableUI の panel 制御ではなく、AAOS 側の notice window が grip の touch event を吸うことを避けるためである。

## All Apps

元の codelab RRO は `system_bar_app_drawer_intent` を `com.android.car.portraitlauncher` package 固定にしていた。1920x1080 の標準 AAOS17 emulator では標準の `com.android.car.carlauncher/.AppGridActivity` を使う方が素直なので、この variant では component 指定に変更している。

`AppGridActivity` は通常の app task として `app_panel` に routing される想定である。

## 既知の未成立項目

`adb shell input swipe` では `GripBarViewController.onTouch()` の drag path に到達しなかった。`GripBarViewController.onClick()` の breakpoint event は検証済みで、tap による panel の上下切り替えと animation は動作した。

このため、この variant で確認済みと言えるのは「ScalableUI XML transition と DecorPanel controller による discrete な panel 切り替え」であり、「連続drag操作の実機相当入力」は追加検証対象である。
