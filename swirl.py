# usage notes for python neopixe pi libraries:
#     https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage


# spiral maths notes:
#     https://www.intmath.com/blog/mathematics/length-of-an-archimedean-spiral-6595
#     https://www.giangrandi.ch/soft/spiral/spiral.shtml

import board
import colorsys  # from pygame
import itertools
import math
import neopixel
import random
import threading
import time

import flask

from math import tau

pixels = neopixel.NeoPixel(board.D18, 50)

bottoms = [50, 49, 46, 37, 22, 0]

new_mode = None

disco_thread = None

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


def mode1():
    global new_mode
    pixels.auto_write = True
    pixels.fill( (0,0,0) )
    n = 0
    while not new_mode:
        pixel = random.randint(0,49)

        if n == 0:
            (red, green, blue) = (0,0,0)
        else:
            hue = random.random()
            (red, green, blue) = hsv_to_neo_rgb(hue)
        pixels[pixel] = (red, green, blue)
        n = (n+1) % 3
        time.sleep(1)


def mode2():
    global new_mode

    period = 3600.0  # seconds
    frame_period = 0.05  # seconds

    frame_step = frame_period / period
    print("Frame step: {} hue units per frame".format(frame_step))
    hue = 0

    pixels.auto_write = False

    t = 0

    while not new_mode:
        print("Hue: {}".format(hue))
        pixels.fill(hsv_to_neo_rgb(hue))

        secs = t % 60

        tick_pixel = int(secs/60.0 * 50.0)

        pixels[tick_pixel] = hsv_to_neo_rgb((hue + 0.5) % 1)

        pixels.show()

        hue = (hue + frame_step) % 1.0
        time.sleep(frame_period)
        t += frame_period


def mode3():
    mode_solid( (255, 0, 32) )


def mode6():
    mode_solid( (0, 0, 0) )


def mode_solid(rgb):

    global new_mode
    pixels.auto_write = True
    
    while not new_mode:
        pixels.fill( rgb )
        time.sleep(1)


def mode31():
    global new_mode
    pixels.auto_write = False

    hue = random.random()

    brightness = []

    b = 0.5
    for p in range(0,50):
        brightness.append(b)
        b = max(0.1, min(1.0, b + random.random() * 0.4 - 0.2))

    while not new_mode:
        for p in range(0,50):
            pixels[p] = hsv_to_neo_rgb(hue, s=0.75, v=brightness[p]) 
        pixels.show()

        # rotate through all hues every 3 hours
        hue = (hue + 1.0 / (3.0 * 60.0 * 60.0) ) % 1.0
        time.sleep(0.5)


def mode4():
    global new_mode
    pixels.auto_write = False
    colours = {}
    for n in range(0,50):
        colours[n] = random.random()

    for n in range(0,50):
        pixels[n] = hsv_to_neo_rgb(colours[n])

    pixels.show()

    count = 0

    while not new_mode:

        swapped = False

        if count == 0:
            new_pixel = random.randint(0,49)
            new_hue = random.random()

        count = (count + 1) % 200

        p1 = random.randint(0,48)
        p2 = p1 + 1

        if colours[p1] > colours[p2]:
            tmp = colours[p1]
            colours[p1] = colours[p2]
            colours[p2] = tmp
            swapped = True

        if swapped:
            for n in range(0,50):
                pixels[n] = hsv_to_neo_rgb(colours[n])

            pixels.show()
            time.sleep(0.1)


def mode5():
    global new_mode
    while not new_mode:
        time.sleep(1)


def mode7():
    global new_mode
    pixels.auto_write = False

    for pixel in range(0,50):
      (b, frac) = pixel_to_layer(pixel)
      pixels[pixel] = hsv_to_neo_rgb(frac)
      
    pixels.show()

    while not new_mode:
        time.sleep(1)


def mode8():
  global new_mode
  pixels.auto_write = False

  rot_hue = 0
  rot_pos = 0

  while not new_mode:

    for pixel in range(0,50):
      (b, frac) = pixel_to_layer(pixel)
      frac_hue = (frac + rot_hue) % 1
      frac_pos = (frac + rot_pos) % 1

      width = 0.15

      if frac_pos > width and frac_pos < (1-width):
          intensity = 0
      elif frac_pos >= (1-width):
          frac_pos = 1 - frac_pos
          intensity = (width - frac_pos) * (1/width)
      else:
          intensity = (width - frac_pos) * (1/width)

      pixels[pixel] = hsv_to_neo_rgb(frac_hue, v=intensity)
      
    pixels.show()

    rot_hue = rot_hue + (1.0/600.0) % 1
    rot_pos = rot_pos + (1.0/423.0) % 1
    time.sleep(0.01)


def mode9():
  global new_mode
  pixels.auto_write = False

  update_period = 0.01
  width = 0.12

  rot_hue = 0


  while not new_mode:
    pixels.fill( (0,0,0) )

    now = time.localtime()

    # set hour
    for pixel in range(0,49):
      (b, frac) = pixel_to_layer(pixel)

      hour_frac = now.tm_hour % 12 / 12.0
      frac_hue = (frac + rot_hue) % 1


      d = (frac + hour_frac + 0.5) % 1
      if d > width and d < (1-width):
          intensity = 0
          # don't set pixel because we want it "transparent" rather than black
      elif d >= (1-width):
          d = 1 - d
          intensity = (width - d) * (1/width)
          pixels[pixel] = hsv_to_neo_rgb(frac_hue, v=intensity)
      else:
          intensity = (width - d) * (1/width)
          pixels[pixel] = hsv_to_neo_rgb(frac_hue, v=intensity)

    pixels.show()

    rot_hue = rot_hue + (1.0/42300.0 * (update_period / 0.01)) % 1
    time.sleep(update_period)


def mode10():
    mode_rotator()

def mode12():
    mode_rotator(spin_speed = 1.0 / 60.0)

def mode_rotator(spin_speed = 1.0/600.0):

    global new_mode
    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    offset = 0

    while not new_mode:
      for pixel in range(0,50):
        (b, proportion_around_loop) = pixel_to_layer(pixel)
        frac = (proportion_around_loop + offset) % 1.0

        # simple radial proportion that assumes that each LED between bottom points
        # is at a constant distance, with an immediate jump at each bottom point to
        # be one unit further in.
        # That leads to some abrupt changes in LED brightness, especially near the end
        # of the strand

        # this should make b into a number that decreases more smoothly than b,
        # taking into account how far round the loop we are (which is stored
        # in frac)
        b_pro_rated = b + proportion_around_loop
        radial_proportion = b_pro_rated / (len(bottoms)-1)

        pixels[pixel] = hsv_to_neo_rgb(frac, s=radial_proportion, v=radial_proportion)

      pixels.show()

      offset = (offset + spin_speed) % 1.0

      time.sleep(0.1)


def mode11():

    global new_mode
    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    hue = 0.5
    angle = 0.3
    width = 1
    speed = 0.2
    outwards = 0

    while not new_mode:


      for pixel in range(0,50):
        (b, proportion_around_loop) = pixel_to_layer(pixel)
        frac = proportion_around_loop

        # simple radial proportion that assumes that each LED between bottom points
        # is at a constant distance, with an immediate jump at each bottom point to
        # be one unit further in.
        # That leads to some abrupt changes in LED brightness, especially near the end
        # of the strand

        # this should make b into a number that decreases more smoothly than b,
        # taking into account how far round the loop we are (which is stored
        # in frac)
        b_pro_rated = b + proportion_around_loop
        radial_proportion = b_pro_rated / (len(bottoms)-1)

        angle_distance = angle-frac
        if angle_distance > 0.5:
          angle_distance = 1-angle_distance


        distance = (math.sqrt( (angle_distance/width) ** 2 + (outwards - radial_proportion) ** 2))
        if distance < 0.3:
          brightness = (0.3 - distance) / 0.3
        else:
          brightness = 0

        pixels[pixel] = hsv_to_neo_rgb(hue, v=brightness)

      pixels.show()

      outwards = outwards + speed

      if outwards > 1.3:
        outwards = 0
        speed = 0.075 + random.random() * 0.225
        hue = random.random()
        angle = random.random()
        width = 0.1 + random.random() * 0.9

      time.sleep(0.02)


