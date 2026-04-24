#!/usr/bin/env bash

set -euxo pipefail

cd $(dirname $0)

cd ../src

#
# 引数
#
INPUT_CHAR_TEXT_FILE_PATH=${1:-../datasets/.example.txt}
OUTPUT_ROOT_DIR_PATH=${2:-../outputs/char2kana/.example}
#

[ ! -f "$INPUT_CHAR_TEXT_FILE_PATH" ] && echo "Error: $INPUT_CHAR_TEXT_FILE_PATH not found" && exit 1

date_str=$(date +%Y-%m-%dT%H-%M-%S)
OUTPUT_DIR_PATH="$OUTPUT_ROOT_DIR_PATH/$date_str"

mkdir -p $OUTPUT_DIR_PATH

#
# ログファイルの設定
#
LOG_FILE="$OUTPUT_DIR_PATH/log.txt"
exec > >(tee "$LOG_FILE") 2>&1
#

mkdir -p "$OUTPUT_DIR_PATH/data" "$OUTPUT_DIR_PATH/processed" "$OUTPUT_DIR_PATH/processed/.errors" "$OUTPUT_DIR_PATH/results" "$OUTPUT_DIR_PATH/results/features" "$OUTPUT_DIR_PATH/results/.errors"

cp "$INPUT_CHAR_TEXT_FILE_PATH" "$OUTPUT_DIR_PATH/data/char.txt"


# 〜(範囲表現), ●◯⬛︎(伏字) は扱いが難しいため、この表現が含まれる行を除去する
PRECHECK_PROBLEM_CHARS='[〜●◯⬛︎]'
PRECHECK_ERROR_FILE="$OUTPUT_DIR_PATH/processed/.errors/precheck_suspicious_chars.txt"

if grep -Pn "${PRECHECK_PROBLEM_CHARS}" "$OUTPUT_DIR_PATH/data/char.txt" > "$PRECHECK_ERROR_FILE" 2>/dev/null; then
    echo ""
    echo "⚠ 警告: 〜(範囲表現), ●◯⬛︎(伏字) が含まれている行を除去します"
    echo ""
fi

grep -Pv "${PRECHECK_PROBLEM_CHARS}" "$OUTPUT_DIR_PATH/data/char.txt" \
        > "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.txt"

# テキストを正規化
python normalizer.py \
    --input_file_path "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.txt" \
    --output_file_path "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.normalized.txt" \
    --convert_kanji_from_numbers true \
    --delimiter "|"

# 繰り返し音声があるか確認
python filter_by_repeat.py \
    --input_text_file_path "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.normalized.txt" \
    --output_text_file_path "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.normalized.no_repeat.txt" \
    --output_error_file_path "$OUTPUT_DIR_PATH/processed/.errors/repeat_error.txt" \
    --repeat 5

python converter_char2kana_feat.py \
    --input_char_text_file_path "$OUTPUT_DIR_PATH/processed/char.precheck_filtered.normalized.no_repeat.txt" \
    --output_kana_with_features_file_path "$OUTPUT_DIR_PATH/results/features/kana_with_features.txt" \
    --output_error_file_path "$OUTPUT_DIR_PATH/results/.errors/char2kana_error.txt" \
    --ignore_filler true \
    --ignore_pyopenjtalk_warnings true \
    --simple_morph_analysis true

# char のみを発話ごとに結合して出力 (フォーマット: "表層形+品詞+読み" → 表層形のみ連結)
awk '{
    id = $1; char = ""
    for (i = 2; i <= NF; i++) {
        n = split($i, parts, "+")
        char = char parts[1]
    }
    print id " " char
}' "$OUTPUT_DIR_PATH/results/features/kana_with_features.txt" > "$OUTPUT_DIR_PATH/results/char.txt"

# kana のみを発話ごとに結合して出力 (フォーマット: "表層形+品詞+読み" → 読みのみ連結)
awk '{
    id = $1; kana = ""
    for (i = 2; i <= NF; i++) {
        n = split($i, parts, "+")
        kana = kana parts[3]
    }
    print id " " kana
}' "$OUTPUT_DIR_PATH/results/features/kana_with_features.txt" > "$OUTPUT_DIR_PATH/results/kana.txt"


line_count_input=$(wc -l < "$INPUT_CHAR_TEXT_FILE_PATH")
line_count_output=$(wc -l < "$OUTPUT_DIR_PATH/results/char.txt")

echo ""
echo "[入力] 漢字かな交じり文の行数: $line_count_input"
echo "[出力] 漢字かな交じり文の行数: $line_count_output"
echo "変換率: $(echo "scale=2; $line_count_output / $line_count_input * 100" | bc)%"
echo ""
