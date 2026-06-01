# ScalableUI Phase 評価メモ 2026-05-31

注記:

- この時点では `Phase 2` の root PoC は「部分合格」だった
- 2026-06-01 の追加修正と再評価結果は [root_poc_fix_evaluation_2026-06-01_ja.md](/home/y-fuk/work/android-automotiveos15-lts3/workdir/scalableui-poc/docs/root_poc_fix_evaluation_2026-06-01_ja.md) を参照

## 目的

ScalableUI PoC を次の 3 phase に分けて、Windows emulator 上で実機相当の挙動を確認した。

- Phase 1: 固定 panel 構成で app を panel に表示する
- Phase 2: grip により panel size を変えられるようにする
- Phase 3: ユーザーが任意 panel に任意 app を表示できるようにする

## 評価サマリ

| Phase | 対象 | 結果 | 要点 |
| --- | --- | --- | --- |
| Phase 1 | `fixed-3zone` | 合格 | 3 panel 表示と fullscreen All Apps を確認 |
| Phase 2 | `sdk_car_scalableui_x86_64` | 部分合格 | 初期 HMI と grip panel の存在は確認。emulator 自動操作では size 変更を再現できず |
| Phase 3 | `widget-workspace` | 合格 | Panel Control menu の表示と panel assignment UI を確認 |

## Phase 1

### 対象

- Product: `sdk_car_scalableui_fixed_3zone_x86_64`
- AVD: `Y-Fuk-fixed-3zone-clean`

### 確認したこと

- boot 完了
- `ro.product.name=sdk_car_scalableui_fixed_3zone_x86_64`
- 左 `map`、右上 `calendar`、右下 `radio` の 3 panel が同時表示される
- `All apps` を起動すると fullscreen `app_panel` 相当で全面表示される

### 画面証跡

- 初期表示: `/tmp/scalableui-phase-eval/phase1/home.png`
- notice dismiss 後: `/tmp/scalableui-phase-eval/phase1/after-dismiss.png`
- All Apps fullscreen: `/tmp/scalableui-phase-eval/phase1/all-apps.png`

### dumpsys 証跡

- `/tmp/scalableui-phase-eval/phase1/activities-after-dismiss.txt`
- `/tmp/scalableui-phase-eval/phase1/visible-apps.txt`
- `/tmp/scalableui-phase-eval/phase1/activities-all-apps.txt`
- `/tmp/scalableui-phase-eval/phase1/visible-all-apps.txt`

### 補足

- `initial user notice` dialog が毎回前面に出るので、評価時は dismiss が必要
- `visible-apps` では次の frame を確認した
  - map: `Rect(38, 32 - 1113, 1047)`
  - calendar: `Rect(1152, 32 - 1881, 518)`
  - radio: `Rect(1152, 561 - 1881, 1047)`

## Phase 2

### 対象

- Product: `sdk_car_scalableui_x86_64`
- AVD: `Y-Fuk-root-grip-clean`

### 確認したこと

- boot 完了
- `ro.product.name=sdk_car_scalableui_x86_64`
- 左 background + floated map、右上 `calendar`、右下 `radio` の初期 HMI を確認
- `decor_vertical_grip_panel` と `decor_horizontal_grip_panel` が visible window として存在することを確認

### 画面証跡

- 初期表示: `/tmp/scalableui-phase-eval/phase2/home.png`
- notice dismiss 後: `/tmp/scalableui-phase-eval/phase2/after-dismiss.png`
- `adb input swipe` 後: `/tmp/scalableui-phase-eval/phase2/after-vertical-drag.png`
- event broadcast 後: `/tmp/scalableui-phase-eval/phase2/after-width-event.png`

### dumpsys 証跡

- `/tmp/scalableui-phase-eval/phase2/visible-home.txt`
- `/tmp/scalableui-phase-eval/phase2/visible-after-dismiss.txt`
- `/tmp/scalableui-phase-eval/phase2/visible-after-vertical-drag.txt`
- `/tmp/scalableui-phase-eval/phase2/visible-after-width-event.txt`

### 確認できた frame

- vertical grip: `Rect(936, 0 - 984, 1080)`
- horizontal grip: `Rect(972, 516 - 1920, 564)`
- map: `Rect(24, 24 - 924, 1056)`
- calendar: `Rect(972, 0 - 1920, 528)`
- radio: `Rect(972, 552 - 1920, 1080)`

### 評価

- ScalableUI 上に grip panel 自体は正しく出ている
- ただし今回の emulator 自動操作では、
  - `adb input swipe` による drag
  - `ACTION_PANEL_EVENT` broadcast による `layout_width_left_wide`
  のどちらでも frame 変化を確認できなかった

### 現時点の解釈

- 「grip を持つ panel 構成」は成立している
- ただし「emulator 上で size 変更を確実に再現する操作経路」は未解決
- 次に詰めるべき点は次のどちらか
  - `GripBarViewController` が emulator の `input swipe` を拾えていない
  - `ACTION_PANEL_EVENT` の generic broadcast 経路では root PoC の layout event が実行されていない

## Phase 3

### 対象

- Product: `sdk_car_scalableui_widget_workspace_x86_64`
- AVD: `Y-Fuk-widget-workspace-clean`

### 確認したこと

- boot 完了
- `ro.product.name=sdk_car_scalableui_widget_workspace_x86_64`
- `Panel Control` button から hidden menu を開ける
- menu 上で
  - target panel
  - app to show
  を選ぶ UI が表示される

### 画面証跡

- 初期表示: `/tmp/scalableui-phase-eval/phase3/home.png`
- notice 表示中: `/tmp/scalableui-phase-eval/phase3/panel-control-open.png`
- Panel Control menu: `/tmp/scalableui-phase-eval/phase3/panel-menu.png`
- app selection 実行後: `/tmp/scalableui-phase-eval/phase3/after-assignment.png`

### dumpsys 証跡

- `/tmp/scalableui-phase-eval/phase3/activities-home.txt`
- `/tmp/scalableui-phase-eval/phase3/activities-panel-control.txt`
- `/tmp/scalableui-phase-eval/phase3/activities-panel-menu.txt`
- `/tmp/scalableui-phase-eval/phase3/activities-after-assignment.txt`

### 評価

- menu-driven な panel assignment という意味では成立
- `Panel Control` menu 自体は明確に確認できた
- 画面上は assignment 後に bottom-left panel の見え方が変化した
- ただし `activities-after-assignment.txt` だけでは target panel 上の task 移動が完全には追い切れていないため、厳密には「UI 上は確認、task 再配置の最終証明は追加確認余地あり」として扱う

## 総括

- Phase 1 は、ScalableUI で panel 構成を作り、app を各 panel に出すという最小機能として成立した
- Phase 3 は、PoC として「ユーザーが panel を選び app を差し替える」入口まで成立した
- いちばん詰めるべきは Phase 2 で、grip による size 変更を emulator 上で確実に再現できるようにすること

## 次の優先作業

1. `GripBarViewController` の input 経路をログ付きで追い、`adb input swipe` が届いているか確認する
2. `ACTION_PANEL_EVENT` から `layout_width_left_wide` が `EventDispatcher` に届き、`StateManager` で処理されているか確認する
3. Phase 2 が安定したら、Phase 3 の assignment 後 task 再配置を `dumpsys activity containers` まで含めて再確認する
