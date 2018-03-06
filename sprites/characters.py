import pygame
import random

from .gamesprite import GameSprite

from constants import *

class Rocket(GameSprite):
    _frames = None
    _trail = None

    def __init__(self):
        super().__init__()

        self._frames = 0
        self._trail = []

        self.image = pygame.image.load("images/rocket.png")

        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.x = self.rect.x
        self.y = self.rect.y

    def draw_trail_rocket(self, coords, alpha):
        tempsurf = pygame.Surface((WIDTH, HEIGHT))
        tempsurf.set_colorkey((0, 0, 0))
        tempsurf.blit(self.image, (0, 0))
        tempsurf.set_alpha(alpha)

        self._mainsurf.blit(tempsurf, coords)

    def draw(self):
        self._frames += 1

        # Compute new trail and blit it
        if self._frames % ROCKET_TRAIL_SPACING == 0:
            self._trail.insert(0, (self.rect.x, self.rect.y))

        if len(self._trail) > ROCKET_MAX_TRAIL:
            self._trail = self._trail[:-1]


        alpha = ROCKET_TRAIL_START_ALPHA
        for trailcoord in self._trail:
            alpha *= ROCKET_TRAIL_FADE

            self.draw_trail_rocket(trailcoord, alpha)

        # Blit rocket

        self._mainsurf.blit(self.image, self.rect)


class Devil(GameSprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/devil.png")

        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.randint(0, WIDTH)
            y = 0
        elif side == 1:  # Right
            x = WIDTH
            y = random.randint(0, HEIGHT)
        elif side == 2:  # Bottom
            x = random.randint(0, WIDTH)
            y = HEIGHT
        elif side == 3:  # Left
            x = 0
            y = random.randint(0, HEIGHT)

        self.rect = pygame.rect.Rect((x, y), self.image.get_size())

    def draw(self):
        self._mainsurf.blit(self.image, self.rect)


class BossDevil(Devil):
    def __init__(self):
        super().__init__()

        self._normalimage = pygame.image.load("images/boss.png")
        self._invertedimage = pygame.image.load("images/boss2.png")

        self._framecounter = 0
        self._inverted = False

        self.image = pygame.image.load('images/boss.png')
        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def draw(self):
        self._framecounter += 1

        if self._framecounter == 5:
            self._framecounter = 0
            self._inverted = not self._inverted
            if self._inverted:
                self.image = self._invertedimage
            else:
                self.image = self._normalimage

        self._mainsurf.blit(self.image, self.rect)