def mode13():

  global new_mode
  pixels.auto_write = False

  toggle = True
  while not new_mode:

    if toggle:
      pixels.fill( (0,0,32) )
    else:
      pixels.fill( (0,0,0) )

    toggle = not toggle

    for b in range(1,len(bottoms)):
      p = bottoms[b]
      pixels[p] = (255,0,0)

    for b in range(1, len(bottoms)-1):
      diff = bottoms[b+1] - bottoms[b]
      if diff % 2 == 0:  # even number
        p = bottoms[b] + diff/2
        pixels[int(p)] = (0,255,0)
      else:
        p = bottoms[b] + diff/2
        pixels[int(p)] = (0,255,0)
        pixels[int(p)+1] = (0,255,0)
    
    pixels.show()

    time.sleep(0.3)


def mode14(display_seconds = False):
  global new_mode
  pixels.auto_write = False

  while not new_mode:
    pixels.fill( (0,0,0) )
    

    now = time.localtime()
    hour = now.tm_hour % 12
    minute = now.tm_min
    second = now.tm_sec

    hour_angle = (0.5 + hour/12.0 + minute/60.0/12.0) % 1.0
    minute_angle = (0.5 + minute/60.0) % 1.0
    second_angle = (0.5 + second/60.0) % 1.0

    mins_scaled = int(minute / 15 + 1)

    hour_pixels = pixels_for_angle(hour_angle, 1)
    minute_pixels = pixels_for_angle(minute_angle, 0)
    second_pixels = pixels_for_angle(second_angle, 0)

    minute_pixels = minute_pixels[0:mins_scaled]
    for dot in minute_pixels:
        (distance, pixel) = dot
        hour_pixels = [(d,p) for (d,p) in hour_pixels if p != pixel]
        second_pixels = [(d,p) for (d,p) in second_pixels if p != pixel]

    if hour == 0:
        hour_dot_count = 12
    else:
        hour_dot_count = hour

    hour_pixels = hour_pixels[0:hour_dot_count]
    for dot in hour_pixels:
        (distance, pixel) = dot
        second_pixels = [(d,p) for (d,p) in second_pixels if p != pixel]

    second_pixels = second_pixels[0:1]
    
    for dot in hour_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (255,0,0)


    for dot in minute_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (0,0,32)

    for dot in minute_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (0,0,32)

    if display_seconds:
        for dot in second_pixels:
            (distance, pixel) = dot
            if now.tm_sec % 2 == 0:
                pixels[pixel] = (0,32,0)
            else:
                pixels[pixel] = (0,1,0)

    pixels.show()
    time.sleep(0.05)


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


def mode15():
  global new_mode
  pixels.auto_write = False

  cells = [0 for n in range(0,50)]

  particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])

  first = True
  boom = False

  while not new_mode:

    # move particle
    (b, frac) = pixel_to_layer(particle)

    choice = random.randint(0,2)

    old_first = first
    first = False

    if choice == 0:
      new_particle = particle + 1
      if new_particle >= bottoms[b]:
        new_particle = bottoms[b+1]

    elif choice == 1:
      new_particle = particle - 1  # TODO: mod
      if new_particle < bottoms[b+1]:
        new_particle = bottoms[b]-1
    elif choice == 2:
      # move inwards
      # determine angle now
      if b == 0:
        # if we reach the centre, solidify
        cells[particle] = 1
        new_particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
        boom = old_first
        first = True
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)

    if cells[new_particle] != 0: # if we're about to move onto solid, solidify
      cells[particle] = 1
      particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
      boom = old_first
      first = True
    else:
      particle = new_particle

    # display state

    for pixel in range(0,50):
      if cells[pixel] == 0:
        pixels[pixel] = (0,0,0)
      elif cells[pixel] == 1:
        pixels[pixel] = (16,16,255)
      else:
        pixels[pixel] = (255,0,0)

    pixels[particle] = (0,32,0)

    pixels.show()

    if boom:
      for exponent in range(8,0,-1):
        brightness = (2 ** exponent) - 1
        for pixel in range(0,50):
          if cells[pixel] == 0:
            pixels[pixel] = (0,0,0)
          elif cells[pixel] == 1:
            pixels[pixel] = (brightness,brightness,brightness)
          else:
            pixels[pixel] = (255,0,0)
        pixels.show()
        time.sleep(0.04)
      cells = [0 for n in range(0,50)]

    boom = False

    time.sleep(0.005)


def mode16():
    iterator_spiral(iterator=generate_mode16(), delay=0.05)


def generate_mode16():
    hue = random.random()

    while True:
        hue = (hue + random.random() * 0.1 - 0.05) % 1.0
        yield hsv_to_neo_rgb(hue)


def iterator_spiral(*, iterator, delay):
  global new_mode
  pixels.auto_write = False

  ps = [(0,0,0) for n in range(0,50)]

  while not new_mode:
    for pixel in range(49,0,-1):
      ps[pixel] = ps[pixel-1]

    ps[0] = next(iterator)

    for pixel in range(0,50):
      pixels[pixel] = ps[pixel]

    pixels.show()
    time.sleep(delay)


def mode35():
    iterator_spiral(iterator=generate_mode35(), delay=0.01)


def generate_mode35():
    hue = random.random()
    v = 0.1

    while True:
        # deliberately biased downwards so we hit 0 more
        v = min(1.0, max(0, v + random.random() * 0.4 - 0.2))
        if v == 0:
            hue = random.random()

        yield hsv_to_neo_rgb(hue, v=v)


def mode17():
  global new_mode
  pixels.auto_write = False

  start_hue = random.random()
  rings = [start_hue for b in bottoms]

  while not new_mode:

    for ring in range(len(rings)-1, 1, -1):
      rings[ring] = rings[ring-1]

    rings[1] += random.random() * 0.15

    for ring in range(1, len(rings)-1):
      for pixel in range(bottoms[ring], bottoms[ring+1] - 1, -1):
        pixels[pixel] = hsv_to_neo_rgb(rings[ring])

    pixels.show()

    time.sleep(0.1)

def mode26():
  global new_mode
  pixels.auto_write = False

  start_hue = random.random()
  rings = [None for b in bottoms]

  while not new_mode:

    for ring in range(len(rings)-1, 1, -1):
      rings[ring] = rings[ring-1]

    if random.random() > 0.66:
        rings[1] = random.random()
    else:
        rings[1] = None

    for ring in range(1, len(rings)-1):
      for pixel in range(bottoms[ring], bottoms[ring+1] - 1, -1):
        if rings[ring]:
            pixels[pixel] = hsv_to_neo_rgb(rings[ring])
        else:
            pixels[pixel] = (0,0,0)

    pixels.show()

    time.sleep(0.1)



def mode18():
    global new_mode
    pixels.auto_write = False

    x = 0
    y = 0
    ndots = 5
    hue = 0.2

    radius = 5.0  # this is the radius that the centre point moves within - it doesn't matter if it goes outside the spiral as dots will just squish up against the edge

    velocity_mag = 0.15

    xv = velocity_mag + random.random() * velocity_mag
    yv = velocity_mag + random.random() * velocity_mag

    pixel_pos = generate_pixel_pos()

    while not new_mode:
        x = x + xv
        y = y + yv

        if math.sqrt(x ** 2 + y ** 2) > radius:

          hue = hue + random.random() * 0.1
          min_dots = 3
          max_dots = 8
          ndots = max(min_dots, min(max_dots, ndots + random.randint(0,2) - 1))

          # pick a new velocity - it should be back roughly towards the centre
          # but with a random deflection

          angle_to_centre = math.atan2(y, x)

          angle_range = 1.3
          angle_to_centre = angle_to_centre + random.random() * angle_range  - (angle_range * 0.5)
          new_mag = velocity_mag + velocity_mag * random.random()
          xv = -math.cos(angle_to_centre) * new_mag
          yv = -math.sin(angle_to_centre) * new_mag

          # shrink back so we are inside the circle
          # could do this better to approximate the point at which
          # we hit the unit circle
          rescale = radius / math.sqrt(x ** 2 + y ** 2)
          x = x * rescale
          y = y * rescale

        s = distances_from_point(x, y, pixel_pos = pixel_pos)

        dots_to_light = s[0:ndots]

        pixels.fill( (0,0,0) )

        for (d, pixel) in dots_to_light:
            pixels[pixel] = hsv_to_neo_rgb(hue)

        pixels.show()
        time.sleep(0.01)


