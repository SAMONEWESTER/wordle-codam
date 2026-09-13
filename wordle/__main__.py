"""Entry point: wires pygame input and rendering to the game logic.

Run with `python -m wordle` (the Makefile does this for you inside
the project's .venv).
"""

import sys
from dataclasses import dataclass

import pygame

from wordle.game import LOST, PLAYING, WON, GameSession, HighScore, WordList
from wordle.visuals import Board, Button

FPS_COUNT = 60

INITIAL_WINDOW_SIZE = (420, 620)
BACKGROUND_COLOR = (18, 18, 19)
MESSAGE_COLOR = (220, 60, 60)
HEADER_TEXT_COLOR = (255, 255, 255)

HIGH_SCORE_PATH = "highscore.json"

# Word lists the player can choose from before a game starts. Each
# entry is (button label, path to the word file).
WORD_LIST_OPTIONS = [
    ("Shitty word list", "words.txt"),
    ("Great amazing word list", "words2.txt"),
]

# Every size in the UI is a multiple of one of these base numbers,
# measured against INITIAL_WINDOW_SIZE. Resizing the window computes
# one scale factor and every element (fonts, buttons, margins, the
# board's own square size) grows or shrinks together from it, so the
# whole UI stays in proportion instead of only the board resizing.
BASE_TOP_MARGIN = 90
BASE_BUTTON_SIZE = (120, 44)
BASE_BUTTON_GAP = 20
BASE_BUTTON_TOP_GAP = 30
BASE_BUTTON_BOTTOM_PADDING = 20
BASE_SIDE_PADDING = 10
BASE_MAX_SQUARE_SIZE = 90

BASE_HEADER_FONT_SIZE = 18
BASE_BUTTON_FONT_SIZE = 20
BASE_TITLE_FONT_SIZE = 26
BASE_HEADER_LINE_1_Y = 30
BASE_HEADER_LINE_2_Y = 60

BASE_MENU_BUTTON_HEIGHT = 54
BASE_MENU_BUTTON_GAP = 24
BASE_MENU_BUTTON_PADDING_X = 36
BASE_MENU_TITLE_TOP = 90

# How far the UI is allowed to scale down or up. Keeps text and
# buttons from shrinking into illegibility on a tiny window, or
# ballooning absurdly on a huge one.
MIN_SCALE = 0.6
MAX_SCALE = 2.5


@dataclass(frozen=True)
class Metrics:
    """All the scaled sizes the UI needs for one window size."""

    scale: float
    top_margin: int
    bottom_margin: int
    button_size: tuple[int, int]
    button_gap: int
    button_top_gap: int
    side_padding: int
    max_square_size: int
    header_font_size: int
    button_font_size: int
    title_font_size: int
    header_line_1_y: int
    header_line_2_y: int
    menu_button_height: int
    menu_button_gap: int
    menu_button_padding_x: int
    menu_title_top: int


@dataclass(frozen=True)
class Fonts:
    header: pygame.font.Font
    button: pygame.font.Font
    title: pygame.font.Font


def compute_scale(window_size: tuple[int, int]) -> float:
    """One factor describing how much bigger/smaller than the
    starting window this window is, clamped to a sane range."""
    width, height = window_size
    base_width, base_height = INITIAL_WINDOW_SIZE
    scale = min(width / base_width, height / base_height)
    return max(MIN_SCALE, min(MAX_SCALE, scale))


def build_metrics(window_size: tuple[int, int]) -> Metrics:
    scale = compute_scale(window_size)

    def s(value: float) -> int:
        return max(1, round(value * scale))

    button_size = (s(BASE_BUTTON_SIZE[0]), s(BASE_BUTTON_SIZE[1]))
    button_top_gap = s(BASE_BUTTON_TOP_GAP)
    bottom_margin = (
        button_top_gap + button_size[1] + s(BASE_BUTTON_BOTTOM_PADDING)
    )

    return Metrics(
        scale=scale,
        top_margin=s(BASE_TOP_MARGIN),
        bottom_margin=bottom_margin,
        button_size=button_size,
        button_gap=s(BASE_BUTTON_GAP),
        button_top_gap=button_top_gap,
        side_padding=s(BASE_SIDE_PADDING),
        max_square_size=s(BASE_MAX_SQUARE_SIZE),
        header_font_size=s(BASE_HEADER_FONT_SIZE),
        button_font_size=s(BASE_BUTTON_FONT_SIZE),
        title_font_size=s(BASE_TITLE_FONT_SIZE),
        header_line_1_y=s(BASE_HEADER_LINE_1_Y),
        header_line_2_y=s(BASE_HEADER_LINE_2_Y),
        menu_button_height=s(BASE_MENU_BUTTON_HEIGHT),
        menu_button_gap=s(BASE_MENU_BUTTON_GAP),
        menu_button_padding_x=s(BASE_MENU_BUTTON_PADDING_X),
        menu_title_top=s(BASE_MENU_TITLE_TOP),
    )


