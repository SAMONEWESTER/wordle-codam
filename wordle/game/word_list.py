"""Loads the list of legal guess words from a text file."""

import random


class WordList:
    """Reads one word per line from a file into a plain list."""

    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.words: list[str] = []
        self._load()

    def _read_lines(self):
        with open(self.file_path) as word_file:
            for line in word_file:
                yield line.strip()

    def _load(self) -> None:
        for word in self._read_lines():
            if word:
                self.words.append(word.lower())

    def is_legal(self, word: str) -> bool:
        return word.lower() in self.words

    def random_word(self) -> str:
        return random.choice(self.words)
