"""Game rules and turn tracking for a game of Wordle.

GameManager knows nothing about pygame or the console. It only
tracks state and exposes it, so any front end (pygame, a terminal
loop, a test file) can drive it the same way and read the same
info back out.
"""

from wordle.game.word_list import WordList
from wordle.logic import GREEN, WORD_LENGTH, check_word

GUESS_COUNT = 6

PLAYING = "playing"
WON = "won"
LOST = "lost"


class GameManager:
    """Owns one game: the answer, the guesses so far, and the status."""

    def __init__(self, word_list: WordList, answer: str | None = None):
        self.word_list = word_list
        self.answer: str = (answer or word_list.random_word()).lower()

        self.board: list[list[dict[str, str]]] = []
        self.current_guess: str = ""
        self.status: str = PLAYING
        self.message: str = ""

    @property
    def row_number(self) -> int:
        """How many guesses have been submitted so far."""
        return len(self.board)

    def add_letter(self, letter: str) -> None:
        """Type one more letter into the guess currently in progress."""
        if self.status != PLAYING:
            return
        if len(self.current_guess) < WORD_LENGTH and letter.isalpha():
            self.current_guess += letter.lower()
            self.message = ""

    def remove_letter(self) -> None:
        """Backspace: drop the last typed letter, if there is one."""
        if self.status != PLAYING:
            return
        self.current_guess = self.current_guess[:-1]

    def submit_guess(self) -> None:
        """Lock in the current guess and score it, if it is valid."""
        if self.status != PLAYING:
            return

        if len(self.current_guess) != WORD_LENGTH:
            self.message = "Word needs to be 5 letters."
            return

        if not self.word_list.is_legal(self.current_guess):
            self.message = "Word not in word list!"
            return

        result = check_word(self.current_guess, self.answer)
        self.board.append(result)
        self.current_guess = ""
        self.message = ""
        self._update_status(result)

    def _update_status(self, result: list[dict[str, str]]) -> None:
        won = all(letter["state"] == GREEN for letter in result)
        if won:
            self.status = WON
        elif self.row_number >= GUESS_COUNT:
            self.status = LOST
