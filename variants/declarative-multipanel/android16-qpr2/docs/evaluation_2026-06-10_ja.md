# Android 16 QPR2 動作確認評価

## 対象

- AOSP branch: `android16-qpr2-release`
- product: `sdk_car_scalableui_declarative_multipanel_x86_64`
- lunch: `sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug`
- Android tree: `/home/y-fuk/work/android16-qpr2-release`
- emulator sysdir: `F:\aaos_images\android16-qpr2-declarative-multipanel\extracted\x86_64`

## 結果

評価: Partially Correct / PoCとして起動・表示・基本操作は可

Android16 QPR2 の ScalableUI runtime に PoC patch を適用し、image build、
emulator boot、初期TaskPanel表示、AppGrid起動まで確認した。

本格適用には、AppGridのtarget panel指定、task migration/reparent時のfocus、
multi-user、process death、永続化、失敗時relaunch policyの追加検証が必要。

## 確認済み

- `m -j8 ScalableUiDeclarativeMultipanelStubCarLauncher CarSystemUIScalableUiDeclarativeMultipanelRRO CarFrameworkScalableUiDeclarativeMultipanelRRO CarServiceScalableUiDeclarativeMultipanelRRO CarSystemUI`
  - 成功
- `m -j4 emu_img_zip`
  - 成功
  - artifact: `out/target/product/emulator_car64_x86_64/sdk-repo-linux-system-images.zip`
- emulator boot
  - `ro.product.name=sdk_car_scalableui_declarative_multipanel_x86_64`
  - `sys.boot_completed=1`
- overlay
  - `[x] android.car.config.rro.scalableui.declarative.multipanel`
  - `[x] com.android.systemui.rro.scalableui.declarative.multipanel`
  - `[x] com.android.car.resources.scalableui.declarative.multipanel`
- 初期表示
  - `nav_panel`: `com.android.car.mapsplaceholder/.MapsPlaceholderActivity`
  - `media_panel`: `com.android.car.carlauncher/.ControlBarActivity`
  - `user_slot_panel`: `com.android.car.carlauncher/.EmptySlotActivity`
- 操作確認
  - 下部AppGridボタンtapで `com.android.car.carlauncher/.AppGridActivity` が起動
  - `app_panel` root task上でfullscreen表示

## 修正内容

初回起動では中央領域が黒く、logcat に以下が出ていた。

```text
XmlModelLoader: org.xmlpull.v1.XmlPullParserException: Unrecognized tag at the beginning: Panel
```

AOSP側の根拠:

- `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/loader/xml/PanelStateXmlParser.java`
  - `parse()` は `DecorPanel` / `TaskPanel` だけを受け付ける
- `packages/apps/Car/systemlibs/car-scalable-ui-lib/src/com/android/car/scalableui/loader/xml/PanelTagXmlParser.java`
  - `TASK_PANEL_TAG = "TaskPanel"`
  - `DECOR_PANEL_TAG = "DecorPanel"`
  - `parsePanel()` は `PanelType.TASK` / `PanelType.DECOR` を生成する

対応:

- Activity componentをroleに持つXMLを `<TaskPanel>` へ変更
- `@layout/...` をroleに持つXMLを `<DecorPanel>` へ変更
- `bool/config_enableScalableUI` overlayを `bool/scalable_ui` へ変更

## 証跡

runtime log / dump / screenshot:

- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_xml_fix\logcat-all.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_xml_fix\dumpsys_activity.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_xml_fix\dumpsys_window.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_xml_fix\scalableui-home-after-fix.png`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_xml_fix\scalableui-appgrid-after-tap.png`

`dumpsys activity activities` で確認したroot task:

```text
Task name=nav_panel        -> MapsPlaceholderActivity
Task name=media_panel      -> ControlBarActivity
Task name=user_slot_panel  -> EmptySlotActivity
Task name=app_panel        -> AppGridActivity after app grid tap
```

`dumpsys window windows` で確認したwindow frame:

```text
MapsPlaceholderActivity frame=(38,53)-(1113,1026)
ControlBarActivity      frame=(1152,53)-(1881,507)
EmptySlotActivity       frame=(1152,572)-(1881,1026)
```

## 残課題

- AppGridを `panel_app_grid` に出すか、fullscreen `app_panel` に出すかの仕様確定
- `TaskPanel is null` ログの扱い整理
  - 起動中のchild task通知タイミングで出ているが、最終window表示は成立している
- user switching時のpanel task再生成
- process death後のstub activity restart
- focus / rotary / input capture
- multi-display構成
- task persistenceとdefault activity復元
