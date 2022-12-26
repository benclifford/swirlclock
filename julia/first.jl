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

magnitude = fill(Float64(0), 50)
rate_of_change = fill(Float64(0), 50)

for i in 1:50
  # if rand() < 0.03
  if i == 25
    magnitude[i] = 10
  else
    magnitude[i] = 0
  end
end

while true
  for i in 1:50
    print(rgbf_to_hex(leds[i]))
  end
  println("")

  new_magnitude = fill(Float64(0), 50)
  
  maximum = 0
  minimum = 1
  tot = 0

  for i in 1:50
    # This syntax for immutable updates is more complicated than
    # I like.

    l = magnitude

    decay = 100

    if i > 1
      ix = i -1
      d_l = (magnitude[i] - magnitude[ix]) / decay
    else
      ix = 50
      # d_l = (magnitude[i] - magnitude[ix]) / decay
      d_l = 0
    end


    if i < 50
      ix  = i + 1
      d_r = (magnitude[i] - magnitude[ix]) / decay
    else
      ix = 1
      # d_r = (magnitude[i] - magnitude[ix]) / decay
      d_r = 0
    end


    rate_of_change[i] = (rate_of_change[i] * 1.0) - d_l - d_r

    nv = magnitude[i] + rate_of_change[i]
    new_magnitude[i] = nv

    intensity = nv
    intensity = max(0, intensity)
    intensity = min(1, intensity)

    roc = rate_of_change[i] * decay / 10
    # println(stderr, roc)
    roc = max(0, roc)
    roc = min(1, roc)

    leds[i] = RGBf(roc, intensity, intensity)

    if nv > maximum
      maximum = nv
    end
    if nv < minimum
      minimum = nv
    end
    tot = tot + nv
  end

  global magnitude = new_magnitude

  print(stderr, minimum)
  print(stderr, " .. ")
  print(stderr, maximum)
  print(stderr, " => ")
  println(stderr, tot)

  sleep(0.05)
end
