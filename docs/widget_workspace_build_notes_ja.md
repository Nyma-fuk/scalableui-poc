# Widget Workspace Build Notes

## 目的

`widget-workspace` は、ScalableUI の panel routing を使って、ユーザー操作で panel 内の app を入れ替えられることを検証する HMI variant です。

追加した要素:

- `ScalableUiHmiMapDemoApp`
- `ScalableUiHmiGBallDemoApp`
- `ScalableUiHmiWidgetsDemoApp`
- `ScalableUiHmiPanelMenuDemoApp`
- `ScalableUiHmiPanelMenuButtonDemoApp`
- `ScalableUiHmiHomeDemoApp`
- `ScalableUiHmiFrameworkConfigRRO`
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

## Panel Control による入れ替え

`PanelMenuButtonActivity` は小さな `Panel Control` ボタンとして常時表示されます。
`PanelMenuActivity` は通常閉じており、ユーザーが `Panel Control` を押した時だけ表示されます。

menu では表示先 Panel を選んでから、次の個別 APK component を explicit launch します。

- `com.android.car.scalableui.hmi.widgets/.WidgetActivity`
- `com.android.car.scalableui.hmi.map/.MapActivity`
- `com.android.car.scalableui.hmi.gball/.GBallActivity`
- `com.android.car.scalableui.hmi.media/.MediaActivity`
- `com.android.car.scalableui.hmi.tasks/.TaskActivity`

`PanelMenuActivity` は `com.android.car.scalableui.extra.TARGET_PANEL_ID` を Intent extra として付けます。
加えて、`TaskInfo.baseIntent` で extra が落ちる環境でも routing できるように、`scalableui-hmi://panel-launch?target_panel=<panel_id>` の data URI も付けます。

SystemUI の `PanelAutoTaskStackTransitionHandlerDelegate` は extra を優先し、なければ data URI を読んで表示先 Panel を決めます。
新規起動直後の task は `AutoTaskStackController` の `appTasksMap` にまだ存在しないことがあるため、`WindowContainerToken` ベースの reparent を追加し、transition request 内で直接ユーザー選択 Panel に移します。

All Apps から起動された app は fullscreen `app_panel` を優先します。
これにより、Panel Control 経由の「選択したPanelへ表示」と、All Apps 経由の「通常のfullscreen起動」を分離しています。

## Task 再利用ポリシー

高負荷 app を同じ Activity component で複数起動すると、CPU / GPU / memory / decoder / surface などの system resource を二重に消費する可能性があります。
そのため `widget-workspace` は、同じ component を複数 Panel に増殖させる評価モードではなく、既存 task を優先して移動する safety-first の runtime policy にしています。

対応:

- `PanelMenuActivity` と `PanelMenuButtonActivity` の起動 Intent から `FLAG_ACTIVITY_MULTIPLE_TASK` を外し、`FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TOP | FLAG_ACTIVITY_SINGLE_TOP` にする
- All Apps の `AppLaunchProvider` からも `FLAG_ACTIVITY_MULTIPLE_TASK` を外し、fullscreen `app_panel` への通常起動でも task / Activity 再利用を優先する
- `TaskPanelInfoRepository` に既存 component task の検索を追加し、ScalableUI panel 上に同じ component の task があれば `PanelAutoTaskStackTransitionHandlerDelegate` が既存 task を選択 Panel に reparent する

期待する挙動:

- 初回起動時は新規 task を作成し、指定 Panel に reparent する
- 同じ app を別 Panel に表示したい場合は、既存 task を新しい Panel へ移動する
- 同じ task 内に同じ Activity instance を積み増さず、既存 top Activity へ戻す
- 同じ重い app が複数 instance として残り続ける状態を避ける

## Home / QuickStep 常駐対策

`CarLauncher` は AppGrid / All Apps のために image へ残します。
一方で、Home / QuickStep として `CarLauncher` process が boot 後に常駐し続ける状態は HMI 評価時に紛らわしいため、次のように分離しています。

- `packages/apps/Car/Launcher/app/AndroidManifest.xml` から `CarLauncher` の `HOME` / `SECONDARY_HOME` / `DEFAULT` / `LAUNCHER_APP` category を外す
- `ScalableUiHmiHomeDemoApp` を追加し、`HomeActivity` を軽量な no-op Home として登録する
- `ScalableUiHmiFrameworkConfigRRO` で framework の `config_recentsComponentName` を `com.android.car.scalableui.hmi.home/.NoOpRecentsActivity` に差し替える
- `NoOpQuickStepService` で `android.intent.action.QUICKSTEP_SERVICE` の bind を受け、SystemUI が `CarQuickStepService` を起動しないようにする

この構成では `CarLauncher` APK 自体は残りますが、boot 直後の Home task と QuickStep service は ScalableUI Home APK 側になります。

## Build / Verification

実行した確認:

