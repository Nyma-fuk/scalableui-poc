# Dynamic Workspace Notes

> Source verification: この文書は `dynamic-workspace` の historical / experimental PoC メモです。現在の live `declarative-multipanel` baseline には Dynamic Workspace runtime は含まれていません。AOSP 実装との照合結果は [AOSP Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aosp_source_verification_ja.md) を参照してください。

`dynamic-workspace` は、固定スロットを前提にしない ScalableUI PoC です。

## 目標

- 初期状態を「固定 3 枚」ではなく空の workspace にする
- panel は runtime model から追加・削除・並び替えする
- panel ごとの app はユーザーが picker で選ぶ
- panel 幅は隣接 grip で変更する
- 画面幅を超えた panel 群は viewport handle で横スクロールする

## 実装の考え方

- RRO は最小限
  - `workspace_home_panel`
  - `app_panel`
- 実際の panel 群は `WorkspaceRuntimeLayoutController` が runtime で `PanelState` を追加する
- panel 本体は task panel、header / grip / toolbar / viewport handle は decor panel
- workspace model は `Settings.Secure` に JSON で保存する

実装分類:

- `StateManager.addState(...)` は ScalableUI library に存在する
- 任意数 panel の生成、geometry、永続化、picker、drag preview は ScalableUI 標準初期化ではなく PoC custom 実装である
- `WorkspaceRuntimeLayoutController` / `WorkspacePanelStateController` は patch 適用後の実装として扱い、live source で再確認してから本格適用判断する

## 現在の動的モデル

- panel ID は `workspace_panel_<n>` を連番で採番
- panel 幅は panel ごとに保持
- viewport offset を保持
- 空 panel は `WorkspaceEmptyPanelActivity` を表示し、そこから app picker を開ける

## 固定スロットを避けるための変更点

- default model は panel 0 枚
- 初回表示は背景 + toolbar のみ
- `Add panel` で panel を 1 枚追加し、そのまま fullscreen picker を開く
- panel をすべて削除しても成立する
- header 名称も `primary` / `secondary` のような slot 名ではなく、割り当て app 名または `Empty panel` を表示する

## 既知の境界

- ScalableUI の標準機能だけで「panel を任意数 runtime 生成」する仕組みは薄いため、
  `WorkspaceRuntimeLayoutController` が `StateManager.addState(...)` を使って補っている
- app を複数 panel にどう複製するか、同一 task をどう移動するかは product policy 次第
- 現在の PoC は 1 panel = 1 foreground task を基本としている

追加境界:

- `Panel` は Activity そのものではなく、`TaskPanel` の場合は root task stack / task を介して Activity を表示する
- `Workspace` は AOSP の `TaskDisplayArea` と同義ではない
- `RemoteCarTaskView` / `TaskView` は ScalableUI `TaskPanel` の実体ではない

## 2026-06-09 評価メモ: emulator resource と grip resize

### emulator resource

当初の評価 AVD `Y-Fuk-dynamic-workspace-eval3` は次の設定だった。

- `hw.ramSize=2G`
- `hw.cpu.ncore=4`
- `hw.gpu.enabled=no`
- `vm.heapSize=48M`

ゲスト側でも `MemTotal` は約 2GB で、ScalableUI の複数 panel / 複数 activity /
SurfaceControl 更新を評価するにはかなり厳しい。Windows host 側は約 34GB RAM / 12 logical
processors があるため、評価時は少なくとも次の起動オプションを使う。

```bash
emulator.exe \
  -avd Y-Fuk-dynamic-workspace-eval3 \
  -sysdir <AAOS_IMAGE_ROOT>\dynamic-workspace\extracted\x86_64 \
  -wipe-data \
  -no-snapshot-load \
  -ports 5562,5563 \
  -memory 6144 \
  -cores 6 \
  -gpu angle_indirect
```

`-gpu host` はこの Windows 環境ではグリップ評価中に emulator process が消えるケースがあった。
そのため、現時点の安定評価は `angle_indirect` を優先する。

### grip resize の実装修正

グリップ操作中の重さには resource 不足だけでなく、実装側の問題もあった。

- `resize_update` 中は task panel surface を更新せず、header / grip など decor panel のみ更新する。
- `resize_end` では保存 model と TaskPanel の surface state は更新する。
- ただし `AutoTaskStackController.startTransition(...)` は投げない。

理由は、`workspace_home_panel` が ScalableUI TaskPanel として存在し、Home activity task が同じ
ScalableUI 管理空間に混ざるためである。`resize_end` で full task-stack transition を投げると、
`WorkspaceHomeActivity` の activity type を後から変えようとして SystemUI が落ちることがあった。

実測された fatal:

```text
java.lang.IllegalStateException: Can't change activity type once set:
ActivityRecord{... com.android.car.scalableui.hmi.home/.WorkspaceHomeActivity ...}
activityType=undefined, was home
```

今回の修正では、grip release 時に ActivityTaskManager 側の task-stack transition を避け、
ScalableUI surface state の更新で視覚的な panel resize を成立させる方針にした。
これは、Google のデモで見える「グリップ中は app を逐次 re-render せず、境界操作を軽く扱う」
挙動に近い。

### 評価結果

評価 artifact:

- `<EVIDENCE_DIR>/dw-eval-20260609-resize-fix/01-before-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-resize-fix/02-after-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-resize-fix/03-after-second-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-resize-fix/02-summary.txt`
- `<EVIDENCE_DIR>/dw-eval-20260609-resize-fix/03-summary.txt`

