import re

import jaconv

from utils.token.phone_handler import validate_phones
from utils.token.syllables_handler import split_syllables
from utils.token.syllables_phone_handler import get_syllable_to_phone_map

SYLLABLE_TO_PHONE_MAP = get_syllable_to_phone_map()


def _convert_syllables_to_phones(
    syllables: list[str],
) -> list[str]:
    """音節リストを音素リストに変換する

    Args:
        syllables: 音節のリスト

    Returns:
        (音素のリスト, エラーのリスト)
    """

    phones = []

    for syllable in syllables:
        if syllable in SYLLABLE_TO_PHONE_MAP:
            phones.extend(SYLLABLE_TO_PHONE_MAP[syllable])
        else:
            # 長音が検出された場合
            if "ー" in syllable:
                if not phones and len(phones) == 0:
                    raise ValueError("文章の最初に長音(ー)が検出された")

                phones[-1] += ":"
                continue
            else:
                raise ValueError(f"未知のカナ文字が検出された: {syllable}")

    return phones


def _repeat_phone_for_long_vowel(
    phones: list[str],
) -> list[str]:
    processed_phones = []
    for phone in phones:
        if ":" in phone:
            processed_phones.append(phone[:-1])  # 最後のコロンを除いた音素
            processed_phones.append(phone[:-1])

        else:
            processed_phones.append(phone)

    return processed_phones


def kana2phone(
    kana: str,
    use_colon_for_long_vowel: bool = True,
) -> list[str]:
    """カナ文字列を音素リストに変換する

    Args:
        kana: カナ文字列（ひらがな・カタカナ両方対応）
        use_colon_for_long_vowel: 長母音の場合、コロン記号を使用するかどうか
            True: コロン記号を使用（デフォルト）
            False: 前の音素を繰り返す
    Returns:
        (音素のリスト, エラーのリスト)
    """
    kana = jaconv.hira2kata(kana)

    # 音節に分割
    syllables = split_syllables(kana)
    # 音節を音素に変換
    phones = _convert_syllables_to_phones(syllables)

    # 音素を検証
    validate_phones(phones)

    # 長母音の場合、前の音素を繰り返す
    if not use_colon_for_long_vowel:
        phones = _repeat_phone_for_long_vowel(phones)

    return phones


def main():
    kana = "キャッカンシヒョー"

    # 前の母音を繰り返す
    try:
        phones = kana2phone(kana, use_colon_for_long_vowel=False)
    except ValueError as e:
        print(f"エラー: {e}")
        return
    print(phones)


if __name__ == "__main__":
    main()
