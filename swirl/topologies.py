
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

