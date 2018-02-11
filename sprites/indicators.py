import pygame

from constants import *
from .gamesprite import GameSprite

class LevelIndicator(GameSprite):
    _level = None
    _font = None

    def __init__(self, level):
        super().__init__()

        self._level = level
        self._font = pygame.font.SysFont(MAIN_FONT, MAIN_FONT_SIZE)

    def setlevel(self, level):
        self._level = level

    def draw(self):
        textsurf = self._font.render(str(self._level), True, MAIN_COLOR)
        self._mainsurf.blit(textsurf, (WIDTH - 50, 50))

class BoostBar(GameSprite):
    _boostleft = None

    def __init__(self, boostleft):
        super().__init__()

        self._boostleft = boostleft

    def setboost(self, boostleft):
        self._boostleft = boostleft

    def draw(self):
        width = (self._boostleft / MAX_BOOST) * BOOST_BAR_WIDTH

        if self._boostleft < MIN_BOOST:
            color = BOOST_BAR_COLOR_DEPLETED
        else:
            color = BOOST_BAR_COLOR

        # The x position of the bar is the width of the screen, minus the width of the bar
        # (so it doesn't go off the screen), minus another 30px so it's not right up
        # against the edge of the screen.
        barx = WIDTH - BOOST_BAR_WIDTH - 30

        # y position is 20px (just a little bit of padding so it's not right at the top)
        bary = 20

        # The width of the bar is the percentage of boost that we have left, times the width
        # of the full bar. So if we're at 50% boost and the full bar is 150 pixels, then
        # we display a bar 75 pixels wide.
        barwidth = (self._boostleft / MAX_BOOST) * BOOST_BAR_WIDTH

        # The height is just a constant
        barheight = BOOST_BAR_HEIGHT

        # Time to draw the bar!
        pygame.draw.rect(self._mainsurf, color, (barx, bary, barwidth, barheight))

        # Now, let's make the line that marks the minimum boost level

        # To compute the x position for the minimum boost line, we take 3 steps:
        #   - First, we divide the minimum boost over the maximum boost, to find out
        #     how far along the bar we should draw the line (as a ratio). For example,
        #     if MIN_BOOST is 20 and MAX_BOOST is 100, then the ratio would be 0.2.
        #   - Next, we multiply this ratio by the width of the bar to get the actual
        #     number of pixels.
        #   - Finally, we add the x position of the bar to push the whole thing to the
        #     right so it lines up with the bar.
        linex = ((MIN_BOOST / MAX_BOOST) * BOOST_BAR_WIDTH) + barx

        # Line y position is the same as bar
        liney = bary

        # Line is 2 pixels wide
        linewidth = 2

        # Line is same height as bar
        lineheight = barheight

        pygame.draw.rect(self._mainsurf, BOOST_BAR_LINE_COLOR, (linex, liney, linewidth, lineheight))
