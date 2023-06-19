'''
Will create a loading window with the desired text.

init() parameters:
    text (mandatory): The text to display on the loading window.
    master (mandatory): The master window (usually root) to attach the loading window to.
    progress: If set to False, will create an indeterminate progress bar. If set to an integer, will create a determinate progress bar with the value of the integer.

destroy() parameters:
    None

update() parameters:
    progress: If set to False, will create an indeterminate progress bar. If set to an integer, will create a determinate progress bar with the value of the integer.

'''

import tkinter as tk
from tkinter import ttk
import sv_ttk

class LoadingWindow:
    def __init__(self, text, master=None, progress=False):
        self.text = text
        self.progress = progress
        self.root = tk.Toplevel(master)
        self.root.title(text)
        self.root.resizable(False, False)
        self.root.geometry("300x80")
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.grab_set()

        self.label = ttk.Label(self.root, text=self.text)
        self.label.pack(pady=10)

        if progress == False:
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
            self.progress.start(10)
        else:
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate", value=progress)
        self.progress.pack(pady=10)
        self.root.update()

    def destroy(self):
        self.root.destroy()

    def update(self, progress=False):
        self.progress = progress
        
        if progress != False:
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate", value=progress)
        
        self.root.update()


