# text_converter

日本語テキストを **かな** および **音素** に変換するパイプラインツールである。
音声認識・音声合成向けのデータ前処理を想定している。

## 機能

| パイプライン | 概要                                                  |
| ------------ | ----------------------------------------------------- |
| `char2phone` | 漢字かな交じり文 → かな → 音素変換 + 辞書ファイル生成 |

各パイプラインは以下のステップを実行する。

1. **正規化** (`normalizer.py`) — 数字の漢字変換・全半角統一など
2. **繰り返しフィルタ** (`filter_by_repeat.py`) — 連続繰り返しを含む発話を除外
3. **かな変換** (`converter_char2kana_feat.py`) — pyopenjtalk による形態素解析とかな読み取得
4. **音素変換** (`converter_kana_feat2phone_feat.py`) — かなから音素列に変換
5. **辞書生成** (`lexicon_converter.py`) — char / kana / phone 形式の辞書ファイルを出力

## 入力フォーマット

各行を `<発話ID> <テキスト>` の形式とする。

```
utt001 今日はいい天気ですね
utt002 明日の会議は3時から始まります
```

## セットアップ

### 依存ライブラリ

```bash
pip install -r requirements.txt
```

## 使い方

### char → phone

```bash
bash scripts/char2phone.sh <入力テキストファイル> <出力ルートディレクトリ>
```

**出力ファイル構成:**

```
<出力ルートディレクトリ>/<タイムスタンプ>/
├── data/char.txt                        # 入力コピー
├── processed/
│   ├── char.normalized.txt              # 正規化済みテキスト
│   └── char.normalized.no_repeat.txt   # 繰り返しフィルタ後
├── results/
│   ├── char.txt                         # 表層形のみ
│   ├── kana.txt                         # かな読みのみ
│   ├── phone.txt                        # 音素列
│   ├── features/kana_with_features.txt  # 表層形+品詞+読み
│   ├── features/phone_with_features.txt # 表層形+品詞+読み+音素
│   └── lexicon/
│       ├── lexicon.char.txt
│       ├── lexicon.kana.txt
│       └── lexicon.phone.txt
└── log.txt
```

### 実行例

```bash
bash scripts/char2phone.sh datasets/.example.txt outputs/char2phone/.example
```

## 主要オプション

各 Python スクリプトは `--help` で引数を確認できる。

| スクリプト                    | 主なオプション                                                                |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `normalizer.py`               | `--convert_kanji_from_numbers`, `--lower_case_only`, `--delimiter`            |
| `filter_by_repeat.py`         | `--repeat`（連続繰り返し閾値、デフォルト: 5）                                 |
| `converter_char2kana_feat.py` | `--ignore_filler`, `--simple_morph_analysis`, `--ignore_pyopenjtalk_warnings` |

## 依存パッケージ

| パッケージ         | 用途                           |
| ------------------ | ------------------------------ |
| `pyopenjtalk-plus` | 形態素解析・かな変換           |
| `neologdn`         | テキスト正規化                 |
| `num2words`        | 数字→語句変換                  |
| `jaconv`           | 全半角・ひらがな・カタカナ変換 |
| `pyyaml`           | 設定ファイル読み込み           |

## 既知の課題

### アルファベット表記への非対応

`pyopenjtalk-plus` はアルファベット文字列（例:`Python`）を受け取った場合、読みとして英語発音ではなくアルファベット名称読み（例: `ピーワイティーエイチオーエヌ`）を返すことがある一方、未知語として処理されると読みが空になったり誤変換が生じたりする。現状、アルファベット表記を日本語読みへ展開する前処理は実装されていない。

### 繰り返し記号（々）を含む表現

「大々的」「堂々と」のような繰り返し記号 `々` を含む語は `pyopenjtalk-plus` が正しく形態素分割・読み付与できる場合が多いが、「大々々的」のように同記号が連続する表現では誤った読みが付与されるか、または変換に失敗することがある。このような入力は事前のフィルタリングが推奨される。

### pyopenjtalk-plus 由来の変換バグ

フィラーとカタカナが混在する文字列において誤変換が生じる場合がある。

```python
import pyopenjtalk
text = "おーホルマントピーク"
njd_feature, _ = pyopenjtalk.run_frontend_detailed(text)
for n in njd_feature:
    print(n["string"], n["pron"], n["pos"])
```

出力結果

```
お    オ              接頭詞
ーホルマントピーク    ーホルマントピーク    フィラー
```
