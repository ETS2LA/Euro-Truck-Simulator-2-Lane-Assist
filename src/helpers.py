"""Provides helper functions for plugins, mainly to create consistent UI."""
from tkinter import ttk
import tkinter as tk
import src.settings as settings
import src.translator as translator
import webview
import webbrowser
from tktooltip import ToolTip
# Import qt for matplotlib
import PyQt5.Qt as Qt
import src.mainUI as mainUI
import src.controls as controls
import src.variables as variables
import win32gui

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
    global lastDefaultColumn
    
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
        

def MakeEmptyLine(parent, row:int, column:int, columnspan:int=1, pady:int=7, autoplace:bool=False, fontSize:int=9):
    """Will create an empty line with the given parameters.

    Args:
        parent (tkObject): The parent object of the empty line.
        row (int): The row of the empty line.
        column (int): The column of the empty line.
        columnspan (int, optional): The number of columns to span the empty line over. Defaults to 1.
        pady (int, optional): Defaults to 7.
        autoplace (bool, optional): Defaults to False. Will automatically determine the row the button should be placed on. You can still use the column option freely, but row will be ignored.
        fontSize (int, optional): Defaults to 9.
    """
    
    if autoplace:
        row = Autoplace(parent, row, column)
    
    ttk.Label(parent, text="", font=("Segoe UI", fontSize)).grid(row=row, column=column, columnspan=columnspan, pady=pady)
    
def MakeNotebook(parent, row:int, column:int, columnspan:int=1, rowspan:int=1, sticky:str="n", padx:int=5, pady:int=5):
    """Will create a new ttk.Notebook with the given parameters.

    Args:
        parent (tkObject): The parent object of the notebook.
        row (int): The row of the notebook.
        column (int): The column of the notebook.
        columnspan (int, optional): Defaults to 1.
        rowspan (int, optional): Defaults to 1.
        sticky (str, optional): Defaults to "n".
        padx (int, optional): Defaults to 5.
        pady (int, optional): Defaults to 5.

    Returns:
        ttk.Notebook: The notebook object we created.
    """
    notebook = ttk.Notebook(parent)
    notebook.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=padx, pady=pady)
    
    return notebook

def OpenWebView(title:str, urlOrFile:str, width:int=900, height:int=700):
    """Will open a webview window with the given parameters.

    Args:
        title (str): The window title.
        urlOrFile (str): A URL / File path.
        width (int, optional): Defaults to 900.
        height (int, optional): Defaults to 700.
    """
    popup = ShowPopup("\nClose the webview to continue...", "Info", timeout=0.1)
    popup.update(len(popups))
    mainUI.root.update()
    webview.create_window(title, urlOrFile, width=width, height=height)
    webview.start()

def OpenInBrowser(url:str):
    """Will open the given URL in the default browser.

    Args:
        url (str)
    """
    webbrowser.open(url)
    ShowPopup("\nOpened browser", "Info", type="info", timeout=2)

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
        
def RunEvery(duration, function, *args, **kwargs):
    """Will run the given function every x seconds.

    Args:
        duration (float): Seconds to wait between each function call.
        function (lambda): The function to run.
    """
    def wrapper():
        while True:
            function(*args, **kwargs)
            time.sleep(duration)
            
    import threading
    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()

runners = []
def RunIn(duration, function, mainThread=False, *args, **kwargs):
    """Will run the given function after x seconds.

    Args:
        duration (float): Seconds to wait before running the function.
        function (lambda): The function to run.
        mainThread (bool, optional): Whether to run the function in the main thread. WARNING: This is not accurate. The accuracy of the sleep depends on the main thread FPS. Defaults to False.
    """
    if not mainThread:
        def wrapper():
            time.sleep(duration)
            function(*args, **kwargs)
            
        import threading
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
    else:
        runners.append([duration, function, time.time(), args, kwargs])
            
