# declarative-multipanel 評価記録 2026-06-09

## 評価対象

- product: `sdk_car_scalableui_declarative_multipanel_x86_64`
- lunch: `sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug`
- SystemUI RRO: `CarSystemUIScalableUiDeclarativeMultipanelRRO`
- Framework RRO: `CarFrameworkScalableUiDeclarativeMultipanelRRO`
- HOME replacement: `StubCarLauncher`
- host emulator: Windows SDK emulator
- AVD: `Y-Fuk-dynamic-workspace-clean2`
- image: `/mnt/f/aaos_images/declarative-multipanel/extracted/x86_64`
- final runtime artifact: `/tmp/aaos-spec-workspace-smoke-20260609-163618`

現在の正は `v12 aaos-scalable-ui-specs baseline 評価` です。v9 から v11 は、`map_panel` / `settings_panel` を使っていた初期検証の履歴として残しています。

## Build 結果

module build:

```bash
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh declarative-multipanel
```

結果: 成功

emulator image build:

```bash
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=4 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh declarative-multipanel
```

結果: 成功

image zip:

```text
out/target/product/emulator_car64_x86_64/sdk-repo-linux-system-images.zip
/mnt/f/aaos_images/declarative-multipanel/sdk-repo-linux-system-images.zip
/mnt/f/aaos_images/declarative-multipanel/extracted/x86_64
```

## 起動方法

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

ADB:

```bash
/mnt/f/Android/Sdk/platform-tools/adb.exe -s emulator-5564
```

最終評価では boot completed は 32 秒で返りました。

## 実装中に潰した問題

### `<TaskPanel>` root は AAOS15 LTS3 で使えない

Passenger6 / Android 16 系 sample に寄せて XML root を `<TaskPanel>` にすると、AAOS15 LTS3 の parser は `<Panel>` root を期待しているため SystemUI が restart loop になりました。

代表ログ:

```text
XmlPullParserException: Expected <Panel> tag at the beginning but TaskPanel
NullPointerException ... PanelState.getId()
```

対応:

- `map_panel.xml`
- `media_panel.xml`
- `settings_panel.xml`
- `panel_app_grid.xml`
- `app_panel.xml`

上記すべての root tag を `<Panel>` にしました。

### 標準 CarLauncher は ScalableUI HMI と干渉する

標準 `CarLauncher` を残したままだと HOME UI / AppGrid / fragment が表示主体になり、ScalableUI panel の背後や前面に意図しない UI が出ます。

対応:

- `StubCarLauncher` を `com.android.car.carlauncher` package で追加
- `overrides: ["CarLauncher", "Launcher2", "Launcher3", "Launcher3QuickStep"]`
- `.CarLauncher` は透明な HOME host
- `.ControlBarActivity` は media panel 用 placeholder
- `.AppGridActivity` は ScalableUI baseline 用 lightweight app grid

### AppGridActivity が HOME task に混ざる

Stub 内の `.CarLauncher` と `.AppGridActivity` が同じ task affinity のままだと、AppGrid が HOME task に積まれて `mActivityType=home` になり、`panel_app_grid` として見えませんでした。

対応:

- `.CarLauncher`: `taskAffinity="com.android.car.carlauncher.home"`
- `.ControlBarActivity`: `taskAffinity="com.android.car.carlauncher.controlbar"`
- `.AppGridActivity`: `taskAffinity="com.android.car.carlauncher.appgrid"`

最終評価では AppGridActivity が `mActivityType=standard` で起動することを確認しました。

## v9 確認結果

summary:

```text
artifact=/tmp/declarative-multipanel-stub-eval-20260609-v9
avd=Y-Fuk-dynamic-workspace-clean2
serial=emulator-5564
image_sysdir=F:\aaos_images\declarative-multipanel\extracted\x86_64
systemui_pid_home=1489
systemui_pid_after=1489
carlauncher_pid_home=2829
carlauncher_pid_after=2829
pm_path=package:/system_ext/priv-app/StubCarLauncher/StubCarLauncher.apk
systemui_overlay=[x] com.android.systemui.rro.scalableui.declarative.multipanel
framework_overlay=[x] android.car.config.rro.scalableui.declarative.multipanel
appgrid_task_type=stateNotNeeded=false componentSpecified=true mActivityType=standard
appgrid_activity_count=9
calendar_activity_mentions=25
app_panel_nonempty_log_count=18
fatal_exception_count=0
```

