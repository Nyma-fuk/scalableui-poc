# AAOS17 ScalableUI Demo Index

AAOS17 source に含まれる ScalableUI demo / sample RRO を demo ごとに分けて解析した資料。各文書は、全体像、画面構成図、画面遷移、trigger、関係 class / method、素の AAOS17 emulator への取り込み可否をまとめる。

## Demo List

| 種別 | Demo | 説明 | 文書 |
| --- | --- | --- | --- |
| codelab | `BoundsExampleRRO` | background_panel の上で app_panel の fullscreen / half-screen / system-bar付き bounds を切り替える構成。 | [boundsexample.md](boundsexample.md) |
| codelab | `DDPanelRRO` | nav_panel と app_panel を分け、panelId 付き task open で個別に開く構成。 | [ddpanel.md](ddpanel.md) |
| codelab | `OnePanelRRO` | 1つの app_panel だけで TaskPanel の open / close を確認する最小構成。 | [onepanel.md](onepanel.md) |
| codelab | `SplitPanelHorzRRO` | 複数 TaskPanel と grip / overlay DecorPanel を組み合わせ、split、drag、task switch を表現する構成。 | [splitpanelhorz.md](splitpanelhorz.md) |
| codelab | `SplitPanelLandRRO` | 複数 TaskPanel と grip / overlay DecorPanel を組み合わせ、split、drag、task switch を表現する構成。 | [splitpanelland.md](splitpanelland.md) |
| codelab | `SplitPanelRRO` | 複数 TaskPanel と grip / overlay DecorPanel を組み合わせ、split、drag、task switch を表現する構成。 | [splitpanel.md](splitpanel.md) |
| codelab | `ThreePanelRRO` | 複数 TaskPanel と grip / overlay DecorPanel を組み合わせ、split、drag、task switch を表現する構成。 | [threepanel.md](threepanel.md) |
| codelab | `TwoPanelRRO` | map_panel を常時表示し、app_panel を task open で前面表示する 2 panel 構成。 | [twopanel.md](twopanel.md) |
| codelab | `TwoPanelRROCast` | map_panel を常時表示し、app_panel を task open で前面表示する 2 panel 構成。 | [twopanelcast.md](twopanelcast.md) |
| codelab | `TwoPanelRROSafeBounds` | map_panel を常時表示し、app_panel を task open で前面表示する 2 panel 構成。 | [twopanelsafebounds.md](twopanelsafebounds.md) |
| codelab | `TwoPanelWithInsetsRRO` | map_panel を常時表示し、app_panel を task open で前面表示する 2 panel 構成。 | [twopanelwithinsets.md](twopanelwithinsets.md) |
| systemui-sample | `DEWDDynamic` | orientation や resource qualifier により window_states を切り替える DEWD dynamic 構成。 | [dewd-dynamic.md](dewd-dynamic.md) |
| systemui-sample | `DEWDLand` | landscape 向けに map、widget、app の基本 panel を配置する構成。 | [dewd-land.md](dewd-land.md) |
| systemui-sample | `DEWDPort` | portrait 向けに app drawer、app grid、map、widget、calm mode、styled view を panel 化する構成。 | [dewd-port.md](dewd-port.md) |
| systemui-sample | `DEWDSplit` | app_panel と map_panel を split 表示し、grip_bar で drag / immersive 遷移する構成。 | [dewd-split.md](dewd-split.md) |
| systemui-sample | `MinimizedControlsDynamic` | floating app、map、widget、minimized media / dialer controls、bar panels を ScalableUI panel 化する構成。 | [minimized-controlsdynamic.md](minimized-controlsdynamic.md) |

## Source roots

- `packages/apps/Car/References/scalable-ui/codelab`
- `packages/apps/Car/SystemUI/samples`

## DEWD sample の読み方

`DEWD*` と `MinimizedControlsDynamic` は、demo directory だけで完結する RRO ではなく、共通 resource library を重ねて構成される。

```text
DEWDCommon
├── common panels
│   ├── assistant_panel
│   ├── suw_panel
│   ├── status_bar / nav_bar / hun_panel
│   ├── projected_panel
│   └── camera_panel
└── common controllers
    ├── app_grid_controller
    ├── assistant_controller
    ├── calm_mode_controller
    ├── camera_controller
    ├── map_controller
    ├── projected_controller
    ├── suw_controller
    └── widget_controller

DEWDDynamic / MinimizedControlsDynamic
├── dewd-res-common
├── dewd-port-res-base
└── dewd-land-res-base
```

そのため、各 `DEWD*` 文書では demo 固有 XML を中心に説明し、共通 panel / controller は `DEWDCommon` 由来の部品として読む。素の AAOS17 emulator に取り込む場合も、RRO 単体ではなく `Android.bp` に記載された static library と required property を合わせて確認する。

## 読み方

1. まず各 demo の「全体構成」と「画面イメージ」で狙いを把握する。
2. 次に「主な画面遷移とトリガー」で、どの event がどの variant を動かすかを見る。
3. 最後に「素の AAOS17 emulator への取り込み可否」で、build / install / overlay enable に必要な条件を確認する。
