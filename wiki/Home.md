# ScalableUI PoC Customization Wiki

この wiki は、ScalableUI PoC をベースにして、自分の好きな HMI を作るためのガイドです。

想定している読者:
- AAOS15 の build 環境はあるが、ScalableUI の panel XML はまだ不慣れな人
- 今ある HMI を少しだけ変えたい人
- 自分専用の HMI variant を新しく作りたい人

この wiki で分かること:
- どの directory と file を触れば HMI が変わるか
- ScalableUI で作りやすい HMI 構成の候補
- panel / overlay / fullscreen routing の役割分担
- app の固定配置や `All apps` の挙動の変え方
- grip あり / なし variant の作り分け方
- patch / variant / tag をどう管理すると再利用しやすいか

おすすめの読み順:
1. [HMI Pattern Ideas](HMI_Pattern_Ideas_ja.md)
2. [HMI Customization HowTo](HMI_Customization_HowTo_ja.md)
3. [XML and Panel Reference](XML_and_Panel_Reference_ja.md)
4. [Customization Recipes](Customization_Recipes_ja.md)

既存のベース資料:
- [README](https://github.com/Nyma-fuk/scalableui-poc/blob/main/README.md)
- [Grip variant spec](https://github.com/Nyma-fuk/scalableui-poc/blob/main/docs/scalableui_hmi_poc_spec_ja.md)
- [No-grip variant spec](https://github.com/Nyma-fuk/scalableui-poc/blob/main/variants/no-grip/docs/scalableui_hmi_poc_spec_ja.md)

この repo の考え方:
- variant は directory で分ける
- snapshot は tag で分ける
- 他人の checkout を壊さないように、apply script は clean apply できないと abort する

最短で試したい人:
- grip あり: root の patch / script を使う
- grip なし: `variants/no-grip/` の patch / script を使う

variant と tag の例:
- `grip-v1`
- `no-grip-v1`

新しい HMI を作るときは、まず既存 variant を 1 つコピーして、小さく変更しながら tag を切っていくのがおすすめです。
