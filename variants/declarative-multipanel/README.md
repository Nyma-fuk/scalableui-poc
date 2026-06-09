# declarative-multipanel

`declarative-multipanel` は、`aaos-scalable-ui-specs` の初期 scope を AAOS15 LTS3 上で評価するための baseline です。

以前の `dynamic-workspace` は、任意 panel 追加、移動、resize、app picker、永続化まで一気に扱うため PoC として重くなっていました。この variant はそこをいったんリセットし、Passenger6 / MultiPanelLandscapeRRO に近い「RRO で panel と transition を宣言し、AAOS 側の ScalableUI orchestration に任せる」構成へ戻しています。

ただし、AAOS15 LTS3 では spec の一部を成立させるために最小限の `CarSystemUI` runtime 修正も含めます。主な理由は、DecorPanel-only transition、target panel routing、StubCarLauncher 分離を安定させるためです。

## 目的

- `sdk_car_x86_64.mk` を土台にする
- `CarSystemUI` / Framework / CarService の RRO で ScalableUI を有効化する
- 標準 `CarLauncher` を `StubCarLauncher` で置き換え、HOME UI と ScalableUI HMI を分離する
- spec の初期 workspace として `nav_panel` / `media_panel` / `user_slot_panel` を表示する
- `panel_app_grid` から user slot に app を投入できることを評価する
- `camera_priority_panel` / `edit_overlay_panel` などの event-driven panel transition を評価する

## 適用 patch

```text
variants/declarative-multipanel/patches/
  device-generic-car/
    0001-add-sdk_car_scalableui_declarative_multipanel_x86_64-product.patch
  packages-services-Car/
    0001-add-scalableui-declarative-multipanel-rro.patch
  packages-apps-Car-SystemUI/
    0001-add-scalableui-declarative-multipanel-runtime-routing.patch
```

この variant は古い `common/patches/packages-services-Car/*` や dynamic workspace 用 patch を必要としません。`scripts/apply_hmi_variant.sh declarative-multipanel` は、この variant だけ common runtime patch を適用しないようにしています。

## Build

```bash
bash workdir/scalableui-poc/scripts/apply_hmi_variant.sh declarative-multipanel
JOBS=8 workdir/scalableui-poc/scripts/build_hmi_modules.sh declarative-multipanel
AAOS_IMAGE_ROOT=/mnt/f/aaos_images JOBS=4 \
  workdir/scalableui-poc/scripts/build_hmi_emulator_images.sh declarative-multipanel
```

手動で build する場合:

```bash
set +u
source build/envsetup.sh
lunch sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug
set -u
m -j8 CarSystemUI CarFrameworkScalableUiDeclarativeMultipanelRRO CarServiceScalableUiDeclarativeMultipanelRRO CarSystemUIScalableUiDeclarativeMultipanelRRO StubCarLauncher
m -j4 emu_img_zip
```

## 評価

評価結果は `docs/evaluation_2026-06-09_ja.md` を参照してください。

この variant で確認するのは「ScalableUI が RRO 宣言を読み、panel / variant / transition / task placement を成立させること」です。

v12 smoke では、`nav_panel` / `media_panel` / `user_slot_panel`、AppGrid から user slot への Calendar routing、workspace page / resize / swap event、layout edit overlay、camera override を Windows host emulator で pass 確認しています。

grip の連続 resize、任意 app picker、panel add / remove、layout persistence は次 phase の対象です。
