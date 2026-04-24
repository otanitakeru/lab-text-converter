from pathlib import Path
from typing import Literal, Set, Tuple

from utils.text_handler import BufferedTextReader, BufferedTextWriter
from utils.text_line_parser import parse_text_line
from utils.token.phone_handler import validate_phones
from utils.token.syllables_handler import split_syllables


def _split_char(char: str) -> list[str]:
    return list(char)


def _split_kana(kana: str) -> list[str]:
    return split_syllables(kana)


def _split_phone(phone: str) -> list[str]:
    phones = phone.split("-")
    validate_phones(phones)
    return phones


def convert_lexicon(
    input_text_file_path: Path,
    output_lexicon_file_path: Path,
    token_type: Literal["char", "kana", "phone"],
) -> None:

    result_lexicon: Set[Tuple[str, str]] = set()
    with BufferedTextReader(input_text_file_path) as reader:
        for line in reader.iter_lines():
            _, text = parse_text_line(line)

            morphs = text.split(" ")

            for morph in morphs:
                surface, other_info = morph.split("+", 1)
                pos, other_info = other_info.split("+", 1)

                key = surface + "+" + pos

                if token_type == "char":
                    tokens = _split_char(surface)
                elif token_type == "kana":
                    kana = other_info.split("+", 1)[0]
                    tokens = _split_kana(kana)
                elif token_type == "phone":
                    phone = other_info.split("+", 1)[1]
                    tokens = _split_phone(phone)
                else:
                    raise NotImplementedError(f"未実装のトークンタイプ: {token_type}")

                result_lexicon.add((key, " ".join(tokens)))

    with BufferedTextWriter(output_lexicon_file_path) as writer:
        for key, value in sorted(result_lexicon):
            writer.write_raw(f"{key} {value}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text_file_path", type=str, required=True)
    parser.add_argument("--output_lexicon_file_path", type=str, required=True)
    parser.add_argument(
        "--token_type",
        type=str,
        required=True,
        choices=["char", "kana", "phone"],
    )
    args = parser.parse_args()
    input_text_file_path = Path(args.input_text_file_path)
    output_lexicon_file_path = Path(args.output_lexicon_file_path)
    token_type = args.token_type

    convert_lexicon(input_text_file_path, output_lexicon_file_path, token_type)
