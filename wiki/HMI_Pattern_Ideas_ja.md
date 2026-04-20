# ScalableUI HMI Pattern Ideas

このページは、ScalableUI を使ってどのような HMI 構成を作れるかを考えるためのアイデア集です。

目的は、単に「今の PoC をどう触るか」ではなく、ScalableUI の panel / variant / transition / overlay を組み合わせると、どんな車載 HMI の方向性を試せるかを見渡せるようにすることです。

このページの 12 案は、`variants/<variant>/` 配下に generated patch として展開済みです。適用手順と product / lunch target の一覧は [HMI Variant Suite](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/hmi_variant_suite_ja.md) を参照してください。

## 前提

このページでは、次の前提で考えます。

- AAOS15 の Car SystemUI 上で ScalableUI を有効化している
- HMI は主に RRO の XML と product 定義で構成する
- 固定表示したい app は persistent panel に割り当てる
- 一時的に前面表示したい app は fullscreen overlay や launch root panel に流す
- 必要な場合だけ SystemUI / Launcher 側に小さな routing 変更を入れる

ScalableUI は app の中身を作り替える仕組みではありません。

得意なこと:

- 複数 app / decor view の表示領域を分ける
- panel の表示 / 非表示、位置、サイズ、layer、focus を切り替える
- map、media、calendar、radio などを常時表示領域に固定する
- All apps や generic app を fullscreen overlay として出す
- grip や event によって layout variant を切り替える
- calm mode や demo mode のような画面モードを作る

苦手なこと:

- app 内部の UI 部品を直接並び替える
- app 側の `singleTask` など launch mode を完全に無視する
- 複雑な business logic を XML だけで実装する
- safety / driver distraction 要件を自動的に満たす
- camera / sensor / vehicle state 連動を event source なしで実現する

## HMI を考えるときの軸

ScalableUI の HMI は、次の軸で考えると整理しやすいです。

| 軸 | 選択肢 | 例 |
| --- | --- | --- |
| 画面の主役 | map / media / productivity / app launcher / calm | navigation first HMI、media cockpit |
| 固定 panel 数 | 1 / 2 / 3 / 4 以上 | map + media、map + calendar + radio |
| 操作方式 | fixed / grip / button event / mode switch | no-grip 固定 split、drag resize |
| overlay | なし / All apps / fullscreen app / modal controls | app grid、settings overlay |
| app routing | fixed panel 優先 / fullscreen 優先 / app ごとに分岐 | All apps からは `app_panel` 優先 |
| decor | 背景 / rail / separator / card / overlay shade | 左背景 panel、floating card |
| variant 管理 | root variant / per use-case variant / tag snapshot | `grip-v1`、`no-grip-v1` |

最初に決めるべきことは、「常に見えていてほしい情報」と「必要なときだけ前面に出ればよい情報」を分けることです。

常に見せたいものは fixed panel に向いています。

必要なときだけ見せたいものは fullscreen overlay や modal panel に向いています。

## Pattern 1: 固定 3 領域 cockpit

現在の PoC に近い構成です。

```text
+----------------------+----------------------+
|        map           |      calendar        |
|                      |                      |
|                      +----------------------+
|                      |        radio         |
|                      |                      |
+----------------------+----------------------+
```

向いている用途:

- navigation を常時見たい
- 右側に予定や media / radio を固定したい
- PoC の最初の baseline を作りたい

panel 構成:

- `map_panel`
- `calendar_panel`
- `radio_panel`
- `app_panel`
- `panel_app_grid`
- grip variant なら `decor_vertical_grip_panel` / `decor_horizontal_grip_panel`

カスタマイズしやすい点:

- 右上 app を Calendar から Settings / Music / Phone に変える
- 右下 app を Radio から Media に変える
- 左右 split を `50/50`、`60/40`、`70/30` に変える
- grip を残すか、no-grip 固定 layout にする

実装難易度:

- XML / RRO だけでもかなり変更できる
- All apps から fixed panel app を fullscreen 優先にしたい場合は Launcher / SystemUI 側 routing の工夫が必要

