'''
This file contains the main UI for the program. It is responsible for creating the window and setting up the main UI elements.
'''

import tkinter as tk
from tkinter import ttk
import sv_ttk

width = 800
height = 500

root = tk.Tk()
root.title("Lane Assist")

root.resizable(False, False)
root.geometry("")
root.protocol("WM_DELETE_WINDOW", lambda: exit())

sv_ttk.set_theme("dark")

root.update()

def init():
    root.geometry(f"{width}x{height}")

def exit():
    root.destroy()

def update():
    root.update()