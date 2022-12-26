using Setfield

struct RGBf
  red::Float64
  green::Float64
  blue::Float64
end

function emit_rgb_chunk(n::Float64)::String
  @assert n >= 0 "RGBf value should be >= 0"
  @assert n <= 1 "RGBf value should be <= 1"
  n = n ^ 1.9  # gamma correction
  i::Int = floor(n * 255)
  string(i, base=16, pad=2)
end

function rgbf_to_hex(rgbf::RGBf)
  r = emit_rgb_chunk(rgbf.red)
  g = emit_rgb_chunk(rgbf.green)
  b = emit_rgb_chunk(rgbf.blue)
  r * g * b
end

leds = fill(RGBf(0,0,0), 50)

rate_of_change = fill(Float64(0), 50)

for i in 1:50
  l = leds[i]
  # l = @set l.blue = rand()
  if rand() < 0.1
    l = @set l.blue = 1
  else
    l = @set l.blue = 0
  end

  leds[i] = l
end

while true
  for i in 1:50
    print(rgbf_to_hex(leds[i]))
  end
  println("")

  
  newleds = fill(RGBf(0,0,0), 50)

  maximum = 0
  minimum = 1

  for i in 1:50
    # This syntax for immutable updates is more complicated than
    # I like.

    l = leds[i]

    if i > 1
      ix = i -1
    else
      ix = 50
    end

    d_l = (leds[i].blue - leds[ix].blue) / 30

    if i < 50
      ix  = i + 1
    else
      ix = 1
    end

    d_r = (leds[i].blue - leds[ix].blue) / 30

    rate_of_change[i] = rate_of_change[i] - d_l - d_r

    l = @set l.blue = l.blue + rate_of_change[i]

    l = @set l.blue = max(0,l.blue)
    l = @set l.blue = min(1,l.blue)

    l = @set l.red = l.blue
    l = @set l.green = l.blue

    newleds[i] = l
    if l.blue > maximum
      maximum = l.blue
    end
    if l.blue < minimum
      minimum = l.blue
    end
  end

  global leds = newleds

  print(stderr, minimum)
  print(stderr, " .. ")
  println(stderr, maximum)

  sleep(0.1)
end
