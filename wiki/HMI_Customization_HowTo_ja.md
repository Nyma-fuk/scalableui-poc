# HMI Customization HowTo

## 1. 何を変えたいかを先に決める

HMI カスタマイズは、最初に「どの種類の変更か」を決めると迷いにくいです。

主な変更種類:
- panel の数を変える
- panel の位置や大きさを変える
- 固定 panel に出す app を変える
- `All apps` や fullscreen overlay の挙動を変える
- grip を追加する / 外す
- product を増やして別 variant として持つ

## 2. どの variant をベースにするか決める

この repo には 2 つのベースがあります。

- grip あり
  - root 配下
  - split を drag で動かせる
- grip なし
  - `variants/no-grip/`
  - 固定 3 分割

迷ったら:
- まず layout の正解を探したいなら `no-grip`
- 後で split を調整したいなら `grip`

## 3. HMI を変えるときの基本ディレクトリ

主に見る場所:
- `patches/device-generic-car/`
  - product を追加する patch
- `patches/packages-services-Car/`
  - RRO と panel XML の本体
- `patches/packages-apps-Car-SystemUI/`
  - ScalableUI 側の routing や grip の共通ロジック
- `patches/packages-apps-Car-Launcher/`
  - `All apps` 起動時の launch ヒント
- `docs/`
  - variant の仕様メモ
- `variants/`
  - 派生版

RRO 側で一番重要なのは `packages/services/Car` 向け patch です。
panel の見た目や配置は、ほぼここで決まります。

## 4. まず最小変更で 1 つだけ触る

おすすめの順番:
1. app を入れ替える
2. panel の bounds を変える
3. fullscreen routing を変える
4. panel 数を増減する
5. grip / animation / keyframe を触る

最初から全部変えると原因が分からなくなりやすいです。

## 5. panel に app を割り当てる

固定 panel の app 割り当ては、主に `config_default_activities` と panel の `role` で決まります。

見る file:
- `res/values/config.xml`
- `res/values/strings.xml`

考え方:
- panel XML には `id` がある
- `config_default_activities` に `panelId;component` を書く
- component は `package/.ActivityName` 形式か完全修飾の component を使う

例:
```xml
<string-array name="config_default_activities" translatable="false">
    <item>calendar_panel;com.android.calendar/.AllInOneActivity</item>
</string-array>
```

## 6. panel の位置と大きさを変える

panel 配置は、各 panel XML の `Variant` と `Bounds` で決まります。

まず見る file:
- `map_panel.xml`
- `calendar_panel.xml`
- `radio_panel.xml`
- `decor_left_background_panel.xml`

重要な属性:
- `left`
- `top`
- `right`
- `bottom`
- `width`
- `height`
- `leftOffset`
- `topOffset`
- `rightOffset`
- `bottomOffset`

考え方:
- `%` は画面全体に対する割合
- `dp` の offset は隙間や margin に使う
- 右側 2 段構成は、`calendar_panel` と `radio_panel` の `top` / `bottom` で分ける

例:
```xml
<Bounds left="50%" leftOffset="12dp" top="0" right="100%" bottom="50%" bottomOffset="12dp"/>
```

## 7. panel を増やす

4 つ以上の panel にしたい場合の基本手順:
1. 新しい panel XML を追加
2. `window_states` に追加
3. layer を必要なら追加
4. `config_default_activities` に割り当てを追加
5. fullscreen overlay と重なったときの閉じ方を必要に応じて調整

増やしやすい例:
- 右下をさらに 2 分割
- 左下に navigation 以外の固定 panel を追加
- 常駐 media panel を追加

## 8. fullscreen overlay を変える

fullscreen 関連は 2 種類あります。

- `panel_app_grid`
  - `All apps` overlay
- `app_panel`
  - 固定 panel 以外の一般 app 起動先

見る file:
- `panel_app_grid.xml`
- `app_panel.xml`
- `PanelAutoTaskStackTransitionHandlerDelegate.java`
- `AppLaunchProvider.kt`
- `AppItemViewHolder.java`

考え方:
- `All apps` は overlay なので、起動後に閉じないと「前面に残って見える」ことがある
- `app_panel` は launch root panel
- `All apps` 起動時の extra により `app_panel` 優先ルートを作っている

## 9. grip を追加または削除する

grip を使うなら:
- `window_states` に grip panel を入れる
- grip panel XML を追加する
- controller XML を追加する
- target panel 側に event transition を追加する

grip を外すなら:
- `window_states` から grip panel を外す
- grip panel XML を使わない
- target panel を固定 variant のみにする

一番分かりやすい比較:
- grip あり: root variant
- grip なし: `variants/no-grip`

## 10. 自分専用 variant を増やす

variant の増やし方:
1. 既存 variant を 1 つ選ぶ
2. `variants/<new-name>/` を作る
3. `README` と `docs` を置く
4. `patches/device-generic-car/` に product patch を置く
5. `patches/packages-services-Car/` に RRO patch を置く
6. 必要なら apply/export script を置く

variant 名の例:
- `no-grip`
- `media-right`
- `four-panel`
- `calendar-fullscreen`

## 11. product を分ける

他人が再現しやすくするには、product 名を分けるのが安全です。

理由:
- 既存 product を上書きしない
- variant ごとに `lunch` で切り替えられる
- build artifact の比較がしやすい

最低限必要:
- `device/generic/car/AndroidProducts.mk` に追加
- `sdk_car_<variant>_x86_64.mk` を新設
- `packages/services/Car/car_product/<variant>/...` を作る

## 12. patch を安全に配る

この repo の script 方針:
- すでに当たっていれば skip
- 対象 file にローカル変更があれば abort
- `git apply --check` に失敗したら abort

これにより、他の人の checkout を壊しにくくしています。

## 13. tag の切り方

variant と tag は役割を分けます。

おすすめ:
- variant
  - どんな構成か
- tag
  - その構成のどの時点か

例:
- `grip-v1`
- `grip-v2`
- `no-grip-v1`
- `four-panel-v1`

## 14. 困ったときの見方

「どこを見ればいいか」が分からないときは次の順で追います。

1. `README`
2. variant の `docs/*spec*.md`
3. `config.xml`
4. 対象 panel XML
5. `app_panel.xml` / `panel_app_grid.xml`
6. `SystemUI` / `Launcher` patch

最初の 1 回は、既存 variant の `map_panel.xml` と `calendar_panel.xml` を見比べるのが一番理解しやすいです。
