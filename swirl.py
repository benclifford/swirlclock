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

def mode1():
    global new_mode
    pixels.auto_write = True
    n = 0
    while not new_mode:
        print("tick")
        pixel = random.randint(0,49)

        if n == 0:
            (red, green, blue) = (0,0,0)
        else:
            hue = random.random()
            (red, green, blue) = colorsys.hsv_to_rgb(hue, 1, 1)
        pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)))
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
        (red, green, blue) = colorsys.hsv_to_rgb(hue, 1, 1)
        pixels.fill( ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue))) )

        secs = t % 60

        tick_pixel = int(secs/60.0 * 50.0)

        (red, green, blue) = colorsys.hsv_to_rgb((hue + 0.5) % 1, 1, 1)
        pixels[tick_pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )

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
        (red, green, blue) = colorsys.hsv_to_rgb(colours[n], 1, 1)
        pixels[n] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )

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

                (red, green, blue) = colorsys.hsv_to_rgb(colours[n], 1, 1)
                pixels[n] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )

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
      (red, green, blue) = colorsys.hsv_to_rgb(frac, 1, 1)
      pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )
      
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

      (red, green, blue) = colorsys.hsv_to_rgb(frac_hue, 1, intensity)
      pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )
      
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
          (red, green, blue) = colorsys.hsv_to_rgb(frac_hue, 1, intensity)
          pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )
      else:
          intensity = (width - d) * (1/width)
          (red, green, blue) = colorsys.hsv_to_rgb(frac_hue, 1, intensity)
          pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )


    """ 
    # set minute 
    for pixel in range(bottoms[len(bottoms)-1],bottoms[len(bottoms)-2]):
      for b in range(0,len(bottoms)-1):
        if pixel < bottoms[b] and pixel >= bottoms[b+1]:
          start = bottoms[b]
          end = bottoms[b+1]
          frac = (pixel - start) / (end - start)
          # print("pixel {}: frac = {}".format(pixel, frac))
          break
      else:
        raise RuntimeError("could not find range for pixel {}".format(pixel))

      mins_frac = now.tm_min / 60.0
      frac_hue = (frac + mins_frac + 0.5) % 1
      frac2 = (frac + mins_frac + 0.5) % 1

      width = 0.05

      d = frac2
      if d > width and d < (1-width):
          intensity = 0
      elif d >= (1-width):
          d = 1 - d
          intensity = (width - d) * (1/width)
          intensity = 0.5 + intensity * 0.5
          (red, green, blue) = colorsys.hsv_to_rgb(frac_hue, 0, intensity)
          pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )
      else:
          intensity = (width - d) * (1/width)
          intensity = 0.5 + intensity * 0.5 # scale up to be quite bright
          (red, green, blue) = colorsys.hsv_to_rgb(frac_hue, 0, intensity)
          pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )
    """
      
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

        (red, green, blue) = colorsys.hsv_to_rgb(frac, radial_proportion, radial_proportion)

        pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )

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

        (red, green, blue) = colorsys.hsv_to_rgb(hue, 1, brightness)

        pixels[pixel] = ( scale(gamma(red)), scale(gamma(green)), scale(gamma(blue)) )

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

    angle = (0.5 + hour/12.0 + minute/60.0/12.0) % 1.0

    # which loop in we're going to pick the base pixel
    # to be. 0 is the outermost loop of the spiral.
    loop_in = 1

    start = bottoms[len(bottoms) - 1 - loop_in]
    end = bottoms[len(bottoms) - 2 - loop_in]
    base_pixel = round(start + (end-start) * angle)

    # pixels[base_pixel] = (255,0,0)

    pixel_pos = {}
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

      tau = 3.14 * 2.0  # better source for this?
      r = 1.0
      p_angle = frac
      x = math.sin(p_angle * tau) * b
      y = math.cos(p_angle * tau) * b
      # print("x = {}, y = {}".format(x,y))
      pixel_pos[pixel] = (x, y)

    distances = []
    (x, y) = pixel_pos[base_pixel]
    for pixel in range(0,50):
      (x1, y1) = pixel_pos[pixel]
      distances.append( (math.sqrt( (x-x1) ** 2 + (y-y1) ** 2) , pixel))
      # print("distances = {}".format(distances))

    s = sorted(distances)
    
    # print("s = {}".format(s))

    for dot in range(0,hour):
        (distance, pixel) = s[dot]
        pixels[pixel] = (255,int(gamma(dot / 12.0) * 255.0),0)

    max_distance = 0
    for dot in range(0,50):
        (distance, pixel) = s[dot]
        if distance > max_distance:
            max_distance = distance

    for dot in range(hour,50):
        (distance, pixel) = s[dot]
        # prop = dot / 50.0  # colour by ranked distance
        prop = distance / max_distance  # colour by actual distance
        pixels[pixel] = (0,int(gamma(prop) * 32.0),int(gamma(1-prop) * 32.0))

    pixels.show()
    time.sleep(1)

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


def go():
    global new_mode
    while True:
        if new_mode:
            print("new mode: {}".format(new_mode))
            m = new_mode
            new_mode = None
            m()

threading.Thread(target=go).start()
