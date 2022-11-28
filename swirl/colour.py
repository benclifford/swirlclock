import colorsys
import random

def scale(f):
    """ scale from 0..1 : float -> 0..255 : int"""
    try:
      return int(f * 255)
    except:
      print("Scale got an exception on input {}".format(f))
      reraise

def gamma(v, gamma_factor=1.9):
    """ gamma correct on range 0..1 : float
    Based on https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix

    gamma_factor default of 1.9 comes from my subjective attempts to get the colourwheel to look even.

    gamma_factor 2.8 is the value that adafruit people like

    """
    if v < 0 or v > 1:
        raise ValueError("Attempted gamma correction on out of range value {}".format(v))

    return (v ** gamma_factor)

def hsv_to_neo_rgb(h, s=1, v=1):
    """Convert specified HSV values to neopixel compatible RGB. S and V default
    to full brightness, fully saturated, as that is a common use mode
    for designs.
    """
    (red, green, blue) = colorsys.hsv_to_rgb(h, s, v)
    return ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )



def different_hue(hue):
    """Returns a hue that is noticeably different than the
    input hue."""
    return (hue + 0.15 + random.random()*0.7) % 1.0


def max_pixel( p1, p2 ):
    (r1, g1, b1) = p1
    (r2, g2, b2) = p2
    return (  max(r1, r2),   max(g1, g2),  max(b1, b2) )
