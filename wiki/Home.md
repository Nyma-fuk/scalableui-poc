# ScalableUI PoC Wiki

この wiki は、ScalableUI AAOS HMI PoC を理解し、現行 baseline を壊さずにカスタマイズするための入口です。

現在の読み方:

- ScalableUI そのものの正は AAOS/AOSP source code です。
- 現行 PoC baseline は `variants/declarative-multipanel` です。
- Android17 では PoC 専用 product を増やさず、標準 `sdk_car_x86_64-trunk_staging-userdebug` に PoC 差分を重ねます。
- `dynamic-workspace`、`editable-home`、`widget-workspace`、generated variant suite は historical / experimental として残します。

## まず読むもの

1. [Repository README](https://github.com/Nyma-fuk/scalableui-poc/blob/main/README.md)
2. [Docs Index](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/README_ja.md)
3. [AAOS17 ScalableUI Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/aaos17_scalableui_source_verification_ja.md)
4. [AAOS ScalableUI / WindowManager 表示フロー](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/scalableui_window_manager_flow_ja.md)
5. [declarative-multipanel README](https://github.com/Nyma-fuk/scalableui-poc/blob/main/variants/declarative-multipanel/README.md)

## Wiki Pages

| Page | 目的 |
| --- | --- |
| [HMI Customization HowTo](HMI_Customization_HowTo_ja.md) | 現行 PoC をどう触るか |
| [XML and Panel Reference](XML_and_Panel_Reference_ja.md) | XML / RRO / Panel の見方 |
| [Customization Recipes](Customization_Recipes_ja.md) | 具体的な変更例 |
| [HMI Pattern Ideas](HMI_Pattern_Ideas_ja.md) | 将来試せる HMI パターン案 |

## 現行 PoC の最短理解

```text
AAOS17:
  sdk_car_x86_64-trunk_staging-userdebug
    + ScalableUI RRO/XML
    + ScalableUiStubCarLauncher
    + 必要最小限の CarSystemUI 差分

実装モデル:
  Panel
    -> TaskPanel
    -> RootTaskStack / Task
    -> Activity
```

`TaskView` / `RemoteCarTaskView` は AAOS に存在しますが、ScalableUI `TaskPanel` の実体ではありません。

## 現行の PoC 作成方法

現在の作成方法は、過去の「variant generator で多数の demo app / 専用 product を生成する」方式ではありません。

現行方針:

1. 標準 AAOS17 emulator target を選ぶ。
2. `variants/declarative-multipanel/patches` を移植元として使う。
3. `device/generic/car/sdk_car_x86_64.mk` に PoC package set を追加する。
4. `packages/services/Car/car_product/scalableui_declarative_multipanel/` に RRO / Stub HOME host を置く。
5. `packages/apps/Car/SystemUI` には task routing / event / controller の最小差分だけを入れる。
6. module build、`emu_img_zip`、emulator smoke evidence で確認する。

```text
<AAOS17_ROOT>
  device/generic/car/sdk_car_x86_64.mk
    -> car_scalableui_declarative_multipanel.mk を inherit

  packages/services/Car/car_product/scalableui_declarative_multipanel/
    -> Framework / CarService / CarSystemUI RRO
    -> ScalableUiStubCarLauncher

  packages/apps/Car/SystemUI/
    -> 必要最小限の ScalableUI routing / event 差分
```

古い作成方法:

| 方式 | 現在の扱い |
| --- | --- |
| PoC 専用 lunch product を Android17 に追加する | 原則使わない。Soong graph が重くなり切り分けが難しいため |
| `dynamic-workspace` を現行 baseline として使う | historical / experimental |
| generated variant suite をそのまま本格適用候補にする | generated idea。再利用時は source / build / runtime で再検証 |
| demo app を多数追加する all-in-one PoC | active baseline ではない |

## PoC の分類

| 区分 | 対象 | 扱い |
| --- | --- | --- |
| Active baseline | `variants/declarative-multipanel` | 現行 PoC として保守 |
| Android17 porting | `docs/aaos17_*`, `scripts/aaos17_*` | 標準 target への差分適用方針を正とする |
| Historical / experimental | `dynamic-workspace`, `editable-home`, `widget-workspace`, `widget-layout-lab`, `no-grip` | 正しい実験記録として残す |
| Generated idea | `fixed-3zone`, `map-first`, `media-dock` など | 再利用する場合は source / build / runtime で再検証 |

詳細は [Variant Status](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/variant_status_ja.md) を参照してください。

## 変更時のルール

- ScalableUI 標準機能と PoC custom 実装を混ぜて説明しない。
- 「Panel に Activity を直接貼る」と説明しない。
- runtime panel 追加、任意 app assignment、persistence、drag resize は custom 領域として扱う。
- Android17 作業では専用 product を増やさず、標準 `sdk_car_x86_64` に差分を載せる。
- runtime 挙動に影響する変更は build だけで完了にせず、emulator smoke evidence を残す。
