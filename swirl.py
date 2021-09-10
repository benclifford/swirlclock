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

import randomwalk

from functools import partial
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


def different_hue(hue):
    """Returns a hue that is noticeably different than the
    input hue."""
    return (hue + 0.15 + random.random()*0.7) % 1.0


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
    pmode_solid( (255, 0, 32) )


def mode6():
    pmode_solid( (0, 0, 0) )

def mode62():
    pmode_solid( hsv_to_neo_rgb(random.random()) )

def pmode_solid(rgb):

    global new_mode
    pixels.auto_write = True
    
    while not new_mode:
        pixels.fill( rgb )
        time.sleep(0.2)


def mode31():
    global new_mode
    pixels.auto_write = False

    hue = random.random()

    brightness = []

    rw = randomwalk.randomwalk(low = 0.1, high = 1.0)

    for p in range(0,50):
        brightness.append(next(rw))

    while not new_mode:
        for p in range(0,50):
            pixels[p] = hsv_to_neo_rgb(hue, s=0.75, v=brightness[p]) 
        pixels.show()

        # rotate through all hues every 3 hours
        hue = (hue + 1.0 / (3.0 * 60.0 * 60.0) ) % 1.0
        time.sleep(0.5)


def mode76():
  global new_mode
  pixels.auto_write = False
  angle = random.random()
  radius = 0

  while not new_mode:
    pixels.fill( (0,0,0) )
    print(f"radius {radius}")
    b1 = bottoms[radius] - 1
    b2 = bottoms[radius + 1]
    pix = int(b1 + (b2-b1)*angle)
    print(f"pixel {pix}")
    pixels[pix] = (255,255,255) 

    radius += 1
    if radius >= 5: # TODO wrt len of bottoms
      radius = 0
      angle = random.random()

    pixels.show()
    time.sleep(0.03)


def mode77():
  global new_mode
  pixels.auto_write = False
  angle = random.random()
  radius = 0

  while not new_mode:
    pixels.fill( (0,0,0) )
    print(f"radius {radius}")
    b1 = bottoms[radius] - 1
    b2 = bottoms[radius + 1]
    pix = int(b1 + (b2-b1)*angle)
    print(f"pixel {pix}")
    pixels[pix] = (255,255,255) 

    radius += 1
    if radius >= 5: # TODO wrt len of bottoms
      radius = 0
      angle += 0.03
      angle %= 1.0

    pixels.show()
    time.sleep(0.03)


def mode78():
  global new_mode
  pixels.auto_write = False
  angle = random.random()
  radius = 0

  while not new_mode:
    pixels.fill( (0,0,0) )
    print(f"radius {radius}")
    b1 = bottoms[radius] - 1
    b2 = bottoms[radius + 1]
    pix = int(b1 + (b2-b1)*angle)
    print(f"pixel {pix}")
    hue = (angle + radius / 5.0 / 3.0) % 1.0
    pixels[pix] = hsv_to_neo_rgb(hue) 

    radius += 1
    if radius >= 5: # TODO wrt len of bottoms
      radius = 0
      angle = random.random()

    pixels.show()
    time.sleep(0.03)


def mode79():
  global new_mode
  pixels.auto_write = False
  hue = random.random()
  rgb = hsv_to_neo_rgb(hue) 

  while not new_mode:
    pixels.fill( (0,0,0) )
    for p in range(0,50):
      if random.random() > 0.5:
          pixels[p] = rgb
    pixels.show()
    time.sleep(0.03)


def mode80():
  global new_mode
  pixels.auto_write = False
  hue = random.random()
  rgb = hsv_to_neo_rgb(hue) 
  contr_rgb = hsv_to_neo_rgb((hue + 0.5)%1.0) 

  while not new_mode:
    pixels.fill( (0,0,0) )
    for p in range(0,50):
      r = random.random()
      if r > 0.95:
          pixels[p] = contr_rgb
      elif r > 0.5: 
          pixels[p] = rgb
    pixels.show()
    time.sleep(0.03)



