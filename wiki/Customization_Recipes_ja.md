# Customization Recipes

現行 `declarative-multipanel` baseline を前提にした変更レシピです。

## Recipe 1: 固定 panel の app を変える

触る場所:

- `config_default_activities`
- `strings.xml`
- 対象 panel XML の `role`

できること:

- map / media / settings など、起動時に panel へ出す app を変える
- 右上・右下など固定領域の役割を入れ替える

注意:

- app が狭い bounds に対応していない場合、panel 側だけでは UI 品質を保証できません。

## Recipe 2: All Apps を中央 floating panel にする

触る場所:

- `panel_app_grid.xml`
- layer 定義
- dismiss event
- AppGrid / SystemUI routing

確認すること:

- どの panel が存在しても前面に出る
- 背後の fullscreen app が消えない
- All Apps icon 再タップで閉じる
- panel 外タップで閉じる

XML だけで足りない場合は、outside tap を event に変換する controller / Activity / SystemUI bridge が必要です。

## Recipe 3: 通常 app を fullscreen-ish `app_panel` に出す

触る場所:

- `app_panel.xml`
- `PanelAutoTaskStackTransitionHandlerDelegate`
- app launch extra / routing policy

使う場面:

- 固定 panel に出ている map / calendar / settings をユーザーが再度起動した
- ユーザーがその app に集中操作したい

設計方針:

- 同じ app を多重起動しない
- 既存 task を再利用できるか確認する
- panel 最大化 / focus / Home 復帰をセットで設計する

## Recipe 4: Home 復帰で直前 layout を戻す

触る場所:

- transition event
- `PanelTransitionCoordinator`
- previous state store
- Home / Back handling

できること:

- app_panel 最大化前の panel 状態を保存する
- Home 操作で最大化 panel を元の位置へ戻す
- All Apps / overlay を閉じた状態へ戻す

注意:

- 直前状態の保存は PoC/custom 領域になりやすい。
- user switching、process death、SystemUI restart 後の復元も別途考える。

## Recipe 5: panel の split を固定で変える

触る場所:

- 対象 `*_panel.xml`
- `Bounds`
- `Layer`
- gap / margin `dimens`

例:

- map を 60%、右側を 40%
- 右 column を 35/65 に分割
- card 風に margin / corner を増やす

固定 layout だけなら RRO/XML で完結しやすいです。

## Recipe 6: grip resize を入れる

扱い:

- 現行 baseline の主目的ではない
- historical variant の知見は参照可能
- Android17 では `GripBarBase` / `HorizontalGripBar` / `VerticalGripBar` 構成を source で確認する

必要になるもの:

- decor panel
- controller
- drag event
- target panel transition
- drag 中 preview と drag end commit の設計

## Recipe 7: runtime panel 追加を試す

扱い:

- ScalableUI 標準だけでは完結しない
- `StateManager.addState(...)` は存在するが、UI / geometry / persistence は custom

必要になるもの:

- panel model
- panel ID 採番
- bounds 計算
- app picker
- persistence
- process death / SystemUI restart recovery

## Recipe 8: 新しい HMI 案を variant として残す

推奨:

1. まず docs に HMI 案を書く。
2. active baseline に入れるか、generated idea として残すか決める。
3. active にする場合だけ patch を整える。
4. Android17 では専用 product を増やさず、標準 target への差分として評価する。

variant の状態は [Variant Status](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/variant_status_ja.md) に追記します。

## Recipe 9: 対象環境へ渡す成果物を整える

渡すもの:

- HMI仕様
- RRO/XML patch
- SystemUI controller / event patch
- product makefile 差分
- build command
- emulator smoke evidence
- 未確認事項一覧

説明の軸:

- ScalableUI 標準でできること
- PoC custom として追加したこと
- 対象環境側で統合確認が必要なこと

## Recipe 10: 変更前チェック

最低限:

```bash
git status --short --branch
git diff --check
bash -n scripts/aaos17_scalableui_build_action.sh
```

runtime 変更なら module build、`emu_img_zip`、emulator smoke を追加します。
