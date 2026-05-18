import sys
from unittest.mock import MagicMock

sys.modules["cups"] = MagicMock()

from escpos.printer import *
from PIL import Image
import numpy as np

if len(sys.argv) < 2:
    print(f"usage: python3 {sys.argv[0]} path [mode=bitImageColumn|bitImageRaster|graphics] [algorithm=default|otsu_threshold|flyod_steinberg|atkinson]")
    print()
    print("positional arguments:")
    print("  path       path to image.png")
    print("  mode       image handling mode on the receipt printer (default: bitImageColumn)")
    print("  algorithm  dithering algorithm to use")
    exit()

# Configure your printer here
p = Serial(
    devfile='/dev/ttyUSB0',
    baudrate=19200,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1.00,
    dsrdtr=True,
    profile="TM-T88III"
)

def resize_to_width(image: Image.Image, width: int = 512) -> Image.Image:
    """
    Resize image to a fixed width while preserving aspect ratio.
    """

    aspect_ratio = image.height / image.width
    new_height = int(width * aspect_ratio)

    return image.resize((width, new_height), Image.Resampling.LANCZOS)

def otsu_threshold(image: Image.Image) -> Image.Image:
    """
    Convert image to 1-bit using an automatically calculated Otsu threshold.
    """

    gray = image.convert("L")
    pixels = np.asarray(gray)

    hist = np.bincount(
        pixels.ravel(),
        minlength=256
    )

    total = pixels.size

    sum_total = np.dot(
        np.arange(256),
        hist
    )

    sum_background = 0
    weight_background = 0

    max_variance = -1
    threshold = 127

    for t in range(256):

        weight_background += hist[t]

        if weight_background == 0:
            continue

        weight_foreground = total - weight_background

        if weight_foreground == 0:
            break

        sum_background += t * hist[t]

        mean_background = (
            sum_background / weight_background
        )

        mean_foreground = (
            (sum_total - sum_background)
            / weight_foreground
        )

        variance = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )

        if variance > max_variance:
            max_variance = variance
            threshold = t

    return gray.point(
        lambda p: 255 if p > threshold else 0,
        mode="1"
    )

def dither_floyd_steinberg(image: Image.Image) -> Image.Image:
    """
    Convert image to black and white using Floyd–Steinberg dithering.
    Returns a 1-bit image.
    """

    grayscale = image.convert("L")

    return grayscale.convert(
        "1",
        dither=Image.Dither.FLOYDSTEINBERG
    )

def dither_atkinson(image: Image.Image) -> Image.Image:
    """
    Convert image to black and white using Atkinson dithering.
    Returns a 1-bit Pillow image.
    """

    grayscale = image.convert("L")
    pixels = np.array(grayscale, dtype=np.float32)

    height, width = pixels.shape

    for y in range(height):
        for x in range(width):

            old_pixel = pixels[y, x]
            new_pixel = 255 if old_pixel > 127 else 0

            pixels[y, x] = new_pixel

            error = (old_pixel - new_pixel) / 8

            neighbors = [
                (x + 1, y),
                (x + 2, y),
                (x - 1, y + 1),
                (x,     y + 1),
                (x + 1, y + 1),
                (x,     y + 2),
            ]

            for nx, ny in neighbors:
                if 0 <= nx < width and 0 <= ny < height:
                    pixels[ny, nx] += error

    result = np.clip(pixels, 0, 255).astype(np.uint8)

    return Image.fromarray(result).convert("1")

image = Image.open(sys.argv[1])
implementation = sys.argv[2] if len(sys.argv) > 2 else "bitImageRaster"
algorithm = sys.argv[3] if len(sys.argv) > 3 else "default"

image = resize_to_width(image, 512)
if algorithm == "floyd_steinberg":
    image = dither_floyd_steinberg(image)
elif algorithm == "atkinson":
    image = dither_atkinson(image)
elif algorithm == "otsu_threshold":
    image = otsu_threshold(image)

p.image(image, impl=implementation)
p.cut()