def mode56():
  global new_mode
  pixels.auto_write = False

  while not new_mode:
    hue = random.random()

    brightness = []

    # slight bias dimmer - the visual effect is pretty
    # sensitive to the bias amount
    rw = randomwalk.randomwalk(low = 0.1, high = 1.0, bias = -0.03)

    for p in range(0,50):
        brightness.append(next(rw))

    for p in range(0,50):
        pixels[p] = hsv_to_neo_rgb(hue, s=0.75, v=brightness[p]) 
    pixels.show()

        # rotate through all hues every 3 hours
        # hue = (hue + 1.0 / (3.0 * 60.0 * 60.0) ) % 1.0
    time.sleep(0.3)


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
    pmode_rotator()

def mode12():
    pmode_rotator(spin_speed = 1.0 / 60.0)

def mode71():
    pmode_rotator(spin_speed = 1.0 / 6.0)

def pmode_rotator(spin_speed = 1.0/600.0):

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

      offset = (offset + spin_speed / 5.0) % 1.0

      time.sleep(0.02)

def mode75():
    global new_mode
    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    # spin_speed = 1.0/60.0
    offset = 0
    target_offset = offset

    window = 0.33
    target_window = window

    window_dir = 0
    target_window_dir = window_dir

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

        if (proportion_around_loop + window_dir) % 1.0 > window:
          radial_proportion = 0.0

        pixels[pixel] = hsv_to_neo_rgb(frac, s=radial_proportion, v=radial_proportion)

      pixels.show()

      # offset = (offset + spin_speed / 5.0) % 1.0

      active = False

      if target_offset > offset:
          offset += 0.02
          if target_offset < offset:
            target_offset = offset
          active = True

      if target_offset < offset:
          offset -= 0.02
          if target_offset > offset:
            target_offset = offset
          active = True

      if target_window > window:
          window += 0.02
          if target_window < window:
            target_window = window
          active = True

      if target_window < window:
          window -= 0.02
          if target_window > window:
            target_window = window
          active = True

      if target_window_dir > window_dir:
          window_dir += 0.02
          if target_window_dir < window_dir:
            target_window_dir = window_dir
          active = True

      if target_window_dir < window_dir:
          window_dir -= 0.02
          if target_window_dir > window_dir:
            target_window_dir = window_dir
          active = True


      if not active:
          choice = random.randint(1,3)
          if choice == 1:
            target_offset = offset + random.random() - 0.5
          elif choice == 2:
            target_window = 0.2 + random.random() * 0.4
          elif choice == 3:
            target_window_dir = random.random()
          

      time.sleep(0.02)


def mode72():

    global new_mode

    spin_speed = 1.0 / 6.0

    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    offset = 0
    colour_segs = 1
    colour_shift_rw = randomwalk.randomwalk(low = 0, high = 1.0)

    next_reconfig_time = 0

    while not new_mode:

      if next_reconfig_time < time.time():
        next_reconfig_time = time.time() + 1.0

        old_segs = colour_segs
        while colour_segs == old_segs:
          colour_segs = float(random.randint(2,6))

        colour_shift = next(colour_shift_rw)

        activation_list = [random.random() < 0.8 for n in range(0,50)]

      for pixel in range(0,50):
        (b, proportion_around_loop) = pixel_to_layer(pixel)
        frac = (proportion_around_loop + offset) % 1.0

        frac = int(frac * colour_segs) / colour_segs

        frac = (frac + colour_shift) % 1.0

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

        if activation_list[pixel] and b > 2:
          radial_proportion = 1.0
        else:
          radial_proportion = 0.0
        
        pixels[pixel] = hsv_to_neo_rgb(frac, s=1.0, v=radial_proportion)

      pixels.show()

      offset = (offset + spin_speed / 5.0) % 1.0

      time.sleep(0.02)


