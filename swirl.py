# usage notes for python neopixe pi libraries:
#     https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage


# spiral maths notes:
#     https://www.intmath.com/blog/mathematics/length-of-an-archimedean-spiral-6595
#     https://www.giangrandi.ch/soft/spiral/spiral.shtml

import board
import colorsys  # from pygame
import math
import neopixel
import random
import threading
import time

import flask


pixels = neopixel.NeoPixel(board.D18, 50)

bottoms = [50, 49, 46, 37, 22, 0]


new_mode = None

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
    global new_mode
    pixels.auto_write = True
    
    while not new_mode:
        pixels.fill( (255,0,32) )
        time.sleep(1)


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

        # print("pass")
        if count == 0:
            new_pixel = random.randint(0,49)
            new_hue = random.random()
            # colours[new_pixel] = new_hue

        count = (count + 1) % 200

        p1 = random.randint(0,48)
        p2 = p1 + 1

        if colours[p1] > colours[p2]:
            # print("swap")
            tmp = colours[p1]
            colours[p1] = colours[p2]
            colours[p2] = tmp
            swapped = True

        if swapped:
            for n in range(0,50):
                pixels[n] = hsv_to_neo_rgb(colours[n])

            pixels.show()
            print("one pass")
            time.sleep(0.1)


def mode5():
    global new_mode
    while not new_mode:
        time.sleep(1)


def mode6():
    global new_mode
    pixels.auto_write = True
    
    while not new_mode:
        pixels.fill( (0,0,0) )
        time.sleep(1)


def mode7():
    global new_mode
    pixels.auto_write = False



    pixels.fill( (0,0,0) )
    pixels.show()

    for pixel in range(0,50):
      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))
      pixels[pixel] = hsv_to_neo_rgb(frac)
      
    pixels.show()

    while not new_mode:
        time.sleep(1)


def mode8():
  global new_mode
  pixels.auto_write = False


  rot = 0
  rot2 = 0

  while not new_mode:

    for pixel in range(0,50):
      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))
      frac_hue = (frac + rot) % 1
      frac2 = (frac + rot2) % 1

      width = 0.15

      d = frac2
      if d > width and d < (1-width):
          intensity = 0
      elif d >= (1-width):
          d = 1 - d
          intensity = (width - d) * (1/width)
      else:
          intensity = (width - d) * (1/width)

      pixels[pixel] = hsv_to_neo_rgb(frac_hue, v=intensity)
      
    pixels.show()

    rot = rot + (1.0/600.0) % 1
    rot2 = rot2 + (1.0/423.0) % 1
    time.sleep(0.01)


def mode9():
  global new_mode
  pixels.auto_write = False

  update_period = 0.01

  rot2 = 0


  while not new_mode:
    pixels.fill( (0,0,0) )

    now = time.localtime()

    # set hour
    for pixel in range(0,49):
      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))

      hour_frac = now.tm_hour % 12 / 12.0
      frac_hue = (frac + rot2) % 1
      frac2 = (frac + hour_frac + 0.5) % 1

      width = 0.12

      d = frac2
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

    rot2 = rot2 + (1.0/42300.0 * (update_period / 0.01)) % 1
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

        for b in range(0,len(bottoms)-1):
          if pixel < bottoms[b] and pixel >= bottoms[b+1]:
            start = bottoms[b]
            end = bottoms[b+1]
            proportion_around_loop = (pixel - start) / (end - start)

            frac = (proportion_around_loop + offset) % 1.0

            radial_pos = b
            break
        else:
          raise RuntimeError("could not find range for pixel {}".format(pixel))

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

    offset = 0

    hue = 0.5
    angle = 0.3
    width = 1
    speed = 0.2
    outwards = 0

    while not new_mode:


      for pixel in range(0,50):

        for b in range(0,len(bottoms)-1):
          if pixel < bottoms[b] and pixel >= bottoms[b+1]:
            start = bottoms[b]
            end = bottoms[b+1]
            proportion_around_loop = (pixel - start) / (end - start)

            frac = proportion_around_loop

            radial_pos = b
            break
        else:
          raise RuntimeError("could not find range for pixel {}".format(pixel))

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

        # print("distance = {}, brightness = {}".format(distance, brightness))

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

    pixels.fill( (0,0,0) )
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

    while not new_mode:
      time.sleep(1)


