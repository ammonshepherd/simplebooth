import time
import random
import textwrap
import mimetypes
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

from gpiozero import LED, Button
from picamera import PiCamera

import qrcode

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='photobooth.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M",)


######################################################################
#
#     CONFIG SETTINGS
#     settings that users can change
#######################################################################
# path to the folder where the simplebooth script lives
SIMPLEPATH = Path('/home/pi/simplebooth')
# Store the files in the Pictures folder of the users' home directory
# Format: /home/<username>/Pictures/simplebooth_pictures/
BOOTH_IMAGE_PATH = Path(f'/home/pi/Pictures/simplebooth_pictures/')

# pinout https://pinout.xyz
# purple wire (switch) to physical/board pin 7
# black wire (both ground) to physical/board pin 9
# blue wire (led) to physical/board pin 11
BUTTON_PIN = 4
LED_PIN = 17

# Set the number of pictures to take
# currently, this program only prints one type of photo strip, three
# images stacked on top of each other. Things will break if you change
# this number to anything other than 3. Better functionality will come
# in the future...
NUM_PICS = 3

# Messages to print at the bottom of the photobooth strip
TOP_TEXT = ["Be the best you can, so you can do the best you can!",
       "Do good, be good, but if you have to choose, be good.",
       "Make it a GREAT day!",
       "Sieze the day!",
       "Ya'll are AWESOME!",
       "WE GOT THIS!",
       "BFF!",
        "We so cool!"]
BOTTOM_TEXT = "Scholars' Lab Makerspace"
#TOP_TEXT = ["Lighting of the Lawn 2023"]

# Photo strip settings
STRIP_BORDER = 40
STRIP_WIDTH = 1200
STRIP_LENGTH = 3600
# Top text settings
TEXT_LENGTH_MAX = STRIP_WIDTH - (STRIP_BORDER * 2) - 20
TOP_TEXT_HEIGHT_MIN = 630
TOP_TEXT_HEIGHT_MAX = 680

PRINTER_NAME = "MITSUBISHI_CK60D70D707D"

# Google Drive settings
# CRED_FILE is the service account key (keep very secret, no versioning).
# FOLDER_ID is the ID for the folder in the tinkertank.uva Google Drive where
# files are stored.
CRED_FILE = 'service_account.json'

# simplebooth_photos
#FOLDER_ID = '1FEH74jojf7WPOYk0ILqexKMs-ezGwGnE'

# LOTL2023
FOLDER_ID = '1jAr4lmGHtwSUDuI6jT8k9XXIIYFnb1dw'
##################### END CONFIG SETTINGS ############################


######################################################################
#
#    GUI Settings
#
######################################################################
win = tk.Tk()
win.attributes('-fullscreen', True)
screen_width = win.winfo_screenwidth()
win.grid_columnconfigure((0, 2), weight=1)
win.configure(bg="black")

# Create the instructions variable and label
instructions_text = tk.StringVar()
instructions_label = tk.Label(win, textvariable=instructions_text, font=(
  "Arial", 85), wraplength=screen_width, bg="black", fg="white")
# Create the logo label
booth_icon = Image.open("simplebooth-icon.png")
pic = ImageTk.PhotoImage(booth_icon)
logo_label = tk.Label(win, image=pic, bg="black")
logo_label.image = pic
##################### END GUI SETTINGS ############################


######################################################################
#
#    HARDWARE SETUP
#
#######################################################################
# Button Settings
# set up button and LED objects
blue_button = Button(BUTTON_PIN)
blue_led = LED(LED_PIN)

# Camera settings
# resolution based on the attached monitor
camera = PiCamera(resolution=(1920, 1080), framerate=15, sensor_mode=5)
# flip horizontally so it doesn't look backwards
camera.hflip = True
# flip camera vertically, upside down or right side up
# camera.rotation = 180
##################### END HARDWARE SETUP ############################


######################################################################
#
#    Functions
#
#######################################################################

def main_screen():
  """Show the main screen to get users to push the button."""
  logging.info('main_screen function begin')

  global logo_label
  global instructions_text
  global instructions_label

  # Blink the button LED
  blue_led.blink()

  # Show the logo and text
  logo_label.grid(row=0, column=1, sticky="ew")
  instructions_text.set("Press the button to take pictures!")
  instructions_label.grid(row=1, column=1, sticky="ew")

  # Wait for the button to be pressed, then fire off the function
  blue_button.when_pressed = button_pressed


