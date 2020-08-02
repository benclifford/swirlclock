# usage notes for python neopixe pi libraries:
#     https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage


# spiral maths notes:
#     https://www.intmath.com/blog/mathematics/length-of-an-archimedean-spiral-6595
#     https://www.giangrandi.ch/soft/spiral/spiral.shtml

import board
import colorsys  # from pygame
import neopixel
import random
import threading
import time

import flask


pixels = neopixel.NeoPixel(board.D18, 50)

new_mode = None

def scale(f):
    """ scale from 0..1 : float -> 0..255 : int"""
    return int(f * 255)


def gamma(v):
    """ gamma correct on range 0..1 : float
    Based on https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix
    """
    gamma_factor = 2.8  # this is value that adafruit people like
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
    pixels_auto_write = False
    colours = {}
    for n in range(0,50):
        colours[n] = random.random()

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


new_mode = mode2


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



def go():
    global new_mode
    while True:
        if new_mode:
            print("new mode: {}".format(new_mode))
            m = new_mode
            new_mode = None
            m()

threading.Thread(target=go).start()
