import sys
from unittest.mock import MagicMock

sys.modules["cups"] = MagicMock()

import serial
import pymupdf
import io
from escpos.printer import *
from PIL import Image

if len(sys.argv) < 2:
    print(f"usage: python3 {sys.argv[0]} path")
    print()
    print("positional arguments:")
    print("  path   path to the pdf file")
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

filePath = sys.argv[1]
doc = pymupdf.open(filePath)
page = doc.load_page(0)

rect = pymupdf.Rect(33.375,82.625,288,215.05)
page.set_cropbox(rect)
# 72mm ^= 512px
pix = page.get_pixmap(matrix=pymupdf.Matrix(2.508888889, 2.508888889))

img = Image.open(io.BytesIO(pix.tobytes("png")))
img = img.crop((14,0,14+512,img.height))

p.image(img)
p.cut()