def button_pressed():
  """After button press, take the pictures, print pictures, and if
  available, upload pictures to Google Doc and show a QR Code. Then
  show the main screen."""
  logging.info("button_pressed function begin")

  global connected
  global logo_label
  global instructions_text
  global instructions_label

  # Turn off the blinking
  blue_led.off()

  # Set new instructions_text, and pause for 6 seconds
  instructions_text.set(f"Get ready to take {NUM_PICS} pictures!")
  time.sleep(3)

  # Remove the logo and the instructions_text
  logo_label.grid_remove()
  instructions_label.grid_remove()

  # Start the camera, call the function to take pictures, and store
  # the paths to the pictures in the list
  logging.info("Starting picture taking process")
  camera.start_preview()
  images = take_pics(NUM_PICS)
  camera.stop_preview()
  logging.info("Ending picture taking process")

  # Make the photobooth image, and the doubled image for printing
  booth_image = make_booth_image(images)
  final_image = printable_image(booth_image)

  if printer_check(PRINTER_NAME):
    logging.info("Printer check returned true. Print the images.")
    print_booth_image(final_image)


  # If connected to internet, upload image to Google Drive and create QR code
  if (connected):
    logging.info("Connected to Internet, send file to GDrive")
    fileUrl = upload_to_gdrive(booth_image)
    if(fileUrl):
      logging.info("File uploaded to GDrive, so here's the QR code.")
      make_qr(fileUrl)
  else:
    logging.info("No network connection, so just display message.")
    # Show logo and instructions while images are created and printed
    logo_label.grid(row=0, column=1, sticky="ew")
    instructions_text.set("Please wait while the picture is printing.")
    instructions_label.grid(row=1, column=1, sticky="ew")

  # And back to the main screen
  main_screen()


def take_pics(num_pics):
  """Take the pictures and return the path to the directory where the
  photos are stored."""
  logging.info("take_pics function begin.")

  global logo_label
  global instructions_text
  global instructions_label

  # remove logo and instructions
  logo_label.grid_remove()
  instructions_text.set("")
  instructions_label.grid_remove()

  # Make a folder to store the photos of this session
  # Format the folder name as "YYYY-MM-DD-HH-MM-SS"
  timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
  Path(f'{str(BOOTH_IMAGE_PATH)}/{timestamp}').mkdir()
  folder_path = Path(f'{str(BOOTH_IMAGE_PATH)}/{str(timestamp)}')

  image_list = []

  # set the background to be white
  win.configure(bg="white")

  # Loop to take num_pics number of pictures
  for i in range(1, num_pics+1):
    # Loop to show the countdown numbers
    for n in range(3, 0, -1):
      img = Image.open(f'{SIMPLEPATH}/count_down/{n}.png')
      pad = Image.new('RGBA', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
      ))
      pad.paste(img, (0, 0))
      # add the number as an overlay
      o = camera.add_overlay(pad.tobytes(), size=img.size)
      o.alpha = 32
      o.layer = 3
      time.sleep(1)
      camera.remove_overlay(o)
    # stop camera preview to show white screen for a split second
    camera.stop_preview()
    camera.start_preview()
    # image size based on three images for a classic photostrip
    camera.capture(f'{folder_path}/{timestamp}_{i}.jpg',
             resize=(1120, 840))
    image_list.append(f'{folder_path}/{timestamp}_{i}.jpg')

  # return the background to black
  win.configure(bg="black")
  return image_list


def check_image_folder():
  """Check for base image folder. Create if it doesn't exist."""
  logging.info("check_image_folder function begin")

  if Path(BOOTH_IMAGE_PATH).exists():
    logging.info("Folder path exists: %s", BOOTH_IMAGE_PATH)
    return True
  else:
    Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()
    logging.warning("Folder path did not exist so it was created: %s", BOOTH_IMAGE_PATH)
    return True


