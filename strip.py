"""Photo strip layout for simplebooth.

Builds the strip image (photos + logo + bottom text) and the double-wide
image that gets sent to the printer. Kept separate from simplebooth.py so it
can be used without the camera, GPIO or tkinter (see preview_strip.py).
"""
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

######################################################################
#
#     EVENT SETTINGS
#     change these for each event
#######################################################################
# Logo printed under the photos. Any size or shape: it is scaled to fit the
# logo area and centered. PNGs with a transparent background work best.
LOGO = 'Brown-College-standin-logo.png'
# LOGO = 'UVA-logo.jpg'

# Text at the very bottom of the strip. Use \n to break it into lines.
BOTTOM_TEXT = "Brown College\nFall Semi-Formal 2026"
# BOTTOM_TEXT = "Scholars' Lab Makerspace 2026"
TEXT_COLOR = (35, 45, 75)
BOTTOM_FONT_SIZE = 100
BOTTOM_FONT = "/usr/share/fonts/truetype/freefont/Bangers-Regular.ttf"

######################################################################
#
#     LAYOUT SETTINGS
#######################################################################
STRIP_BORDER = 40
STRIP_WIDTH = 1200
STRIP_LENGTH = 3600
# Photos come from the camera at this size (see take_pictures)
PHOTO_SIZE = (1100, 640)
PHOTO_TOP = STRIP_BORDER + 80   # y of the first photo
PHOTO_STEP = 880                # distance from the top of one photo to the next
# Widest the bottom text may be
TEXT_LENGTH_MAX = STRIP_WIDTH - (STRIP_BORDER * 2) - 20
# Logo area: from LOGO_TOP down to just above the bottom text
LOGO_TOP = STRIP_LENGTH - STRIP_BORDER - 940
LOGO_MAX_WIDTH = 900
LOGO_GAP = 10                   # space between the logo and the text

# Nudge everything on the printed sheet to correct for the printer not
# centering the print. Positive X moves right, positive Y moves down (pixels).
# Only affects the printed (double) image, not the strip uploaded to Drive.
PRINT_OFFSET_X = 0
PRINT_OFFSET_Y = 0

# Fonts to try if BOTTOM_FONT isn't installed (e.g. previewing off the Pi)
FALLBACK_FONTS = [
  "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf",
  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
  "/Library/Fonts/Arial Narrow Bold.ttf",
  "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
  "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def load_font(size):
  """Load the bottom-text font, falling back if it isn't installed."""
  for path in [BOTTOM_FONT] + FALLBACK_FONTS:
    try:
      return ImageFont.truetype(path, size)
    except OSError:
      continue
  logging.warning("No TrueType font found; using Pillow's default font")
  return ImageFont.load_default()


def fit_bottom_text(draw, text):
  """Return (font, bbox) for the largest size where every line fits."""
  size = BOTTOM_FONT_SIZE
  while True:
    font = load_font(size)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=10, align="center")
    if bbox[2] - bbox[0] <= TEXT_LENGTH_MAX or size <= 40:
      return font, bbox
    size -= 5


def paste_logo(booth_image, logo_path, box_top, box_bottom):
  """Scale the logo to fit the box between box_top and box_bottom and
  center it horizontally."""
  logo = Image.open(logo_path).convert("RGBA")
  max_w = min(LOGO_MAX_WIDTH, STRIP_WIDTH - 2 * STRIP_BORDER)
  max_h = box_bottom - box_top
  scale = min(max_w / logo.width, max_h / logo.height)
  new_size = (max(1, round(logo.width * scale)), max(1, round(logo.height * scale)))
  logo = logo.resize(new_size, Image.LANCZOS)
  x = (STRIP_WIDTH - logo.width) // 2
  y = box_top + (max_h - logo.height) // 2
  booth_image.paste(logo, (x, y), logo)


def build_strip(images, logo=None, bottom_text=None):
  """Build the photo strip and return it as a PIL Image.
  images: list of photo paths or PIL Images."""
  logo = logo or LOGO
  bottom_text = BOTTOM_TEXT if bottom_text is None else bottom_text
  booth_image = Image.new('RGB', (STRIP_WIDTH, STRIP_LENGTH), (255, 255, 255))

  # Photos, centered horizontally, stacked from PHOTO_TOP
  y = PHOTO_TOP
  for img in images:
    photo = img if isinstance(img, Image.Image) else Image.open(img)
    x = (STRIP_WIDTH - photo.width) // 2
    booth_image.paste(photo, (x, y))
    y += PHOTO_STEP

  # Bottom text: centered, bottom just above the strip border
  draw = ImageDraw.Draw(booth_image)
  font, (left, top, right, bottom) = fit_bottom_text(draw, bottom_text)
  text_x = (STRIP_WIDTH - (right - left)) // 2 - left
  text_y = STRIP_LENGTH - STRIP_BORDER - 20 - bottom
  draw.multiline_text((text_x, text_y), bottom_text, font=font, fill=TEXT_COLOR, spacing=10, align="center")

  # Logo fills the space between LOGO_TOP and the top of the text
  logo_path = Path(logo)
  if not logo_path.is_absolute():
    logo_path = HERE / logo_path
  paste_logo(booth_image, logo_path, LOGO_TOP, text_y + top - LOGO_GAP)
  return booth_image


def make_booth_image(images):
  """Make photobooth image from the photos and save it next to them."""
  logging.info("make_booth_image function begin")
  folder_path = Path(images[0]).parent
  build_strip(images).save(f'{folder_path}/booth_image.jpg')
  return f'{folder_path}/booth_image.jpg'


def build_print_sheet(strip):
  """Two strips side by side, shifted by PRINT_OFFSET_X/Y."""
  sheet = Image.new('RGB', (2 * strip.width, strip.height), (255, 255, 255))
  for i in range(2):
    sheet.paste(strip, (i * strip.width + PRINT_OFFSET_X, PRINT_OFFSET_Y))
  return sheet


def printable_image(booth_image):
  """Make the image ready for printing. The printer needs an image that
  is a composition of two photobooth strips side-by-side."""
  logging.info("printable_image function begin")
  folder_path = Path(booth_image).parent
  new_name = Path(booth_image).stem
  print_image = f'{folder_path}/{new_name}_double.jpg'
  build_print_sheet(Image.open(booth_image)).save(print_image)
  return print_image
