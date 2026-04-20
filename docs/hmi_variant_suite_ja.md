# ScalableUI HMI Variant Suite

この文書は、ScalableUI で検討した HMI 案を AAOS15 checkout に適用し、ビルド時の product / lunch target で切り替えるための手順です。

## 目的

この variant suite は、次を満たすための構成です。

- HMI 案ごとに独立した product 名を持つ
- HMI 案ごとに独立した RRO patch を持つ
- HMI 案で必要になる placeholder / demo app を共通 patch として持つ
- `lunch` の product 選択で HMI を切り替えられる
- 他人の checkout を壊さないように、patch が clean apply できない場合は止まる

## 構成

主要ディレクトリ:

- `common/patches/device-generic-car/`
  - すべての HMI product を `AndroidProducts.mk` に追加する suite 用 patch
- `common/patches/packages-services-Car/`
  - HMI 用共通 demo app `ScalableUiHmiDemoApps` を追加する patch
- `variants/<variant>/patches/device-generic-car/`
  - 1 variant だけを clean checkout に追加する product patch
- `variants/<variant>/patches/packages-services-Car/`
  - その variant 専用 RRO / product layer patch
- `variants/<variant>/README.md`
  - variant の概要、product 名、適用方法
- `variants/<variant>/docs/hmi_spec_ja.md`
  - panel 構成、bounds、component、検証項目
- `scripts/apply_hmi_suite.sh`
  - すべての HMI 案をまとめて適用する script
- `scripts/apply_hmi_variant.sh`
  - 指定した HMI 案だけを適用する script
- `scripts/generate_hmi_variants.py`
  - variant docs / patch を再生成するための generator

## HMI 一覧

| Variant | Product | 用途 |
| --- | --- | --- |
| `fixed-3zone` | `sdk_car_scalableui_fixed_3zone_x86_64` | map / calendar / radio の固定 3 領域 |
| `map-first` | `sdk_car_scalableui_map_first_x86_64` | map を主役にした navigation first |
| `media-dock` | `sdk_car_scalableui_media_dock_x86_64` | media / radio 操作を広く見せる bottom dock |
| `productivity-dashboard` | `sdk_car_scalableui_productivity_dashboard_x86_64` | calendar / task / phone / map の assistant dashboard |
| `app-with-rail` | `sdk_car_scalableui_app_with_rail_x86_64` | fullscreen app と persistent side rail の共存 |
| `floating-card` | `sdk_car_scalableui_floating_card_x86_64` | map 背景 + floating card |
| `app-grid-hub` | `sdk_car_scalableui_app_grid_hub_x86_64` | All apps を中心にした launcher hub |
| `calm-mode` | `sdk_car_scalableui_calm_mode_x86_64` | 情報量を減らした minimal / calm 表示 |
| `parking-mode` | `sdk_car_scalableui_parking_mode_x86_64` | parking / charging 向け dashboard |
| `developer-cockpit` | `sdk_car_scalableui_developer_cockpit_x86_64` | debug / validation 用 cockpit |
| `dual-display` | `sdk_car_scalableui_dual_display_x86_64` | driver / passenger display 分離の検討 |
| `showcase-modes` | `sdk_car_scalableui_showcase_modes_x86_64` | normal / calm / app focus の比較 showcase |

## すべての HMI を適用する

clean な AAOS15 checkout で、repo root から実行します。

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_suite.sh
```

この script は次を適用します。

- suite 用 device product patch
- 共通 demo app patch
- 12 個すべての variant RRO patch
- 既存 PoC と同じ SystemUI routing patch
- 既存 PoC と同じ Launcher All apps patch

適用後、ビルドしたい HMI を `lunch` で選びます。

```bash
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
m
```

別の HMI を試したい場合は、同じ checkout で `lunch` を変えます。

```bash
lunch sdk_car_scalableui_media_dock_x86_64-trunk_staging-userdebug
m
```

## 1 つの HMI だけ適用する

checkout を小さく保ちたい場合は、1 variant だけを適用できます。

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh map-first
lunch sdk_car_scalableui_map_first_x86_64-trunk_staging-userdebug
m
```

variant ディレクトリ側の wrapper も同じことをします。

```bash
bash workdir/scalableui-poc/variants/map-first/scripts/apply_patches.sh
```

