# ScalableUI PoC No-Grip Variant

この variant は、`grip` を使わずに 3 つの panel 領域だけで固定 HMI を試すための構成です。

## 構成

- 左: `map_panel`
- 右上: `calendar_panel`
- 右下: `radio_panel`
- fullscreen overlay: `panel_app_grid`
- generic fullscreen panel: `app_panel`

`decor_vertical_grip_panel` / `decor_horizontal_grip_panel` と controller は使いません。
panel は固定レイアウトで、split を動かす UI は持ちません。

## 適用手順

前提:
- AAOS15 系 checkout
- この repository を checkout 内の `workdir/scalableui-poc` に置いている

手順:
1. `bash workdir/scalableui-poc/variants/no-grip/scripts/apply_patches.sh`
2. `lunch sdk_car_scalableui_nogrip_x86_64-trunk_staging-userdebug`
3. build

この variant の script は次を適用します。
- `variants/no-grip/patches/device-generic-car/`
- `variants/no-grip/patches/packages-services-Car/`
- 共通 patch として root の `packages/apps/Car/SystemUI` / `packages/apps/Car/Launcher`

## 差分の考え方

- `grip` 版と共存できるように product 名を分けている
- `All apps` からの `app_panel` 優先起動は共通で使う
- layout は固定で、調整点を減らして panel 配置そのもののユースケース確認をしやすくする

## Tag 運用メモ

tag は snapshot 管理に使い、variant 自体は directory で分ける。

おすすめ:
- `grip-v1`
- `no-grip-v1`
- `no-grip-v2`

variant を増やすたびに directory を追加し、節目ごとに tag を打つと追いやすいです。
