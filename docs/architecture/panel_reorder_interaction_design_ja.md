# Panel 全面操作による 3-slot 並べ替え設計

> Status: design proposal / not implemented
>
> Target: AAOS17 `sdk_car_x86_64-trunk_staging-userdebug` + 現行 `declarative-multipanel`
>
> 調査時点: 2026-10-01
>
> AAOS17 source基準: [`android17-release` / `android-17.0.0_r1` snapshot](../verification/aaos17_source_snapshot_2026-10-01_ja.md)

## 1. 目的

3つの `TaskPanel` が横に並ぶ HMI で、ユーザーが Panel を左右へ drag and drop し、表示位置を入れ替えられるようにする。

想定例:

```text
初期:
┌────────────┬────────────┬────────────┐
│ Map        │ Media      │ Vehicle    │
└────────────┴────────────┴────────────┘

Map を右端へ drop:
┌────────────┬────────────┬────────────┐
│ Vehicle    │ Media      │ Map        │
└────────────┴────────────┴────────────┘
```

ここで移動するのは Activity の描画だけではない。`Panel -> TaskPanel -> RootTaskStack / Task -> Activity` という ScalableUI の所有関係を維持したまま、Panel の bounds / layer / 現在 Variant と WM Shell 上の Task surface を整合させる。

本設計は、次の2方式を比較したうえで、編集モード方式を第一実装とする。

1. 通常画面で Panel 全面を長押しして並べ替える
2. 明示的なレイアウト編集モード中だけ Panel 全面をドラッグ可能にする

## 2. 結論

第一実装は「編集モード + 全画面編集 Overlay + 固定3-slot + 直接 swap」とする。

通常画面の全面長押し方式もAAOS17では実現可能性があるが、Mapなどアプリの入力と同じ pointer streamを共有するため、Spy window、長押し競合、pointer pilfer、`ACTION_CANCEL`、privileged permissionまで扱う必要がある。最初からこの方式を採用すると、Panel配置ロジックと入力競合の問題を同時にデバッグすることになる。

編集モードでは、アプリ操作を意図的に停止し、編集Overlayが入力を専有できる。Panel swap自体の状態管理、Surface preview、Drop確定、復元を先に独立して検証できる。

公式Scalable UIの`KeyFrameVariant`は、0..1の連続fractionからbounds等を補間する標準部品であり、既存sampleにもdrag transitionがある。ただし、この部品だけでは「Panel全面の長押し検出」「Map gestureとのarbitration」「3-slot swap policy」「保存・復元」は提供されない。本設計は標準のdrag/transition部品を再利用しつつ、その外側の入力・編集policyを追加する。

またWM invariantsに合わせ、drag中はSurface previewを優先し、Drop時に最終boundsを一度のtransitionで確定する。Activityをdrag中の各frameでrelayoutさせない。

| 観点 | 通常画面の全面長押し | 編集モード中だけ操作 | 判定 |
| --- | --- | --- | --- |
| Mapのpan / pinch | gesture arbitrationが必要 | 通常モードでは無干渉 | 編集モードを優先 |
| Mapの長押し | Panel長押しと両立困難 | 通常モードでは維持可能 | 編集モードを優先 |
| 入力取得 | Spy window + `pilferPointers()` | 通常のtouchable overlay | 編集モードが単純 |
| permission | `MONITOR_INPUT` が必要 | 追加のpointer監視権限は不要 | 編集モードが安全 |
| 誤操作 | 長押し時間とslop依存 | 明示的に編集開始 | 編集モードが明確 |
| rotary拡張 | 別のfocus設計が必要 | slot選択UIへ拡張しやすい | 編集モードが有利 |
| PoC切り分け | 入力とlayoutを同時検証 | layout swapを先に検証可能 | 編集モードを優先 |

## 3. 前提と非目標

### 3.1 前提

