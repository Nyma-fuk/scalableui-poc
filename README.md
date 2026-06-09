# ScalableUI AAOS HMI PoC

この repository は、AAOS15 の ScalableUI を使った HMI PoC を別 checkout に再適用できるようにするための patch / docs / workflow 集です。

現在は、いったん `declarative-multipanel` を再出発用 baseline として扱います。これは `sdk_car_x86_64.mk` を土台に、`aaos-scalable-ui-specs` の初期 workspace を ScalableUI の panel / variant / transition / task placement として確認する構成です。

`dynamic-workspace` は、ユーザー操作で panel を追加・削除・移動・resize し、panel ごとに任意の app を割り当てる方向の大きな PoC として残しています。ただし、現在の開発方針では、まず `declarative-multipanel` で ScalableUI 標準の責務を確認してから、必要な custom 実装を段階的に足します。

## まず読むもの

人が全体を理解する場合は、次の順で読むのが一番迷いません。

1. `README.md`
2. `variants/declarative-multipanel/docs/hmi_spec_ja.md`
3. `variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md`
4. `docs/scalableui_window_manager_flow_ja.md`
5. `docs/scalableui_poc_architecture_ja.md`
6. `docs/dynamic_workspace_notes_ja.md`
7. `docs/ai_implementation_guide_ja.md`
8. `docs/hmi_variant_suite_ja.md`

AI agent に実装を任せる場合は、最初に `AGENTS.md` と `docs/ai_implementation_guide_ja.md` を読ませてください。

## 現在の到達点: declarative-multipanel

`declarative-multipanel` で確認済みのこと:

- clean `sdk_car_x86_64.mk` ベースの専用 product を build できる
- `CarSystemUI` RRO で `config_enableScalableUI=true` にできる
- Framework RRO で `config_remoteInsetsControllerControlsSystemBars=true` にできる
- CarService RRO を product overlay として入れられる
- 標準 `CarLauncher` を透明 HOME host の `StubCarLauncher` に置き換えられる
- `window_states` に定義した spec panel が SystemUI に読み込まれる
- `config_default_activities` で既存 app activity を panel に配置できる
- AppGrid を `panel_app_grid` として表示できる
- AppGrid から選択した Calendar を `user_slot_panel` に表示できる
- workspace page / resize / swap / layout edit / camera override event を評価できる
- Windows host emulator で起動し、event dispatch 後も SystemUI PID が維持される

直近の評価 artifact:

- `/tmp/aaos-spec-workspace-smoke-20260609-163618`

重要な発見:

- AAOS15 LTS3 の ScalableUI panel XML root は `<Panel>` が必要
- Passenger6 / Android 16 系 sample の `<TaskPanel>` をそのまま使うと SystemUI が restart loop になる
- AppGrid など Stub 内 Activity は HOME task と task affinity を分離する必要がある
- DecorPanel-only transition は AAOS15 LTS3 では WM transition ではなく直接 surface update へ流す必要がある
- camera override は workspace panel を hidden にせず、fullscreen high-layer の camera panel を重ねる方が復帰が安定する

## 既存 PoC: dynamic-workspace

`dynamic-workspace` で確認済みのこと:

- ScalableUI を有効化した専用 product を build できる
- Home を `WorkspaceHomeActivity` に置き換えられる
- runtime model から panel を動的生成できる
- panel を追加・削除できる
- panel header から app picker を開ける
- launchable app を panel に割り当てられる
- 隣接 panel 間の grip drag で panel 幅を変更できる
- 画面幅を超える panel 群を viewport offset で横スクロールできる
- drag 中は app task surface を逐次更新せず、操作中 grip preview を優先する
- Windows host emulator で build image を起動し、2回連続 resize 操作後も SystemUI が落ちないことを確認済み

直近の評価 artifact:

- `/tmp/dw-eval-20260609-solid-refactor`

## ScalableUI と custom 実装の境界

ScalableUI 標準で扱いやすい範囲:

- RRO XML による panel 宣言
- panel の variant / transition / layer / bounds 定義
- task activity を panel に載せること
- decor panel を重ねること
- grip / controller から event を出すこと
- launch-root panel や fullscreen fallback panel を用意すること
- 未割当 app を launch-root panel へ routing すること

`declarative-multipanel` で custom 実装している範囲:

- 標準 CarLauncher を ScalableUI HMI の邪魔をしない Stub HOME に置き換えること
- Stub AppGrid から target panel ID を付けて Activity を起動すること
- AAOS15 LTS3 で DecorPanel-only transition と target panel routing を安定させること

`dynamic-workspace` で実験した custom 実装の範囲:

- runtime model から任意数 panel を生成すること
- panel 幅、順序、viewport offset、割り当て component を保存・復元すること
- drag 中の軽量 preview と drag end 後の final surface commit
- panel header / toolbar / viewport handle など Dynamic Workspace 固有 UI
- All Apps と panel assignment の routing policy

この境界を崩さないことが、AAOS15 LTS5 / AAOS17 へ移植するときの重要な方針です。

## Repository 構成

```text
workdir/scalableui-poc/
  README.md
  AGENTS.md
  common/patches/
    device-generic-car/
    packages-services-Car/
  variants/
    declarative-multipanel/
    dynamic-workspace/
    widget-workspace/
    editable-home/
    ...
  patches/
    packages-apps-Car-SystemUI/
    packages-apps-Car-Launcher/
    packages-apps-Car-systemlibs-car-scalable-ui-lib/
    packages-services-Car/
    device-generic-car/
  scripts/
    apply_hmi_variant.sh
    build_hmi_modules.sh
    build_hmi_emulator_images.sh
    export_patches.sh
  docs/
  wiki/
```

## declarative-multipanel の主要 patch

clean AAOS checkout へ最小 baseline を適用するには、次の patch だけを使います。

- `variants/declarative-multipanel/patches/device-generic-car/0001-add-sdk_car_scalableui_declarative_multipanel_x86_64-product.patch`
- `variants/declarative-multipanel/patches/packages-services-Car/0001-add-scalableui-declarative-multipanel-rro.patch`
- `variants/declarative-multipanel/patches/packages-apps-Car-SystemUI/0001-add-scalableui-declarative-multipanel-runtime-routing.patch`

`scripts/apply_hmi_variant.sh declarative-multipanel` は、従来の common demo apps / dynamic workspace / Launcher / scalable-ui-lib patch を適用しません。

## Dynamic Workspace の主要 patch

`dynamic-workspace` を clean AAOS checkout へ適用するには、概念上次の patch 群が必要です。

- `common/patches/device-generic-car/0001-add-scalableui-hmi-suite-products.patch`
- `common/patches/packages-services-Car/0001-add-scalableui-hmi-demo-apps.patch`
- `common/patches/packages-services-Car/0002-add-token-reparent-for-panel-routing.patch`
- `common/patches/packages-services-Car/0003-add-dynamic-workspace-demo-home.patch`
- `variants/dynamic-workspace/patches/device-generic-car/0001-add-sdk_car_scalableui_dynamic_workspace_x86_64-product.patch`
- `variants/dynamic-workspace/patches/packages-services-Car/0001-add-scalableui-hmi-dynamic_workspace-rro.patch`
- `patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch`
- `patches/packages-apps-Car-Launcher/0001-all-apps-launch-to-app-panel.patch`
- `patches/packages-apps-Car-systemlibs-car-scalable-ui-lib/0001-add-runtime-layout-variant-overrides.patch`

`scripts/apply_hmi_variant.sh dynamic-workspace` はこれらを順に適用する入口です。

## Quick Start

前提:

- AAOS15 checkout の root にいる
- この repository が `workdir/scalableui-poc` にある
- `device/generic/car`、`packages/services/Car`、`packages/apps/Car/SystemUI`、`packages/apps/Car/Launcher` が存在する

適用:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh declarative-multipanel
```

module build:

```bash
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh declarative-multipanel
```

emulator image build:

```bash
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=8 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh declarative-multipanel
```

Windows host emulator で評価する場合:

```powershell
Start-Process -FilePath 'F:\Android\Sdk\emulator\emulator.exe' `
  -ArgumentList '-avd','Y-Fuk-dynamic-workspace-clean2',
                '-sysdir','F:\aaos_images\declarative-multipanel\extracted\x86_64',
                '-wipe-data','-no-snapshot-load',
                '-ports','5564,5565',
                '-memory','6144',
                '-cores','6',
                '-gpu','angle_indirect'
```

起動済み emulator に対する smoke:

```bash
ADB_BIN=/mnt/f/Android/Sdk/platform-tools/adb.exe \
OUT_DIR=/tmp/declarative-multipanel-smoke-$(date +%Y%m%d-%H%M%S) \
  workdir/scalableui-poc/scripts/verify_declarative_multipanel_smoke.sh emulator-5564
```

この smoke は、StubCarLauncher / RRO 有効化 / spec workspace panel / user slot app assignment / workspace event / layout edit / camera override / System Bar Apps / process 維持を確認します。

## declarative-multipanel の重要ファイル

AAOS tree に patch 適用後、現在の clean baseline の中心は以下です。