def mode73():

    global new_mode


    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    phases = [0.0 for n in range(0,50)]

    while not new_mode:

      for pixel in range(0,50):

        x = math.sin(phases[pixel])

        x = (x / 2.0) + 0.5

        phases[pixel] += 0.04 + (float(pixel) / 50.0 * 0.02)
        
        pixels[pixel] = hsv_to_neo_rgb(0, s=0, v=x)

      pixels.show()

      time.sleep(0.01)


def mode74():

    global new_mode


    pixels.auto_write = False

    pixels.fill( (0,0,0) )
    pixels.show()

    phases = [0.0 for n in range(0,50)]

    while not new_mode:

      for pixel in range(0,50):

        p = phases[pixel]

        if p > 0.85:
          rgb = (0, 255, 0)
        elif p > 0.7: 
          rgb = (255, 0, 0)
        elif p > 0.35: 
          rgb = (1,1,1)
        else:
          rgb = (0,0,0)


        phases[pixel] += 0.04 + (float(pixel) / 50.0 * 0.02)
        phases[pixel] %= 1.0
        
        pixels[pixel] = rgb

      pixels.show()

      time.sleep(0.01)



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


def mode14():
    pmode_dotclock(display_seconds = False)

def mode57():
    pmode_dotclock(display_seconds = True)

def pmode_dotclock(*, display_seconds):
  global new_mode
  pixels.auto_write = False

  while not new_mode:
    pixels.fill( (0,0,0) )
    

    t = time.time()
    frac_sec = t % 1.0
    now = time.localtime(t)
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

    second_pixels = second_pixels[0:10]

    hour_count = 0
    for dot in hour_pixels:
        (distance, pixel) = dot
        factor = hour_count / float(len(hour_pixels))
        pixels[pixel] = (scale(gamma(1.0 - 0.6 * factor)), scale(gamma(0.2 * factor)), scale(gamma(0.2 * factor)))
        hour_count = hour_count + 1.0


    for dot in minute_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (0,0,32)

    for dot in minute_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (0,0,32)

    if display_seconds:
        for dot in second_pixels:
            (distance, pixel) = dot

            # turn frac_sec into a sawtooth wave
            if frac_sec < 0.5:
                intensity = frac_sec
            else:
                intensity = 1.0 - frac_sec

            pixels[pixel] = (0,scale(gamma(0.3 * intensity)),0)

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
    pmode_iterator_spiral(iterator=generate_mode16(), delay=0.05)


def generate_mode16():
    hue = random.random()

    while True:
        hue = (hue + random.random() * 0.1 - 0.05) % 1.0
        yield hsv_to_neo_rgb(hue)


def pmode_iterator_spiral(*, iterator, delay):
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
    pmode_iterator_spiral(iterator=generate_mode35(), delay=0.01)


def generate_mode35():
    hue = random.random()

    rw = randomwalk.randomwalk(low = 0, high = 1.0)

    while True:

        v = next(rw)

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


def mode60():
  """This is a variant of mode20 so TODO refactor?"""
  global new_mode
  pixels.auto_write = False
  display_pixels = [None for n in range(0,50)]

  start_particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
  particle = start_particle
  hue = random.random()

  first = True
  boom = False

  tc = 0.001
  hc = 0.004

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
        new_particle = start_particle
        boom = old_first
        first = True
        pixels.show()
        pixels.fill( (0,0,0) )
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)

    particle = new_particle

    # display state

    display_pixels[particle] = (hue, 1)
    fade_hv_fadepixel(display_pixels, 0.01)
    render_hv_fadepixel(pixels, display_pixels)

    time.sleep(tc)

    hue = (hue + hc) % 1.0

    boom = False

def mode61():
  """another reparameterisation of mode20 - TODO factor?"""
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
        pixels.show()
        time.sleep(0.03)
        pixels.fill( (0,0,0) )
        hue = random.random()
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)

    particle = new_particle

    # display state

    pixels[particle] = hsv_to_neo_rgb(hue)


    boom = False





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