注意:

- `apply_hmi_variant.sh` は clean checkout で 1 variant だけ入れる用途です
- 複数 variant を同じ checkout に入れたい場合は `apply_hmi_suite.sh` を使ってください
- 既に root の `grip` / `no-grip` patch を入れた checkout では、device product patch が clean apply できず止まる場合があります

## patch 適用時の安全性

apply script は次の方針です。

- patch が既に適用済みなら skip する
- patch 対象ファイルに local modification があれば止まる
- `git apply --check` に失敗した場合は何も適用せず止まる
- `git reset --hard` や `git checkout --` のような destructive operation は行わない

つまり、想定と違う checkout に無理やり patch を当てることはありません。

## 共通 demo app

標準 AAOS に存在しない task / status / energy / debug / controls などの領域には、共通の placeholder app を使います。

module:

- `ScalableUiHmiDemoApps`

package:

- `com.android.car.scalableui.hmi.demo`

主な Activity alias:

- `.TaskPanelActivity`
- `.PhonePanelActivity`
- `.MediaPanelActivity`
- `.StatusPanelActivity`
- `.ControlsPanelActivity`
- `.ShortcutsPanelActivity`
- `.EnergyPanelActivity`
- `.SettingsPanelActivity`
- `.DebugPanelActivity`
- `.PassengerPanelActivity`
- `.CalmPanelActivity`

この app は HMI variant の panel 領域を検証するための軽量 placeholder です。
量産向け UI ではなく、panel bounds / routing / layout を試すためのものです。

## RRO の見方

各 variant の RRO patch は、`packages/services/Car` に次の形で展開されます。

```text
car_product/scalableui_hmi_<variant>/
  car_scalableui_hmi_<variant>.mk
  rro/
    rro.mk
    CarSystemUIScalableUiHmi...RRO/
      Android.bp
      AndroidManifest.xml
      res/values/config.xml
      res/values/strings.xml
      res/values/integers.xml
      res/xml/*.xml
```

主に見る場所:

- `res/values/config.xml`
  - `window_states`
  - `config_default_activities`
- `res/xml/<panel>.xml`
  - `Panel`
  - `Variant`
  - `Bounds`
  - `Layer`
  - `Visibility`
  - `Corner`
- `res/xml/app_panel.xml`
  - generic app の fullscreen / workspace fallback
- `res/xml/panel_app_grid.xml`
  - All apps overlay

## variant を更新する

variant 定義は `scripts/generate_hmi_variants.py` に集約しています。

更新手順:

1. `VARIANTS` の対象 variant を編集する
2. generator を実行する

```bash
python3 workdir/scalableui-poc/scripts/generate_hmi_variants.py
```

3. 生成された patch / docs を確認する

```bash
git -C workdir/scalableui-poc diff --stat
```

4. patch apply check を行う

```bash
for p in workdir/scalableui-poc/common/patches/packages-services-Car/*.patch \
         workdir/scalableui-poc/variants/*/patches/packages-services-Car/*.patch; do
  git -C packages/services/Car apply --check "$p"
done
```

device patch は clean base に対して確認してください。

```bash
tmp=$(mktemp -d)
git -C device/generic/car show HEAD:AndroidProducts.mk > "$tmp/AndroidProducts.mk"
git -C "$tmp" apply --check workdir/scalableui-poc/common/patches/device-generic-car/0001-add-scalableui-hmi-suite-products.patch
```

## tag 管理

12 variant の初期生成状態は、tag を切って snapshot 化する運用が向いています。

例:

```bash
git tag hmi-suite-v1
git push origin main hmi-suite-v1
```

各 variant を個別に進化させる場合:

- `map-first-v2`
- `media-dock-v2`
- `floating-card-v2`
- `calm-mode-v2`

のように、variant 名を含めた tag を推奨します。

## 既知の制約

- ここで追加した 12 variant は HMI layout / routing 検証用の PoC です
- 車両状態連動、parking / charging event、UX restriction 連動はまだ実装していません
- `dual-display` は `displayId=1` を含むため、multi-display 環境での検証が必要です
- demo app は placeholder であり、量産 UI 品質の app ではありません
- fixed panel app を All apps から起動したときの fullscreen 化は、app 自身の launch mode に影響されます
