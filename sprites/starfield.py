import random

import pygame

from sprites.gamesprite import GameSprite
from constants import *


class StarField(GameSprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())

        y = 0
        while y < HEIGHT:
            x = 0
            while x < WIDTH:
                if random.randint(0, 100) == 0:
                    startype = random.choice(['white', 'red', 'blue'])
                    if startype == 'white':
                        color = (255, 255, 255)
                    elif startype == 'red':
                        color = (random.randint(150, 255), 50, 50)
                    elif startype == 'blue':
                        color = (50, 50, random.randint(150, 255))

                    self.image.set_at((x, y), color)
                x += 1
            y += 1

    def draw(self):
        self._mainsurf.blit(self.image, self.rect)
