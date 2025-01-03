"""
This file contains handlers for ETS2LA's submodules.
Note that they are not actual submodules, instead we git clone them and handle the updates in this file.
"""

from ETS2LA.Utils.Console.colors import *
import git
import os

def EnsureSubmoduleExists(folder: str, url: str, 
                          download_updates: bool = False, 
                          post_download_action: str = "", 
                          post_update_action: str = ""):
    if not os.path.exists(folder):
        print(f"{GREEN} -- Please wait, we need to download the following submodule: {YELLOW} {folder} {GREEN} -- {END}") 
        os.system(f"git clone {url} {folder}")
        if post_download_action != "":
            print(f"{GREEN} -- Running post download action for submodule: {YELLOW} {folder} {GREEN} -- {END}")
            os.system(post_download_action)
        return True
            
    elif download_updates:
        did_update = CheckForSubmoduleUpdate(folder)
        if did_update and post_update_action != "":
            print(f"{GREEN} -- Running post update action for submodule: {YELLOW} {folder} {GREEN} -- {END}")
            os.system(post_update_action)
        return did_update
    
    return False
    
def CheckForSubmoduleUpdate(folder: str):
    # Check for updates
    repo = git.Repo(folder)
    origin = repo.remotes.origin
    current_hash = repo.head.object.hexsha
    origin_hash = origin.fetch()
    if len(origin_hash) > 0:
        origin_hash = origin_hash[0].commit.hexsha
    else:
        origin_hash = current_hash
        
    if current_hash != origin_hash:
        print(f"{GREEN} -- Please wait, we need to update the following submodule: {YELLOW} {folder} {GREEN} -- {END}")
        os.system(f"git -C {folder} pull")
        return True
    
    return False