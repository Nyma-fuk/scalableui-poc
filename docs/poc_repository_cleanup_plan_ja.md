# ScalableUI PoC Repository 整理計画

## 目的

ScalableUI そのものの情報、現行 PoC、Android17 移植、過去実験、generated idea が混在している状態を整理する。

方針は「正しい情報を消さず、現行作業で参照すべきものを明確にする」ことである。

## 現在の分類

| 区分 | 主な場所 | 扱い |
| --- | --- | --- |
| ScalableUI source verification | `docs/aosp_source_verification_ja.md`, `docs/aaos17_scalableui_source_verification_ja.md` | source 事実の基準 |
| Active PoC | `variants/declarative-multipanel/` | 現行 baseline |
| Android17 porting | `docs/aaos17_*`, `scripts/aaos17_scalableui_build_action.sh` | 標準 AAOS17 target への移植手順 |
| Historical patches | `patches/`, `common/patches/` | 過去実装。削除せず分類する |
| Historical variants | `dynamic-workspace`, `editable-home`, `widget-workspace`, `widget-layout-lab`, `no-grip` | 実験記録として保持 |
| Generated ideas | `fixed-3zone` など | HMI 案として保持。再利用時は再検証 |
| Wiki | `wiki/` | 現行読み方とカスタマイズ入口 |

## 整理ステップ

### Step 1: ラベル付け

完了条件:

- `README.md` が情報区分を示す
- `docs/README_ja.md` が docs の読み方を示す
- `variants/README.md` が variant status を示す
- `patches/README.md` と `common/README.md` が historical 扱いを示す
- wiki が現行 baseline / Android17 方針に更新される

### Step 2: Active baseline の同期

対象:

- `variants/declarative-multipanel/README.md`
- `variants/declarative-multipanel/docs/hmi_spec_ja.md`
- `variants/declarative-multipanel/patches/`
- Android17 workspace の `packages/services/Car/car_product/scalableui_declarative_multipanel`

完了条件:

- AAOS15 / Android17 の差分を docs で分けて説明できる
- Android17 では標準 `sdk_car_x86_64` target を正とする
- module build / image build / emulator smoke の証跡が残る

### Step 3: Historical 情報の棚卸し

対象:

- root `patches/`
- `common/patches/`
- historical variants
- generated variants

やること:

- 消さない
- active baseline と混ぜない
- source 未検証の記述は historical / generated と明記する
- 再利用候補だけを issue / TODO として切り出す

### Step 4: Runtime custom phase の分離

ScalableUI 標準の外側にあるものを別 phase として管理する。

例:

- runtime panel add/delete
- arbitrary app assignment
- assignment persistence
- continuous grip resize
- existing task maximize
- Home restore
- telemetry

これらは `declarative-multipanel` の標準 RRO baseline と混ぜず、SystemUI controller / event / app bridge の custom phase として扱う。

## 削除しないもの

以下は古くても削除しない。

- 実機・emulator 評価記録
- build error と回避策
- source verification 結果
- historical variant の設計意図
- generated HMI idea

## 今後削除または移動を検討できるもの

実施前に必ず確認する。

- `scripts/__pycache__/`
- 重複した古い generated output
- active baseline から参照されない一時ファイル
- `backups/` の扱い

## 完了判定

- 初見の人が `README.md` -> `docs/README_ja.md` -> `variants/declarative-multipanel/README.md` の順に読めば現行作業に入れる。
- wiki から古い root grip/no-grip 前提へ誘導されない。
- Android17 作業で専用 product 作成に戻らない。
- ScalableUI 標準機能と PoC custom 実装が文書上で分離されている。
