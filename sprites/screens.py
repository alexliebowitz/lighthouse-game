import pygame

from .gamesprite import GameSprite
from constants import *

class Screen(GameSprite):
    BACKDROP_COLOR = None
    BACKDROP_ALPHA = 60
    CONTENT_COLOR = None

    _font = None
    _snapshot = None
    _backdrop = None
    _content = None

    def __init__(self):
        super().__init__()

        self._font = pygame.font.SysFont(MAIN_FONT, MAIN_FONT_SIZE)

        self.image = pygame.Surface((WIDTH, HEIGHT))

        self._snapshot = self._mainsurf.copy()

        self._backdrop = pygame.Surface((WIDTH, HEIGHT))
        self._backdrop.fill(self.BACKDROP_COLOR)
        self._backdrop.set_alpha(self.BACKDROP_ALPHA)

        self._content = pygame.Surface((WIDTH, HEIGHT))
        self._content.set_colorkey((0, 0, 0))

    def draw(self):
        self.image.blit(self._snapshot, (0, 0))
        self.image.blit(self._backdrop, (0, 0))
        self.image.blit(self._content, (0, 0))
        self._mainsurf.blit(self.image, (0, 0))

class WinScreen(Screen):
    BACKDROP_COLOR = (255, 255, 255)
    BACKDROP_ALPHA = 255
    CONTENT_COLOR = (0, 100, 0)

    def draw(self):
        textsurf = self._font.render('YOU WON', True, self.CONTENT_COLOR)
        textrect = textsurf.get_rect(center=self._mainsurf.get_rect().center)

        self._content.blit(textsurf, textrect)
        super().draw()

class LoseScreen(Screen):
    BACKDROP_COLOR = (150, 0, 0)
    CONTENT_COLOR = (230, 230, 230)

    def draw(self):
        textsurf = self._font.render("YOU LOST", True, self.CONTENT_COLOR)
        textrect = textsurf.get_rect(center=self._mainsurf.get_rect().center)

        self._content.blit(textsurf, textrect)
        super().draw()

class PauseScreen(Screen):
    BACKDROP_COLOR = (252, 254, 234)
    CONTENT_COLOR = (0, 0, 0)

    def draw(self):
        textsurf = self._font.render("GAME PAUSED", True, self.CONTENT_COLOR)
        textrect = textsurf.get_rect(center=self._mainsurf.get_rect().center)

        self._content.blit(textsurf, textrect)
        super().draw()