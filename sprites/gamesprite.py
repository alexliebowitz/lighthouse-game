import math

import pygame

import constants


class GameSprite(pygame.sprite.Sprite):
    _mainsurf = None
    x = None
    y = None

    def __init__(self):
        super().__init__()
        self._mainsurf = pygame.display.get_surface()

    def movetoward(self, target, amount):
        # Moves this sprite toward another sprite by the given amount
        # in a straight line.

        # Get the difference between this sprite and the target
        # along the x and y axis. We can also think about this
        # as a vector.
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery

        # Convert the x axis difference and y axis difference
        # to an overall distance, using the Pythagorean theorem.
        distance = math.sqrt(dx**2 + dy**2)

        # Now, we don't actually care about the original distance—
        # we just care about the angle. So we want to make a vector
        # where the *angle* is the same, but the *length* is 1. That
        # makes it a lot easier to deal with.

        # To achieve this, we divide each component by the length. Essentially,
        # for both x and y, we're saying "scale yourself down so that the
        # total length is 1 instead of the original distance."

        # This is called "normalizing" the vector.

        if distance == 0:
            # Don't want to divide by 0
            dx_normalized = dy_normalized = 0
        else:
            dx_normalized = dx / distance
            dy_normalized = dy / distance

        # To get the final result, multiply the normalized x and y difference
        # by the distance we want to move

        move_dx = dx_normalized * amount
        move_dy = dy_normalized * amount

        self.incrx(move_dx)
        self.incry(move_dy)

    def colliding(self, othersprite):
        # This function is used to ask a sprite if it's colliding with another one.
        # You can override this when you need custom collision detection, because your
        # sprite is an unusual shape or it has "slave" sprites

        return pygame.sprite.collide_rect(self, othersprite)

    def setx(self, x):
        self.x = x
        self.rect.x = x

    def sety(self, y):
        self.y = y
        self.rect.y = y

    def incrx(self, amount):
        self.x += amount
        self.rect.x = self.x

    def incry(self, amount):
        self.y += amount
        self.rect.y = self.y
