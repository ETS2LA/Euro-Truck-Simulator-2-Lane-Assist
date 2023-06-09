import tkinter as tk
from tkinter import ttk
import sv_ttk
import src.helpers as helpers

class FirstTimeSetup():
    def __init__(self, master):
        self.root = tk.Canvas(master, width=400, height=300)
        
        label = ttk.Label(self.root, text="Welcome!", font=("Roboto", 20, "bold"))
        label.grid(row=0, column=0, columnspan=2, pady=10, padx=30)

        label = ttk.Label(self.root, text="This is the first time you've run this program, so we need to set up some things first.", font=("Segoe UI", 10))
        label.grid(row=1, column=0, columnspan=2, pady=10, padx=30)

        helpers.MakeButton(self.root, "Continue", lambda: self.root.destroy(), 3,0)

        self.root.pack()

