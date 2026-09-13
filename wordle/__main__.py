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

HIGH_SCORE_PATH = "highscore.json"

# Word lists the player can choose from before a game starts. Each
# entry is (button label, path to the word file).
WORD_LIST_OPTIONS = [
    ("Shitty word list", "words.txt"),
    ("Great amazing word list", "words2.txt"),
]

MENU_BUTTON_HEIGHT = 54
MENU_BUTTON_GAP = 24
MENU_BUTTON_PADDING_X = 36
MENU_TITLE_TOP = 90


def handle_key(session: GameSession, event: pygame.event.Event) -> None:
    if event.key == pygame.K_RETURN:
        session.submit_guess()
    elif event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
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


def build_menu_buttons(
    window_size: tuple[int, int], font: pygame.font.Font
) -> list[tuple[Button, str]]:
    """Lay out one button per word list option, stacked and centered.

    Button width is sized from the longest label so it stays
    readable at any window size, and is clamped so it never runs
    past the window edges.
    """
    width, height = window_size
    max_text_width = max(
        font.size(label)[0] for label, _ in WORD_LIST_OPTIONS
    )
    button_width = max_text_width + MENU_BUTTON_PADDING_X * 2
    button_width = min(button_width, width - SIDE_PADDING * 2)
    left = (width - button_width) // 2

    option_count = len(WORD_LIST_OPTIONS)
    total_height = (
        MENU_BUTTON_HEIGHT * option_count
        + MENU_BUTTON_GAP * (option_count - 1)
    )
    top = MENU_TITLE_TOP + ((height - MENU_TITLE_TOP) - total_height) // 2

    buttons = []
    for index, (label, path) in enumerate(WORD_LIST_OPTIONS):
        y = top + index * (MENU_BUTTON_HEIGHT + MENU_BUTTON_GAP)
        rect = pygame.Rect(left, y, button_width, MENU_BUTTON_HEIGHT)
        buttons.append((Button(rect, label), path))
    return buttons


def draw_menu(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    button_font: pygame.font.Font,
    window_width: int,
    buttons: list[tuple[Button, str]],
) -> None:
    title = title_font.render(
        "Choose a word list", True, HEADER_TEXT_COLOR
    )
    surface.blit(
        title, title.get_rect(center=(window_width // 2, MENU_TITLE_TOP))
    )
    for button, _ in buttons:
        button.draw(surface, button_font)


def run_menu(
    screen: pygame.Surface,
    window_size: tuple[int, int],
    title_font: pygame.font.Font,
    button_font: pygame.font.Font,
) -> tuple[pygame.Surface, tuple[int, int], str] | None:
    """Show the word list picker until the player chooses or quits.

    Returns the (possibly resized) screen, the current window size,
    and the chosen word list path, or None if the player quit.
    """
    clock = pygame.time.Clock()
    buttons = build_menu_buttons(window_size, button_font)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            elif event.type == pygame.VIDEORESIZE:
                # The window manager has already resized the actual
                # window by this point. Calling set_mode() again
                # here recreates the underlying window, which on
                # Linux fights with the window manager's live-resize
                # drag and makes the window flicker and snap back to
                # its old size. Just pick up the surface SDL already
                # resized for us instead.
                window_size = (event.w, event.h)
                screen = pygame.display.get_surface()
                buttons = build_menu_buttons(window_size, button_font)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, path in buttons:
                    if button.is_clicked(event.pos):
                        return screen, window_size, path

        screen.fill(BACKGROUND_COLOR)
        draw_menu(
            screen, title_font, button_font, window_size[0], buttons
        )
        pygame.display.flip()
        clock.tick(30)


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
    title_font = pygame.font.SysFont("arial", 26, bold=True)

    window_size = INITIAL_WINDOW_SIZE
    menu_result = run_menu(screen, window_size, title_font, button_font)
    if menu_result is None:
        pygame.quit()
        sys.exit()
    screen, window_size, word_list_path = menu_result

    session = GameSession(WordList(word_list_path), HighScore(HIGH_SCORE_PATH))
    board = Board()

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
                # See the comment in run_menu(): don't call
                # set_mode() again here, just pick up the surface
                # SDL already resized in response to the window
                # manager's resize.
                window_size = (event.w, event.h)
                screen = pygame.display.get_surface()
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