def mode81():
    global new_mode
    pixels.auto_write = False

    display_pixels = [random.random() > 0.5 for n in range(0,50)]

    while not new_mode:
        new_pixels = []
        for p in range(0,50):
           p_left = (p-1)%50
           p_right = (p+1)%50

           c = 0
           if display_pixels[p_left]:
             c += 1
           if display_pixels[p]:
             c += 1
           if display_pixels[p_right]:
             c += 1

           new_pixels.append(c == 1) 

        display_pixels = new_pixels

        for p in range(0,50):
            if display_pixels[p]:
                pixels[p] = (128, 128, 128) 
            else:
                pixels[p] = (2,2,2) 


        pixels.show()
        time.sleep(0.1)

def mode82():
    global new_mode
    pixels.auto_write = False

    display_pixels = []

    for p in range(0,50):
      if random.random() > 0.5:
        display_pixels.append(random.random())
      else:
        display_pixels.append(None)

    while not new_mode:
        new_pixels = []
        for p in range(0,50):
           p_left = (p-1)%50
           p_right = (p+1)%50

           hue = None
           c = 0
           if display_pixels[p_left] is not None:
             c += 1
             hue = display_pixels[p_left]
             if p == 0:  # inject colour change on loop
               hue = (hue + 0.1) % 1.0
           if display_pixels[p] is not None:
             c += 1
             hue = display_pixels[p]
           if display_pixels[p_right] is not None:
             c += 1
             hue = display_pixels[p_right]
             if p == 49:  # inject colour change on loop
               hue = (hue + 0.1) % 1.0

           if c == 1:
               new_pixels.append(hue) 
           else:
               new_pixels.append(None) 

        display_pixels = new_pixels

        for p in range(0,50):
            if display_pixels[p] is not None:
                pixels[p] = hsv_to_neo_rgb(display_pixels[p])
            else:
                pixels[p] = (2,2,2) 


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
        active_pixel = random.randint(0,49)

        # highlight the chosen pixel
        # pixels[active_pixel] = (255,0,0)
        # pixels.show()

        (x,y) = pixel_pos[active_pixel]

        s = distances_from_point(x, y, pixel_pos=pixel_pos)

        ball = [(d, n) for (d,n) in s if d < 1.5]

        # remove self from ball
        ball = [(d, n) for (d,n) in ball if n != active_pixel]

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
            if state[active_pixel] is None:
                iterations_since_last_change += 1
            else:
                iterations_since_last_change = 0
            state[active_pixel] = None
        elif state[active_pixel] is None:
            # turn on
            ball_live = [(d, p) for (d, p) in ball if state[p] is not None]
            if ball_live == []:
                state[active_pixel] = M25_state(random.random())
                iterations_since_last_change = 0
            else:
                hues_live = [state[p1].hue for (d1, p1) in ball_live]
                hues_sorted = sorted(hues_live)
                hues_grouped = [list(it) for (h, it) in itertools.groupby(hues_sorted)]
                hues_counted = [(len(l), l[0]) for l in hues_grouped]
                hues_counted_sorted = sorted(hues_counted)
                (last_count, _) = hues_counted_sorted[0]
                minimal_hues = [hue for (count, hue) in hues_counted_sorted if count == last_count]

                if minimal_hues != []:
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
                   mode52,
                   mode53,
                   mode54,
                   mode56,
                   mode60,
                   mode61,
                   mode63,
                   mode64,
                   mode65,
                   mode66,
                   mode67,
                   mode68,
                   mode69,
                   mode71,
                   mode72,
                   mode73,
                   mode74,
                   mode75,
                   mode76,
                   mode77,
                   mode78,
                   mode79,
                   mode80,
                   mode81,
                   mode82]

    remaining_disco_modes = disco_modes.copy()

    while disco_thread == me:
        new_mode_num = random.randint(0, len(remaining_disco_modes) - 1)
        new_mode = remaining_disco_modes[new_mode_num]
        print("selected new disco mode {} from {} possibilities".format(new_mode, len(remaining_disco_modes)))

        remaining_disco_modes.remove(new_mode)

        if remaining_disco_modes == []:
            remaining_disco_modes = disco_modes.copy()

        time.sleep(60)

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

    star_factor = float(random.randint(1,4)) + random.random() * 0.1

    while not new_mode:

        theta = (time.time() % 3600.0) * (timescale * 10 + 10)

        pixels.fill( (0,0,0) )

        scale_r = 4

        r = math.cos(theta * star_factor) * scale_r/2.5 + scale_r/2.0

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

    rw = randomwalk.randomwalk(low=-4, high=4, spread = 0.5)

    rot = random.random()
    rot_speed = 0.001 * random.random()

    while not new_mode:
        h = next(rw)
        pixel_pos = generate_pixel_pos(rot=rot)

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 5.0)

            pixels[p] = hsv_to_neo_rgb(hue, v = d)

   
        pixels.show()

        rot = (rot + rot_speed) % 1.0


