import sys
from unittest.mock import MagicMock

sys.modules["cups"] = MagicMock()

from escpos.printer import *

if len(sys.argv) < 2:
    print(f"usage: python3 {sys.argv[0]} \"text\" [wrap]")
    print()
    print("positional arguments:")
    print("  text  text to print")
    print("  wrap  maximum number of characters before a new line is inserted (default: 42)")
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

# Use width=39 for symmetrical margins (80mm paper, default font size)
def wrap_text(text, width=42):
    if len(text) <= width:
        return text
    space_index = text.rfind(' ', 0, width)
    if space_index == -1:
        return text[:width] + '\n' + wrap_text(text[width:], width)
    else:
        return text[:space_index] + '\n' + wrap_text(text[space_index+1:], width)
        
text = sys.argv[1]
width = sys.argv[2] if len(sys.argv) > 2 else 42

p.set_with_default()
p.text(wrap_text(sys.argv[1], width))
p.cut()
