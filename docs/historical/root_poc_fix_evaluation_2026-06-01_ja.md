# root PoC 修正評価メモ 2026-06-01

> Source verification: この文書は 2026-06-01 時点の runtime 評価記録です。AOSP source 上の責務分担と未確認事項は [AOSP Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aosp_source_verification_ja.md) を参照してください。

## 対象

- Product: `sdk_car_scalableui_x86_64`
- AVD: `Y-Fuk-root-grip-clean`
- image source: `F:\\aaos_images\\root-grip-fix\\x86_64`

## 今回の修正観点

1. `decor_vertical_grip_panel` が 1 回だけでなく反復して左右 resize できること
2. `decor_horizontal_grip_panel` の drag が極端に重くならず、現 grip 位置から再操作できること
3. top / bottom system bar と panel が重ならないこと
4. `Settings` を launcher icon 相当の launch で起動したときに fullscreen 前面へ出ること
5. 今後も emulator 評価を必須にする workflow / skill の整備

## 結果サマリ

| 項目 | 結果 | 要点 |
| --- | --- | --- |
| system bar overlap 解消 | 合格 | `TopCarSystemBar` / `BottomCarSystemBar` を避けた bounds を確認 |
| vertical grip repeated swipe | 合格 | `balanced -> wide -> narrow -> balanced` を emulator 上で再現 |
| horizontal grip repeated swipe | 合格 | 現 grip 位置を起点に `balanced -> tall -> compact` を再現 |
| Settings launch behind-home 解消 | 合格 | `Settings_Launcher_Homepage` の実 UI が fullscreen 前面表示されることを screenshot / UI dump / visible windows で確認 |
| Settings task の panel routing 純度 | 留意 | task 自体は `FallbackHome` を root に持つ `type=home` のまま |

## 証跡

### 初期表示

- screenshot: `<EVIDENCE_DIR>/scalableui-fix-eval/home-initial.png`
- dismiss 後: `<EVIDENCE_DIR>/scalableui-fix-eval/home-after-dismiss.png`
- visible windows: `<EVIDENCE_DIR>/scalableui-fix-eval/visible-after-dismiss.txt`

確認できた代表 frame:

- `TopCarSystemBar`: `Rect(0, 0 - 1920, 76)`
- `BottomCarSystemBar`: `Rect(0, 984 - 1920, 1080)`
- `decor_left_background_panel`: `Rect(0, 76 - 960, 984)`
- `map_panel`: `Rect(24, 100 - 924, 960)`
- `decor_vertical_grip_panel`: `Rect(936, 76 - 984, 984)`
- `calendar_panel`: `Rect(972, 76 - 1920, 518)`
- `radio_panel`: `Rect(972, 542 - 1920, 984)`

評価:

- bar は ScalableUI panel ではなく通常の CarSystemUI window
- root PoC panel はその内側の content area に収まり、以前のような top / bottom overlap は解消した

### vertical grip repeated swipe

- artifact dir: `<EVIDENCE_DIR>/scalableui-regress/v2/`
- visible windows:
  - `visible-width-1.txt`
  - `visible-width-2.txt`
  - `visible-width-3.txt`
- logcat:
  - `log-width.txt`

確認できた代表 frame:

- `visible-width-1.txt`
  - `decor_vertical_grip_panel`: `Rect(1076, 76 - 1124, 984)`
  - `map_panel`: `Rect(24, 100 - 1064, 960)`
- `visible-width-2.txt`
  - `decor_vertical_grip_panel`: `Rect(744, 76 - 792, 984)`
  - `map_panel`: `Rect(24, 100 - 732, 960)`
- `visible-width-3.txt`
  - `decor_vertical_grip_panel`: `Rect(936, 76 - 984, 984)`
  - `map_panel`: `Rect(24, 100 - 924, 960)`

評価:

- 旧 build の根本原因は `BreakPoint point="40%"` が縦 grip でも高さ基準で解釈されていたこと
- 修正後は `balanced -> wide -> narrow -> balanced` を再現できた
- `log-width.txt` でも `widthRatio=0.6 -> 0.4 -> 0.50025976` と連続更新を確認できた

