# AAOS17 Source Snapshot（2026-10-01）

## 目的

AAOS17 ScalableUI の調査・実装・説明で使用する branch、tag、commit hash を固定し、公式 AOSP、ローカル checkout、PoC 差分を混同しないための基準文書である。

## 結論

- 追随先の公式 branch は `android17-release`、2026-10-01 時点の manifest HEAD は `29ace668ae756c7b8917c57abb440f6518844b0c`。
- 再現可能な検証基準は `android-17.0.0_r1`、manifest commit は `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f`、Build ID は `CP2A.260605.016`。
- 2026-10-01 時点で公開されている Android 17 release tag は `android-17.0.0_r1`。`android17-release` は moving branch なので、文書や証跡では branch 名だけでなく確認日と hash を併記する。
- ScalableUI の主要 project は `android17-release` HEAD とローカル r1 checkout が同一 hash である。この文書群の capability 評価は current release branch にも適用できる。
- ローカル checkout には PoC と既存ユーザー変更がある。以下の hash は各 project の基準 commit であり、working tree 全体が pristine AOSP であることを意味しない。

## Official Refs

| 用途 | ref | commit | 日時 |
| --- | --- | --- | --- |
| 追随先 | `refs/heads/android17-release` | `29ace668ae756c7b8917c57abb440f6518844b0c` | 2026-06-16 23:40:21 +0000 |
| 固定検証点 | `refs/tags/android-17.0.0_r1` | tag `7a9e46ba6ed424f922a3457f4964e67e0b966201` / manifest `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f` | 2026-06-16 23:31:21 +0000 |

公式参照:

- `https://android.googlesource.com/platform/manifest/+/refs/heads/android17-release`
- `https://android.googlesource.com/platform/manifest/+/refs/tags/android-17.0.0_r1`

公式Scalable UI referenceの確認対象:

| Page | 2026-10-01時点で確認した要点 |
| --- | --- |
| `scalableui` overview | dedicated root task、TaskPanel / DecorPanel、Android17 advanced windowing、CTS上の位置づけ |
| `implement` | `config_enableScalableUI`、`android.software.car.splitscreen_multitasking`、競合legacy windowing無効化 |
| `panel-ref` | `window_states`、`TaskBehavior`、`Restart`、controller metadata |
| `variant-ref` | bounds / safe bounds / insets / background、`KeyFrameVariant`による連続補間 |
| `transitions-ref` / `event-ref` | event filter、from/to variant、animation、token matching |
| `wm-invariants` | launch configuration、Home lifecycle、overlay/insets、immersive、corner |
| `ecosystem` | runtime resizeの性能影響、overlayによる視覚的緩和、app側のadaptive/insets対応 |

## ScalableUI 関連 project hash

`git ls-remote` で公式 `android17-release` を確認し、ローカル checkout の基準 commit と照合した。

| local path | AOSP project | `android17-release` HEAD | local base | 判定 |
| --- | --- | --- | --- | --- |
| `build/make` | `platform/build` | `5ce6f787337d0223710bf7d4a16dbe6d2a35f777` | 同左 | 同一 |
| `frameworks/base` | `platform/frameworks/base` | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | 同左 | 同一 |
| `packages/apps/Car/SystemUI` | `platform/packages/apps/Car/SystemUI` | `8dd6b4135ad531ae26adc96f99a4f6f2eb693138` | 同左 | 同一 |
| `packages/apps/Car/systemlibs` | `platform/packages/apps/Car/systemlibs` | `50c8ca46d83136931d49d1c82ad9029ca8354dc1` | 同左 | 同一 |
| `packages/services/Car` | `platform/packages/services/Car` | `9f04df65daa8b9a65ee05fd4039fe95446874d76` | 同左 | 同一 |
| `device/generic/car` | `device/generic/car` | `f7883270a86b40fb7c3f11f2f755af4a43d0beef` | 同左 | 同一 |

`packages/apps/Car/systemlibs/car-scalable-ui-lib` と `packages/services/Car/libs/car-wm-shell-lib` は独立 Git repository ではなく、表の親 project の一部である。

## Local checkout の状態

ローカル `<AAOS17_ROOT>` は次の二層として扱う。

```text
android-17.0.0_r1 / CP2A.260605.016
  + ScalableUI PoC 差分
  + 既存ユーザー変更
```

2026-10-01 の確認時点で、少なくとも次の変更が基準 commit の上に存在する。

| project | working tree の主な差分 |
| --- | --- |
| `packages/apps/Car/SystemUI` | MinimizedControls sample resource の既存変更 |
| `packages/services/Car` | `car_dewd_common.mk`、permission定義、`scalableui_declarative_multipanel` product/RRO |
| `device/generic/car` | `sdk_car_x86_64.mk` への PoC package 統合 |

このため、公式仕様の主張は基準 commit の source で確認し、PoC の成立性は working tree 差分と runtime 証跡で別に確認する。

## 現行 ScalableUI の実力

主要 project が release branch と固定 tag で一致しているため、2026-10-01 時点の実力は次のように整理できる。

公式 overview は 2026-09-27、app ecosystem は 2026-09-24 に更新されている。overview は、新規AAOS programへのScalableUI採用を強く推奨し、AAOS 16以降ではScalableUIを無効にした構成はCTSを通過しないとしている。またAndroid 17のadvanced windowing項目としてHUN panel、system bar customization、WM invariants、Setup Wizard integrationを明示している。

| 領域 | 現行 source にあるもの | 完成機能としては存在しないもの |
| --- | --- | --- |
| Panel model | XML / DCF、`PanelState`、variant、`TaskPanel`、`DecorPanel`、`SysUIPanel` | 任意レイアウトを作る汎用ユーザー editor |
| App表示 | `TaskPanel -> RootTaskStack / Task -> Activity` | `Panel -> Activity` の直接モデル、TaskViewとの同一性 |
| 状態遷移 | Event / token、`PanelTransaction`、WM transition、Surface transaction | HMI固有の編集policyや競合解決の自動生成 |
| Runtime update | `StateManager.addState()` / `reloadPanelState()`、panel update API | app picker、永続化、復元まで含む完成済み layout editor |
| Drag入力 | `KeyFrameVariant`、sampleのgrip drag、caption/spy input、`pilferPointers()`を組み合わせられる部品 | Panel全面長押しswapの標準実装 |
| System UI | system bar、HUN、SUW、UXR/user/task event との統合 | 製品固有要件を設定だけで完結させる仕組み |

固定3-slotの Panel 入れ替えは実現可能だが、ScalableUI 標準機能を有効化するだけでは完成しない。Map の pinch / pan と競合させない第一候補は編集モードであり、全面長押し方式を採る場合は spy input、long-press 判定後の pointer pilfer、Surface preview、drop 時の slot state commit を追加する。詳細は [Panel並べ替え入力設計](../architecture/panel_reorder_interaction_design_ja.md) を参照する。

## 更新ルール

1. 日常の追随確認は `android17-release` と主要 project の HEAD hash を記録する。
2. build、runtime証跡、再現手順は immutable tag と Build ID に固定する。
3. branch HEAD が変わった場合は、hash 更新だけで capability が同じと仮定せず、該当 project の source diff を再確認する。
4. PoC working tree の変更を AOSP標準 capability として記述しない。
5. security branch はセキュリティ取り込み用の別 ref とし、ScalableUI機能の追随先と混同しない。
