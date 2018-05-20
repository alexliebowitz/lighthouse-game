import random

import pygame

from constants import *
from sprites.gamesprite import GameSprite
from utils import normalize


class GhostSprite(GameSprite):
    """ Simple class that allows us to display an image with alpha
        transparency (i.e., faded out). Mainly useful for creating
        trail effects. """

    def __init__(self, image, coords):
        super().__init__()

        self.image = image
        self.rect = pygame.rect.Rect(coords, image.get_size())

    def draw(self, alpha):
        # Pygame can't blit images to the screen with a "faded" look (transparent)
        # if the image itself already contains transparency. So to get the "fade"
        # effect we want, we need to blit the image to a temporary surface, then
        # blit the temporary surface to the screen.
        # (Solution from here: https://stackoverflow.com/a/12880257)

        # Make temporary surface. Like all surfaces, it will be filled with
        # black to start with.
        tempsurf = pygame.Surface((self.rect.width, self.rect.height))

        # Set color key to black on the temporary surface, so that black shows
        # up as transparent. Note: because we only have one color that is
        # transparent (black), we can't get gradual/partial alpha in the
        # image itself. So around the edges it will look "dirty" (no
        # anti-aliasing). But because the image is faded anyway, it's not really
        # noticeable.
        tempsurf.set_colorkey((0, 0, 0))

        # Blit the image onto the temporary surface
        tempsurf.blit(self.image, (0, 0))

        # Set the transparency on the temporary surface
        tempsurf.set_alpha(alpha)

        # Blit the temporary surface to the screen
        self._mainsurf.blit(tempsurf, self.rect)


class Rocket(GameSprite):
    _frames = None
    _trail = None
    _booston = None
    _boostmode = None
    _angle = None
    _speedincr = None
    _speedx = None
    _speedy = None

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("images/rocket.png")

        self._frames = 0
        self._speedincr = DEFAULT_SPEED_INCR
        self.boostmode = False
        self._speedx = 0
        self._speedy = 0

        # self._trail is used to draw the trail that goes behind the rocket.
        # It's a list containing sprites that are snapshots of the rocket's
        # position and apperance at that moment in time.

        self._trail = []

        self._angle = 0  # Start off pointing upward

        self.rect = pygame.rect.Rect((WIDTH / 2, HEIGHT / 2), self.image.get_size())
        self.setx(WIDTH / 2)
        self.sety(HEIGHT / 2)

    def booston(self):
        self.boostmode = True
        self._speedincr = BOOST_SPEED_INCR

    def boostoff(self):
        self.boostmode = False
        self._speedincr = DEFAULT_SPEED_INCR

    def setspeedx(self, speedx):
        self._speedx = speedx

    def setspeedy(self, speedy):
        self._speedy = speedy

    def incrspeedx(self):
        self._speedx += self._speedincr

    def incrspeedy(self):
        self._speedy += self._speedincr

    def decrspeedx(self):
        self._speedx -= self._speedincr

    def decrspeedy(self):
        self._speedy -= self._speedincr

    def draw(self):
        self._frames += 1

        self._speedx *= FRICTION
        self._speedy *= FRICTION
        self.incrx(self._speedx)
        self.incry(self._speedy)


        if self._speedx != 0 or self._speedy != 0:
            # We're moving, so we need to update self._angle to match
            # the direction we're moving.
            rotvec = pygame.math.Vector2((self._speedx, self._speedy))
            _, raw_angle = rotvec.as_polar()

            # as_polar() gives us an "azimuthal angle" (whatever that means).
            # For mysterious reasons, we need to add 90 degrees and flip
            # the sign to get a regular angle.
            self._angle = 0 - (raw_angle + 90)


        rotatedimage = pygame.transform.rotate(self.image, self._angle)

        # When we called pygame.transform.rotate(), that gave us a new surface
        # enlarged to contain the rotated image. This means if we tried to blit
        # the image with self.rect, it would be slightly off center. Instead we
        # create a temporary rectangle object from the rotated image, and
        # re-center it on the center of the rocket.

        draw_rect = rotatedimage.get_rect()
        draw_rect.centerx = self.rect.centerx
        draw_rect.centery = self.rect.centery


        # Now draw_rect contains the correct position info, so we
        # blit the rotated image at that position.
        self._mainsurf.blit(rotatedimage, draw_rect)


        # Add a new sprite at the beginning of the trail
        if self._frames % ROCKET_TRAIL_SPACING == 0:
            self._trail.insert(0, GhostSprite(rotatedimage, (draw_rect.x, draw_rect.y)))

        # If the trail is now too long, chop off one at the end
        if len(self._trail) > ROCKET_MAX_TRAIL:
            self._trail = self._trail[:-1]

        # Draw trail
        alpha = ROCKET_TRAIL_START_ALPHA
        for trailsprite in self._trail:
            alpha *= ROCKET_TRAIL_FADE

            trailsprite.draw(alpha)


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

        self.image = pygame.image.load("images/boss.png")
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
    _rotate_angle = 0

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

        rotatedimage = pygame.transform.rotate(self.image, self._rotate_angle)
        self._rotate_angle += FIREBALL_SPIN_SPEED

        self._mainsurf.blit(rotatedimage, self.rect)
