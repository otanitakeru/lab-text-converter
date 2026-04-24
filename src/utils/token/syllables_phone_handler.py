import os

import yaml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_KANA_TO_SYLLABLE_MAP: dict | None = None


def get_syllable_to_phone_map() -> dict:
    """YAMLマップをキャッシュから取得（初回のみファイル読み込み）"""
    global _KANA_TO_SYLLABLE_MAP
    if _KANA_TO_SYLLABLE_MAP is None:
        with open(
            os.path.join(CURRENT_DIR, "kana2phone.yaml"), "r", encoding="utf-8"
        ) as f:
            _KANA_TO_SYLLABLE_MAP = yaml.safe_load(f)
    if _KANA_TO_SYLLABLE_MAP is None:
        raise ValueError("kana2phone.yaml が読み込めませんでした")
    return _KANA_TO_SYLLABLE_MAP
