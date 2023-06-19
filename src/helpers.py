from tkinter import ttk
import tkinter as tk
import src.settings as settings

def MakeButton(parent, text, command, row, column, style="TButton", width=15, center=False, padx=5, pady=10, state="!disabled"):
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width, state=state)
    if not center:
        button.grid(row=row, column=column, padx=padx, pady=pady)
    else:
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky="n")
    return button
    
def MakeCheckButton(parent, text, category, setting, row, column, width=17, values=[True, False], onlyTrue=False, onlyFalse=False, default=False):
    variable = tk.BooleanVar()
    
    value = settings.GetSettings(category, setting)
    
    if value == None:
        value = default
        settings.CreateSettings(category, setting, value)
        variable.set(value)
    
    if onlyTrue:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[0]) if variable.get() else None, width=width)
    elif onlyFalse:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[1]) if not variable.get() else None, width=width)
    else:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[0] if variable.get() else values[1]), width=width)
    button.grid(row=row, column=column, padx=0, pady=7, sticky="w")
    return variable

def MakeComboEntry(parent, text, category, setting, row, column, width=10, isFloat=False, isString=False, value=""):
    if not isFloat and not isString:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.IntVar()
        
        try:
            var.set(settings.GetSettings(category, setting))
        except:
            var.set(value)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var
    elif isString:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.StringVar()
        
        try:
            var.set(settings.GetSettings(category, setting))
        except:
            var.set(value)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var
    else:
        ttk.Label(parent, text=text, width=15).grid(row=row, column=column, sticky="w")
        var = tk.DoubleVar()
        
        try:
            var.set(settings.GetSettings(category, setting))
        except:
            var.set(value)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky="w", padx=7, pady=7)
        return var

def MakeLabel(parent, text, row, column, font=("Segoe UI", 10), pady=7, padx=7, columnspan=1, sticky="n"):
    if text == "":
        var = tk.StringVar()
        var.set(text)
        ttk.Label(parent, font=font, textvariable=var).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        return var
    else:
        ttk.Label(parent, font=font, text=text).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        
        
def ConvertCapitalizationToSpaces(text):
    newText = ""
    for i in range(len(text)):
        char = text[i]
        nextChar = text[i+1] if i+1 < len(text) else ""
        
        if char.isupper() and nextChar.islower() and i != 0:
            newText += " " + char
        else:
            newText += char
            
    return newText