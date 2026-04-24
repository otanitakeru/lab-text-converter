# text_converter

日本語テキストを **かな** および **音素** に変換するパイプラインツールです。
音声認識・音声合成向けのデータ前処理を想定しています。

## 機能

| パイプライン | 概要                                                  |
| ------------ | ----------------------------------------------------- |
| `char2kana`  | 漢字かな交じり文 → かな変換                           |
| `char2phone` | 漢字かな交じり文 → かな → 音素変換 + 辞書ファイル生成 |

各パイプラインは以下のステップを実行します。

1. **正規化** (`normalizer.py`) — 数字の漢字変換・全半角統一など
2. **繰り返しフィルタ** (`filter_by_repeat.py`) — 連続繰り返しを含む発話を除外
3. **かな変換** (`converter_char2kana_feat.py`) — pyopenjtalk による形態素解析とかな読み取得
4. **音素変換** (`converter_kana_feat2phone_feat.py`) — かなから音素列に変換（char2phone のみ）
5. **辞書生成** (`lexicon_converter.py`) — char / kana / phone 形式の辞書ファイルを出力（char2phone のみ）

## 入力フォーマット

各行を `<発話ID> <テキスト>` の形式にしてください。

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

### char → kana

```bash
bash scripts/char2kana.sh <入力テキストファイル> <出力ルートディレクトリ>
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
│   └── features/kana_with_features.txt  # 表層形+品詞+読み
└── log.txt
```

### char → phone

```bash
bash scripts/char2phone.sh <入力テキストファイル> <出力ルートディレクトリ>
```

**出力ファイル構成（char2kana の出力に加えて）:**

```
results/
├── phone.txt                             # 音素列
├── features/phone_with_features.txt      # 表層形+品詞+読み+音素
└── lexicon/
    ├── lexicon.char.txt
    ├── lexicon.kana.txt
    └── lexicon.phone.txt
```

### 実行例

```bash
# char → kana
bash scripts/char2kana.sh datasets/.example.txt outputs/char2kana/.example

# char → phone
bash scripts/char2phone.sh datasets/.example.txt outputs/char2phone/.example
```

## 主要オプション

各 Python スクリプトは `--help` で引数を確認できます。

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
