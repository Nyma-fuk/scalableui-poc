# ScalableUI PoC HMI 仕様メモ No-Grip Variant

## 目的

`sdk_car_scalableui_nogrip_x86_64` 上で、ScalableUI の panel 制御だけを使い、
grip なしの固定 3 分割 HMI を作る。

## 構成

- `decor_left_background_panel`
  - 左半分の背景
- `map_panel`
  - 左側 map
- `calendar_panel`
  - 右上
- `radio_panel`
  - 右下
- `panel_app_grid`
  - All apps overlay
- `app_panel`
  - 固定 panel 以外の fullscreen 起動先

## レイアウト

```text
+----------------------+----------------------+
|  left background     |    calendar_panel    |
|   +--------------+   |                      |
|   |  map_panel   |   |                      |
|   +--------------+   +----------------------+
|                      |                      |
|                      |      radio_panel     |
|                      |                      |
+----------------------+----------------------+
```

右側は `50/50` の固定 split、左右は `50/50` の固定 split。
grip は存在しないため、panel variant の切り替えも行わない。

## 共通仕様

- `All apps` からの起動は `app_panel` 優先
- `All apps` 起動後は overlay を閉じる
- `Calendar` は product 側で追加
- `Radio` は既存 `CarRadioApp` を利用

## 主な違い

`grip` 版との違い:
- `window_states` に grip panel を含めない
- grip controller xml を持たない
- panel xml は固定 variant のみ
- grip 用 dimen / layer / drawable overlay を持たない
