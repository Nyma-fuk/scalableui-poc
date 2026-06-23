# Android 17 As-Is担保付き ScalableUI PoC移植計画

## 目的

Android 17 AAOSのAs-Is画面構成と画面遷移を壊さずに、既存の
`declarative-multipanel` ScalableUI PoCを段階的に移植する。

この移植では、PoCの見た目を一気に入れることを優先しない。先にAndroid 17標準AAOSが
正しく起動し、Home、All Apps、Settingsなどの基本導線が維持されていることを基準化し、
その基準から差分を小さく積み上げる。

詳細な開発フローは以下に分離して整理する。

```text
docs/android17/aaos17_scalableui_development_flow_ja.md
```

## As-Is基準

Android 17 `android-17.0.0_r1` の `sdk_car_x86_64-trunk_staging-userdebug`
をAs-Is基準とする。

確認済みの基準は以下。

| 項目 | 結果 |
| --- | --- |
| Emulator起動 | OK |
| `sys.boot_completed` | `1` |
| Home表示 | OK |
| All Apps表示 | OK |
| Settings起動 | OK |
| 直近logcat fatal | `FATAL EXCEPTION` / `AndroidRuntime` / fatal signalなし |

証跡:

```text
<EVIDENCE_DIR>/android17-r1-runtime-20260623-202045/
```

主な証跡:

```text
boot.png
all_apps_after_tap.png
settings_after_tap.png
fingerprint.txt
sys_boot_completed.txt
dumpsys_activity_top_after_settings.txt
logcat_tail.txt
```

Build fingerprint:

```text
Android/sdk_car_x86_64/emulator_car64_x86_64:Baklava/CP2A.260605.016/eng.y-fuk:userdebug/test-keys
```

## 移植方針

As-Isを壊さないため、Android 17標準AAOS emulatorで通った
`sdk_car_x86_64-trunk_staging-userdebug` を基準にする。

当初はPoC専用productを追加する方針も検討した。

```text
sdk_car_scalableui_declarative_multipanel_x86_64-trunk_staging-userdebug
```

しかし、今回のAndroid 17移植ではこの方針を採用しない。
理由は、専用productを追加すると、既にbuild実績のある標準AAOS17 emulator productから外れ、
Soongのproduct/module graph生成が重くなり、RAM制約下で切り分けが難しくなるためである。

したがって、実作業では以下を正とする。

```text
sdk_car_x86_64-trunk_staging-userdebug
  + ScalableUI PoC RRO
  + ScalableUiStubCarLauncher
  + 必要最小限のCarSystemUI差分
```

この構成は「素のAAOS17 emulatorへの追加差分」として扱う。

| 系統 | 目的 |
| --- | --- |
| As-Is検証 | PoC差分なしの `sdk_car_x86_64` でAndroid 17標準挙動を担保する |
| PoC検証 | 同じ `sdk_car_x86_64` にPoC package/RROを追加して検証する |

## 推奨開発フロー

### 全体像

```text
AOSP android-17.0.0_r1
  |
  | 1. 標準AAOS emulatorをbuildしてAs-Is基準を固定
  v
sdk_car_x86_64-trunk_staging-userdebug
  |
  | 2. PoC差分を小さく追加
  |    - RRO/XML
  |    - ScalableUiStubCarLauncher
  |    - 必要最小限のCarSystemUI差分
  v
AAOS17 + ScalableUI PoC
  |
  | 3. 変更単位ごとにmodule build
  v
RRO / Launcher / CarSystemUI
  |
  | 4. 最終確認としてemulator image化
  v
emu_img_zip
  |
  | 5. Windows host emulatorでruntime確認
  v
screenshot / overlay / package / dumpsys / smoke test
```

### 基本原則

