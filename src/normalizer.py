from pathlib import Path

from normalize.normalize_text_for_asr import normalize_text
from utils.text_handler import BufferedTextReader, BufferedTextWriter
from utils.text_line_parser import parse_text_line

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file_path", type=str, required=True)
    parser.add_argument("--output_file_path", type=str, required=True)
    parser.add_argument("--repeat", type=int, default=None)
    parser.add_argument(
        "--convert_kanji_from_numbers", action="store_true", default=True
    )
    parser.add_argument("--lower_case_only", action="store_true", default=True)
    parser.add_argument("--delimiter", type=str, default="|")
    args = parser.parse_args()

    input_file_path = Path(args.input_file_path)
    output_file_path = Path(args.output_file_path)
    repeat = args.repeat
    convert_kanji_from_numbers = args.convert_kanji_from_numbers
    lower_case_only = args.lower_case_only
    delimiter = args.delimiter

    with BufferedTextReader(input_file_path) as reader, BufferedTextWriter(
        output_file_path
    ) as writer:
        for line in reader.iter_lines():
            try:
                utt_id, text = parse_text_line(line)
            except ValueError:
                print(
                    f"⚠️warning: 使用されているテキストファイルの形式が間違っている可能性がある: {line}"
                )
                continue

            normalized_text = normalize_text(
                text,
                repeat=repeat,
                convert_kanji_from_numbers=convert_kanji_from_numbers,
                lower_case_only=lower_case_only,
                delimiter=delimiter,
            )
            writer.write_line(f"{utt_id} {normalized_text}")
