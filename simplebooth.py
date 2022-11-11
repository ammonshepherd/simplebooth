import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause

# Store the files in the Pictures folder of the users' home directory
# The base image folder should be ~/Pictures/booth_pics/
HOME = Path.home()
BOOTH_IMAGE_PATH = Path(f'{str(HOME)}/Pictures/booth_pics')
BUTTON_PIN = 2

TEXT_BOX_1 = "Make it a GREAT day!"
TEXT_BOX_2 = "Scholars' Lab TinkerTank"

COUNT3 = Image.open('./count_down/3.png')
COUNT2 = Image.open('./count_down/2.png')
COUNT1 = Image.open('./count_down/1.png')

# Set up button and camera objects
#the_button = Button(BUTTON_PIN)
the_camera = PiCamera()

# Check for base image folder, create if doesn't exist
# Run this at start up of the script
def check_image_folder():
  if Path(BOOTH_IMAGE_PATH).exists:
    return True
  else:
    Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()

check_image_folder()


# Show Controls
# - show text/image to click button to take a pictures



# Take the pictures
# Returns the path to the directory where photos are stored
def take_pics():
  # Make a folder to store the photos of this session
  # Format the folder name as "YYYY-MM-DD-HH-MM-SS"
  timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
  Path(f'{str(BOOTH_IMAGE_PATH)}/{timestamp}').mkdir()
  folder_path = Path(f'{str(BOOTH_IMAGE_PATH)}/{str(timestamp)}')

  image_list = []

  for i in range(1,4):
    the_camera.start_preview(resolution=(1024,768))
    for n in range(3,0,-1):
      img = Image.open(f'./count_down/{n}.png')
      pad = Image.new('RGBA', (
          ((img.size[0] + 31) // 32) * 32,
          ((img.size[1] + 15) // 16) * 16,
          ))
      pad.paste(img, (0, 0))
      o = the_camera.add_overlay(pad.tobytes(), size=img.size)
      o.alpha = 32
      o.layer = 3
      time.sleep(1)
      the_camera.remove_overlay(o)
    the_camera.capture(f'{folder_path}/{timestamp}_{i}.jpg', resize=(1120, 840))
    the_camera.stop_preview()
    image_list.append(f'{folder_path}/{timestamp}_{i}.jpg')
  return image_list




# Make photobooth image
# - make a new image using the 3 pictures taken
def make_booth_image(images):
  folder_path = Path(images[0]).parent
  booth_image = Image.new('RGB', (1200, 3600), (230,230,230))
  x, y = 40, 40
  for img in images:
    new_img = Image.open(img)
    booth_image.paste(new_img, (x, y))
    y = y + 880
  # Add the main, big text box
  fnt1 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 210)
  text_1 = ImageDraw.Draw(booth_image)
  text_1.multiline_text((40, 2680), "Lighting\n of the Lawn\n 2022!", font=fnt1, fill=(35, 45, 75), spacing=20, align="center", stroke_width=4, stroke_fill=(229,114,0))

  # add the smaller text
  fnt2 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
  text_2 = ImageDraw.Draw(booth_image)
  text_2.multiline_text((40, 3420), "Scholars' Lab TinkerTank", font=fnt2, fill=(248, 76, 30), align="center")

  booth_image.save(f'{folder_path}/booth_image.jpg')
  return f'{folder_path}/booth_image.jpg'





# Make duplicate of booth image ready for printing
def printable_image(booth_image):
  folder_path = Path(booth_image).parent
  img = Image.open(booth_image)
  new_img = Image.new('RGB', (2*img.size[0], img.size[1]), (250,250,250))
  new_img.paste(img, (0,0))
  new_img.paste(img, (img.size[0],0))
  new_name = Path(booth_image).stem
  new_img.save(f'{folder_path}/{new_name}_double.jpg')
  # return full path and file name
  print_image = f'{folder_path}/{new_name}_double.jpg'
  return print_image





# Send booth image to printer
# - use the basic CUPS lp command
# - TODO: look into using pycups library
def print_booth_image(printable_image):
  output = subprocess.run(["lp", printable_image], capture_output=True)
  print('command: lp')
  print('Return Code: ', output.returncode)
  print('Output: ', output.stdout.decode("utf-8"))
  
# print_booth_image(print_it)



def button_pressed():
  images = take_pics()
  booth_image = make_booth_image(images)
  print_it = printable_image(booth_image)
  # print_booth_image(print_it)

# The main running code
# the_button.when_pressed = button_pressed()
# pause()
button_pressed()