# ScalableUI PoC Docs Index

この `docs/` 配下は、ScalableUI の source 照合、AAOS17 移植、PoC 作業手順、過去実験ログを用途別に分けている。

まず読む順番:

1. `verification/`
2. `architecture/`
3. `android17/`
4. `workflows/`
5. `historical/`

## Directory Map

| ディレクトリ | 役割 | 読むと理解できること | できるようになること |
| --- | --- | --- | --- |
| [verification](verification/README.md) | AAOS/AOSP source を正とした照合結果 | ScalableUI の実装事実、docs の正誤、Android17 で確認済みのクラス/メソッド | 推測ではなく source 根拠で設計判断できる |
| [architecture](architecture/README.md) | ScalableUI / WM / ATM / app layer の責務整理 | Panel、TaskPanel、StateManager、Task routing、Launcher との関係 | 「Panel に app が出る」流れを正しく説明できる |
| [android17](android17/README.md) | Android17 移植と差分調査 | Android15/16 系から Android17 へ移すときの差分、build 方針、As-Is 検証 | 標準 AAOS17 emulator target に PoC 差分を段階適用できる |
| [workflows](workflows/README.md) | 実装・整理・検証の作業手順 | repo 整理、variant 管理、runtime panel 検討、AI 実装時の注意 | 作業を小さく分け、patch/docs/evidence を同期できる |
| [historical](historical/README.md) | 過去 PoC / 実験 / 評価ログ | dynamic workspace、editable home、widget 系の試行錯誤と評価結果 | 過去の正しい知見を拾いつつ、現行 baseline と混ぜずに扱える |

## Current Baseline

現行 baseline は `variants/declarative-multipanel`。

重要な前提:

- ScalableUI の正はこの repo の docs ではなく AAOS/AOSP source code。
- Android17 では PoC 専用 product を増やさず、標準 `sdk_car_x86_64-trunk_staging-userdebug` に PoC 差分を載せる。
- `dynamic-workspace`、`editable-home`、`widget-workspace`、generated variant suite は historical / experimental。
- 「Panel に Activity を直接表示する」と説明しない。実装上は `Panel -> TaskPanel -> RootTaskStack / Task -> Activity`。
- runtime panel 生成、任意 app assignment、persistence、drag resize は ScalableUI 標準だけでは完結しない。

## Shared Wording

この repo は個人検証・技術調査の形で読めるように、特定の相手先や勤務文脈を想起させる語を避ける。

共有用ドキュメントでは以下の placeholder を使う。

| 目的 | 表記 |
| --- | --- |
| Android checkout root | `<AAOS17_ROOT>` |
| この repository の checkout root | `<SCALABLEUI_POC_ROOT>` |
| emulator image 出力先 | `<AAOS_IMAGE_ROOT>` |
| adb binary | `<ADB_BIN>` |
| adb serial | `<DEVICE_SERIAL>` |
| 検証証跡の保存先 | `<EVIDENCE_DIR>` |

## Key Documents

| 文書 | 何が理解できるか | 何ができるようになるか |
| --- | --- | --- |
| [verification/aosp_source_verification_ja.md](verification/aosp_source_verification_ja.md) | docs の主張を AAOS/AOSP source で照合した結果 | ScalableUI 標準機能と PoC/custom 実装を切り分けられる |
| [verification/aaos17_scalableui_source_verification_ja.md](verification/aaos17_scalableui_source_verification_ja.md) | Android17 source 上の ScalableUI 実装 | Android17 前提で Panel / TaskPanel / StateManager を説明できる |
| [architecture/scalableui_window_manager_flow_ja.md](architecture/scalableui_window_manager_flow_ja.md) | app launch から panel 表示までの責務分担 | WM / ATM / CarSystemUI / Launcher の関係を図で説明できる |
| [architecture/aaos_app_layer_scalableui_scope_ja.md](architecture/aaos_app_layer_scalableui_scope_ja.md) | app layer と platform 差分の境界 | 個人検証で作れる成果物と対象 AAOS 環境で必要な取り込み作業を分けられる |
| [android17/aaos17_scalableui_as_is_capability_ja.md](android17/aaos17_scalableui_as_is_capability_ja.md) | AAOS17 ScalableUI の As-Is 実力、Panel/XML/Task event/Controller の詳細 | source 根拠をもとに ScalableUI 標準実装の範囲を説明できる |
| [android17/aaos17_scalableui_development_flow_ja.md](android17/aaos17_scalableui_development_flow_ja.md) | AAOS17 標準 target での開発フロー | Soong 負荷を抑えながら module build / image build へ進められる |
| [android17/android17_scalableui_delta_ja.md](android17/android17_scalableui_delta_ja.md) | Android16 QPR2 PoC と Android17 ScalableUI の差分 | どの patch を再設計すべきか判断できる |
| [workflows/variant_status_ja.md](workflows/variant_status_ja.md) | 各 variant の現行/過去/案の区分 | 古い variant を誤って現行 baseline として扱わずに済む |
| [workflows/poc_repository_cleanup_plan_ja.md](workflows/poc_repository_cleanup_plan_ja.md) | repository 整理方針 | docs / patches / variants の棚卸しを継続できる |

## Active PoC References

| 文書 | 何が理解できるか | 何ができるようになるか |
| --- | --- | --- |
| [../variants/declarative-multipanel/README.md](../variants/declarative-multipanel/README.md) | 現行 baseline variant の概要 | `declarative-multipanel` の patch と build 対象を確認できる |
| [../variants/declarative-multipanel/docs/hmi_spec_ja.md](../variants/declarative-multipanel/docs/hmi_spec_ja.md) | HMI 仕様 | map/media/settings/appgrid/app_panel の意図を確認できる |
| [../variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md](../variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md) | runtime smoke の評価記録 | 過去の合格条件や検証観点を再利用できる |
