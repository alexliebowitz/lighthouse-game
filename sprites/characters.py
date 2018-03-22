import pygame
import random

from sprites.gamesprite import GameSprite

from constants import *
from utils import *

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
    _rocket = None

    def __init__(self, rocket):
        super().__init__()

        self.image = pygame.image.load("images/devil.png")
        self._rocket = rocket

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
        self.setx(x)
        self.sety(y)

    def draw(self):
        self._mainsurf.blit(self.image, self.rect)


class BossDevil(Devil):
    _fireballs = None

    def __init__(self, rocket):
        super().__init__(rocket)

        self._normalimage = pygame.image.load("images/boss.png")
        self._invertedimage = pygame.image.load("images/boss2.png")

        self._framecounter = 0
        self._inverted = False

        self._fireballs = pygame.sprite.Group()

        self.image = pygame.image.load('images/boss.png')
        self.rect = pygame.rect.Rect((0, 0), self.image.get_size())
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.setx(self.rect.x)
        self.sety(self.rect.y)

    def colliding(self, othersprite):
        return (pygame.sprite.collide_rect(self, othersprite)
                or pygame.sprite.spritecollideany(self._rocket, self._fireballs))

    def draw(self):
        self._framecounter += 1

        if self._framecounter % 5 == 0:
            self._inverted = not self._inverted

        if self._inverted:
            self.image = self._invertedimage
        else:
            self.image = self._normalimage

        if self._framecounter % FIREBALL_INTERVAL == 0:
            dx = self._rocket.rect.centerx - self.rect.centerx
            dy = self._rocket.rect.centery - self.rect.centery
            bearingx, bearingy = normalize(dx, dy)

            newfireball = Fireball((self.rect.centerx, self.rect.centery), (bearingx, bearingy))
            self._fireballs.add(newfireball)

        for fireball in self._fireballs:
            fireball.draw()

        self._mainsurf.blit(self.image, self.rect)

class Fireball(GameSprite):
    _bearingx = None
    _bearingy = None

    def __init__(self, startcoords, bearing):
        super().__init__()
        self.image = pygame.image.load("images/fireball.png")

        self.rect = pygame.rect.Rect(startcoords, self.image.get_size())

        self._bearingx, self._bearingy = bearing
        startx, starty = startcoords
        self.setx(startx)
        self.sety(starty)

    def draw(self):
        self.incrx(self._bearingx * FIREBALL_SPEED)
        self.incry(self._bearingy * FIREBALL_SPEED)

        self._mainsurf.blit(self.image, self.rect)
