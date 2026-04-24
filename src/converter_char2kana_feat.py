import fcntl
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable

from char2kana.char2kana import Char2KanaError, char2kana_pyopenjtalk
from utils.text_handler import BufferedTextReader, BufferedTextWriter
from utils.text_line_parser import parse_text_line


def _call_capturing_c_stderr(
    func: Callable, *args: Any, **kwargs: Any
) -> tuple[Any, str]:
    """C ライブラリが fd 2 へ直接書き込む警告を捕捉して返す。

    Python レベルの sys.stderr では捕捉できない C ライブラリ由来の出力を、
    OS レベルで fd 2 をパイプへ付け替えることで取得する。
    """
    r_fd, w_fd = os.pipe()
    saved_fd2 = os.dup(2)
    os.dup2(w_fd, 2)
    os.close(w_fd)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.stderr.flush()
        os.dup2(saved_fd2, 2)
        os.close(saved_fd2)

    flags = fcntl.fcntl(r_fd, fcntl.F_GETFL)
    fcntl.fcntl(r_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    captured = b""
    try:
        while True:
            chunk = os.read(r_fd, 4096)
            if not chunk:
                break
            captured += chunk
    except BlockingIOError:
        pass
    os.close(r_fd)
    return result, captured.decode("utf-8", errors="replace")


def convert_char_to_kana_with_features(
    input_char_text_file_path: Path,
    output_kana_with_features_file_path: Path,
    output_error_file_path: Path,
    ignore_filler: bool = True,
    simple_morph_analysis: bool = True,
    ignore_pyopenjtalk_warnings: bool = True,
) -> None:
    """大規模テキストファイルをストリーミング処理し、normalized_text と kana を同時に出力する。

    全行をメモリに展開せず、バッチ単位でバッファリング書き込みを行うことで、
    巨大なファイルでもメモリ使用量を一定に保つ。

    Args:
        input_char_text_file_path: 入力テキストファイルのパス。
        output_kana_with_features_file_path: 出力カナファイル（特徴付き）のパス。
        output_error_file_path: 出力エラーファイルのパス。
        ignore_filler: フィラーを無視するかどうか。
        simple_morph_analysis: シンプルな形態素解析を使用するかどうか。
        ignore_pyopenjtalk_warnings: pyopenjtalk 警告が発生した発話を除外するかどうか。
    """

    with (
        BufferedTextReader(input_char_text_file_path) as reader,
        BufferedTextWriter(output_kana_with_features_file_path) as kana_w,
        BufferedTextWriter(output_error_file_path) as error_w,
    ):
        for line in reader.iter_lines():
            try:
                utt_id, char_text = parse_text_line(line)
            except ValueError:
                error_w.write_raw(f"parse_text_line ValueError: {line}\n")
                continue

            try:
                kana_with_features_list, stderr_kana_with_features = (
                    _call_capturing_c_stderr(
                        char2kana_pyopenjtalk,
                        char_text,
                        ignore_filler=ignore_filler,
                        simple_morph_analysis=simple_morph_analysis,
                        include_features=True,
                    )
                )

            except Char2KanaError as e:
                error_text = f"カナに変換できない文字が含まれている可能性があります: {utt_id} {e}\n"
                print(error_text)
                error_w.write_raw(error_text)
                continue
            except RuntimeError as e:
                error_text = (
                    f"pyopenjtalk でエラーが発生した可能性があります: {utt_id} {e}\n"
                )
                print(error_text)
                error_w.write_raw(error_text)
                continue

            # 変換の結果、kanaが空になった場合はエラーとする。
            if len(kana_with_features_list) == 0:
                error_text = f"カナが空になった可能性があります: {utt_id}\n"
                print(error_text)
                error_w.write_raw(error_text)
                continue

            # pyopenjtalk の警告を取得
            warning_message = ""
            for warn in stderr_kana_with_features:
                if warn.strip():
                    warning_message += warn.strip()

            # pyopenjtalk の警告がある場合はエラーとする。
            if len(warning_message) > 0:
                error_text = (
                    f"pyopenjtalk の警告があります: {utt_id} {warning_message}\n"
                )
                print(error_text)
                if ignore_pyopenjtalk_warnings:
                    error_w.write_raw(error_text)
                    continue

            kana_w.write_raw(f"{utt_id} {kana_with_features_list}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_char_text_file_path", type=str, required=True)
    parser.add_argument(
        "--output_kana_with_features_file_path", type=str, required=True
    )
    parser.add_argument("--output_error_file_path", type=str, required=True)

    parser.add_argument(
        "--ignore_filler",
        type=bool,
        default=True,
        help="フィラーを無視するかどうか",
    )
    parser.add_argument(
        "--simple_morph_analysis",
        type=bool,
        default=True,
        help="シンプルな形態素解析を使用するかどうか",
    )
    parser.add_argument(
        "--ignore_pyopenjtalk_warnings",
        type=bool,
        default=True,
        help="pyopenjtalkの警告を無視するかどうか (うまく形態素解析ができていない可能性があるものを除去するため)",
    )
    args = parser.parse_args()

    input_char_text_file_path = Path(args.input_char_text_file_path)
    output_kana_with_features_file_path = Path(args.output_kana_with_features_file_path)
    output_error_file_path = Path(args.output_error_file_path)
    ignore_filler = args.ignore_filler
    simple_morph_analysis = args.simple_morph_analysis
    ignore_pyopenjtalk_warnings = args.ignore_pyopenjtalk_warnings

    convert_char_to_kana_with_features(
        input_char_text_file_path,
        output_kana_with_features_file_path,
        output_error_file_path,
        ignore_filler=ignore_filler,
        simple_morph_analysis=simple_morph_analysis,
        ignore_pyopenjtalk_warnings=ignore_pyopenjtalk_warnings,
    )