def mode14():
  global new_mode
  pixels.auto_write = False

  while not new_mode:
    pixels.fill( (0,0,0) )
    

    now = time.localtime()
    hour = now.tm_hour % 12
    minute = now.tm_min

    hour_angle = (0.5 + hour/12.0 + minute/60.0/12.0) % 1.0
    minute_angle = (0.5 + minute/60.0) % 1.0

    mins_scaled = int(minute / 15 + 1)

    hour_pixels = pixels_for_angle(hour_angle, 1)
    minute_pixels = pixels_for_angle(minute_angle, 0)
    minute_pixels = minute_pixels[0:mins_scaled]

    for dot in minute_pixels:
        (distance, pixel) = dot
        hour_pixels = [(d,p) for (d,p) in hour_pixels if p != pixel]

    if hour == 0:
        hour_dot_count = 12
    else:
        hour_dot_count = hour

    hour_pixels = hour_pixels[0:hour_dot_count]
    
    for dot in hour_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (255,0,0)


    for dot in minute_pixels:
        (distance, pixel) = dot
        pixels[pixel] = (0,0,32)

    #max_distance = 0
    #for dot in range(0,50):
    #    (distance, pixel) = hour_pixels[dot]
    #    if distance > max_distance:
    #        max_distance = distance

    #for dot in range(hour,50):
    #    (distance, pixel) = hour_pixels[dot]
    #    # prop = dot / 50.0  # colour by ranked distance
    #    prop = distance / max_distance  # colour by actual distance
    #    pixels[pixel] = (0,int(gamma(prop) * 32.0),int(gamma(1-prop) * 32.0))

    pixels.show()
    time.sleep(1)