def build_fonts(metrics: Metrics) -> Fonts:
    return Fonts(
        header=pygame.font.SysFont("arial", metrics.header_font_size),
        button=pygame.font.SysFont(
            "arial", metrics.button_font_size, bold=True
        ),
        title=pygame.font.SysFont(
            "arial", metrics.title_font_size, bold=True
        ),
    )


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
    window_size: tuple[int, int], board_bottom: int, metrics: Metrics
) -> tuple[Button, Button]:
    width, _ = window_size
    button_width, button_height = metrics.button_size
    gap = metrics.button_gap
    side_padding = metrics.side_padding
    total_width = button_width * 2 + gap
    left = (width - total_width) // 2
    left = max(side_padding, min(left, width - total_width - side_padding))
    top = board_bottom + metrics.button_top_gap

    retry_rect = pygame.Rect(left, top, button_width, button_height)
    quit_rect = pygame.Rect(
        left + button_width + gap, top, button_width, button_height
    )
    return Button(retry_rect, "Retry"), Button(quit_rect, "Quit")


def build_menu_buttons(
    window_size: tuple[int, int], font: pygame.font.Font, metrics: Metrics
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
    button_width = max_text_width + metrics.menu_button_padding_x * 2
    button_width = min(button_width, width - metrics.side_padding * 2)
    left = (width - button_width) // 2

    button_height = metrics.menu_button_height
    button_gap = metrics.menu_button_gap
    title_top = metrics.menu_title_top
    option_count = len(WORD_LIST_OPTIONS)
    total_height = (
        button_height * option_count + button_gap * (option_count - 1)
    )
    top = title_top + ((height - title_top) - total_height) // 2

    buttons = []
    for index, (label, path) in enumerate(WORD_LIST_OPTIONS):
        y = top + index * (button_height + button_gap)
        rect = pygame.Rect(left, y, button_width, button_height)
        buttons.append((Button(rect, label), path))
    return buttons


def draw_menu(
    surface: pygame.Surface,
    fonts: Fonts,
    window_width: int,
    metrics: Metrics,
    buttons: list[tuple[Button, str]],
) -> None:
    title = fonts.title.render("Choose a word list", True, HEADER_TEXT_COLOR)
    surface.blit(
        title,
        title.get_rect(center=(window_width // 2, metrics.menu_title_top)),
    )
    for button, _ in buttons:
        button.draw(surface, fonts.button)


def run_menu(
    screen: pygame.Surface,
    window_size: tuple[int, int],
    metrics: Metrics,
    fonts: Fonts,
) -> tuple[pygame.Surface, tuple[int, int], Metrics, Fonts, str] | None:
    """Show the word list picker until the player chooses or quits.

    Returns the (possibly resized) screen, window size, metrics,
    fonts, and the chosen word list path, or None if the player quit.
    """
    clock = pygame.time.Clock()
    buttons = build_menu_buttons(window_size, fonts.button, metrics)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            elif event.type == pygame.VIDEORESIZE:
                window_size = (event.w, event.h)
                screen = pygame.display.get_surface()
                metrics = build_metrics(window_size)
                fonts = build_fonts(metrics)
                buttons = build_menu_buttons(
                    window_size, fonts.button, metrics
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, path in buttons:
                    if button.is_clicked(event.pos):
                        return screen, window_size, metrics, fonts, path

        screen.fill(BACKGROUND_COLOR)
        draw_menu(screen, fonts, window_size[0], metrics, buttons)
        pygame.display.flip()
        clock.tick(30)


def draw_header(
    surface: pygame.Surface,
    font: pygame.font.Font,
    session: GameSession,
    window_width: int,
    metrics: Metrics,
) -> None:
    best = session.high_score.value
    streak_text = f"Streak: {session.streak}   Best: {best}"
    text = font.render(streak_text, True, HEADER_TEXT_COLOR)
    center = (window_width // 2, metrics.header_line_1_y)
    surface.blit(text, text.get_rect(center=center))

    status_text = session.game.message or end_of_game_text(session)
    color = MESSAGE_COLOR if session.game.message else HEADER_TEXT_COLOR
    if status_text:
        status = font.render(status_text, True, color)
        center = (window_width // 2, metrics.header_line_2_y)
        surface.blit(status, status.get_rect(center=center))


def build_letter_font(square_size: int) -> pygame.font.Font:
    return pygame.font.SysFont("arial", int(square_size * 0.5), bold=True)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(INITIAL_WINDOW_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Wordle")
    clock = pygame.time.Clock()

    window_size = INITIAL_WINDOW_SIZE
    metrics = build_metrics(window_size)
    fonts = build_fonts(metrics)

    menu_result = run_menu(screen, window_size, metrics, fonts)
    if menu_result is None:
        pygame.quit()
        sys.exit()
    screen, window_size, metrics, fonts, word_list_path = menu_result

    session = GameSession(WordList(word_list_path), HighScore(HIGH_SCORE_PATH))
    board = Board()

    board.layout(
        window_size,
        metrics.top_margin,
        metrics.bottom_margin,
        metrics.max_square_size,
    )
    retry_button, quit_button = build_buttons(
        window_size, board.bottom, metrics
    )

    letter_font_size = board.square_size
    letter_font = build_letter_font(letter_font_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_size = (event.w, event.h)
                screen = pygame.display.get_surface()
                metrics = build_metrics(window_size)
                fonts = build_fonts(metrics)
                board.layout(
                    window_size,
                    metrics.top_margin,
                    metrics.bottom_margin,
                    metrics.max_square_size,
                )
                retry_button, quit_button = build_buttons(
                    window_size, board.bottom, metrics
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
        draw_header(screen, fonts.header, session, window_size[0], metrics)

        if session.status != PLAYING:
            retry_button.draw(screen, fonts.button)
            quit_button.draw(screen, fonts.button)

        pygame.display.flip()
        clock.tick(FPS_COUNT)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
