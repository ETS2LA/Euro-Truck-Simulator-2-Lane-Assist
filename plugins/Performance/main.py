"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="Performance", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will display current app performance.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import os
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

frames = []
idleTime = []
lastUpdateTime = time.time()
updateRate = 0.25

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.once = False
            mainUI.resizeWindow(900,600)
            self.main()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def tabFocused(self):
            mainUI.resizeWindow(900,600)

        def updateAxis(self):
            try:
                # Update the axis using blitting to avoid redrawing the whole graph
                # the data is updated in the frames list
                self.line.set_ydata(frames)
                self.line.set_xdata(range(len(frames)))
                self.idleLine.set_ydata(idleTime)
                self.idleLine.set_xdata(range(len(idleTime)))
                self.ax.draw_artist(self.ax.patch)
                self.ax.draw_artist(self.line)
                self.ax.draw_artist(self.idleLine)
                
                self.canvas.blit(self.ax.bbox)
                self.canvas.flush_events()
            except:
                pass
            
        def createGraph(self):
            
            # Try and delete the old graph if it exists
            try:
                self.canvas.get_tk_widget().destroy()
                del self.canvas
                del self.fig
                del self.ax
                del self.line
                
            except: pass
            
            try:
                background = "#313131"
                foreground = "#ffffff"
                graphColor = "#51b7eb" 
                idleTimeColor = "#ff0000"
                
                # Make a frametime graph (also support blitting)
                self.fig, self.ax = plt.subplots()
                self.fig.set_size_inches(7, 2)
                # "Remove" the white space around the graph
                self.fig.set_facecolor(background) # Set the background color
                self.ax.set_facecolor(background) # Set the background color
                self.ax.tick_params(axis='x', colors=foreground) # Set the axis text color to white
                self.ax.tick_params(axis='y', colors=foreground) # Set the axis text color to white
                # Remove the small black lines around the graph
                self.ax.spines['bottom'].set_color(background)
                self.ax.spines['top'].set_color(background)
                self.ax.spines['right'].set_color(background)
                self.ax.spines['left'].set_color(background)
                
                self.ax.set_ylabel("Time (ms) Idle (%)")
                self.ax.yaxis.label.set_color(foreground)
                
                self.ax.set_ylim(0, 100)
                self.ax.set_xlim(0, 100)
                self.ax.set_autoscale_on(False)
                
                self.line, = self.ax.plot(frames, color=graphColor)
                self.idleLine, = self.ax.plot(idleTime, color=idleTimeColor)
                
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
                self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=10)
                self.canvas.draw()
            except:
                pass
            
            
        def main(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=700, height=750, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            # Helpers provides easy to use functions for creating consistent widgets!
            self.fps = helpers.MakeLabel(self.root, "", 1,0, font=("Roboto", 20, "bold"), padx=30, pady=5, columnspan=1)
            self.cpu = helpers.MakeLabel(self.root, "", 2,0, font=("Roboto", 12), padx=30, pady=2, columnspan=1)
            # Make the list of plugins and their frametimes (can't be a treeview since that is too slow)
            self.list = tk.Text(self.root, width=60, height=14, font=("Consolas", 10))
            self.list.grid(row=3, column=0, padx=30, pady=0, columnspan=1)
            helpers.MakeLabel(self.root, "* all information is for the last frame", 5,0, font=("Roboto", 10), padx=30, pady=10)
            
            self.createGraph()
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def update(self, data): # When the panel is open this function is called each frame 
            global frames
            global lastUpdateTime
            global lastTheme
            global idleTime
            
            data = data["last"] # Get last frame's data
            try:
                lastFrameTime = data["executionTimes"]["all"]
                fps = 1/lastFrameTime
                ms = lastFrameTime*1000
                self.fps.set(f"{round(fps)} fps ({round(ms, 1)} ms)")
                
                frames.append(ms)
                if len(frames) > 100:
                    frames.pop(0)
                
                if(time.time() - lastUpdateTime > updateRate):
                    lastUpdateTime = time.time()
                    # Clear the text box and add the new data
                    self.list.delete("1.0", "end")
                    for plugin in data["executionTimes"]:
                        # Take into account the width to make the values line up 
                        listObject = f"{plugin}:"
                        listObject += " "*(50-len(listObject))
                        listObject += f"{int(data['executionTimes'][plugin]*1000)} ms"
                        self.list.insert("end", listObject + "\n")

                try:
                    self.updateAxis()
                except Exception as ex:
                    print(ex.args)
                    pass

                try:
                    self.cpu.set(f"Idle Time: {round((data['executionTimes']['FPSLimiter'] / lastFrameTime) * 100)}%")
                    idleTime.append((data['executionTimes']['FPSLimiter'] / lastFrameTime) * 100)
                    
                    if len(idleTime) > 100:
                        idleTime.pop(0)
                except:
                    idleTime = []
                    
            except Exception as ex:
                print(ex.args)
    
            self.root.update()
            
    
    except Exception as ex:
        print(ex.args)