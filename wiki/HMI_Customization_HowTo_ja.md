# HMI Customization HowTo

このページは、現行 `declarative-multipanel` baseline を起点に HMI を変更するための手順です。

## 1. まず変更の種類を決める

| 変更したいこと | 主な担当 | まず見る場所 |
| --- | --- | --- |
| 固定 panel の app を変える | RRO/XML | `config_default_activities`, `strings.xml` |
| panel の位置や大きさを変える | RRO/XML | `res/xml/*_panel.xml` |
| All Apps の出方を変える | RRO/XML + Launcher/SystemUI | `panel_app_grid`, AppGrid, routing |
| 通常 app の fullscreen 表示を変える | RRO/XML + SystemUI | `app_panel`, TaskPanel routing |
| Home 復帰や最大化を変える | SystemUI controller / event | `PanelTransitionCoordinator`, `EventDispatcher` |
| runtime panel 追加や app assignment | PoC/custom | controller, store, picker |

## 2. ベースラインを間違えない

現行 baseline:

```text
variants/declarative-multipanel
```

AAOS17 では、次の標準 target を維持します。

```bash
cd <AAOS17_ROOT>
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug
```

古い `dynamic-workspace` や generated variant suite は、設計案や実験記録として参照できます。ただし、現行 PoC や Android17 移植の根拠にする場合は、必ず source / build / runtime で再検証します。

## 3. 現行 PoC を作る順番

Android17 では、PoC 専用 product を新規に増やすのではなく、標準 AAOS17 emulator target に ScalableUI 差分を重ねます。

```text
1. 標準 AAOS17 emulator target を build できる状態にする
   sdk_car_x86_64-trunk_staging-userdebug

2. RRO / XML を追加する
   Framework RRO
   CarService RRO
   CarSystemUI RRO
   window_states / default_activities / panel XML

3. HOME host を差し替える
   ScalableUiStubCarLauncher
   標準 CarLauncher UI を HMI の主役にしない

4. All Apps / app_panel routing を追加する
   panel_app_grid
   app_panel
   fixed panel に属さない app の逃がし先

5. 必要な場合だけ SystemUI event / controller を追加する
   outside tap dismiss
   existing app maximize
   Home restore

6. build と runtime evidence を残す
   module build
   emu_img_zip
   emulator smoke
```

非推奨の作り方:

| 古い作り方 | 現在の扱い |
| --- | --- |
| Android17 に `sdk_car_scalableui_*` の専用 lunch target を追加する | 原則使わない |
| 古い generator で variant を一括生成して baseline にする | 使わない。現行 baseline は手で保守する |
| `dynamic-workspace` / `editable-home` をそのまま現行 PoC として扱う | historical / experimental |
| demo app を多数追加して HMI を作る | active baseline ではない |

## 4. 触る場所

現行 baseline の主な編集対象:

```text
variants/declarative-multipanel/
  README.md
  docs/hmi_spec_ja.md
  patches/
    device-generic-car/
    packages-services-Car/
    packages-apps-Car-SystemUI/
```

Android17 workspace 側の主な対応先:

```text
<AAOS17_ROOT>/
  device/generic/car/sdk_car_x86_64.mk
  packages/services/Car/car_product/scalableui_declarative_multipanel/
  packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/
```

## 5. 小さく変更する順番

1. RRO/XML だけでできる変更から始める。
2. Launcher / AppGrid の導線を変える。
3. SystemUI event / routing を最小限足す。
4. image を作って emulator smoke を取る。
5. docs と patch を同期する。

最初から runtime panel 追加、永続化、reparent、drag resize まで入れると、ScalableUI 標準の問題か PoC custom の問題か切り分けにくくなります。

## 6. panel と app の割り当て

固定 panel の app 割り当ては、主に `config_default_activities` と panel role で決まります。

例:

```xml
<string-array name="config_default_activities" translatable="false">
    <item>map_panel;com.android.car.mapsplaceholder/.MapsPlaceholderActivity</item>
    <item>media_panel;com.android.car.carlauncher/.ControlBarActivity</item>
</string-array>
```

注意:

- Settings など、ユーザーが集中操作したい app は固定 panel ではなく `app_panel` に逃がす設計も検討する。
- 既に panel 内にいる app を再度起動した場合、単純な多重起動ではなく最大化 / focus へつなげる設計が必要になる。

## 7. panel の位置と大きさ

panel XML の `Variant` と `Bounds` を変更します。

見る値:

- `left`
- `top`
- `right`
- `bottom`
- `leftOffset`
- `topOffset`
- `rightOffset`
- `bottomOffset`
- `Layer`
- `Visibility`
- `Corner`

実装モデルは次の通りです。

```text
Panel XML
  -> PanelState / Variant
  -> StateManager
  -> TaskPanel
  -> RootTaskStack / Task
  -> Activity
```

## 8. All Apps / app_panel

`panel_app_grid` は All Apps 用の panel、`app_panel` は固定 panel 以外の通常 app を表示する launch-root 的な panel として扱います。

確認すること:

- All Apps が他 panel より前面に出るか
- All Apps を再タップまたは外側タップで閉じられるか
- All Apps から app 起動後、All Apps 自体が残らないか
- 通常 app が固定 panel を壊さず `app_panel` へ出るか

## 9. controller / task event

XML だけで表現しづらいものは controller / event で扱います。

例:

- All Apps outside tap dismiss
- 既存 app 再選択時の最大化
- Home 復帰時の直前 layout restore
- user / display / focus 条件による分岐
- telemetry の event start / end 計測

Android17 では `PanelTransitionCoordinator` が Window State と Surface animation を分けて扱うため、変更が WM transition を必要とするかを先に分類します。

## 10. Build / validation

推奨:

```bash
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing

SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO

SOONG_NINJA=ninja m -j6 emu_img_zip
```

runtime 変更後は、screenshot、overlay state、package state、`dumpsys activity top`、`dumpsys window displays`、logcat fatal check を残します。

## 11. 迷ったときの参照先

- [AAOS17 Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aaos17_scalableui_source_verification_ja.md)
- [WindowManager Flow](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/architecture/scalableui_window_manager_flow_ja.md)
- [AAOS17 Development Flow](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/android17/aaos17_scalableui_development_flow_ja.md)
- [Variant Status](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/workflows/variant_status_ja.md)
