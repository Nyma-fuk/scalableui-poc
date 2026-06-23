# Legacy Root Patches

この directory は、初期 ScalableUI PoC / dynamic-workspace 系で使った root-level patch を保持する場所である。

## 現在の扱い

| Path | Status | 備考 |
| --- | --- | --- |
| `device-generic-car/` | Historical | 初期 PoC product 追加 patch |
| `packages-services-Car/` | Historical | 初期 RRO / demo app patch |
| `packages-apps-Car-SystemUI/` | Historical / experimental | AppGrid routing、grip、runtime layout などの実験 |
| `packages-apps-Car-Launcher/` | Historical / experimental | All Apps launch routing 実験 |
| `packages-apps-Car-systemlibs-car-scalable-ui-lib/` | Historical / experimental | runtime layout variant override 実験 |

## Active baseline との関係

現行 baseline は次を正とする。

```text
variants/declarative-multipanel/patches/
```

root-level `patches/` は、過去の実装を比較・回収するための資料であり、現行 baseline にそのまま混ぜない。

## Android17 方針

Android17 では、root-level patch を機械的に再適用しない。

1. [docs/aaos17_scalableui_source_verification_ja.md](../docs/aaos17_scalableui_source_verification_ja.md) で source 事実を確認する。
2. [docs/aaos17_scalableui_development_flow_ja.md](../docs/aaos17_scalableui_development_flow_ja.md) の順に RRO / launcher / SystemUI 差分を小さく載せる。
3. build と emulator smoke で確認する。