確認できたこと:

- SystemUI RRO が有効
- Framework RRO が有効
- `StubCarLauncher` が標準 `CarLauncher` の代わりに入っている
- Home で `map_panel` / `media_panel` / `settings_panel` が表示される
- `AppGridActivity` が `panel_app_grid` として画面に表示される
- AppGrid から `Calendar` を選ぶと、未割当 app として launch-root の `app_panel` に表示される
- `app_panel` open 時に `map_panel` / `media_panel` / `settings_panel` は隠れる
- 操作後も SystemUI PID と StubCarLauncher PID は維持される
- 最終評価中の `FATAL EXCEPTION` は 0

## v9 Screenshot artifact

```text
/tmp/declarative-multipanel-stub-eval-20260609-v9/01-home.png
/tmp/declarative-multipanel-stub-eval-20260609-v9/02-appgrid.png
/tmp/declarative-multipanel-stub-eval-20260609-v9/03-after-appgrid-row-tap.png
```

`02-appgrid.png` では `Apps` panel と launchable app 一覧を確認しました。

`03-after-appgrid-row-tap.png` では `Calendar` が system bar を避けた大きな `app_panel` として表示されることを確認しました。

## v9 判定

Pass:

- clean `sdk_car_x86_64.mk` ベースの専用 product を build できる
- ScalableUI を RRO で有効化できる
- Framework 側の remote insets 設定も RRO で有効化できる
- 標準 CarLauncher を Stub に置き換え、ScalableUI HMI の邪魔をしない HOME host にできる
- RRO XML で固定 multi panel HMI を構成できる
- AppGrid を panel として表示できる
- AppGrid から選んだ未割当 app を launch-root `app_panel` に表示できる
- Windows host emulator で起動評価できる

Out of scope:

- grip resize
- panel add / delete
- panel drag / reorder
- 任意 panel への任意 app assignment UI
- runtime persistence

## 次 phase の推奨

1. `declarative-multipanel` を ScalableUI 標準責務の baseline として維持する
2. grip resize は XML event / controller でできる範囲をまず評価する
3. 動的 panel / 任意 app picker は ScalableUI 標準の外側に custom Home runtime として足す
4. その際も Stub HOME、task affinity 分離、launch-root panel の考え方は維持する

## v10 UI 整合性再評価

ユーザー指摘:

- All Apps が出ないことがある
- panel 内の Settings 項目をタップすると Calendar が表示されるように見える

対応:

- 固定 `settings_panel` の role を本物の `CarSettings` から `StubCarLauncher` 内の `SettingsPanelActivity` に変更
- All Apps から起動する本物の `CarSettings` は未割当 app として launch-root `app_panel` に流す
- `AppGridActivity` は app 起動後に `finishAndRemoveTask()` し、AppGrid overlay task を残しにくくした
- app 起動時に `RESET_TASK_IF_NEEDED` / `CLEAR_TOP` / `SINGLE_TOP` を付与した

評価 artifact:

```text
/tmp/declarative-multipanel-ui-eval-20260609-v10
```

build:

```text
module build: pass
emu_img_zip: pass
image save: first attempt failed because emulator-5564 locked old system.img/vendor.img
image save retry after emulator kill: pass
```

runtime summary:

```text
avd=Y-Fuk-dynamic-workspace-clean2
serial=emulator-5564
image_sysdir=F:\aaos_images\declarative-multipanel\extracted\x86_64
pm_path=package:/system_ext/priv-app/StubCarLauncher/StubCarLauncher.apk
systemui_pid_home=2101
systemui_pid_after_settings=2101
carlauncher_pid_home=2885
carlauncher_pid_after_settings=2885
systemui_overlay=[x] com.android.systemui.rro.scalableui.declarative.multipanel
framework_overlay=[x] android.car.config.rro.scalableui.declarative.multipanel
home_settings_panel_stub_mentions=15
systembar_appgrid_activity_mentions=15
systembar_appgrid_ui_apps_title_count=1
settings_full_panel_bounds=found:     mBounds=Rect(38, 53 - 1881, 1026)
settings_item_network_visible=1
calendar_mentions_after_settings_item=0
fatal_exception_count=0
```

