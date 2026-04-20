# ScalableUI PoC Workdir

このディレクトリは、ScalableUI PoC をスモールスタートで進めるための作業用領域です。

## 目的

- Android ソースへの変更を patch として外出しできるようにする
- 別の checkout に対して同じ変更を再適用しやすくする
- 既存 product を直接崩さず、PoC 専用 product で開発する
- `dewd` の広い overlay 群に依存せず、最小構成から ScalableUI を育てる

## 現在の PoC 構成

- `sdk_car_scalableui_x86_64` という PoC 専用 product を追加
- `sdk_car_x86_64` をベースにして、PoC 専用 RRO だけを追加
- `Calendar` を PoC product に追加
- 左背景 panel の上にフロートした `map`、右上 `calendar`、右下 `radio` の固定 HMI を定義
- 固定 panel 以外の起動先として fullscreen `app_panel` を追加
- `All apps` は fullscreen overlay として定義
- GripBar はサイズだけ拡大し、タップでは layout を切り替えず drag 専用として扱う
- `All apps` からの起動は `app_panel` を優先するヒントを付け、overlay を閉じる

## 主要ファイル

- `scripts/export_patches.sh`
  - 今回の PoC が所有する Android ソース変更を repo ごとの patch として書き出す
- `scripts/apply_patches.sh`
  - 書き出した patch を別 checkout に安全に適用する
- `patches/device-generic-car/`
  - `device/generic/car` repo 向け patch を置く
- `patches/packages-services-Car/`
  - `packages/services/Car` repo 向け patch を置く
- `patches/packages-apps-Car-SystemUI/`
  - `packages/apps/Car/SystemUI` repo 向け patch を置く
- `patches/packages-apps-Car-Launcher/`
  - `packages/apps/Car/Launcher` repo 向け patch を置く
- `docs/scalableui_hmi_poc_spec_ja.md`
  - 現在の HMI 構成、package 調査結果、Grip 仕様、fullscreen overlay、既知制約の整理
- `variants/no-grip/`
  - grip を使わない固定 3 分割 variant
- `wiki/`
  - HMI を自分好みに組み替えるための wiki-ready markdown 群

## 再現手順

前提:
- 対象 checkout は AAOS15 系で、`device/generic/car`、`packages/services/Car`、`packages/apps/Car/SystemUI`、`packages/apps/Car/Launcher` が存在する
- `workdir/scalableui-poc` を checkout に置いた状態で実行する

手順:
1. `bash workdir/scalableui-poc/scripts/apply_patches.sh`
2. `lunch sdk_car_scalableui_x86_64-trunk_staging-userdebug`
3. 通常どおり build する

`apply_patches.sh` の方針:
- patch が既に適用済みなら skip する
- patch 対象ファイルにローカル変更があれば止まる
- `git apply --check` に失敗した場合は何も変更せず止まる

この script は「他人の checkout を壊さない」ことを優先しているため、想定ベースからズレている環境では無理に当てず abort する。

## Variant

- root
  - 現在の `grip` あり variant
- `variants/no-grip`
  - 左 map / 右上 calendar / 右下 radio を固定 split で持つ variant

複数ユースケースを試す場合は、variant は directory で分け、release や検証区切りを tag で管理するのが扱いやすいです。

## Customization Wiki

HMI の構成を自分で編集したい人向けに、repo 内に wiki-ready な markdown を用意しています。

- `wiki/Home.md`
  - wiki の入口
- `wiki/HMI_Pattern_Ideas_ja.md`
  - ScalableUI で実現しやすい HMI 構成パターンのアイデア集
- `wiki/HMI_Customization_HowTo_ja.md`
  - どの順で何を触ればよいかの実践手順
- `wiki/XML_and_Panel_Reference_ja.md`
  - XML / panel 構成のリファレンス
- `wiki/Customization_Recipes_ja.md`
  - 典型的なカスタマイズ例

GitHub Wiki を有効にしたい場合は、これらの markdown をそのまま移植するか、repo の `wiki/` を docs として公開する運用がしやすいです。

## 次の前提

- `Calendar` は PoC product 側で追加している
- `Radio` は car product 側に元から入っている `CarRadioApp` を使う
- fullscreen overlay の routing は `app_panel` を launch root panel にすることで実現している
- 左 map は `decor_left_background_panel` の上に `map_panel` を重ねることでフロート風に見せている
- Grip は `48dp` に拡大しているが、見た目の overlay 差し替えは現在は使っていない
- `All apps` から起動した app は `com.android.car.carlauncher.extra.LAUNCH_IN_APP_PANEL=true` を付けて launch し、ScalableUI 側で `app_panel` 優先に routing する
- `All apps` 起動後は `AppGridActivity` 側を閉じ、overlay が残って「何も起きない」見え方を避けている
- ただし fixed panel app を常に別 fullscreen task として出せることまでは保証していない
- GitHub に push する前に、patch と docs を同じ repository に置いておくと再利用しやすい