```text
device/generic/car/
  sdk_car_scalableui_declarative_multipanel_x86_64.mk

packages/services/Car/car_product/scalableui_declarative_multipanel/
  car_scalableui_declarative_multipanel.mk
  apps/StubCarLauncher/
    Android.bp
    AndroidManifest.xml
    src/com/android/car/carlauncher/CarLauncher.java
    src/com/android/car/carlauncher/AppGridActivity.java
    src/com/android/car/carlauncher/ControlBarActivity.java
    src/com/android/car/carlauncher/EmptySlotActivity.java
    src/com/android/car/carlauncher/CameraStubActivity.java
  rro/CarFrameworkScalableUiDeclarativeMultipanelRRO/
  rro/CarServiceScalableUiDeclarativeMultipanelRRO/
  rro/CarSystemUIScalableUiDeclarativeMultipanelRRO/
    res/values/config.xml
    res/xml/top_bar_panel.xml
    res/xml/bottom_bar_panel.xml
    res/xml/hvac_panel.xml
    res/xml/nav_panel.xml
    res/xml/media_panel.xml
    res/xml/user_slot_panel.xml
    res/xml/empty_slot_hint_panel.xml
    res/xml/camera_priority_panel.xml
    res/xml/edit_overlay_panel.xml
    res/xml/panel_app_grid.xml
    res/xml/app_panel.xml

packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/
  PanelAutoTaskStackTransitionHandlerDelegate.java
  PanelConfigReader.java
  PanelTransitionCoordinator.java
  ScalableUIWMInitializer.java
  panel/DecorPanel.java
```

## Dynamic Workspace の重要ファイル

AAOS tree に patch 適用後、Dynamic Workspace の中心は以下です。

```text
packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/workspace/
  WorkspaceRuntimeLayoutController.java
  WorkspaceGeometry.java
  WorkspacePanelStateController.java
  WorkspaceTaskRouter.java
  WorkspaceModelStore.java
  WorkspaceHeaderView.java
  WorkspaceGripView.java
  WorkspaceToolbarView.java
  WorkspaceViewportHandleView.java

packages/services/Car/car_product/scalableui_hmi_dynamic_workspace/
  car_scalableui_hmi_dynamic_workspace.mk
  rro/CarSystemUIScalableUiHmiDynamicWorkspaceRRO/...

packages/services/Car/car_product/scalableui_hmi_demo_apps/apps/home/
  AndroidManifest.xml
  src/.../WorkspaceHomeActivity.java
  src/.../WorkspaceEmptyPanelActivity.java
  src/.../WorkspaceAppPickerActivity.java
  src/.../WorkspaceRuntimeBridge.java
```

## 評価ルール

runtime 挙動に影響する変更を入れたら、build だけで完了にしないでください。

`declarative-multipanel` の最低限必要な確認:

- 対象 module build
- `declarative-multipanel` emulator image zip build
- Windows host emulator 起動
- `verify_declarative_multipanel_smoke.sh` 実行
- System Bar Apps から AppGrid が表示されること
- AppGrid から Calendar を起動すると `user_slot_panel` に表示されること
- workspace page / resize / swap event で bounds が変わること
- layout edit overlay が表示されること
- camera override が fullscreen 表示され、解除後に workspace が復帰すること
- `SystemUI` PID 維持
- `FATAL EXCEPTION` / `AndroidRuntime` / `IllegalStateException` が出ていないこと
- screenshot と logcat summary を `/tmp/<評価名>/` に保存

`dynamic-workspace` を触る場合は追加で以下を確認します。

- panel add / app assignment / grip resize / second resize 操作
- drag 中の UI 重さ、surface 更新頻度、viewport 横スクロール

## 既知の注意点

- `-gpu host` はこの Windows 環境では emulator process が消えることがあったため、現時点では `-gpu angle_indirect` を優先します。
- guest RAM 2GB の AVD は複数 panel / 複数 activity / SurfaceControl 更新の評価には重いため、評価時は `-memory 6144 -cores 6` を使います。
- `.patch` ファイルに対する `git diff --check` は `+ ` の空行を warning として拾うことがあります。必ず AAOS ソース本体の whitespace と分けて判断してください。
- `dynamic-workspace` は ScalableUI の標準 XML だけで完結していません。runtime panel 生成と persistence は PoC custom 実装です。

## その他の variant

`docs/hmi_variant_suite_ja.md` に HMI variant 一覧があります。

代表例:

- `fixed-3zone`: 固定 3 panel の baseline
- `widget-workspace`: Panel Control 経由の app routing 検証
- `editable-home`: 保存可能な 3 panel home の実験
- `widget-layout-lab`: widget 配置案の UI 実験
- `dynamic-workspace`: 過去の動的 workspace 実験