確認結果:

- Home の右下 `settings_panel` は `SettingsPanelActivity` stub として表示された
- 実System BarのAppsボタンをタップして `AppGridActivity` が表示された
- AppGridから本物の Settings を選ぶと `app_panel` bounds `Rect(38, 53 - 1881, 1026)` に表示された
- Settings 内の `Network & internet` 項目をタップしても Calendar には遷移せず、Settings 内部画面が表示された
- 評価中の SystemUI PID / StubCarLauncher PID は維持された
- `FATAL EXCEPTION` は 0

Screenshot artifact:

```text
/tmp/declarative-multipanel-ui-eval-20260609-v10/02-home-dismissed.png
/tmp/declarative-multipanel-ui-eval-20260609-v10/03-after-systembar-apps-tap.png
/tmp/declarative-multipanel-ui-eval-20260609-v10/04-after-settings-from-appgrid.png
/tmp/declarative-multipanel-ui-eval-20260609-v10/05-after-settings-item-tap.png
```

判定:

- `declarative-multipanel` baseline の UI 整合性は、固定 panel / All Apps / Settings fullscreen routing の範囲で pass
- ただし、これは静的 multipanel baseline の評価であり、grip resize / panel追加削除 / 任意panel app割当は未実装

## v11 smoke script 化

手動評価の再現性を上げるため、同じ観点を `verify_declarative_multipanel_smoke.sh` に落とし込みました。

実行:

```bash
ADB_BIN=/mnt/f/Android/Sdk/platform-tools/adb.exe \
OUT_DIR=/tmp/declarative-multipanel-smoke-20260609-script-v1 \
  workdir/scalableui-poc/scripts/verify_declarative_multipanel_smoke.sh emulator-5564
```

評価 artifact:

```text
/tmp/declarative-multipanel-smoke-20260609-script-v1
```

report:

```text
- [PASS] StubCarLauncher is installed under system_ext
- [PASS] SystemUI ScalableUI overlay is enabled
- [PASS] Framework ScalableUI overlay is enabled
- [PASS] fixed settings placeholder panel is visible
- [PASS] map panel activity is present
- [PASS] media panel activity is present
- [PASS] settings placeholder panel activity is present
- [PASS] AppGridActivity task is present
- [PASS] System Bar Apps button opens AppGrid
- [PASS] Settings row is visible in AppGrid
- [PASS] real Settings is launched
- [PASS] real Settings uses fullscreen app_panel bounds on 1920x1080
- [PASS] Settings item tap stays inside Settings
- [PASS] Settings item tap does not route to Calendar
- [PASS] SystemUI process stayed alive
- [PASS] StubCarLauncher process stayed alive
- [PASS] No recent FATAL EXCEPTION in logcat tail
```

summary:

```text
artifact=/tmp/declarative-multipanel-smoke-20260609-script-v1
serial=emulator-5564
wm_size=1920x1080
pm_path=package:/system_ext/priv-app/StubCarLauncher/StubCarLauncher.apk
systemui_pid_home=2101
carlauncher_pid_home=2885
systemui_pid_after=2101
carlauncher_pid_after=2885
fatal_exception_count=0
```

この script は今後 `declarative-multipanel` の runtime 変更後に必ず実行する smoke として扱います。

## v12 aaos-scalable-ui-specs baseline 評価

ユーザー指定の `/home/y-fuk/work/android-automotiveos15-lts3/aaos-scalable-ui-specs` を正として、固定 3 panel の Home workspace、user slot への app routing、workspace page / resize / swap event、layout edit overlay、camera override を smoke 化して評価しました。

build:

```text
module build: pass
emu_img_zip: pass
saved image: /mnt/f/aaos_images/declarative-multipanel/sdk-repo-linux-system-images.zip
extracted image: /mnt/f/aaos_images/declarative-multipanel/extracted/x86_64
sha256: 4e1a8179ad17244ac26466daac900a409d19dcb044a09cd73f490b23d4dd79fd
```

runtime:

```text
AVD: Y-Fuk-dynamic-workspace-clean2
serial: emulator-5564
host emulator: Windows SDK emulator
artifact: /tmp/aaos-spec-workspace-smoke-20260609-163618
report: /tmp/aaos-spec-workspace-smoke-20260609-163618/report.md
```

smoke result:

```text
- [PASS] StubCarLauncher is installed under system_ext
- [PASS] SystemUI ScalableUI overlay is enabled
- [PASS] Framework ScalableUI overlay is enabled
- [PASS] CarService PoC overlay is enabled
- [PASS] nav_panel activity is present
- [PASS] media_panel activity is present
- [PASS] user_slot_panel empty activity is present
- [PASS] user_slot_panel uses expected empty slot bounds
- [PASS] user slot empty hint is visible in screenshot 01-home
- [PASS] AppGrid carries user_slot_panel target
- [PASS] Calendar launches
- [PASS] Calendar is routed to user_slot_panel bounds
- [PASS] switch_workspace_page_2 changes nav_panel bounds
- [PASS] resize_panel_nav_wide changes nav_panel bounds
- [PASS] swap_panel_position_nav_media moves nav_panel to media position
- [PASS] layout edit overlay appears
- [PASS] camera override activity is present
- [PASS] camera override uses full display bounds
- [PASS] camera override activity remains restorable after exit
- [PASS] camera fullscreen is dismissed after exit
- [PASS] System Bar Apps button opens fullscreen AppGrid
- [PASS] SystemUI process stayed alive
- [PASS] StubCarLauncher process stayed alive
- [PASS] No recent FATAL EXCEPTION in logcat tail
```

追加で確認したこと:

- `CalledFromWrongThreadException`
- `Accessibility content change on non-UI thread`
- `FATAL EXCEPTION`

上記はいずれも runtime logcat から検出されませんでした。

### v12 で入れた安定化

`layout_edit` は `edit_overlay_panel` だけを変える DecorPanel-only transition です。AAOS15 LTS3 の `PanelTransaction.Builder` は window change を true として扱うため、従来のままだと WM transition 経由に入り、TaskPanel を含まない transition が表面更新されず overlay が見えませんでした。

対応:

- `PanelTransitionCoordinator` で TaskPanel root stack を含む transition だけ WM transition に流す
- DecorPanel-only transition は shell main executor 上で直接 `updatePanelSurface()` する
- AutoDecor 未生成の場合は `reset()` 後にもう一度 main executor へ enqueue し、view 生成後に variant を適用する

また `DecorPanel.updateInternal()` で `setAlpha()` だけが UI thread 外から直接呼ばれていたため、visibility と同じく `post()` 内に移動しました。

`camera_override` では `camera_priority_panel` を fullscreen high-layer に出し、workspace panel 自体は hidden にしない構成へ寄せました。workspace panel を隠すと empty panel event が発火し、Home event により復帰後の workspace が黒く見えるためです。PoC では camera を workspace の上に被せ、解除時に camera panel だけ hidden に戻す方式を採用します。

### v12 patch 同期

評価済みの AAOS 差分は以下へ同期済みです。

```text
variants/declarative-multipanel/patches/device-generic-car/0001-add-sdk_car_scalableui_declarative_multipanel_x86_64-product.patch
variants/declarative-multipanel/patches/packages-services-Car/0001-add-scalableui-declarative-multipanel-rro.patch
variants/declarative-multipanel/patches/packages-apps-Car-SystemUI/0001-add-scalableui-declarative-multipanel-runtime-routing.patch
```

### v12 時点のスコープ判定

Pass と言える範囲:

- `aaos-scalable-ui-specs` の初期 workspace を ScalableUI RRO で構成する
- StubCarLauncher により標準 Launcher と HMI を分離する
- panel id / event id を spec に沿わせる
- user slot へ AppGrid から選んだ app を routing する
- workspace page / resize / swap / layout edit / camera override を event と panel transition として評価する
- Windows host emulator で build image から起動評価する

まだ別 phase として扱うべき範囲:

- 任意 panel 追加 / 削除
- 完全自由な panel drag / reorder
- grip の連続 resize
- 任意 app assignment の永続化
- reverse gear / real camera signal 連携
- focus mode の完成
