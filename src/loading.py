"""Provides a loading window with a progress bar and a text label.

Usage: 
```python
loading = LoadingWindow("Loading...")
loading.update(progress=0.5, text="Loading 50%")
loading.update(progress=1, text="Loading 100%")
loading.destroy()
```
"""
import tkinter as tk
from tkinter import ttk
import sv_ttk

class LoadingWindow:
    def __init__(self, text:str, master=None, progress:float=False, grab:bool=True, totalProgress:float=-1):
        """Will create a loading window with a progress bar and a text label.

        Args:
            text (str): The text to display on the loading window.
            master (tkObject, optional): The master object. Otherwise we will create a new tk.Tk() object. Defaults to None.
            progress (bool / float, optional): If False, the progress bar will indeterminate. Otherwise input is from 0 to 1. Defaults to False.
            grab (bool, optional): Whether to grab the window focus. Defaults to True.
            totalProgress (float, optional): Will display another loading bar with the total progress. Defaults to -1.
        """
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

    def update(self, progress:float=False, text:str=False, totalProgress:float=-1):
        """Will update the loading window.

        Args:
            progress (float, optional): If a float is provided, the progress bar will be moved to the correct location. Defaults to False.
            text (str, optional): If a string is provided, the text will be updated. Defaults to False.
            totalProgress (float, optional): If a float is provided, will update the second loading bar. Defaults to -1.
        """
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
