# root PoC runtime-owner 整理と評価 2026-06-07

> Source verification: この文書は root PoC の runtime owner 評価記録です。AOSP source 上の正確な ScalableUI / WM / ATM 責務分担は [AOSP Source Verification](./aosp_source_verification_ja.md) を参照してください。

## 対象

- Product: `sdk_car_scalableui_x86_64`
- AVD: `Y-Fuk-root-grip-clean`
- image source: `F:\\aaos_images\\root-grip-fix\\x86_64`

## 今回の目的

1. RRO の先にある ScalableUI code path を整理する
2. root PoC の split state の source of truth を明確にする
3. root PoC をその理解に合わせて簡素化する
4. emulator で回帰確認する

## 実装方針

2026-06-07 時点の root PoC は、次の役割分担に揃えた。

- RRO
  - panel の存在
  - fixed app
  - fullscreen `app_panel`
  - fullscreen `panel_app_grid`
  - grip controller metadata
- runtime helper
  - width / height ratio の保持
  - safe area 考慮の bounds 計算
  - 3 task panel + 3 decor panel の runtime 更新

そのため、`map/calendar/radio/background/grip` の XML は `opened` 1 variant に簡素化した。
旧来の `w40_h35` のような行列は root PoC の source of truth ではないため削除した。

## 変更点

### RRO 側

- `map_panel.xml`
- `calendar_panel.xml`
- `radio_panel.xml`
- `decor_left_background_panel.xml`
- `decor_vertical_grip_panel.xml`
- `decor_horizontal_grip_panel.xml`

上記を単一 `opened` variant に整理。

### SystemUI 側

- `ScalableUiPocRuntimeLayoutController.java`

drag 中の更新を coalesce し、pending ratio の最新値にまとめて layout 適用するようにした。

## build

実行コマンド:

```bash
source build/envsetup.sh
lunch sdk_car_scalableui_x86_64-trunk_staging-userdebug
m -j10 CarSystemUI CarSystemUIScalableUiPocRRO emu_img_zip
```

結果:

- build 成功
- 出力: `out/target/product/emulator_car64_x86_64/sdk-repo-linux-system-images.zip`

## emulator 評価

### 初期表示

artifact:

- `/tmp/scalableui-rro-audit/home-initial.png`
- `/tmp/scalableui-rro-audit/home-dismissed.png`
- `/tmp/scalableui-rro-audit/visible-home-dismissed.txt`
- `/tmp/scalableui-rro-audit/panelstates-home-dismissed.txt`

確認:

- 左 `map`
- 右上 `calendar`
- 右下 `radio`
- 左右 grip
- 右上下 grip

が表示された。

`panelstates-home-dismissed.txt` では `map/calendar/radio/grip/background` が
すべて単一 variant 構成になっており、bounds は runtime helper により更新済み。

### vertical grip

artifact:

- `/tmp/scalableui-rro-audit/visible-width-wide.txt`
- `/tmp/scalableui-rro-audit/visible-width-narrow.txt`
- `/tmp/scalableui-rro-audit/visible-width-balanced.txt`
- `/tmp/scalableui-rro-audit/width-wide.png`
- `/tmp/scalableui-rro-audit/width-narrow.png`
- `/tmp/scalableui-rro-audit/width-balanced.png`

確認:

- `wide`
  - `decor_vertical_grip_panel`: `Rect(1128, 76 - 1176, 984)`
  - `map_panel`: `Rect(24, 100 - 1116, 960)`
- `narrow`
  - `decor_vertical_grip_panel`: `Rect(744, 76 - 792, 984)`
  - `map_panel`: `Rect(24, 100 - 732, 960)`
- `balanced`
  - `decor_vertical_grip_panel`: `Rect(936, 76 - 984, 984)`
  - `map_panel`: `Rect(24, 100 - 924, 960)`

結論:

- 反復操作で左右 split は再現できた
- XML の variant 行列を削っても挙動は維持された

### horizontal grip

artifact:

- `/tmp/scalableui-rro-audit/visible-height-tall.txt`
- `/tmp/scalableui-rro-audit/visible-height-compact.txt`
- `/tmp/scalableui-rro-audit/visible-height-balanced.txt`
- `/tmp/scalableui-rro-audit/height-tall.png`
- `/tmp/scalableui-rro-audit/height-compact.png`
- `/tmp/scalableui-rro-audit/height-balanced.png`

確認:

- `balanced`
  - `decor_horizontal_grip_panel`: `Rect(972, 642 - 1920, 690)`
  - `calendar_panel`: `Rect(972, 76 - 1920, 654)`
  - `radio_panel`: `Rect(972, 678 - 1920, 984)`

結論:

- 上下 split も反復操作で維持
- drag 中 update は coalesce により少し整理されたが、実アプリ relayout 起因の重さはまだ残る

### fullscreen app grid

artifact:

- `/tmp/scalableui-rro-audit/appgrid-fullscreen.png`
- `/tmp/scalableui-rro-audit/visible-appgrid.txt`

確認:

- `AppGridActivity` は fullscreen で表示された
- root PoC の固定 3 panel より前面に出る

### Settings launch

artifact:

- `/tmp/scalableui-rro-audit/settings-launch.png`
- `/tmp/scalableui-rro-audit/visible-settings.txt`
- `/tmp/scalableui-rro-audit/ui-settings.xml`

確認:

- `Settings_Launcher_Homepage` は `Rect(0, 0 - 1920, 1080)` の fullscreen window として前面に出る
- ただし screenshot 上は settings content の見え方がまだ不安定で、package 固有の task / UI 特性を完全には吸収できていない

## 結論

- root PoC を「RRO は fixed panel 定義、split state は runtime helper」が正の構造に整理できた
- XML の複雑な variant 行列を削っても、root PoC の主要機能は維持できた
- initial layout / grip repeated resize / fullscreen app grid は emulator で確認できた
- Settings まわりは fullscreen window としては前面化できているが、依然として package 固有挙動の詰め余地がある

## 次にやるなら

1. drag 中は preview だけ動かして task resize を `ACTION_UP` に寄せる
2. `Settings` のような特殊 package を fullscreen policy で個別吸収する
3. root PoC の理解を土台に、Phase 3 相当の app assignment を別 variant として育てる
