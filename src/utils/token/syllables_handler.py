import os

from utils.token.syllables_phone_handler import get_syllable_to_phone_map

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_SYLLABLE_SET: set | None = None
_MAX_SYLLABLE_LEN: int | None = None


def _get_syllable_set_and_max_syllable_len() -> tuple[set, int]:
    """音節セットと最大長をキャッシュから取得（初回のみファイル読み込み）"""

    global _SYLLABLE_SET, _MAX_SYLLABLE_LEN

    if _SYLLABLE_SET is None:

        syllable_to_phone_map = get_syllable_to_phone_map()
        keys = list(syllable_to_phone_map.keys()) + ["ー"]
        _SYLLABLE_SET = set(keys)
        _MAX_SYLLABLE_LEN = max(len(k) for k in _SYLLABLE_SET)

    if _MAX_SYLLABLE_LEN is None:
        raise ValueError("カナの最大長が取得できませんでした")

    return _SYLLABLE_SET, _MAX_SYLLABLE_LEN


def split_syllables(kana: str) -> list[str]:

    syllable_set, max_len = _get_syllable_set_and_max_syllable_len()

    syllables = []
    i = 0
    while i < len(kana):
        matched = False
        for length in range(min(max_len, len(kana) - i), 0, -1):
            candidate = kana[i : i + length]
            if candidate in syllable_set:
                syllables.append(candidate)
                i += length
                matched = True
                break
        if not matched:
            i += 1

    if "".join(syllables) != kana:
        raise ValueError(f"カナ文字列が分割できませんでした: {kana} -> {syllables}")

    return syllables
