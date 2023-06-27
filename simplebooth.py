import time
from datetime import datetime
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

from gpiozero import LED, Button
from picamera import PiCamera

######################################################################
#
#         CONFIG SETTINGS
#         settings that users can change
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
TOP_TEXT = "Make it a GREAT day!"
BOTTOM_TEXT = "Scholars' Lab TinkerTank"
##################### END CONFIG SETTINGS ############################


######################################################################
#
#        GUI Settings
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
#        HARDWARE SETUP
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
#        Functions
#
#######################################################################

def main_screen():
    """Show the main screen to get users to push the button."""

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

    global logo_label
    global instructions_label
    global instructions_text

    # Turn off the blinking
    blue_led.off()

    # Set new instructions_text, and pause for 6 seconds
    instructions_text.set(f"Get ready to take {NUM_PICS} pictures!")
    time.sleep(6)

    # Remove the logo and the instructions_text
    logo_label.grid_remove()
    instructions_label.grid_remove()

    # Start the camera, call the function to take pictures, and store
    # the paths to the pictures in the list
    camera.start_preview()
    images = take_pics(NUM_PICS)
    camera.stop_preview()

    # Show logo and instructions while images are created and printed
    logo_label.grid(row=0, column=1, sticky="ew")
    instructions_text.set("Please wait while the picture is printing.")
    instructions_label.grid(row=1, column=1, sticky="ew")

    # make the photobooth image, and the doubled image for printing
    booth_image = make_booth_image(images)
    final_image = printable_image(booth_image)

    # And back to the main screen
    main_screen()


def take_pics(num_pics):
    """Take the pictures and return the path to the directory where the
    photos are stored."""

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

    if Path(BOOTH_IMAGE_PATH).exists():
        return True
    else:
        Path(f'{str(BOOTH_IMAGE_PATH)}').mkdir()
        return True


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
    font1 = ImageFont.truetype( "/usr/share/fonts/truetype/freefont/FreeSans.ttf")
    top_text = ImageDraw.Draw(booth_image)
    top_text.multiline_text((40, 2680), TOP_TEXT, font=font1, fill=(
        35, 45, 75), spacing=20, align="center", stroke_width=8, stroke_fill=(229, 114, 0))

    # add the smaller text
    font2 = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf", 90)
    bottom_text = ImageDraw.Draw(booth_image)
    bottom_text.multiline_text((40, 3420), BOTTOM_TEXT, font=font2,
                               fill=(248, 76, 30), align="center")

    booth_image.save(f'{folder_path}/booth_image.jpg')
    return f'{folder_path}/booth_image.jpg'


def printable_image(booth_image):
    """Make the image ready for printing. The printer needs an image that 
    is a composition of two photobooth strips side-by-side."""

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


######################################################################
#
#        Main Script Functionality
#
#######################################################################
# Check for the folder to store images.
check_image_folder()

# Call the main screen function to get things going!
main_screen()


# Escape key closes app
def close_window(e):
    win.destroy()
    exit()
win.bind('<Escape>', lambda e: close_window(e))

win.mainloop()
