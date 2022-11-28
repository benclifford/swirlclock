import math
from math import tau

bottoms = [50, 49, 46, 37, 22, 0]


def pixel_to_layer(pixel):
    """Given a pixel, return the loop number and fraction around the
    loop for this pixel.
    """
    for b in range(0,len(bottoms)-1):
      if pixel < bottoms[b] and pixel >= bottoms[b+1]:
        start = bottoms[b]
        end = bottoms[b+1]
        frac = (pixel - start) / (end - start)
        break
    else:
      raise RuntimeError("could not find range for pixel {}".format(pixel))
    return (b, frac)


def generate_pixel_pos(*, extra_pixels=[], rot = 0):
    """Generate a list of each pixel's x,y position
    based on bottoms info.

    A better implementation might take into account the
    decreasing radius around the spiral (and perhaps
    I've done that somewhere already?)"""

    pixel_pos = {}
    for pixel in list(range(0,50)) + extra_pixels:
      (b, frac) = pixel_to_layer(pixel)
      p_angle = (frac + rot) % 1.0
      x = math.sin(p_angle * tau) * b
      y = math.cos(p_angle * tau) * b
      pixel_pos[pixel] = (x, y)

    return pixel_pos

def distances_from_point(x, y, *, pixel_pos):
    """Return a sorted list of pixels by distance from the specified
    point, the list being tuples (distance, pixel number).

    pixel_pos should come from generate_pixel_pos.
    """

    distances = []
    for pixel in range(0,50):
      (x1, y1) = pixel_pos[pixel]
      distances.append( (math.sqrt( (x-x1) ** 2 + (y-y1) ** 2) , pixel))

    s = sorted(distances)
    return s


def closest_pixels(pixelish):

    pixel_pos = generate_pixel_pos(extra_pixels=[pixelish])

    (x, y) = pixel_pos[pixelish]

    return distances_from_point(x, y, pixel_pos=pixel_pos)


def pixels_for_angle(angle, loop_in):

    # loop_in = 
    # which loop in we're going to pick the base pixel
    # to be. 0 is the outermost loop of the spiral.

    start = bottoms[len(bottoms) - 1 - loop_in]
    end = bottoms[len(bottoms) - 2 - loop_in]
    base_pixelish = start + (end-start) * angle  # almost a pixel, but not rounded

    pixel_pos = generate_pixel_pos(extra_pixels=[base_pixelish])

    (x, y) = pixel_pos[base_pixelish]

    return distances_from_point(x, y, pixel_pos=pixel_pos)