def make_booth_image(images):
  """Make photobooth image. Use images in the given path to create the
  photobooth image that will be printed."""
  logging.info("make_booth_image function begin")
  # Currently, the only option is the classic, three stacked images

  folder_path = Path(images[0]).parent
  booth_image = Image.new(
    'RGB', (STRIP_WIDTH, STRIP_LENGTH), (255, 255, 255))
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
  vert_centered_spacing = (TOP_TEXT_HEIGHT_MAX-get_text_lh((STRIP_BORDER, 2680), top_text, long_text, font1)[1])//2
  print(vert_centered_spacing)
  top_text.multiline_text((STRIP_BORDER, 2680+vert_centered_spacing), long_text, font=font1, fill=(
    35, 45, 75), spacing=20, align="center")

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
  logging.info("create_text function begin")
  font_size = 180
  wrapped_height = 100
  wrapped_text = ""

  font1 = ImageFont.truetype(
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf", font_size)
  wrap_size = get_wrap(text_obj, text, font1)

  while (wrapped_height < height_min) or (wrapped_height > height_max):
    font1 = ImageFont.truetype(
      "/usr/share/fonts/truetype/freefont/FreeSans.ttf", font_size)
    wrap_size = get_wrap(text_obj, text, font1)
    wrapped_text = textwrap.fill(text, wrap_size)
    wrapped_length, wrapped_height = get_text_lh(
      (STRIP_BORDER, 2680), text_obj, wrapped_text, font1)
    if wrapped_length > TEXT_LENGTH_MAX:
      break
    if wrapped_height > height_max:
      font_size -= 10
    elif wrapped_height < height_min:
      font_size += 10

  return wrapped_text, font1


def get_wrap(text_obj, text, the_font):
  """ Get the number of characters to wrap the text at 1100 pixels """
  logging.info("get_wrap function being")
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
  logging.info("get_text_lh function begin")
  left, top, right, bottom = text_obj.multiline_textbbox(
    xy, text, font=the_font)
  length = right - left
  height = bottom - top
  return length, height


def printable_image(booth_image):
  """Make the image ready for printing. The printer needs an image that
  is a composition of two photobooth strips side-by-side."""
  logging.info("printable_image function begin")

  folder_path = Path(booth_image).parent
  img = Image.open(booth_image)
  new_img = Image.new('RGB', (2*img.size[0], img.size[1]), (250, 250, 250))
  new_img.paste(img, (0, 0))
  new_img.paste(img, (img.size[0], 0))
  new_name = Path(booth_image).stem
  new_img.save(f'{folder_path}/{new_name}_double.jpg')
  # return full path and file name
  print_image = f'{folder_path}/{new_name}_double.jpg'
  return print_image


def has_internet(host='https://google.com'):
  """ Check if the Pi has connection to the internet """
  logging.info("has_internet function begin")

  try:
    urllib.request.urlopen(host)
    logging.info("Internet connection established.")
    return True
  except:
    logging.warning("No internet connection")
    return False


def upload_to_gdrive(file_path):
  """ Upload the photobooth image to the Google Drive folder and return the URL
  to dowload the image. """
  logging.info("upload_to_gdrive function begin")

  global CRED_FILE
  global FOLDER_ID

  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  creds = service_account.Credentials.from_service_account_file(CRED_FILE)
  scoped = creds.with_scopes(SCOPES)

  file_name = Path(file_path).parts[5] + "-" + Path(file_path).name
  mime_type = mimetypes.guess_type(file_path)

  try:
    logging.info("Uploading file %s to GDrive.", file_name)
    service = build("drive", "v3", credentials=scoped)

    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    image_file = MediaFileUpload(file_path, mimetype=mime_type[0], resumable=True)
    file = service.files().create(body=file_metadata, media_body=image_file, fields='webViewLink').execute()
    return file.get('webViewLink')

  except HttpError as error:
    logging.warning("Can't connect to GDrive or upload the file. Error: %s", error)
    print(f'Thus an error: {error}')
    print(f'Check if this app can connect to the Google Account. Does the service account key file still exist?')
    quit()
    return None


def make_qr(fileUrl):
  """ Create a QR code of the URL to download the image """
  logging.info("make_qr function begin")

  global logo_label
  global instructions_text
  global instructions_label

  camera.stop_preview()
  qr = qrcode.make(fileUrl)
  qr.save(f'{SIMPLEPATH}/qrimage.png')
  logo_label.grid_remove()
  instructions_text.set(
    "While your photo is printing, scan this code to download your image!")
  instructions_label.grid(row=1, column=1, sticky="ew")
  qrImage = tk.PhotoImage(file=f'{SIMPLEPATH}/qrimage.png')
  qrLabel = tk.Label(win, image=qrImage)
  qrLabel.config(bg="black")
  qrLabel.grid(row=0, column=1, sticky="ew")
  time.sleep(20)
  qrLabel.grid_remove()


# - TODO: look into using pycups library
def print_booth_image(printable_image):
  """ Send the booth image to the printer """
  logging.info("print_booth_image function begin")
  try:
    logging.info("Pringing image file.")
    output = subprocess.run(["lp", "-d", PRINTER_NAME, printable_image], capture_output=True)
  except:
    logging.warning("Image failed to print.")
    print(output)
  return True


def printer_check(printer_name):
  """ Check if the printer is connected """
  logging.info("printer_check function begin. printer_name = %s", printer_name)

  attached_printers = subprocess.run(['lpstat', '-p'], capture_output=True)
  if printer_name in attached_printers.stdout.decode('utf-8'):
    logging.info("Connected to %s", printer_name)
    return True
  else:
    logging.warning("Could not connect to printer: %s", printer_name)
    return False


######################################################################
#
#    Main Script Functionality
#
#######################################################################
# Check for the folder to store images.
check_image_folder()

# Check if connected to the internet
connected = False
if (has_internet):
  connected = True
else:
  connected = False

# Call the main screen function to get things going!
main_screen()


# Escape key closes app
def close_window(e):
  win.destroy()
  exit()
win.bind('<Escape>', lambda e: close_window(e))

win.mainloop()
