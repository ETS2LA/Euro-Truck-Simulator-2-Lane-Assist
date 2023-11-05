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
    text: The text to display on the loading window.
'''

import tkinter as tk
from tkinter import ttk
import sv_ttk

class LoadingWindow:
    def __init__(self, text, master=None, progress=False, grab=True, totalProgress=-1):
        self.text = text
        self.progress = progress
        
        if master == None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(master)
        
        def ignore():
            pass
            
        self.root.title(text)
        self.root.resizable(False, False)
        self.root.geometry("300x80")
        self.root.protocol("WM_DELETE_WINDOW", ignore)
        self.root.attributes("-topmost", True)
        if grab:
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
        
        if totalProgress != -1:
            self.totalProgress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate", value=totalProgress)
            self.root.geometry("300x140")
            self.totalProgress.pack(pady=10)
        
        self.root.update()

    def destroy(self):
        try:
            del self.progress
            self.root.destroy()
        except:
            del self

    def update(self, progress=False, text=False, totalProgress=-1):
        try:
            if progress != False:
                self.progress["value"] = progress
            
            if text != False:
                self.label.config(text=text)
                
            if totalProgress != -1:
                self.totalProgress["value"] = totalProgress
        except:
            pass
        
        self.root.update()