- 現行 baseline は `declarative-multipanel`。
- Android17では標準 `sdk_car_x86_64` targetへPoC差分を追加する。
- 3つのPanelは固定slotに収まり、任意の自由座標へ保存しない。
- Panel IDとPanel内のTaskは維持し、Panel IDとslotの対応だけを変更する。
- drag中の見た目と、Drop後のWindowManager / ScalableUI確定状態を分けて扱う。

### 3.2 第一段階の非目標

- Panel数の動的追加・削除
- 任意サイズへのresize
- Panel間でのTask reparent
- 任意座標へのfree-form配置
- userごとの永続化
- 走行中の編集許可
- 通常画面でのPanel全面長押し

Panelの位置交換では、Taskを別Panelへreparentしない。たとえば `nav_panel` がMap Taskを所有したまま `slot_right` へ移動する。この方がTask lifecycle、launch root、role、focusの責務を崩しにくい。

## 4. 参考PoCから採用する考え方

参考実装:

- [`passenger6/car-systemui-win98-pod`](https://github.com/passenger6/car-systemui-win98-pod)
- [Building a desktop on AAOS with Scalable UI](https://medium.com/@passenger6/building-a-desktop-on-aaos-with-scalable-ui-framework-dc339ed3cc1c)
- 調査時のrepository commit: `3e4512ec606d63cd74364f7be32b9d68220b3446`（2026-10-01にremote HEADと一致確認）

採用する中核原則:

> drag中はSurfaceを動かして応答性を保ち、WindowManagerとScalableUIの確定状態はDrop時に一度だけ更新する。

参考PoCでは、captionの `MotionEvent` から `AutoSurfaceTransaction.setTaskSurfacePosition()` を呼び、Drop時にruntime Variantとevent transitionへ最終Rectを書き込む。

本設計では自由座標を保存する必要がないため、`win98_free_a` / `win98_free_b` のような可変Variantを第一選択にしない。各Panelが持つ `slot_left` / `slot_center` / `slot_right` の静的Variantへ遷移させる。

採用しない要素:

- Windows 98 chrome
- 任意数window pool
- app launch rootを空きwindowへ切り替えるrouting
- minimize / maximize / close
- 自由座標のruntime Variant

## 5. 用語と状態モデル

### 5.1 Panel identityとslot identityを分ける

```text
Panel identity:
  nav_panel
  media_panel
  user_slot_panel

Slot identity:
  slot_left
  slot_center
  slot_right
```

状態は次のmappingとして扱う。

```text
panelToSlot = {
  nav_panel:       slot_left,
  media_panel:     slot_center,
  user_slot_panel: slot_right
}
```

`nav_panel` を右端の `user_slot_panel` 上へDropした場合、第一段階では直接swapとする。

```text
panelToSlot = {
  nav_panel:       slot_right,
  media_panel:     slot_center,
  user_slot_panel: slot_left
}
```

途中slotへ挿入して他Panelを順送りするreorder方式は、直接swapとは操作結果が異なる。第一段階では採用せず、必要なら別policyとして追加する。

### 5.2 slot bounds

slot boundsはsystem bar / insetを除いたworkspace bounds内で定義する。

```text
workspaceBounds
  ├─ slot_left_bounds
  ├─ slot_center_bounds
  └─ slot_right_bounds
```

slot間にgapがある場合、Drop判定には見た目のPanel boundsではなく、slot centerを使う。

```text
targetSlot = minBy(abs(draggedPanel.centerX - slot.centerX))
```

workspace外へ出た場合は左右端へclampする。system bar、HVAC、camera priority layerはdrop targetに含めない。

## 6. 推奨方式: 編集モード

### 6.1 通常モード

- 編集Overlayは非表示。
- TaskPanelの入力は各アプリが直接受け取る。
- Mapのtap、pan、pinch、アプリ固有のlong pressを妨げない。
- Panel boundsとslot mappingだけを表示状態として使う。

### 6.2 編集モードへの入口

入口候補:

- system barまたはworkspace menuの「レイアウト編集」
- parked時だけ有効なsettings action
- debug build用shell command

`enter_layout_edit` eventで編集Overlayを表示し、開始時mappingをsnapshotする。

```text
savedAtEnter = panelToSlot.copy()
```

現行HMI specには `edit_overlay_panel` と `enter_layout_edit` / `exit_layout_edit` がすでに存在する。ただし現在の役割は編集モードを示すOverlayであり、Panel全面の入力処理やswap確定を行うcontrollerは未実装である。

### 6.3 編集Overlay

推奨はPanelごとに3枚のOverlayを置く構成ではなく、workspace全体を覆う1枚の `DecorPanel` とする。

```text
PanelReorderOverlayView
  ├─ workspace内のtouchを受け取る
  ├─ panel boundsをhit-testする
  ├─ selected panelのoutlineを描く
  ├─ drop target slotをhighlightする
  ├─ Done / Cancelを表示する
  └─ drag中のaccessibility descriptionを更新する
```

1枚にする理由:

- Panel境界をまたいでもgesture ownerが変わらない。
- 他Panel上へDropするhit-testを一箇所に集約できる。
- z-orderとtouchable regionを管理しやすい。
- Done / Cancel、scrim、slot highlightを同一surfaceで描ける。

編集OverlayはTaskPanelより上のlayerに置く。半透明scrim、Panel名、drag handle、選択枠を描き、編集モード中は下のアプリが操作できないことを明確にする。

既存の `edit_overlay_panel` は中央dialog相当のboundsからworkspace全体へ広げる必要がある。system barまで覆うかは製品UX次第だが、第一段階ではworkspace boundsだけをtouchableにし、system barのHome / safety操作を維持する。

### 6.4 gesture state

編集モードでは明示的に操作状態へ入っているため、長押しを必須にしない。

```text
NORMAL
  |
  | enter_layout_edit
  v
EDIT_IDLE
  |
  | ACTION_DOWN in panel bounds
  v
DRAGGING
  |-- ACTION_MOVE --> preview更新 / target slot更新
  |-- ACTION_UP ----> COMMIT_SWAP --> EDIT_IDLE
  `-- ACTION_CANCEL -> ROLLBACK_PREVIEW --> EDIT_IDLE

EDIT_IDLE
  |-- Done   --> 保存（将来phase）/ exit_layout_edit --> NORMAL
  `-- Cancel --> savedAtEnterを復元 / exit_layout_edit --> NORMAL
```

誤操作が問題になる場合は、編集モード内だけ次の条件を追加する。

- `ACTION_DOWN` 後にtouch slopを超えてからdrag開始
- 150-250ms程度の短いhold
- drag開始時のhaptic feedback

通常Androidのlong press timeoutを待つ必要はない。

## 7. drag preview

### 7.1 drag開始

1. touch座標からPanel IDを特定する。
2. Panelの開始boundsと開始slotを保存する。
3. Panel layerを一時的に前面へ上げる。
4. 選択枠、影、scaleなどのdrag feedbackを表示する。
5. 他Panelのアプリ入力は編集Overlayが遮断する。

### 7.2 ACTION_MOVE

drag中は水平方向だけ追従させる。

```text
deltaX = currentRawX - downRawX
previewBounds = startBounds.offset(deltaX, 0)
previewBounds = clampToWorkspace(previewBounds)
```

Taskの見た目は `AutoSurfaceTransaction` で移動する。

候補API:

```java
transaction.setTaskSurfacePosition(rootTaskId,
        previewBounds.left, previewBounds.top);
```

drag中にPanel Variant transitionやWindowContainerTransactionをMOVEごとに実行しない。毎frame Task boundsをWindowManagerへ確定すると、Activity側のrelayoutやconfiguration更新と競合し、jankの原因になる。

編集Overlay側では次を更新する。

- dragged Panelのoutline
- 現在のtarget slot
- target slotにいるPanelのoutline
- drop可能 / 不可の表示

### 7.3 他Panelのpreview

第一実装はdrag対象だけを動かし、交換相手は元の位置に残す。target slot highlightで交換先を示す。

将来、交換相手をdrag開始slotへ滑らせるpreviewを追加できるが、2 Panel分のtemporary surface stateとcancel復元が必要になるため、第一段階では行わない。

## 8. DropとScalableUI状態の確定

### 8.1 Drop判定

`ACTION_UP` 時点で、dragged Panel中心に最も近いslotをtargetとする。

```text
sourceSlot == targetSlot
  -> previewを元boundsへ戻し、mappingは変更しない

sourceSlot != targetSlot
  -> targetSlot occupantと直接swap
```

### 8.2 静的Variant

各TaskPanelに3つのVariantを用意する。

```xml
<Variant id="@+id/slot_left">
    <Bounds ...left slot... />
    <TaskToolbarBounds ...left slot... />
</Variant>

<Variant id="@+id/slot_center">
    <Bounds ...center slot... />
    <TaskToolbarBounds ...center slot... />
</Variant>

<Variant id="@+id/slot_right">
    <Bounds ...right slot... />
    <TaskToolbarBounds ...right slot... />
</Variant>
```

`TaskToolbarBounds` は通常画面長押し方式を採用しない段階では必須ではない。将来のSpy toolbar方式を試す場合に追加する。

### 8.3 event設計

実装方法は2案ある。

#### 案A: layout permutation event

3 Panelの全配置をlayout stateとして扱う。

```text
panel_layout_map_media_vehicle
panel_layout_map_vehicle_media
panel_layout_media_map_vehicle
panel_layout_media_vehicle_map
panel_layout_vehicle_map_media
panel_layout_vehicle_media_map
```

1つのeventを3 Panelが受け、それぞれ対応slot Variantへ遷移する。

利点:

- XMLだけで最終配置を確認できる。
- 3 Panel / 6 permutationなら状態数が小さい。
- Home restore policyを明示しやすい。

欠点:

- Panel数が増えると組合せが急増する。
- user追加Panelには向かない。

固定3 Panelの第一実装では案Aを推奨する。

#### 案B: runtime destination Variant

PanelごとにA/Bの可変destination Variantを持ち、Drop時にbounds/layer/insets/visibilityを一組で書き換える。

利点:

- Panel数やslot数を動的に扱える。
- free-form layoutへ拡張しやすい。

欠点:

- `Variant`内部setterへのアクセス方法が必要。
- ScalableUI modelとlive Panel fieldの同期を独自に保証する必要がある。
- SystemUI再起動・user切替・theme変更時の復元が複雑になる。

これは参考Win98 PoCに近いが、固定3-slotの第一実装には過剰である。

### 8.4 atomicity

swap対象2 Panelの状態は同じ操作として確定させる。

要求:

- dragged Panelだけ先に確定しない。
- 一時的に2 Panelが同じslot boundsへ入らない。
- layer、bounds、visibilityを不整合な組で適用しない。
- ScalableUIのcurrent VariantとWM ShellのTask stack stateを一致させる。

まず同一eventで複数Panel transitionが1つのcoordination cycleに入ることをruntime traceで確認する。画面上のちらつきや複数WCTが問題になる場合は、custom coordinatorが2つの `AutoTaskStackState` を1つの `AutoTaskStackTransaction`へ追加して確定し、その後ScalableUI modelを同じlayout stateへ同期する。

「Surfaceだけ最終位置に残し、Variantは旧slotのまま」という状態を許容しない。別transition、theme変更、Task再生成時に旧boundsへ戻るためである。

### 8.5 cancel

`ACTION_CANCEL`、編集Overlay消失、camera override、user switch、display configuration changeが発生した場合はcommitしない。

```text
Task surface    -> drag開始boundsへ戻す
temporary layer -> 元layerへ戻す
target highlight -> 消す
panelToSlot     -> 変更しない
```

camera priority transitionが始まった場合は、編集モード自体を終了し、必要なら開始時snapshotへ戻す。

## 9. 通常画面の全面長押し方式

この方式は第二段階の実験とする。

### 9.1 単純な透明Overlayでは成立しない

TaskPanelより上に通常のtouchable Viewを全面配置すると、最初の `ACTION_DOWN` からOverlayがgesture targetになり、Mapへtap / pan / pinchが届かない。

TaskPanelより下にDecorPanelを置くとMap操作はできるが、app Taskが上にあるためDecorPanelはPanel内部のtouchを観測できない。参考Win98 PoCがcaptionやframeだけを入力領域にしている理由でもある。

### 9.2 Spy window

AAOS17のautomotive WM ShellにはSpy windowを作る経路がある。

```text
<AAOS17_ROOT>/packages/services/Car/libs/car-wm-shell-lib/
  src/com/android/wm/shell/automotive/AutoDecor.java
```

`AutoDecor` は `WindowManager.LayoutParams.INPUT_FEATURE_SPY` を設定できる。`AutoCaptionController` はcaption decorをTaskへattachするとき、このSpy設定を使用する。

```text
<AAOS17_ROOT>/packages/services/Car/libs/car-wm-shell-lib/
  src/com/android/wm/shell/automotive/AutoCaptionController.java
```

Spy windowは同じpointer streamを観測しつつ、下のアプリにも入力を渡す。

### 9.3 TaskToolbarをPanel全面へ広げる案

各Variantの `TaskToolbarBounds` をPanel全体にし、custom `TaskToolbarController` が透明Viewを返す。

```text
PanelReorderTaskToolbarController
  -> transparent full-panel View
  -> Spy windowとしてTaskへattach
  -> DOWN/MOVE/POINTER_DOWNを観測
```

関連source:

```text
<AAOS17_ROOT>/packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui/
  panel/TaskPanel.java
  panel/controller/TaskToolbarController.kt
  panel/controller/PanelControllerInitializer.java
```

成立条件:

- `DisplayCompatV2` が有効であること
- `safe_region_letterboxing_v1` 系の必要flagが有効であること
- custom `TaskToolbarController.Factory` をDagger mapへ登録すること
- caption/toolbar lifecycleがPanel bounds変更へ追従すること

### 9.4 pointer pilfer

候補gesture中はSpy windowとMapの両方がeventを受ける。

```text
ACTION_DOWN
  -> candidate開始

touch slop超過 before timeout
  -> candidate破棄
  -> Mapがgestureを継続

POINTER_DOWN before timeout
  -> candidate破棄
  -> Mapがpinchを継続

long press成立
  -> InputManager.pilferPointers(spyInputToken)
  -> MapへACTION_CANCEL
  -> Spy側だけが残りのMOVE/UPを受信
  -> Panel dragへ移行
```

`InputManager.pilferPointers()` は、pilferしたSpy window以外へcancelを生成する。CarSystemUIを含むSystemUI manifestは `android.permission.MONITOR_INPUT` を持つが、これは一般アプリへ移せる実装ではない。

関連source:

```text
<AAOS17_ROOT>/frameworks/base/core/java/android/hardware/input/InputManager.java
<AAOS17_ROOT>/frameworks/base/packages/SystemUI/AndroidManifest.xml
<AAOS17_ROOT>/frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/pip2/phone/
  PipResizeGestureHandler.java
```

### 9.5 gesture arbitration

推奨判定:

| 入力 | 所有者 |
| --- | --- |
| tap | app |
| 1本指でtimeout前にslop超過 | app pan |
| timeout前に2本目のpointer | app pinch |
| slop内でlong press成立後に移動 | Panel reorder |
| Panel drag中の追加pointer | 無視またはgesture cancel |

Map固有のlong pressとPanel long pressは同じ領域・同じ時間条件を使うため、本質的に競合する。Panel全面long pressを有効にする場合、Mapのlong press機能を製品UXとして予約解除するか、Panel reorderを別gestureへ変更する必要がある。

長押し成立直前にSpy側がpilferしても、app側long press callbackとのraceを完全には排除できない。これが通常画面方式を第二段階とする主な理由である。

## 10. 実装コンポーネント案

### 10.1 CarSystemUI pod / module

参考Win98 PoCと同様に、機能をCarSystemUIの小さなpodまたは専用packageへ分離する。

```text
PanelReorderModule
  Dagger bindings

PanelReorderCoordinator
  edit mode、mapping、gesture、commit/cancelの所有者

PanelReorderOverlayController
  edit_overlay_panelのcontroller

PanelReorderOverlayView
  hit-test、outline、slot highlight、Done/Cancel

PanelSlotLayout
  workspaceと3 slotのgeometry計算

PanelSurfacePreview
  AutoSurfaceTransactionによるdrag previewとrollback

PanelLayoutCommitter
  event発行またはAutoTaskStackTransactionによる確定

PanelOrderStore   # phase 2
  userごとの保存・復元

PanelReorderTaskToolbarController  # phase 3
  通常画面長押し用Spy toolbar
```

### 10.2 RRO/XML

```text
edit_overlay_panel
  hidden / editing
  editing boundsをworkspace全体へ拡張
  controllerをPanelReorderOverlayControllerへ接続

nav_panel / media_panel / user_slot_panel
  slot_left / slot_center / slot_right Variant
  layout permutation event transitions

window_states
  edit_overlay_panelを維持

resources
  slot gap、drag scale、scrim alpha、animation duration
```

### 10.3 event案

```text
enter_layout_edit
exit_layout_edit

panel_layout_map_media_vehicle
panel_layout_map_vehicle_media
panel_layout_media_map_vehicle
panel_layout_media_vehicle_map
panel_layout_vehicle_map_media
panel_layout_vehicle_media_map

cancel_layout_edit
reset_layout_default
```

event名へsource/target Panel IDを埋め込む方式より、最終layoutを表す名前の方が再起動復元やログ解析で曖昧になりにくい。

## 11. 永続化

第一段階ではプロセス内だけでよい。`_System_OnHomeEvent`、SystemUI再起動、emulator再起動のどこでdefaultへ戻すかを明記する。

第二段階で保存する場合:

- userごとに保存する。
- version付きmodelにする。
- panel IDが不足・追加されたときdefaultへ安全にmergeする。
- 保存値から任意boundsを直接復元せず、slot IDを復元する。

例:

```json
{
  "version": 1,
  "order": ["nav_panel", "media_panel", "user_slot_panel"]
}
```

候補保存先は `Settings.Secure`。SystemUI側でuser switchを監視し、該当userのorderを読み直す。破損JSON、未知Panel ID、重複Panel IDはdefaultへfallbackする。

## 12. UX / automotive制約

- 編集開始時に明確なmode labelとscrimを表示する。
- drag開始時にhaptic feedbackを出す。
- app内容は見えるが操作できないことをoutlineやlabelで示す。
- Done / Cancelを常時表示する。
- Home、camera priority、user switchで安全に編集を終了する。
- driving UX restrictions中は編集入口を無効化する方針を検討する。
- rotaryではPanel focusを左右移動し、決定後にslotを選ぶ別interactionを設計する。
- accessibility service向けにPanel名、現在slot、移動先slotをannounceする。

## 13. failure handling

| 条件 | 動作 |
| --- | --- |
| target Task leashがない | dragを開始しない |
| Panelが非表示になった | previewをrollbackし編集終了 |
| camera override | commitせず編集終了 |
| user switch | 現userの編集をcancelし、新user状態をload |
| display rotation / resolution変更 | dragをcancelしslot geometryを再計算 |
| shell transitionがdrag中に開始 | 次MOVEでpreview再適用、またはdragをcancel |
| Drop event失敗 | surfaceをmodel上のcurrent Variantへ戻す |
| 保存失敗 | runtime swapは維持可能だが未保存表示を出す |

## 14. 検証計画

### 14.1 unit test

- touch座標からPanel IDを正しく選ぶ。
- x座標からtarget slotを正しく選ぶ。
- 同一slot dropはno-op。
- LEFTとRIGHTの直接swapでCENTERが変化しない。
- cancelで開始mappingへ戻る。
- duplicate / unknown Panel IDをdefaultへ戻す。
- system barを除いたworkspace clamp。

### 14.2 controller test

- `enter_layout_edit` でOverlayが表示される。
- edit mode外ではtouchを消費しない。
- edit mode中はappへtouchを渡さない。
- ACTION_CANCELでpreviewをrollbackする。
- camera eventでediting stateを終了する。
- Drop時にswap対象2 Panelの最終Variantが一致する。

### 14.3 runtime test

最低シナリオ:

1. 通常モードでMapのtap / pan / pinchが動作する。
2. 編集モードへ入る。
3. Map上の任意位置からdragできる。
4. Mapを右端へDropし、左右Panelがswapする。
5. 中央Panelは同じslotに残る。
6. 編集モードを終了後、各appが操作できる。
7. Cancelで開始時順序へ戻る。
8. Home / camera overrideで破綻しない。
9. SystemUI / launcher processが維持される。
10. logcatにFATAL EXCEPTIONがない。

通常画面長押し方式を試すphaseでは追加で確認する。

1. tapがMapへ届く。
2. timeout前のdragがMap panになる。
3. 2本指がMap pinchになる。
4. long press成立時にMapへ `ACTION_CANCEL` が届く。
5. pilfer後のMOVEがPanelだけを動かす。
6. app固有long pressとの競合結果を記録する。

### 14.4 evidence

- 編集前、drag中、Drop後、Cancel後のscreenshot
- Panel bounds / layer / current Variant dump
- root task stack bounds
- overlay state
- SystemUI / launcher PID before/after
- event / transition log
- recent FATAL EXCEPTION count
- Perfettoまたはframe timingによるdrag jank確認

## 15. 段階的実装

### Phase 1: 編集モードの直接swap

- 3固定slot
- 全画面編集Overlay
- drag対象だけsurface preview
- 静的slot Variant
- 直接swap
- Done / Cancel
- 永続化なし

完了条件:

- Mapの通常操作へ影響しない。
- 6 permutationを繰り返し切り替えられる。
- cancel / Home / camera overrideでmodelとsurfaceがずれない。

### Phase 2: 永続化とuser lifecycle

- user別order保存
- boot / SystemUI restart復元
- user switch
- model versioningとfallback

### Phase 3: 通常画面の全面長押し実験

- full-panel Spy task toolbar
- long press candidate
- pinch / pan arbitration
- pointer pilfer
- app long press競合評価

Phase 3が不安定でもPhase 1/2は独立して製品UX候補として残せる。

### Phase 4: 高度なreorder

- insertion reorder
- 他Panelのlive preview
- Panel数増加
- rotary / accessibility編集
- animation / jank最適化

## 16. 実装開始前の確認事項

- 実際の3 Panel IDとslot geometryを確定する。
- 直接swapと挿入reorderのどちらをUX要件とするか確定する。
- Homeでdefaultへ戻すか、最後のlayoutを維持するか確定する。
- camera override中の編集state policyを確定する。
- Android17 runtime flagを実機で確認する。
- 同一eventによる複数Panel transitionのWCT構成をtraceで確認する。
- `edit_overlay_panel` をworkspace全体へ広げた際のsystem bar touchabilityを確認する。

## 17. 判定まとめ

- Panel全面を長押しして移動する方式は、AAOS17のSpy windowとpointer pilferを使えば技術的には可能性が高い。
- ただしMapのlong pressと競合し、通常入力を壊さないためのgesture arbitrationが必要である。
- 明示的な編集モードなら、通常時のMap操作を完全に維持し、通常のtouchable DecorPanelだけでPanel全面dragを実装できる。
- 3固定slotでは、自由座標runtime Variantより静的slot Variantとlayout permutation eventが適している。
- drag中はSurface-only preview、Drop時はScalableUI VariantとWindowManager状態を同時に確定する。
- 第一実装は編集モード方式、通常画面長押しは後続の実験phaseとする。
