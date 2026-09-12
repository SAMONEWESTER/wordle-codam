"""Core word-checking rules"""

from wordle.logic.checker import (  # noqa: F401
    GREEN,
    GREY,
    WORD_LENGTH,
    YELLOW,
    check_word,
)

__all__ = [
    "check_word",
    "GREEN",
    "YELLOW",
    "GREY",
    "WORD_LENGTH",
]
