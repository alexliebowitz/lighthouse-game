import random

import pygame

from constants import *
from sprites.gamesprite import GameSprite


class Item(GameSprite):
    IMAGE_FILE = None

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/" + self.IMAGE_FILE)
        self.rect = pygame.rect.Rect((random.randint(15, WIDTH - 15), random.randint(15, HEIGHT - 15)), self.image.get_size())


    def draw(self):
        self._mainsurf.blit(self.image, self.rect)


class Cookie(Item):
    IMAGE_FILE = "cookie.png"


class Powerup(Item):
    SOUND_FILE = "powerup.wav"
    NAME = None
    BLINK_RATE = 3

    state = None
    _sound = None
    _frames = None
    _blinker = None

    def __init__(self):
        super().__init__()

        self._sound = pygame.mixer.Sound("sounds/" + self.SOUND_FILE)
        self.state = 'notdropped'
        self._frames = 0
        self._blinker = 0

    def drop(self):
        self.state = 'onscreen'

    def collect(self):
        self.state = 'collected'
        self._sound.play()

    def draw(self):
        self._frames += 1

        if self._frames <= 30:
            if self._frames % self.BLINK_RATE == 0:
                self._blinker = not self._blinker

            if self._blinker:
                self._mainsurf.blit(self.image, self.rect)
        else:
            self._mainsurf.blit(self.image, self.rect)


class BombPowerup(Powerup):
    IMAGE_FILE = "bomb_powerup.png"
    NAME = 'bomb'


class ShieldPowerup(Powerup):
    IMAGE_FILE = "shield_powerup.png"
    NAME = 'shield'


class TimeBombPowerup(Powerup):
    IMAGE_FILE = "time_bomb_powerup.png"
    NAME = 'timebomb'
