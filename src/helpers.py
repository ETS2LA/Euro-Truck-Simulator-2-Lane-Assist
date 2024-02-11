"""Provides helper functions for plugins, mainly to create consistent UI."""
from tkinter import ttk
import tkinter as tk
import src.settings as settings
import src.translator as translator
import webview
import webbrowser
from tktooltip import ToolTip

lastRow = 0
lastParent = None
defaultAutoplaceColumn = 0
"""Use this value to set the default column (what column means a new line) for the autoplace function. The value will get reset once a new parent is used."""
def Autoplace(parent, row:int, column:int):
    """Will automatically determine the row the next element should be placed on. You can still use the column option freely, but row will be ignored.

    Args:
        parent (tkObject): The parent object of the element.
    
    Returns:
        int: The row the next element should be placed on.
    """
    global lastRow
    global lastParent
    global defaultAutoplaceColumn
    
    if lastParent != parent:
        lastRow = 0
        defaultAutoplaceColumn = 0
        lastParent = parent
    else:
        if column == defaultAutoplaceColumn:
            lastRow += 1
        
    return lastRow
        

def MakeButton(parent, text:str, command, row:int, column:int, style:str="TButton", width:int=15, center:bool=False, padx:int=5, pady:int=10, state:str="!disabled", columnspan:int=1, rowspan:int=1, translate:bool=True, sticky:str="n", tooltip="", autoplace:bool=False):
    """Will create a new standard button with the given parameters.

    Args:
        parent (tkObject): The parent object of the button.
        text (str): The text that will be displayed on the button.
        command (lambda): The command that will be executed when the button is pressed.
        row (int): The row of the button.
        column (int): The column of the button.
        style (str, optional): You can use different tk styles here. Defaults to "TButton".
        width (int, optional): Defaults to 15.
        center (bool, optional): Defaults to False.
        padx (int, optional): Defaults to 5.
        pady (int, optional): Defaults to 10.
        state (str, optional): Defaults to "!disabled".
        columnspan (int, optional): How many columns the button will span over. Defaults to 1.
        rowspan (int, optional): How many rows the button will span over. Defaults to 1.
        translate (bool, optional): Whether to translate the text or not. Defaults to True.
        sticky (str, optional): Defaults to "n".
        tooltip (str, optional): Defaults to "".
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the button should be placed on. You can still use the column option freely, but row will be ignored.

    Returns:
        ttk.button: The button object we created.
    """
    
    if autoplace:
        row = Autoplace(parent, row, column)
    
    if translate:
        text = translator.Translate(text)
    
    button = ttk.Button(parent, text=text, command=command, style=style, padding=10, width=width, state=state)
    if not center:
        button.grid(row=row, column=column, padx=padx, pady=pady, columnspan=columnspan, rowspan=rowspan, sticky=sticky)
    else:
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky="n", columnspan=columnspan, rowspan=rowspan)
        
    if tooltip != "":
        ToolTip(button, msg=tooltip)
        
    return button

    
