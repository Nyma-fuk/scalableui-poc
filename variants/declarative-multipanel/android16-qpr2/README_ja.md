# Android 16 QPR2 移植メモ

このディレクトリは、既存の Android 15 / AAOS LTS3 向け PoC 構成を壊さずに、
`android16-qpr2-release` ベースへ移植するための差分を分離したものです。

## ベース

- AOSP manifest branch: `android16-qpr2-release`
- lunch target:
  `sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug`
- checkout path used during verification:
  `/home/y-fuk/work/android16-qpr2-release`

## パッチ

以下の順に、対応する AOSP サブプロジェクトのルートで適用します。

```sh
git -C device/generic/car apply \
  /home/y-fuk/work/scalableui-poc/variants/declarative-multipanel/android16-qpr2/patches/device-generic-car/0001-add-sdk-car-scalableui-declarative-multipanel-x86-64-product.patch

git -C packages/services/Car apply \
  /home/y-fuk/work/scalableui-poc/variants/declarative-multipanel/android16-qpr2/patches/packages-services-Car/0001-add-scalableui-declarative-multipanel-rro.patch

git -C packages/apps/Car/SystemUI apply \
  /home/y-fuk/work/scalableui-poc/variants/declarative-multipanel/android16-qpr2/patches/packages-apps-Car-SystemUI/0001-add-scalableui-declarative-multipanel-runtime-routing.patch

git -C packages/apps/Car/Launcher apply \
  /home/y-fuk/work/scalableui-poc/variants/declarative-multipanel/android16-qpr2/patches/packages-apps-Car-Launcher/0001-mark-appgrid-launch-source.patch
```

## Android 15 版からの主な追従点

- `packages/apps/Car/SystemUI` の ScalableUI 初期化が Android16 側で
  `ScalableUIDumpsys` や `Lazy<PanelAutoTaskStackTransitionHandlerDelegate>` を使う形へ
  変わっているため、既存の broadcast bridge をその構造へ合わせて移植した。
- `PanelConfigReader` の `PanelPool.setDelegate` が `id` と `type` を受け取る形に
  なっているため、DecorPanel 判定を Android16 の delegate 形状へ合わせた。
- `PanelAutoTaskStackTransitionHandlerDelegate` は、初回起動時の target panel 指定が
  `shouldHandleByPanels()` で落ちないよう、Intent extra / URI query から panel id を
  解釈する処理を Android16 実装へ合わせて追加した。
- All Apps から既存 panel 上のアプリを再起動した場合に、その panel を fullscreen
  variant へ遷移させるため、AppGrid 表示中の task open event に `source=app_grid`
  token を追加した。
- All Apps の再タップ close は、`panel_app_grid` の可視状態に応じて
  `_System_TaskOpenEvent` に `action=open` / `action=close` token を付ける形にした。
- Android16 既存の `StubCarLauncher` module と名前が衝突するため、PoC 側の module 名を
  `ScalableUiDeclarativeMultipanelStubCarLauncher` に変更した。
- `sdk_car_x86_64` 継承元の property 配置が Android16 の artifact path enforcement に
  引っかかるため、既存の Android16 `sdk_car_dewd_x86_64` と同様に
  `PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := false` を設定した。

## ビルド確認

2026-06-10 に以下を実行し、成功を確認した。

```sh
source build/envsetup.sh
lunch sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug
m -j8 \
  ScalableUiDeclarativeMultipanelStubCarLauncher \
  CarSystemUIScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarSystemUI
m -j4 emu_img_zip
```

結果:

```text
#### build completed successfully ####
```

## 実機能確認

2026-06-10 に `emu_img_zip` の full image build、Windows emulator boot、
初期パネル表示、既存 AAOS AppGrid の centered floating panel 表示、All Apps の
再タップ close、panel 外タップ close、app picker panel、customizable slot への
選択アプリ配置、既存 panel アプリ再起動時の fullscreen 化、Home 復帰を確認した。

詳細は [docs/evaluation_2026-06-10_ja.md](docs/evaluation_2026-06-10_ja.md) を参照。

注意:

- Android16 QPR2 の ScalableUI XML parser は `<Panel>` ではなく
  `<TaskPanel>` / `<DecorPanel>` を要求する。
- 旧 `bool/config_enableScalableUI` は Android16 の `Flag.ScalableUIEnabled`
  fallback resource ではないため、PoC RRO では `bool/scalable_ui` を overlay する。
- 下部 All Apps ボタンは `PanelTriggerActivity` で target panel event を発生させ、
  実体の `AppGridActivity` は `panel_app_grid` の default activity として起動する。
- All Apps は `panel_app_grid` の layer 90 で中央表示し、背面の
  `app_grid_scrim_panel` が panel 外タップを `close_app_grid` ScalableUI event に変換する。
- All Apps のアイコン再タップは `PanelAutoTaskStackTransitionHandlerDelegate` が
  `action=close` token つき event に変換し、XML transition で閉じる。
- customizable slot の `Choose app` は `app_picker_panel` を開き、選択結果は
  `user_slot_panel` から起動する。`user_slot_panel` には `TaskBehavior
  newTaskLaunchPolicy="REPARENT_TO_SOURCE"` を設定している。
