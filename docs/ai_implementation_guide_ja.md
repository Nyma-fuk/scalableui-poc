# AI 実装ガイド: ScalableUI Dynamic Workspace PoC

> Source verification: 実装前に必ず [AOSP Source Verification](./aosp_source_verification_ja.md) を読むこと。この文書は Dynamic Workspace を進めるための作業ガイドであり、AOSP 標準機能の保証ではない。

この文書は、AI agent がこの repository だけを入口にして、ScalableUI と今回の PoC を理解し、実装・build・評価まで進めるための実装ガイドです。

## 1. 判定

2026-06-09 時点の判定:

- 以前の状態: 情報は多いが、AI が迷わず実装を継続するには不足があった。
- 主な不足: `dynamic-workspace` の patch / variant directory / demo app 追補 / 読む順番 / ScalableUI 標準と custom 実装の境界が分散していた。
- 補填後の状態: `README.md`、`AGENTS.md`、本ファイル、`docs/scalableui_poc_architecture_ja.md`、`docs/dynamic_workspace_notes_ja.md` を読めば、AI が実装・build・Windows emulator 評価まで進められる情報量を持つ。

ただし、AAOS15 LTS5 / AAOS17 へ移植する場合は API 差分が出る可能性があるため、patch apply 後の build error はその版の source に合わせて解釈する。

## 2. 現在の主 PoC

主対象は `dynamic-workspace`。

目的:

- 固定 slot を持たない
- panel をユーザー操作で追加・削除できる
- panel をユーザー操作で移動できる
- panel 間の幅を grip で変更できる
- panel に表示する app をユーザーが選べる
- panel 群が画面端からはみ出す場合は横スクロールできる
- All Apps など通常 app 起動は fullscreen `app_panel` 側へ逃がせる

## 3. ScalableUI の基礎理解

ScalableUI は AAOS の cockpit HMI を panel 単位で orchestration する仕組み。

基本概念:

- Panel: 画面上の管理単位
- TaskPanel: root task stack / task を介して Activity を表示する panel
- DecorPanel: grip、header、toolbar など装飾や操作 UI を載せる panel
- Variant: panel の状態。bounds、layer、visibility などを持つ
- Transition: event に応じて variant を切り替える定義
- Event: system event、controller event、custom event
- Role: panel に載せる activity や default behavior
- StateManager: PanelState を保持し、現在 variant を適用する
- PanelPool: panel instance を取得・再利用する

今回の PoC では、固定的な panel/variant は RRO XML で定義し、動的 panel 群は SystemUI runtime code で追加する。

## 4. どこまでが標準で、どこから custom か

ScalableUI 標準で担うこと:

- RRO から `window_states` を読む
- XML の Panel / Variant / Transition を parse する
- TaskPanel / DecorPanel を作る
- Activity task を panel root task に載せる
- transition に従って panel の visibility / bounds / layer を更新する

PoC custom で担うこと:

- runtime model から任意数 panel を作る
- `StateManager.addState(...)` で runtime panel を追加する
- panel ごとの width / component / order / viewport offset を保存する
- header / grip / toolbar / viewport handle を Dynamic Workspace 専用 decor として生成する
- drag 中に task surface を重く更新しない preview policy
- panel assignment と fullscreen app launch の routing policy

検証済み境界:

- `StateManager.addState(...)` は存在するが、任意数 runtime panel 生成は標準 RRO / XML 初期化ではない
- `RemoteCarTaskView` / `TaskView` は ScalableUI `TaskPanel` の実体ではない
- Panel 間の既存 task reparent は、AOSP API として可能性はあるが live ScalableUI source では標準機能として未確認

## 5. Patch の役割

Dynamic Workspace に必要な patch:

```text
common/patches/device-generic-car/0001-add-scalableui-hmi-suite-products.patch
  HMI variant suite の product をまとめて追加する。

common/patches/packages-services-Car/0001-add-scalableui-hmi-demo-apps.patch
  demo app 群と FrameworkConfig RRO を追加する。

common/patches/packages-services-Car/0002-add-token-reparent-for-panel-routing.patch
  panel routing 用の token reparent 補助を追加する historical patch。
  live source に適用済みかを確認するまで、AOSP 標準機能として扱わない。

common/patches/packages-services-Car/0003-add-dynamic-workspace-demo-home.patch
  WorkspaceHomeActivity / WorkspaceAppPickerActivity / WorkspaceRuntimeBridge などを Home demo app に追加する。

variants/dynamic-workspace/patches/device-generic-car/0001-add-sdk_car_scalableui_dynamic_workspace_x86_64-product.patch
  `sdk_car_scalableui_dynamic_workspace_x86_64` product を追加する。

variants/dynamic-workspace/patches/packages-services-Car/0001-add-scalableui-hmi-dynamic_workspace-rro.patch
  Dynamic Workspace RRO と product package を追加する。

patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch
  SystemUI 側の ScalableUI runtime、routing、workspace controller、decor view を追加・拡張する。

patches/packages-apps-Car-Launcher/0001-all-apps-launch-to-app-panel.patch
  All Apps から起動した app を fullscreen app panel 側に寄せる。

patches/packages-apps-Car-systemlibs-car-scalable-ui-lib/0001-add-runtime-layout-variant-overrides.patch
  Variant runtime override に必要な library 側拡張を入れる。
```