def mode19():
    global new_mode
    pixels.auto_write = False

    # hue of pixel, or None if it should be blank
    display_pixels = [None for pixel in range(0,50)]

    x = 0
    y = 0
    min_dots = 1
    max_dots = 3
    hue = 0.2

    radius = 5.0  # this is the radius that the centre point moves within - it doesn't matter if it goes outside the spiral as dots will just squish up against the edge

    velocity_mag = 0.15

    ndots = round( (max_dots + min_dots) / 2)
    xv = velocity_mag + random.random() * velocity_mag
    yv = velocity_mag + random.random() * velocity_mag


    pixel_pos = generate_pixel_pos()

    while not new_mode:
        x = x + xv
        y = y + yv

        if math.sqrt(x ** 2 + y ** 2) > radius:

          hue = hue + 0.05 + random.random() * 0.07
          ndots = max(min_dots, min(max_dots, ndots + random.randint(0,2) - 1))
           

          # pick a new velocity - it should be back roughly towards the centre
          # but with a random deflection

          angle_to_centre = math.atan2(y, x)

          angle_range = 1.3
          angle_to_centre = angle_to_centre + random.random() * angle_range  - (angle_range * 0.5)
          new_mag = velocity_mag + velocity_mag * random.random()
          xv = -math.cos(angle_to_centre) * new_mag
          yv = -math.sin(angle_to_centre) * new_mag

          # shrink back so we are inside the circle
          # could do this better to approximate the point at which
          # we hit the unit circle
          rescale = radius / math.sqrt(x ** 2 + y ** 2)
          x = x * rescale
          y = y * rescale

        s = distances_from_point(x,y,pixel_pos=pixel_pos)

        dots_to_light = s[0:ndots]

        for dot in dots_to_light:
            (distance, pixel) = dot
            display_pixels[pixel] = (hue, 1)

        render_hv_fadepixel(pixels, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.0075)
        
        time.sleep(0.01)

def mode20():
  global new_mode
  pixels.auto_write = False

  particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
  hue = random.random()

  first = True
  boom = False

  while not new_mode:

    # move particle
    (b, frac) = pixel_to_layer(particle)

    choice = random.randint(0,2)

    old_first = first
    first = False

    if choice == 0:
      new_particle = particle + 1
      if new_particle >= bottoms[b]:
        new_particle = bottoms[b+1]

    elif choice == 1:
      new_particle = particle - 1  # TODO: mod
      if new_particle < bottoms[b+1]:
        new_particle = bottoms[b]-1
    elif choice == 2:
      # move inwards
      # determine angle now
      if b == 0:
        # if we reach the centre, solidify
        new_particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
        boom = old_first
        first = True
        pixels.fill( (0,0,0) )
        hue = random.random()
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)

    particle = new_particle

    # display state

    pixels[particle] = hsv_to_neo_rgb(hue)

    pixels.show()

    boom = False

    time.sleep(0.02)


def mode21():
    global new_mode
    pixels.auto_write = False

    # the inner loops don't look good in this mode
    # because not enough pixels so leave them empty
    min_loop = 3

    min_frac = 0.3
    max_frac = 0.6

    params = {}
    for b in range(min_loop, len(bottoms)):
        params[b] = {}
        params[b]["hue"] = random.random()
        params[b]["length"] = min_frac + random.random() * (max_frac - min_frac)
        params[b]["offset"] = 0
        params[b]["speed"] = random.random() + 0.3
        if(random.random() > 0.5):
            params[b]["speed"] = -params[b]["speed"]

    while not new_mode:
        pixels.fill( (0,0,0) )

        for b in range(min_loop, len(bottoms)):
            bottom_len = bottoms[b-1] - bottoms[b]
            slice_len = max(1, int(bottom_len * params[b]["length"]))
            for s in range(0,slice_len):
                t = bottoms[b] + int( (params[b]["offset"] + s) % bottom_len)
                hue = params[b]["hue"]
                pixels[t] = hsv_to_neo_rgb(hue)
            params[b]["offset"] = (params[b]["offset"] + params[b]["speed"]) % bottom_len

        pixels.show()
        time.sleep(0.01)


def mode22():
    global new_mode
    pixels.auto_write = False

    # None = blank, otherwise a hue
    display_pixels = [None for n in range(0,50)]

    while not new_mode:

        active_pixel = random.randint(0,49)

        if display_pixels[active_pixel] is None:
            # off-rules:

            total_lit = 0
            for p in display_pixels:
                if p is not None:
                    total_lit = total_lit + 1

            if total_lit < 30:
                display_pixels[active_pixel] = random.random()

        else:
            display_pixels[active_pixel] = (display_pixels[active_pixel] + 0.1)
            if display_pixels[active_pixel] >= 1.0:
                display_pixels[active_pixel] = None

        for pixel in range(0,50):
            if display_pixels[pixel] is None:
                pixels[pixel] = (0,0,0)
            else:
                pixels[pixel] = hsv_to_neo_rgb(display_pixels[pixel])

        pixels.show()

        time.sleep(0.1)


def mode23():
    global new_mode
    pixels.auto_write = False

    # None = blank, otherwise a hue
    display_pixels = [None for n in range(0,50)]

    end_rainbow_increase_factor = 1.1
    blanking_probability = 0.999
    rotate_period = 0.07

    rotate_time = time.time()

    while not new_mode:

        # rotate along spiral with a certain percentage
        # hopefully this makes the spiralness more visible
        # than a static display

        new_rotate_time = time.time()
        if False and new_rotate_time > rotate_time+rotate_period:

            tmp = display_pixels[49]
            for n in range(49,0,-1):
                display_pixels[n] = display_pixels[n-1]
            display_pixels[0] = tmp
            rotate_time = new_rotate_time


        active_pixel = random.randint(0,49)

        # this lets us watch how fast things are considered
        if False:
            pixels[active_pixel] = (255,255,255)
            pixels.show()

        total_lit = 0
        for p in display_pixels:
            if p is not None:
                total_lit = total_lit + 1

        (b, frac) = pixel_to_layer(active_pixel)

        if b >= 1:
            inwards_particle = int(bottoms[b-1] + (bottoms[b] - bottoms[b-1])*frac)
            inwards_hue = display_pixels[inwards_particle]
        else:
            inwards_hue = None

        if b < len(bottoms):
            outwards_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)
            outwards_hue = display_pixels[outwards_particle]
        else:
            outwards_hue = None

        if display_pixels[active_pixel] is None:
            # off-rules:
            if total_lit < 32:
                # dark pixel turning on
                # according to assorted rainbow-forming rules

                # if we're between two lit pixels, choose a hue that is
                # part of a rainbow between the two:
                if active_pixel >= 1 and active_pixel <= 48 and \
                   display_pixels[active_pixel - 1] is not None and \
                   display_pixels[active_pixel + 1] is not None:

                  diff = (display_pixels[active_pixel + 1] - display_pixels[active_pixel - 1]) 
                  if diff > 0.5:
                      diff -= 1.0

                  if abs(diff) < 0.2:  # only do an infill for close colours
                    new_hue = (display_pixels[active_pixel - 1] + diff / 2.0) % 1.0
                    display_pixels[active_pixel] = new_hue 
                  else:
                    display_pixels[active_pixel] = None

                # pixel downwards is on. pixel upwards is not on, otherwise caught by previous case.
                elif active_pixel >= 2 and \
                    display_pixels[active_pixel - 1] is not None and \
                    display_pixels[active_pixel - 2] is not None:

                    diff = display_pixels[active_pixel - 1] - display_pixels[active_pixel - 2]
                    if diff > 0.5:
                        diff -= 1.0
                    # multiple diff up a bit to try to force the rainbowness
                    new_hue = (display_pixels[active_pixel - 1] + (diff * end_rainbow_increase_factor)) % 1.0
                    display_pixels[active_pixel] = new_hue 

                elif active_pixel <= 47 and \
                    display_pixels[active_pixel + 1] is not None and \
                    display_pixels[active_pixel + 2] is not None:

                    diff = display_pixels[active_pixel + 1] - display_pixels[active_pixel + 2]
                    if diff > 0.5:
                        diff -= 1.0
                    new_hue = (display_pixels[active_pixel + 1] + (diff * end_rainbow_increase_factor)) % 1.0
                    display_pixels[active_pixel] = new_hue 

                # possible elif here: look inwards and outwards rather than around the spiral to
                # find other nearby colours
                elif inwards_hue is not None or outwards_hue is not None:
                    if inwards_hue is not None and outwards_hue is None:
                        display_pixels[active_pixel] = inwards_hue
                    elif inwards_hue is None and outwards_hue is not None:
                        display_pixels[active_pixel] = outwards_hue
                    else:
                        diff = inwards_hue - outwards_hue
                        if diff > 0.5:
                            diff -= 1.0
                        new_hue = (outwards_hue + diff / 2.0) % 1.0
                        display_pixels[active_pixel] = new_hue

                else:  # all we can do now is pick a random hue
                    display_pixels[active_pixel] = random.random()

        else:
            if total_lit > 20 and random.random() > blanking_probability: # some hysteresis with the off-mode equivalent to keep a decent twinkling zone, perhaps
                display_pixels[active_pixel] = None
 
            # if we're between two lit pixels, choose a hue that is
            # part of a rainbow between the two:
            elif active_pixel >= 1 and active_pixel <= 48 and \
                display_pixels[active_pixel - 1] is not None and \
                display_pixels[active_pixel + 1] is not None:

                diff = (display_pixels[active_pixel + 1] - display_pixels[active_pixel - 1]) 
                if diff > 0.5:
                    diff -= 1.0
                new_hue = (display_pixels[active_pixel - 1] + diff / 2.0) % 1.0
                display_pixels[active_pixel] = new_hue 

            # pixel downwards is on. pixel upwards is not on, otherwise caught by previous case.
            elif active_pixel >= 2 and \
                display_pixels[active_pixel - 1] is not None and \
                display_pixels[active_pixel - 2] is not None:

                diff = display_pixels[active_pixel - 1] - display_pixels[active_pixel - 2]
                if diff > 0.5:
                    diff -= 1.0

                forced_diff = max(-0.1, min(0.1, diff * end_rainbow_increase_factor))
                # multiple diff up a bit to try to force the rainbowness
                new_hue = (display_pixels[active_pixel - 1] + forced_diff) % 1.0
                display_pixels[active_pixel] = new_hue 

            elif active_pixel <= 47 and \
                display_pixels[active_pixel + 1] is not None and \
                display_pixels[active_pixel + 2] is not None:

                diff = display_pixels[active_pixel + 1] - display_pixels[active_pixel + 2]
                if diff > 0.5:
                    diff -= 1.0
                forced_diff = max(-0.1, min(0.1, diff * end_rainbow_increase_factor))
                new_hue = (display_pixels[active_pixel + 1] + forced_diff) % 1.0
                display_pixels[active_pixel] = new_hue 

            else:
                # we can't do anything to this pixel to enhance rainbowness, so
                # with a certain percentage, blank it so we can get a new chance
                # elsewhere. Otherwise leave it untouched.

                if random.random() < 0.1:
                    display_pixels[active_pixel] = None

                # if we can't enhance the rainbowness of an existing pixel, just leave it as.
                # pass  

                ##                display_pixels[active_pixel] = (display_pixels[active_pixel] + random.random() * 0.01) % 1.0

        for pixel in range(0,50):
            if display_pixels[pixel] is None:
                pixels[pixel] = (0,0,0)
            else:
                pixels[pixel] = hsv_to_neo_rgb(display_pixels[pixel])

        pixels.show()

        # time.sleep(0.1)


