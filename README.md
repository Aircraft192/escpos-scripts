# Getting started
## Requirements
```bash
pip3 install pyserial python-escpos pymupdf
```
## Configuration
You will need to configure your receipt printer in each script seperately as of now. This offers the advantage that the scripts can also be used individually. I might change this in the future.

The code snippet you'll need to change looks like this:
```python
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
```
The values are pretty self-explanatory. If you're unsure, press and hold the "feed"-button while plugging in your Epson receipt printer. It will print out the information.

At the moment I don't have access to LPT-, USB- or Ethernet-printers, so take a look at the [python-escpos documentation](https://python-escpos.readthedocs.io/en/latest/) if you want to use one of those.

# Overview
This is an overview of all scripts included in this repository, along with a brief guide on how to use them. You can run all scripts without parameters to read their usage.

## print_text.py
Prints plain text
```bash
python3 print_text.py "your_text_here"
```

## print_image.py
Prints an image at the largest size possible
```bash
python3 print_image.py /path/to/image.png
```

## dp_label.py
Prints singular DIN-A4 labels from [Deutsche Post](https://shop.deutschepost.de/) with exact scaling
```bash
python3 dp_label.py /path/to/label.pdf
```
