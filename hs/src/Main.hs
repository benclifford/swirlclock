module Main where

import Control.Concurrent (threadDelay)
import Control.Monad (forever, join)
import Data.Word (Word8)
import System.Environment (getArgs)
import System.IO (hFlush, stdout)
import Text.Printf (printf)


data RGB t = RGB {
  _red :: t,
  _green :: t,
  _blue :: t
  }


render :: [RGB Word8] -> String
render leds = join $ map f leds
  where f l = (hex . _red) l ++ (hex . _green) l ++ (hex . _blue) l
        hex v = printf "%2.2x" v

updateLeds :: [RGB Word8] -> IO ()
updateLeds leds = do
  putStrLn $ render leds
  hFlush stdout

runLeds (h:t) = do
  updateLeds h
  threadDelay 100000
  runLeds t

toggleSeq = [True, False] ++ toggleSeq

toggleToLeds = map f toggleSeq
  where f False = [redled, blueled]
        f True = [blueled, redled]
        redled = RGB 255 0 0
        blueled = RGB 0 0 255

main :: IO ()
main = do
  args <- getArgs
  -- switch on the mode number supplied on the CLI

  case (read $ head args) of
    90 -> runLeds toggleToLeds