def mode24():
    global new_mode
    pixels.auto_write = False

    gamma_factor = 1.4

    red_exp = 1
    green_exp = 1
    blue_exp = 1

    while not new_mode:
        for pixel in range(0,50):
            (b, frac) = pixel_to_layer(pixel)

            (red, green, blue) = colorsys.hsv_to_rgb(frac, 1, 1)

            red *= red_exp
            green *= green_exp
            blue *= blue_exp

            (red, green, blue) = ( scale(gamma(red, gamma_factor=gamma_factor)),
                                   scale(gamma(green, gamma_factor=gamma_factor)),
                                   scale(gamma(blue, gamma_factor=gamma_factor)) )

            pixels[pixel] = (red, green, blue)
      
        pixels.show()

        red_exp = max(0, red_exp - 0.09)
        green_exp = max(0, green_exp - 0.09)
        blue_exp = max(0, blue_exp - 0.09)

        if random.random() < 0.08:
            red_exp = 1
        if random.random() < 0.08:
            green_exp = 1
        if random.random() < 0.08:
            blue_exp = 1

        time.sleep(0.03)



class M25_state:
    def __init__(self, hue):
        self.hue = hue
        self.born = time.time()

def mode25():
    global new_mode
    pixels.auto_write = False

    target_frac = 0.5

    state = [None for c in range(0,50)]

    pixel_pos = generate_pixel_pos()

    iterations_since_last_change = 0

    while not new_mode:
        """
        # print("====")
        global_hues_live = [state[p1].hue for p1 in range(0,50) if state[p1] is not None]

        if global_hues_live != []:
            global_hues_sorted = sorted(global_hues_live)
            global_hues_grouped = [list(it) for (h, it) in itertools.groupby(global_hues_sorted)]
            global_hues_counted = [(len(l), l[0]) for l in global_hues_grouped]
            global_hues_counted_sorted = sorted(global_hues_counted)
            # print("global_hues_counted_sorted = {}".format(global_hues_counted_sorted))
            (top_count, _) = global_hues_counted_sorted[0]
            if top_count > 10:
                global_maximal_hues = [hue for (count, hue) in global_hues_counted_sorted if count == top_count]
            else:
                global_maximal_hues = []
        else:
            global_maximal_hues = []
        """

        active_pixel = random.randint(0,49)

        # highlight the chosen pixel
        # pixels[active_pixel] = (255,0,0)
        # pixels.show()

        (x,y) = pixel_pos[active_pixel]

        s = distances_from_point(x, y, pixel_pos=pixel_pos)

        # print("---")
        ball = [(d, n) for (d,n) in s if d < 1.5]

        # remove self from ball
        # print("len ball first: {}".format(len(ball)))
        ball = [(d, n) for (d,n) in ball if n != active_pixel]
        # print("len ball after removing self: {}".format(len(ball)))

        # print("ball size: {}".format(len(ball)))

        # for (d, p) in ball:
        #    pixels[p] = (0,255,0)
        # pixels.show()
        # time.sleep(0.5)

        # main rule:
        # aim to have 50% of pixels on

        count_on = 0
        for (d,p) in ball:
            if state[p] is not None:
                count_on += 1

        if state[active_pixel] is not None:
            count_on += 1

        if state[active_pixel] is not None and count_on == 0: 
            iterations_since_last_change += 1
            pass  # leave on, but do not do colour selection
        elif count_on >= len(ball) * target_frac:
            # print("turning pixel off")
            if state[active_pixel] is None:
                iterations_since_last_change += 1
            else:
                iterations_since_last_change = 0
            state[active_pixel] = None
        elif state[active_pixel] is None:
            # turn on
            #print("turning pixel on")
            ball_live = [(d, p) for (d, p) in ball if state[p] is not None]
            # print("len live_ball = {}".format(len(ball_live)))
            if ball_live == []:
                state[active_pixel] = M25_state(random.random())
                iterations_since_last_change = 0
            else:
                hues_live = [state[p1].hue for (d1, p1) in ball_live]
                hues_sorted = sorted(hues_live)
                hues_grouped = [list(it) for (h, it) in itertools.groupby(hues_sorted)]
                hues_counted = [(len(l), l[0]) for l in hues_grouped]
                hues_counted_sorted = sorted(hues_counted)
                # print("hues_grouped = {}".format(hues_grouped))
                # print("hues_counted_sorted = {}".format(hues_counted_sorted))
                (last_count, _) = hues_counted_sorted[0]
                # print("last_count = {}".format(last_count))
                minimal_hues = [hue for (count, hue) in hues_counted_sorted if count == last_count]
                # print("suppressing global_maximal_hues {}".format(global_maximal_hues))
                # minimal_hues = [h for h in minimal_hues if h not in global_maximal_hues]
                # print("remaining minimal hues: {}".format(minimal_hues))

                if minimal_hues != []:
                # print("minimal_hues = {}".format(minimal_hues))
                    new_hue = minimal_hues[random.randint(0, len(minimal_hues)-1)]
                    iterations_since_last_change = 0
                    state[active_pixel] = M25_state(new_hue)
                else:
                    iterations_since_last_change += 1
        else:
            ball_live = [(d, p) for (d, p) in ball if state[p] is not None]
            hues_live = [state[p].hue for (d, p) in ball_live if state[p].hue != state[active_pixel].hue]
            # hues_live now has the list of colours that are not the colour of this
            # pixel

            # turn off if any nearby different colours
            if hues_live != []:
                state[active_pixel] = None
                iterations_since_last_change = 0
            else:
                iterations_since_last_change += 1

        if iterations_since_last_change > 500:
            print("NO CHANGE THRESHOLD REACHED")
            iterations_since_last_change = 0
            live_pixels = [pixel for pixel in range(0,50) if state[pixel] is not None]
            # assume some live pixels else we would be getting changes
            if live_pixels != []:
                p = random.randint(0, len(live_pixels)-1)
                state[p] = None

            hues_live = [state[p].hue for p in range(0,50) if state[p] is not None]
            if hues_live != []:
                # then we have some colours
                first_hue = hues_live[0]
                other_hues = [h for h in hues_live if h != first_hue]
                if other_hues == []:
                    print("Game over - restarting")
                    # one hue has won!
                    # so it's game over
                    # restart this game
                    new_mode = mode25

        hues_sorted = sorted([state[n].hue for n in range(0,50) if state[n] is not None])

        hues = [h for (h, _) in itertools.groupby(hues_sorted)]

        if len(hues) > 1:
          this_hue_n = random.randint(0, len(hues) - 1)

          this_hue = hues[this_hue_n]
          old_hue = this_hue
          next_hue = hues[(this_hue_n + 1) % len(hues)]

          diff = next_hue - this_hue

          if diff > 0.5:
              diff -= 1.0

          if abs(diff) < 0.1:

            if diff > 0:
                new_hue = (this_hue - 0.001) % 1.0
            else:
                new_hue = (this_hue + 0.001) % 1.0


            for n in range(0,50):
                if state[n] and state[n].hue == old_hue:
                    state[n].hue = new_hue

        # expire pixels that haven't changed for a while
        now = time.time()
        for n in range(0,50):
            if state[n]:
                expire_time = state[n].born + 30
                if expire_time < now:
                    print("expire a pixel")
                    state[n] = None

        for pixel in range(0,50):
            if state[pixel] is None:
                pixels[pixel] = (0,0,0)
            else:
                pixels[pixel] = hsv_to_neo_rgb(state[pixel].hue)

        pixels.show()



