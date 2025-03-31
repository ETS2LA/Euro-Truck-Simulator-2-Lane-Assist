# type: ignore
# TODO: Make this file type-safe. I'm not even going to try and do it myself.
#     - Tumppi066
#
#       Changed it to use a class for the models, is it better now?
#     - Glas42
import ETS2LA.Utils.settings as settings
import ETS2LA.Utils.Console.visibility as console
import ETS2LA.variables as variables
from bs4 import BeautifulSoup
import threading
import traceback
import requests
import torch
import time
import sys
import os


def SendCrashReport(Title, Description):
    print("NOT IMPLEMENTED: SendCrashReport")


try:
    from torchvision import transforms
    import torch
    TorchAvailable = True
except:
    TorchAvailable = False
    exc = traceback.format_exc()
    SendCrashReport("PyTorch - PyTorch import error.", str(exc))


RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
YELLOW = "\033[93m"
NORMAL = "\033[0m"


class Model:
    def __init__(Self, HuggingFaceOwner:str, HuggingFaceRepository:str, HuggingFaceModelFolder:str, PluginSelf:object=None, Threaded:bool=True):
        Self.Device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        Self.Path = f"{variables.PATH}model-cache/{HuggingFaceOwner}/{HuggingFaceRepository}/{HuggingFaceModelFolder}"

        Self.HuggingFaceOwner = str(HuggingFaceOwner)
        Self.HuggingFaceRepository = str(HuggingFaceRepository)
        Self.HuggingFaceModelFolder = str(HuggingFaceModelFolder)

        Self.Identifier = f"{HuggingFaceRepository}/{HuggingFaceModelFolder}"

        Self.Threaded = Threaded

        Self.UpdateThread:threading.Thread
        Self.LoadThread:threading.Thread
        Self.Loaded:bool = False

        Self.Metadata:dict
        Self.Model:torch.jit.ScriptModule

        Self.ImageWidth:int
        Self.ImageHeight:int
        Self.ColorChannels:int
        Self.ColorChannelsStr:str
        Self.Outputs:int
        Self.TrainingTime:str
        Self.TrainingDate:str

        def PopupReset():
            StopTime = time.time() + 5
            FirstPopupValues = Self.PopupValues
            while time.time() < StopTime:
                time.sleep(0.1)
                if FirstPopupValues != Self.PopupValues:
                    FirstPopupValues = Self.PopupValues
                    StopTime = time.time() + 5
            Self.PopupHandler.state.text = ""
            Self.PopupHandler.state.progress = -1
        Self.PopupResetThread = threading.Thread(target=PopupReset, daemon=True)
        Self.PopupHandler = PluginSelf
        Self.PopupValues = ""

    def Popup(Self, Text="", Progress=0):
        try:
            if Self.PopupHandler != None:
                Self.PopupValues = Text, Progress
                Self.PopupHandler.state.text = Text
                Self.PopupHandler.state.progress = Progress / 100
                if Self.PopupResetThread.is_alive() == False:
                    Self.PopupResetThread.start()
        except:
            pass

    def Load(Self):
        try:
            def LoadFunction():
                try:
                    Self.CheckForUpdates()
                    while Self.UpdateThread.is_alive():
                        time.sleep(0.1)

                    if Self.GetName() == None:
                        return

                    Self.Popup(Text="Loading the model...", Progress=0)
                    print(GRAY + f"[{Self.Identifier}] " + GREEN + "Loading the model..." + NORMAL)

                    ModelFileBroken = False

                    try:
                        Self.Metadata = {"data": [], "Data": [], "metadata": [], "Metadata": []}
                        Self.Model = torch.jit.load(os.path.join(Self.Path, Self.GetName()), _extra_files=Self.Metadata, map_location=Self.Device)
                        Self.Model.eval()
                        Key = max(Self.Metadata, key=lambda Key: len(Self.Metadata[Key]))
                        Self.Metadata = eval(Self.Metadata[Key])
                        for Item in Self.Metadata:
                            Item = str(Item)
                            if "image_width" in Item or "ImageWidth" in Item:
                                Self.ImageWidth = int(Item.split("#")[1])
                            if "image_height" in Item or "ImageHeight" in Item:
                                Self.ImageHeight = int(Item.split("#")[1])
                            if "image_channels" in Item or "ImageChannels" in Item:
                                Data = Item.split("#")[1]
                                try:
                                    Self.ColorChannels = int(Data)
                                except ValueError:
                                    Self.ColorChannelsStr = str(Data)
                            if "color_channels" in Item or "ColorChannels" in Item:
                                Data = Item.split("#")[1]
                                try:
                                    Self.ColorChannels = int(Data)
                                except ValueError:
                                    Self.ColorChannelsStr = str(Data)
                            if "outputs" in Item or "Outputs" in Item:
                                Self.Outputs = int(Item.split("#")[1])
                            if "training_time" in Item or "TrainingTime" in Item:
                                Self.TrainingTime = Item.split("#")[1]
                            if "training_date" in Item or "TrainingDate" in Item:
                                Self.TrainingDate = Item.split("#")[1]
                    except:
                        ModelFileBroken = True

                    if ModelFileBroken == False:
                        Self.Popup(Text="Successfully loaded the model!", Progress=100)
                        print(GRAY + f"[{Self.Identifier}] " + GREEN + "Successfully loaded the model!" + NORMAL)
                        Self.Loaded = True
                    else:
                        Self.Popup(Text="Failed to load the model because the model file is broken.", Progress=0)
                        print(GRAY + f"[{Self.Identifier}] " + RED + "Failed to load the model because the model file is broken." + NORMAL)
                        Self.Loaded = False
                        Self.HandleBroken()
                except:
                    SendCrashReport("PyTorch - Loading Error.", str(traceback.format_exc()))
                    Self.Popup(Text="Failed to load the model!", Progress=0)
                    print(GRAY + f"[{Self.Identifier}] " + RED + "Failed to load the model!" + NORMAL)
                    Self.Loaded = False

            if TorchAvailable:
                if Self.Threaded:
                    Self.LoadThread = threading.Thread(target=LoadFunction, daemon=True)
                    Self.LoadThread.start()
                else:
                    LoadFunction()

        except:
            SendCrashReport("PyTorch - Error in function Load.", str(traceback.format_exc()))
            Self.Popup(Text="Failed to load the model.", Progress=0)
            print(GRAY + f"[{Self.Identifier}] " + RED + "Failed to load the model." + NORMAL)


    def CheckForUpdates(Self):
        try:
            def CheckForUpdatesFunction():
                try:

                    if "--dev" in sys.argv:
                        if Self.GetName() != None:
                            print(GRAY + f"[{Self.Identifier}] " + YELLOW + "Development mode enabled, skipping update check..." + NORMAL)
                            return
                        else:
                            print(GRAY + f"[{Self.Identifier}] " + YELLOW + "Development mode enabled, downloading model because it doesn't exist..." + NORMAL)

                    Self.Popup(Text="Checking for model updates...", Progress=0)
                    print(GRAY + f"[{Self.Identifier}] " + GREEN + "Checking for model updates..." + NORMAL)

                    if settings.Get("PyTorch", f"{Self.Identifier}-LastUpdateCheck", 0) + 600 > time.time():
                        if settings.Get("PyTorch", f"{Self.Identifier}-LatestModel", "unset") == Self.GetName():
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "No model updates available!" + NORMAL)
                            return

                    try:
                        HuggingFaceResponse = requests.get("https://huggingface.co/", timeout=3)
                        HuggingFaceResponse = HuggingFaceResponse.status_code
                        ETS2LAResponse = None
                    except:
                        try:
                            ETS2LAResponse = requests.get("https://cdn.ets2la.com/", timeout=3)
                            ETS2LAResponse = ETS2LAResponse.status_code
                            HuggingFaceResponse = None
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "Using cdn.ets2la.com..." + NORMAL)
                        except:
                            HuggingFaceResponse = None
                            ETS2LAResponse = None

                    if HuggingFaceResponse == 200:
                        Url = f'https://huggingface.co/{Self.HuggingFaceOwner}/{Self.HuggingFaceRepository}/tree/main/{Self.HuggingFaceModelFolder}'
                        Response = requests.get(Url)
                        Soup = BeautifulSoup(Response.content, 'html.parser')

                        LatestModel = None
                        for Link in Soup.find_all("a", href=True):
                            HREF = Link["href"]
                            if HREF.startswith(f'/{Self.HuggingFaceOwner}/{Self.HuggingFaceRepository}/blob/main/{Self.HuggingFaceModelFolder}'):
                                LatestModel = HREF.split("/")[-1]
                                settings.Set("PyTorch", f"{Self.Identifier}-LatestModel", LatestModel)
                                break
                        if LatestModel == None:
                            LatestModel = settings.Get("PyTorch", f"{Self.Identifier}-LatestModel", "unset")

                        CurrentModel = Self.GetName()

                        if str(LatestModel) != str(CurrentModel):
                            Self.Popup(Text="Updating the model...", Progress=0)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "Updating the model..." + NORMAL)
                            Self.Delete()
                            StartTime = time.time()
                            Response = requests.get(f'https://huggingface.co/{Self.HuggingFaceOwner}/{Self.HuggingFaceRepository}/resolve/main/{Self.HuggingFaceModelFolder}/{LatestModel}?download=true', stream=True, timeout=15)
                            with open(os.path.join(Self.Path, f"{LatestModel}"), "wb") as ModelFile:
                                TotalSize = int(Response.headers.get('content-length', 1))
                                DownloadedSize = 0
                                ChunkSize = 1024
                                for Data in Response.iter_content(chunk_size=ChunkSize):
                                    DownloadedSize += len(Data)
                                    ModelFile.write(Data)
                                    Progress = (DownloadedSize / TotalSize) * 100
                                    ETA = time.strftime('%H:%M:%S' if (time.time() - StartTime) / Progress * (100 - Progress) >= 3600 else '%M:%S', time.gmtime((time.time() - StartTime) / Progress * (100 - Progress)))
                                    Self.Popup(Text=f"Downloading the model: {round(Progress)}% - ETA: {ETA}", Progress=Progress)
                            Self.Popup(Text="Successfully updated the model!", Progress=100)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "Successfully updated the model!" + NORMAL)
                        else:
                            Self.Popup(Text="No model updates available!", Progress=100)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "No model updates available!" + NORMAL)
                        settings.Set("PyTorch", f"{Self.Identifier}-LastUpdateCheck", time.time())

                    elif ETS2LAResponse == 200:
                        Url = f'https://cdn.ets2la.com/models/{Self.HuggingFaceOwner}/{Self.HuggingFaceRepository}/{Self.HuggingFaceModelFolder}'
                        Response = requests.get(Url).json()

                        LatestModel = None
                        if "success" in Response:
                            LatestModel = Response["success"]
                            settings.Set("PyTorch", f"{Self.Identifier}-LatestModel", LatestModel)
                        if LatestModel == None:
                            LatestModel = settings.Get("PyTorch", f"{Self.Identifier}-LatestModel", "unset")

                        CurrentModel = Self.GetName()

                        if str(LatestModel) != str(CurrentModel):
                            Self.Popup(Text="Updating the model...", Progress=0)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "Updating the model..." + NORMAL)
                            Self.Delete()
                            StartTime = time.time()
                            Response = requests.get(f'https://cdn.ets2la.com/models/{Self.HuggingFaceOwner}/{Self.HuggingFaceRepository}/{Self.HuggingFaceModelFolder}/download', stream=True, timeout=15)
                            with open(os.path.join(Self.Path, f"{LatestModel}"), "wb") as ModelFile:
                                TotalSize = int(Response.headers.get('content-length', 1))
                                DownloadedSize = 0
                                ChunkSize = 1024
                                for Data in Response.iter_content(chunk_size=ChunkSize):
                                    DownloadedSize += len(Data)
                                    ModelFile.write(Data)
                                    Progress = (DownloadedSize / TotalSize) * 100
                                    ETA = time.strftime('%H:%M:%S' if (time.time() - StartTime) / Progress * (100 - Progress) >= 3600 else '%M:%S', time.gmtime((time.time() - StartTime) / Progress * (100 - Progress)))
                                    Self.Popup(Text=f"Downloading the model: {round(Progress)}% - ETA: {ETA}", Progress=Progress)
                            Self.Popup(Text="Successfully updated the model!", Progress=100)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "Successfully updated the model!" + NORMAL)
                        else:
                            Self.Popup(Text="No model updates available!", Progress=100)
                            print(GRAY + f"[{Self.Identifier}] " + GREEN + "No model updates available!" + NORMAL)
                        settings.Set("PyTorch", f"{Self.Identifier}-LastUpdateCheck", time.time())

                    else:

                        console.RestoreConsole()
                        Self.Popup(Text="Connection to 'https://huggingface.co' and 'https://cdn.ets2la.com' is not available. Unable to check for updates.", Progress=0)
                        print(GRAY + f"[{Self.Identifier}] " + RED + "Connection to 'https://huggingface.co' and 'https://cdn.ets2la.com' is not available. Unable to check for updates." + NORMAL)

                except:
                    SendCrashReport("PyTorch - Error in function CheckForUpdatesFunction.", str(traceback.format_exc()))
                    Self.Popup(Text="Failed to check for model updates or update the model.", Progress=0)
                    print(GRAY + f"[{Self.Identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)

            if Self.Threaded:
                Self.UpdateThread = threading.Thread(target=CheckForUpdatesFunction, daemon=True)
                Self.UpdateThread.start()
            else:
                CheckForUpdatesFunction()

        except:
            SendCrashReport("PyTorch - Error in function CheckForUpdates.", str(traceback.format_exc()))
            Self.Popup(Text="Failed to check for model updates or update the model.", Progress=0)
            print(GRAY + f"[{Self.Identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)


    def FolderExists(Self):
        try:
            if os.path.exists(Self.Path) == False:
                os.makedirs(Self.Path)
        except:
            SendCrashReport("PyTorch - Error in function FolderExists.", str(traceback.format_exc()))


    def GetName(Self):
        try:
            Self.FolderExists()
            for File in os.listdir(Self.Path):
                if File.endswith(".pt"):
                    return File
            return None
        except:
            SendCrashReport("PyTorch - Error in function GetName.", str(traceback.format_exc()))
            return None


    def Delete(Self):
        try:
            if "--dev" in sys.argv and os.listdir(Self.Path) != []:
                print(GRAY + f"[{Self.Identifier}] " + YELLOW + "Development mode enabled, skipping model deletion..." + NORMAL)
                return
            Self.FolderExists()
            for File in os.listdir(Self.Path):
                if File.endswith(".pt"):
                    os.remove(os.path.join(Self.Path, File))
        except PermissionError:
            global TorchAvailable
            TorchAvailable = False
            print(GRAY + f"[{Self.Identifier}] " + RED + "PyTorch - PermissionError in function Delete:\n" + NORMAL + str(traceback.format_exc()))
            console.RestoreConsole()
        except:
            SendCrashReport("PyTorch - Error in function Delete.", str(traceback.format_exc()))


    def HandleBroken(Self):
        try:
            if "--dev" in sys.argv:
                print(GRAY + f"[{Self.Identifier}] " + RED + "Can't handle broken models in development mode, all pytorch loader actions paused..." + NORMAL)
                while True: time.sleep(1)
            Self.Delete()
            Self.CheckForUpdates()
            while Self.UpdateThread.is_alive():
                time.sleep(0.1)
            time.sleep(0.5)
            if TorchAvailable == True:
                Self.Load()
        except:
            SendCrashReport("PyTorch - Error in function HandleBroken.", str(traceback.format_exc()))