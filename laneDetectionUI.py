import tkinter as tk
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# create CTk window like you do with the Tk window
app = customtkinter.CTk()

# Width and height, everything should scale well
Height = 400
Width = 800

# Make the main window
app.geometry("{}x{}".format(Width, Height))
app.title("ETS2/ATS Lane Detection")

# A helper function for making a button (declutters code)
def AddButton(master, text, command, relx=0.5, rely=0.5, anchor="center", width=140, color=None):
    if color == None:
        button = customtkinter.CTkButton(master, text=text, command=command, width=width)
    else:
        button = customtkinter.CTkButton(master, text=text, command=command, width=width, fg_color=color)
    button.place(relx=relx, rely=rely, anchor=anchor)

def ToggleOnOff():
    print("Lane Assist Toggled")
def TogglePreview():
    print("Preview Toggled")
def SwitchToMainView():
    print("Switched to main view")
def SwitchToSettingsView():
    print("Switched to settings view")

# Make the sidebar frame
sidebar = customtkinter.CTkFrame(master=app, width=150, height=Height, corner_radius=10)
sidebar.pack(padx=20, pady=20, anchor="nw")

# Calculate the required offset
buttonSeparation = 5 # In pixels
buttonHeight = 40 # In pixels
buttonSeparation = (buttonSeparation + buttonHeight) / Height

# Add all the sidebar buttons with the required offset
AddButton(sidebar, "Toggle On/Off", ToggleOnOff, rely=buttonSeparation*0.6, width=130)
AddButton(sidebar, "Toggle Preview", TogglePreview, rely=buttonSeparation*1.6, width=130)
AddButton(sidebar, "Main View", SwitchToMainView, rely=buttonSeparation*3.6, width=130, color="grey")
AddButton(sidebar, "Settings", SwitchToSettingsView, rely=buttonSeparation*4.6, width=130, color="grey")


app.mainloop()