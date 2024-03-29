module Main where

import Control.Concurrent (threadDelay)
import Control.Monad (forever, join)
import Data.Time.Clock.POSIX (getPOSIXTime)
import Data.Word (Word8)
import Numeric (showHex)
import System.Environment (getArgs)
import System.IO (hFlush, hPutStrLn, stderr, stdout)
import Text.Printf (printf)


data RGB t = RGB {
  _red :: t,
  _green :: t,
  _blue :: t
  }


render :: [RGB Word8] -> String
render leds = join $ map f leds
  where f l = (hex . _red) l ++ (hex . _green) l ++ (hex . _blue) l
        hex v = if v < 16 then ['0', onehex v]
                          else [onehex (v `quot` 16), onehex (v `rem` 16)]


-- onehex v = "0123456789ABCDEF" !! (fromIntegral v)
onehex 0 = '0'
onehex 1 = '1'
onehex 2 = '2'
onehex 3 = '3'
onehex 4 = '4'
onehex 5 = '5'
onehex 6 = '6'
onehex 7 = '7'
onehex 8 = '8'
onehex 9 = '9'
onehex 10 = 'A'
onehex 11 = 'B'
onehex 12 = 'C'
onehex 13 = 'D'
onehex 14 = 'E'
onehex 15 = 'F'


updateLeds :: [RGB Word8] -> IO ()
updateLeds leds = do
  putStrLn $ render leds
  hFlush stdout

runLeds period (h:t) = do
  now <- getPOSIXTime
  runLedsInner (now + period) period (h:t)

runLedsInner nextTime period (h:t) = do
  updateLeds h
  -- wait until nextTime
  -- rather than a specific delay
  -- to accomodate the varying, significant
  -- time taken in updateLeds
  now <- getPOSIXTime
  let remaining = nextTime - now
  if remaining > 0 then do -- hPutStrLn stderr $ "extra time: " ++ show remaining
                           threadDelay (floor (remaining * 1000000))
                   else hPutStrLn stderr $ "WARNING: time overrun: " ++ show remaining
  runLedsInner (nextTime + period) period t

toggleSeq = [True, False] ++ toggleSeq

toggleToLeds = map f toggleSeq
  where f False = [redled, blueled]
        f True = [blueled, redled]
        redled = RGB 255 0 0
        blueled = RGB 0 0 255


-- spin round forever
angleSpin p = [0, p..6.28319] ++ angleSpin p

-- TODO: gamma correction
sinSpiral p = map sinSpiralFrame (angleSpin p)
sinSpiralFrame th = map (brightnessToRGB . fracToBrightness . normaliseSin . sin. adjAngle) (all50 th `zip` [0..49])
adjAngle (a,b) = a + (b/50.0)

normaliseSin x = x / 2.0 + 0.5

fracToBrightness x = floor (x * 255)

brightnessToRGB x = RGB x x x

all50 v = take 50 $ repeat v

main :: IO ()
main = do
  args <- getArgs
  -- switch on the mode number supplied on the CLI

  case (read $ head args) of
    90 -> runLeds 0.1 toggleToLeds
    91 -> runLeds 0.05 (sinSpiral 0.05)


