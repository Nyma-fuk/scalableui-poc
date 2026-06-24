# ScalableUI HMI Pattern Ideas

このページは、ScalableUI を使って検討できる HMI パターン案を整理するためのメモです。

重要:

- ここにある案は、すべてが現行 PoC として完成しているわけではありません。
- 現行 baseline は `declarative-multipanel` です。
- ほかの variant は historical / experimental / generated idea として扱います。
- Android17 で試す場合は、variant ごとの専用 product を増やす前に、標準 `sdk_car_x86_64` へ差分を重ねる方針を優先します。

## ScalableUI で考える軸

| 軸 | 選択肢 | 例 |
| --- | --- | --- |
| 主役 | map / media / app / calm / productivity | navigation-first, media cockpit |
| 固定 panel 数 | 1 / 2 / 3 / 4以上 | map + media + settings |
| overlay | All Apps / app_panel / camera / picker | central floating All Apps |
| routing | fixed panel / app_panel / priority panel | Settings は app_panel へ |
| transition | Window State / Surface animation | maximize, dismiss fade |
| custom度 | RROのみ / SystemUI event / controller / persistence | runtime panel assignment |

## Pattern 1: Declarative Multipanel Baseline

現行 PoC の基準です。

```text
+----------------------+----------------------+
|        map           |       media          |
|                      +----------------------+
|                      |     settings         |
+----------------------+----------------------+
```

用途:

- ScalableUI の RRO/XML、Panel、Variant、Transition、TaskPanel routing を確認する
- Android17 へ段階的に移植する基準にする
- All Apps、app_panel、固定 panel の境界を確認する
- 古い dynamic workspace 方式ではなく、AAOS17 標準 target への差分適用として説明する

Status:

- Active baseline / Porting target

参照:

