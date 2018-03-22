import pygame
import math
import random

from constants import *

from pygame.locals import *
from sprites.indicators import *
from sprites.screens import *
from sprites.gamesprite import *
from sprites.items import BombPowerup, TimeBombPowerup, ShieldPowerup, Cookie
from sprites.starfield import StarField
from sprites.abilities import *
from sprites.characters import *
from utils import *


pygame.init()
pygame.mixer.init()
 
mainfont = pygame.font.SysFont('Helvetica', 25)

mainsurf = pygame.display.set_mode((WIDTH, HEIGHT))

rocketspeedx = 0
rocketspeedy = 0
rocketspeed = 0
rocketspeedincr = DEFAULT_SPEED_INCR

boostmode = False
boostleft = MAX_BOOST

devils = []
bombs = []
timebomb = None

level = 1

paused = False
gamewon = False
gamelost = False

devilgroup = pygame.sprite.Group()

winsound = pygame.mixer.Sound("sounds/winscreen.wav")
losesound = pygame.mixer.Sound("sounds/sadtrombone.wav")
levelupsound = pygame.mixer.Sound("sounds/omnomnom.ogg")

losescreen = None
winscreen = None
pausescreen = None

levelindicator = LevelIndicator(level)
boostbar = BoostBar(boostleft)

powerups = {
    'bomb': BombPowerup(),
    'shield': ShieldPowerup(),
    'timebomb': TimeBombPowerup()
}
starfield = StarField()

rocket = Rocket()
cookie = Cookie()
shield = None

# Create first devil

firstdevil = Devil(rocket)
devils.append(firstdevil)
devilgroup.add(firstdevil)

