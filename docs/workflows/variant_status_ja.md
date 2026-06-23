# Variant Status

この文書は、各variantの現在の扱いを明確にするための一覧である。

## Status定義

| Status | 意味 |
| --- | --- |
| Active baseline | 現行PoCとして保守する |
| Porting target | Android17移植で直接扱う |
| Historical / experimental | 正しい実験記録を含むが、現行baselineではない |
| Generated idea | HMI案の生成物。再利用する場合は再検証が必要 |

## 一覧

| Variant / area | Status | 備考 |
| --- | --- | --- |
| `declarative-multipanel` | Active baseline / Porting target | 現行baseline。Android17では標準 `sdk_car_x86_64` にPoC差分を載せる |
| `dynamic-workspace` | Historical / experimental | runtime panel生成、app assignment、resize、persistence実験 |
| `editable-home` | Historical / experimental | 3 panel home、grip resize、assignment persistence実験 |
| `widget-workspace` | Historical / experimental | panel menuによるapp routing実験 |
| `widget-layout-lab` | Historical / experimental | widget配置パターン切替実験 |
| `no-grip` | Historical / experimental | gripなし固定3panel実験 |
| `fixed-3zone` | Generated idea | AAOS15向けvariant suite案 |
| `map-first` | Generated idea | AAOS15向けvariant suite案 |
| `media-dock` | Generated idea | AAOS15向けvariant suite案 |
| `productivity-dashboard` | Generated idea | AAOS15向けvariant suite案 |
| `app-with-rail` | Generated idea | AAOS15向けvariant suite案 |
| `floating-card` | Generated idea | AAOS15向けvariant suite案 |
| `app-grid-hub` | Generated idea | AAOS15向けvariant suite案 |
| `calm-mode` | Generated idea | AAOS15向けvariant suite案 |
| `parking-mode` | Generated idea | AAOS15向けvariant suite案 |
| `developer-cockpit` | Generated idea | AAOS15向けvariant suite案 |
| `dual-display` | Generated idea | AAOS15向けvariant suite案 |
| `showcase-modes` | Generated idea | AAOS15向けvariant suite案 |

## 注意

- Historical / generated variantの記述は削除しない。正しい実験結果や設計案を含むため。
- ただし、現行PoCやAndroid17移植の根拠として扱う場合は、必ず対象AAOS branchのsourceとbuild artifactで再検証する。
- Android17では、variantごとの専用productを増やすより、標準 `sdk_car_x86_64` へ差分を載せる方針を優先する。
