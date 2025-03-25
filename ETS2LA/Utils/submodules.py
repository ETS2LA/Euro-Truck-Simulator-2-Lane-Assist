"""
This file contains handlers for ETS2LA's submodules.
Note that they are not actual submodules, instead we git clone them and handle the updates in this file.
"""

from ETS2LA.Utils.Console.colors import *
from ETS2LA.Utils.network import DownloadFile
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Utils.settings as settings 
import requests
import zipfile
import shutil
import time
import git
import os

def DownloadSubmoduleViaCDN(folder: str, cdn_url: str, cdn_path: str):
    try:
        print(f"{YELLOW} -- Downloading the submodule from ETS2LA servers due to no github connectivity -- {END}")
        
        DownloadFile(f"{cdn_url}", f"download.zip", chunk_size=8192, rich=True)
            
        # Extract the zip file
        with zipfile.ZipFile("download.zip", "r") as zip_ref:
            zip_ref.extractall(f"temp/extraction")
        
        # Move the extracted files from their internal path to the folder
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
        shutil.move(f"temp/extraction/{cdn_path}", folder)
        
        # Clean up
        os.remove("download.zip")
        shutil.rmtree("temp/extraction", ignore_errors=True)
        settings.Set("global", f"{folder}_downloaded", time.time())
    except:
        print(f"{RED} -- Failed to download the submodule: {YELLOW} {folder} {RED} -- {END}")

def EnsureSubmoduleExists(folder: str, url: str, cdn_url: str = "", cdn_path: str = "",
                          download_updates: bool = False, 
                          post_download_action: str = "", 
                          post_update_action: str = ""):
    if not os.path.exists(folder):
        print(f"{GREEN} -- Please wait, we need to download the following submodule: {YELLOW} {folder} {GREEN} -- {END}") 
        try:
            result = ExecuteCommand(f"git clone {url} {folder}")
            if result != 0:
                DownloadSubmoduleViaCDN(folder, cdn_url, cdn_path)
        except:
            DownloadSubmoduleViaCDN(folder, cdn_url, cdn_path)
        
        try:
            if post_download_action != "":
                print(f"{GREEN} -- Running post download action for submodule: {YELLOW} {folder} {GREEN} -- {END}")
                ExecuteCommand(post_download_action)
        except:
            print(f"{RED} -- Failed to run post download action for submodule: {YELLOW} {folder} {RED} -- {END}")
            
        return True
            
    elif download_updates:
        did_update = CheckForSubmoduleUpdate(folder, cdn_path=cdn_path, cdn_url=cdn_url)
        if did_update and post_update_action != "":
            print(f"{GREEN} -- Running post update action for submodule: {YELLOW} {folder} {GREEN} -- {END}")
            ExecuteCommand(post_update_action)
        return did_update
    
    return False
    
def CheckForSubmoduleUpdate(folder: str, cdn_url: str = "", cdn_path: str = ""):
    # Check for updates
    try:
        repo = git.Repo(folder)
    except:
        download_time = settings.Get("global", f"{folder}_downloaded", 0)
        download_time = 0 if download_time is None else float(download_time)
        try:
            if time.time() - download_time > 86400: # = 1 day
                print(f"{GREEN} -- Please wait, we need to redownload the following submodule: {YELLOW} {folder} {GREEN} -- {END}") 
                DownloadSubmoduleViaCDN(folder, cdn_url, cdn_path)
                return True
        except:
            print(f"{RED} -- Failed to download the submodule: {YELLOW} {folder} {RED} -- {END}")
            
        return False
    
    try:
        origin = repo.remotes.origin
        current_hash = repo.head.object.hexsha
        origin_hash = origin.fetch(kill_after_timeout=1)
        if len(origin_hash) > 0:
            origin_hash = origin_hash[0].commit.hexsha
        else:
            origin_hash = current_hash
            
        if current_hash != origin_hash:
            print(f"{GREEN} -- Please wait, we need to update the following submodule: {YELLOW} {folder} {GREEN} -- {END}")
            ExecuteCommand(f"git -C {folder} pull")
            return True
    except:
        print(f"{YELLOW} -- Failed to update / check for updates for the submodule (remove the corresponding folder in code/app to redownload if possible): {folder} -- {END}")
    
    return False