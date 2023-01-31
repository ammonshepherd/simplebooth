# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# import qrcode
# import tkinter as tk


# gauth = GoogleAuth()           
# drive = GoogleDrive(gauth) 

# gfile = drive.CreateFile({'parents': [{'id': '1FEH74jojf7WPOYk0ILqexKMs-ezGwGnE'}]})
# # Read file and set it as the content of this instance.
# gfile.SetContentFile('simplebooth-icon.png')
# gfile.Upload() # Upload the file.

# fileUrl = gfile.metadata['webContentLink']

# qr = qrcode.make(fileUrl)
# qr.save('qrimage.png')

# w = tk.Tk()
# w.attributes('-fullscreen',True) 
# t = tk.Label(w, text="Scan this code to download your image!", font=("Arial", 55))
# t.grid(row=2,column=1)
# img = tk.PhotoImage(file='./qrimage.png')
# l = tk.Label(w, image=img)
# l.grid(row=1,column=1)
# w.after(9000, lambda: w.destroy()) # Destroy the widget after 30 seconds
# w.mainloop()

import urllib.request

def connected(host='https://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
    
print("connected" if connected() else "no internet")