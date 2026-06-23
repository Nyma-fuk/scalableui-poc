# ScalableUI AAOS HMI PoC

この repository は、AAOS の ScalableUI を使った HMI 検証を、AOSP/AAOS source に基づいて整理・再現するための patch / docs / workflow 集です。

重要:

- ScalableUI / WindowManager / ActivityTaskManager の正は、この repository の docs ではなく AAOS/AOSP source code です。
- source 照合結果は [docs/aosp_source_verification_ja.md](docs/aosp_source_verification_ja.md) と [docs/aaos17_scalableui_source_verification_ja.md](docs/aaos17_scalableui_source_verification_ja.md) を正とします。
- この repository には、現行PoC、Android17移植メモ、過去variantの実験記録が混在していました。現在は下記の区分で読む前提に整理しています。

## 情報の区分

| 区分 | 内容 | 主な参照先 |
| --- | --- | --- |
| ScalableUIそのもの | AAOS/AOSP上のScalableUI、TaskPanel、StateManager、WindowManager連携の説明 | [docs/aosp_source_verification_ja.md](docs/aosp_source_verification_ja.md), [docs/aaos17_scalableui_source_verification_ja.md](docs/aaos17_scalableui_source_verification_ja.md), [docs/scalableui_window_manager_flow_ja.md](docs/scalableui_window_manager_flow_ja.md) |
| 現行PoC baseline | `declarative-multipanel` の仕様、評価、patch | [variants/declarative-multipanel/README.md](variants/declarative-multipanel/README.md), [variants/declarative-multipanel/docs/hmi_spec_ja.md](variants/declarative-multipanel/docs/hmi_spec_ja.md) |
| Android17移植 | Android17 as-isを壊さずPoC差分を載せる開発フロー | [docs/aaos17_scalableui_source_verification_ja.md](docs/aaos17_scalableui_source_verification_ja.md), [docs/aaos17_scalableui_development_flow_ja.md](docs/aaos17_scalableui_development_flow_ja.md), [docs/android17_as_is_scalableui_migration_plan_ja.md](docs/android17_as_is_scalableui_migration_plan_ja.md) |
| 個人検証側/対象環境分担 | アプリレイヤー、RRO/XML、controller、task eventの担当境界 | [docs/aaos_app_layer_scalableui_scope_ja.md](docs/aaos_app_layer_scalableui_scope_ja.md) |
| historical / experimental | 過去のdynamic workspace、editable home、widget系variant | [docs/README_ja.md](docs/README_ja.md) の分類表 |
| variant status | 各variantの現行/過去/生成案の扱い | [docs/variant_status_ja.md](docs/variant_status_ja.md) |
| repository cleanup | PoC情報の整理方針と棚卸し計画 | [docs/poc_repository_cleanup_plan_ja.md](docs/poc_repository_cleanup_plan_ja.md) |

docs全体の読み分けは [docs/README_ja.md](docs/README_ja.md) を参照してください。

## 現行baseline

現在の実装・評価の基準は `declarative-multipanel` です。

目的:

- RRO/XMLでScalableUI panel、variant、transitionを宣言する
- Framework / CarService / CarSystemUI RROでScalableUIを有効化する
- 標準CarLauncherをPoC用の空HOME hostで分離する
- AppGridをpanelとして扱い、選択アプリを指定panelへroutingする
- 固定panel構成から、All Apps、最大化、Home復帰などのPoC挙動へ段階的に拡張する

実装上の重要な読み替え:

- 「Panelにアプリを表示する」は、実装上は `Panel -> TaskPanel -> task/root task -> Activity` です。
- `RemoteCarTaskView` / `TaskView` はAAOSに存在しますが、ScalableUI `TaskPanel` の実体として扱いません。
- runtime panel生成、任意panel移動、永続化、pickerは、ScalableUI標準だけでは完結せずPoC/custom領域です。
- `WindowContainerTransaction.reparent()` はAOSPに存在しますが、現在確認したScalableUI sourceだけでは、Panel間task reparentの標準機能とは判断しません。

## Android17での開発方針