- 標準AAOS17 emulator targetから外れない。
- 新しいproductを増やすのは最後の手段とする。
- 変更はRRO、Launcher、CarSystemUIの順で小さく積む。
- `emu_img_zip` は最終確認であり、通常の編集サイクルでは毎回実行しない。
- RAM制約下ではSoong生成とNinja実コンパイルを分けて考える。
- `SOONG_INCREMENTAL_ANALYSIS=false` はSoong graph生成そのものを不要にする設定ではない。
- WSLのRAMを無理に増やすより、標準target維持と差分縮小を優先する。

### 変更単位ごとの確認

| 変更種別 | 主な対象 | まず実行する確認 | 最終確認 |
| --- | --- | --- | --- |
| RRO/XML変更 | panel XML、transition XML、overlay config | RRO module build | `cmd overlay list`、screenshot |
| Launcher/Home host変更 | `ScalableUiStubCarLauncher`、AppGrid | launcher module build | Home/All Apps runtime確認 |
| CarSystemUI制御変更 | controller、task event、routing | CarSystemUI build | `dumpsys activity/window`、smoke |
| product/package構成変更 | `sdk_car_x86_64.mk`、package list | `m nothing` | `emu_img_zip` |

### 推奨コマンド

標準targetを選択する。

```bash
cd <AAOS17_ROOT>
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug
```

Soong graph生成だけ先に越える。

```bash
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing
```

RRO/Launcherだけ確認する。

```bash
SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO
```

runtime imageを確認する段階でのみ `emu_img_zip` を実行する。

```bash
SOONG_NINJA=ninja m -j6 emu_img_zip
```

`nproc` はWSL設定に依存するため、必ずしも最適値ではない。
今回の環境では `nproc` が一時的に4を返したため、`-j$(nproc)` は `-j4` になる。
Java/Kotlin compileが主になる段階では `-j4` から `-j6` を目安とする。

## 適用戦略

### 1. RRO/XMLを先に適用する

最初に適用するのは、ScalableUIのpanel定義、transition定義、overlay configである。

この段階でできること:

- Home上に固定panelを宣言する
- panelごとの初期Activityを指定する
- AppGrid用panelや通常app用panelを宣言する
- ScalableUI有効化に必要なframework / service / SystemUI overlayを入れる

この段階でやらないこと:

- Runtimeでpanelを増減する
- 既存taskを別panelへ移動する独自制御
- All Appsのfloating表示制御
- Home復帰時の直前layout復元

### 2. Stub launcherを追加する

標準CarLauncherを直接大改造するのではなく、PoCでは空のHome hostとして
`ScalableUiStubCarLauncher` を使う。

この段階でできること:

- HOME intentの受け皿をPoC用に差し替える
- Home画面の主導権をCarSystemUI / ScalableUI側へ寄せる
- 標準CarLauncherの複雑なUI責務からPoCを分離する

注意:

Android 17にはDEWD用の `StubCarLauncher` moduleが既に存在する。
そのためPoC側のmodule名は `ScalableUiStubCarLauncher` とし、module衝突を避ける。

### 3. CarSystemUI差分は最小化する

Android 17にはScalableUI関連実装が既に存在する。
そのため、Android 15/16 PoCのSystemUI patchをそのまま入れない。

確認対象:

```text
packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui
packages/services/Car/libs/car-wm-shell-lib
```

この段階でできること:

- TaskPanelへのActivity routing
- All Apps用panelの表示/非表示制御
- 既存task再起動時の最大化
- Home復帰時のlayout restoration
- task event / transition eventの接続

この段階で守ること:

- `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` の実装モデルを崩さない
- ActivityをPanelに直接貼る、という説明や実装に寄せない
- RootWindowContainer / TaskDisplayArea / ShellTaskOrganizerとの整合を確認する

### 4. emulator確認は証跡込みで行う

runtime確認では、画面を見ただけで完了としない。

最低限残す証跡:

```text
screenshot
getprop
cmd overlay list
pm list packages
dumpsys activity top
dumpsys window displays
logcat tail
```

確認観点:

