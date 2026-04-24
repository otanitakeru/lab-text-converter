from pathlib import Path

from kana2phone.kana2phone import kana2phone
from utils.text_handler import BufferedTextReader, BufferedTextWriter
from utils.text_line_parser import parse_text_line
from utils.token.phone_handler import validate_phones_sequence


def convert_kana_with_features_to_phone(
    input_kana_with_features_text_file_path: Path,
    output_phone_with_features_text_file_path: Path,
    output_error_file_path: Path,
) -> None:
    """カナファイル（特徴付き）をストリーミング処理し、音素ファイル（特徴付き）を出力する。"""

    with (
        BufferedTextReader(input_kana_with_features_text_file_path) as reader,
        BufferedTextWriter(
            output_phone_with_features_text_file_path
        ) as phone_with_features_w,
        BufferedTextWriter(output_error_file_path) as error_w,
    ):
        for line in reader.iter_lines():
            try:
                utt_id, kana_with_features = parse_text_line(line)
            except ValueError:
                error_w.write_raw(f"parse_text_line ValueError: {line}\n")
                continue

            morphs = kana_with_features.split(" ")

            phones_with_features = []
            all_phones = []
            try:
                for morph in morphs:
                    # morph : 表層形+品詞+読み
                    surface, pos, kana = morph.split("+")

                    phones = kana2phone(kana)
                    phones_with_features.append(
                        f"{surface}+{pos}+{kana}+{'-'.join(phones)}"
                    )

                    all_phones.extend(phones)

                validate_phones_sequence(all_phones)

            except ValueError as e:
                error_text = f"kana2phone ValueError: {utt_id} {e}\n"
                print(error_text)
                error_w.write_raw(error_text)
                continue

            phone_with_features_w.write_raw(
                f"{utt_id} {" ".join(phones_with_features)}\n"
            )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_kana_with_features_text_file_path", type=str, required=True
    )
    parser.add_argument(
        "--output_phone_with_features_text_file_path", type=str, required=True
    )
    parser.add_argument("--output_error_file_path", type=str, required=True)
    args = parser.parse_args()

    input_kana_with_features_text_file_path = Path(
        args.input_kana_with_features_text_file_path
    )
    output_phone_with_features_text_file_path = Path(
        args.output_phone_with_features_text_file_path
    )
    output_error_file_path = Path(args.output_error_file_path)

    convert_kana_with_features_to_phone(
        input_kana_with_features_text_file_path,
        output_phone_with_features_text_file_path,
        output_error_file_path,
    )