Android17移植では、PoC専用productを増やさず、build実績のある標準AAOS17 emulator targetを維持します。

```text
sdk_car_x86_64-trunk_staging-userdebug
  + ScalableUI PoC RRO
  + ScalableUiStubCarLauncher
  + 必要最小限のCarSystemUI差分
```

この方針により、「素のAAOS17 emulatorへの追加差分」として開発・説明できます。

推奨コマンド:

```bash
cd <AAOS17_ROOT>
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug

SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing

SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO

SOONG_NINJA=ninja m -j6 emu_img_zip
```

詳細は [docs/aaos17_scalableui_development_flow_ja.md](docs/aaos17_scalableui_development_flow_ja.md) を参照してください。

## AAOS15/Android16系の扱い

AAOS15 LTS3 / Android16 QPR2向けの既存patchや評価記録は残します。

ただし、それらはAndroid17の正ではありません。Android17ではScalableUI core、WMShell、TaskView周辺が更新されているため、Android15/16向けpatchをそのまま適用するのではなく、[docs/aaos17_scalableui_source_verification_ja.md](docs/aaos17_scalableui_source_verification_ja.md) と source 差分を確認して移植します。

## Historical / experimental variant

以下は正しい実験記録を含みますが、現行baselineではありません。

- `dynamic-workspace`
- `editable-home`
- `widget-workspace`
- `widget-layout-lab`
- generated HMI variant suite
- `no-grip`

これらの情報は削除せず、historical / experimental として扱います。本格適用設計やAndroid17移植の根拠にする場合は、必ず [docs/aosp_source_verification_ja.md](docs/aosp_source_verification_ja.md) と対象AAOS branchのsourceで再照合してください。

## Repository構成

```text
scalableui-poc/
  README.md
  AGENTS.md
  docs/
    README_ja.md
    aosp_source_verification_ja.md
    scalableui_window_manager_flow_ja.md
    aaos17_scalableui_source_verification_ja.md
    aaos17_scalableui_development_flow_ja.md
    android17_as_is_scalableui_migration_plan_ja.md
    aaos_app_layer_scalableui_scope_ja.md
  variants/
    README.md
    declarative-multipanel/
      docs/
      patches/
    dynamic-workspace/        # historical / experimental
    editable-home/            # historical / experimental
    widget-workspace/         # historical / experimental
    widget-layout-lab/        # historical / experimental
  scripts/
    aaos17_scalableui_build_action.sh
    apply_hmi_variant.sh
    build_hmi_modules.sh
    build_hmi_emulator_images.sh
    verify_declarative_multipanel_smoke.sh
  wiki/
```

## 評価ルール

runtime挙動に影響する変更を入れたら、buildだけで完了にしません。

最低限確認すること:

- 対象module build
- `emu_img_zip`
- Windows host emulator起動
- overlay state
- package install state
- `dumpsys activity top`
- `dumpsys window displays`
- screenshot
- logcat fatal確認

`declarative-multipanel` のsmoke script:

```bash
ADB_BIN=<ADB_BIN> \
OUT_DIR=<EVIDENCE_DIR>/declarative-multipanel-smoke-$(date +%Y%m%d-%H%M%S) \
  <SCALABLEUI_POC_ROOT>/scripts/verify_declarative_multipanel_smoke.sh <DEVICE_SERIAL>
```

Android17 build前の手動action:

```bash
<SCALABLEUI_POC_ROOT>/scripts/aaos17_scalableui_build_action.sh status
<SCALABLEUI_POC_ROOT>/scripts/aaos17_scalableui_build_action.sh commands
```

## 既知の注意点

- `-gpu host` はこのWindows環境ではemulator processが消えることがあったため、`-gpu angle_indirect` を優先します。
- `.patch` ファイルに対する `git diff --check` は、patch contextの `+ ` 空行をwarningとして拾うことがあります。
- Android17では、PoC専用productを作るより標準 `sdk_car_x86_64` に差分を載せる方針を優先します。
- ScalableUI標準機能とPoC custom実装を混ぜて説明しないでください。
