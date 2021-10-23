import random

def randomwalk(*, low, high, bias=0.0, spread = 0.2):

    range = high - low

    x = random.random() * range + low

    while True:
        x = max(low, min(high, x + random.random() * spread * 2 - spread + bias))
        yield x