def MakeCheckButton(parent, text:str, category:str, setting:str, row:int, column:int, width:int=17, values=[True, False], onlyTrue:bool=False, onlyFalse:bool=False, default=False, translate:bool=True, columnspan:int=1, callback=None, tooltip="", autoplace:bool=False):
    """Will create a new checkbutton with the given parameters. The text will be on column 0 and the checkbutton on column 1. (Depending on the input column)

    Args:
        parent (tkObject): The parent object of the checkbutton.
        text (str): The text that will be displayed on the checkbutton.
        category (str): The json category of the setting.
        setting (str): The json setting.
        row (int): The row of the checkbutton.
        column (int): The column of the checkbutton.
        width (int, optional): Defaults to 17.
        values (list, optional): Set custom values to save when the button is on or off. Defaults to [True, False].
        onlyTrue (bool, optional): Only save the value when it's true. Defaults to False.
        onlyFalse (bool, optional): Only save the value when it's false. Defaults to False.
        default (bool, optional): The default value. Defaults to False.
        translate (bool, optional): Whether to translate the text or not. Defaults to True.
        columnspan (int, optional): How many columns the checkbutton will span over. Defaults to 1.
        callback (lambda, optional): Lambda callback. Defaults to None.
        tooltip (str, optional): Defaults to "".
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the button should be placed on. You can still use the column option freely, but row will be ignored.

    Returns:
        tk.BooleanVar: The boolean variable of the checkbutton. (use .get() to get the value)
    """
    if autoplace:
        row = Autoplace(parent, row, column)
    
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
        if callback != None:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[0])
                callback()
        else:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[0])
                
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: ButtonPressed() if variable.get() else None, width=width)
    elif onlyFalse:
        if callback != None:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[1])
                callback()
        else:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[1])
        
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: ButtonPressed() if not variable.get() else None, width=width)
    else:
        if callback != None:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[0] if variable.get() else values[1])
                callback()
                
        else:
            def ButtonPressed():
                settings.CreateSettings(category, setting, values[0] if variable.get() else values[1])
                
        button = ttk.Checkbutton(parent, text=text, variable=variable, command=lambda: ButtonPressed(), width=width)
    
    button.grid(row=row, column=column, padx=0, pady=7, sticky="w", columnspan=columnspan)
    
    if tooltip != "":
        ToolTip(button, msg=tooltip)
    
    return variable


def MakeComboEntry(parent, text:str, category:str, setting:str, row: int, column: int, width: int=10, labelwidth:int=15, isFloat:bool=False, isString:bool=False, value="", sticky:str="w", labelSticky:str="w", translate:bool=True, labelPadX:int=10, tooltip="", autoplace:bool=False):
    """Will make a new combo entry with the given parameters. The text will be on column 0 and the entry on column 1. (Depending on the input column)

    Args:
        parent (tkObject): The parent object of the combo entry.
        text (str): The text that will be displayed on the combo entry.
        category (str): The json category of the setting.
        setting (str): The json setting.
        row (str): The row of the combo entry.
        column (str): The column of the combo entry.
        width (int, optional): Defaults to 10.
        labelwidth (int, optional): The width of the label (text). Defaults to 15.
        isFloat (bool, optional): If the entry output should be a float. Defaults to False.
        isString (bool, optional): If the entry output should be a string. Defaults to False.
        value (str, optional): The default value. Defaults to "".
        sticky (str, optional): Defaults to "w".
        labelSticky (str, optional): Defaults to "w".
        translate (bool, optional): Whether to translate the text or not. Defaults to True.
        labelPadX (int, optional): Defaults to 10.
        tooltip (str, optional): Defaults to "".
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the entry should be placed on. You can still use the column option freely, but row will be ignored.

    Returns:
        tk.Var: The corresponding variable. Will be int, str, or float depending on the input. (use .get() to get the value)
    """
    if autoplace:
        row = Autoplace(parent, row, column)
    
    if translate:
        text = translator.Translate(text)
    
    label = ttk.Label(parent, text=text, width=labelwidth).grid(row=row, column=column, sticky=labelSticky, padx=labelPadX)
    if tooltip != "": 
        ToolTip(label, msg=tooltip)
    
    if not isFloat and not isString:
        var = tk.IntVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
    elif isString:
        var = tk.StringVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
    else:
        var = tk.DoubleVar()
        
        setting = settings.GetSettings(category, setting)
        if setting == None:
            var.set(value)
            settings.CreateSettings(category, setting, value)
        else:
            var.set(setting)
            
    entry = ttk.Entry(parent, textvariable=var, width=width, validatecommand=lambda: settings.CreateSettings(category, setting, var.get())).grid(row=row, column=column+1, sticky=sticky, padx=7, pady=7)
    
    if tooltip != "":
        ToolTip(entry, msg=tooltip)
    
    return var

