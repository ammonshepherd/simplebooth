import time

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

from gpiozero import LED, Button

######################################################################
#
#         CONFIG SETTINGS
#         settings that users can change
#######################################################################
# pinout https://pinout.xyz
# purple wire (switch) to physical/board pin 7
# black wire (both ground) to physical/board pin 9
# blue wire (led) to physical/board pin 11
BUTTON_PIN = 4
LED_PIN = 17
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
# set up button and LED objects
blue_button = Button(BUTTON_PIN)
blue_led = LED(LED_PIN)
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

    # Wait for the button to be pressed, then fire of the function
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
    instructions_text.set("Get ready to take 3 pictures.")
    time.sleep(6)

    # Remove the logo and the instructions_text
    logo_label.grid_remove()
    instructions_label.grid_remove()

    # And back to the main screen
    main_screen()


######################################################################
#
#        Main Script Functionality
#
#######################################################################
# Call the main screen function to get things going!
main_screen()


# Escape key closes app
def close_window(e):
    win.destroy()
    exit()
win.bind('<Escape>', lambda e: close_window(e))

win.mainloop()
