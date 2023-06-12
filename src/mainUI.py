'''
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.
'''

import time
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import src.helpers as helpers

width = 800
height = 600

root = tk.Tk()
root.title("Lane Assist")

root.resizable(False, False)
root.geometry(f"{width}x{height}")
root.protocol("WM_DELETE_WINDOW", lambda: quit())

sv_ttk.set_theme("dark")

ttk.Label(root, text="ETS2 Lane Assist    ©Tumppi066 - 2023", font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)
fps = tk.StringVar()
ttk.Label(root, textvariable=fps, font=("Roboto", 8)).pack(side="bottom", anchor="s", padx=10, pady=0)

root.update()

def init():
    root.geometry(f"{width}x{height}")
    ttk.Label(root, text="Work In Progress", font=("Roboto", 30, "bold")).pack(side="top", anchor="n", padx=10, pady=20)

def quit():
    global root
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # Destroy the root window
        root.destroy()
        del root

prevFrame = 100
def update():
    global fps
    global prevFrame
    
    # Calculate the UI caused overhead
    frame = time.time()
    try:
        fps.set(f"UI Overhead: {round((frame-prevFrame)*1000)}ms")
    except: pass
    prevFrame = frame
    
    root.update()