class PID:
    """A simple PID controller.
    
    Usage:
    ```python
    pid = PID(0.2, 0.0, 0.0)
    pid.SetPoint = 1.0
    while True:
        feedback = value
        pid.update(feedback)
        output = pid.output
        time.sleep(0.01)
        
    # and auto tune
    pid.autoTune(feedback)
    ```
    
    Explanation of P, I, D:
    - P: Proportional. The proportional term produces an output value that is proportional to the current error value.
    - I: Integral. The integral term produces an output value that is proportional to both the magnitude of the error and the duration of the error.
    - D: Derivative. The derivative term produces an output value that is proportional to the rate of change of the error.
    """
    def __init__(self, P=0.2, I=0.0, D=0.0, plot=False):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.plot = plot
        if self.plot:
            self.createPlot()
        self.current_time = time.time()
        self.last_time = self.current_time
        self.clear()
        
    def createPlot(self):
        import matplotlib.pyplot as plt
        self.plot_data = []
        self.input_data = []
        # Create one window and plot with 2 values for the plot and input
        self.plot = plt
        self.plot.ion()
        self.plot.show()
        # Show the window on top
        self.plot.gcf().canvas.manager.window.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
        
    def clear(self):
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.int_error = 0.0
        self.windup_guard = 20.0
        self.output = 0.0
        
    def update(self, feedback_value, current_time=None):
        if current_time is None:
            current_time = time.time()
        delta_time = current_time - self.last_time
        delta_error = feedback_value - self.SetPoint
        self.PTerm = self.Kp * delta_error
        self.ITerm += delta_error * delta_time
        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard
        self.DTerm = 0.0
        if delta_time > 0:
            self.DTerm = delta_error / delta_time
        self.last_time = current_time
        self.last_error = feedback_value
        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
    
        if self.plot:
            self.plot_data.append(self.output)
            self.input_data.append(feedback_value)
            # Only have 200 values
            if len(self.plot_data) > 200:
                self.plot_data.pop(0)
            if len(self.input_data) > 200:
                self.input_data.pop(0)
                
            self.plot.clf()
            self.plot.plot(self.plot_data)
            self.plot.plot(self.input_data)
            self.plot.pause(0.0001)
        
    def setKp(self, proportional_gain):
        self.Kp = proportional_gain
        
    def setKi(self, integral_gain):
        self.Ki = integral_gain
        
    def setKd(self, derivative_gain):
        self.Kd = derivative_gain
        
    def setWindup(self, windup):
        self.windup_guard = windup
        
    def autoTune(self, feedback_value, current_time=None):
        if current_time is None:
            current_time = time.time()
        delta_time = current_time - self.last_time
        delta_error = feedback_value - self.SetPoint
        self.PTerm = self.Kp * delta_error
        self.ITerm += delta_error * delta_time
        if (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        elif (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard
        self.DTerm = 0.0
        if delta_time > 0:
            self.DTerm = delta_error / delta_time
        self.last_time = current_time
        self.last_error = feedback_value
        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
        self.Kp += self.PTerm
        self.Ki += self.ITerm
        self.Kd += self.DTerm
        self.clear()
        
popups = [] 
timeoutlessPopups = []
def ShowPopup(text, title, type="info", translate=True, timeout=4, indeterminate=False, closeIfMainloopStopped=False):
    """Will show a popup inside the app window.

    Args:
        text (str): What the popup says.
        title (str): The title of the popup.
        type (str, optional): Optional type, currently only info is implemented. Defaults to "info".
        translate (bool, optional): Whether to translate the text and title or not. Defaults to True.
        timeout (int, optional): Number of seconds to close the popup. If 0, timing is disabled and the popup will need to be manually closed. Defaults to 4.
        indeterminate (bool, optional): Whether the progressbar should be indeterminate or not. Defaults to False.
        closeIfMainloopStopped (bool, optional): Whether the popup should close if the mainloop is stopped. Defaults to False.

    Returns:
        popup: The popup class.
        
    Popup class:
        close(): Will close the popup.
        update(index): Will update the popup. (note: this is usually run by the mainloop, you don't need to call this manually)
        progressBar: The progressbar of the popup. Edit the settings and value of this to change the progress.
        text: The text of the popup. Edit the settings of this to change the text.
        closed: Indicates whether the popup has been closed or not. Useful if you use closeIfMainloopStopped and keep a reference to the popup.
    """
    global popups
    root = mainUI.root
    if translate:
        text = translator.Translate(text)
        title = translator.Translate(title)
    
    class popup(ttk.LabelFrame):
        def __init__(self, parent, text, title, type, timeout, indeterminate, closeIfMainloopStopped):
            super().__init__(parent, text=title, width=200, height=100)
            self.pack_propagate(False)
            self.grid_propagate(False)
            self.closed = False
            self.initTime = time.time()
            self.lastUpdateTime = time.time()
            if timeout == 0: 
                # Put the popup in the bottom right
                self.lastRely = ((mainUI.root.winfo_height()-60))/mainUI.root.winfo_height()
                self.place(relx=(mainUI.root.winfo_width()-110) / mainUI.root.winfo_width(), rely=self.lastRely, anchor="center")
            else:
                # Put the popup in the top center
                self.lastRely = 0.085 + (100*len(popups)/mainUI.root.winfo_height())
                self.place(relx=0.5, rely=self.lastRely, anchor="center")
            self.text = ttk.Label(self, text=text)
            self.text.pack()
            self.indeterminate = indeterminate
            self.closeIfMainloopStopped = closeIfMainloopStopped
            self.progressBar = ttk.Progressbar(self, mode="determinate", maximum=timeout if not indeterminate else 10, length=190)
            self.progressBar.pack(side="bottom")
            self.update(len(popups))
            self.timeout = timeout
            if timeout != 0:
                RunIn(timeout, lambda: self.close(), mainThread=True)
            # Bind all the popup elemets to close when clicked on (right or left or middle)
            for element in [self, self.text, self.progressBar]:
                element.bind("<Button-1>", lambda e: self.close())
                element.bind("<Button-2>", lambda e: self.close())
                element.bind("<Button-3>", lambda e: self.close())
    
        def update(self, index):
            if not time.time() - self.lastUpdateTime > 0.1:
                return
            else:
                self.lastUpdateTime = time.time()
            # Update the progressbar
            if self.timeout != 0:
                timeSinceInit = time.time() - self.initTime
                self.progressBar["value"] = timeSinceInit
            # If the mode is indeterminate, then bounce the value between 0 and 10
            if self.indeterminate:
                try:
                    self.progressBar["value"] = (self.progressBar["value"] + 0.5) % 10
                except:
                    pass
            # Update the position based on the amount of popups
            #self.place_forget()
            if self.timeout == 0:
                rely = ((mainUI.root.winfo_height()-60) - (100*index/mainUI.root.winfo_height()))/mainUI.root.winfo_height()
                if rely != self.lastRely:
                    self.place(relx=(mainUI.root.winfo_width()-110) / mainUI.root.winfo_width(), rely=rely, anchor="center")
                    self.lastRely = rely
            else:    
                rely = 0.085 + (100*index/mainUI.root.winfo_height())
                if rely != self.lastRely:
                    self.place(relx=0.5, rely=rely, anchor="center")
                    self.lastRely = rely
            
            if closeIfMainloopStopped and not variables.ENABLELOOP:
                self.close()
                return
            
            super().update()
            
        def close(self):
            self.destroy()
            self.closed = True
    
    if timeout == 0:
        timeoutlessPopups.append(popup(root, text, title, type, timeout, indeterminate, closeIfMainloopStopped))
        return timeoutlessPopups[-1]
    else:
        popups.append(popup(root, text, title, type, timeout, indeterminate, closeIfMainloopStopped))
    
    return popups[-1]

def GetWindowPosition(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return x, y, w, h

import mss
import mss.tools
background = None
def DimAppBackground():
    """Will take a screenshot of the app and dim it for the background. NOTE: This will overlay the image on the root, so you can't use any other functions. Not recommended to use directly.
    
    Returns:
        tk.Label: The label with the image, also available at helpers.background
    """
    global background
    # Get the app location, and make an mss 
    x,y,w,h = GetWindowPosition(mainUI.root.winfo_id())
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {"top": y, "left": x, "width": w, "height": h}
        # Grab the data
        sct_img = sct.grab(monitor)
        # Save to a file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output="screenshot.png")
    
    # Open the image
    from PIL import Image
    img = Image.open("screenshot.png")
    # Darken the image
    img = img.point(lambda p: p * 0.4)
    # Apply gaussian blur
    from PIL import ImageFilter
    img = img.filter(ImageFilter.GaussianBlur(2))
    # Cut out the titlebar (Not needed with GetWindowPosition)
    # from plugins.ScreenCapturePlacement.main import GetTitlebarHeight
    # img = img.crop((0, GetTitlebarHeight(), width, height))
    # Save the image
    img.save("screenshot.png")
    # Open the image with tkinter
    background = tk.PhotoImage(file="screenshot.png")
    # Place it on the root
    label = tk.Label(mainUI.root, image=background)
    label.place(x=0, y=0, relwidth=1, relheight=1)
    # Color titlebar
    from plugins.ThemeSelector.main import ColorTitleBar
    ColorTitleBar(mainUI.root, "0x141414")
    return label

def AskOkCancel(title, text, yesno=False, translate=True):
    """Similar to the tkinter messagebox, but will show the messagebox inside the app window. In addition it will dim the app background with some magic.

    Args:
        title (str): Title of the messagebox.
        text (str): Content of the messagebox.
        translate (bool, optional): Whether to translate the text or not. Defaults to True.
        
    Returns:
        bool: Whether the user pressed ok or cancel.
    """
    global selection
    
    if translate:
        title = translator.Translate(title)
        text = translator.Translate(text)
    
    # Dim the app 
    background = DimAppBackground()
    # Create the messagebox
    f = tk.Frame()
    frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
    ttk.Label(frame, text="", font=("Segoe UI", 6, "bold")).pack()
    title = ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"))
    title.pack()
    text = ttk.Label(frame, text=text)
    text.pack(pady=0)
    
    selection = None
    def Answer(answer):
        global selection
        frame.destroy()
        background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        selection = answer
    
    # Empty line
    ttk.Label(frame, text="").pack()
    
    # Create the buttons
    buttonFrame = ttk.Frame(frame)
    buttonFrame.pack()
    okText = "Ok" if not yesno else "Yes"
    cancelText = "Cancel" if not yesno else "No"
    if translate:
        okText = translator.Translate(okText)
        cancelText = translator.Translate(cancelText)
    okButton = ttk.Button(buttonFrame, text=okText, command=lambda: Answer(True))
    okButton.pack(side="left", padx=10)
    cancelButton = ttk.Button(buttonFrame, text=cancelText, command=lambda: Answer(False))
    cancelButton.pack(side="right", padx=10)
    # Place the messagebox
    frame.place(relx=0.5, rely=0.5, anchor="center")
    # Bind enter to ok
    mainUI.root.bind("<Return>", lambda e: Answer(True))
    # Bind escape and backspace to cancel
    mainUI.root.bind("<Escape>", lambda e: Answer(False))
    mainUI.root.bind("<BackSpace>", lambda e: Answer(False))
    # Increase the width and height of the frame by 20 to make it fit better
    try:
        frame.update()
        propagateSize = frame.winfo_width() + 20, frame.winfo_height() + 20
        frame.pack_propagate(False)
        frame.config(width=propagateSize[0], height=propagateSize[1])
    except: # Closed before the frame was updated
        return selection
    # Get focus if we don't have it
    if not mainUI.root.focus_get():
        mainUI.root.focus_force()
    
    mainUI.root.update()
    
    while selection == None:
        # Wait for the user to press a button
        mainUI.root.update()
        
    return selection

def RunInMainThread(function, *args, **kwargs):
    """Will run the given function in the main thread.

    Args:
        function (lambda): The function to run.
    """
    RunIn(0, function, mainThread=True, *args, **kwargs)
    
def Dialog(title, text, options, enterOption="", escapeOption="", translate=True):
    """Will show a dialog with the options specified.

    Args:
        title (str): Dialog title.
        text (str): Dialog text.
        options ([str]): The options to choose from (str array).
        enterOption (str, optional): The option to bind the Enter key to. Defaults to "".
        escapeOption (str, optional): The option to bind the Escape and Backspace keys to. Defaults to "".
        translate (bool, optional): Whether to translate the text or not. Defaults to True.
    
    Returns:
        str: The option that was chosen.
    """
    global selection
    
    if translate:
        title = translator.Translate(title)
        text = translator.Translate(text)
        options = [translator.Translate(option) for option in options]
    
    # Dim the app 
    background = DimAppBackground()
    # Create the messagebox
    f = tk.Frame()
    frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
    ttk.Label(frame, text="", font=("Segoe UI", 6, "bold")).pack()
    title = ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"))
    title.pack()
    text = ttk.Label(frame, text=text)
    text.pack()
    
    selection = None
    def Answer(answer):
        global selection
        frame.destroy()
        background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        selection = answer
    
    # Empty line
    ttk.Label(frame, text="").pack()
    ttk.Label(frame, text="").pack()
    
    # Create the buttons
    buttonFrame = ttk.Frame(frame)
    buttonFrame.pack()
    for option in options:
        button = ttk.Button(buttonFrame, text=option, command=lambda option=option: Answer(option))
        button.pack(side="left", padx=10)
    # Place the messagebox
    frame.place(relx=0.5, rely=0.5, anchor="center")
    # Bind enter
    if enterOption != "":
        mainUI.root.bind("<Return>", lambda e: Answer(enterOption))
    # Bind escape and backspace
    if escapeOption != "":
        mainUI.root.bind("<Escape>", lambda e: Answer(escapeOption))
        mainUI.root.bind("<BackSpace>", lambda e: Answer(escapeOption))
    # Increase the width and height of the frame by 20 to make it fit better
    try:
        frame.update()
        propagateSize = frame.winfo_width() + 20, frame.winfo_height() + 20
        frame.pack_propagate(False)
        frame.config(width=propagateSize[0], height=propagateSize[1])
    except: # Closed before the frame was updated
        return selection
    # Get focus if we don't have it
    if not mainUI.root.focus_get():
        mainUI.root.focus_force()
    
    mainUI.root.update()
    
    while selection == None:
        # Wait for the user to press a button
        mainUI.root.update()
        
    return selection

class FrameDialog():
    """Will create a new dialog to display a frame inside.
    
    Args:
        closeButtonText (str, optional): The text of the close button. Defaults to "Close".
    
    Usage:
    ```python	
    dialog = FrameDialog()
    frame = ttk.Frame(dialog.frame)
    dialog.close()
    ```
    """
    
    def close(self):
        """Will close the dialog."""
        self.frame.destroy()
        self.background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        del self
        
    def __init__(self) -> None:
        # Dim the app
        self.background = DimAppBackground()
        # Create the frame
        f = tk.Frame()
        self.frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
        # Place the frame
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        

def ShowSuccess(text, title="Success", translate=True):
    """Will show a success message inside the app window.

    Args:
        text (str): The success message.
        title (str, optional): The title of the success message. Defaults to "Success".
        translate (bool, optional): Whether to translate the text and title or not. Defaults to True.
    """
    if translate:
        title = translator.Translate(title)
        text = translator.Translate(text)
    
    # Dim the app 
    background = DimAppBackground()
    # Create the messagebox
    f = tk.Frame()
    frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
    ttk.Label(frame, text="", font=("Segoe UI", 6, "bold")).pack()
    title = ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"), foreground="#008800")
    title.pack()
    text = ttk.Label(frame, text=text)
    text.pack(pady=0)
    
    selection = None
    def Answer(answer):
        global selection
        frame.destroy()
        background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        selection = answer
    
    # Empty line
    ttk.Label(frame, text="").pack()
    
    # Create the buttons
    buttonFrame = ttk.Frame(frame)
    buttonFrame.pack()
    if translate:
        okText = translator.Translate("Ok")
    okButton = ttk.Button(buttonFrame, text=okText, command=lambda: Answer(True))
    okButton.pack(side="bottom", padx=10)
    # Place the messagebox
    frame.place(relx=0.5, rely=0.5, anchor="center")
    # Bind enter to ok
    mainUI.root.bind("<Return>", lambda e: Answer(True))
    # Bind escape and backspace to cancel
    mainUI.root.bind("<Escape>", lambda e: Answer(False))
    mainUI.root.bind("<BackSpace>", lambda e: Answer(False))
    # Increase the width and height of the frame by 20 to make it fit better
    try:
        frame.update()
        propagateSize = frame.winfo_width() + 20, frame.winfo_height() + 20
        frame.pack_propagate(False)
        frame.config(width=propagateSize[0], height=propagateSize[1])
    except: # Closed before the frame was updated
        return selection
    # Get focus if we don't have it
    if not mainUI.root.focus_get():
        mainUI.root.focus_force()
    
    mainUI.root.update()
    
    while selection == None:
        # Wait for the user to press a button
        mainUI.root.update()
        
    return

def ShowFailure(text, title="Failure", translate=True):
    """Will show a failure message inside the app window.

    Args:
        text (str): The failure message.
        title (str, optional): The title of the failure message. Defaults to "Failure".
        translate (bool, optional): Whether to translate the text and title or not. Defaults to True.
    """
    if translate:
        title = translator.Translate(title)
        text = translator.Translate(text)
    
    # Dim the app 
    background = DimAppBackground()
    # Create the messagebox
    f = tk.Frame()
    frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
    ttk.Label(frame, text="", font=("Segoe UI", 6, "bold")).pack()
    title = ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"), foreground="#cc2200")
    title.pack()
    text = ttk.Label(frame, text=text)
    text.pack(pady=0)
    
    selection = None
    def Answer(answer):
        global selection
        frame.destroy()
        background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        selection = answer
    
    # Empty line
    ttk.Label(frame, text="").pack()
    
    # Create the buttons
    buttonFrame = ttk.Frame(frame)
    buttonFrame.pack()
    if translate:
        okText = translator.Translate("Ok")
    okButton = ttk.Button(buttonFrame, text=okText, command=lambda: Answer(True))
    okButton.pack(side="bottom", padx=10)
    # Place the messagebox
    frame.place(relx=0.5, rely=0.5, anchor="center")
    # Bind enter to ok
    mainUI.root.bind("<Return>", lambda e: Answer(True))
    # Bind escape and backspace to cancel
    mainUI.root.bind("<Escape>", lambda e: Answer(False))
    mainUI.root.bind("<BackSpace>", lambda e: Answer(False))
    # Increase the width and height of the frame by 20 to make it fit better
    try:
        frame.update()
        propagateSize = frame.winfo_width() + 20, frame.winfo_height() + 20
        frame.pack_propagate(False)
        frame.config(width=propagateSize[0], height=propagateSize[1])
    except: # Closed before the frame was updated
        return selection
    
    # Get focus if we don't have it
    if not mainUI.root.focus_get():
        mainUI.root.focus_force()
        
    mainUI.root.update()
    
    while selection == None:
        # Wait for the user to press a button
        mainUI.root.update()
        
    return

def ShowInfo(text, title="Info", translate=True):
    """Will show an info message inside the app window.

    Args:
        text (str): The info message.
        title (str, optional): The title of the info message. Defaults to "Info".
        translate (bool, optional): Whether to translate the text and title or not. Defaults to True.
    """
    if translate:
        title = translator.Translate(title)
        text = translator.Translate(text)
    
    # Dim the app 
    background = DimAppBackground()
    # Create the messagebox
    f = tk.Frame()
    frame = ttk.LabelFrame(mainUI.root, labelwidget=f)
    ttk.Label(frame, text="", font=("Segoe UI", 6, "bold")).pack()
    title = ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"))
    title.pack()
    text = ttk.Label(frame, text=text)
    text.pack(pady=0)
    
    selection = None
    def Answer(answer):
        global selection
        frame.destroy()
        background.destroy()
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        selection = answer
    
    # Empty line
    ttk.Label(frame, text="").pack()
    
    # Create the buttons
    buttonFrame = ttk.Frame(frame)
    buttonFrame.pack()
    if translate:
        okText = translator.Translate("Ok")
    okButton = ttk.Button(buttonFrame, text=okText, command=lambda: Answer(True))
    okButton.pack(side="bottom", padx=10)
    # Place the messagebox
    frame.place(relx=0.5, rely=0.5, anchor="center")
    # Bind enter to ok
    mainUI.root.bind("<Return>", lambda e: Answer(True))
    # Bind escape and backspace to cancel
    mainUI.root.bind("<Escape>", lambda e: Answer(False))
    mainUI.root.bind("<BackSpace>", lambda e: Answer(False))
    # Increase the width and height of the frame by 20 to make it fit better
    try:
        frame.update()
        propagateSize = frame.winfo_width() + 20, frame.winfo_height() + 20
        frame.pack_propagate(False)
        frame.config(width=propagateSize[0], height=propagateSize[1])
    except: # Closed before the frame was updated
        return selection
    
    # Get focus if we don't have it
    if not mainUI.root.focus_get():
        mainUI.root.focus_force()
        
    mainUI.root.update()
    
    while selection == None:
        # Wait for the user to press a button
        mainUI.root.update()
        
    return

class SplashScreen(ttk.LabelFrame):
    def __init__(self, parent, text="Loading...", totalSteps=10):
        self.background = DimAppBackground()
        f = tk.Frame()
        super().__init__(parent, labelwidget=f)
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.label = ttk.Label(self, text=text, font=("Segoe UI", 12, "bold"))
        self.label.pack(pady=10, padx=10)
        self.progress = ttk.Progressbar(self, mode="determinate", length=200, maximum=totalSteps)
        self.progress.pack(pady=10, padx=10)
        self.update()
        
    def updateProgress(self, step=-1, text="Loading..."):
        if text != "":
            self.label.config(text=text)
        if step != -1:
            self.progress["value"] = step
        self.update_idletasks()
        
    def close(self):
        from plugins.ThemeSelector.main import ColorTitleBar
        ColorTitleBar(mainUI.root, "0x313131")
        self.background.destroy()
        self.destroy()