## 6. Runtime architecture

```text
WorkspaceHomeActivity
  |
  | ACTION_SYNC
  v
SystemEventHandler
  |
  v
WorkspaceRuntimeLayoutController
  |
  +-- WorkspaceModelStore
  |     Settings.Secure の JSON model を load/save
  |
  +-- WorkspaceGeometry
  |     display bounds / system bar / panel / header / grip / viewport bounds を計算
  |
  +-- WorkspacePanelStateController
  |     StateManager.addState, Variant runtime bounds, BasePanel.update
  |
  +-- WorkspaceTaskRouter
        TaskPanel role 設定、panel app launch、picker fullscreen launch
```

## 7. Command flow

Demo app から SystemUI へ送る broadcast:

- action: `com.android.car.scalableui.hmi.workspace.ACTION_COMMAND`
- sync action: `com.android.car.scalableui.hmi.workspace.ACTION_SYNC`
- package: `com.android.systemui`

主な command:

- `add_panel`
- `remove_panel`
- `move_start`
- `move_update`
- `move_end`
- `resize_start`
- `resize_update`
- `resize_end`
- `pan_start`
- `pan_update`
- `pan_end`
- `center_view`
- `assign_component`
- `open_picker`

## 8. Persistence model

保存先:

```text
Settings.Secure
key=scalableui_dynamic_workspace_model_v2
user=current user
```

JSON:

```json
{
  "version": 2,
  "next_panel_index": 3,
  "viewport_offset_dp": 0,
  "panels": [
    {
      "id": "workspace_panel_1",
      "component": "com.android.car.scalableui.hmi.map/.MapActivity",
      "width_dp": 420
    }
  ]
}
```

`WorkspaceModelStore` は SystemUI 側と Home demo app 側の両方にある。SystemUI 側が runtime の正、Home demo app 側は picker 表示や現在選択状態の参照用。

## 9. Resize policy

過去の問題:

- drag 中に task panel surface / task-stack transition を更新し続けると極めて重い
- `WorkspaceHomeActivity` の HOME task を task-stack transition 対象にすると activity type 変更で SystemUI が落ちることがあった

現在の方針:

- `resize_update` では model width は更新する
- drag 中に動かすのは操作中 grip decor の surface だけ
- task panel / header / toolbar / viewport は drag 中に更新しない
- `resize_end` で保存と final surface commit を行う
- `resize_end` でも `AutoTaskStackController.startTransition(...)` は投げない

この方針は Google demo で見える「drag 中に app をリアルタイム再描画し続けない」挙動に寄せている。

## 10. Build

AAOS root で実行:

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh dynamic-workspace
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh dynamic-workspace
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=8 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh dynamic-workspace
```

単体で SystemUI を確認する場合:

```bash
source build/envsetup.sh
lunch sdk_car_scalableui_dynamic_workspace_x86_64-trunk_staging-userdebug
m -j8 CarSystemUI
```

## 11. Windows emulator evaluation

推奨起動:

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

boot wait:

```bash
ADB=/mnt/f/Android/Sdk/platform-tools/adb.exe
for i in $(seq 1 120); do
  boot="$($ADB -s emulator-5562 shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
  anim="$($ADB -s emulator-5562 shell getprop init.svc.bootanim 2>/dev/null | tr -d '\r')"
  echo "attempt=$i boot=${boot:-?} anim=${anim:-?}"
  [ "$boot" = "1" ] && [ "$anim" = "stopped" ] && break
  sleep 5
done
```

評価時に確認すること:

- boot が 1 になる
- `pidof com.android.systemui` が取得できる
- model を投入して sync できる
- grip drag で `width_dp` が変化する
- 2回目 drag が効く
- SystemUI PID が変わらない
- fatal がない

## 12. Known risks

- AAOS15 LTS5 / AAOS17 では ScalableUI API、WMShell API、Dagger graph が変わる可能性がある。
- `WorkspacePanelStateController` は `StateManager` / `PanelPool` / `BasePanel.update(...)` に依存しており、移植時に最も差分が出やすい。
- `PanelAutoTaskStackTransitionHandlerDelegate` の task reparent / target panel routing は platform 側 task policy の影響を受ける。
- task reparent は live source と `WindowContainerTransaction` 適用箇所を必ず再確認する。
- Dynamic Workspace は overlay だけで完結しない。XML-only PoC として扱ってはいけない。

## 13. 実装を続けるときの優先順位

1. 再現性: clean checkout に patch が当たること
2. 安定性: SystemUI が落ちないこと
3. 操作性: add / remove / assign / resize / pan が直感的に動くこと
4. 性能: drag 中に task surface を過剰更新しないこと
5. 移植性: AAOS core 変更を増やさず、workspace package に閉じること
6. 見た目: Material Design ベースで HMI として自然に見えること