def mode30():
    """This could be merged with mode28 because only hue
    choice differs"""
    global new_mode
    pixels.auto_write = False
    pixels.fill( (0,0,0) )
    pixels.show()

    hue1 = random.random()
    hue2 = different_hue(hue1)

    rw = randomwalk.randomwalk(low = -4, high = 4, spread = 0.5)

    pixel_pos = generate_pixel_pos()

    while not new_mode:
        h = next(rw)

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 5.0)

            if y > h:
                hue = hue1
            else:
                hue = hue2

            pixels[p] = hsv_to_neo_rgb(hue, v = d)

   
        pixels.show()

        if h == 4:  # hue1 is invisible, pick new
            hue1 = different_hue(hue2)
        if h == -4: # hue2 is invisible, pick new
            hue2 = different_hue(hue1)


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

            intensity = 0.25 + 0.75 * pixel / 50.0

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

    pixel_pos = generate_pixel_pos()

    while not new_mode:
        hue = random.random()
        h = random.random() * 8.0 - 4.0

        for p in range(0,50):
            (x, y) = pixel_pos[p]

            d = min(1, abs(y - h) / 2.0)

            pixels[p] = hsv_to_neo_rgb(hue, v = (1-d))
        pixels.show()

        time.sleep(0.05)


def mode43():

    global new_mode
    pixels.auto_write = False

    h = 0.5

    display_pixels = [None for n in range(0,50)]

    hue0 = random.random()
    hue1 = (hue0 + 0.333) % 1.0
    hue2 = (hue1 + 0.333) % 1.0

    pixel_pos = generate_pixel_pos()

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

          for p in range(0,50):
              (x, y) = pixel_pos[p]

              d = min(1, abs(y - h) / 2.0)

              v = 1-d
              if v > 0:
                display_pixels[p] = (hue, v)

        render_hv_fadepixel(pixels, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.05)

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

          for p in range(0, count):
            (d, pix) = s[p]
            pixels[pix] = hsv_to_neo_rgb(hue)
            used_pixels.append(pix)

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

        render_hv_fadepixel(pixels, display_pixels)
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
    pmode_rgb_swirl(delay=0.02, k_step=0.002, active_blue=True)

def mode46():
    pmode_rgb_swirl(delay=0, k_step=0.02, active_blue=False)

def pmode_rgb_swirl(*, delay, k_step, active_blue):
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
    pmode_vertical_prism(k_step = 0.1)


def mode55():
    pmode_vertical_prism(k_step = 0.003)


def pmode_vertical_prism(*, k_step):
    global new_mode
    pixels.auto_write = False

    k = random.random() * tau
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


