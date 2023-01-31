import tkinter as tk
import urllib.request
from gpiozero import Button, LED
from picamera import PiCamera


# Declare global variables
root = None
canvas = None
circle = None

# Pins definitions
BUTTON_PIN = 4
LED_PIN = 17

# Parameters
# canvas_width = 100
# canvas_height = 100

# Set up button and camera objects
blue_button = Button(BUTTON_PIN)
blue_led = LED(LED_PIN)
camera = PiCamera(resolution=(1920,1080), framerate=15, sensor_mode=5)
# flip camera vertically, upside down or right side up
camera.rotation = 180
# flip horizontally so it doesn't look backwards
camera.hflip = True

def connected(host='https://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False

has_internet = connected()

# Check on button state and update circle color
def poll():

    global root
    global canvas
    global circle

    if blue_button.is_pressed:
        canvas.itemconfig(circle, fill='black')
    else:
        canvas.itemconfig(circle, fill='red')

    # Schedule the poll() function for another 10 ms from now
    root.after(10, poll)


# Create the main window
root = tk.Tk()
root.attributes('-fullscreen',True) 
root.title("Simple Photobooth")

# Create the main container
frame = tk.Frame(root)

# Lay out the main container (center it in the window)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Show Controls
# - show text/image to click button to take a pictures
def show_instructions():
    if (has_internet):
      text = "Get ready to take 3 pictures!\nAfterwards, scan the QR code to download your photo!\n\nPress the button to begin!"
    else:
      text = "Get ready to take 3 pictures!\n\nPress the button to begin!"
    instructions = tk.Label(frame, text=text, width=500, wraplength=1500, font=("Helvetica", 75))
    instructions.pack()

    # root.after(10, poll)

# # Create a canvas widget
# canvas = tk.Canvas(frame, width=canvas_width, height=canvas_height)

# # Lay out widget in frame
# canvas.pack()

# # Calculate top left and bottom right coordinates of the circle
# x0 = (canvas_width / 2) - radius
# y0 = (canvas_height / 2) - radius
# x1 = (canvas_width / 2) + radius
# y1 = (canvas_height / 2) + radius

# # Draw circle on canvas
# circle = canvas.create_oval(x0, y0, x1, y1, width=4, fill='black')


blue_led.blink()

show_instructions()

# Schedule the poll() function to be called periodically
# root.after(10, poll)



# Escape key closes app
def close_window(e):
    root.destroy()

root.bind('<Escape>', lambda e: close_window(e))

# Run forever
root.mainloop()
