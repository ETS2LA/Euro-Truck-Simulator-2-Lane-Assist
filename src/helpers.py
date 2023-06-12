from tkinter import ttk
import tkinter as tk
import src.settings as settings

def MakeButton(parent, text, command, row, column, style="TButton", width=15, center=False):
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width)
    if not center:
        button.grid(row=row, column=column, padx=5, pady=10)
    else:
        button.grid(row=row, column=column, padx=5, pady=10, sticky="n")
    return button
    
def MakeCheckButton(parent, text, category, setting, row, column, width=17, values=[True, False], onlyTrue=False, onlyFalse=False):
    variable = tk.BooleanVar()
    
    try:
        variable.set(settings.GetSettings(category, setting))
    except:
        variable.set(False)
    
    if onlyTrue:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.UpdateSettings(category, setting, values[0]) if variable.get() else None)
    elif onlyFalse:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.UpdateSettings(category, setting, values[1]) if not variable.get() else None)
    else:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.UpdateSettings(category, setting, values[0] if variable.get() else values[1]), width=width)
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

def MakeLabel(parent, text, row, column, font=("Segoe UI", 10), pady=7, padx=7, columnspan=1, sticky="n"):
    if text == "":
        var = tk.StringVar()
        var.set(text)
        ttk.Label(parent, font=font, textvariable=var).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        return var
    else:
        ttk.Label(parent, font=font, text=text).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)