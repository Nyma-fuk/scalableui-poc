# Runtime Panel Control

> Source verification: この文書は `widget-workspace` の historical PoC メモです。AAOS/AOSP live source で確認できる標準機能と、過去 patch / PoC custom 実装を分けて読んでください。詳細は [AOSP Source Verification](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/verification/aosp_source_verification_ja.md) を参照してください。

## 目的

`widget-workspace` は、当時ユーザーが実行時に「どのアプリを、どの Panel に表示するか」を選べる HMI として更新した実験です。

以前の構成では左側の `PanelMenuActivity` が常時表示され、アプリ選択ボタンは固定で `workspace_panel` へルーティングしていました。
当時の最終構成では、常時表示されるのは小さな `Panel Control` ボタンだけです。
ユーザーがこのボタンを押した時だけ、隠れていた `panel_menu` が開きます。

## 操作モデル

1. `panel_menu_button` に表示される `Panel Control` を押す。
2. 隠れていた `panel_menu` が表示される。
3. `Workspace`、`Controls`、`Status`、`Fullscreen` から表示先を選ぶ。
4. `Widgets`、`Map`、`G Ball`、`Media`、`Tasks` から表示したいアプリを選ぶ。
5. 選択されたアプリが指定 Panel に起動し、メニューは閉じる。

## 実装メモ

`PanelMenuActivity` は選択された表示先を Intent extra と data URI に入れてアプリを起動します。

```text
com.android.car.scalableui.extra.TARGET_PANEL_ID=<panel_id>
scalableui-hmi://panel-launch?target_panel=<panel_id>
```

SystemUI 側の `PanelAutoTaskStackTransitionHandlerDelegate` は extra を優先し、extra が `TaskInfo.baseIntent` で落ちる場合は data URI を fallback として使います。
該当する `TaskPanel` が決まったら、その panel を対象にした `_System_TaskOpenEvent` / launch-root / task placement 方針へ渡します。
これにより、同じアプリでもユーザーが選んだ Panel に表示できます。

All Apps から起動されたアプリは `com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL=true` を持つため、固定 Panel ではなく fullscreen の `app_panel` を優先します。
この経路でも `FLAG_ACTIVITY_MULTIPLE_TASK` は付けず、`FLAG_ACTIVITY_CLEAR_TOP` と `FLAG_ACTIVITY_SINGLE_TOP` で既存 task / Activity の再利用を優先します。
同じ component の task がすでに ScalableUI panel 上にある場合は、新規 instance を増やさず既存 task を活用する方針です。

検証注記:

- AOSP の `WindowContainerTransaction` には `reparent()` / `reparentTasks()` が存在する
- Android17公式`TaskBehavior`には新規task launch用の`REPARENT_TO_SOURCE`がある
- この文書の `WindowContainerToken` ベース reparent は `widget-workspace` 実験時の PoC / patch 方針である
- 新規task launch policyと、Panel間の任意な既存task reparent editorを同一視しない
- 「Panel にアプリを表示」は実装上 `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` である

## Launcher が背後で動く理由

AAOS の ScalableUI は Launcher を完全に消して置き換えているわけではありません。
`com.android.car.carlauncher/.AppGridActivity` は All Apps を表示する通常の Activity であり、ScalableUI の `panel_app_grid` に割り当てられています。

つまり Launcher は「ScalableUI の外側にある別物」ではなく、ScalableUI が管理する Panel の中に表示されるアプリのひとつです。
Home、All Apps、通常アプリ起動の仕組みは AAOS Launcher / WindowManager / SystemUI の既存経路を使い、その表示先を ScalableUI が Panel として制御します。

この構造により、次のように経路を分けています。

- Panel Control 経由: `TARGET_PANEL_ID` を見て、ユーザーが選んだ Panel へ表示する。
- All Apps 経由: fullscreen `app_panel` に表示し、Panel 内の既存アプリ配置をなるべく維持する。
- 固定 Panel の初期表示: RRO の `config_default_activities` で起動する。

## Home / QuickStep の扱い

AAOS では、通常の Android と同じく `HOME` category を持つ Activity が常にシステムの戻り先として必要です。
そのため、Home アプリ自体をゼロにすると WindowManager / SystemUI の前提を崩しやすくなります。

この PoC では `CarLauncher` を Home として起動し続ける代わりに、軽量な `ScalableUiHmiHomeDemoApp` を追加しています。
`HomeActivity` は黒背景の no-op Home として動き、表示上の HMI は ScalableUI の panel 群が担います。

さらに SystemUI は `config_recentsComponentName` を見て QuickStep / Recents 用 service を bind します。
初期状態ではここが `com.android.car.carlauncher/.recents.CarRecentsActivity` だったため、Home を置き換えても `CarQuickStepService` 経由で `com.android.car.carlauncher` process が残りました。
現在は `ScalableUiHmiFrameworkConfigRRO` で `config_recentsComponentName` を `com.android.car.scalableui.hmi.home/.NoOpRecentsActivity` に差し替え、`NoOpQuickStepService` を ScalableUI Home APK 側で受ける構成にしています。

このため、`CarLauncher` APK は AppGrid / All Apps のために image 内へ残しますが、boot 直後に Home / QuickStep として常駐しない状態を目指しています。

## 注意点

高負荷アプリを同じ Activity component で複数起動すると、CPU / GPU / memory / decoder / surface を二重に消費する可能性があります。
そのため当時の PoC は safety-first の runtime policy とし、Panel Control と All Apps の起動では `FLAG_ACTIVITY_MULTIPLE_TASK` を使いませんでした。
代わりに `FLAG_ACTIVITY_CLEAR_TOP` と `FLAG_ACTIVITY_SINGLE_TOP` を付け、同じ task 内に同じ Activity instance が積み重なることも抑えます。

このhistorical PoCでは、同じappを別Panelに表示したい場合、既存taskがあればcustom routingで移動する方針でした。
完全に独立した複数instanceを評価する場合は、別APK / 別package / 別taskAffinityで評価用appを用意する方が、実機HMIのresource riskと切り分けやすくなります。
