# AAOS17 ScalableUI PoC 開発フロー

## 目的

Android 17 AAOS emulatorのAs-Is挙動を壊さずに、ScalableUI PoCを段階的に移植する。

AAOS17 source上のScalableUI実装確認は [aaos17_scalableui_source_verification_ja.md](aaos17_scalableui_source_verification_ja.md) を正とする。
この文書は、その確認結果を前提にした開発手順を扱う。

今回の開発では、PoC専用の新productを作るのではなく、build実績のある標準AAOS17 emulator
targetへPoC差分を重ねる。

```text
sdk_car_x86_64-trunk_staging-userdebug
  + ScalableUI RRO
  + ScalableUiStubCarLauncher
  + 必要最小限のCarSystemUI差分
```

この方針により、サプライヤーへ説明する際も「素のAAOS17 emulator targetへの追加差分」として扱える。

## なぜ標準targetを使うか

Android 17のSoongは、Android.bp解析の終盤で巨大なmodule graphをまとめて処理する。
AAOS、Car、SystemUI、Compose、SDK image生成が絡むため、RAM使用量が急に増える。

今回、PoC専用productを追加したところ、標準AAOS17で通っていたbuild経路から外れ、
Soongの切り分けが難しくなった。

したがって、開発の基本方針は以下とする。

- 標準 `sdk_car_x86_64-trunk_staging-userdebug` から外れない。
- `AndroidProducts.mk` にPoC専用lunch targetを追加しない。
- PoC packageは `sdk_car_x86_64.mk` から追加inheritする。
- RRO、Launcher、CarSystemUIの順に小さく適用する。
- `emu_img_zip` は最終確認で実行し、編集ごとに毎回実行しない。

## 全体フロー

```text
AOSP android-17.0.0_r1
  |
  | 1. 標準AAOS emulatorをbuild
  v
sdk_car_x86_64-trunk_staging-userdebug
  |
  | 2. As-Is runtime証跡を保存
  v
Home / All Apps / Settings baseline
  |
  | 3. PoC差分を小さく追加
  |    - RRO/XML
  |    - ScalableUiStubCarLauncher
  |    - CarSystemUI routing
  v
AAOS17 + ScalableUI PoC
  |
  | 4. module build
  v
RRO / Launcher / CarSystemUI
  |
  | 5. emu_img_zip
  v
runtime image
  |
  | 6. emulator smoke
  v
screenshot / overlay / package / dumpsys / logcat
```

## 適用単位

| 段階 | 対象 | できること | 確認 |
| --- | --- | --- | --- |
| 1 | RRO/XML | panel定義、初期Activity、transition定義、ScalableUI有効化 | RRO module build、overlay state |
| 2 | Stub launcher | HOME host差し替え、標準CarLauncherからPoC Homeを分離 | launcher module build、Home起動 |
| 3 | AppGrid / All Apps | All Appsのpanel表示、閉じる操作、app起動導線 | screenshot、activity top |
| 4 | CarSystemUI routing | TaskPanel routing、既存task最大化、Home復帰 | dumpsys activity/window |
| 5 | image | emulator runtime成立性 | `emu_img_zip`、smoke test |

## 推奨コマンド

標準targetを選択する。

```bash
cd ~/work/android17-r1
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug
```

Soong graph生成だけを先に越える。

```bash
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing
```

PoC moduleを確認する。

```bash
SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO
```

runtime imageを作る。

```bash
SOONG_NINJA=ninja m -j6 emu_img_zip
```

## RAM制約下の運用

32GB実RAMのWSL2では、WSLへ渡すメモリをさらに増やすより、対象productを増やさないことを優先する。

推奨:

- `m -j1 nothing` でSoong preflightを先に通す。
- Soongが通った後に `-j4` から `-j6` へ上げる。
- userが自分でbuildする前に、Codexが起動したbuild processが残っていないか確認する。
- `out/.lock` を保持している `soong_ui` が残っている場合は、同じoutで次のbuildを始めない。

確認コマンド:

```bash
pgrep -af 'soong_build|soong_ui|build/soong/bin/m|prebuilts/build-tools/linux-x86/bin/ninja' || true
if command -v lsof >/dev/null; then lsof out/.lock || true; fi
free -h
df -h ~/work/android17-r1 /mnt/f
```

## 手動Action

Codex側には手動actionを用意している。

```bash
/home/y-fuk/work/scalableui-poc/scripts/aaos17_scalableui_build_action.sh status
/home/y-fuk/work/scalableui-poc/scripts/aaos17_scalableui_build_action.sh stop
/home/y-fuk/work/scalableui-poc/scripts/aaos17_scalableui_build_action.sh commands
```

Codex local hook側にも同じ用途のhelperを置いている。

```bash
/home/y-fuk/.codex/hooks/aaos17_scalableui_build_action.sh status
/home/y-fuk/.codex/hooks/aaos17_scalableui_build_action.sh stop
/home/y-fuk/.codex/hooks/aaos17_scalableui_build_action.sh commands
```

使い分け:

| action | 用途 |
| --- | --- |
| `status` | build process、`out/.lock`、memory、diskを確認する |
| `stop` | Android build process groupをTERM優先で停止する |
| `commands` | 推奨build commandを表示する |

このactionは自動実行しない。userが手動buildする前に、既存プロセスを安全に確認・停止するための補助である。

## runtime検証

`emu_img_zip` が通った後は、Windows host emulatorで確認する。

最低限保存する証跡:

```text
screenshot
getprop
cmd overlay list
pm list packages
dumpsys activity top
dumpsys window displays
logcat tail
```

合格条件:

- `sys.boot_completed=1`
- Homeが起動する
- All Appsが表示される
- All Appsを閉じられる
- 通常appが想定panelへroutingされる
- 既存panel内appの再起動時に最大化される
- Home復帰で直前layoutへ戻る
- SystemUI / Launcher / target appに致命的クラッシュがない

## サプライヤー折り込み時の説明

説明の軸は以下にする。

```text
標準AAOS17 emulator target:
  sdk_car_x86_64

追加差分:
  - ScalableUI RRO/XML
  - HOME host replacement
  - AppGrid / All Apps routing
  - CarSystemUI task routing / transition最小差分

確認方法:
  - module build
  - emu_img_zip
  - emulator smoke evidence
```

「新しいOEM productを作った」のではなく、「標準AAOS17 productへHMI差分を追加した」と説明する。
