# Android 16 QPR2 動作確認評価

## 対象

- AOSP branch: `android16-qpr2-release`
- product: `sdk_car_scalableui_declarative_multipanel_x86_64`
- lunch: `sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug`
- Android tree: `<ANDROID16_QPR2_ROOT>`
- emulator sysdir: `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\extracted\x86_64`

## 結果

評価: Correct / PoC 要求範囲の主要導線は動作確認済み

Android16 QPR2 の ScalableUI runtime に PoC patch を適用し、image build、
Windows emulator boot、初期 TaskPanel 表示、既存 AAOS AppGrid の centered floating
panel 表示、All Apps の close affordance、customizable slot 用 picker panel、
選択アプリの customizable slot 表示、既存 panel アプリ再起動時の fullscreen 化、
Home 復帰まで確認した。

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
  - `panel_app_grid` は layer 90、中央 bounds `16%,12%,84%,88%` で表示
  - `app_grid_scrim_panel` は layer 89、fullscreen transparent panel として背面に表示
  - `dumpsys activity activities` で `AppGridActivity` が `panel_app_grid` 配下であることを確認
  - `app_panel` は空のまま
  - All Apps アイコン再タップ相当の `ACTION_SHOW_PANEL` 再実行で `action=close` が発生し閉じる
  - AppGrid 外側 tap で `AppGridScrimActivity` が `close_app_grid` event を送信し閉じる
- customizable slot
  - `Choose app` で `com.android.car.carlauncher/.AppPickerActivity` を `app_picker_panel` に表示
  - Calendar 選択後、`com.android.calendar/.AllInOneActivity` が `user_slot_panel` 配下に表示
  - `app_picker_panel` は選択後に閉じ、`app_panel` は空のまま
- 既存 panel アプリの再起動
  - Calendar が `user_slot_panel` に存在する状態で All Apps から Calendar を再起動
  - `_System_TaskOpenEvent` は `panelId=user_slot_panel, source=app_grid` として dispatch
  - `user_slot_panel` は fullscreen variant へ遷移し、`nav_panel` / `media_panel` は画面外へ退避
  - Home 操作で `user_slot_panel` は元の右下位置に戻り、直前まで存在していた Calendar が復帰
- 右上 panel
  - `media_panel` は launcher のスタブではなく `com.android.car.media/.MediaDispatcherActivity`
    を表示

## 実装上の要点

- `system_bar_app_drawer_intent` は `PanelTriggerActivity` を起動する。
  `PanelTriggerActivity` 自体はすぐ終了し、target panel event だけを ScalableUI に渡す。
  `PanelAutoTaskStackTransitionHandlerDelegate` は `panel_app_grid` の可視状態に基づき
  `action=open` / `action=close` token を付ける。
- 実体の `AppGridActivity` は `panel_app_grid` の default activity として
  `TaskPanel.setBaseIntent()` / `ActivityOptions.setLaunchRootTask()` 経由で起動する。
- 外側 tap close は、`AppGridActivity` とは別の `app_grid_scrim_panel` に
  `AppGridScrimActivity` を置き、ScalableUI broadcast bridge に `close_app_grid`
  event を送ることで実現している。
- `Choose app` も同じ trigger 経路で `app_picker_panel` を開き、実体の
  `AppPickerActivity` は panel default activity として起動する。
- 選択されたアプリは `EmptySlotActivity` へブロードキャストで通知し、
  `user_slot_panel` 側から起動する。
- `user_slot_panel` には `<TaskBehavior newTaskLaunchPolicy="REPARENT_TO_SOURCE"/>`
  を設定し、`CarActivityManager.LAUNCH_BEHAVIOR_REPARENT_TO_SOURCE_ROOT_TASK`
  により選択アプリを同 root task へ配置する。

## 証跡

runtime log / dump / screenshot:

- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_appgrid_close_affordance\01_appgrid_open.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_appgrid_close_affordance\02_appgrid_closed_by_retrigger.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_appgrid_close_affordance\04_appgrid_closed_by_outside_tap.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\01_picker_open.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\02_calendar_in_user_slot.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\03_all_apps_open.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\04_calendar_fullscreen.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\05_home_restored.png`
- `<AAOS_IMAGE_ROOT>\android16-qpr2-declarative-multipanel\runtime_after_close_affordance_full_flow\summary.txt`

`dumpsys activity activities` で確認した root task:

```text
Task name=panel_app_grid  -> AppGridActivity
Task name=app_grid_scrim_panel -> AppGridScrimActivity
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

All Apps close 時の logcat:

```text
StateManager: handleEvent Event{mId='_System_TaskOpenEvent' mTokens='action=close , panelId=panel_app_grid ...}
ScalableUIWMInitializer: Dispatch ScalableUI panel event: close_app_grid
```

All Apps から既存 panel アプリを再起動した時の logcat:

```text
StateManager: handleEvent Event{mId='_System_TaskOpenEvent' mTokens='panelId=user_slot_panel , component=com.android.calendar/com.android.calendar.AllInOneActivity , source=app_grid' ...}
```

## 残課題

- picker の UI は PoC 独自実装。量産では既存 launcher UX / rotary / DUX 制約に合わせる必要がある。
- 選択アプリの永続化は launcher shared preferences。multi-user、user switching、
  app uninstall、process death 後の復元は追加検証が必要。
- `TaskPanel is null` ログは child task 通知タイミングで出るが、最終 window / root task
  配置は成立している。量産向けにはログ抑制または null 判定整理が必要。
- focus、rotary、input capture、multi-display、back stack、task persistence は別途評価が必要。
