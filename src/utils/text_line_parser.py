from typing import List, Tuple


def parse_text_line(line: str) -> Tuple[str, str]:
    """Kaldi形式の1行 ``"utt_id text..."`` を ``(utt_id, text)`` に変換する。

    先頭トークンが発話ID、残りのすべてがテキストとして扱われる。

    Args:
        line: strip済みの1行文字列。空行は渡さないこと。

    Returns:
        ``(utt_id, text)`` のタプル。

    Examples:
        >>> parse_text_line("utt001 hello world")
        ('utt001', 'hello world')
    """
    parts = line.split(" ", 1)
    if len(parts) != 2:
        raise ValueError(f"不正な行: {line}")
    return parts[0], parts[1]


def parse_text_phones_line(line: str) -> Tuple[str, List[str]]:
    """Kaldi形式の1行 ``"utt_id token1 token2 ..."`` を ``(utt_id, [token1, token2, ...])`` に変換する。

    先頭トークンが発話ID、以降のスペース区切りトークン列がphone/tokenリストになる。

    Args:
        line: strip済みの1行文字列。空行は渡さないこと。

    Returns:
        ``(utt_id, tokens)`` のタプル。

    Raises:
        ValueError: スペース区切りで3フィールド以上存在しない場合（トークンが1つ以下）。

    Examples:
        >>> parse_text_phones_line("utt001 a b c")
        ('utt001', ['a', 'b', 'c'])
    """
    parts = line.split(" ")
    if len(parts) > 2:
        utt_id = parts[0]
        tokens = parts[1:]
        return utt_id, tokens
    elif len(parts) == 2:
        print(
            f"warning: 使用されているテキストファイルの形式が間違っている可能性がある: {line}"
        )
        utt_id = parts[0]
        text = parts[1]
        return utt_id, [text]
    else:
        raise ValueError(f"不正な行: {line}")
