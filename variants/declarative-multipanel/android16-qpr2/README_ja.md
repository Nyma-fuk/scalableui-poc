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
```

結果:

```text
#### build completed successfully (53:44 (mm:ss)) ####
```

## 未確認事項

- emulator boot と実機 runtime 動作
- target panel extra / URI 指定による TaskPanel ルーティングの end-to-end 動作
- Decor-only transition の見た目と SurfaceControl 更新順
- full image build と SDK system image packaging