def mode58():
    global new_mode
    pixels.auto_write = False

    k = float(random.randint(0,100)) # 100 is just some arbitrary max... would be better to work out where the three phase contacts co-incide again and use that range (and mod it there for better precision in the loop too)
    k_step = 0.02
    delay = 0.02

    pixel_pos = generate_pixel_pos()

    def f(x):
      x = x / 5.0
      x = x % 1.5

      if x>1.0:
          return 0
      elif x>0.5:  # x = 0.5 .. 1.0
          return (0.5 - (x - 0.5)) * 2
      else: # x = 0 .. 0.5
          return x*2

    ang1 = random.random() * tau
    ang2 = (ang1 + tau / 3.0) % tau

    while not new_mode:

        for p in range(0,50):

            (b, frac) = pixel_to_layer(p)
            (x, y) = pixel_pos[p]

            red = (( f(k * 0.6123 + x * math.sin(ang1) + y*math.cos(ang1) )))
            green = math.cos(k * 1.1 + tau * math.sqrt( x**2 + (y - 5.0) ** 2) / 25.0) * 0.5 + 0.5
            blue = math.sin(k * 1.54 + p/50.0 * tau) * 0.5 + 0.5

            level = ((red + green + blue) / 3)
            if level < 0.25:
              v = 1.0 - (0.25 - level) * 3
              s = 1.0
            else:
              v = 1.0
              s = 1.0 - (level - 0.25) / 0.75

            pixels[p] = hsv_to_neo_rgb(0.66, s=s, v=v)

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


def mode59():
    global new_mode
    pixels.auto_write = False

    display_pixels = [None for pixel in range(0,50)]

    pixel_pos = generate_pixel_pos()
    ang = tau / 8.0

    while not new_mode:

      hue = random.random()
 
      for p in range(0,50):

        # red bit
        (x1, y1) = pixel_pos[p]

        (b, frac) = pixel_to_layer(p)
        r = abs(math.cos(frac * tau + ang) * 5.0)
        if math.sqrt(x1 ** 2 + y1 ** 2) < r and b >= 2:
            nx = (0, 1 - abs(b - 3.0)/ 3.0)
        else:
            nx = None
 
        # green bit
        green_width = 2.0
        d = abs(x1-y1)
        if d < green_width and y1 < 0 and nx is None and random.random() > 0.9:
            nx = (0.3333, 1.0 - d/green_width)


        if nx is not None:
            (hue, v) = nx
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
      ang = ang + 0.005


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


def mode53():
    global new_mode
    pixels.auto_write = False
    
    display_pixels = [None for pixel in range(0,50)]

    hue = random.random()

    while not new_mode:

        display_pixels[random.randint(0, 49)] = (hue, 1)

        render_hv_fadepixel(pixels, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.05)

        time.sleep(0.05)

        hue = (hue + 0.005) % 1.0


def mode54():
    global new_mode
    pixels.auto_write = False
    
    pixel_pos = generate_pixel_pos()

    display_pixels = [None for pixel in range(0,50)]

    hue = random.random()
    pixel = random.randint(0, 49)

    while not new_mode:

        display_pixels[pixel] = (hue, 1)

        render_hv_fadepixel(pixels, display_pixels)
        fade_hv_fadepixel(display_pixels, 0.03)

        time.sleep(0.01)

        (x, y) = pixel_pos[pixel]

        candidates = distances_from_point(x, y, pixel_pos = pixel_pos)

        candidates = [(d, n) for (d, n) in candidates if display_pixels[n] is None]

        if candidates != []:
            (least_d, _) = candidates[0]

            candidates = [(d, n) for (d, n) in candidates if d < least_d * 1.25]

            x = random.randint(0, len(candidates) - 1)

            (d, n) = candidates[x]

            pixel = n


def mode63():
    pmode_firefront(hue_step = 0.01)

def mode64():
    pmode_firefront(hue_step = 0)

def mode65():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode65_fire_scheme, hue))

def mode65_fire_scheme(hue, x):
    other_hue = (hue + 0.5) % 1.0
    if x is None:
        return (hue, 1)
    else:
        return (other_hue, 1)

def mode66():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode66_fire_scheme, hue))

