import os
import shutil

from subprocess import call
from PIL import Image, ImageDraw, ImageFont
from slugify import slugify

################################################################################
# BUILD OPTIONS
################################################################################

MODIFIER = 0.6

IMAGE_WIDTH = 1028
IMAGE_HEIGHT = 540
IMAGE_PADDING_TOP = 25
IMAGE_PADDING_BOTTOM = int(153/2)
IMAGE_PADDING_LEFT = 25
IMAGE_PADDING_RIGHT = 25

TILE_W = 7
TILE_H = 8

BASE_FONT_SIZE = 200
BREAKPOINT_DIFF = 5
# fontFile = "fonts/Zapfino.ttf"
# fontFile = "fonts/Pacifico.ttf"
# fontFile = "fonts/RobotoMono-Regular.ttf"
# fontFile = "fonts/KaushanScript-Regular.ttf"
# fontFile = "fonts/Lobster-Regular.ttf"
fontFile = "fonts/SCRIPTBL.TTF"

################################################################################
# MODIFIED BUILD OPTIONS
################################################################################

IMAGE_WIDTH = int(IMAGE_WIDTH * MODIFIER)
IMAGE_HEIGHT = int(IMAGE_HEIGHT * MODIFIER)
IMAGE_PADDING_TOP = int(IMAGE_PADDING_TOP * MODIFIER)
IMAGE_PADDING_BOTTOM = int(IMAGE_PADDING_BOTTOM * MODIFIER)
IMAGE_PADDING_LEFT = int(IMAGE_PADDING_LEFT * MODIFIER)
IMAGE_PADDING_RIGHT = int(IMAGE_PADDING_RIGHT * MODIFIER)

IMAGE_DIMENSIONS = (IMAGE_WIDTH + IMAGE_PADDING_LEFT + IMAGE_PADDING_RIGHT, IMAGE_HEIGHT + IMAGE_PADDING_TOP + IMAGE_PADDING_BOTTOM)

################################################################################
# PRINT THE SETTTINGS
################################################################################

print("### SETTINGS")
print("IMAGE_WIDTH = {0}".format(IMAGE_WIDTH))
print("IMAGE_HEIGHT = {0}".format(IMAGE_HEIGHT))
print("IMAGE_PADDING_TOP = {0}".format(IMAGE_PADDING_TOP))
print("IMAGE_PADDING_BOTTOM = {0}".format(IMAGE_PADDING_BOTTOM))
print("IMAGE_PADDING_LEFT = {0}".format(IMAGE_PADDING_LEFT))
print("IMAGE_PADDING_RIGHT = {0}".format(IMAGE_PADDING_RIGHT))

################################################################################
# DELCARE THE THINGS
################################################################################

def compute_max_fontsize(names):
    minFontSize = BASE_FONT_SIZE
    myFontSize = BASE_FONT_SIZE

    for name in names:
        image = Image.new("RGBA", IMAGE_DIMENSIONS, (255, 255, 255))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(fontFile, myFontSize)

        while True:
            w, h = draw.textsize(name, font=font)

            if w > IMAGE_WIDTH or h > IMAGE_HEIGHT:
                myFontSize = myFontSize - 1
                font = ImageFont.truetype(fontFile, myFontSize)
                continue

            break

        if myFontSize < minFontSize:
            minFontSize = myFontSize

    return minFontSize

def draw_image(fontSize, i, txt):
    myFontSize = fontSize + BREAKPOINT_DIFF

    image = Image.new("RGBA", IMAGE_DIMENSIONS, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(fontFile, myFontSize)

    w, h = draw.textsize(txt, font=font)

    if w > IMAGE_WIDTH or h > IMAGE_HEIGHT:
        myFontSize = myFontSize - BREAKPOINT_DIFF
        font = ImageFont.truetype(fontFile, myFontSize)
        w, h = draw.textsize(txt, font=font)

    w = (IMAGE_WIDTH + IMAGE_PADDING_LEFT + IMAGE_PADDING_RIGHT - w) / 2
    h = (IMAGE_HEIGHT + IMAGE_PADDING_TOP - h) / 2

    draw.text((w, h), txt, (0, 0, 0), font=font)

    imageFileName = "nameplates/{0:03d}-{1}.jpg".format(i, slugify(txt))

    print("Created {0} with font {1}".format(imageFileName, myFontSize))

    with open(imageFileName, "w+") as f:
        image.save(f, "JPEG")

################################################################################
# RUN THE THINGS
################################################################################

shutil.rmtree("nameplates")
os.makedirs("nameplates")

with open("names.csv") as f:
    names = [name.strip() for name in f.readlines()]

    maxFontSize = compute_max_fontsize(names) - 2

    print("Max Font Size: {0}".format(maxFontSize))

    for i, name in enumerate(names):
        draw_image(maxFontSize, i, name)

shutil.rmtree("merged")
os.makedirs("merged")

montage_command = ["montage", "nameplates/*", "-geometry", "+0+0", "-tile", "{0}x{1}".format(TILE_W, TILE_H), "merged/nameplates.jpg"]

print("Calling: " + " ".join(montage_command))

call(montage_command)

mogrify_command = ["mogrify", "-flop", "-threshold", "50%", "-type", "Bilevel", "-depth", "1", "-colors", "2", "-colorspace", "Gray", "-format", "bmp", "merged/*.jpg"]

print("Calling: " + " ".join(mogrify_command))

call(mogrify_command)
