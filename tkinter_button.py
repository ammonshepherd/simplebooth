import tkinter as tk

import RPi.GPIO as GPIO

# Declare global variables
root = None
canvas = None
circle = None

# Pins definitions
btn_pin = 4

# Parameters
canvas_width = 100
canvas_height = 100
radius = 30

# Check on button state and update circle color
def poll():

    global root
    global btn_pin
    global canvas
    global circle

    # Make circle red if button is pressed and black otherwise
    if GPIO.input(btn_pin):
        canvas.itemconfig(circle, fill='black')
    else:
        canvas.itemconfig(circle, fill='red')

    # Schedule the poll() function for another 10 ms from now
    root.after(10, poll)

# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(btn_pin, GPIO.IN)

# Create the main window
root = tk.Tk()
root.title("Button Responder")

# Create the main container
frame = tk.Frame(root)

# Lay out the main container (center it in the window)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Create a canvas widget
canvas = tk.Canvas(frame, width=canvas_width, height=canvas_height)

# Lay out widget in frame
canvas.pack()

# Calculate top left and bottom right coordinates of the circle
x0 = (canvas_width / 2) - radius
y0 = (canvas_height / 2) - radius
x1 = (canvas_width / 2) + radius
y1 = (canvas_height / 2) + radius

# Draw circle on canvas
circle = canvas.create_oval(x0, y0, x1, y1, width=4, fill='black')

# Schedule the poll() function to be called periodically
root.after(10, poll)

# Run forever
root.mainloop()
