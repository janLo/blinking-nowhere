#!/usr/bin/env python


import sys
import random

from PIL import Image
import numpy as np


from blinkstick import blinkstick


def load_color(image_name):
    pic = Image.open(image_name)
    return np.asarray(pic, dtype=np.uint8)[0]


def foo(x):
    return min(max(x, 5), 180)


if __name__ == "__main__":
    bstick = blinkstick.find_first()
    if bstick is None:
        print "No BlinkSticks found..."
        time.sleep(10)
        sys.exit(1)

    assert len(sys.argv) == 2

    img = load_color(sys.argv[1])
    LEN = len(img)
    last = 0

    while True:
        diff = 0
        cur = 0

        while diff < 30:
            cur = random.randint(0, LEN - 1)
            diff = abs(last-cur)

        steps = max(10, int(diff / 10.0))
        color = [foo(x) for x in img[cur]]

        bstick.morph(red=color[0],
                     green=color[1],
                     blue=color[2],
                     duration=50*steps,
                     steps=steps)
