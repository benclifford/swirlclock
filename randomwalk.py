import random

def randomwalk(*, low, high, bias=0.0):

    range = high - low

    x = random.random() * range + low

    while True:
        x = max(low, min(high, x + random.random() * 0.4 - 0.2 + bias))
        yield x
