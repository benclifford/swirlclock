struct RGBf
  red::Float64
  green::Float64
  blue::Float64
end

function emit_rgb_chunk(n::Float64)::String
  i::Int = floor(n * 255)
  string(i, base=16, pad=2)
end

function rgbf_to_hex(rgbf::RGBf)
  r = emit_rgb_chunk(rgbf.red)
  g = emit_rgb_chunk(rgbf.green)
  b = emit_rgb_chunk(rgbf.blue)
  r * g * b
end

while true
  for i in 0:49
    if i % 2 == 0
      v = RGBf(1,0,0)
    else
      v = RGBf(0,1,0)
    end
    print(rgbf_to_hex(v))
  end
  println("")
  sleep(0.5)
  for i in 0:49
    frac = i / 50.0
    rgbf = RGBf(frac, 1-frac, frac)
    print(rgbf_to_hex(rgbf))
  end
  println("")
  sleep(0.5)
end