- Homeが起動する
- All Appsが意図したlayerで表示される
- All Appsを閉じられる
- 通常appが想定panelへroutingされる
- 既存panel内appの再起動時に最大化される
- Home復帰で直前layoutへ戻る
- SystemUI / Launcher / target appに致命的クラッシュがない

## フェーズ計画

### Phase 0: As-Is固定

目的:

Android 17標準AAOSの画面構成を壊していないか比較できる状態を作る。

実施内容:

- `sdk_car_x86_64-trunk_staging-userdebug` をbuildする
- emulatorを起動する
- Home、All Apps、Settingsをスクリーンショット取得する
- `dumpsys activity`、`dumpsys window`、`logcat` を保存する

合格条件:

- `sys.boot_completed=1`
- Homeが標準AAOSとして描画される
- All Appsが表示される
- Settingsが起動する
- SystemUI / Launcher / Settingsに致命的クラッシュがない

現在状態:

完了。

### Phase 1: 標準productへのPoC package追加

目的:

As-Isでbuild実績のある `sdk_car_x86_64` のまま、PoC packageを追加する。

実施内容:

- `device/generic/car/sdk_car_x86_64.mk` に
  `packages/services/Car/car_product/scalableui_declarative_multipanel/car_scalableui_declarative_multipanel.mk`
  をinheritする
- `AndroidProducts.mk` にはPoC専用productを追加しない
- 既存の標準lunch targetを維持する

合格条件:

```bash
lunch sdk_car_x86_64-trunk_staging-userdebug
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing
```

が成功する。

現在状態:

専用product方針から標準product追加方針へ変更済み。

### Phase 2: RRO/XML定義の追加

目的:

Android 17標準ScalableUI実装に対して、PoCのpanel XML、transition XML、overlay configを
適用できるか確認する。

実施内容:

- `CarSystemUIScalableUiDeclarativeMultipanelRRO` を追加
- `CarFrameworkScalableUiDeclarativeMultipanelRRO` を追加
- `CarServiceScalableUiDeclarativeMultipanelRRO` を追加
- まずJava実装追加なしでRRO単体のbuildを確認する

合格条件:

- RRO moduleがbuildできる
- image内にRRO APKが入る
- emulator上でoverlay stateが確認できる
- As-IsのHome/All Apps/Settings導線を破壊しない

注意:

RROだけでPoCの全挙動は成立しない。ScalableUIに対するpanel定義と一部configを入れる段階であり、
All Appsのfloating制御、既存taskの最大化、Home復帰などは後続phaseで扱う。

### Phase 3: Stub launcher追加

目的:

PoC用productで標準CarLauncherの代わりに空のHome hostを入れ、
ScalableUI側にHome panel構成を任せられるか確認する。

Android 17差分:

Android 17には既に以下のDEWD用moduleが存在する。

```text
packages/services/Car/car_product/dewd/apps/StubCarLauncher
```

そのため、PoC側のmodule名 `StubCarLauncher` は衝突する。
PoC側はmodule名を以下に変更する。

```text
ScalableUiStubCarLauncher
```

ただし、APK package/classは既存PoC仕様を維持できる。

合格条件:

- `ScalableUiStubCarLauncher` がbuildできる
- `overrides` によりPoC productで標準launcherが置き換わる
- Home起動時にSystemUI/Launcherがクラッシュしない

### Phase 4: Android 17標準ScalableUIとの接続

目的:

Android 17標準実装に入っているScalableUIを正として、PoC XMLとの整合を取る。

確認対象:

```text
packages/apps/Car/SystemUI/src/com/android/systemui/car/wm/scalableui
```

Android 17ではScalableUI本体が既に存在するため、Android 16 PoCで作った
`packages/apps/Car/SystemUI` patchをそのまま入れない。

既存patchの適用状況:

| patch | Android 17適用性 |
| --- | --- |
| `device-generic-car` | product一覧の文脈差分あり。手移植が必要 |
| `packages-services-Car` | ほぼ適用可能。ただしStub launcher module名衝突あり |
| `packages-apps-Car-SystemUI` | そのまま適用不可。Android 17 ScalableUI実装との差分調査が必要 |

