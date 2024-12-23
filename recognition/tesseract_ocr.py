import pytesseract as tess
import PIL
config = ('-l eng --oem 1 --psm 3')
def oer_out():
    img = PIL.Image.open('screenshot.png')
    text = tess.image_to_string(img, config=config)
    return text
