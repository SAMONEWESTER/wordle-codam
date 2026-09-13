"""A small clickable rectangle with a label. Visuals only, no logic."""

import pygame

FILL_COLOR = (58, 58, 60)
HOVER_COLOR = (86, 87, 88)
BORDER_COLOR = (129, 131, 132)
TEXT_COLOR = (255, 255, 255)
BORDER_WIDTH = 2
BORDER_RADIUS = 8


class Button:
    """Draws itself and reports whether a click landed inside it."""

    def __init__(self, rect: pygame.Rect, label: str):
        self.rect = rect
        self.label = label

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = HOVER_COLOR if hovered else FILL_COLOR
        pygame.draw.rect(
            surface, color, self.rect, border_radius=BORDER_RADIUS
        )
        pygame.draw.rect(
            surface,
            BORDER_COLOR,
            self.rect,
            BORDER_WIDTH,
            border_radius=BORDER_RADIUS,
        )
        text = font.render(self.label, True, TEXT_COLOR)
        surface.blit(text, text.get_rect(center=self.rect.center))
