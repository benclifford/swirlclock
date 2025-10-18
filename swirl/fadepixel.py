from swirl.colour import hsv_to_neo_rgb

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