def disco_manager():
    global disco_thread
    global new_mode

    me = disco_thread  # assume disco thread hasn't changed since start, a tiny race condition

    print("starting disco manager")

    disco_modes = [mode8,
                   mode11,
                   mode15,
                   mode20,
                   mode16,
                   mode17,
                   mode26,
                   mode18,
                   mode19,
                   mode21,
                   mode24,
                   mode27,
                   mode28,
                   mode33,
                   mode34,
                   mode30,
                   mode35,
                   mode36,
                   mode38,
                   mode39,
                   mode40,
                   mode41,
                   mode42,
                   mode43,
                   mode44,
                   mode46,
                   mode47,
                   mode48,
                   mode49,
                   mode50,
                   mode51,
                   mode52]

    remaining_disco_modes = disco_modes.copy()

    while disco_thread == me:
        new_mode_num = random.randint(0, len(remaining_disco_modes) - 1)
        new_mode = remaining_disco_modes[new_mode_num]
        print("selected new disco mode {} from {} possibilities".format(new_mode, len(remaining_disco_modes)))

        remaining_disco_modes.remove(new_mode)

        if remaining_disco_modes == []:
            remaining_disco_modes = disco_modes.copy()

        time.sleep(180)

    print("ended disco manager")


def mode27():
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    theta = 0

    pixel_pos = generate_pixel_pos()

    k1 = random.random()*2 + 0.7

    hue = random.random()
    rgb = hsv_to_neo_rgb(hue)

    compl_hue = (hue+0.5) % 1.0
    compl_rgb = hsv_to_neo_rgb(compl_hue, v=0.3 + random.random() * 0.7)

    num_first = random.randint(1,2)
    num_extra = random.randint(num_first,5)

    timescale = random.random()

    while not new_mode:

        theta = (time.time() % 3600.0) * (timescale * 10 + 10)

        pixels.fill( (0,0,0) )
        x = math.cos(theta*k1) * 3.5
        y = math.sin(theta) * 3.5

        s = distances_from_point(x, y, pixel_pos=pixel_pos)

        for n in range(0, num_first):
            (d, p) = s[n]
            pixels[p] = rgb

        for n in range(num_first, num_extra):
            (d, p) = s[n]
            pixels[p] = compl_rgb

        pixels.show()
        # time.sleep(0.001)



def mode40():
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    theta = 0

    pixel_pos = generate_pixel_pos()

    k1 = random.random()*2 + 0.7

    hue = random.random()
    rgb = hsv_to_neo_rgb(hue)

    compl_hue = (hue+0.5) % 1.0
    compl_rgb = hsv_to_neo_rgb(compl_hue, v=0.3 + random.random() * 0.7)

    num_first = 1 # random.randint(1,2)
    num_extra = num_first # random.randint(num_first,5)

    timescale = random.random() + 1

    star_factor = random.random() * 5 + 2

    while not new_mode:

        theta = (time.time() % 3600.0) * (timescale * 10 + 10)

        pixels.fill( (0,0,0) )

        scale_r = 4

        r = math.cos(theta * star_factor) * scale_r/2.5 + scale_r/2.0 + 0.5

        x = math.cos(theta) * r
        y = math.sin(theta) * r

        s = distances_from_point(x, y, pixel_pos = pixel_pos)

        for n in range(0, num_first):
            (d, p) = s[n]
            pixels[p] = rgb

        for n in range(num_first, num_extra):
            (d, p) = s[n]
            pixels[p] = compl_rgb

        pixels.show()
        # time.sleep(0.001)


def mode28():
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    hue = random.random()

    h = 0

    rot = random.random()
    rot_speed = 0.001 * random.random()

    while not new_mode:

        pixel_pos = generate_pixel_pos(rot=rot)

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 5.0)

            pixels[p] = hsv_to_neo_rgb(hue, v = d)

   
        pixels.show()

        h = min(4, max(-4, h + random.random() - 0.5))

        rot = (rot + rot_speed) % 1.0


def mode30():
    """This could be merged with mode28 because only hue
    choice differs"""
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    hue1 = random.random()

    # make the 2nd hue is at least 0.15 away in both directions
    hue2 = (hue1 + 0.15 + random.random()*0.7) % 1.0

    h = 0

    pixel_pos = generate_pixel_pos()

    while not new_mode:

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 5.0)

            if y > h:
                hue = hue1
            else:
                hue = hue2

            pixels[p] = hsv_to_neo_rgb(hue, v = d)

   
        pixels.show()

        h = min(4, max(-4, h + random.random() - 0.5))
        if h == 4:  # hue1 is invisible, pick new
            hue1 = (hue2 + 0.15 + random.random()*0.7) % 1.0
        if h == -4: # hue2 is invisible, pick new
            hue2 = (hue1 + 0.15 + random.random()*0.7) % 1.0


def mode32():
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    ro = random.random()
    bo = random.random()
    go = random.random()

    while not new_mode:
        for p in range(0,50):
            theta = p/50.0 * tau
            r = int(128 + 127 * math.sin(ro + theta))
            g = int(128 + 127 * math.sin(bo + theta * 1.1))
            b = int(128 + 127 * math.sin(go + theta * (-1.06)))
            pixels[p] = (r, g, b) 
            ro = (ro + 0.0013) % tau
            go = (go + 0.0011) % tau
            bo = (bo + 0.0009) % tau
        pixels.show()
        time.sleep(0.05)


def mode33():
  
  global new_mode
  pixels.auto_write = False
  pixels.fill( (0,0,0) )
  pixels.show()


  while not new_mode:

    r_ang = random.random()
    g_ang = random.random()
    b_ang = random.random()

    r_width = random.random() * 0.15 + 0.05
    g_width = random.random() * 0.15 + 0.05
    b_width = random.random() * 0.15 + 0.05

    for pixel in range(0,50):
      (b, frac) = pixel_to_layer(pixel)
      frac_red = (frac + r_ang) % 1
      frac_green = (frac + g_ang) % 1
      frac_blue = (frac + b_ang) % 1

      def f(pos, width):
        if pos > width and pos < (1-width):
            intensity = 0
        elif pos >= (1-width):
            pos = 1 - pos
            intensity = (width - pos) * (1/width)
        else:
            intensity = (width - pos) * (1/width)
        return int(intensity * 255)

      pixels[pixel] = ( f(frac_red, r_width), f(frac_green, g_width), f(frac_blue, b_width) )
    pixels.show()
    time.sleep(0.1)
     

