# ScalableUI PoC Documentation Audit（2026-10-01）

## 目的

repository内のMarkdownを横断確認し、現行AAOS17 source、2026年9月更新の公式Scalable UI資料、現行PoC baseline、過去の評価記録を混同しない状態にする。

## 監査範囲

2026-10-01の監査開始時点で、`backups/`を除く既存Markdown 103件を次の単位で棚卸しした。本監査結果ファイルを追加した後の総数は104件である。

| 区分 | 件数 | 確認方針 |
| --- | ---: | --- |
| `docs/` | 51 | source依存の主張、index、日付、相互リンクを再確認 |
| `variants/` | 41 | active / AAOS17 sample / historical / generatedの分類を再確認 |
| `wiki/` | 6 | 現行baselineとcanonical docsへの導線を更新 |
| root / `common` / `patches` / `hmi-variants` | 5 | 現行扱い、古いパス、AAOS15専用productとの境界を確認 |

`AGENTS.md`は利用者向け文書ではないが、参照先の古いパスが作業を誤らせるため監査対象に含めた。

## Source Of Truth

| 種別 | 基準 |
| --- | --- |
| moving branch | `android17-release` manifest `29ace668ae756c7b8917c57abb440f6518844b0c` |
| reproducible tag | `android-17.0.0_r1` manifest `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f` |
| Build ID | `CP2A.260605.016` |
| source hash詳細 | [AAOS17 Source Snapshot](aaos17_source_snapshot_2026-10-01_ja.md) |
| official docs | Scalable UI overview / implement / panel / variant / transition / event / ecosystem / WM invariants |

主要ScalableUI projectのbranch HEADと固定tag checkoutは同一hashである。このため、個別demo資料のXML/class表はsource driftによる再生成を必要としなかった。

## 主な修正結果

| 論点 | 修正後の扱い |
| --- | --- |
| PanelとActivity | `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` |
| TaskView | `TaskPanel`とは別経路 |
| Panel drag | `KeyFrameVariant`、drag sample、runtime resizeは標準部品。任意reorder editor、入力競合解決、永続化はcustom |
| task reparent | `TaskBehavior`には新規task launch policyがある。任意の既存taskをUI操作でPanel間移動する完成機能とは区別 |
| WindowManager | launch時の最終configuration安定、Home時のstandard Activity停止、overlay/insets、immersive、cornerのinvariantsを設計条件化 |
| feature enable | `config_enableScalableUI=true`に加え、公式implement資料が要求する`android.software.car.splitscreen_multitasking`と競合legacy windowingの無効化を確認対象化 |
| AAOS 25Q4 | Android 17の別名ではない。AAOS API level 16.1のrelease資料として、Android 17 source調査の補助比較に使用 |
| historical docs | 当時の事実を改変せず、現行sourceの根拠に使う際は再検証が必要と明記 |
| generated variants | AAOS15向けidea。Android17では専用productを増やす手順として使わない |

## 文書群ごとの判定

| 文書群 | 判定 | 対応 |
| --- | --- | --- |
| `docs/verification` | Current | official docsとAAOS17 hashを追加し、標準部品/custom境界を補正 |
| `docs/architecture` | Current | WindowManager invariants、TaskBehavior、KeyFrameVariant、Panel reorderへの影響を追記 |
| `docs/android17` | Current / point-in-time evidence | source snapshotを共通基準にし、AAOS25Q4とのrelease区分を補正 |
| `docs/android17/scalableui_demos` | Current for pinned source | 親indexでsource hashを固定。個別表は同一source hashのため維持 |
| `docs/external` | External snapshot | 対象repository commitとAAOS17照合時点を明記 |
| `docs/workflows` | Mixed | active workflowとhistorical/generated workflowを分類。古いpathを補正 |
| `docs/historical` | Historical | point-in-time記録として内容を保持。現行判断には使用しない |
| `variants/declarative-multipanel` | Active design / mixed validation | AAOS15評価済み範囲とAAOS17未完了移植を分離 |
| その他の`variants` | Historical / generated | 親indexの分類を正とし、個別のAAOS15 lunch手順をAndroid17手順と解釈しない |
| `wiki` | Current entry point | snapshot、公式仕様、現行パスへ更新 |

## 意図的に更新しない情報

- 日付付きruntime評価の結果やスクリーンショット判定は、当時の証跡であり最新runtimeの代替ではない。
- historical patchのclass名や挙動は、履歴の再現に必要なため現行classへ機械的に置換しない。
- generated variantの専用product名はAAOS15案の識別子として残す。Android17の推奨targetではない。
- external repository解析は記録したcommitに固定し、upstream最新状態を無条件に代表するとは記述しない。

## 今後の更新ルール

1. `android17-release`または主要project hashが変わったら、source diffを確認してsnapshotを更新する。
2. 公式Scalable UIページの更新日と新しいreference pageをfact checkへ取り込む。
3. runtime挙動の表は、新しいbuild / emulator証跡なしに`OK`へ更新しない。
4. current、point-in-time evidence、historical、generated、external snapshotを混在させない。
5. Markdown相対リンクと`git diff --check`をpublish前に全件確認する。
