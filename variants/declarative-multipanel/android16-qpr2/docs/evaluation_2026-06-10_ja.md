# Android 16 QPR2 動作確認評価

## 対象

- AOSP branch: `android16-qpr2-release`
- product: `sdk_car_scalableui_declarative_multipanel_x86_64`
- lunch: `sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug`
- Android tree: `/home/y-fuk/work/android16-qpr2-release`
- emulator sysdir: `F:\aaos_images\android16-qpr2-declarative-multipanel\extracted\x86_64`

## 結果

評価: Correct / PoC 要求範囲の主要導線は動作確認済み

Android16 QPR2 の ScalableUI runtime に PoC patch を適用し、image build、
Windows emulator boot、初期 TaskPanel 表示、既存 AAOS AppGrid の floating panel
表示、customizable slot 用 picker panel、選択アプリの customizable slot 表示まで確認した。

## 確認済み

- `m -j8 ScalableUiDeclarativeMultipanelStubCarLauncher CarSystemUIScalableUiDeclarativeMultipanelRRO CarSystemUI`
  - 成功
- `m -j4 emu_img_zip`
  - 成功
  - artifact: `out/target/product/emulator_car64_x86_64/sdk-repo-linux-system-images.zip`
- emulator boot
  - `sys.boot_completed=1`
  - `system_server`, `com.android.systemui`, `com.android.car.carlauncher` 起動確認
- 初期表示
  - `nav_panel`: `com.android.car.mapsplaceholder/.MapsPlaceholderActivity`
  - `media_panel`: `com.android.car.media/.MediaDispatcherActivity`
  - `user_slot_panel`: `com.android.car.carlauncher/.EmptySlotActivity`
- All Apps
  - 下部 All Apps ボタンで既存 AAOS `com.android.car.carlauncher/.AppGridActivity` を表示
  - `dumpsys activity activities` で `AppGridActivity` が `panel_app_grid` 配下であることを確認
  - `app_panel` は空のまま
- customizable slot
  - `Choose app` で `com.android.car.carlauncher/.AppPickerActivity` を `app_picker_panel` に表示
  - Calendar 選択後、`com.android.calendar/.AllInOneActivity` が `user_slot_panel` 配下に表示
  - `app_picker_panel` は選択後に閉じ、`app_panel` は空のまま
- 右上 panel
  - `media_panel` は launcher のスタブではなく `com.android.car.media/.MediaDispatcherActivity`
    を表示

## 実装上の要点

- `system_bar_app_drawer_intent` は `PanelTriggerActivity` を起動する。
  `PanelTriggerActivity` 自体はすぐ終了し、target panel event だけを ScalableUI に渡す。
- 実体の `AppGridActivity` は `panel_app_grid` の default activity として
  `TaskPanel.setBaseIntent()` / `ActivityOptions.setLaunchRootTask()` 経由で起動する。
- `Choose app` も同じ trigger 経路で `app_picker_panel` を開き、実体の
  `AppPickerActivity` は panel default activity として起動する。
- 選択されたアプリは `EmptySlotActivity` へブロードキャストで通知し、
  `user_slot_panel` 側から起動する。
- `user_slot_panel` には `<TaskBehavior newTaskLaunchPolicy="REPARENT_TO_SOURCE"/>`
  を設定し、`CarActivityManager.LAUNCH_BEHAVIOR_REPARENT_TO_SOURCE_ROOT_TASK`
  により選択アプリを同 root task へ配置する。

## 証跡

runtime log / dump / screenshot:

- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\initial-home.png`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\floating-all-apps.png`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\app-picker-panel-retry.png`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\selected-user-slot.png`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\dumpsys-activities-all-apps.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\dumpsys-activities-picker-retry.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\dumpsys-activities-selected.txt`
- `F:\aaos_images\android16-qpr2-declarative-multipanel\runtime_after_panel_trigger_fix\logcat-selected-full.txt`

`dumpsys activity activities` で確認した root task:

```text
Task name=panel_app_grid  -> AppGridActivity
Task name=app_picker_panel -> AppPickerActivity
Task name=user_slot_panel -> EmptySlotActivity + Calendar AllInOneActivity
Task name=app_panel       -> empty after these flows
```

選択アプリ配置時の logcat:

```text
CarLaunchParamsModifierUpdatableImpl: Applying root task behavior, preferred root task=Task{... name=user_slot_panel ...}
ActivityTaskManager: START ... cmp=com.android.calendar/.AllInOneActivity ...
StateManager: handleEvent Event{mId='_System_TaskOpenEvent' mTokens='panelId=user_slot_panel , component=com.android.calendar/com.android.calendar.AllInOneActivity' ...}
```

## 残課題

- picker の UI は PoC 独自実装。量産では既存 launcher UX / rotary / DUX 制約に合わせる必要がある。
- 選択アプリの永続化は launcher shared preferences。multi-user、user switching、
  app uninstall、process death 後の復元は追加検証が必要。
- `TaskPanel is null` ログは child task 通知タイミングで出るが、最終 window / root task
  配置は成立している。量産向けにはログ抑制または null 判定整理が必要。
- focus、rotary、input capture、multi-display、back stack、task persistence は別途評価が必要。