SystemUI runtime routingで確認する代表ファイル:

```text
PanelAutoTaskStackTransitionHandlerDelegate.java
PanelConfigReader.java
PanelTransitionCoordinator.java
ScalableUIWMInitializer.java
panel/DecorPanel.java
../wmshell/CarWMShellModule.java
```

合格条件:

- Android 17標準ScalableUIの責務を壊さない
- PoC独自のAll Apps floatingやtask routingは、Android 17実装上必要な最小差分に限定する
- `Panel -> TaskPanel -> RootTaskStack / Task -> Activity` の実装モデルを維持する

### Phase 5: PoC挙動の段階復帰

目的:

以前作成したPoC挙動を、As-Is退行を見ながら戻す。

復帰順:

1. 固定panel表示
2. All Appsをpanel/floatingとして表示
3. panel外tapまたはAll Apps再tapで閉じる
4. Settingsなど通常アプリを `app_panel` へrouting
5. 既存panel内アプリの再起動時に最大化
6. 最大化時に他panelを押しのけるtransition
7. Home復帰時に直前layoutへ戻す

各段階の合格条件:

- As-IsのHome/All Apps/Settings基本導線が説明可能な形で維持される
- SystemUI、Launcher、対象アプリに致命的クラッシュがない
- スクリーンショットとdumpsysでpanel/task状態を残す

## 現在の実施結果

実施済み:

- Android 17 As-Is emulator起動検証
- PoC移植用branch作成
- `packages-services-Car` patchの低リスク層をAndroid 17実ツリーへ適用
- Android 17側の既存 `StubCarLauncher` module衝突を確認
- PoC側module名を `ScalableUiStubCarLauncher` に変更する方針で実ツリー修正
- PoC専用product方針を撤回
- 標準 `sdk_car_x86_64` へPoC packageを追加する方針に変更

未完了:

- 標準 `sdk_car_x86_64` + PoC差分でのSoong/Ninja生成完了確認
- RRO/Stub launcher module build
- PoC差分入り `sdk_car_x86_64` の `emu_img_zip`
- PoC差分入り emulator runtime検証
- Android 17向けpatch再生成

## 現在のブロッカー

Android 17でAndroid.bpやproduct packageを追加した後、Soong/Ninja再生成がRAM制約下で重い。

確認した傾向:

- PoC専用productではSoongが20GB超RSSまで上がり、終盤でメモリ待ちになりやすい
- `sdk_car_x86_64` 既存productでもAndroid.bp追加後は再解析が入る
- `-j` はこの段階では本質的な改善にならない
- emulator image生成やJava compileに入る前のSoong解析が律速
- ただし素のAAOS17 `sdk_car_x86_64` はbuild実績があるため、標準targetを維持することが最も重要

当面の推奨:

- Soong生成フェーズは `-j1`
- `SOONG_NINJA=ninja` を使う
- `SOONG_INCREMENTAL_ANALYSIS=false` でまず安定側に倒す
- WSL memoryを無理に増やさない
- Soong生成完了後の実コンパイル/emu image生成では `-j4` から `-j6` へ増やす

## 推奨コマンド

PoC差分入り標準target:

```bash
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing
```

Soong生成完了後のmodule build:

```bash
SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO
```

image build:

```bash
SOONG_NINJA=ninja m -j6 emu_img_zip
```

## 判定

Android 17 As-Isを担保しながら、ScalableUI PoCを段階移植することは可能。

ただし、現時点では実装差分そのものよりも、Android 17のSoong再解析がビルド環境上の最大リスク。
したがって、以降は以下の順で進める。

1. 標準 `sdk_car_x86_64` targetを維持する
2. RROのみのbuild境界を作る
3. Stub launcherをbuild境界に追加する
4. SystemUI runtime routing patchはAndroid 17標準ScalableUIとの差分を読んでから最小移植する
5. 各phaseでemulator証跡を取り、As-Isとの差分を記録する
