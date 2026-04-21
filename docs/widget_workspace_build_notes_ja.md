# Widget Workspace Build Notes

## 目的

`widget-workspace` は、ScalableUI の panel routing を使って、ユーザー操作で panel 内の app を入れ替えられることを検証する HMI variant です。

追加した要素:

- `ScalableUiHmiMapDemoApp`
- `ScalableUiHmiGBallDemoApp`
- `ScalableUiHmiWidgetsDemoApp`
- `ScalableUiHmiPanelMenuDemoApp`
- `sdk_car_scalableui_widget_workspace_x86_64`
- `CarSystemUIScalableUiHmiWidgetWorkspaceRRO`

各 demo は 1 APK に複数 Activity を詰める形ではなく、個別 APK / 個別 package として構成しています。
これにより、ScalableUI の複数 app package / task routing を評価できます。

## Map App の扱い

Google Maps の画面画像や tile は再配布条件がこの repo の patch 配布と相性が悪いため、直接同梱していません。
代わりに `MapActivity` が Java の `Canvas` で synthetic map artwork を描画します。

この判断により、他の人が public repo の patch を適用しても、外部アセットの権利や API key に依存せず同じ build 結果を得られます。

## G Ball App

`GBallActivity` は `ScalableUiHmiGBallDemoApp` の sample app です。

- ball は panel 内を animation する
- touch / drag で ball の位置を変えられる
- ScalableUI の panel bounds 内で app interaction が通ることを確認する用途

## Widget App

`WidgetActivity` は Android 標準 widget を使った操作可能な sample panel です。

- `SeekBar` で fan 値を更新
- `Switch` で quiet mode を切り替え
- `Button` で widget layout apply の状態表示を更新

## Panel Menu による入れ替え

`PanelMenuActivity` は左側の menu panel に常駐します。
menu の button は次の個別 APK component を explicit launch します。

- `com.android.car.scalableui.hmi.widgets/.WidgetActivity`
- `com.android.car.scalableui.hmi.map/.MapActivity`
- `com.android.car.scalableui.hmi.gball/.GBallActivity`
- `com.android.car.scalableui.hmi.media/.MediaActivity`
- `com.android.car.scalableui.hmi.tasks/.TaskActivity`

`workspace_panel` は `role="@array/workspace_panel_componentNames"` を持ち、上記 Activity 群を persistent activity として扱います。
そのため、menu から起動された app は fullscreen fallback ではなく `workspace_panel` に route されます。

## Build / Verification

実行した確認:

```bash
JOBS=10 workdir/scalableui-poc/scripts/build_hmi_modules.sh widget-workspace
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=10 workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh widget-workspace
```

結果:

- demo app APK 群 build 成功
- `CarSystemUIScalableUiHmiWidgetWorkspaceRRO` build 成功
- `m emu_img_zip` 成功
- `/mnt/f/aaos_images/widget-workspace/sdk-repo-linux-system-images.zip` 生成済み
- 生成 zip sha256: `5772bcb368c2731aa5d0d808cdc3d728859b390f47cfeff9602e6af066bfadf9`

`system_ext.img` 内で存在確認した APK:

- `/priv-app/ScalableUiHmiMapDemoApp/ScalableUiHmiMapDemoApp.apk`
- `/priv-app/ScalableUiHmiGBallDemoApp/ScalableUiHmiGBallDemoApp.apk`
- `/priv-app/ScalableUiHmiWidgetsDemoApp/ScalableUiHmiWidgetsDemoApp.apk`
- `/priv-app/ScalableUiHmiPanelMenuDemoApp/ScalableUiHmiPanelMenuDemoApp.apk`

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

### `android_app_defaults` が未対応

複数 demo APK 化の初回 build で次のエラーが出ました。

```text
unrecognized module type "android_app_defaults"
```

原因:

- この AAOS15 tree の Soong では `android_app_defaults` module type を使えない

対応:

- 共通 app property は `defaults` module にせず、各 `android_app` module に明示的に展開した

### `android_library` が manifest を要求

共通 UI 実装を `android_library` にした初回 build で次のエラーが出ました。

```text
module "ScalableUiHmiDemoCommon" variant "android_common": module source path ".../AndroidManifest.xml" does not exist
```

原因:

- 共通部は Android resource / manifest を持たない Java 実装だけなのに `android_library` として定義していた

対応:

- `ScalableUiHmiDemoCommon` を `java_library` に変更し、各 APK から `static_libs` で取り込む構成にした

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
- `WidgetActivity` の `SeekBar` / `Switch` / `Button` が panel 内で操作できること
- `GBallActivity` の animation と touch が panel 内で動作すること
- `MapActivity` が外部地図 tile なしで安定表示されること
