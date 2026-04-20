# Widget Workspace Build Notes

## 目的

`widget-workspace` は、ScalableUI の panel routing を使って、ユーザー操作で panel 内の app を入れ替えられることを検証する HMI variant です。

追加した要素:

- `MapPanelActivity`
- `GBallActivity`
- `WidgetPanelActivity`
- `PanelMenuActivity`
- `sdk_car_scalableui_widget_workspace_x86_64`
- `CarSystemUIScalableUiHmiWidgetWorkspaceRRO`

## Map App の扱い

Google Maps の画面画像や tile は再配布条件がこの repo の patch 配布と相性が悪いため、直接同梱していません。
代わりに `MapPanelActivity` が Java の `Canvas` で synthetic map artwork を描画します。

この判断により、他の人が public repo の patch を適用しても、外部アセットの権利や API key に依存せず同じ build 結果を得られます。

## G Ball App

`GBallActivity` は `ScalableUiDemoActivity` 内の `GBallView` を使う sample app です。

- ball は panel 内を animation する
- touch / drag で ball の位置を変えられる
- ScalableUI の panel bounds 内で app interaction が通ることを確認する用途

## Widget App

`WidgetPanelActivity` は Android 標準 widget を使った操作可能な sample panel です。

- `SeekBar` で fan 値を更新
- `Switch` で quiet mode を切り替え
- `Button` で widget layout apply の状態表示を更新

## Panel Menu による入れ替え

`PanelMenuActivity` は左側の menu panel に常駐します。
menu の button は次の Activity を explicit launch します。

- `WidgetPanelActivity`
- `MapPanelActivity`
- `GBallActivity`
- `MediaPanelActivity`
- `TaskPanelActivity`

`workspace_panel` は `role="@array/workspace_panel_componentNames"` を持ち、上記 Activity 群を persistent activity として扱います。
そのため、menu から起動された app は fullscreen fallback ではなく `workspace_panel` に route されます。

## Build / Verification

実行した確認:

```bash
JOBS=10 workdir/scalableui-poc/scripts/build_hmi_modules.sh widget-workspace
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=10 workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh widget-workspace
```

結果:

- `ScalableUiHmiDemoApps` build 成功
- `CarSystemUIScalableUiHmiWidgetWorkspaceRRO` build 成功
- `m emu_img_zip` 成功
- `/mnt/f/aaos_images/widget-workspace/sdk-repo-linux-system-images.zip` 生成済み

生成 artifact:

```text
/mnt/f/aaos_images/widget-workspace/
  manifest.txt
  run.sh
  sdk-repo-linux-system-images.zip
  sdk-repo-linux-system-images.zip.sha256
  extracted/x86_64/
```

## 発生した warning / 対応

### R8 missing class warning

RRO build 時に `android.car.Car$CarServiceLifecycleListener` や `CarUxRestrictions` 系の missing class warning が出ます。

状況:

- 既存の HMI RRO build でも同じ warning が出ている
- build は成功する
- APK install / dexpreopt まで完了する

対応:

- 現時点では非致命 warning として扱う
- RRO の `static_libs` に含まれる car-ui-lib 側の参照に起因するものとして記録

### Ninja Missing restat warning

`m emu_img_zip` 中に `linker.config.pb` や `installed-files*.txt` で `Missing restat` warning が出ます。

状況:

- build は成功する
- `sdk-repo-linux-system-images.zip` は生成される
- 生成 zip の sha256 も作成済み

対応:

- artifact 生成に影響しない warning として記録
- 失敗扱いにはしていない

## 今後の確認ポイント

- emulator 起動後に `Panel Menu` の button で `workspace_panel` の app が切り替わること
- `WidgetPanelActivity` の `SeekBar` / `Switch` / `Button` が panel 内で操作できること
- `GBallActivity` の animation と touch が panel 内で動作すること
- `MapPanelActivity` が外部地図 tile なしで安定表示されること
