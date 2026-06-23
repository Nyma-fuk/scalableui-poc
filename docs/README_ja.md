# ScalableUI PoC Docs Index

このdocs配下には、ScalableUIそのものの調査、PoC仕様、Android17移植、過去variantの実験記録が含まれる。
読むときは、必ず以下の区分を意識する。

## Source-Verified / ScalableUI General

AAOS/AOSP sourceを正としてScalableUIの責務境界を説明する資料。

| 文書 | 位置づけ |
| --- | --- |
| [aosp_source_verification_ja.md](aosp_source_verification_ja.md) | docsの主張をAAOS/AOSP sourceで照合した基準文書 |
| [aaos17_scalableui_source_verification_ja.md](aaos17_scalableui_source_verification_ja.md) | Android17 source上のScalableUI実装とdocs記述の整合性確認 |
| [scalableui_window_manager_flow_ja.md](scalableui_window_manager_flow_ja.md) | ScalableUI / WindowManager / ActivityTaskManager / Launcherの表示フロー |
| [aaos_app_layer_scalableui_scope_ja.md](aaos_app_layer_scalableui_scope_ja.md) | アプリレイヤー、自社開発、サプライヤー統合の責務分担 |

## Active PoC Baseline

現行PoCとして扱う資料。

| 文書 | 位置づけ |
| --- | --- |
| [../variants/declarative-multipanel/README.md](../variants/declarative-multipanel/README.md) | 現行baseline variant |
| [../variants/declarative-multipanel/docs/hmi_spec_ja.md](../variants/declarative-multipanel/docs/hmi_spec_ja.md) | HMI仕様 |
| [../variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md](../variants/declarative-multipanel/docs/evaluation_2026-06-09_ja.md) | AAOS15 LTS3での評価記録 |

## Android17 Porting

Android17移植・開発フローに関する資料。

| 文書 | 位置づけ |
| --- | --- |
| [aaos17_scalableui_development_flow_ja.md](aaos17_scalableui_development_flow_ja.md) | Android17での推奨開発フロー |
| [aaos17_scalableui_source_verification_ja.md](aaos17_scalableui_source_verification_ja.md) | Android17 ScalableUI source verification |
| [android17_as_is_scalableui_migration_plan_ja.md](android17_as_is_scalableui_migration_plan_ja.md) | As-Is担保付き移植計画 |
| [android17_scalableui_delta_ja.md](android17_scalableui_delta_ja.md) | Android16 QPR2 PoCとAndroid17 ScalableUI差分 |
| [aaos17_vs_android15_lts5_feature_delta_ja.md](aaos17_vs_android15_lts5_feature_delta_ja.md) | Android15 LTS5とAndroid17のAAOS差分 |

## Historical / Experimental

正しい実験記録を含むが、現行baselineではない資料。
量産判断やAndroid17移植に使う場合は、必ずsource再照合する。

| 文書 | 位置づけ |
| --- | --- |
| [dynamic_workspace_notes_ja.md](dynamic_workspace_notes_ja.md) | runtime panel生成を含むDynamic Workspace実験 |
| [scalableui_poc_architecture_ja.md](scalableui_poc_architecture_ja.md) | Dynamic Workspace中心の古い全体構成メモ |
| [editable_home_fullscreen_architecture_ja.md](editable_home_fullscreen_architecture_ja.md) | editable-home実験 |
| [widget_layout_lab_notes_ja.md](widget_layout_lab_notes_ja.md) | widget-layout-lab実験 |
| [widget_workspace_build_notes_ja.md](widget_workspace_build_notes_ja.md) | widget-workspace build note |
| [hmi_variant_suite_ja.md](hmi_variant_suite_ja.md) | generated variant suite案 |
| [variant_status_ja.md](variant_status_ja.md) | variantごとの現行/過去/生成案ステータス |
| [phase_evaluation_2026-05-31_ja.md](phase_evaluation_2026-05-31_ja.md) | 過去phase評価 |
| [root_poc_fix_evaluation_2026-06-01_ja.md](root_poc_fix_evaluation_2026-06-01_ja.md) | 過去fix評価 |
| [root_poc_runtime_owner_validation_2026-06-07_ja.md](root_poc_runtime_owner_validation_2026-06-07_ja.md) | 過去runtime owner検証 |

## Implementation / Agent Notes

| 文書 | 位置づけ |
| --- | --- |
| [ai_implementation_guide_ja.md](ai_implementation_guide_ja.md) | agent向け実装ガイド |
| [runtime_panel_control_ja.md](runtime_panel_control_ja.md) | runtime panel control検討 |
| [scalableui_hmi_poc_spec_ja.md](scalableui_hmi_poc_spec_ja.md) | 初期PoC仕様メモ |

## 読み方のルール

- ScalableUIそのものを知りたい場合は、`aosp_source_verification_ja.md` と `scalableui_window_manager_flow_ja.md` を読む。
- 現行PoCを触る場合は、`variants/declarative-multipanel` を読む。
- Android17作業では、source事実は `aaos17_scalableui_source_verification_ja.md`、開発手順は `aaos17_scalableui_development_flow_ja.md` を正とする。
- historical資料の正しい内容は残すが、現行baselineとは混ぜない。
- 「PanelにActivityを直接表示する」と説明しない。実装上はtask/root taskを介する。
- runtime panel生成や任意app assignmentは、ScalableUI標準ではなくPoC/OEM custom領域として扱う。