def mode34():
  
  global new_mode
  pixels.auto_write = False
  pixels.fill( (0,0,0) )
  pixels.show()

  r_ang = random.random()
  g_ang = random.random()
  b_ang = random.random()

  r_speed = random.random() * 0.05 - 0.025
  g_speed = random.random() * 0.05 - 0.025
  b_speed = random.random() * 0.05 - 0.025

  while not new_mode:

    for pixel in range(0,50):
      (b, frac) = pixel_to_layer(pixel)
      frac_red = (frac + r_ang) % 1
      frac_green = (frac + g_ang) % 1
      frac_blue = (frac + b_ang) % 1

      width = 0.15

      def f(pos):
        if pos > width and pos < (1-width):
            intensity = 0
        elif pos >= (1-width):
            pos = 1 - pos
            intensity = (width - pos) * (1/width)
        else:
            intensity = (width - pos) * (1/width)
        return int(intensity * 255)

      pixels[pixel] = ( f(frac_red), f(frac_green), f(frac_blue) )
    pixels.show()

    r_ang = (r_ang + r_speed) % 1.0
    g_ang = (g_ang + g_speed) % 1.0
    b_ang = (b_ang + b_speed) % 1.0

    time.sleep(0.05)


def mode36():
    global new_mode
    pixels.auto_write = False

    rot = 0

    hue_1 = random.random()
    hue_2 = random.random()
    hue_3 = random.random()

    hue_speed_1 = random.random() * 0.01
    hue_speed_2 = random.random() * 0.01
    hue_speed_3 = random.random() * 0.01

    while not new_mode:
      for pixel in range(0,50):
        (b, pixel_rot) = pixel_to_layer(pixel)

        v_frac = float(b) / float(len(bottoms))

        frac = (pixel_rot + rot) % 1.0

        if frac < 1.0/6.0:
            (h, v) = (0,0)
        elif frac < 2.0/6.0:
            (h, v) = (hue_1, v_frac)
        elif frac < 3.0/6.0:
            (h, v) = (0,0)
        elif frac < 4.0/6.0:
            (h, v) = (hue_2, v_frac)
        elif frac < 5.0/6.0:
            (h, v) = (0,0)
        else:
            (h, v) = (hue_3, v_frac)

        pixels[pixel] = hsv_to_neo_rgb(h, v=v)

      pixels.show()

      rot = rot + 0.025

      hue_1 = (hue_1 + hue_speed_1) % 1.0
      hue_2 = (hue_2 + hue_speed_2) % 1.0
      hue_3 = (hue_3 + hue_speed_3) % 1.0

      time.sleep(0.025)


def mode38():
    global new_mode
    pixels.auto_write = False

    rot = 0

    hue_1 = random.random()
    hue_2 = random.random()
    hue_3 = random.random()

    hue_speed_1 = random.random() * 0.01
    hue_speed_2 = random.random() * 0.01
    hue_speed_3 = random.random() * 0.01

    while not new_mode:
      for pixel in range(0,50):
        (b, pixel_rot) = pixel_to_layer(pixel)

        v_frac = float(b) / float(len(bottoms))

        frac = (pixel_rot + rot + v_frac / 1.5) % 1.0

        if frac < 2.0/6.0:
            (h, v) = (hue_1, v_frac)
        elif frac < 4.0/6.0:
            (h, v) = (hue_2, v_frac)
        else:
            (h, v) = (hue_3, v_frac)

        pixels[pixel] = hsv_to_neo_rgb(h, v=v)

      pixels.show()

      rot = rot + 0.025

      hue_1 = (hue_1 + hue_speed_1) % 1.0
      hue_2 = (hue_2 + hue_speed_2) % 1.0
      hue_3 = (hue_3 + hue_speed_3) % 1.0

      time.sleep(0.025)


def mode39():
    global new_mode
    pixels.auto_write = False

    rot = 0

    hue_1 = random.random()
    hue_2 = random.random()
    hue_3 = random.random()

    hue_speed_1 = random.random() * 0.01
    hue_speed_2 = random.random() * 0.01
    hue_speed_3 = random.random() * 0.01

    while not new_mode:
      for pixel in range(0,50):
        (b, pixel_rot) = pixel_to_layer(pixel)

        v_frac = float(b) / float(len(bottoms))

        frac = (pixel_rot + rot) % 1.0

        if frac < 2.0/6.0:
            k = 1 - frac / (2.0/6.0)
            (h, v) = (hue_1, v_frac * k)
        elif frac < 4.0/6.0:
            k = 1- (frac - 2.0/6.0) / (2.0/6.0)
            (h, v) = (hue_2, v_frac * k)
        else:
            k = 1- (frac - 4.0/6.0) / (2.0/6.0)
            (h, v) = (hue_3, v_frac * k)

        pixels[pixel] = hsv_to_neo_rgb(h, v=v)

      pixels.show()

      rot = rot + 0.025

      hue_1 = (hue_1 + hue_speed_1) % 1.0
      hue_2 = (hue_2 + hue_speed_2) % 1.0
      hue_3 = (hue_3 + hue_speed_3) % 1.0

      time.sleep(0.025)




def mode37():
    global new_mode
    pixels.auto_write = False
    while not new_mode:

        for pixel in range(0,50):

            intensity = pixel / 50.0

            v = scale(gamma(intensity, gamma_factor=4))

            pixels[pixel] = (v,v,v) 

        pixels.show()
        time.sleep(1)


def mode41():

    global new_mode
    pixels.auto_write = False

    h = 0.5

    hue = random.random()

    rot = random.random()
    rot_speed = random.random() * 0.05 + 0.025

    while not new_mode:
        pixel_pos = generate_pixel_pos(rot=rot)

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 2.0)

            pixels[p] = hsv_to_neo_rgb(hue, v = (1-d))
        pixels.show()

        rot = (rot + rot_speed) % 1.0
        time.sleep(0.05)
 

def mode42():

    global new_mode
    pixels.auto_write = False

    h = 0.5


    rot = 0
    rot_speed = 0

    while not new_mode:
        hue = random.random()
        h = random.random() * 8.0 - 4.0
        pixel_pos = generate_pixel_pos(rot=rot)

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 2.0)

            pixels[p] = hsv_to_neo_rgb(hue, v = (1-d))
        pixels.show()

        rot = (rot + rot_speed) % 1.0
        time.sleep(0.05)


def mode43():

    global new_mode
    pixels.auto_write = False

    h = 0.5

    display_pixels = [None for n in range(0,50)]

    rot = 0
    rot_speed = 0

    hue0 = random.random()
    hue1 = (hue0 + 0.333) % 1.0
    hue2 = (hue1 + 0.333) % 1.0

    while not new_mode:
        skip = False
        pos = random.randint(0,12)
        if pos == 0:
          h = 3
          hue = hue0
        elif pos == 1:
          h = 0
          hue = hue1
        elif pos == 2:
          h = -3
          hue = hue2
        else:
          skip = True

        if not skip:
          pixel_pos = generate_pixel_pos(rot=rot)

          for p in range(0,50):
              (x, y) = pixel_pos[p]

              d = min(1, abs(y - h) / 2.0)

              v = 1-d
              if v > 0:
                display_pixels[p] = (hue, v)

        render_hv_fadepixel(pixels, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.05)

        rot = (rot + rot_speed) % 1.0
        time.sleep(0.05)


def mode44():
    global new_mode
    pixels.auto_write = False

    n = 4

    base_hue = random.random()

    # (x,y,hue, count, xv, yv)
    state = [(random.random()*8.0 - 4.0, random.random()*8.0 - 4.0, base_hue + float(i) / float(n), 7, random.random(), random.random()) for i in range(0,n)]

    pixel_pos = generate_pixel_pos()

    while not new_mode:
        pixels.fill( (0, 0, 0) )
        used_pixels = []

        for (x,y,hue,count,xv,yv) in state:
       

          s = distances_from_point(x, y, pixel_pos = pixel_pos)

          def snd(t):
            (a, b) = t
            return b

          s = [e for e in s if snd(e) not in used_pixels]

          # print("count = {}".format(count))
          for p in range(0, count):
            (d, pix) = s[p]
            # print("pixel = {}".format(pix))
            pixels[pix] = hsv_to_neo_rgb(hue)
            used_pixels.append(pix)

        # print("used_pixels = {}".format(used_pixels))
        pixels.show()


        for target in range(0, n):
          (x,y,hue,count,xv,yv) = state[target]

          v_k = 0.2
          new_x = x + xv * v_k
          new_y = y + yv * v_k

          if new_x > 5 or new_x < -5:
              new_x = x
              xv = -xv

          if new_y > 5 or new_y < -5:
              new_y = y
              yv = -yv

          state[target] = (new_x, new_y, hue, count, xv, yv)

        time.sleep(0.02)


