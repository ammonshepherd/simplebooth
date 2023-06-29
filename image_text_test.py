from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageTk

HOME = "/home/slabpi/simplebooth/simplebooth"
if Path(f'{HOME}/temp_pics/2023-06-26-12-44-49/booth_image.jpg').exists():
    Path(f'{HOME}/temp_pics/2023-06-26-12-44-49/booth_image.jpg').unlink()

image_list = list(Path(f"{HOME}/temp_pics/2023-06-26-12-44-49/").iterdir())

TOP_TEXT = "Make it a GREAT day!"
BOTTOM_TEXT = "Scholars' Lab TinkerTank"
TOP_TEXT_BOX_WIDTH = 1120
TOP_TEXT_BOX_HEIGHT = 700


def make_booth_image(images):
    """Make photobooth image. Use images in the given path to create the
    photobooth image that will be printed."""
    # Currently, the only option is the classic, three stacked images

    folder_path = Path(images[0]).parent
    booth_image = Image.new('RGB', (1200, 3600), (255, 255, 255))
    # place the first image 40 pixels in from the top left corner
    x, y = 40, 40
    for img in images:
        new_img = Image.open(img)
        booth_image.paste(new_img, (x, y))
        # add 880 pixels to where the bottom of each image is placed
        y = y + 880

    top_font_size = 180
    wrapped_height = 100

    top_text = ImageDraw.Draw(booth_image)
    font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", top_font_size)
    wrap_size = get_wrap(top_text, TOP_TEXT, font1)

    while (wrapped_height < 630) or (wrapped_height > 680):
        font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", top_font_size)
        wrap_size = get_wrap(top_text, TOP_TEXT, font1)
        wrapped_text = textwrap.fill(TOP_TEXT, wrap_size)
        wrapped_length, wrapped_height = get_text_lh((40, 2680), top_text, wrapped_text, font1)
        print(wrapped_length, wrapped_height, top_font_size, wrap_size)
        if wrapped_length > 1050:
            break
        if wrapped_height > 680:
            top_font_size -= 10
        elif wrapped_height < 630:
            top_font_size += 10

    # font1 = ImageFont.truetype(
    #     "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 200)
    # wrapped_text = textwrap.fill(TOP_TEXT, 12)

    top_text.multiline_text((40, 2680), wrapped_text, font=font1, fill=( 35, 45, 75), spacing=20, align="center")


    # add the smaller text
    font2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
    bottom_text = ImageDraw.Draw(booth_image)
    bottom_text.multiline_text((40, 3420), BOTTOM_TEXT, font=font2,
                               fill=(248, 76, 30), align="center")

    booth_image.save(f'{folder_path}/booth_image.jpg')
    return f'{folder_path}/booth_image.jpg'


def get_wrap(text_obj, text, the_font):
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