def MakeLabel(parent, text:str, row:int, column:int, font=("Segoe UI", 10), pady:int=7, padx:int=7, columnspan:int=1, sticky:str="n", fg:str="", bg:str="", translate:bool=True, tooltip="", autoplace:bool=False):
    """Will make a label with the given parameters.

    Args:
        parent (tkObject): The parent object of the label.
        text (str): The text that will be displayed on the label.
        row (int): The row of the label.
        column (int): The column of the label.
        font (tuple, optional): Defaults to ("Segoe UI", 10).
        pady (int, optional): Defaults to 7.
        padx (int, optional): Defaults to 7.
        columnspan (int, optional): Will span the label over a number of columns. Defaults to 1.
        sticky (str, optional): Defaults to "n".
        fg (str, optional): Foreground color. Defaults to "".
        bg (str, optional): Background color. Defaults to "".
        translate (bool, optional): Whether to translate the label or not. Defaults to True.
        tooltip (str, optional): Defaults to "".
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the label should be placed on. You can still use the column option freely, but row will be ignored.

    Returns:
        tk.StringVar / ttk.Label: Depending on whether the text input is "" or not.
    """
    if autoplace:
        row = Autoplace(parent, row, column)
    
    if translate:
        text = translator.Translate(text)
    
    if text == "":
        var = tk.StringVar()
        var.set(text)
        
        if fg != "" and bg != "":
            label = ttk.Label(parent, font=font, textvariable=var, background=bg, foreground=fg)
        elif fg != "":
            label = ttk.Label(parent, font=font, textvariable=var, foreground=fg)
        elif bg != "":
            label = ttk.Label(parent, font=font, textvariable=var, background=bg)
        else: 
            label = ttk.Label(parent, font=font, textvariable=var)
            
        label.grid(row=row, column=column, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        
        if tooltip != "":
            ToolTip(label, msg=tooltip)
            
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
        
        if tooltip != "":
            ToolTip(label, msg=tooltip)
        
        return label
        

def MakeEmptyLine(parent, row:int, column:int, columnspan:int=1, pady:int=7, autoplace:bool=False):
    """Will create an empty line with the given parameters.

    Args:
        parent (tkObject): The parent object of the empty line.
        row (int): The row of the empty line.
        column (int): The column of the empty line.
        columnspan (int, optional): The number of columns to span the empty line over. Defaults to 1.
        pady (int, optional): Defaults to 7.
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the button should be placed on. You can still use the column option freely, but row will be ignored.
    """
    
    if autoplace:
        row = Autoplace(parent, row, column)
    
    ttk.Label(parent, text="").grid(row=row, column=column, columnspan=columnspan, pady=pady)
        

def OpenWebView(title:str, urlOrFile:str, width:int=900, height:int=700):
    """Will open a webview window with the given parameters.

    Args:
        title (str): The window title.
        urlOrFile (str): A URL / File path.
        width (int, optional): Defaults to 900.
        height (int, optional): Defaults to 700.
    """
    webview.create_window(title, urlOrFile, width=width, height=height)
    webview.start()

def OpenInBrowser(url:str):
    """Will open the given URL in the default browser.

    Args:
        url (str)
    """
    webbrowser.open(url)

def ConvertCapitalizationToSpaces(text:str):
    """Standard way to convert capitalization to spaces.

    Args:
        text (str): Input text.

    Returns:
        str: Output text with spaces.
    """
    newText = ""
    for i in range(len(text)):
        char = text[i]
        nextChar = text[i+1] if i+1 < len(text) else ""
        
        if char.isupper() and nextChar.islower() and i != 0:
            newText += " " + char
        else:
            newText += char
            
    return newText

import time
# https://stackoverflow.com/a/60185893
def AccurateSleep(duration, get_now=time.perf_counter):
    """Will sleep for the given duration. This function is more accurate than the standard time.sleep function.

    Args:
        duration (float): Seconds to sleep.
        get_now (float, optional): Current time. Defaults to time.perf_counter.
    """
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()