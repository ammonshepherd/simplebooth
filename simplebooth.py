import time
import subprocess
from pathlib import Path
from PIL import Image
from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause

# Store the files in the Pictures folder of the users' home directory
HOME = str(Path.home())
BOOTH_IMAGE_PATH = Path(f'{HOME}/Pictures/booth_pics')
BUTTON_PIN = 2

# Set up button and camera objects
the_button = Button(BUTTON_PIN)
the_camera = PiCamera()


# Take the pictures
def take_pics():
  try:
    # Format the folder name as "YYYY-MM-DD-HH-MM-SS"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    Path(f'{str(BOOTH_IMAGE_PATH)}/{timestamp}').mkdir()
    folder_path = Path(f'{str(BOOTH_IMAGE_PATH)}/{str(timestamp)}')
    print("3")
    time.sleep(1)
    the_camera.capture(f'{folder_path}/{timestamp}_1.jpg')
    print("2")
    time.sleep(1)
    the_camera.capture(f'{folder_path}/{timestamp}_2.jpg')
    print("1")
    time.sleep(1)
    the_camera.capture(f'{folder_path}/{timestamp}_3.jpg')
  except FileExistsError:
    print("ERROR: Folder path already exists")
    print(FileExistsError)
    pass
  return folder_path


# Show Controls
# - show text/image to click button to take a pictures

# Take Picture
# - code to take 3 pictures using Pi Camera
# - store the photo in an image with name DD-MM-YY-TIMESTAMP.jpg

# Make photobooth image
# - make a new image using the 3 pictures taken
def make_booth_image():
  current_booth_image = Image.new('RGB', (1200, 3600), (250,250,250))
  return current_booth_image

# Make duplicate of booth image ready for printing
def printable_image(current_booth_image, current_booth_folder):
  img = Image.open(BOOTH_IMAGE_PATH/current_booth_image)
  print(f"Adding {img}", img.size[0], img.size[1])
  new_img = Image.new('RGB', (2*img.size[0], img.size[1]), (250,250,250))
  new_img.paste(img, (0,0))
  new_img.paste(img, (img.size[0],0))
  new_name = Path(img).stem
  new_img.save(f'{BOOTH_IMAGE_PATH}/{current_booth_folder}/{new_name}_double.jpg')

# Send booth image to printer
# - use the basic CUPS lp command
# - TODO: look into using pycups library
def print_booth_image(printable_image):
  output = subprocess.run(["lp", printable_image], capture_output=True)
  print('command: lp')
  print('Return Code: ', output.returncode)
  print('Output: ', output.stdout.decode("utf-8"))
  

# The main running code
the_button.when_pressed = take_pics
pause()
