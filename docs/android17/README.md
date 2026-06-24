# Android17 Docs

Android17 ベースへ ScalableUI PoC を移すための資料。

| 文書 | 何が理解できるか | 何ができるようになるか |
| --- | --- | --- |
| [aaos17_scalableui_development_flow_ja.md](aaos17_scalableui_development_flow_ja.md) | 標準 AAOS17 emulator target を維持する開発手順 | module build、`emu_img_zip`、runtime smoke へ段階的に進められる |
| [aaos17_scalableui_as_is_capability_ja.md](aaos17_scalableui_as_is_capability_ja.md) | AAOS17 ScalableUI の As-Is 実力、Panel/XML/Task event/Controller の全体像 | source 根拠をもとに ScalableUI でできること・できないことを説明できる |
| [official_scalableui_factcheck_ja.md](official_scalableui_factcheck_ja.md) | 公式 ScalableUI ページと AAOS17 source を照合した事実・詳細・想定 | HUN、SUW、system bar、event、runtime resize、drag、carousel の説明で断定できる範囲を分けられる |
| [scalableui_demos/README.md](scalableui_demos/README.md) | AAOS17 source 内の ScalableUI codelab / DEWD sample / minimized controls sample の構成 | 各 demo の画面構成、遷移、trigger、取り込み条件を demo 単位で確認できる |
| [../../variants/aaos17-codelab-threepanel-1080/README.md](../../variants/aaos17-codelab-threepanel-1080/README.md) | AAOS17 codelab ThreePanel RRO を 1920x1080 emulator に合わせた検証結果 | Home、KitchenSink、PaintBooth、grip tap、Home 復帰の UI 動作を再現できる |
| [android17_scalableui_delta_ja.md](android17_scalableui_delta_ja.md) | Android16 QPR2 PoC と Android17 ScalableUI の差分 | そのまま再適用できない patch を見分けられる |
| [android17_as_is_scalableui_migration_plan_ja.md](android17_as_is_scalableui_migration_plan_ja.md) | AAOS17 As-Is を崩さず PoC 差分を載せる計画 | 移植順序と検証観点を決められる |
| [aaos17_vs_android15_lts5_feature_delta_ja.md](aaos17_vs_android15_lts5_feature_delta_ja.md) | Android15 LTS5 と Android17 の AAOS 差分 | ScalableUI 以外の影響候補を洗い出せる |
