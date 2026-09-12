"""A Wordle clone: game logic plus an optional pygame visualizer."""

from wordle.game import GameManager, WordList  # noqa: F401
from wordle.logic import check_word  # noqa: F401

__all__ = [
    "GameManager",
    "WordList",
    "check_word",
]
