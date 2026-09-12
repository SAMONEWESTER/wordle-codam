"""Ties one GameManager round to a running win streak and high score."""

from wordle.game.high_score import HighScore
from wordle.game.manager import LOST, WON, GameManager
from wordle.game.word_list import WordList


class GameSession:
    """Plays round after round, tracking consecutive wins.

    A "round" is one full game of Wordle (up to 6 guesses at one
    answer). The session starts a fresh round on retry, and keeps a
    running streak of consecutive rounds won, persisting the best
    streak ever seen through the HighScore it is given.
    """

    def __init__(self, word_list: WordList, high_score: HighScore):
        self.word_list = word_list
        self.high_score = high_score
        self.streak = 0
        self.game: GameManager = self._new_round()
        self._recorded = False

    @property
    def status(self) -> str:
        return self.game.status

    def add_letter(self, letter: str) -> None:
        self.game.add_letter(letter)

    def remove_letter(self) -> None:
        self.game.remove_letter()

    def submit_guess(self) -> None:
        self.game.submit_guess()
        self._record_result_once()

    def retry(self) -> None:
        """Start a fresh round with a new random answer."""
        self.game = self._new_round()
        self._recorded = False

    def _new_round(self) -> GameManager:
        return GameManager(self.word_list)

    def _record_result_once(self) -> None:
        """Update the streak the first time a round finishes.

        submit_guess() can still be called after a round is already
        won or lost (GameManager just ignores it), so this guards
        against counting the same result twice.
        """
        if self._recorded:
            return
        if self.game.status == WON:
            self.streak += 1
            self.high_score.update_if_higher(self.streak)
            self._recorded = True
        elif self.game.status == LOST:
            self.streak = 0
            self._recorded = True