- [declarative-multipanel](https://github.com/Nyma-fuk/scalableui-poc/blob/main/variants/declarative-multipanel/README.md)
- [AAOS17 Development Flow](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/android17/aaos17_scalableui_development_flow_ja.md)

## Pattern 2: Map-first Navigation

```text
+--------------------------------+--------------+
|                                | next event   |
|              map               +--------------+
|                                | media mini   |
|                                +--------------+
|                                | status       |
+--------------------------------+--------------+
```

向いている用途:

- navigation を主役にする
- 補助情報を右 rail に集約する
- route guidance / ETA / media mini を同時表示する

必要な検討:

- 右 rail を app panel にするか decor panel にするか
- map app が広い bounds と narrow rail の両方に耐えるか
- app_panel overlay が map を隠す時の focus / Home 復帰

Status:

- Generated idea

## Pattern 3: Media Dock

```text
+----------------------+----------------------+
|      map mini        |      now playing     |
+----------------------+                      |
|      queue / controls / radio               |
+---------------------------------------------+
```

向いている用途:

- entertainment / audio HMI 検討
- media control を広く見せる
- map を補助表示にする

必要な検討:

- media app の split-screen 適性
- parked / driving UX restriction
- media session / audio focus との整合

Status:

- Generated idea

## Pattern 4: Productivity Dashboard

```text
+----------------------+----------------------+
|      calendar        |       tasks          |
+----------------------+----------------------+
|      map mini        |       phone          |
+----------------------+----------------------+
```

向いている用途:

- schedule / task / call を並べる
- 運転前後や fleet 向けの dashboard を検討する

必要な検討:

- driving 中に表示してよい情報量
- app package の有無
- notification / HUN / focus との干渉

Status:

- Generated idea

## Pattern 5: App With Persistent Rail

```text
+--------------------------------+--------------+
|                                | shortcuts    |
|          app_panel             +--------------+
|                                | media mini   |
|                                +--------------+
|                                | home/status  |
+--------------------------------+--------------+
```

向いている用途:

- 通常 app を広く表示しつつ、最小限の system / media 操作を残す
- tablet 風の app focus HMI を試す

必要な検討:

- `app_panel` と rail の layer / focus
- Home 復帰時の rail 維持
- rail button からの ScalableUI event

Status:

- Generated idea

## Pattern 6: Floating Card

```text
+---------------------------------------------+
|                    map                      |
|        +-----------------------------+      |
|        | calendar / media card       |      |
|        +-----------------------------+      |
+---------------------------------------------+
```

向いている用途:

- map 背景の上に card 状の情報を浮かせる
- Corner / margin / Layer / alpha を活用する

必要な検討:

- card 内 app が狭い bounds で成立するか
- Surface animation で見た目だけ動かせる範囲
- background map と overlay の touch/focus 境界

Status:

- Generated idea

## Pattern 7: App Grid Hub

```text
+---------------------------------------------+
|                 app grid / hub              |
|        app icons / shortcuts / cards        |
+---------------------------------------------+
|              app_panel overlay              |
+---------------------------------------------+
```

向いている用途:

- 多くの app を素早く起動する導線を検討する
- fixed panel より launcher 的な操作を重視する

必要な検討:

- All Apps を常時表示にするか、floating overlay にするか
- app 起動後に hub を閉じるか残すか
- AppGrid が ScalableUI panel 上で前面を維持できるか

Status:

- Generated idea / 現行 baseline の `panel_app_grid` で一部評価

## Pattern 8: Calm Mode

```text
+---------------------------------------------+
|                                             |
|                  map / calm                 |
|          small media / status only          |
|                                             |
+---------------------------------------------+
```

向いている用途:

- 情報量を減らす
- driving 中の視覚負荷を下げる
- normal / calm / app focus の比較を行う

必要な検討:

- vehicle state event
- UX restriction
- hidden panel の復帰条件

Status:

- Generated idea

## Pattern 9: Parking / Charging Mode

```text
+----------------------+----------------------+
| charging / energy    | media / safe content |
+----------------------+----------------------+
| settings / schedule  | app shortcuts        |
+----------------------+----------------------+
```

向いている用途:

- 駐車中 / 充電中だけ情報量を増やす
- drive mode と parked mode の差分を見せる

必要な検討:

- vehicle state / power state event
- safety policy
- app lifecycle / resume

Status:

- Generated idea

## Pattern 10: Developer Cockpit

```text
+----------------------+----------------------+
| log / status         | app under test       |
+----------------------+----------------------+
| controls             | map / media          |
+----------------------+----------------------+
```

向いている用途:

- PoC 検証
- app under test と status を並べる
- screenshot / dumpsys / overlay state を取りやすくする

必要な検討:

- debug panel を app にするか decor にするか
- 配布用 image に入れないための product 分離
- telemetry / privacy

Status:

- Generated idea

## Pattern 11: Dual Display

向いている用途:

- driver display と passenger display の分離
- displayId 別 panel set
- passenger app と driver app の focus 分離

必要な検討:

- multi-display policy
- user switching
- input / audio / display area
- passenger display の safety 要件

Status:

- Generated idea / 要 source 再検証

## Pattern 12: Dynamic Workspace

任意 panel 追加、削除、移動、resize、app assignment、persistence を扱う方向です。

できることの候補:

- runtime panel creation
- app picker
- panel assignment persistence
- horizontal viewport
- drag resize

重要:

- ScalableUI 標準だけでは完結しません。
- `StateManager.addState(...)` は存在しますが、UI / geometry / persistence は custom 実装です。
- 現行 baseline ではありません。

Status:

- Historical / experimental

参照:

- [dynamic-workspace notes](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/historical/dynamic_workspace_notes_ja.md)
- [runtime panel control](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/workflows/runtime_panel_control_ja.md)

## Pattern を実装候補へ進める条件

1. ScalableUI 標準でできる範囲を明確にする。
2. PoC custom が必要な範囲を明確にする。
3. AAOS17 source で関連 class を確認する。
4. module build / image build / emulator smoke を取る。
5. `docs/workflows/variant_status_ja.md` を更新する。
