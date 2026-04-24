import os
import re
import unicodedata
from typing import Optional

import neologdn
from num2words import num2words

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "symbols.txt"), "r") as f:
    _SPECIAL_SYMBOLS = [line.strip() for line in f if line.strip()]

_SPECIAL_SYMBOLS_TABLE = str.maketrans({s: " " for s in _SPECIAL_SYMBOLS})


def normalize_text(
    text: str,
    repeat: Optional[int] = None,
    convert_kanji_from_numbers: bool = True,
    lower_case_only: bool = False,
    delimiter: str = " ",
) -> str:
    """
    文を正規化

    記号は削除せず、読点「、」も保存される。

    Args:
        text: 正規化するテキスト
        repeat: neologdnの繰り返し文字正規化の閾値
        convert_kanji_from_numbers: 数字を漢字に変換するかどうか
        lower_case_only: 小文字に変換するかどうか
        delimiter: 記号を正規化する際に変換する文字。デフォルトはスペース。
    Returns:
        normalized_text: 正規化後のテキスト
    """

    text = text.translate(_SPECIAL_SYMBOLS_TABLE)

    # Unicode正規化（NFKC: 互換等価性に基づく正規化）
    # 全角英数字→半角、異体字の統一など
    # １２３ａｂｃｱｲｳｴｵ①㈱㌖ -> 123abcアイウエオ1(株)キロメートル
    text = unicodedata.normalize("NFKC", text)

    # 単語間のスペースがneologdnで削除されるので、placeholderで置換
    placeholder = "\x01"
    text = re.sub(r"\s+", placeholder, text)

    # neologdnで正規化（繰り返し文字、長音記号など）
    if repeat is not None:
        text = neologdn.normalize(text, repeat=repeat)
    else:
        text = neologdn.normalize(text)

    text = text.replace(placeholder, " ")

    if convert_kanji_from_numbers:
        text = re.sub(
            r"(?<=[零〇一二三四五六七八九十百千万億兆京垓秭穣溝澗正載極])[.．](?=[零〇一二三四五六七八九十百千万億兆京垓秭穣溝澗正載極])",
            "点",
            text,
        )
        matches = list(re.finditer(r"\d+(?:[.．]\d+)?", text))
        offset = 0
        for m in matches:
            m_group = m.group()
            replacement = num2words(m_group, lang="ja")
            start, end = m.start() + offset, m.end() + offset
            text = text[:start] + replacement + text[end:]
            offset += len(replacement) - (m.end() - m.start())
        text = text.replace(".", " ").replace("．", " ")
    else:
        # 数字[.．]数字（小数点）はそのまま保持し、それ以外の [.．] のみスペースに置換
        text = re.sub(r"(?<!\d)[.．]|[.．](?!\d)", " ", text)
        text = text.replace("．", ".")

    if lower_case_only:
        text = text.lower()

    text = text.replace(" ", delimiter)

    return text