def mode66_fire_scheme(hue, x):
    other_hue = (hue + 0.5) % 1.0
    if x is None:
        return (other_hue, 1)
    else:
        (h, v) = x

        return (h, v)


def mode67():
    hue = random.random()
    pmode_firefront(hue_step = 0.01, colour_scheme = partial(mode67_fire_scheme, hue))

def mode67_fire_scheme(hue, x):
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

def mode68_fire_scheme(hue, x):
    if x is None:
        return (0, 0)
    else:
        (h, v) = x
        return (random.random(), v)


def pmode_firefront(*, hue_step, colour_scheme = None):
    global new_mode
    pixels.auto_write = False
    
    pixel_pos = generate_pixel_pos()

    hue = random.random()

    display_pixels = [None for pixel in range(0,50)]

    while not new_mode:

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
              schemed_display_pixels = [colour_scheme(hv) for hv in display_pixels]

          render_hv_fadepixel(pixels, schemed_display_pixels)
          fade_hv_fadepixel(display_pixels, 0.03)
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

def mode69():
    global new_mode
    pixels.auto_write = False

    rw = randomwalk.randomwalk(low = 2, high = 8)

    red1_mod = random.randint(2,5)
    red1_speed = 2 + random.random() * 4

    orange1_speed = 0.5 + random.random()

    while not new_mode:

        gf = next(rw)
        white_centre = []
        for pixel in range(0,50):
            intensity = pixel / 50.0
            v = scale(gamma(intensity, gamma_factor=gf))
            white_centre.append( (v,v,v) )


        red1 = []
        for pixel in range(0,50):
            if pixel % red1_mod == int(time.time() * red1_speed) % red1_mod:
                red1.append( (128,0,0) )
            else:
                red1.append( (0,0,0) )
 
        yellow1 = []
        for pixel in range(0,50):
            if random.random() > 0.90:
                v = int(random.random() * 128)
                yellow1.append( (v,v,0) )
            else:
                yellow1.append( (0,0,0) )
  
        orange1 = []
        for pixel in range(0,50):
            phase = float(pixel) / 50.0 * tau
            phase += (time.time() * orange1_speed) % tau
            v = 0.5 + 0.5 * math.sin(-phase)
            orange1.append( ( int(v * 128), int(v * 48), 0 ) )
                    
        for pixel in range(0,50):
            # pixels[pixel] = orange1[pixel]
            pixels[pixel] = max_pixel(max_pixel(max_pixel(white_centre[pixel], red1[pixel]), yellow1[pixel]), orange1[pixel])

        pixels.show()
        time.sleep(0.02)


def mode70():
    global new_mode
    pixels.auto_write = False

    pixel_pos = generate_pixel_pos()

    # approx times for sunrise/sunset in early May
    sunrise = 5.5
    sunset = 20.43

    while not new_mode:

        t = time.time()
        now = time.localtime(t)
        hour = now.tm_hour
        minute = now.tm_min
        second = now.tm_sec

        h_m = hour + (minute / 60.0) + (second / 60.0 / 60.0)
        print("now h_m = {}".format(h_m))

        if h_m < sunrise:
            print("pre-dawn")
            rgb = (0,0,0)
            for pixel in range(0,50):
                pixels[pixel]=rgb

        elif h_m < (sunrise + 1.0): # rising
            print("sun rising")
            frac = h_m - sunrise
            v = int(255 * frac)
            rgb = (v, v, v)
            for pixel in range(0,50):
                pixels[pixel]=rgb

        elif h_m < sunset:
            print("daytime")
            rgb = (255, 255, 255)
            for pixel in range(0,50):
                pixels[pixel]=rgb

        elif h_m < (sunset + 1.0): # setting
            print("sun setting")
            frac = h_m - sunset
            frac = 1.0 - frac
            for pixel in range(0,50):
                (x, y) = pixel_pos[pixel]
                y_frac = (5 * (frac * 2.0 - 1.0) + y + 5.0) / 10.0
                y_frac = min(y_frac, 1)
                y_frac = max(y_frac, 0)
                p_frac = frac * y_frac
                g_boost = frac
                b_boost = frac * frac
                r = int(255.0 * p_frac)
                g = int(255.0 * p_frac * g_boost)
                b = int(255.0 * p_frac * b_boost)
                rgb = (r, g, b)
                print("rgb = {}".format(rgb)) 
                pixels[pixel]=rgb

        else: # post sunset
            print("night-time")
            rgb = (0,0,0)
            for pixel in range(0,50):
                pixels[pixel]=rgb

        pixels.show()
        time.sleep(1) 


