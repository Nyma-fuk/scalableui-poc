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
  - HMI 評価用の複数 demo app APK と共通 library を追加する patch
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
| `widget-workspace` | `sdk_car_scalableui_widget_workspace_x86_64` | menu 操作で workspace panel の app を入れ替える widget cockpit |
| `editable-home` | `sdk_car_scalableui_editable_home_x86_64` | system bar を避けた multipanel home と保存可能な panel assignment |
| `widget-layout-lab` | `sdk_car_scalableui_widget_layout_lab_x86_64` | 右側 Widget picker と配置パターン切替を試す layout lab |

## すべての HMI を適用する

clean な AAOS15 checkout で、repo root から実行します。

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_suite.sh
```

この script は次を適用します。

- suite 用 device product patch
- 共通 demo app patch
- 15 個すべての variant RRO patch
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

## Demo Apps

標準 AAOS に存在しない map / G Ball / widget / task / status / energy / debug / controls などの領域には、評価用の複数 APK を使います。
ScalableUI が複数 app package / task をどう panel routing するかを正しく見るため、各 demo app は個別 module / 個別 package に分けています。

主な module / component:

- `ScalableUiHmiMapDemoApp`: `com.android.car.scalableui.hmi.map/.MapActivity`
- `ScalableUiHmiGBallDemoApp`: `com.android.car.scalableui.hmi.gball/.GBallActivity`
- `ScalableUiHmiWidgetsDemoApp`: `com.android.car.scalableui.hmi.widgets/.WidgetActivity`
- `ScalableUiHmiCalendarDemoApp`: `com.android.car.scalableui.hmi.calendar/.CalendarActivity`
- `ScalableUiHmiWeatherDemoApp`: `com.android.car.scalableui.hmi.weather/.WeatherActivity`
- `ScalableUiHmiWidgetMenuDemoApp`: `com.android.car.scalableui.hmi.widgetmenu/.WidgetMenuActivity`
- `ScalableUiHmiWidgetMenuButtonDemoApp`: `com.android.car.scalableui.hmi.widgetmenubutton/.WidgetMenuButtonActivity`
- `ScalableUiHmiWidgetDropZoneDemoApp`: `com.android.car.scalableui.hmi.widgetdropzone/.WidgetDropZoneActivity`
- `ScalableUiHmiPanelMenuDemoApp`: `com.android.car.scalableui.hmi.panelmenu/.PanelMenuActivity`
- `ScalableUiHmiMediaDemoApp`: `com.android.car.scalableui.hmi.media/.MediaActivity`
- `ScalableUiHmiTasksDemoApp`: `com.android.car.scalableui.hmi.tasks/.TaskActivity`

描画や widget の共通実装は static library `ScalableUiHmiDemoCommon` に集約し、各 APK は薄い Activity wrapper として実装しています。
`MapActivity` は外部地図 tile を同梱せず、repo 内で再配布可能な synthetic map artwork をコード描画します。
`PanelMenuActivity` は `widget-workspace` の menu panel からユーザーが選んだ panel に表示する app を起動し、ScalableUI の token reparent routing で panel 内の app 入れ替えを確認します。
`HomeEditActivity` は `editable-home` の content area 内 editor として動き、L1/L2/L3 と panel assignment を `SharedPreferences` に保存し、保存時に ScalableUI event と panel launch を行います。
`WidgetMenuActivity` は `widget-layout-lab` の右側 picker から prepared layout event を broadcast し、ScalableUI の `Variant` / `Transition` で widget 配置パターンを切り替えます。
量産向け UI ではなく、panel bounds / routing / layout / widget 操作を試すためのものです。

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

15 variant の初期生成状態は、tag を切って snapshot 化する運用が向いています。

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

- ここで追加した 13 variant は HMI layout / routing 検証用の PoC です
- 車両状態連動、parking / charging event、UX restriction 連動はまだ実装していません
- `dual-display` は `displayId=1` を含むため、multi-display 環境での検証が必要です
- demo app は placeholder / sample app であり、量産 UI 品質の app ではありません
- fixed panel app を All apps から起動したときの fullscreen 化は、app 自身の launch mode に影響されます
- Google Maps の画像や tile は再配布権限が不明確なため同梱していません。地図領域は synthetic map artwork で代替しています。

## エミュレータ image の作成と保存

Windows host の `F:\aaos_images` は、WSL からは `/mnt/f/aaos_images` として見えます。

先に app / RRO だけを順次 build して、Java / resource / overlay の問題を潰す場合:

```bash
bash workdir/scalableui-poc/scripts/build_hmi_modules.sh
```

1 variant だけ確認する場合:

```bash
bash workdir/scalableui-poc/scripts/build_hmi_modules.sh map-first
```

エミュレータ image は、full build の生 output をコピーするのではなく、AAOS / Goldfish の配布用 target である `emu_img_zip` を使います。
script は各 variant で `m emu_img_zip` を実行し、`sdk-repo-linux-system-images.zip` と展開済み起動用 image を保存します。

13 variant すべての emulator image zip を build して保存する場合:

```bash
AAOS_IMAGE_ROOT=/mnt/f/aaos_images \
  bash workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh
