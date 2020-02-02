import sys
import os
from tkinter import *
from PIL import Image, ImageTk
from multiprocessing.connection import Client

cwd = "C:\\Users\\harsh\\Desktop\\dtoxd-demo\\dist\\image_viewer"
default_im = os.path.join(cwd,"default_image.png")
print(default_im)

address = ('localhost', 6969)
conn = Client(address, authkey=b'dtoxd-data-incoming')
print("[INFO] Connection with server established...")

root = Tk()
root.title("dtoxd : Image Viewer")

try:
	img_name = str(sys.argv[1])
	conn.send(['p',img_name]) #path
	pred = conn.recv()
	print(pred)
	if pred == 1:
		print("Explicit Image")
		img = ImageTk.PhotoImage(Image.open(default_im))
	else:
		print("Safe Image")
		img = ImageTk.PhotoImage(Image.open(img_name))
	panel = Label(root, image = img)
	panel.pack(side = "bottom", fill = "both", expand = "yes")
	root.mainloop()
except:
	root.geometry("640x400")
	panel = Label(root, text="Path not correct or File not found.")
	panel.pack(side = "bottom", fill = "both", expand = "yes")
	root.mainloop()
