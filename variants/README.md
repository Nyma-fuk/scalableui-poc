# Variants

この directory には、現行 baseline、過去実験、generated HMI idea が混在している。

## 読み方

| 区分 | 対象 | 扱い |
| --- | --- | --- |
| Active baseline | `declarative-multipanel` | 現行 PoC として保守する |
| AAOS17 source sample validation | `aaos17-codelab-threepanel-1080` | AAOS17 codelab ThreePanel RRO を 1920x1080 emulator で動かす検証用 |
| Historical / experimental | `dynamic-workspace`, `editable-home`, `widget-workspace`, `widget-layout-lab`, `no-grip` | 正しい実験記録として残すが、現行 baseline ではない |
| Generated idea | `fixed-3zone`, `map-first`, `media-dock`, `productivity-dashboard`, `app-with-rail`, `floating-card`, `app-grid-hub`, `calm-mode`, `parking-mode`, `developer-cockpit`, `dual-display`, `showcase-modes` | HMI 案として残す。再利用時は source / build / runtime で再検証する |

詳細な status は [../docs/workflows/variant_status_ja.md](../docs/workflows/variant_status_ja.md) を参照する。

## Android17 方針

Android17 では variant ごとの専用 product を増やすより、標準 `sdk_car_x86_64-trunk_staging-userdebug` に PoC 差分を重ねる方針を優先する。

```text
sdk_car_x86_64-trunk_staging-userdebug
  + ScalableUI PoC RRO
  + ScalableUiStubCarLauncher
  + 必要最小限の CarSystemUI 差分
```

## 注意

- generated variant の `README.md` に書かれた product / lunch target は、AAOS15 向け generated idea として扱う。
- 現行 PoC を触る場合は、まず `declarative-multipanel` を見る。
- historical variant の正しい知見は削除しない。ただし Android17 移植の根拠にする場合は再検証する。