```

1 variant だけ emulator image zip を build する場合:

```bash
AAOS_IMAGE_ROOT=/mnt/f/aaos_images \
  bash workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh map-first
```

保存先:

```text
/mnt/f/aaos_images/<variant>/
  manifest.txt
  run.sh
  sdk-repo-linux-system-images.zip
  sdk-repo-linux-system-images.zip.sha256
  extracted/
    x86_64/
    system.img
    vendor.img
    ramdisk.img
    kernel-ranchu
    ...
```

保存済み image から起動する場合:

```bash
bash workdir/scalableui-poc/scripts/run_hmi_emulator.sh map-first
```

または保存先の wrapper を使います。

```bash
/mnt/f/aaos_images/map-first/run.sh
```

emulator に追加 option を渡す場合:

```bash
bash workdir/scalableui-poc/scripts/run_hmi_emulator.sh map-first -no-window -gpu swiftshader_indirect
```

`AAOS_IMAGE_ROOT` を指定しない場合、script は `/mnt/f/aaos_images` を使います。

## Windows host で emulator.exe から起動する

Android Studio / SDK Manager で system image を install 済み、かつ AVD 作成済みなら、Windows host 側の `emulator.exe` を直接起動できます。
WSL から PowerShell を呼んでも、表示は Windows デスクトップ側に出ます。

AVD 一覧を確認:

```powershell
F:\Android\Sdk\emulator\emulator.exe -list-avds
```

既存 AVD を visible window 付きで起動:

```powershell
Start-Process -FilePath 'F:\Android\Sdk\emulator\emulator.exe' `
  -ArgumentList '-avd','Y-Fuk-scalableui-widget-layout-lab','-no-snapshot-load'
F:\Android\Sdk\platform-tools\adb.exe devices -l
```

同じ AVD が既に起動中なら、先に emulator console から stop してから再起動します。

```powershell
F:\Android\Sdk\platform-tools\adb.exe -s emulator-5554 emu kill
Start-Process -FilePath 'F:\Android\Sdk\emulator\emulator.exe' `
  -ArgumentList '-avd','Y-Fuk-scalableui-widget-layout-lab','-no-snapshot-load'
```

PoC の確認例:

- `widget-layout-lab` では右下の `Widget Layout` button を押すと右側 picker が開く
- `adb exec-out screencap -p` で表示を記録できる
- `adb shell input tap` で preset button を押し、variant の切替結果を確認できる

## 検証プロセスの標準化

variant ごとに「見た目が出た」だけで完了扱いにはしません。基本フローは次です。

1. patch を適用する
2. module build を通す
3. image 変更を含む場合は `emu_img_zip` まで作る
4. emulator を起動する
5. screenshot / `dumpsys` / `SharedPreferences` を使って受け入れ条件を確認する
6. その variant の README / spec に結果を反映する

特に `editable-home` は formal spec があるため、`widget-layout-lab` の動作確認を代用しません。
必ず `editable-home` の emulator 上で次を確認します。

- `L1/L2/L3` の layout 切替
- panel ごとの whitelist app assignment
- duplicate assignment rejection
- 保存後の復元
- system bar と content area の非干渉

自動検証の入口:

```bash
bash workdir/scalableui-poc/scripts/verify_editable_home_acceptance.sh
```

既定の artifact 出力先:

```text
/tmp/editable-home-acceptance/
  acceptance_report.md
  home-l2.png
  home-l1.png
  home-l1-restored.png
  activities-l2.txt
  activities-l1.txt
  activities-l1-restored.txt
```

この script は `editable-home` product 上でのみ動作し、受け入れ条件のうち自動化できる部分をまとめて確認します。