def mode49():
    global new_mode
    pixels.auto_write = False

    display_pixels = [None for pixel in range(0,50)]

    n = 4

    base_hue = random.random()

    # (x,y,hue, count, xv, yv)
    state = [(random.random()*8.0 - 4.0, random.random()*8.0 - 4.0, base_hue + float(i) / float(n), 7, random.random(), random.random()) for i in range(0,n)]

    pixel_pos = generate_pixel_pos()

    while not new_mode:
        pixels.fill( (0, 0, 0) )
        used_pixels = []

        for (x,y,hue,count,xv,yv) in state:

          s = distances_from_point(x, y, pixel_pos = pixel_pos)

          def snd(t):
            (a, b) = t
            return b

          s = [e for e in s if snd(e) not in used_pixels]

          for p in range(0, count):
            (d, pix) = s[p]
            display_pixels[pix] = (hue, 1.0 - min(1.0, d/8.0))
            used_pixels.append(pix)

        render_hv_fadepixel(pixel, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.05)

        for target in range(0, n):
          (x,y,hue,count,xv,yv) = state[target]

          v_k = 0.2
          new_x = x + xv * v_k
          new_y = y + yv * v_k

          if new_x > 5 or new_x < -5:
              new_x = x
              xv = -xv

          if new_y > 5 or new_y < -5:
              new_y = y
              yv = -yv

          state[target] = (new_x, new_y, hue, count, xv, yv)

        time.sleep(0.02)


def mode45():
    parameterised_rgb_swirl(delay=0.02, k_step=0.002, active_blue=True)

def mode46():
    parameterised_rgb_swirl(delay=0, k_step=0.02, active_blue=False)

def parameterised_rgb_swirl(*, delay, k_step, active_blue):
    global new_mode
    pixels.auto_write = False

    k = 0

    pixel_pos = generate_pixel_pos()

    while not new_mode:

        for p in range(0,50):

            (b, frac) = pixel_to_layer(p)

            red = scale(gamma(0.5 + 0.5 * math.sin(k*1.1 + tau * float(b) / float(len(bottoms)-1))))

            b_prop = float(b) / float(len(bottoms) - 1)
            v1 = b_prop * (0.5 + 0.5 * math.sin(k*1.2 + tau * frac))
            v2 = 1 - b_prop
            fade_frac = 0.5 + 0.5 * math.sin(k/5.0)
            val = fade_frac * v1 + (1-fade_frac) * v2
            green = scale(gamma( val ))

            if active_blue:
                (x,y) = pixel_pos[p]
                blue = scale(gamma(0.5 + 0.25 * math.sin(k*1.4 + 1.5 * tau * (y + 6.0) / 12.0) + 0.25 * math.sin(k*1.3 + 1.5 * tau * (x + 6.0) / 12.0)))
            else:
                blue = 0

            pixels[p] = (red, green, blue)

        k = k + k_step
        pixels.show()
        time.sleep(delay)


def mode47():
    global new_mode
    pixels.auto_write = False

    k = 0
    k_step = 0.1
    delay = 0

    k_scale_1 = 1 + random.random()
    k_scale_2 = 1 + random.random()
    k_scale_3 = 1 + random.random()

    pixel_pos = generate_pixel_pos()

    while not new_mode:

        for p in range(0,50):

            (b, frac) = pixel_to_layer(p)
            (x, y) = pixel_pos[p]

            red = scale(gamma(0.5 + 0.5 * math.sin(k + x)))
            green = scale(gamma(0.5 + 0.5 * math.sin(k*k_scale_1 + x)))
            blue = scale(gamma(0.5 + 0.5 * math.sin(k*k_scale_2 + x)))

            pixels[p] = (red, green, blue)

        k = k + k_step
        pixels.show()
        time.sleep(delay)


def mode48():
    global new_mode
    pixels.auto_write = False

    k = float(random.randint(0,100)) # 100 is just some arbitrary max... would be better to work out where the three phase contacts co-incide again and use that range (and mod it there for better precision in the loop too)
    k_step = 0.5
    delay = 0.02

    pixel_pos = generate_pixel_pos()

    def f(x):
      x = x / 5.0
      x = x % 4.0

      if x>1.0:
          return 0
      elif x>0.5:  # x = 0.5 .. 1.0
          return 0.5 - (x - 0.5)
      else: # x = 0 .. 0.5
          return x

    ang1 = random.random() * tau
    ang2 = (ang1 + tau / 3.0) % tau
    ang3 = (ang2 + tau / 3.0) % tau

    while not new_mode:

        for p in range(0,50):

            (b, frac) = pixel_to_layer(p)
            (x, y) = pixel_pos[p]

            red = scale(gamma( f(k * 1.03 + x * math.sin(ang1) + y*math.cos(ang1) )))
            green = scale(gamma( f(k * 1.07 + x * math.sin(ang2) + y * math.cos(ang2))))
            blue = scale(gamma( f(k * 1.11 + x * math.sin(ang3) + y * math.cos(ang3))))

            pixels[p] = (red, green, blue)

        k = k + k_step
        pixels.show()
        time.sleep(delay)


def mode50():
    global new_mode
    pixels.auto_write = False

    pixel_pos = generate_pixel_pos()

    while not new_mode:

      hue = random.random()

      x = random.random() * 6 - 3
      y = random.random() * 6 - 3

      for p in range(0,50):

        (x1, y1) = pixel_pos[p]

        d = math.sqrt( (x1 - x) ** 2 + (y1 - y) ** 2)

        v = 1-min(1,d/5.0)

        pixels[p] = hsv_to_neo_rgb(hue, v=v)

      pixels.show()
      time.sleep(0.3)


def mode51():
    global new_mode
    pixels.auto_write = False

    display_pixels = [None for pixel in range(0,50)]

    pixel_pos = generate_pixel_pos()

    while not new_mode:

      hue = random.random()
 
      (x, y) = random_in_radius(5)

      for p in range(0,50):

        (x1, y1) = pixel_pos[p]

        d = math.sqrt( (x1 - x) ** 2 + (y1 - y) ** 2)

        v = 1-min(1,math.sqrt(d)/2.5)

        opix = display_pixels[p]
        if opix is None: 
          display_pixels[p] = (hue, v)
        else:
          (oh, ov) = display_pixels[p]
          if v > ov:
            display_pixels[p] = (hue, v)

      render_hv_fadepixel(pixels, display_pixels)
      fade_hv_fadepixel(display_pixels, 0.05)

      time.sleep(0.05)


def random_in_radius(r):
    """Pick a random point inside the radius r circle"""
    while True:

      x = random.random() * 2*r - r
      y = random.random() * 2*r - r

      if math.sqrt(x ** 2 + y **2) <= r **2:
        return (x,y)


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


def render_hv_fadepixel(pixels, display_pixels):
    """Renders a list of (hue, value) tuples in display_pixels
    onto the pixels"""

    for pixel in range(0,50):
        if display_pixels[pixel] is None:
            pixels[pixel] = (0,0,0)
        else:
            (hue_dp, value_dp) = display_pixels[pixel]
            pixels[pixel] = hsv_to_neo_rgb(hue_dp, v=value_dp)

    pixels.show()


def fade_hv_fadepixel(display_pixels, amount):

      for pixel in range(0,50):
          if display_pixels[pixel] is not None:
            (display_hue, value) = display_pixels[pixel]
            new_value = value - amount
            if new_value <= 0:
              display_pixels[pixel] = None
            else:
              display_pixels[pixel] = (display_hue, new_value)



