from pathlib import Path

from neologdn import normalize

from utils.text_handler import BufferedTextReader, BufferedTextWriter
from utils.text_line_parser import parse_text_line


def has_repeat(text: str, repeat: int = 5):
    """
    Args:
        kana: カナ文字列
    """

    if text != normalize(text):
        print("⚠️warning: 正規化したテキストを入力されることを想定しています。")

    text = normalize(text)

    if text != normalize(text, repeat=repeat):
        raise ValueError(f"Repeat detected: {text}")


def _run(reader, writer, error_w) -> None:
    for line in reader.iter_lines():
        try:
            utt_id, text = parse_text_line(line)
            has_repeat(text, repeat=repeat)
        except ValueError as e:
            error_text = f"[{utt_id}] {e}"
            if error_w is not None:
                error_w.write_line(error_text)
            print(error_text)
            continue

        writer.write_line(f"{utt_id} {text}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text_file_path", type=str, required=True)
    parser.add_argument("--output_text_file_path", type=str, required=True)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--output_error_file_path", type=str, required=False)

    args = parser.parse_args()
    input_text_file_path = Path(args.input_text_file_path)
    output_text_file_path = Path(args.output_text_file_path)
    repeat = args.repeat
    output_error_file_path = (
        Path(args.output_error_file_path)
        if args.output_error_file_path is not None
        else None
    )

    error_w = None
    if output_error_file_path is not None:
        error_w = BufferedTextWriter(output_error_file_path)

    with (
        BufferedTextReader(input_text_file_path) as reader,
        BufferedTextWriter(output_text_file_path) as writer,
    ):
        if output_error_file_path is not None:
            with BufferedTextWriter(output_error_file_path) as error_w:
                _run(reader, writer, error_w)
        else:
            _run(reader, writer, None)
