from pathlib import Path
from typing import IO, Iterable, Iterator, List, Optional

_DEFAULT_WRITE_BUFFER_SIZE = 8192
_DEFAULT_BATCH_SIZE = 1000


# ---------------------------------------------------------------------------
# 書き込みユーティリティ
# ---------------------------------------------------------------------------


class BufferedTextWriter:
    """バッチバッファリング付きテキストファイルライター。

    大量行を逐次書き込む際に、毎回 `f.write()` を呼ぶ代わりに内部バッファに
    蓄積し、`batch_size` 行に達したタイミングで `writelines` を一括発行する。
    `with` ブロック終了時に残りバッファを自動フラッシュ・クローズする。

    Examples:
        >>> with BufferedTextWriter(Path("out.txt"), batch_size=500) as w:
        ...     for utt_id, text in data:
        ...         w.write(utt_id, text)
    """

    def __init__(
        self,
        path: Path,
        *,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        io_buffer_size: int = _DEFAULT_WRITE_BUFFER_SIZE,
        encoding: str = "utf-8",
        mode: str = "w",
    ) -> None:
        self._path = path
        self._batch_size = batch_size
        self._io_buffer_size = io_buffer_size
        self._encoding = encoding
        self._mode = mode
        self._buf: list[str] = []
        self._f: Optional[IO[str]] = None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def write_line(self, line: str, end="\n") -> None:
        """任意の文字列を1行としてバッファに追加する"""
        self._buf.append(line + end)
        if len(self._buf) >= self._batch_size:
            self.flush()

    def flush(self) -> None:
        """バッファをファイルに書き出す。"""
        if self._buf and self._f is not None:
            self._f.writelines(self._buf)
            self._buf.clear()

    # ------------------------------------------------------------------
    # context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "BufferedTextWriter":
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(
            self._path,
            self._mode,
            encoding=self._encoding,
            buffering=self._io_buffer_size,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.flush()
        if self._f is not None:
            self._f.close()
            self._f = None


# ---------------------------------------------------------------------------
# 読み込みユーティリティ
# ---------------------------------------------------------------------------


class BufferedTextReader:
    """バッチ単位で行をイテレートするテキストファイルリーダー。

    ファイルを開いたままコンテキストマネージャで保持し、`iter_batches` で
    `batch_size` 行ずつリストとして取り出せる。行単位で処理しつつ、
    バッチ処理のまとまりを維持したい場合に使用する。

    Examples:
        >>> with BufferedTextReader(Path("input.txt"), batch_size=500) as r:
        ...     for batch in r.iter_batches():
        ...         process(batch)  # batch: list[str]
    """

    def __init__(
        self,
        path: Path,
        *,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        encoding: str = "utf-8",
    ) -> None:
        self._path = path
        self._batch_size = batch_size
        self._encoding = encoding
        self._f: Optional[IO[str]] = None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def iter_batches(self) -> Iterator[list[str]]:
        """`batch_size` 行ずつ生の行文字列リストをyieldする（strip済み、空行除外）。"""
        if self._f is None:
            raise RuntimeError("with ブロック内で呼び出してください")
        batch: list[str] = []
        for line in self._f:
            line = line.strip()
            if not line:
                continue
            batch.append(line)
            if len(batch) >= self._batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def iter_lines(self) -> Iterator[str]:
        """1行ずつ生の行文字列をyieldする（strip済み、空行除外）。"""
        if self._f is None:
            raise RuntimeError("with ブロック内で呼び出してください")
        for line in self._f:
            line = line.strip()
            if line:
                yield line

    # ------------------------------------------------------------------
    # context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "BufferedTextReader":
        self._f = open(self._path, "r", encoding=self._encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._f is not None:
            self._f.close()
            self._f = None


# ---------------------------------------------------------------------------
# シンプルな単発書き込みヘルパー（小規模）
# ---------------------------------------------------------------------------


def write_text_lines(
    lines: Iterable[str],
    output_path: Path,
    *,
    encoding: str = "utf-8",
) -> None:
    """任意の文字列イテラブルをテキストファイルへ書き出す。

    Args:
        lines: 書き出す行のイテラブル（末尾改行は含まなくてよい）。
        output_path: 書き出し先ファイルパス。
        encoding: ファイルエンコーディング。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding=encoding) as f:
        f.writelines(f"{line}\n" if not line.endswith("\n") else line for line in lines)


# ---------------------------------------------------------------------------
# シンプルな単発読み込みヘルパー（小規模）
# ---------------------------------------------------------------------------


def read_text_lines(
    input_path: Path,
    *,
    encoding: str = "utf-8",
) -> List[str]:
    """テキストファイルの全行をリストで返す（strip済み、空行除外）。

    Args:
        input_path: 読み込むファイルのパス。
        encoding: ファイルエンコーディング。

    Returns:
        各行の文字列リスト。
    """
    with open(input_path, "r", encoding=encoding) as f:
        return [line.strip() for line in f if line.strip()]