while True:
    event = pygame.event.poll()     
 
    if event.type == QUIT:
        exit()
 
    if gamewon:
        if winscreen is None:
            winscreen = WinScreen()
        winscreen.draw()
        pygame.display.update()
        continue
 
    if gamelost:
        if losescreen is None:
            losescreen = LoseScreen()
        losescreen.draw()
        pygame.display.update()
        continue

    if event.type == KEYUP and event.key == K_ESCAPE:  # If the player just pressed escape...
        paused = not paused  # Flip paused state
        if paused:
            pausescreen = PauseScreen()
        else:
            pausescreen = None

    # If the game is paused, display the pause screen and skip everything else
    if paused:
        pausescreen.draw()
        pygame.display.update()
        continue

    keyspressed = pygame.key.get_pressed()

    ### Update rocket speed

    # If the player pressed "b" and we have enough boost to start, then go into boost mode
    if event.type == KEYDOWN and event.key == K_b and boostleft > MIN_BOOST:
        boostmode = True
        rocketspeedincr = BOOST_SPEED_INCR

    if event.type == KEYUP and event.key == K_b:  # Boost mode over
        boostmode = False
        rocketspeedincr = DEFAULT_SPEED_INCR

    if boostmode:
        # We're in boost mode

        boostleft -= 1  # Deplete the boost counter
        if boostleft <= 0:
            boostmode = False
            rocketspeedincr = DEFAULT_SPEED_INCR
    else:
        # We're not in boost mode

        # Replenish boost counter
        if boostleft <= MAX_BOOST:
            boostleft += 0.25
            boostbar.setboost(boostleft)

    ### Update rocket position using the speed we just calculated

    if keyspressed[K_UP]:
        rocketspeedy -= rocketspeedincr
 
    if keyspressed[K_DOWN]:
        rocketspeedy += rocketspeedincr
 
    if keyspressed[K_LEFT]:
        rocketspeedx -= rocketspeedincr
 
    if keyspressed[K_RIGHT]:
        rocketspeedx += rocketspeedincr

    # If the rocket is now past the edge in any direction, move it back to the edge.
    if rocket.rect.x < 0:
        rocket.setx(0)

    if rocket.rect.x > WIDTH - rocket.rect.width:
        rocket.setx(WIDTH - rocket.rect.width)

    if rocket.rect.y < 0:
        rocket.sety(0)

    if rocket.rect.y > HEIGHT - rocket.rect.height:
        rocket.sety(HEIGHT - rocket.rect.height)
    

    ### Update devil positions

    for devil in devils: # For each devil...
        # If there is a time bomb and it's exploding, we ask it for a time
        # scale to find out how much to slow down the world.
        if timebomb is not None and timebomb.exploding:
            timescale = timebomb.get_time_scale()
        else:
            timescale = 1

        devil.movetoward(rocket, DEVILSPEED * timescale)

        devilgroup.remove(devil)
        collidingdevil = pygame.sprite.spritecollideany(devil, devilgroup)
        devilgroup.add(devil)


        if collidingdevil is not None:
            rd = randomdirection()
            dirx = rd[0]
            diry = rd[1]

            devil.rect.x += dirx
            devil.rect.y += diry

    if event.type == KEYDOWN and event.key == K_d:
        for bomb in bombs:
            bomb.detonate()

    # For each of the powerup objects...
    for powerup in powerups.values():
        # If we are colliding with this powerup and it hasn't been
        # collected already, collect it.
        if rocket.rect.colliderect(powerup.rect) and powerup.state == 'onscreen':
            powerup.collect()

    ### We have the new positions for everything. Now, check for collisions and update the game in response

    # Check if the rocket is colliding with any of the devils. If so, we lost
    i = 0
    while i < len(devils):
        devil = devils[i]

        if devil.colliding(rocket):
            gamelost = True
            break
        i += 1

    if gamelost:
        losesound.play()
        continue

    # Check for collisions with bombs.
    for bomb in bombs:
        if bomb.exploding and pygame.sprite.collide_circle(bomb, rocket):
            # If the rocket is colliding with an exploding bomb, we lose
            gamelost = True
            continue

        for devil in list(devils):
            # If a devil is colliding with an exploding bomb, it goes bye-bye
            if bomb.exploding and pygame.sprite.collide_circle(bomb, devil):
                devils.remove(devil)
                devilgroup.remove(devil)

    if event.type == KEYDOWN and event.key == K_d:
        for bomb in bombs:
            bomb.detonate()


    if gamelost:
        losesound.play()
        continue

    rocket.incrx(rocketspeedx)
    rocket.incry(rocketspeedy)
 
    # Check if the rocket is colliding with the cookie
    if rocket.rect.colliderect(cookie.rect):
        # Time to level up!
        level += 1
        levelindicator.setlevel(level)

        if level > MAX_POINTS:  # We won
            gamewon = True
            winsound.play()
            continue
        else:
            cookie = Cookie()
            if level == MAX_POINTS:  # Final level
                devilgroup.empty()
                devils = [BossDevil(rocket)]
            else:
                for i in range(level):
                    newdevil = Devil(rocket)
                    devilgroup.add(newdevil)
                    devils.append(newdevil)
            levelupsound.play()

            # If there's a powerup for this level, drop it.
            if level in LEVEL_TO_POWERUP: 
                # There is a powerup in the table for this level.
                # So get the powerup's name
                powerupname = LEVEL_TO_POWERUP[level]

                # Now, look up the actual powerup object and tell it to drop
                powerups[powerupname].drop()

    if event.type == KEYUP and event.key == K_RETURN and powerups['bomb'].state == 'collected':  # Drop a bomb
        bombs.append(Bomb(rocket.rect.x, rocket.rect.y))

    # Clear out bombs that have finished detonating
    for bomb in list(bombs):
        if bomb.done:
            bombs.remove(bomb)

    if (event.type == KEYDOWN and event.key == K_t and timebomb is None
        and powerups['timebomb'].state == 'collected'):
        timebomb = TimeBomb(rocket.rect.x, rocket.rect.y)

    if timebomb is not None and timebomb.done:
        timebomb = None

    if shield is not None:
        if shield.done:
            shield = None
        else:
            for devil in devils:
                if pygame.sprite.collide_circle(devil, shield):
                    # OK, we need to move the devil outward past the edge of the shield.
   
                    # Get the difference between this devil and the center of the shield along
                    # the x and y axes. You can also think of this as a vector of the two numbers
                    # "dx" and "dy"
                    dx = devil.rect.centerx - rocket.rect.centerx
                    dy = devil.rect.centery - rocket.rect.centery

                    # Convert the difference along the x and y axis to a distance
                    # (You can also think of this as the length of a vector)
                    len_xy = math.sqrt(dx**2 + dy**2)


                    # Divide each component of the vector by the length so it is "normalized"
                    # to a vector with a length between 0 and 1
                    if len_xy == 0:
                        # Don't want to divide by zero
                        dx_normalized = dy_normalized = 0
                    else:
                        dx_normalized = dx / len_xy
                        dy_normalized = dy / len_xy

                    # We will push the devil out just enough to get it to the edge --
                    # we start with the radius of the shield, then subtract the distance
                    # of the devil from the center. We also add 5 pixels as a "fudge factor"
                    # so it's not sitting right on the edge.

                    pushdistance = shield.radius - len_xy + 5

                    # Add the appropriate distance to each dimension, multiplying by the 
                    # normalized vector from before to make sure it goes out at the same
                    # angle.
                    devil.rect.centerx += dx_normalized * pushdistance
                    devil.rect.centery += dy_normalized * pushdistance

    if (event.type == KEYDOWN and event.key == K_s and shield is None and
        powerups['shield'].state == 'collected'):
        shield = Shield(rocket)

    ### The game state has been updated. Time to render!

    starfield.draw()

    levelindicator.draw()
    boostbar.draw()

    # Render rocket and cookie
    cookie.draw()

    for bomb in bombs:
        bomb.draw()

    for powerup in powerups.values():
        if powerup.state == 'onscreen':
            powerup.draw()

    if timebomb is not None:
        timebomb.draw()

    # Render devils
    i = 0
    while i < len(devils):
        devil = devils[i]
        devil.draw()
        i += 1

    rocket.draw()

    if shield is not None:
        shield.draw()

    pygame.display.update()
