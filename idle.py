import subprocess
import time
import tkinter as tk
import urllib.request
from datetime import datetime
from pathlib import Path

import qrcode
from gpiozero import LED, Button
from picamera import PiCamera
from PIL import Image, ImageDraw, ImageFont, ImageTk
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


######################################################################
#
#        Config Settings
#
######################################################################
# Store the files in the Pictures folder of the users' home directory
# The base image folder should be ~/Pictures/booth_pics/
SIMPLEPATH = Path('/home/pi/simplebooth')
BOOTH_IMAGE_PATH = Path(f'/home/pi/Pictures/booth_pics')

# Pinout https://pinout.xyz
# purple wire (switch) to physical/board pin 7
# black wire (both ground) to physical/board pin 9
# blue wire (LED) to physical/board pin 11
BUTTON_PIN = 4
LED_PIN = 17

TEXT_BOX_1 = "Seize the day!"
TEXT_BOX_2 = "Scholars' Lab TinkerTank"

PRINTER_NAME = "MITSUBISHI_CK60D70D707D"
#PRINTER_NAME = "NO PRINT"
##################### END CONFIG SETTINGS ############################


######################################################################
# TODO:
# - Auto format the text to fit in the space without needing new line characters
# - Center text and QR horizontally and vertically in instructions and showing QR code
# - Sleep if inactive for 30 seconds. 
######################################################################


# Set up button and camera objects
blue_button = Button(BUTTON_PIN)
blue_led = LED(LED_PIN)
camera = PiCamera(resolution=(1920,1080), framerate=15, sensor_mode=5)
# flip camera vertically, upside down or right side up
#camera.rotation = 180
# flip horizontally so it doesn't look backwards
camera.hflip = True


win = tk.Tk()
win.attributes('-fullscreen',True) 
screen_width = win.winfo_screenwidth()

# show idle instructions
instructions = tk.StringVar()
instruct_label = tk.Label(win, textvariable=instructions, font=("Arial", 85), wraplength=screen_width)

booth_icon = Image.open("simplebooth-icon.png")
pic = ImageTk.PhotoImage(booth_icon)
icon_label = tk.Label(win, image = pic)
icon_label.image = pic

#####################################################################
#
#  QR Code and Google Drive
gdrive_status = False
try:
  gauth = GoogleAuth()
  gauth.LocalWebserverAuth()
  drive = GoogleDrive(gauth)
  gdrive_status = True
except:
  gdrive_status = False

def upload_image(image_file):
    gfile = drive.CreateFile({'parents': [{'id': '1FEH74jojf7WPOYk0ILqexKMs-ezGwGnE'}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(image_file)
    gfile.Upload() # Upload the file.
    return gfile.metadata['webContentLink']

def make_qr(fileUrl):
    camera.stop_preview()
    qr = qrcode.make(fileUrl)
    qr.save(f'{SIMPLEPATH}/qrimage.png')
    icon_label.destroy()
    instructions.set("While your photo is printing, scan this code to download your image!")
    qrImage = tk.PhotoImage(file=f'{SIMPLEPATH}/qrimage.png')
    qrLabel = tk.Label(win, image=qrImage)
    qrLabel.grid(row=1)
    time.sleep(20)
    qrLabel.grid_remove()
#####################################################################


def connected(host='https://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


# Check for base image folder, create if doesn't exist
# Run this at start up of the script
def check_image_folder():
  if Path(BOOTH_IMAGE_PATH).exists:
    return True
  else:
    Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()




def show_idle_instructions():
    camera.stop_preview()
    blue_led.blink()

    booth_icon = Image.open("simplebooth-icon.png")
    pic = ImageTk.PhotoImage(booth_icon)
    icon_label = tk.Label(win, image = pic)
    icon_label.image = pic
    icon_label.grid(row=1)

    instructions.set(f"Press the button to take pictures!")
    instruct_label.grid(row=2)

    blue_button.when_pressed = button_pressed



# Take the pictures
# Returns the path to the directory where photos are stored
def take_pics():
  icon_label.destroy()

  # Make a folder to store the photos of this session
  # Format the folder name as "YYYY-MM-DD-HH-MM-SS"
  timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
  Path(f'{str(BOOTH_IMAGE_PATH)}/{timestamp}').mkdir()
  folder_path = Path(f'{str(BOOTH_IMAGE_PATH)}/{str(timestamp)}')

  image_list = []

  for i in range(1,4):
    for n in range(3,0,-1):
      img = Image.open(f'{SIMPLEPATH}/count_down/{n}.png')
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
    # show white screen
    camera.stop_preview()
    instructions.set("")
    instruct_label.grid_remove()
    camera.start_preview()

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
  fnt1 = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 130)
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


# Set default printer 
def printer_default(printer_name):
  # Set the default printer to the one desired
  current_default = subprocess.run(["lpstat", "-d"], capture_output=True)
  if printer_name not in current_default.stdout.decode("utf-8"):
    subprocess.run(["lpoptions", "-d", printer_name])
    current_default = printer_name

def printer_check(printer_name):
  # Check if desired printer is attached
  attached_printers = subprocess.run(['lpstat', '-p'], capture_output=True)
  if printer_name in attached_printers.stdout.decode('utf-8'):
    return True
  else:
    return False



# Send booth image to printer
# - use the basic CUPS lp command
# - TODO: look into using pycups library
def print_booth_image(printable_image):
  output = subprocess.run(["lp", "-d", PRINTER_NAME, printable_image], capture_output=True)
  return True
  



def button_pressed():
  if(gdrive_status):
    instructions.set("Get ready to take 3 pictures. Then scan the QR code to download the image.")
  else:
    instructions.set("Get ready to take 3 pictures.")

  time.sleep(6)
  instruct_label.grid_remove()

  camera.start_preview()
  blue_led.off()
  images = take_pics()
  camera.stop_preview()

  booth_icon = Image.open("simplebooth-icon.png")
  pic = ImageTk.PhotoImage(booth_icon)
  icon_label = tk.Label(win, image = pic)
  icon_label.image = pic
  icon_label.grid(row=1)
  instruct_label.grid(row=2)
  instructions.set("Please wait while pictures are created.")

  booth_image = make_booth_image(images)
  final_image = printable_image(booth_image)

  if printer_check(PRINTER_NAME) :
    print_booth_image(final_image)
    print("printing image")
  
  if (has_internet and gdrive_status):
    fileUrl = upload_image(booth_image)
    make_qr(fileUrl)
    print("uploading file and making QR code")

  blue_led.blink()
  show_idle_instructions()



# The main running code
has_internet = connected()

blue_led.blink()

show_idle_instructions()

# Escape key closes app
def close_window(e):
  win.destroy()
  exit()

win.bind('<Escape>', lambda e: close_window(e))
win.mainloop()
