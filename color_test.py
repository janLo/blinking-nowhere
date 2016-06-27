#!/usr/bin/env python

import pyaudio
import struct
import sys
import argparse

import numpy as np

from PIL import Image
import time
import math

from normalize import DataNormalizer, ArrayNormalizer


nFFT = 400
CHUNK = 3*nFFT
FORMAT = pyaudio.paFloat32
RATE = 44100


class PyGamePutput(object):
    def __init__(self):
        import pygame

        pygame.init()
        screen = pygame.display.set_mode((468, 60))
        pygame.display.set_caption('Blinkstick')
        pygame.mouse.set_visible(0)

        self.surface = pygame.display.get_surface()
        self.display = pygame.display

    def set_color(self, color):
        self.surface.fill(color)
        self.display.update()


class BlinkStickOutput(object):
    def __init__(self):
        from blinkstick import blinkstick
        self.bstick = blinkstick.find_first()
        if self.bstick is None:
            print "No BlinkSticks found..."
            time.sleep(10)
            sys.exit(1)

    def set_color(self, color):
        color = color * 0.5


        self.bstick.set_color(red=color[0],
                              green=color[1],
                              blue=color[2])



def argparser():
    parser = argparse.ArgumentParser("Blinkstick audio foo")
    parser.add_argument("--output", choices=["blinkstick", "pygame"], default="blinkstick",
                        help="Choose output-'driver'")
    parser.add_argument("--color", required=True, help="image file to select color from")
    parser.add_argument("--mono", action='store_true', help="use only one channel")

    return parser


def load_color(image_name):
    pic = Image.open(image_name)
    return np.asarray(pic, dtype=np.uint8)[0]


def open_stream(channels):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    return stream




_normalizer = DataNormalizer(150)


def process_data(data, CHANNELS):
    y = np.array(struct.unpack("%df" % (CHUNK * CHANNELS), data))

    if CHANNELS == 2:
        y_L = y[::2]
        y_R = y[1::2]
 
        Y_L = np.fft.fft(y_L, nFFT)
        Y_R = np.fft.fft(y_R, nFFT)
 
        # Sewing FFT of two channels together, DC part uses right channel's
        Y = abs(np.hstack((Y_L[-nFFT / 2:-1], Y_R[:nFFT / 2])))

    else:
        y = np.fft.fft(y, nFFT)
        Y = y

    ret = _normalizer(abs(Y[1]), min_norm=3.8)
    return ret



if __name__ == "__main__":
    args = argparser().parse_args()

    color_data = load_color(args.color)

    if args.output == "pygame":
        output = PyGamePutput()
    else:
        output = BlinkStickOutput()

    CHANNELS = 2
    if "mono" in args:
        CHANNELS = 1

    stream = open_stream(CHANNELS)

    DIV = len(color_data)/9.0
    color_len = len(color_data)

    last = 0

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except IOError:
            stream.stop_stream()
            stream.close()
            stream = open_stream(CHANNELS)
            continue

        val = min(1.0, process_data(data, CHANNELS))

        offset = min(int(val * color_len), 1023)

        step = max(offset - last, -20)
        offset = last + step

        if 0 < step < 10:
            continue
        output.set_color(color_data[offset])

        last = offset


    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