def pixels_for_angle(angle, loop_in):

    # loop_in = 
    # which loop in we're going to pick the base pixel
    # to be. 0 is the outermost loop of the spiral.

    start = bottoms[len(bottoms) - 1 - loop_in]
    end = bottoms[len(bottoms) - 2 - loop_in]
    base_pixelish = start + (end-start) * angle  # almost a pixel, but not rounded

    pixel_pos = {}
    for pixel in list(range(0,50)) + [base_pixelish]:

      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))

      tau = 3.14 * 2.0  # better source for this?
      r = 1.0
      p_angle = frac
      x = math.sin(p_angle * tau) * b
      y = math.cos(p_angle * tau) * b
      # print("x = {}, y = {}".format(x,y))
      pixel_pos[pixel] = (x, y)

    distances = []
    (x, y) = pixel_pos[base_pixelish]
    for pixel in range(0,50):
      (x1, y1) = pixel_pos[pixel]
      distances.append( (math.sqrt( (x-x1) ** 2 + (y-y1) ** 2) , pixel))
      # print("distances = {}".format(distances))

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
    for b in range(0,len(bottoms)-1):
      pixel = particle
      if pixel < bottoms[b] and pixel >= bottoms[b+1]:
        start = bottoms[b]
        end = bottoms[b+1]
        frac = (pixel - start) / (end - start)
        break
    else:
      raise RuntimeError("could not find range for pixel {}".format(pixel))

    choice = random.randint(0,2)

    old_first = first
    first = False

    if choice == 0:
      # print("choice 0")
      new_particle = particle + 1
      if new_particle >= bottoms[b]:
        new_particle = bottoms[b+1]

    elif choice == 1:
      # print("choice 1")
      new_particle = particle - 1  # TODO: mod
      if new_particle < bottoms[b+1]:
        new_particle = bottoms[b]-1
    elif choice == 2:
      # print("choice 2")
      # move inwards
      # determine angle now
      if b == 0:
        # if we reach the centre, solidify
        # print("solidifying: first = {}, old_first = {}".format(first, old_first))
        cells[particle] = 1
        new_particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
        boom = old_first
        first = True
        # print("boom: {}".format(boom))
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)
        # print("new particle by radius is {}".format(new_particle))

    if cells[new_particle] != 0: # if we're about to move onto solid, solidify
      # print("solidifying: first = {}, old_first = {}".format(first, old_first))
      cells[particle] = 1
      particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
      boom = old_first
      first = True
      # print("boom: {}".format(boom))
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

    # print("particle is {}".format(particle))
    pixels[particle] = (0,32,0)

    pixels.show()

    if boom:
      # print("BOOM")
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
  global new_mode
  pixels.auto_write = False

  start_hue = random.random()
  cells = [start_hue for n in range(0,50)]

  while not new_mode:

    for pixel in range(49,0,-1):
      cells[pixel] = cells[pixel - 1]

    cells[0] = (cells[0] + (random.random() * 0.1 - 0.05)) % 1.0

    for pixel in range(0,50):
      pixels[pixel] = hsv_to_neo_rgb(cells[pixel])
    pixels.show()
    time.sleep(0.05)


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


    pixel_pos = {}
    for pixel in list(range(0,50)):

      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))

      tau = 3.14 * 2.0  # better source for this?
      r = 1.0
      p_angle = frac
      x = math.sin(p_angle * tau) * b
      y = math.cos(p_angle * tau) * b
      # print("x = {}, y = {}".format(x,y))
      pixel_pos[pixel] = (x, y)

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

        # compute nearest pixels

        distances = []
        for pixel in range(0,50):
          (x1, y1) = pixel_pos[pixel]
          distances.append( (math.sqrt( (x-x1) ** 2 + (y-y1) ** 2) , pixel))
        s = sorted(distances)

        dots_to_light = s[0:ndots]

        pixels.fill( (0,0,0) )

        for dot in dots_to_light:
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


    pixel_pos = {}
    for pixel in list(range(0,50)):

      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))

      tau = 3.14 * 2.0  # better source for this?
      r = 1.0
      p_angle = frac
      x = math.sin(p_angle * tau) * b
      y = math.cos(p_angle * tau) * b
      # print("x = {}, y = {}".format(x,y))
      pixel_pos[pixel] = (x, y)

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

        # compute nearest pixels

        distances = []
        for pixel in range(0,50):
          (x1, y1) = pixel_pos[pixel]
          distances.append( (math.sqrt( (x-x1) ** 2 + (y-y1) ** 2) , pixel))
        s = sorted(distances)

        dots_to_light = s[0:ndots]

        for dot in dots_to_light:
            (distance, pixel) = dot
            display_pixels[pixel] = (hue, 1)


        for pixel in range(0,50):
            if display_pixels[pixel] is None:
                pixels[pixel] = (0,0,0)
            else:
                (display_hue, value) = display_pixels[pixel]
                pixels[pixel] = hsv_to_neo_rgb(display_hue, v=value)

        pixels.show()

        for pixel in range(0,50):
          if display_pixels[pixel] is not None:
            (display_hue, value) = display_pixels[pixel]
            new_value = value - 0.0075
            if new_value <= 0:
              display_pixels[pixel] = None
            else:
              display_pixels[pixel] = (display_hue, new_value)

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
    for b in range(0,len(bottoms)-1):
      pixel = particle
      if pixel < bottoms[b] and pixel >= bottoms[b+1]:
        start = bottoms[b]
        end = bottoms[b+1]
        frac = (pixel - start) / (end - start)
        break
    else:
      raise RuntimeError("could not find range for pixel {}".format(pixel))

    choice = random.randint(0,2)

    old_first = first
    first = False

    if choice == 0:
      # print("choice 0")
      new_particle = particle + 1
      if new_particle >= bottoms[b]:
        new_particle = bottoms[b+1]

    elif choice == 1:
      # print("choice 1")
      new_particle = particle - 1  # TODO: mod
      if new_particle < bottoms[b+1]:
        new_particle = bottoms[b]-1
    elif choice == 2:
      # print("choice 2")
      # move inwards
      # determine angle now
      if b == 0:
        # if we reach the centre, solidify
        # print("solidifying: first = {}, old_first = {}".format(first, old_first))
        new_particle = random.randint(bottoms[len(bottoms)-1], bottoms[len(bottoms)-2])
        boom = old_first
        first = True
        pixels.fill( (0,0,0) )
        hue = random.random()
        # print("boom: {}".format(boom))
      else:
        b = b - 1
        new_particle = int(bottoms[b] + (bottoms[b+1] - bottoms[b])*frac)
        # print("new particle by radius is {}".format(new_particle))

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
    blanking_probability = 0.99

    while not new_mode:

        active_pixel = random.randint(0,49)

        total_lit = 0
        for p in display_pixels:
            if p is not None:
                total_lit = total_lit + 1

        for b in range(0,len(bottoms)-1):
            pixel = active_pixel
            if pixel < bottoms[b] and pixel >= bottoms[b+1]:
                start = bottoms[b]
                end = bottoms[b+1]
                frac = (pixel - start) / (end - start)
                break
        else:
            raise RuntimeError("could not find range for pixel {}".format(pixel))

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
            if total_lit < 40:
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
                  new_hue = (display_pixels[active_pixel - 1] + diff / 2.0) % 1.0
                  display_pixels[active_pixel] = new_hue 

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
            if total_lit > 30 and random.random() > blanking_probability: # some hysteresis with the off-mode equivalent to keep a decent twinkling zone, perhaps
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

            else:
                # if we can't enhance the rainbowness of an existing pixel, just leave it as.
                pass  
                ##                display_pixels[active_pixel] = (display_pixels[active_pixel] + random.random() * 0.01) % 1.0

        for pixel in range(0,50):
            if display_pixels[pixel] is None:
                pixels[pixel] = (0,0,0)
            else:
                pixels[pixel] = hsv_to_neo_rgb(display_pixels[pixel])

        pixels.show()

        # time.sleep(0.1)


new_mode = mode14


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


def go():
    global new_mode
    while True:
        if new_mode:
            print("new mode: {}".format(new_mode))
            m = new_mode
            new_mode = None
            m()

threading.Thread(target=go).start()
