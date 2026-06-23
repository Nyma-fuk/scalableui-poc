# Common Patches

この directory は、過去の HMI variant suite / demo app 実験で使った共通 patch を保持する場所である。

## 現在の扱い

| Path | Status | 備考 |
| --- | --- | --- |
| `patches/device-generic-car/` | Historical / generated suite | 複数 HMI product をまとめて追加する過去の suite 用 patch |
| `patches/packages-services-Car/` | Historical / generated suite | demo app / dynamic workspace / token reparent routing 実験を含む |

## Active baseline との関係

現行 `declarative-multipanel` baseline は、この `common/patches` を前提にしない。

現行 baseline の portable patch は次を参照する。

```text
variants/declarative-multipanel/patches/
```

## 注意

- この directory の patch は削除しない。正しい実験記録や再利用可能な部品を含む。
- Android17 移植へそのまま適用しない。
- 再利用する場合は、対象 AAOS branch の source、module build、emulator runtime で再検証する。
