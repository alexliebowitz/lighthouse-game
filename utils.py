import random
import math

def randomdirection(maxdist=10):
    # Return a vector we can use to push an object in a random
    # direction. For example, if we return (-5, -5), that means
    # push the object 5 pixels up and to the left.

    # We're going to pick a random point around a unit circle.
    # First, we need to pick a number from -1 to 1 to choose
    # where to sample from the circle along the x dimension.

    x = random.uniform(-1, 1)

    # Use the circle formula to get the y position of the circle
    # for this value of x.
    y = math.sqrt(1 - x**2)

    # Now for any x dimension, there are actually *2* possible
    # points along the y dimension: the top or the bottom.
    # math.sqrt only returns a positive number, so randomly
    # flip y to the bottom 50% of the time.
    if random.choice([True, False]):
        y *= -1

    distance = random.randint(0, maxdist)

    return (x * distance, y * distance)
