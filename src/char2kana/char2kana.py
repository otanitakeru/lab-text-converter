import re

import pyopenjtalk  # type: ignore


class Char2KanaError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _is_all_kana(kana: str):
    """
    Args:
        kana: カナ文字列
    """
    for c in kana:
        if not re.match(r"[ァ-ンヴー]", c):
            raise Char2KanaError(f"Detected non-kana character: {c}")


def char2kana_pyopenjtalk(
    char: str,
    include_features: bool = False,
    ignore_filler: bool = False,
    simple_morph_analysis: bool = True,
) -> str:
    """
    Args:
        char: 文字列
        include_features: 特徴を含めるかどうか
        ignore_filler: フィラーを無視するかどうか
        simple_morph_analysis: シンプルな形態素解析を使用するかどうか
    """
    njd_feature, _ = pyopenjtalk.run_frontend_detailed(char)

    prons = []
    features = []
    for n in njd_feature:
        surface = n["string"]
        pron = n["pron"]  # 読み
        pos_group1 = n["pos_group1"]  # 品詞細分類1
        pos_group2 = n["pos_group2"]  # 品詞細分類2
        pos_group3 = n["pos_group3"]  # 品詞細分類3

        if n["pos"] == "記号":
            continue

        if ignore_filler and n["pos"] == "フィラー":
            continue

        # 特殊文字を削除
        for c in "’":
            pron = pron.replace(c, "")

        if simple_morph_analysis and pos_group1 != "*":
            pos = n["pos"] + "-" + pos_group1.split("／")[0]
        else:
            pos = n["pos"]
            if pos_group1 != "*":
                pos += "-" + pos_group1
                if pos_group2 != "*":
                    pos += "-" + pos_group2
                    if pos_group3 != "*":
                        pos += "-" + pos_group3

        _is_all_kana(pron)

        if pron == "ー" and len(features) > 0:

            b_surface, b_pos, b_pron = features[-1].split("+")

            surface = b_surface + surface
            pos = b_pos + pos
            pron = b_pron + pron

            features[-1] = f"{surface}+{pos}+{pron}"
            continue

        if include_features:
            features.append(f"{surface}+{pos}+{pron}")
        else:
            prons.append(pron)

    if include_features:
        return " ".join(features)
    else:
        return "".join(prons)


if __name__ == "__main__":
    text = "こんにちは"
    print(char2kana_pyopenjtalk(text))
    print(char2kana_pyopenjtalk(text, include_features=True))