確認できたこと:

- `420dp / 420dp` の 2 panel 構成から、1 回目の左ドラッグで `287dp / 553dp` に変化した。
- 2 回目の右ドラッグで `420dp / 420dp` に戻った。
- 2 回連続操作後も emulator は生存し、SystemUI PID は維持された。
- `FATAL EXCEPTION` / `AndroidRuntime` / `IllegalStateException` は再発していない。

残課題:

- `Slow dispatch` はまだ 1 回の drag あたり 7 件程度残る。
- したがって、安定性は改善したが、体感 performance はまだ追加改善の余地がある。
- 次の改善候補は decor panel の更新頻度削減、header 再計測の抑制、drag 中の app icon placeholder
  表示である。

## 2026-06-09 追加評価メモ: grip preview 軽量化

### 追加修正

`resize_update` のたびに全 header / grip / toolbar / viewport decor を更新していたため、
drag 中の dispatch が重くなっていた。

追加修正では、drag 中の `resize_update` を次の方針へ変えた。

- model 上の panel width は従来通り連続更新する。
- app task surface は drag 中に更新しない。
- header / toolbar / viewport も drag 中に更新しない。
- drag 中に画面上で動かすのは、操作中の境界 grip decor のみ。
- 指を離した `resize_end` で、保存 model に基づいて panel / header / grip の最終配置をまとめて反映する。

これにより、Google の split / scalable UI demo に近い「drag 中は app を逐次 re-render しない」
挙動へさらに寄せた。

### 評価結果

評価 artifact:

- `<EVIDENCE_DIR>/dw-eval-20260609-grip-preview/01-before-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-grip-preview/02-after-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-grip-preview/03-after-second-grip.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-grip-preview/02-summary.txt`
- `<EVIDENCE_DIR>/dw-eval-20260609-grip-preview/03-summary.txt`

確認できたこと:

- 1 回目の左ドラッグで `420dp / 420dp` から `287dp / 553dp` に変化した。
- 2 回目の右ドラッグで `287dp / 553dp` から `420dp / 420dp` に戻った。
- 2 回連続操作後も emulator は生存し、SystemUI PID は維持された。
- `FATAL EXCEPTION` / `AndroidRuntime` / `IllegalStateException` は再発していない。
- `Slow dispatch` は 1 回の drag あたり `7` 件程度から `1` 件へ減少した。

残課題:

- `resize_end` の最終反映で `Slow dispatch` が 1 件残る。
- これは最終的な panel / header / grip surface commit のため、現時点では許容できる範囲。
- さらに軽くする場合は、最終反映の task surface commit を非同期化するか、
  drag end 後に短い delayed commit を挟む設計を検討する。

## 2026-06-09 追加評価メモ: SOLID refactor

### 目的

`WorkspaceRuntimeLayoutController` が大きくなり、AAOS15 LTS5 / AAOS17 へ patch を移す際に
「ScalableUI の本体に必要な変更」と「PoC 固有の HMI runtime」が混ざって見えづらくなっていた。

今回の refactor では、挙動を変えずに責務を次のように分割した。

```text
WorkspaceRuntimeLayoutController
  - broadcast command を受ける
  - model を更新する
  - 各 collaborator を呼び出して最終反映を orchestration する

WorkspaceGeometry
  - display / system bar / toolbar / viewport / panel / header / grip の bounds を計算する
  - panel width の最小値を clamp する
  - decor panel id を生成する

WorkspacePanelStateController
  - StateManager.addState(...) で runtime task/decor panel を登録する
  - Variant の runtime bounds / visibility / layer を更新する
  - BasePanel.update(...) と SurfaceControl.Transaction を適用する

WorkspaceTaskRouter
  - TaskPanel role に割り当て component を設定する
  - panel 向け app 起動 intent を作る
  - app picker を fullscreen 起動する
```

### SOLID 観点

- Single Responsibility: geometry / panel state / task launch / command orchestration を分離した。
- Open Closed: layout 計算を変更する場合は主に `WorkspaceGeometry` を触ればよい。
- Dependency Inversion: Dagger injection point は `WorkspaceRuntimeLayoutController` のままにし、PoC 固有 collaborator は内部で生成する。AAOS 側の DI 差分を増やさない。
- Interface Segregation: 今回は public interface を増やさず、package-private class に閉じた。将来 AAOS17 で API 差が出た場合に置き換え範囲を限定できる。

### 評価結果

評価 artifact:

- `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor/01-before.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor/02-after-left.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor/03-after-right.png`
- `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor/02-summary.txt`
- `<EVIDENCE_DIR>/dw-eval-20260609-solid-refactor/03-summary.txt`

確認できたこと:

- `CarSystemUI` module build は成功した。
- `dynamic-workspace` emulator image zip build は成功した。
- Windows host emulator `Y-Fuk-dynamic-workspace-eval3` を `-memory 6144 -cores 6 -gpu angle_indirect` で起動し、boot 完了を確認した。
- 1 回目の drag で `420dp / 420dp` から `287dp / 553dp` に変化した。
- 2 回目の drag で `287dp / 553dp` から `420dp / 420dp` に戻った。
- SystemUI PID は `1506` のまま維持された。
- `FATAL EXCEPTION` / `AndroidRuntime` / `IllegalStateException` は再発していない。
- `Slow dispatch` は各 drag `1` 件で、refactor 前の grip preview 軽量化後と同等だった。
