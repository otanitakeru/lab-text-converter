import os

import yaml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_TOKEN_SET: set | None = None
_MAX_TOKEN_LEN: int | None = None


def _get_token_set_and_max_token_len() -> tuple[set, int]:
    """トークンセットと最大長をキャッシュから取得（初回のみファイル読み込み）"""
    global _TOKEN_SET, _MAX_TOKEN_LEN
    if _TOKEN_SET is None:
        with open(
            os.path.join(CURRENT_DIR, "../kana2phone/kana2phone.yaml"),
            "r",
            encoding="utf-8",
        ) as f:
            keys = list(yaml.safe_load(f).keys()) + ["ー"]
        _TOKEN_SET = set(keys)
        _MAX_TOKEN_LEN = max(len(k) for k in _TOKEN_SET)

    if _MAX_TOKEN_LEN is None:
        raise ValueError("カナの最大長が取得できませんでした")

    return _TOKEN_SET, _MAX_TOKEN_LEN


def split_kana(kana: str) -> list[str]:
    """カナ文字列を最長一致グリーディマッチで分割する"""
    token_set, max_len = _get_token_set_and_max_token_len()

    tokens = []
    i = 0
    while i < len(kana):
        matched = False
        for length in range(min(max_len, len(kana) - i), 0, -1):
            candidate = kana[i : i + length]
            if candidate in token_set:
                tokens.append(candidate)
                i += length
                matched = True
                break
        if not matched:
            i += 1

    return tokens
