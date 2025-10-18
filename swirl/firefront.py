import random
import time

from functools import partial

from swirl.colour import different_hue
from swirl.fadepixel import render_hv_fadepixel, fade_hv_fadepixel
from swirl.topologies import distances_from_point, generate_pixel_pos

from main import pixels, new_mode

def pmode_firefront(*, hue_step, colour_scheme = None):
    pixels.auto_write = False
    
    pixel_pos = generate_pixel_pos()

    hue = random.random()

    display_pixels = [None for pixel in range(0,50)]

    while not new_mode.is_set():

        max_v = 0
        for n in range(0,49):
            if display_pixels[n] is not None:
                (h,v) = display_pixels[n]
                max_v = max(v, max_v)

        if max_v < 0.75: 
            hue = different_hue(hue)
            start_pixel = random.randint(0, 49)
            fire_pixels = [start_pixel]
            display_pixels[start_pixel] = (hue, 1)
  

        for n in range(0, 6):

          if colour_scheme is None:
              schemed_display_pixels = display_pixels
          else:
              schemed_display_pixels = [colour_scheme(hv, n) for (hv, n) in zip(display_pixels, range(0,50))]

          render_hv_fadepixel(pixels, schemed_display_pixels)
          fade_hv_fadepixel(display_pixels, 0.03)

          del schemed_display_pixels  # just to make it clear this doesn't need to be in scope

          time.sleep(0.01)

        new_fire_pixels = []

        for pixel in fire_pixels:
          if display_pixels[pixel] is not None:
            (h, v) = display_pixels[pixel]

            (x, y) = pixel_pos[pixel]

            candidates = distances_from_point(x, y, pixel_pos = pixel_pos)

            candidates = [(d, n) for (d, n) in candidates if display_pixels[n] is None]

            if candidates != []:
                least_d = 1.5

                candidates = [(d, n) for (d, n) in candidates if d <= least_d]

                hue = (hue + hue_step) % 1.0
                for (d,n) in candidates:
                    if random.random() > 0.5:
                        display_pixels[n] = (hue, 1)
                        new_fire_pixels.append(n)

        fire_pixels = new_fire_pixels

def mode63():
    pmode_firefront(hue_step = 0.01)

def mode64():
    pmode_firefront(hue_step = 0)

def mode65():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode65_fire_scheme, hue))

def mode65_fire_scheme(hue, x, n):
    other_hue = (hue + 0.5) % 1.0
    if x is None:
        return (hue, 1)
    else:
        return (other_hue, 1)

def mode66():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode66_fire_scheme, hue))

def mode66_fire_scheme(hue, x, n):
    other_hue = (hue + 0.5) % 1.0
    if x is None:
        return (other_hue, 1)
    else:
        (h, v) = x

        return (h, v)


def mode67():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode67_fire_scheme, hue))

def mode67_fire_scheme(hue, x, n):
    other_hue = (hue + 0.5) % 1.0
    if x is None:
        return (other_hue, 0.2)
    else:
        (h, v) = x

        if v > 0.1:
            return (hue, (v-0.1)*(1.0 / 0.9))
        else:
            return (other_hue, 0.2) 

def mode68():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode68_fire_scheme, hue))

def mode68_fire_scheme(hue, x, n):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        return (random.random(), v)

def mode124():
    colours = {}
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode124_fire_scheme, colours))

def mode124_fire_scheme(colours, x, n):
    if x is None:
        if n in colours:
            del colours[n]
        return (0, 0)
    else:
        if n not in colours:
            colours[n] = random.random()
        (h, v) = x
        return (colours[n], v)


def mode125():
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode125_fire_scheme, random.random()))

def mode125_fire_scheme(hue, x, n):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        return ((hue + v / 4) % 1.0, v)



def mode109():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode109_fire_scheme, hue))

def mode109_fire_scheme(hue_base, x, n):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        if v > 0.5:
            return (hue_base, 1.0)
        else:
            return ((hue_base + 0.5) % 1.0, 1.0)

def mode110():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode110_fire_scheme, hue))

def mode110_fire_scheme(hue_base, x, n):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        if v > 0.85:
            return (hue_base, 1.0)
        elif v > 0.5:
            return (hue_base, 0.3)
        else:
            return (0, 0)

def mode111():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode111_fire_scheme, hue))

def mode111_fire_scheme(hue_base, x, n):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        if v > 0.80:
            return (hue_base, 1.0)
        elif v > 0 and v < 0.2:
            return ((hue_base + 0.5) % 1.0, 1.0)
        else:
            return (0, 0)


