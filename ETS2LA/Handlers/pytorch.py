# type: ignore
# TODO: Make this file type-safe. I'm not even going to try and do it myself.
#     - Tumppi066
#
#       Better now?
#     - Glas42
import ETS2LA.Utils.settings as settings
import ETS2LA.Utils.Console.visibility as console
import ETS2LA.variables as variables
from bs4 import BeautifulSoup
import threading
import traceback
import requests
import numpy
import time
import cv2
import sys
import os


def send_crash_report(title, description):
    print("NOT IMPLEMENTED: send_crash_report")


try:
    from torchvision import transforms
    import torch
    torch_available = True
except:
    torch_available = False
    send_crash_report("PyTorch - PyTorch import error", str(traceback.format_exc()))


RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
YELLOW = "\033[93m"
NORMAL = "\033[0m"


class Model:
    def __init__(self, HF_owner:str, HF_repository:str, HF_model_folder:str, plugin_self:object=None, torch_dtype:torch.dtype=torch.bfloat16, threaded:bool=True):
        """
        Initialize a model.

        Parameters
        ----------
        HF_owner : str
            The Hugging Face user or organization that owns the model.
        HF_repository : str
            The name of the repository that contains the model.
        HF_model_folder : str
            The path to the folder that contains the model.
        plugin_self : object, optional
            The self of the plugin which uses this model, needed for popups.
        torch_dtype : torch.dtype, optional
            The data type to use for the model.
        threaded : bool, optional
            Whether to run the loading and updating in a separate thread.

        Returns
        -------
        None
        """
        self.torch_dtype = torch_dtype
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.path = f"{variables.PATH}model-cache/{HF_owner}/{HF_repository}/{HF_model_folder}"

        self.HF_owner = str(HF_owner)
        self.HF_repository = str(HF_repository)
        self.HF_model_folder = str(HF_model_folder)

        self.identifier = f"{HF_repository}/{HF_model_folder}"

        self.threaded = threaded

        self.update_thread:threading.Thread
        self.load_thread:threading.Thread
        self.loaded:bool = False

        self.metadata:dict
        self.model:torch.jit.ScriptModule

        self.image_width:int
        self.image_height:int
        self.color_channels:int
        self.color_channels_str:str
        self.outputs:int
        self.training_time:str
        self.training_date:str

        def popup_reset():
            stop_time = time.time() + 5
            first_popup_values = self.popup_values
            while time.time() < stop_time:
                time.sleep(0.1)
                if first_popup_values != self.popup_values:
                    first_popup_values = self.popup_values
                    stop_time = time.time() + 5
            self.popup_handler.state.text = ""
            self.popup_handler.state.progress = -1
        self.popup_reset_thread = threading.Thread(target=popup_reset, daemon=True)
        self.popup_handler = plugin_self
        self.popup_values = ""


    def popup(self, text="", progress=0):
        try:
            if self.popup_handler != None:
                self.popup_values = text, progress
                self.popup_handler.state.text = text
                self.popup_handler.state.progress = progress / 100
                if self.popup_reset_thread.is_alive() == False:
                    self.popup_reset_thread.start()
        except:
            pass


    def detect(self, image:numpy.ndarray):
        """
        Run the model on an image.
        Automatically converts and resizes the image.

        Parameters
        ----------
        image : numpy.ndarray
            The image to run the model on.

        Returns
        -------
        list
            The output of the model.
        """
        try:
            if len(image.shape) == 3:
                if image.shape[2] == 1 and self.color_channels == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                elif image.shape[2] == 3 and self.color_channels == 1:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                elif image.shape[2] == 4 and self.color_channels == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
                elif image.shape[2] == 4 and self.color_channels == 1:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            elif len(image.shape) == 2:
                if self.color_channels == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            image = cv2.resize(image, (self.image_width, self.image_height))
            if image.dtype == numpy.uint8:
                image = numpy.array(image, dtype=numpy.float32) / 255.0
            image = torch.as_tensor(transforms.ToTensor()(image).unsqueeze(0), dtype=self.torch_dtype, device=self.device)
            with torch.no_grad():
                output = self.model(image)
                output = output.tolist()
            return output
        except:
            send_crash_report("PyTorch - Error in function detect", str(traceback.format_exc()))


    def load_model(self):
        """
        Load the model from the cache, automatically handles updates.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            def thread():
                try:
                    self.check_for_updates()
                    while self.update_thread.is_alive():
                        time.sleep(0.1)

                    if self.get_name() == None:
                        return

                    self.popup("Loading the model...", 0)
                    print(GRAY + f"[{self.identifier}] " + GREEN + "Loading the model..." + NORMAL)

                    model_file_broken = False

                    try:
                        self.metadata = {"data": [], "Data": [], "metadata": [], "Metadata": []}
                        self.model = torch.jit.load(os.path.join(self.path, self.get_name()), _extra_files=self.metadata, map_location=self.device)
                        self.model.eval()
                        self.model.to(self.torch_dtype)
                        key = max(self.metadata, key=lambda key: len(self.metadata[key]))
                        self.metadata = eval(self.metadata[key])
                        for item in self.metadata:
                            try:
                                item = str(item)
                                if "image_width" in item or "ImageWidth" in item:
                                    self.image_width = int(item.split("#")[1])
                                if "image_height" in item or "ImageHeight" in item:
                                    self.image_height = int(item.split("#")[1])
                                if "image_channels" in item or "ImageChannels" in item:
                                    data = item.split("#")[1]
                                    try:
                                        self.color_channels = int(data)
                                    except ValueError:
                                        self.color_channels_str = str(data)
                                if "color_channels" in item or "ColorChannels" in item:
                                    data = item.split("#")[1]
                                    try:
                                        self.color_channels = int(data)
                                    except ValueError:
                                        self.color_channels_str = str(data)
                                if "outputs" in item or "Outputs" in item:
                                    self.outputs = int(item.split("#")[1])
                                if "training_time" in item or "TrainingTime" in item:
                                    self.training_time = item.split("#")[1]
                                if "training_date" in item or "TrainingDate" in item:
                                    self.training_date = item.split("#")[1]
                            except:
                                try:
                                    print(GRAY + f"[{self.identifier}] " + YELLOW + f"> Unable to parse '{item.split('#')[0]}' from model metadata!" + NORMAL)
                                except:
                                    print(GRAY + f"[{self.identifier}] " + YELLOW + f"> Unable to parse an item from model metadata!" + NORMAL)
                    except:
                        model_file_broken = True

                    if model_file_broken == False:
                        self.popup("Successfully loaded the model!", 100)
                        print(GRAY + f"[{self.identifier}] " + GREEN + "Successfully loaded the model!" + NORMAL)
                        self.loaded = True
                    else:
                        self.popup("Failed to load the model because the model file is broken.", 0)
                        print(GRAY + f"[{self.identifier}] " + RED + "Failed to load the model because the model file is broken." + NORMAL)
                        self.loaded = False
                        self.handle_broken()
                except:
                    send_crash_report("PyTorch - Error in function thread (load_model)", str(traceback.format_exc()))
                    self.popup("Failed to load the model!", 0)
                    print(GRAY + f"[{self.identifier}] " + RED + "Failed to load the model!" + NORMAL)
                    self.loaded = False

            if torch_available:
                if self.threaded:
                    self.load_thread = threading.Thread(target=thread, daemon=True)
                    self.load_thread.start()
                else:
                    thread()

        except:
            send_crash_report("PyTorch - Error in function load_model", str(traceback.format_exc()))
            self.popup("Failed to load the model.", 0)
            print(GRAY + f"[{self.identifier}] " + RED + "Failed to load the model." + NORMAL)


    def check_for_updates(self):
        """
        Checks for model updates.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            def thread():
                try:

                    if "--dev" in sys.argv:
                        if self.get_name() != None:
                            print(GRAY + f"[{self.identifier}] " + YELLOW + "Development mode enabled, skipping update check..." + NORMAL)
                            return
                        else:
                            print(GRAY + f"[{self.identifier}] " + YELLOW + "Development mode enabled, downloading model because it doesn't exist..." + NORMAL)

                    self.popup("Checking for model updates...", 0)
                    print(GRAY + f"[{self.identifier}] " + GREEN + "Checking for model updates..." + NORMAL)

                    if settings.Get("PyTorch", f"{self.identifier}-LastUpdateCheck", 0) + 600 > time.time():
                        if settings.Get("PyTorch", f"{self.identifier}-latest_model", "unset") == self.get_name():
                            print(GRAY + f"[{self.identifier}] " + GREEN + "No model updates available!" + NORMAL)
                            return

                    try:
                        HF_response = requests.get("https://huggingface.co/", timeout=3)
                        HF_response = HF_response.status_code
                        ETS2LA_response = None
                    except:
                        try:
                            ETS2LA_response = requests.get("https://cdn.ets2la.com/", timeout=3)
                            ETS2LA_response = ETS2LA_response.status_code
                            HF_response = None
                            print(GRAY + f"[{self.identifier}] " + GREEN + "Using cdn.ets2la.com..." + NORMAL)
                        except:
                            HF_response = None
                            ETS2LA_response = None

                    if HF_response == 200:
                        url = f'https://huggingface.co/{self.HF_owner}/{self.HF_repository}/tree/main/{self.HF_model_folder}'
                        response = requests.get(url)
                        soup = BeautifulSoup(response.content, 'html.parser')

                        latest_model = None
                        for Link in soup.find_all("a", href=True):
                            HREF = Link["href"]
                            if HREF.startswith(f'/{self.HF_owner}/{self.HF_repository}/blob/main/{self.HF_model_folder}'):
                                latest_model = HREF.split("/")[-1]
                                settings.Set("PyTorch", f"{self.identifier}-latest_model", latest_model)
                                break
                        if latest_model == None:
                            latest_model = settings.Get("PyTorch", f"{self.identifier}-latest_model", "unset")

                        current_model = self.get_name()

                        if str(latest_model) != str(current_model):
                            self.popup("Updating the model...", 0)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "Updating the model..." + NORMAL)
                            self.delete()
                            start_time = time.time()
                            response = requests.get(f'https://huggingface.co/{self.HF_owner}/{self.HF_repository}/resolve/main/{self.HF_model_folder}/{latest_model}?download=true', stream=True, timeout=15)
                            with open(os.path.join(self.path, f"{latest_model}"), "wb") as model_file:
                                total_size = int(response.headers.get('content-length', 1))
                                downloaded_size = 0
                                chunk_size = 1024
                                for data in response.iter_content(chunk_size=chunk_size):
                                    downloaded_size += len(data)
                                    model_file.write(data)
                                    progress = (downloaded_size / total_size) * 100
                                    ETA = time.strftime('%H:%M:%S' if (time.time() - start_time) / progress * (100 - progress) >= 3600 else '%M:%S', time.gmtime((time.time() - start_time) / progress * (100 - progress)))
                                    self.popup(f"Downloading the model: {round(progress)}% - ETA: {ETA}", progress)
                            self.popup("Successfully updated the model!", 100)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "Successfully updated the model!" + NORMAL)
                        else:
                            self.popup("No model updates available!", 100)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "No model updates available!" + NORMAL)
                        settings.Set("PyTorch", f"{self.identifier}-LastUpdateCheck", time.time())

                    elif ETS2LA_response == 200:
                        url = f'https://cdn.ets2la.com/models/{self.HF_owner}/{self.HF_repository}/{self.HF_model_folder}'
                        response = requests.get(url).json()

                        latest_model = None
                        if "success" in response:
                            latest_model = response["success"]
                            settings.Set("PyTorch", f"{self.identifier}-latest_model", latest_model)
                        if latest_model == None:
                            latest_model = settings.Get("PyTorch", f"{self.identifier}-latest_model", "unset")

                        current_model = self.get_name()

                        if str(latest_model) != str(current_model):
                            self.popup("Updating the model...", 0)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "Updating the model..." + NORMAL)
                            self.delete()
                            start_time = time.time()
                            response = requests.get(f'https://cdn.ets2la.com/models/{self.HF_owner}/{self.HF_repository}/{self.HF_model_folder}/download', stream=True, timeout=15)
                            with open(os.path.join(self.path, f"{latest_model}"), "wb") as model_file:
                                total_size = int(response.headers.get('content-length', 1))
                                downloaded_size = 0
                                chunk_size = 1024
                                for data in response.iter_content(chunk_size=chunk_size):
                                    downloaded_size += len(data)
                                    model_file.write(data)
                                    progress = (downloaded_size / total_size) * 100
                                    ETA = time.strftime('%H:%M:%S' if (time.time() - start_time) / progress * (100 - progress) >= 3600 else '%M:%S', time.gmtime((time.time() - start_time) / progress * (100 - progress)))
                                    self.popup(f"Downloading the model: {round(progress)}% - ETA: {ETA}", progress)
                            self.popup("Successfully updated the model!", 100)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "Successfully updated the model!" + NORMAL)
                        else:
                            self.popup("No model updates available!", 100)
                            print(GRAY + f"[{self.identifier}] " + GREEN + "No model updates available!" + NORMAL)
                        settings.Set("PyTorch", f"{self.identifier}-LastUpdateCheck", time.time())

                    else:

                        console.RestoreConsole()
                        self.popup("Connection to 'https://huggingface.co' and 'https://cdn.ets2la.com' is not available. Unable to check for updates.", 0)
                        print(GRAY + f"[{self.identifier}] " + RED + "Connection to 'https://huggingface.co' and 'https://cdn.ets2la.com' is not available. Unable to check for updates." + NORMAL)

                except:
                    send_crash_report("PyTorch - Error in function thread (check_for_updates)", str(traceback.format_exc()))
                    self.popup("Failed to check for model updates or update the model.", 0)
                    print(GRAY + f"[{self.identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)

            if self.threaded:
                self.update_thread = threading.Thread(target=thread, daemon=True)
                self.update_thread.start()
            else:
                thread()

        except:
            send_crash_report("PyTorch - Error in function check_for_updates", str(traceback.format_exc()))
            self.popup("Failed to check for model updates or update the model.", 0)
            print(GRAY + f"[{self.identifier}] " + RED + "Failed to check for model updates or update the model." + NORMAL)


    def folder_exists(self):
        """
        Creates the model folder if it doesn't exist.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            if os.path.exists(self.path) == False:
                os.makedirs(self.path)
        except:
            send_crash_report("PyTorch - Error in function folder_exists", str(traceback.format_exc()))


    def get_name(self):
        """
        Returns the file name of the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            self.folder_exists()
            for file in os.listdir(self.path):
                if file.endswith(".pt"):
                    return file
            return None
        except:
            send_crash_report("PyTorch - Error in function get_name", str(traceback.format_exc()))
            return None


    def delete(self):
        """
        Deletes the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            if "--dev" in sys.argv and os.listdir(self.path) != []:
                print(GRAY + f"[{self.identifier}] " + YELLOW + "Development mode enabled, skipping model deletion..." + NORMAL)
                return
            self.folder_exists()
            for file in os.listdir(self.path):
                if file.endswith(".pt"):
                    os.remove(os.path.join(self.path, file))
        except PermissionError:
            global torch_available
            torch_available = False
            print(GRAY + f"[{self.identifier}] " + RED + "PyTorch - PermissionError in function Delete:\n" + NORMAL + str(traceback.format_exc()))
            console.RestoreConsole()
        except:
            send_crash_report("PyTorch - Error in function delete", str(traceback.format_exc()))


    def handle_broken(self):
        """
        Deletes and redownloads the model if it's broken.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            if "--dev" in sys.argv:
                print(GRAY + f"[{self.identifier}] " + RED + "Can't handle broken models in development mode, all pytorch loader actions paused..." + NORMAL)
                while True: time.sleep(1)
            self.delete()
            self.check_for_updates()
            while self.update_thread.is_alive():
                time.sleep(0.1)
            time.sleep(0.5)
            if torch_available == True:
                self.load_model()
        except:
            send_crash_report("PyTorch - Error in function handle_broken", str(traceback.format_exc()))