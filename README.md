# ScalableUI AAOS HMI PoC

この repository は、AAOS15 の ScalableUI を使った HMI PoC を別 checkout に再適用できるようにするための patch / docs / workflow 集です。

現在の主対象は `dynamic-workspace` です。これは固定 XML slot ではなく、ユーザー操作で panel を追加・削除・移動・resize し、panel ごとに任意の app を割り当てる方向の PoC です。

## まず読むもの

人が全体を理解する場合は、次の順で読むのが一番迷いません。

1. `README.md`
2. `docs/scalableui_poc_architecture_ja.md`
3. `docs/dynamic_workspace_notes_ja.md`
4. `docs/ai_implementation_guide_ja.md`
5. `docs/hmi_variant_suite_ja.md`

AI agent に実装を任せる場合は、最初に `AGENTS.md` と `docs/ai_implementation_guide_ja.md` を読ませてください。

## 現在の到達点

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

今回 custom 実装している範囲:

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
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh dynamic-workspace
```

module build:

```bash
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh dynamic-workspace
```

emulator image build:

```bash
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=8 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh dynamic-workspace
```

Windows host emulator で評価する場合:

```powershell
Start-Process -FilePath 'F:\Android\Sdk\emulator\emulator.exe' `
  -ArgumentList '-avd','Y-Fuk-dynamic-workspace-eval3',
                '-sysdir','F:\aaos_images\dynamic-workspace\extracted\x86_64',
                '-wipe-data','-no-snapshot-load',
                '-ports','5562,5563',
                '-memory','6144',
                '-cores','6',
                '-gpu','angle_indirect'
```

## 実装上の重要ファイル

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

最低限必要な確認:

- `CarSystemUI` または対象 module build
- `dynamic-workspace` emulator image zip build
- Windows host emulator 起動
- panel add / app assignment / grip resize / second resize 操作
- `SystemUI` PID 維持
- `FATAL EXCEPTION` / `AndroidRuntime` / `IllegalStateException` が出ていないこと
- screenshot と logcat summary を `/tmp/<評価名>/` に保存

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
- `dynamic-workspace`: 現在の主 PoC
