import time
import subprocess
from pathlib import Path
from PIL import Image
from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause

# Store the files in the Pictures folder of the users' home directory
# The base image folder should be ~/Pictures/booth_pics/
HOME = Path.home()
BOOTH_IMAGE_PATH = Path(f'{str(HOME)}/Pictures/booth_pics')
BUTTON_PIN = 2

# Set up button and camera objects
the_button = Button(BUTTON_PIN)
the_camera = PiCamera()

# Check for base image folder, create if doesn't exist
# Run this at start up of the script
def check_image_folder(BOOTH_IMAGE_PATH):
  if Path(BOOTH_IMAGE_PATH).exists:
    return True
  else:
    Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()


# Take the pictures
# Returns the path to the directory where photos are stored
def take_pics():
  try:
    # Make a folder to store the photos of this session
    # Format the folder name as "YYYY-MM-DD-HH-MM-SS"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    Path(f'{str(BOOTH_IMAGE_PATH)}/{timestamp}').mkdir()
    folder_path = Path(f'{str(BOOTH_IMAGE_PATH)}/{str(timestamp)}')

    for i in range(1,3):
      the_camera.start_preview()
      the_camera.annotate_text = '3'
      time.sleep(1)
      the_camera.annotate_text = '2'
      time.sleep(1)
      the_camera.annotate_text = '1'
      time.sleep(1)
      the_camera.capture(f'{folder_path}/{timestamp}_{i}.jpg')
      the_camera.stop_preview()

  except FileExistsError:
    print("ERROR: Folder path already exists")
    print(FileExistsError)
    pass
  return folder_path

# Show Controls
# - show text/image to click button to take a pictures

# Make photobooth image
# - make a new image using the 3 pictures taken
def make_booth_image(folder_path):
  booth_image = Image.new('RGB', (1200, 3600), (250,250,250))
  return booth_image

# Make duplicate of booth image ready for printing
def printable_image(booth_image, folder_path):
  img = Image.open(folder_path/booth_image)
  print(f"Adding {img}", img.size[0], img.size[1])
  new_img = Image.new('RGB', (2*img.size[0], img.size[1]), (250,250,250))
  new_img.paste(img, (0,0))
  new_img.paste(img, (img.size[0],0))
  new_name = Path(img).stem
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
  

# The main running code
# the_button.when_pressed = take_pics
# pause()
