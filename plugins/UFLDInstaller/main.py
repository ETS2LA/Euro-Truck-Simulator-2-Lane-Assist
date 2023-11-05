"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="UFLDInstaller", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Installs all files needed for UFLD",
    version="0.1",
    author="DylDev",
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
import gdown
import time

class UI():
    global download

    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.welcome()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def download(url):
            prefix = 'https://drive.google.com/uc?/export=download&id='
            file_id = url.split('/')[-2]
            gdown.download(prefix + file_id)

        def welcome(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "UFLD Installer", 0,0, font=("Roboto", 20, "bold"), padx=110, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "This panel installs all required files for UFLD.", 1,0, font=("Segoe UI", 10), padx=110, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "Keep in mind your GPU must be a NVIDIA GPU 1060 TI or better.", 2,0, font=("Segoe UI", 10), padx=110, pady=2, columnspan=2)
            
            helpers.MakeButton(self.root, "Quit", lambda: mainUI.quit(), 3,0)
            helpers.MakeButton(self.root, "Next", lambda: self.disclaimer1(), 3,1)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def disclaimer1(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "The following NVIDIA Binaries", 0,0, font=("Roboto", 20, "bold"), padx=70, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Will Be Downloaded", 1,0, font=("Roboto", 20, "bold"), padx=70, pady=5, columnspan=2)
            binaries = tk.Listbox(self.root, font=("Segoe UI", 10), width=50)
            def binariesins(row, text):
                binaries.insert(row, text)
            binariesins(1, "cufft64_10.dll")
            binariesins(2, "cudnn_ops_infer64_8.dll")
            binariesins(3, "cudnn_cnn_infer64_8.dll")
            binariesins(4, "cudnn_adv_infer64_8.dll")
            binariesins(5, "cudnn64_8.dll")
            binariesins(6, "cudart64_110.dll")
            binariesins(7, "cudart32_110.dll")
            binariesins(8, "cublastLt64_11.dll")
            binariesins(9, "cublas64_11.dll")
            binaries.grid( row=2, column=0, padx=70, pady=2, columnspan=2)

            helpers.MakeLabel(self.root, "These binaries were not made by me and are property of NVIDIA Corporation.", 3,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, '''"This software contains source code provided by NVIDIA Corporation."''', 4,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=2)
            
            helpers.MakeButton(self.root, "Back", lambda: self.welcome(), 5,0)
            helpers.MakeButton(self.root, "Next", lambda: self.disclaimer2(), 5,1)

            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        def disclaimer2(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "By downloading you agree to", 0,0, font=("Roboto", 20, "bold"), padx=20, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "the following terms:", 1,0, font=("Roboto", 20, "bold"), padx=20, pady=5, columnspan=2)
            helpers.MakeLabel(self.root, "1. https://docs.nvidia.com/deeplearning/cudnn/sla/index.html", 2,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "2. https://docs.nvidia.com/cuda/eula/index.html", 3,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, '''3. You agree to use the files only as a part of the "Euro-Truck-Simulator-2-Lane-Assist" application.''', 4,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "4. You agree to delete all downloaded files in the case you delete the program.", 5,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "5. **You are legally responsible for downloading these NVIDIA binaries.**", 6,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)

            helpers.MakeButton(self.root, "Back", lambda: self.disclaimer1(), 7,0)
            helpers.MakeButton(self.root, "Next", lambda: self.disclaimer3(), 7,1)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def disclaimer3(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "Additional Notes", 0,0, font=("Roboto", 20, "bold"), padx=20, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "These terms follow the NVIDIA guidelines, but I am not a lawyer and thus I have included term 5.", 1,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "This means that in the case that you do not follow these terms,", 2,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "or the terms are not sufficient from the start **I am not responsible.**", 3,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "In addition in the case that I would find out that you are not following these terms,", 4,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "**I am legally bound to report it to NVIDIA.**", 5,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "It is important to not that as in with the guidelines by NVIDIA", 6,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, '''"Additionally, you agree that you will protect the privacy,''', 7,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, '''security and legal rights of your application users."''', 8,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "My application does not log any user data.", 9,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "All files being downloaded are hosted on Google Drive.", 10,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "By downloading you agree to the previously listed terms. Please read them carefully!", 11,0, font=("Segoe UI", 10), padx=20, pady=2, columnspan=2)


            helpers.MakeButton(self.root, "Back", lambda: self.disclaimer2(), 12,0)
            helpers.MakeButton(self.root, "Next", lambda: self.downloadBinariesPanel(), 12,1)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def downloadBinariesPanel(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "Install NVIDIA Binaries", 0,0, font=("Roboto", 20, "bold"), padx=70, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "All terms listed previously apply to these files.", 1,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "Once you have read all the terms you can click the download button.", 2,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "This will download all files from Google Drive and place them in the correct folder.", 3,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=2)

            helpers.MakeButton(self.root, "Back", lambda: self.disclaimer3(), 4,0)
            helpers.MakeButton(self.root, "Download", lambda: self.downloadbinaries(), 4,1)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def downloadbinaries(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "Downloading...", 0,0, font=("Roboto", 20, "bold"), padx=130, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "Binaries are currently being downloaded.", 1,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "This will take awhile due to the size of the files.", 2,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "When all files are downloaded the next page will appear.", 3,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "Check the console for more information.", 4,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()

            binaryfolder = variables.PATH + r"\src\NVIDIA"
            os.chdir(binaryfolder)
            download("https://drive.google.com/file/d/1kJsg2-FiWG6TmNIVDgh6nPlxjW3_wQEB/view?usp=sharing")
            download("https://drive.google.com/file/d/1-68zJB5L0Ff04ZwbA6m_MLx7cPvQLGGD/view?usp=sharing")
            download("https://drive.google.com/file/d/1MBrMnB2Awyiqe25lSo6x17Xxe04iVVwO/view?usp=sharing")
            download("https://drive.google.com/file/d/1KbD2otVJVYFN7qlTCDfU62Nf0yAUYTVH/view?usp=sharing")
            download("https://drive.google.com/file/d/1ALvTba6BEDJjAl8B4Qagm2SkSbKZVTBX/view?usp=sharing")
            download("https://drive.google.com/file/d/19bGUy32AuR5YKZiVZJOOnVXMHNTjNvVB/view?usp=sharing")
            download("https://drive.google.com/file/d/135sr_EuJr7nLxcXLGPNFXOoca9lk-B4d/view?usp=sharing")
            download("https://drive.google.com/file/d/1KMmeHHuqds1XQlU0kM7zpYeIpLvwEExD/view?usp=sharing")
            download("https://drive.google.com/file/d/1pdTyUk06BILaTWd9cTLUTVPMKKlYfMY1/view?usp=sharing")
            download("https://drive.google.com/file/d/1KwBiqgernBSbYo4FThoGSS7c_1vd8Bdx/view?usp=sharing")

            self.downloadModelPanel()

        def downloadModelPanel(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "Install UFLD Model", 0,0, font=("Roboto", 20, "bold"), padx=70, pady=10, columnspan=1)
            helpers.MakeLabel(self.root, "This is the file that will make UFLD work", 1,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=1)
            helpers.MakeLabel(self.root, "This will download the file from Google Drive and place them in the correct folder.", 2,0, font=("Segoe UI", 10), padx=70, pady=2, columnspan=1)

            helpers.MakeButton(self.root, "Download", lambda: self.downloadmodel(), 4,0)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def downloadmodel(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "Downloading...", 0,0, font=("Roboto", 20, "bold"), padx=130, pady=10, columnspan=2)
            helpers.MakeLabel(self.root, "UFLD Model is currently being downloaded.", 1,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "This will take awhile due to the size of the file.", 2,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "When all files are downloaded the next page will appear.", 3,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            helpers.MakeLabel(self.root, "Check the console for more information.", 4,0, font=("Segoe UI", 10), padx=130, pady=2, columnspan=2)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()

            modelfolder = variables.PATH + r"\plugins\UFLDLaneDetection\UFLD\models"
            os.chdir(modelfolder)
            download("https://drive.google.com/file/d/1X8VCVFNmnImmMrqyrIjwfkqipA6jZom2/view?usp=sharing")
            self.finish()

        def finish(self):
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)

            helpers.MakeLabel(self.root, "UFLD Is Installed", 0,0, font=("Roboto", 20, "bold"), padx=160, pady=10, columnspan=1)
            helpers.MakeLabel(self.root, "Click the finish button to reload the program.", 1,0, font=("Segoe UI", 10), padx=160, pady=2, columnspan=1)
            
            def reload():
                os.chdir(variables.PATH)
                variables.RELOAD = True

            helpers.MakeButton(self.root, "Finish", lambda: reload(), 3,0)

            self.root.pack(anchor="center", expand=False)
            self.root.update()

        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)