```bash
JOBS=10 workdir/scalableui-poc/scripts/build_hmi_modules.sh widget-workspace
set +u; source build/envsetup.sh >/dev/null; lunch sdk_car_scalableui_widget_workspace_x86_64-trunk_staging-userdebug >/dev/null; set -u; m -j10 Car-WindowManager-Shell CarSystemUI CarLauncher
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=10 workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh widget-workspace
```

結果:

- demo app APK 群 build 成功
- `CarSystemUIScalableUiHmiWidgetWorkspaceRRO` build 成功
- `Car-WindowManager-Shell` / `CarSystemUI` / `CarLauncher` build 成功
- `m emu_img_zip` 成功
- `/mnt/f/aaos_images/widget-workspace/sdk-repo-linux-system-images.zip` 生成済み
- 生成日時: `2026-04-23T09:05:24+09:00`
- 生成 zip sha256: `a0a3608c1d10160f35f7ade7e6abcac6c7d88683cb87b8efa61e651532823b63`
- 生成 zip sha1: `0ae508f6c4133828959ff6a8297359c21a14be26`
- 生成 zip size: `897420681`

`system_ext.img` 内で存在確認した APK:

- `/priv-app/ScalableUiHmiMapDemoApp/ScalableUiHmiMapDemoApp.apk`
- `/priv-app/ScalableUiHmiGBallDemoApp/ScalableUiHmiGBallDemoApp.apk`
- `/priv-app/ScalableUiHmiWidgetsDemoApp/ScalableUiHmiWidgetsDemoApp.apk`
- `/priv-app/ScalableUiHmiPanelMenuDemoApp/ScalableUiHmiPanelMenuDemoApp.apk`
- `/priv-app/ScalableUiHmiPanelMenuButtonDemoApp/ScalableUiHmiPanelMenuButtonDemoApp.apk`
- `/priv-app/ScalableUiHmiHomeDemoApp/ScalableUiHmiHomeDemoApp.apk`
- `/overlay/ScalableUiHmiFrameworkConfigRRO.apk`

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

### Panel menu が起動直後から表示される

初期実装では `panel_menu` を RRO の `config_default_activities` に含めていたため、起動直後に menu が表示されていました。

原因:

- `defaultVariant="@id/closed"` だけでは、default activity として起動された `PanelMenuActivity` 自体は生成される
- その起動イベントで menu panel が表示状態へ遷移していた

対応:

- `panel_menu` に `default_launch=false` を追加し、`config_default_activities` から除外
- `panel_menu_button` だけを常時表示し、ユーザーがボタンを押したときだけ `panel_menu` を起動

### Panel Control の選択先が全画面に出る

`PanelMenuActivity` から `G Ball` を選んだとき、初回は `workspace_panel` ではなく fullscreen の `app_panel` に表示されました。

原因:

- `TARGET_PANEL_ID` extra はアプリ側で付けていたが、SystemUI が読む `TaskInfo.baseIntent` では extra が保持されないケースがある
- extra を URI に退避した後も、taskId ベースの reparent は新規起動直後に `appTasksMap` 未登録で失敗した

対応:

- `PanelMenuActivity` が `scalableui-hmi://panel-launch?target_panel=<panel_id>` を `Intent.setData()` で付与
- SystemUI が extra fallback として data URI を読む
- `Car-WindowManager-Shell` に `ReparentTaskToken` を追加し、`TransitionRequestInfo.getTriggerTask().token` で新規taskを直接reparent

確認:

- `G Ball` を `Workspace` 選択で起動すると bounds `[249,32][1881,734]` の `workspace_panel` に表示される
- logcat で `ReparentTaskToken(... parentTaskStackId=4 ...)` を確認
- `failed to reparent` は出ていない

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

## Runtime 確認済み

- emulator 起動後、`PanelMenuActivity` は初期表示されず、`Panel Control` ボタンだけが表示される
- `Panel Control` ボタンを押すと menu が表示される
- `Workspace` のまま `G Ball` を選ぶと、`GBallActivity` が fullscreen ではなく `workspace_panel` に表示される
- `WidgetActivity` の `SeekBar` / `Switch` / `Button` は panel 内で操作できる
- `MapActivity` は外部地図 tile なしで synthetic map artwork を表示する
- `cmd package resolve-activity ... HOME` は `com.android.car.scalableui.hmi.home/.HomeActivity` を返す
- `cmd overlay lookup android android:string/config_recentsComponentName` は `com.android.car.scalableui.hmi.home/.NoOpRecentsActivity` を返す
- `dumpsys activity services` では SystemUI の `QUICKSTEP_SERVICE` bind 先が `com.android.car.scalableui.hmi.home/.NoOpQuickStepService` になる
- `ps -A` では boot 後に `com.android.car.carlauncher` / `com.android.car.mapsplaceholder` process が残らない
