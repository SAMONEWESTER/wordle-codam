"""Entry point: wires pygame input and rendering to the game logic.

Run with `python -m wordle` (the Makefile does this for you inside
the project's .venv).
"""

import sys

import pygame

from wordle.game import LOST, PLAYING, WON, GameSession, HighScore, WordList
from wordle.visuals import Board, Button

INITIAL_WINDOW_SIZE = (420, 620)
BACKGROUND_COLOR = (18, 18, 19)
MESSAGE_COLOR = (220, 60, 60)
HEADER_TEXT_COLOR = (255, 255, 255)

TOP_MARGIN = 90
BUTTON_SIZE = (120, 44)
BUTTON_GAP = 20
BUTTON_TOP_GAP = 30
BUTTON_BOTTOM_PADDING = 20
BOTTOM_MARGIN = BUTTON_TOP_GAP + BUTTON_SIZE[1] + BUTTON_BOTTOM_PADDING
SIDE_PADDING = 10

WORD_LIST_PATH = "words.txt"
HIGH_SCORE_PATH = "highscore.json"


def handle_key(session: GameSession, event: pygame.event.Event) -> None:
    if event.key == pygame.K_RETURN:
        session.submit_guess()
    elif event.key == pygame.K_BACKSPACE:
        session.remove_letter()
    elif event.unicode.isalpha():
        session.add_letter(event.unicode)


def handle_click(
    session: GameSession,
    retry_button: Button,
    quit_button: Button,
    mouse_pos: tuple[int, int],
) -> bool:
    """Returns False if the click should end the game loop."""
    if session.status == PLAYING:
        return True
    if retry_button.is_clicked(mouse_pos):
        session.retry()
    elif quit_button.is_clicked(mouse_pos):
        return False
    return True


def end_of_game_text(session: GameSession) -> str:
    if session.status == WON:
        return "You got it!"
    if session.status == LOST:
        return f"Out of guesses. The word was {session.game.answer.upper()}."
    return ""


def build_buttons(
    window_size: tuple[int, int], board_bottom: int
) -> tuple[Button, Button]:
    width, _ = window_size
    button_width, button_height = BUTTON_SIZE
    total_width = button_width * 2 + BUTTON_GAP
    left = (width - total_width) // 2
    left = max(SIDE_PADDING, min(left, width - total_width - SIDE_PADDING))
    top = board_bottom + BUTTON_TOP_GAP

    retry_rect = pygame.Rect(left, top, button_width, button_height)
    quit_rect = pygame.Rect(
        left + button_width + BUTTON_GAP, top, button_width, button_height
    )
    return Button(retry_rect, "Retry"), Button(quit_rect, "Quit")


def draw_header(
    surface: pygame.Surface,
    font: pygame.font.Font,
    session: GameSession,
    window_width: int,
) -> None:
    best = session.high_score.value
    streak_text = f"Streak: {session.streak}   Best: {best}"
    text = font.render(streak_text, True, HEADER_TEXT_COLOR)
    surface.blit(text, text.get_rect(center=(window_width // 2, 30)))

    status_text = session.game.message or end_of_game_text(session)
    color = MESSAGE_COLOR if session.game.message else HEADER_TEXT_COLOR
    if status_text:
        status = font.render(status_text, True, color)
        surface.blit(status, status.get_rect(center=(window_width // 2, 60)))


def build_letter_font(square_size: int) -> pygame.font.Font:
    return pygame.font.SysFont("arial", int(square_size * 0.5), bold=True)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(INITIAL_WINDOW_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Wordle")
    clock = pygame.time.Clock()

    header_font = pygame.font.SysFont("arial", 18)
    button_font = pygame.font.SysFont("arial", 20, bold=True)

    session = GameSession(WordList(WORD_LIST_PATH), HighScore(HIGH_SCORE_PATH))
    board = Board()

    window_size = INITIAL_WINDOW_SIZE
    board.layout(window_size, TOP_MARGIN, BOTTOM_MARGIN)
    retry_button, quit_button = build_buttons(window_size, board.bottom)

    letter_font_size = board.square_size
    letter_font = build_letter_font(letter_font_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_size = (event.w, event.h)
                screen = pygame.display.set_mode(
                    window_size, pygame.RESIZABLE
                )
                board.layout(window_size, TOP_MARGIN, BOTTOM_MARGIN)
                retry_button, quit_button = build_buttons(
                    window_size, board.bottom
                )
            elif event.type == pygame.KEYDOWN and session.status == PLAYING:
                handle_key(session, event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = handle_click(
                    session, retry_button, quit_button, event.pos
                )

        if board.square_size != letter_font_size:
            letter_font_size = board.square_size
            letter_font = build_letter_font(letter_font_size)

        board.sync_with_game(session.game)

        screen.fill(BACKGROUND_COLOR)
        board.draw(screen, letter_font)
        draw_header(screen, header_font, session, window_size[0])

        if session.status != PLAYING:
            retry_button.draw(screen, button_font)
            quit_button.draw(screen, button_font)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()