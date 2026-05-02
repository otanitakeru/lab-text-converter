import os

from utils.token.syllables_phone_handler import get_syllable_to_phone_map

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_PHONE_SET: set | None = None


def get_phone_set() -> set:
    global _PHONE_SET
    if _PHONE_SET is None:
        syllable_to_phone_map = get_syllable_to_phone_map()
        _PHONE_SET = set(
            phone for phones in syllable_to_phone_map.values() for phone in phones
        )

        _PHONE_SET.add("a:")
        _PHONE_SET.add("i:")
        _PHONE_SET.add("u:")
        _PHONE_SET.add("e:")
        _PHONE_SET.add("o:")

    return _PHONE_SET


def validate_phones(phones: list[str]) -> None:
    phone_set = get_phone_set()
    for phone in phones:
        if phone not in phone_set:
            raise ValueError(f"未知の音素が検出されました: {phone}")


def validate_phones_sequence(phones: list[str]) -> None:
    phone_set = get_phone_set()
    for i, phone in enumerate(phones):

        if phone not in phone_set:
            raise ValueError(f"未知の音素が検出されました: {phone}")

        if i == 0:
            if phone == "q":
                raise ValueError("文頭にqが検出されました")
            if phone == "N":
                raise ValueError("文頭にNが検出されました")
        else:
            # HACK: "お父さんって"は許容する？
            # if phones[i - 1] == "N" and phone == "q":
            #     raise ValueError("Nの後にqが検出されました")
            if phones[i - 1] == "q" and phone == "N":
                raise ValueError("qの後にNが検出されました")
            if phones[i - 1] == "q" and phone == "q":
                raise ValueError("連続するqが検出されました")
            if phones[i - 1] == "N" and phone == "N":
                raise ValueError("連続するNが検出されました")

            # HACK: "通って"は"とーって"となるので許容する？
            # if ":" in phones[i - 1] and phone == "q":
            #     raise ValueError("長母音の後にqが検出されました")
