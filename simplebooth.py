import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk


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

# show idle instructions
instructions = tk.StringVar()
instruct_label = tk.Label(win, textvariable=instructions, font=(
    "Arial", 85), wraplength=screen_width, bg="black", fg="white")

booth_icon = Image.open("simplebooth-icon.png")
pic = ImageTk.PhotoImage(booth_icon)
icon_label = tk.Label(win, image=pic, bg="black")
icon_label.image = pic
##################### END GUI SETTINGS ############################


def main_screen():
    global icon_label
    global instructions
    global instruct_label

    icon_label.grid(row=0, column=1, sticky="ew")

    instructions.set("Press the button to take pictures!")
    instruct_label.grid(row=1, column=1, sticky="ew")


# Call the main screen function to get things going!
main_screen()


# Escape key closes app
def close_window(e):
    win.destroy()
    exit()


win.bind('<Escape>', lambda e: close_window(e))

win.mainloop()