variant 名の例:

- `fixed-3zone-v1`
- `map-calendar-radio-v1`
- `no-grip-3zone-v1`

## Pattern 2: Map-first navigation cockpit

map を主役にして、右側を細い information rail にする構成です。

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

- navigation 体験を最優先したい
- map は広く、補助情報は右 rail にまとめたい
- route guidance、ETA、media mini player、vehicle status を同時に見せたい

panel 構成:

- `map_panel`
- `right_top_panel`
- `right_middle_panel`
- `right_bottom_panel`
- `app_panel`
- 必要に応じて `decor_right_rail_panel`

カスタマイズしやすい点:

- 右 rail を 2 分割または 3 分割にする
- 右 rail を app 固定ではなく decor + shortcut にする
- map を fullscreen に近い大きさにして corner / margin を減らす
- `app_panel` を map の上に fullscreen overlay として出す

実装難易度:

- 右 rail の app 数を増やすだけなら XML / RRO 中心
- 右 rail の shortcut や custom view を作り込む場合は layout resource の追加が必要

variant 名の例:

- `map-first-v1`
- `navigation-rail-v1`
- `wide-map-v1`

## Pattern 3: Media-first cockpit

media を主役にして、map や予定は compact にする構成です。

```text
+----------------------+----------------------+
|      map mini        |      now playing     |
|                      |                      |
+----------------------+                      |
|      queue / radio / controls               |
|                                             |
+---------------------------------------------+
```

向いている用途:

- entertainment / audio demo を重視したい
- media app の視認性を高めたい
- map は補助情報として小さく表示できればよい

panel 構成:

- `media_panel`
- `map_panel`
- `radio_panel` または `queue_panel`
- `calendar_panel` または `context_panel`
- `app_panel`

カスタマイズしやすい点:

- bottom に media control を広く取る
- right side に album art / queue を置く
- map を左上 mini panel にする
- radio と media app のどちらを persistent にするか選ぶ

実装難易度:

- app の割り当て変更は XML / RRO 中心
- media app の内部 UI が split に向いていない場合、bounds だけでは見え方に限界がある

variant 名の例:

- `media-first-v1`
- `media-dock-v1`
- `entertainment-cockpit-v1`

## Pattern 4: Productivity assistant dashboard

予定、タスク、通話、メモなどを assistant 的に並べる構成です。

```text
+----------------------+----------------------+
|      calendar        |       tasks          |
+----------------------+----------------------+
|      map mini        |       phone          |
+----------------------+----------------------+
|              app / detail overlay           |
+---------------------------------------------+
```

向いている用途:

- schedule / task / call を見ながら運転前後の操作をしたい
- calendar や communication app の見え方を検証したい
- fleet / business 向けの HMI を試したい

panel 構成:

- `calendar_panel`
- `task_panel`
- `map_panel`
- `phone_panel`
- `app_panel`

カスタマイズしやすい点:

- 2x2 grid にする
- map を左下 mini にする
- detail 操作は `app_panel` fullscreen へ逃がす
- driving 中は productivity panel を閉じる calm variant を用意する

実装難易度:

- 固定 app の package が product に入っていれば XML / RRO 中心
- Calendar 以外の app を追加する場合は product package の追加が必要
- 運転中制限を考える場合は policy / UX restriction との整理が必要

variant 名の例:

- `productivity-dashboard-v1`
- `assistant-grid-v1`
- `calendar-task-v1`

## Pattern 5: Fullscreen app + persistent side rail

任意 app を fullscreen に近いサイズで出しながら、横に小さな常時 rail を残す構成です。

```text
+--------------------------------+--------------+
|                                | shortcuts    |
|                                +--------------+
|          app_panel             | media mini   |
|                                +--------------+
|                                | home/status  |
+--------------------------------+--------------+
```

向いている用途:

- app の操作領域を広く取りたい
- それでも media / home / status は常に見せたい
- tablet 的な HMI を試したい

panel 構成:

- `app_panel`
- `side_rail_panel`
- `media_mini_panel`
- `status_panel`
- `panel_app_grid`

カスタマイズしやすい点:

- `app_panel` を `90%` 幅にする
- right rail を decor layout にする
- side rail の button から All apps / Home / media を開く
- rail を左側に置くか右側に置くか変える

実装難易度:

- rail が decor だけなら XML / layout resource 中心
- rail の button で custom event を投げる場合は action / controller 連携の調査が必要
- app routing を細かく制御する場合は SystemUI 側の fallback rule が必要

variant 名の例:

- `app-with-rail-v1`
- `fullscreen-plus-rail-v1`
- `tablet-cockpit-v1`

## Pattern 6: Floating card HMI

map や背景を広く取り、その上に card 状の app panel を浮かせる構成です。

```text
+---------------------------------------------+
|                                             |
|                    map                      |
|        +-----------------------------+      |
|        | calendar / media card       |      |
|        +-----------------------------+      |
|                                             |
+---------------------------------------------+
```

向いている用途:

- modern cockpit 風の floating UI を作りたい
- background map の上に必要な情報だけ浮かせたい
- panel の `Corner`、`Background`、`Layer`、margin を活用したい

panel 構成:

- `map_panel`
- `floating_card_panel`
- `floating_secondary_panel`
- `app_panel`

カスタマイズしやすい点:

- card の角丸、margin、背景色を変える
- card を左右どちらに寄せるか変える
- card を event で compact / expanded に切り替える
- map ではなく calm background / wallpaper を下地にする

実装難易度:

- 見た目は XML / RRO で作りやすい
- card 内 app が狭い bounds でも成立するかは app 側 UI に依存する

variant 名の例:

- `floating-card-v1`
- `map-card-v1`
- `ambient-card-v1`

## Pattern 7: App grid hub

ホーム画面を固定 app ではなく、All apps / launcher hub 中心にする構成です。

```text
+---------------------------------------------+
|                 home / hub                  |
|                                             |
|        app icons / shortcuts / cards        |
|                                             |
+---------------------------------------------+
|                 app_panel overlay           |
+---------------------------------------------+
```

向いている用途:

- demo で多くの app を素早く起動したい
- fixed HMI より launcher 的な操作を重視したい
- app 起動後は fullscreen で見せたい

panel 構成:

- `panel_app_grid`
- `app_panel`
- `decor_home_background_panel`
- 必要に応じて `media_mini_panel`

カスタマイズしやすい点:

- All apps を常時表示に近い扱いにする
- app 起動後に hub を閉じるか残すか決める
- fixed panel を減らし、routing を `app_panel` に寄せる
- shortcut rail を追加する

実装難易度:

- `panel_app_grid` の bounds / layer は XML で変更可能
- app 起動時の close / fullscreen 優先は Launcher / SystemUI 側の変更が必要

variant 名の例:

- `app-grid-hub-v1`
- `launcher-first-v1`
- `demo-hub-v1`

## Pattern 8: Calm mode / minimal HMI

運転中や集中したい場面で、情報量を減らす構成です。

```text
+---------------------------------------------+
|                                             |
|                  map / calm                 |
|                                             |
|          small media / status only          |
|                                             |
+---------------------------------------------+
```

向いている用途:

- 視覚負荷を下げたい
- demo 中に「通常モード」と「集中モード」を比較したい
- 一時的に calendar / app grid / widgets を隠したい

panel 構成:

- `map_panel` または `calm_background_panel`
- `media_mini_panel`
- `status_panel`
- hidden variant を持つ fixed panels

カスタマイズしやすい点:

- panel の `Visibility` と `Alpha` を落とす
- layer を下げる
- `Focus` を外す
- `app_panel` や `panel_app_grid` を close event で閉じる

実装難易度:

- mode 切り替え event が既にあるなら XML 中心
- 新しい vehicle state や button から mode 切り替えしたい場合は event source の追加が必要

variant 名の例:

- `calm-mode-v1`
- `minimal-drive-v1`
- `focus-mode-v1`

## Pattern 9: Parking / charging / stopped mode HMI

走行中ではなく、駐車中や充電中に情報量を増やす構成です。

```text
+----------------------+----------------------+
| charging / energy    | media / video safe   |
+----------------------+----------------------+
| settings / schedule  | app shortcuts        |
+----------------------+----------------------+
```

向いている用途:

- charging UI を試したい
- 駐車中だけ productivity / entertainment を広げたい
- drive mode と parked mode の切り替えを検証したい

panel 構成:

- `energy_panel`
- `media_panel`
- `settings_panel`
- `shortcut_panel`
- `app_panel`

カスタマイズしやすい点:

- parked variant では 2x2 grid にする
- driving variant では map + media mini だけにする
- charging 中だけ `energy_panel` を前面に出す
- settings は fullscreen overlay に逃がす

実装難易度:

- parked / charging event の取り込みは追加実装が必要になりやすい
- layout variant 自体は XML で表現しやすい

variant 名の例:

- `parking-mode-v1`
- `charging-dashboard-v1`
- `drive-park-switch-v1`

## Pattern 10: Diagnostics / developer cockpit

開発者や検証者向けに、状態確認と app 操作を並べる構成です。

```text
+----------------------+----------------------+
| log / status         | app under test       |
+----------------------+----------------------+
| controls             | map / media          |
+----------------------+----------------------+
```

向いている用途:

- PoC の demo / debug をしやすくしたい
- app under test を見ながら status panel を残したい
- HMI variant の比較検証を行いたい

panel 構成:

- `app_panel`
- `debug_status_panel`
- `control_panel`
- `map_panel`
- `media_panel`

カスタマイズしやすい点:

- debug status を decor layout にする
- app under test を `app_panel` に固定する
- controls から All apps や calm mode を開く
- status panel の layer を常に最前面にする

実装難易度:

- static status は XML / layout resource で作れる
- live diagnostic data を出す場合は app / service 側実装が必要

variant 名の例:

- `developer-cockpit-v1`
- `diagnostics-panel-v1`
- `testbench-hmi-v1`

## Pattern 11: Multi-display / passenger display HMI

displayId を分け、driver display と passenger display で別 panel set を持つ構成です。

```text
Driver display:
+----------------------+----------------------+
| map                  | media mini           |
+----------------------+----------------------+

Passenger display:
+---------------------------------------------+
| app / entertainment / browsing              |
+---------------------------------------------+
```

向いている用途:

- 複数 display 前提の HMI を検討したい
- driver 側は minimal、passenger 側は app 操作中心にしたい
- display ごとに異なる app routing を試したい

panel 構成:

- driver display の `map_panel` / `media_mini_panel`
- passenger display の `passenger_app_panel`
- displayId ごとの `panel_app_grid`

カスタマイズしやすい点:

- `displayId` ごとに panel 定義を分ける
- driver 側は safety first にする
- passenger 側は fullscreen app 中心にする

実装難易度:

- 複数 display の product / emulator / hardware 前提が必要
- app launch target display の制御は追加調査が必要
- single display PoC より検証範囲が広い

variant 名の例:

- `dual-display-v1`
- `passenger-app-panel-v1`
- `driver-passenger-v1`

## Pattern 12: Mode-switching showcase

1 つの product で複数の HMI mode を切り替える demo 構成です。

```text
normal mode:
+----------------------+----------------------+
| map                  | calendar             |
+----------------------+----------------------+
| map                  | radio                |
+----------------------+----------------------+

calm mode:
+---------------------------------------------+
| map + minimal status                         |
+---------------------------------------------+

app mode:
+---------------------------------------------+
| app_panel fullscreen                         |
+---------------------------------------------+
```

向いている用途:

- ScalableUI の variant 切り替えを見せたい
- 同じ app set で HMI の表情を変えたい
- tag を切る前に複数案を 1 product 内で比較したい

panel 構成:

- 各 fixed panel に `normal` / `calm` / `app_focus` variant を持たせる
- `app_panel`
- `panel_app_grid`
- mode button 用 decor panel

カスタマイズしやすい点:

- event 名を mode ごとに分ける
- open / close / focus の組み合わせで画面を切り替える
- grip ではなく button event で切り替える

実装難易度:

- XML の variant と transition が増えるため設計管理が重要
- mode button や custom event dispatch は追加実装が必要になりやすい

variant 名の例:

- `showcase-modes-v1`
- `normal-calm-app-v1`
- `hmi-comparison-v1`

## 実装難易度の目安

| レベル | 内容 | 例 |
| --- | --- | --- |
| A | XML / RRO だけで変更しやすい | bounds、corner、background、layer、panel 追加、app component 差し替え |
| B | product 定義の変更が必要 | Calendar など未同梱 app を `PRODUCT_PACKAGES` に追加 |
| C | SystemUI / Launcher の小変更が必要 | All apps 起動時の fullscreen 優先、launch root fallback、grip 挙動変更 |
| D | app 側実装が必要 | panel 内に収まる専用 UI、live diagnostics、custom service data |
| E | vehicle / hardware / policy 連携が必要 | driving / parked / charging / multi-display / UX restriction 連動 |

おすすめは、まず A と B の範囲で HMI の形を作り、必要になったところだけ C 以降に進むことです。

## 最初に作ると良さそうな variant 候補

この repo で次に増やすなら、次の順番が扱いやすいです。

| 優先 | variant | 目的 | 主な変更 |
| --- | --- | --- | --- |
| 1 | `map-first-v1` | map を広くした navigation first 案 | 左右 split を `70/30`、右 rail を 2 または 3 分割 |
| 2 | `media-dock-v1` | media / radio を大きく見せる案 | bottom media dock、map mini |
| 3 | `floating-card-v1` | floating card 風の見た目を試す案 | map 背景 + corner 付き card panel |
| 4 | `app-with-rail-v1` | fullscreen app と side rail の共存案 | `app_panel` を広く、right rail を固定 |
| 5 | `calm-mode-v1` | 情報量を減らした運転中表示案 | fixed panel を hidden / alpha down、map + status 中心 |
| 6 | `showcase-modes-v1` | 複数 mode を 1 product で比較する案 | normal / calm / app focus variant を追加 |

## アイデアを variant に落とす手順

1. 既存 variant を 1 つ選ぶ
2. `variants/<name>/` にコピーする
3. product 名を決める
4. 固定 panel と overlay panel の役割を決める
5. `config_default_activities` に固定 app を割り当てる
6. panel XML の `Bounds` / `Layer` / `Visibility` / `Corner` を決める
7. All apps と `app_panel` の挙動を確認する
8. build して実機または emulator で操作する
9. `export_patches.sh` で patch を書き出す
10. README / docs / wiki を更新する
11. 動作確認できた時点で tag を切る

## 設計時の注意点

fixed panel に app を割り当てるほど、HMI は安定して見えます。

一方で、fixed panel app を All apps から起動したときに fullscreen として別表示したい場合は、app の launch mode や task 再利用に注意が必要です。

狭い panel に app を押し込む場合、app 側 UI が responsive でないと操作しづらくなります。

ScalableUI の XML は強力ですが、variant が増えすぎると読みにくくなります。最初は fixed layout を 1 つ作り、そこから 1 つずつ mode や overlay を追加するのが安全です。

他人に配る variant は、必ず patch、README、docs、tag をセットにしてください。

## まとめ

ScalableUI で作りやすい HMI は、大きく分けると次の 5 系統です。

- 常時表示 app を並べる dashboard 型
- map や media を主役にする cockpit 型
- fullscreen app と side rail を組み合わせる workspace 型
- overlay や floating card で必要な情報を重ねる card 型
- normal / calm / parked などを切り替える mode 型

どの方向でも、最初は「常時表示する panel」と「一時的に出す overlay」を分けて考えると、XML と patch の管理がしやすくなります。
