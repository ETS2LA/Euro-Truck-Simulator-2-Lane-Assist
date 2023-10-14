from tkinter import ttk
import tkinter as tk
import src.settings as settings
import src.translator as translator
import webview
import webbrowser

def MakeButton(parent, text, command, row, column, style="TButton", width=15, center=False, padx=5, pady=10, state="!disabled", columnspan=1, translate=True, sticky="n"):
    if translate:
        text = translator.Translate(text)
    
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width, state=state)
    if not center:
        button.grid(row=row, column=column, padx=padx, pady=pady, columnspan=columnspan, sticky=sticky)
    else:
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky="n", columnspan=columnspan)
    return button
    
def MakeCheckButton(parent, text, category, setting, row, column, width=17, values=[True, False], onlyTrue=False, onlyFalse=False, default=False, translate=True, columnspan=1):
    if translate:
        text = translator.Translate(text)
    
    variable = tk.BooleanVar()
    value = settings.GetSettings(category, setting)
    
    if value == None:
        value = default
        settings.CreateSettings(category, setting, value)
        variable.set(value)
    else:
        variable.set(value)
    
    if onlyTrue:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[0]) if variable.get() else None, width=width)
    elif onlyFalse:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[1]) if not variable.get() else None, width=width)
    else:
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: settings.CreateSettings(category, setting, values[0] if variable.get() else values[1]), width=width)
    button.grid(row=row, column=column, padx=0, pady=7, sticky="w", columnspan=columnspan)
    return variable

def MakeComboEntry(parent, text, category, setting, row, column, width=10, labelwidth=15, isFloat=False, isString=False, value="", sticky="w", labelSticky="w", translate=True, labelPadX=10):
    if translate:
        text = translator.Translate(text)
    
    if not isFloat and not isString:
        ttk.Label(parent, text=text, width=labelwidth).grid(row=row, column=column, sticky=labelSticky, padx=labelPadX)
        var = tk.IntVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky=sticky, padx=7, pady=7)
        return var
    elif isString:
        ttk.Label(parent, text=text, width=labelwidth).grid(row=row, column=column, sticky=labelSticky, padx=labelPadX)
        var = tk.StringVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky=sticky, padx=7, pady=7)
        return var
    else:
        ttk.Label(parent, text=text, width=labelwidth).grid(row=row, column=column, sticky=labelSticky, padx=labelPadX)
        var = tk.DoubleVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
        ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky=sticky, padx=7, pady=7)
        return var

def MakeLabel(parent, text, row, column, font=("Segoe UI", 10), pady=7, padx=7, columnspan=1, sticky="n", fg="", bg="", translate=True):
    if translate:
        text = translator.Translate(text)
    
    if text == "":
        var = tk.StringVar()
        var.set(text)
        
        if fg != "" and bg != "":
            ttk.Label(parent, font=font, textvariable=var, background=bg, foreground=fg).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        elif fg != "":
            ttk.Label(parent, font=font, textvariable=var, foreground=fg).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        elif bg != "":
            ttk.Label(parent, font=font, textvariable=var, background=bg).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        else: 
            ttk.Label(parent, font=font, textvariable=var).grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        return var
    else:
        if fg != "" and bg != "":
            label = ttk.Label(parent, font=font, text=text, background=bg, foreground=fg)
        elif fg != "":
            label = ttk.Label(parent, font=font, text=text, foreground=fg)
        elif bg != "":
            label = ttk.Label(parent, font=font, text=text, background=bg)
        else:
            label = ttk.Label(parent, font=font, text=text)
        label.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        return label
        

def MakeEmptyLine(parent, row, column, columnspan=1, pady=7):
    ttk.Label(parent, text="").grid(row=row, column=column, columnspan=columnspan, pady=pady)
        

def OpenWebView(title, urlOrFile, width=900, height=700):
    webview.create_window(title, urlOrFile, width=width, height=height)
    webview.start()

def OpenInBrowser(url):
    webbrowser.open(url)

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