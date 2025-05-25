from ETS2LA.Utils.Console.colors import *
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Networking.cloud as cloud
from importlib.metadata import version
import traceback
import requests
import zipfile
import shutil
import tqdm
import os

library_path = "ETS2LA/Assets/Libraries/"
library_urls = {
    "ffmpeg": {
        "windows": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "linux": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
        
        "move_up": True, # ffmpeg/ffmpeg.../ -> ffmpeg/
        "command": "ffmpeg -version", # won't download if this command works
        "path": "bin/ffmpeg.exe" # path to the executable that will be returned
    }
}

# This was used to check the version of ultralytics a while back.
# It's no longer used in ETS2LA but we'll keep the code here if
# we need to check for malicious packages in the future.
malicious_packages = {

}

def CheckForMaliciousPackages():
    for package in malicious_packages.keys():
        try:
            ver = version(package)
            if ver in malicious_packages[package]:
                print(RED + f"Your installed version of the '{package}' package might be malicious! Trying to remove it... (Package Version: {ver})" + END)
                ExecuteCommand(f"pip uninstall {package} -y & pip cache purge & pip install {package} --force-reinstall")
                cloud.SendCrashReport(package, f"Successfully updated a malicious package.", f"From version {ver} to the latest version.")
                print(GREEN + f"Successfully updated the '{package}' package to the latest version." + END)
        except:
            cloud.SendCrashReport(package, "Update malicious package error.", traceback.format_exc())
            print(RED + f"Unable to check the version of the '{package}' package. Please update your '{package}' package manually if you have one of these versions installed: {malicious_packages[package]}" + END)

def FixModule(module, ver, url):
    try:
        cur_ver = version(module)
    except:
        cur_ver = "0.0.0"
        
    if cur_ver < ver:
        print(f"{GREEN} -- Please wait, we need to install the correct version of:{YELLOW} {module} {GREEN} -- {END}")
        ExecuteCommand(f"pip install {url}")
        
def DownloadLibrary(library: str, force: bool = False):
    """Download a specified library into the Assets/Libraries folder.

    :param str library: The name of the library to download.
    :param bool force: Whether to force redownload the library, defaults to False
    """
    
    if not os.path.exists(library_path):
        os.makedirs(library_path)
    
    if not library in library_urls:
        print(RED + f"Library '{library}' not found in the library_urls dictionary." + END)
        return
    
    library_info = library_urls[library]
    move_up = library_info["move_up"] if "move_up" in library_info else False
    url = library_info["windows"] if os.name == "nt" else library_info["linux"]
    command = library_info["command"] if "command" in library_info else None
    path = library_info["path"] if "path" in library_info else None
    
    if command:
        code = ExecuteCommand(command, silent=True)
        if code == 0:
            return
    
    if force:
        shutil.rmtree(library_path + library, ignore_errors=True)
        
    if not os.path.exists(library_path + library):
        print(f"{GREEN} -- Please wait, we need to download the library:{YELLOW} {library} {GREEN}--{END}")
        print(f"{GREEN} -- If the download seems slow, then -- {END}")
        
        with requests.get(url, stream=True, timeout=2) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            with open(library_path + library + ".zip", "wb") as file:
                for data in tqdm.tqdm(response.iter_content(block_size), total=total_size/block_size, unit="kb", mininterval=0.25):
                    file.write(data)
        
        with zipfile.ZipFile(library_path + library + ".zip", "r") as zip_ref:
            zip_ref.extractall(library_path + library)
        
        if move_up:
            # Move the contents of the first folder up one level
            if len(os.listdir(library_path + library)) == 1:
                item = os.listdir(library_path + library)[0]
                for file in os.listdir(library_path + library + "/" + item):
                    shutil.move(library_path + library + "/" + item + "/" + file, library_path + library)
                shutil.rmtree(library_path + library + "/" + item)
        
        os.remove(library_path + library + ".zip")
        
        print(GREEN + f"Successfully downloaded the '{library}' library." + END)
    
    if path:
        return os.pathsep + os.path.abspath(library_path + library + "/" + path)