### horizontal grip repeated swipe

- artifact dir: `<EVIDENCE_DIR>/scalableui-regress/v2/`
- visible windows:
  - `visible-height-7.txt`
  - `visible-height-9.txt`
- logcat:
  - `log-height.txt`
  - `log-height-3.txt`

確認できた代表 frame:

- `visible-height-7.txt`
  - `decor_horizontal_grip_panel`: `Rect(780, 642 - 1920, 690)`
  - `calendar_panel`: `Rect(780, 76 - 1920, 654)`
  - `radio_panel`: `Rect(780, 678 - 1920, 984)`
- `visible-height-9.txt`
  - `decor_horizontal_grip_panel`: `Rect(780, 370 - 1920, 418)`
  - `calendar_panel`: `Rect(780, 76 - 1920, 382)`
  - `radio_panel`: `Rect(780, 406 - 1920, 984)`

評価:

- 旧 build の重さは、`dragDecreaseEventId` / `dragIncreaseEventId` が `EventId` と同じで、1 move あたり同じ drag event を二重送信していたことが一因
- 修正後は drag event の二重発火を止め、runtime controller でも同値 ratio 再適用を抑止した
- emulator 上で current grip の中心から drag すれば `balanced -> tall -> compact` を再現できた

### Settings launch

- screenshot: `<EVIDENCE_DIR>/scalableui-regress/v2/settings-launch.png`
- UI dump: `<EVIDENCE_DIR>/scalableui-regress/v2/ui-settings.xml`
- visible windows: `<EVIDENCE_DIR>/scalableui-regress/v2/visible-settings.txt`
- top dump: `<EVIDENCE_DIR>/scalableui-regress/v2/activity-top-settings.txt`

再現コマンド:

```bash
adb shell am start \
  -a android.intent.action.MAIN \
  -c android.intent.category.LAUNCHER \
  -n com.android.car.settings/.Settings_Launcher_Homepage \
  --ez com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL true
```

確認できた状態:

- screenshot と `ui-settings.xml` の両方で `com.android.car.settings` の fullscreen UI を確認
- `Connected devices` toolbar や Settings の recycler content が UI dump に出ている
- `visible-settings.txt` では `Window{... Settings_Launcher_Homepage}` が `Rect(0, 0 - 1920, 1080)` で最前面

評価:

- 以前の「Home の後ろに出る」状態は解消した
- 旧評価では `dumpsys` の focus 状態だけで合格扱いしてしまっていたが、今回の再評価では実 UI 表示を確認した
- ただし task 自体は `FallbackHome` を root に持つ `type=home` task のまま
- これは `Settings` package の manifest / launchMode 由来で、ScalableUI 側で fullscreen 前面化はできても task type の意味づけまでは完全には変えられない

## 結論

- root PoC の safe area は改善できた
- vertical grip の再操作不能は修正できた
- horizontal grip の drag は軽量化でき、current grip 位置からの反復操作も通った
- Settings launch は behind-home を解消できた
- 一方で `FallbackHome` root task を完全に `app_panel` 的な task へ変換しているわけではないため、「ScalableUI 標準 routing だけで task type まで理想形にする」のは限界がある

## 実装上の整理

ScalableUI だけでできること:

- fixed panel の構成
- fullscreen launch-root panel の用意
- event による panel transition
- panel 内 task placement の土台
- grip event をきっかけにした bounds 更新

注記: AOSP の `WindowContainerTransaction.reparent(...)` は存在しますが、現在の live ScalableUI source だけでは Panel 間既存 task reparent を標準機能として確認していません。reparent は PoC custom / custom policy として再検証してください。

custom 実装が必要だったこと:

- root PoC 専用 runtime layout 補助
- system bar safe area を使った deterministic bounds 更新
- `HOME category` を持つ task の誤判定回避
- grip breakpoint の軸解釈修正
- drag event 二重発火の抑止
- emulator 評価を前提にした運用ルール化
