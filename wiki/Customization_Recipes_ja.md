# Customization Recipes

## Recipe 1: 右上の Calendar を別 app に変える

触る場所:
- `res/values/strings.xml`
- `res/values/config.xml`

やること:
1. component 名を新しい app に置き換える
2. `config_default_activities` の `calendar_panel;...` を更新する

向いている例:
- Calendar を media に置き換える
- settings panel を右上に固定する

## Recipe 2: 左右の split を固定で `60/40` にする

触る場所:
- `map_panel.xml`
- `decor_left_background_panel.xml`
- `calendar_panel.xml`
- `radio_panel.xml`

やること:
1. `left_60` 系を default にする
2. `calendar_panel` / `radio_panel` の `left="60%"` 系を default にする
3. grip variant なら drag を残すか外すか決める

固定 layout にしたいなら、`no-grip` variant のように他 variant を消して 1 つだけ残すのが分かりやすいです。

## Recipe 3: 右上と右下の split を固定で `35/65` にする

触る場所:
- `calendar_panel.xml`
- `radio_panel.xml`

やること:
1. `w50_h35` と `w50_h65` を使う
2. defaultVariant を更新する
3. 不要な height drag 系の variant を整理する

## Recipe 4: grip を完全に外す

一番簡単なのは `variants/no-grip` をベースにすることです。

自分で外す場合:
1. `window_states` から grip panel を削除
2. grip panel XML を削除または未使用にする
3. target panel 側から drag event 用 transition を整理する
4. grip 用 dimen / integer を整理する

## Recipe 5: 4 枚目の固定 panel を追加する

例:
- 右下をさらに 2 分割して `media_panel` を作る

やること:
1. `media_panel.xml` を追加
2. `window_states` に追加
3. layer を追加
4. `config_default_activities` に割り当てを追加
5. 既存 `calendar_panel` / `radio_panel` の bounds を調整

## Recipe 6: ある app を常に fullscreen に送りたい

方法:
- fixed panel に割り当てない
- `config_default_activities` から外す
- `app_panel` に流す

注意:
- app 自体の launch mode が `singleTask` などだと、期待どおりの task 分離にならないことがある

## Recipe 7: `All apps` を使わず、直接固定 panel だけにしたい

触る場所:
- `config_default_activities`
- `window_states`
- `panel_app_grid.xml`

方法:
1. `panel_app_grid` を `window_states` から外す
2. launcher 側から `All apps` の呼び出し導線を使わない
3. fixed panel と `app_panel` だけで運用する

## Recipe 8: map をフロートではなく、完全な左ペインにしたい

触る場所:
- `map_panel.xml`
- `decor_left_background_panel.xml`

やること:
1. `map_panel` の margin を減らすか無くす
2. `Corner` を外す
3. `decor_left_background_panel` との差を少なくする

## Recipe 9: fullscreen overlay の閉じ方を変える

触る場所:
- `panel_app_grid.xml`
- `app_panel.xml`
- `AppItemViewHolder.java`

変えられること:
- app 起動後に `All apps` を閉じる / 閉じない
- `Home` で閉じる
- 特定 panel が開いたら閉じる

## Recipe 10: 新しい variant を増やす

おすすめ手順:
1. 既存 variant をコピー
2. product 名を変更
3. `README` を置く
4. `docs` を置く
5. patch を variant directory に分ける
6. `apply_patches.sh` を置く
7. 動いた時点で tag を切る

## Recipe 11: tag の付け方

おすすめルール:
- variant 名を含める
- `v1`, `v2` のように時系列を付ける
- 大きなレイアウト変更のたびに切る

例:
- `grip-v1`
- `grip-v2`
- `no-grip-v1`
- `four-panel-v1`

## Recipe 12: 他の人に配る前のチェック

最低限見るポイント:
- `README` が最新か
- variant ごとの `docs` が最新か
- patch が全部揃っているか
- apply script が safe abort するか
- tag を切ったか

「自分の checkout で動く」だけでなく、「他人の clean checkout に安全に適用できるか」を最後に確認すると配布しやすいです。