def mode52():
    global new_mode
    pixels.auto_write = False

    pixel_pos = generate_pixel_pos()

    centre_info = []

    for centres in range(0,3):
      (x,y) = random_in_radius(4)
      hue = random.random()

      centre_info.append( (x, y, hue, 1.0) )

    while not new_mode:

      display_pixels = [None for pixel in range(0,50)]

      for (x,y,hue,intensity) in centre_info:

        for p in range(0,50):

          (x1, y1) = pixel_pos[p]

          d = math.sqrt( (x1 - x) ** 2 + (y1 - y) ** 2)

          v = 1-min(1,math.sqrt(d)/2.5)
          v *= intensity

          opix = display_pixels[p]
          if opix is None: 
            display_pixels[p] = (hue, v)
          else:
            (oh, ov) = display_pixels[p]
            if v > ov:
              display_pixels[p] = (hue, v)

      render_hv_fadepixel(pixels, display_pixels)


      # i think this fading is unnecessary for this particular mode
      # because all the fading is done by the centre_info intensity
      # value and display_pixels is regerenated each frame...
      fade_hv_fadepixel(display_pixels, 0.05)

      (ox, oy, ohue, ointensity) = centre_info[0]
      new_intensity = max(0, ointensity - 0.05)
      if new_intensity > 0:
        centre_info[0] = (ox, oy, ohue, new_intensity)
      else:
        del centre_info[0]

        (x,y) = random_in_radius(4)
        hue = random.random()
        centre_info.append( (x, y, hue, 1.0) )

      time.sleep(0.05)



new_mode = mode32


app = flask.Flask(__name__)

@app.route('/')
def index_page():
    return flask.send_file("./index.html")

@app.route('/mode/1')
def set_mode1():
    global new_mode
    new_mode = mode1
    return flask.redirect("/", code=302)

@app.route('/mode/2')
def set_mode2():
    global new_mode
    new_mode = mode2
    return flask.redirect("/", code=302)

@app.route('/mode/3')
def set_mode3():
    global new_mode
    new_mode = mode3
    return flask.redirect("/", code=302)

@app.route('/mode/4')
def set_mode4():
    global new_mode
    new_mode = mode4
    return flask.redirect("/", code=302)

@app.route('/mode/5')
def set_mode5():
    global new_mode
    new_mode = mode5
    return flask.redirect("/", code=302)

@app.route('/mode/6')
def set_mode6():
    global new_mode
    new_mode = mode6
    return flask.redirect("/", code=302)

@app.route('/mode/7')
def set_mode7():
    global new_mode
    new_mode = mode7
    return flask.redirect("/", code=302)


@app.route('/mode/8')
def set_mode8():
    global new_mode
    new_mode = mode8
    return flask.redirect("/", code=302)

@app.route('/mode/9')
def set_mode9():
    global new_mode
    new_mode = mode9
    return flask.redirect("/", code=302)


@app.route('/mode/10')
def set_mode10():
    global new_mode
    new_mode = mode10
    return flask.redirect("/", code=302)


@app.route('/mode/11')
def set_mode11():
    global new_mode
    new_mode = mode11
    return flask.redirect("/", code=302)


@app.route('/mode/12')
def set_mode12():
    global new_mode
    new_mode = mode12
    return flask.redirect("/", code=302)


@app.route('/mode/13')
def set_mode13():
    global new_mode
    new_mode = mode13
    return flask.redirect("/", code=302)


@app.route('/mode/14')
def set_mode14():
    global new_mode
    new_mode = mode14
    return flask.redirect("/", code=302)


@app.route('/mode/15')
def set_mode15():
    global new_mode
    new_mode = mode15
    return flask.redirect("/", code=302)


@app.route('/mode/16')
def set_mode16():
    global new_mode
    new_mode = mode16
    return flask.redirect("/", code=302)


@app.route('/mode/17')
def set_mode17():
    global new_mode
    new_mode = mode17
    return flask.redirect("/", code=302)


@app.route('/mode/18')
def set_mode18():
    global new_mode
    new_mode = mode18
    return flask.redirect("/", code=302)


@app.route('/mode/19')
def set_mode19():
    global new_mode
    new_mode = mode19
    return flask.redirect("/", code=302)


@app.route('/mode/20')
def set_mode20():
    global new_mode
    new_mode = mode20
    return flask.redirect("/", code=302)


@app.route('/mode/21')
def set_mode21():
    global new_mode
    new_mode = mode21
    return flask.redirect("/", code=302)


@app.route('/mode/22')
def set_mode22():
    global new_mode
    new_mode = mode22
    return flask.redirect("/", code=302)


@app.route('/mode/23')
def set_mode23():
    global new_mode
    new_mode = mode23
    return flask.redirect("/", code=302)


@app.route('/mode/24')
def set_mode24():
    global new_mode
    new_mode = mode24
    return flask.redirect("/", code=302)


@app.route('/mode/25')
def set_mode25():
    global new_mode
    new_mode = mode25
    return flask.redirect("/", code=302)


@app.route('/mode/26')
def set_mode26():
    global new_mode
    new_mode = mode26
    return flask.redirect("/", code=302)


@app.route('/mode/27')
def set_mode27():
    global new_mode
    new_mode = mode27
    return flask.redirect("/", code=302)


@app.route('/mode/28')
def set_mode28():
    global new_mode
    new_mode = mode28
    return flask.redirect("/", code=302)


@app.route('/mode/30')
def set_mode30():
    global new_mode
    new_mode = mode30
    return flask.redirect("/", code=302)


@app.route('/mode/31')
def set_mode31():
    global new_mode
    new_mode = mode31
    return flask.redirect("/", code=302)


@app.route('/mode/32')
def set_mode32():
    global new_mode
    new_mode = mode32
    return flask.redirect("/", code=302)


@app.route('/mode/33')
def set_mode33():
    global new_mode
    new_mode = mode33
    return flask.redirect("/", code=302)


@app.route('/mode/34')
def set_mode34():
    global new_mode
    new_mode = mode34
    return flask.redirect("/", code=302)


@app.route('/mode/35')
def set_mode35():
    global new_mode
    new_mode = mode35
    return flask.redirect("/", code=302)


@app.route('/mode/36')
def set_mode36():
    global new_mode
    new_mode = mode36
    return flask.redirect("/", code=302)


@app.route('/mode/38')
def set_mode38():
    global new_mode
    new_mode = mode38
    return flask.redirect("/", code=302)


@app.route('/mode/39')
def set_mode39():
    global new_mode
    new_mode = mode39
    return flask.redirect("/", code=302)


@app.route('/mode/37')
def set_mode37():
    global new_mode
    new_mode = mode37
    return flask.redirect("/", code=302)


@app.route('/mode/40')
def set_mode40():
    global new_mode
    new_mode = mode40
    return flask.redirect("/", code=302)


@app.route('/mode/41')
def set_mode41():
    global new_mode
    new_mode = mode41
    return flask.redirect("/", code=302)


@app.route('/mode/42')
def set_mode42():
    global new_mode
    new_mode = mode42
    return flask.redirect("/", code=302)


@app.route('/mode/43')
def set_mode43():
    global new_mode
    new_mode = mode43
    return flask.redirect("/", code=302)


@app.route('/mode/44')
def set_mode44():
    global new_mode
    new_mode = mode44
    return flask.redirect("/", code=302)


@app.route('/mode/45')
def set_mode45():
    global new_mode
    new_mode = mode45
    return flask.redirect("/", code=302)


@app.route('/mode/46')
def set_mode46():
    global new_mode
    new_mode = mode46
    return flask.redirect("/", code=302)


@app.route('/mode/47')
def set_mode47():
    global new_mode
    new_mode = mode47
    return flask.redirect("/", code=302)


@app.route('/mode/48')
def set_mode48():
    global new_mode
    new_mode = mode48
    return flask.redirect("/", code=302)


@app.route('/mode/49')
def set_mode49():
    global new_mode
    new_mode = mode49
    return flask.redirect("/", code=302)


@app.route('/mode/50')
def set_mode50():
    global new_mode
    new_mode = mode50
    return flask.redirect("/", code=302)


@app.route('/mode/51')
def set_mode51():
    global new_mode
    new_mode = mode51
    return flask.redirect("/", code=302)


@app.route('/mode/52')
def set_mode52():
    global new_mode
    new_mode = mode52
    return flask.redirect("/", code=302)


@app.route('/disco/on')
def disco_on():
    global disco_thread
    if not disco_thread:
        disco_thread = threading.Thread(target=disco_manager)
        disco_thread.start()
    return flask.redirect("/", code=302)


@app.route('/disco/off')
def disco_off():
    global disco_thread
    disco_thread = None
    return flask.redirect("/", code=302)


def go():
    global new_mode
    while True:
        if new_mode:
            print("new mode: {}".format(new_mode))
            m = new_mode
            new_mode = None
            m()

threading.Thread(target=go).start()
