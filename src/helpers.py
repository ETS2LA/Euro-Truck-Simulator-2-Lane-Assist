from tkinter import ttk
import tkinter as tk
import src.settings as settings

def MakeButton(parent, text, command, row, column, style="TButton", width=15, center=False):
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width)
    if not center:
        button.grid(row=row, column=column, padx=5, pady=5)
    else:
        button.grid(row=row, column=column, padx=5, pady=5, sticky="n")
    return button
    
def MakeCheckButton(parent, text, category, setting, row, column, width=17):
    variable = tk.BooleanVar()
    variable.set(settings.GetSettings(category, setting))
    button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.UpdateSettings(category, setting, variable.get()), width=width)
    button.grid(row=row, column=column, padx=0, pady=7, sticky="w")
    return variable

def MakeComboEntry(parent, text, category, setting, row, column, width=10, isFloat=False, isString=False):
    if not isFloat and not isString:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.IntVar()
        var.set(int(settings.GetSettings(category, setting)))
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.UpdateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var
    elif isString:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.StringVar()
        var.set(settings.GetSettings(category, setting))
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.UpdateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var
    else:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.DoubleVar()
        var.set(float(settings.GetSettings(category, setting)))
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.UpdateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var

