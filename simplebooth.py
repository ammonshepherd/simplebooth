import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button, LED
from picamera import PiCamera
from datetime import datetime
from signal import pause

# Store the files in the Pictures folder of the users' home directory
# The base image folder should be ~/Pictures/booth_pics/
HOME = Path.home()
BOOTH_IMAGE_PATH = Path(f'{str(HOME)}/Pictures/booth_pics')

# Pinout https://pinout.xyz
# purple wire (switch) to physical/board pin 7
# black wire (both ground) to physical/board pin 9
# blue wire (LED) to physical/board pin 11
BUTTON_PIN = 4
LED_PIN = 17

TEXT_BOX_1 = "Lighting\n of the Lawn\n 2022"
TEXT_BOX_2 = "Scholars' Lab TinkerTank"

PRINTER_NAME = "MITSUBISHI_CK60D70D707D"

# Set up button and camera objects
blue_button = Button(BUTTON_PIN)
blue_led = LED(LED_PIN)
camera = PiCamera()

# Check for base image folder, create if doesn't exist
# Run this at start up of the script
def check_image_folder():
  if Path(BOOTH_IMAGE_PATH).exists:
    return True
  else:
    Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()



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
    for n in range(3,0,-1):
      img = Image.open(f'./count_down/{n}.png')
      pad = Image.new('RGBA', (
          ((img.size[0] + 31) // 32) * 32,
          ((img.size[1] + 15) // 16) * 16,
          ))
      pad.paste(img, (0, 0))
      o = camera.add_overlay(pad.tobytes(), size=img.size)
      o.alpha = 32
      o.layer = 3
      time.sleep(1)
      camera.remove_overlay(o)
    camera.capture(f'{folder_path}/{timestamp}_{i}.jpg', resize=(1120, 840))
    image_list.append(f'{folder_path}/{timestamp}_{i}.jpg')
  return image_list




# Make photobooth image
# - make a new image using the 3 pictures taken
def make_booth_image(images):
  folder_path = Path(images[0]).parent
  booth_image = Image.new('RGB', (1200, 3600), (255,255,255))
  x, y = 40, 40
  for img in images:
    new_img = Image.open(img)
    booth_image.paste(new_img, (x, y))
    y = y + 880
  # Add the main, big text box
  fnt1 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 210)
  text_1 = ImageDraw.Draw(booth_image)
  text_1.multiline_text((40, 2680), TEXT_BOX_1, font=fnt1, fill=(35, 45, 75), spacing=20, align="center", stroke_width=8, stroke_fill=(229,114,0))

  # add the smaller text
  fnt2 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
  text_2 = ImageDraw.Draw(booth_image)
  text_2.multiline_text((40, 3420), TEXT_BOX_2, font=fnt2, fill=(248, 76, 30), align="center")

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


# Check that the correct printer is selected. Set it as default if not.
def printer_check(printer_name):
    current_default = subprocess.run(["lpstat", "-d"], capture_output=True)
    if printer_name not in current_default.stdout.decode("utf-8"):
        subprocess.run(["lpoptions", "-d", printer_name])
        current_default = printer_name
    #print(current_default)



# Send booth image to printer
# - use the basic CUPS lp command
# - TODO: look into using pycups library
def print_booth_image(printable_image):
  output = subprocess.run(["lp", printable_image], capture_output=True)
  



def button_pressed():
  blue_led.off()
  images = take_pics()
  booth_image = make_booth_image(images)
  print_it = printable_image(booth_image)
  printer_check(PRINTER_NAME)
  print_booth_image(print_it)
  blue_led.blink()

# The main running code
camera.start_preview()
blue_led.blink()
blue_button.when_pressed = button_pressed
pause()