def max_pixel( p1, p2 ):
    (r1, g1, b1) = p1
    (r2, g2, b2) = p2
    return (  max(r1, r2),   max(g1, g2),  max(b1, b2) )



new_mode = mode32


app = flask.Flask(__name__)

@app.route('/')
def index_page():
    return flask.send_file("./index.html")


def set_mode(m):
    global new_mode
    global disco_thread
    disco_thread = None
    new_mode = m
    return flask.redirect("/", code=302)

def declare_mode(name, func):
    p = partial(set_mode, func)
    p.__name__ = "set_" + (func.__name__)
    app.route('/mode/' + name)(p)

declare_mode("1", mode1)
declare_mode("2", mode2)
declare_mode("3", mode3)
declare_mode("4", mode4)
declare_mode("5", mode5)
declare_mode("6", mode6)
declare_mode("7", mode7)
declare_mode("8", mode8)
declare_mode("9", mode9)
declare_mode("10", mode10)
declare_mode("11", mode11)
declare_mode("12", mode12)
declare_mode("13", mode13)
declare_mode("14", mode14)
declare_mode("15", mode15)
declare_mode("16", mode16)
declare_mode("17", mode17)
declare_mode("18", mode18)
declare_mode("19", mode19)
declare_mode("20", mode20)
declare_mode("21", mode21)
declare_mode("22", mode22)
declare_mode("23", mode23)
declare_mode("24", mode24)
declare_mode("25", mode25)
declare_mode("26", mode26)
declare_mode("27", mode27)
declare_mode("28", mode28)
# nb mode 29 unused
declare_mode("30", mode30)
declare_mode("31", mode31)
declare_mode("32", mode32)
declare_mode("33", mode33)
declare_mode("34", mode34)
declare_mode("35", mode35)
declare_mode("36", mode36)
declare_mode("37", mode37)
declare_mode("38", mode38)
declare_mode("39", mode39)
declare_mode("40", mode40)
declare_mode("41", mode41)
declare_mode("42", mode42)
declare_mode("43", mode43)
declare_mode("44", mode44)
declare_mode("45", mode45)
declare_mode("46", mode46)
declare_mode("47", mode47)
declare_mode("48", mode48)
declare_mode("49", mode49)
declare_mode("50", mode50)
declare_mode("51", mode51)
declare_mode("52", mode52)
declare_mode("53", mode53)
declare_mode("54", mode54)
declare_mode("55", mode55)
declare_mode("56", mode56)
declare_mode("57", mode57)
declare_mode("58", mode58)
declare_mode("59", mode59)
declare_mode("60", mode60)
declare_mode("61", mode61)
declare_mode("62", mode62)
declare_mode("63", mode63)
declare_mode("64", mode64)
declare_mode("65", mode65)
declare_mode("66", mode66)
declare_mode("67", mode67)
declare_mode("68", mode68)
declare_mode("69", mode69)
declare_mode("70", mode70)
declare_mode("71", mode71)
declare_mode("72", mode72)
declare_mode("73", mode73)
declare_mode("74", mode74)
declare_mode("75", mode75)
declare_mode("76", mode76)
declare_mode("77", mode77)
declare_mode("79", mode79)
declare_mode("80", mode80)
declare_mode("81", mode81)
declare_mode("82", mode82)


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
