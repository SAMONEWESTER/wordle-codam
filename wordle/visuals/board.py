"""Pygame visuals for the Wordle board.

No game rules live here. Square and Board only know how to draw
themselves from whatever state they are handed; wordle.game is the
only place that decides what that state should be. Board also has
no idea the window can be resized, layout() is just told the space
it has to work with and lays its squares out to fit it.
"""

import pygame

from wordle.game import GUESS_COUNT
from wordle.logic import GREEN, GREY, WORD_LENGTH, YELLOW

EMPTY = "empty"
TYPING = "typing"

FILL_COLORS = {
    EMPTY: (18, 18, 19),
    TYPING: (18, 18, 19),
    GREEN: (83, 141, 78),
    YELLOW: (181, 159, 59),
    GREY: (58, 58, 60),
}
BORDER_COLORS = {
    EMPTY: (58, 58, 60),
    TYPING: (86, 87, 88),
    GREEN: (83, 141, 78),
    YELLOW: (181, 159, 59),
    GREY: (58, 58, 60),
}
LETTER_COLOR = (255, 255, 255)

MIN_SQUARE_SIZE = 36
MAX_SQUARE_SIZE = 90
GAP_RATIO = 0.15
BORDER_WIDTH = 2
WIDTH_USE_RATIO = 0.9
HEIGHT_USE_RATIO = 0.9


class Square:
    """One letter tile. Knows how to draw its own state and letter."""

    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.letter: str = ""
        self.state: str = EMPTY

    def set_rect(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def set_content(self, letter: str, state: str) -> None:
        self.letter = letter.upper()
        self.state = state

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, FILL_COLORS[self.state], self.rect)
        pygame.draw.rect(
            surface, BORDER_COLORS[self.state], self.rect, BORDER_WIDTH
        )
        if self.letter:
            text = font.render(self.letter, True, LETTER_COLOR)
            surface.blit(text, text.get_rect(center=self.rect.center))


class Board:
    """A grid of Squares that re-lays itself out when the window resizes."""

    def __init__(self):
        self.squares: list[list[Square]] = [
            [Square() for _ in range(WORD_LENGTH)]
            for _ in range(GUESS_COUNT)
        ]
        self.square_size: int = MIN_SQUARE_SIZE

    def layout(
        self,
        window_size: tuple[int, int],
        top_margin: int,
        bottom_margin: int = 0,
    ) -> None:
        """Recompute every square's rect to fit the current window.

        top_margin and bottom_margin reserve space above and below
        the grid (for header text and the Retry/Quit buttons) so the
        grid itself never grows into that space.
        """
        width, height = window_size
        available_height = max(height - top_margin - bottom_margin, 1)

        size_for_width = self._fit(width * WIDTH_USE_RATIO, WORD_LENGTH)
        size_for_height = self._fit(
            available_height * HEIGHT_USE_RATIO, GUESS_COUNT
        )
        square_size = min(size_for_width, size_for_height)
        square_size = max(MIN_SQUARE_SIZE, min(MAX_SQUARE_SIZE, square_size))
        self.square_size = int(square_size)

        gap = int(self.square_size * GAP_RATIO)
        grid_width = WORD_LENGTH * self.square_size
        grid_width += (WORD_LENGTH - 1) * gap
        grid_height = GUESS_COUNT * self.square_size
        grid_height += (GUESS_COUNT - 1) * gap

        left = (width - grid_width) // 2
        top = top_margin + (available_height - grid_height) // 2

        for row_index, row in enumerate(self.squares):
            for col_index, square in enumerate(row):
                x = left + col_index * (self.square_size + gap)
                y = top + row_index * (self.square_size + gap)
                square.set_rect(
                    pygame.Rect(x, y, self.square_size, self.square_size)
                )

    @staticmethod
    def _fit(budget: float, count: int) -> float:
        return budget / (count + (count - 1) * GAP_RATIO)

    def sync_with_game(self, game) -> None:
        """Pull the latest state out of the GameManager and apply it."""
        for row_index, row in enumerate(self.squares):
            if row_index < len(game.board):
                self._fill_submitted_row(row, game.board[row_index])
            elif row_index == len(game.board):
                self._fill_typing_row(row, game.current_guess)
            else:
                for square in row:
                    square.set_content("", EMPTY)

    @staticmethod
    def _fill_submitted_row(row, result) -> None:
        for square, letter_result in zip(row, result):
            square.set_content(
                letter_result["letter"], letter_result["state"]
            )

    @staticmethod
    def _fill_typing_row(row, current_guess: str) -> None:
        for index, square in enumerate(row):
            if index < len(current_guess):
                square.set_content(current_guess[index], TYPING)
            else:
                square.set_content("", EMPTY)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for row in self.squares:
            for square in row:
                square.draw(surface, font)

    @property
    def bottom(self) -> int:
        """Y coordinate just past the last row, for placing UI below it."""
        return self.squares[-1][0].rect.bottom