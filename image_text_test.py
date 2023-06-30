from pathlib import Path
import textwrap
import random

from PIL import Image, ImageDraw, ImageFont, ImageTk

HOME = "/home/slabpi/simplebooth/simplebooth"
if Path(f'{HOME}/temp_pics/2023-06-26-12-44-49/booth_image.jpg').exists():
    Path(f'{HOME}/temp_pics/2023-06-26-12-44-49/booth_image.jpg').unlink()

image_list = list(Path(f"{HOME}/temp_pics/2023-06-26-12-44-49/").iterdir())

TOP_TEXT = ["Be the best you can, so you can do the best you can!",
            "Do good, be good, but if you have to choose, be good.",
            "Make it a GREAT day!",
            "Sieze the day!",
            "Ya'll are AWESOME!",
            "WE GOT THIS!",
            "BFF!",
            "We so cool!"]
BOTTOM_TEXT = "Scholars' Lab TinkerTank"

STRIP_BORDER = 40
STRIP_WIDTH = 1200
STRIP_LENGTH = 3600

TEXT_LENGTH_MAX = STRIP_WIDTH - (STRIP_BORDER * 2) - 20
TOP_TEXT_HEIGHT_MIN = 630
TOP_TEXT_HEIGHT_MAX = 680


def make_booth_image(images):
    """Make photobooth image. Use images in the given path to create the
    photobooth image that will be printed."""
    # Currently, the only option is the classic, three stacked images

    folder_path = Path(images[0]).parent
    booth_image = Image.new('RGB', (STRIP_WIDTH, STRIP_LENGTH), (255, 255, 255))
    # place the first image 40 pixels in from the top left corner
    x, y = STRIP_BORDER, STRIP_BORDER
    for img in images:
        new_img = Image.open(img)
        booth_image.paste(new_img, (x, y))
        # add 880 pixels to where the bottom of each image is placed
        y = y + 880

    # Top text 
    random_text = random.choice(TOP_TEXT)
    top_text = ImageDraw.Draw(booth_image)
    long_text, font1 = create_text(top_text, random_text, TOP_TEXT_HEIGHT_MIN,
                                      TOP_TEXT_HEIGHT_MAX)
    top_text.multiline_text((STRIP_BORDER, 2680), long_text, font=font1, fill=( 35, 45, 75), spacing=20, align="center")

    # add the smaller text
    bottom_text = ImageDraw.Draw(booth_image)
    font2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
    bottom_text.multiline_text((40, 3420), BOTTOM_TEXT, font=font2,
                               fill=(248, 76, 30), align="center")

    booth_image.save(f'{folder_path}/booth_image.jpg')
    return f'{folder_path}/booth_image.jpg'

def create_text(text_obj, text, height_min, height_max):
    """ Create the text under the images """
    font_size = 180
    wrapped_height = 100
    wrapped_text = ""

    font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", font_size)
    wrap_size = get_wrap(text_obj, text, font1)

    while (wrapped_height < height_min) or (wrapped_height > height_max):
        font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", font_size)
        wrap_size = get_wrap(text_obj, text, font1)
        wrapped_text = textwrap.fill(text, wrap_size)
        wrapped_length, wrapped_height = get_text_lh((STRIP_BORDER, 2680), text_obj, wrapped_text, font1)
        print(wrapped_length, wrapped_height, font_size, wrap_size)
        if wrapped_length > TEXT_LENGTH_MAX:
            break
        if wrapped_height > height_max:
            font_size -= 10
        elif wrapped_height < height_min:
            font_size += 10

    return wrapped_text, font1

def get_wrap(text_obj, text, the_font):
    """ Get the number of characters to wrap the text at 1100 pixels """
    new_text = ""
    char_count = 0
    line_length = 0
    for x in text:
        char_count += 1
        new_text = f'{new_text}{x}'
        line_length = int(text_obj.textlength(new_text, font=the_font))
        if line_length >= 1100:
            break
    return char_count

def get_text_lh(xy, text_obj, text, the_font):
    """ Given a wrapped text object, return the height """
    left, top, right, bottom = text_obj.multiline_textbbox(xy, text, font=the_font)
    length = right - left
    height = bottom - top
    return length, height


make_booth_image(image_list)
