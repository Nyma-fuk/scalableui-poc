# Runtime Panel Control

## 目的

`widget-workspace` は、ユーザーが実行時に「どのアプリを、どの Panel に表示するか」を選べる HMI として更新しています。

以前の構成では左側の `PanelMenuActivity` が常時表示され、アプリ選択ボタンは固定で `workspace_panel` へルーティングしていました。
現在の構成では、常時表示されるのは小さな `Panel Control` ボタンだけです。
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
該当する `TaskPanel` が決まったら、`WindowContainerToken` ベースで起動タスクを reparent します。
これにより、同じアプリでもユーザーが選んだ Panel に表示できます。

All Apps から起動されたアプリは `com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL=true` を持つため、固定 Panel ではなく fullscreen の `app_panel` を優先します。
この経路でも `FLAG_ACTIVITY_MULTIPLE_TASK` は付けず、`FLAG_ACTIVITY_CLEAR_TOP` と `FLAG_ACTIVITY_SINGLE_TOP` で既存 task / Activity の再利用を優先します。
同じ component の task がすでに ScalableUI panel 上にある場合は、新規 instance を増やすのではなく、既存 task を選択された Panel へ reparent する方針です。

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
そのため現在の PoC は safety-first の runtime policy とし、Panel Control と All Apps の起動では `FLAG_ACTIVITY_MULTIPLE_TASK` を使いません。
代わりに `FLAG_ACTIVITY_CLEAR_TOP` と `FLAG_ACTIVITY_SINGLE_TOP` を付け、同じ task 内に同じ Activity instance が積み重なることも抑えます。

同じ app を別 Panel に表示したい場合は、既存 task があればそれを移動します。
完全に独立した複数 instance を評価したい場合は、別 APK / 別 package / 別 taskAffinity で評価用 app を用意する方が、量産HMIの resource risk と切り分けやすいです。
