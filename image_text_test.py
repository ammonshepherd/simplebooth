from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageTk

if Path(f'/home/pi/Pictures/simplebooth_pictures/2023-06-26-12-44-49/booth_image.jpg').exists():
    Path(f'/home/pi/Pictures/simplebooth_pictures/2023-06-26-12-44-49/booth_image.jpg').unlink()

images = list(Path("/home/pi/Pictures/simplebooth_pictures/2023-06-26-12-44-49/").iterdir())

TOP_TEXT = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
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

    # Add the main, big text box
    # font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 130)
    top_font_size = 180
    wrap_size = 28
    line_length = 2000

    while line_length > 1160:
        # while wrapped_width > 1160 or wrapped_height > 700
        font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf", top_font_size)
        top_text = ImageDraw.Draw(booth_image)
        wrapped_text = textwrap.fill(TOP_TEXT, wrap_size)
        top_text.multiline_text((40, 2680), wrapped_text, font=font1, fill=( 35, 45, 75), spacing=20, align="center")

        wrap_size, line_length = get_text_dimensions(top_text, TOP_TEXT, font1)
        wrap_size -= 1
        top_font_size += 10
        print(get_text_dimensions(top_text, TOP_TEXT, font1))

    # add the smaller text
    font2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
    bottom_text = ImageDraw.Draw(booth_image)
    bottom_text.multiline_text((40, 3420), BOTTOM_TEXT, font=font2,
                               fill=(248, 76, 30), align="center")

    booth_image.save(f'{folder_path}/booth_image.jpg')
    return f'{folder_path}/booth_image.jpg'


def get_text_dimensions(text_obj, text, the_font):
    new_text = ""
    char_count = 0
    line_length = 0
    for x in text:
        char_count += 1
        new_text = f'{new_text}{x}'
        line_length = int(text_obj.textlength(new_text, font=the_font))
        if line_length >= 1100:
            break
    return char_count, line_length



make_booth_image(images)