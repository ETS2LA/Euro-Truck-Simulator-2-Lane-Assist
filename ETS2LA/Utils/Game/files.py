"""Reads information like configs or controls from the game files.
This file is quite old but still works, it just means the code is not
that pretty... well that might be an understatement, it's quite ugly :)
"""

import os
import winreg
import traceback
import ctypes.wintypes
from ETS2LA.Networking.cloud import SendCrashReport

RED = "\033[91m"
NORMAL = "\033[0m"


def get_paths():
    global STEAM_PATH
    global ETS2_STEAM_PATH
    global ATS_STEAM_PATH
    global ETS2_STEAM_FOUND
    global ATS_STEAM_FOUND
    global DOCUMENTS_PATH
    global ETS2_DOCUMENTS_PATH
    global ATS_DOCUMENTS_PATH
    global ETS2_DOCUMENTS_FOUND
    global ATS_DOCUMENTS_FOUND
    global ETS2_LAST_LOG_CHANGE
    global ATS_LAST_LOG_CHANGE

    try:
        STEAM_PATH = winreg.QueryValueEx(
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam"),
            "SteamPath",
        )[0]
    except Exception:
        STEAM_PATH = r"C:/program files (x86)/steam"

    ETS2_STEAM_PATH = STEAM_PATH + r"/steamapps/common/Euro Truck Simulator 2"
    ATS_STEAM_PATH = STEAM_PATH + r"/steamapps/common/American Truck Simulator"

    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
    )
    DOCUMENTS_PATH = f"{buf.value}"
    DOCUMENTS_PATH = DOCUMENTS_PATH.replace("\\", "/")

    ETS2_STEAM_FOUND = os.path.exists(ETS2_STEAM_PATH)
    ATS_STEAM_FOUND = os.path.exists(ATS_STEAM_PATH)

    ETS2_DOCUMENTS_PATH = DOCUMENTS_PATH + "/Euro Truck Simulator 2"
    ATS_DOCUMENTS_PATH = DOCUMENTS_PATH + "/American Truck Simulator"

    ETS2_DOCUMENTS_FOUND = os.path.exists(ETS2_DOCUMENTS_PATH)
    ATS_DOCUMENTS_FOUND = os.path.exists(ATS_DOCUMENTS_PATH)

    if ETS2_DOCUMENTS_FOUND:
        ETS2_LAST_LOG_CHANGE = os.path.getmtime(f"{ETS2_DOCUMENTS_PATH}/game.log.txt")
    else:
        ETS2_LAST_LOG_CHANGE = 0
    if ATS_DOCUMENTS_FOUND:
        ATS_LAST_LOG_CHANGE = os.path.getmtime(f"{ATS_DOCUMENTS_PATH}/game.log.txt")
    else:
        ATS_LAST_LOG_CHANGE = 0


def ReadProfileControlsFile(game="automatic"):
    """Reads the controls file of the selected game with the most recent usedprofile.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                profiles = []
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/profiles"):
                        if os.path.exists(
                            ETS2_DOCUMENTS_PATH
                            + "/profiles/"
                            + folder
                            + "/controls.sii"
                        ):
                            profiles.append(
                                (
                                    f"profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ETS2_DOCUMENTS_PATH}/profiles/{folder}"
                                    ),
                                )
                            )
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                        if os.path.exists(
                            ETS2_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + folder
                            + "/controls.sii"
                        ):
                            profiles.append(
                                (
                                    f"steam_profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ETS2_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                    ),
                                )
                            )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    with open(
                        f"{ETS2_DOCUMENTS_PATH}/{most_recent_profile[0]}/controls.sii",
                        "r",
                    ) as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No profile with controls in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                profiles = []
                if os.path.exists(ATS_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/profiles"):
                        if os.path.exists(
                            ATS_DOCUMENTS_PATH + "/profiles/" + folder + "/controls.sii"
                        ):
                            profiles.append(
                                (
                                    f"profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ATS_DOCUMENTS_PATH}/profiles/{folder}"
                                    ),
                                )
                            )
                if os.path.exists(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                        if os.path.exists(
                            ATS_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + folder
                            + "/controls.sii"
                        ):
                            profiles.append(
                                (
                                    f"steam_profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ATS_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                    ),
                                )
                            )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    with open(
                        f"{ATS_DOCUMENTS_PATH}/{most_recent_profile[0]}/controls.sii",
                        "r",
                    ) as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No profile with controls in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to read file." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: ReadProfileControlsFile", str(exc))
        print("Error in gamefiles.py: ReadProfileControlsFile" + str(e))


def ReadProfileConfigFile(game="automatic"):
    """Reads the config_local file of the selected game with the most recent usedprofile.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                profiles = []
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/profiles"):
                        if os.path.exists(
                            ETS2_DOCUMENTS_PATH
                            + "/profiles/"
                            + folder
                            + "/config_local.cfg"
                        ):
                            profiles.append(
                                (
                                    f"profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ETS2_DOCUMENTS_PATH}/profiles/{folder}"
                                    ),
                                )
                            )
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                        if os.path.exists(
                            ETS2_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + folder
                            + "/config_local.cfg"
                        ):
                            profiles.append(
                                (
                                    f"steam_profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ETS2_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                    ),
                                )
                            )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    with open(
                        f"{ETS2_DOCUMENTS_PATH}/{most_recent_profile[0]}/config_local.cfg",
                        "r",
                    ) as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No profile with controls in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                profiles = []
                if os.path.exists(ATS_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/profiles"):
                        if os.path.exists(
                            ATS_DOCUMENTS_PATH
                            + "/profiles/"
                            + folder
                            + "/config_local.cfg"
                        ):
                            profiles.append(
                                (
                                    f"profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ATS_DOCUMENTS_PATH}/profiles/{folder}"
                                    ),
                                )
                            )
                if os.path.exists(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                        if os.path.exists(
                            ATS_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + folder
                            + "/config_local.cfg"
                        ):
                            profiles.append(
                                (
                                    f"steam_profiles/{folder}",
                                    os.path.getmtime(
                                        f"{ATS_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                    ),
                                )
                            )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    with open(
                        f"{ATS_DOCUMENTS_PATH}/{most_recent_profile[0]}/config_local.cfg",
                        "r",
                    ) as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No profile with controls in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to read file." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: ReadProfileConfigFile", str(exc))
        print("Error in gamefiles.py: ReadProfileConfigFile" + str(e))


def ReadGlobalControlsFile(game="automatic"):
    """Reads the global controls file of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/global_controls.sii"):
                    with open(
                        f"{ETS2_DOCUMENTS_PATH}/global_controls.sii", "r"
                    ) as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No global controls file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                if os.path.exists(ATS_DOCUMENTS_PATH + "/global_controls.sii"):
                    with open(f"{ATS_DOCUMENTS_PATH}/global_controls.sii", "r") as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No global controls file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to read file." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: ReadGlobalControlsFile", str(exc))
        print("Error in gamefiles.py: ReadGlobalControlsFile" + str(e))


def ReadGlobalConfigFile(game="automatic"):
    """Reads the global config file of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/config.cfg"):
                    with open(f"{ETS2_DOCUMENTS_PATH}/config.cfg", "r") as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No global config file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                if os.path.exists(ATS_DOCUMENTS_PATH + "/config.cfg"):
                    with open(f"{ATS_DOCUMENTS_PATH}/config.cfg", "r") as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No global config file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to read file." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: ReadGlobalConfigFile", str(exc))
        print("Error in gamefiles.py: ReadGlobalConfigFile" + str(e))


def ReadGameLogFile(game="automatic"):
    """Reads the game log of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/game.log.txt"):
                    with open(f"{ETS2_DOCUMENTS_PATH}/game.log.txt", "r") as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No game log file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                if os.path.exists(ATS_DOCUMENTS_PATH + "/game.log.txt"):
                    with open(f"{ATS_DOCUMENTS_PATH}/game.log.txt", "r") as file:
                        return file.read()
                else:
                    print(
                        RED
                        + "No game log file in documents found, unable to read file."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to read file." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: ReadGameLogFile", str(exc))
        print("Error in gamefiles.py: ReadGameLogFile" + str(e))


def GetCurrentProfile(game="automatic"):
    """Returns the ID of the current profile of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                profiles = []
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ETS2_DOCUMENTS_PATH}/profiles/{folder}"
                                ),
                            )
                        )
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ETS2_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                ),
                            )
                        )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    return most_recent_profile[0]
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return ID."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                profiles = []
                if os.path.exists(ATS_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ATS_DOCUMENTS_PATH}/profiles/{folder}"
                                ),
                            )
                        )
                if os.path.exists(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ATS_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                ),
                            )
                        )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    return most_recent_profile[0]
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return ID."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to return ID." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: GetCurrentProfile", str(exc))
        print("Error in gamefiles.py: GetCurrentProfile" + str(e))


def GetCurrentProfilePath(game="automatic"):
    """Returns the ID of the current profile of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                profiles = []
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ETS2_DOCUMENTS_PATH}/profiles/{folder}"
                                ),
                            )
                        )
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ETS2_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                ),
                            )
                        )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    if os.path.exists(
                        ETS2_DOCUMENTS_PATH + "/profiles/" + most_recent_profile[0]
                    ):
                        path = (
                            ETS2_DOCUMENTS_PATH + "/profiles/" + most_recent_profile[0]
                        )
                        return path
                    if os.path.exists(
                        ETS2_DOCUMENTS_PATH
                        + "/steam_profiles/"
                        + most_recent_profile[0]
                    ):
                        path = (
                            ETS2_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + most_recent_profile[0]
                        )
                        return path
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return path."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                profiles = []
                if os.path.exists(ATS_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ATS_DOCUMENTS_PATH}/profiles/{folder}"
                                ),
                            )
                        )
                if os.path.exists(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append(
                            (
                                folder,
                                os.path.getmtime(
                                    f"{ATS_DOCUMENTS_PATH}/steam_profiles/{folder}"
                                ),
                            )
                        )
                if profiles != []:
                    profiles.sort(key=lambda x: x[1], reverse=True)
                    most_recent_profile = profiles[0]
                else:
                    most_recent_profile = None
                if most_recent_profile is not None:
                    if os.path.exists(
                        ATS_DOCUMENTS_PATH + "/profiles/" + most_recent_profile[0]
                    ):
                        path = (
                            ATS_DOCUMENTS_PATH + "/profiles/" + most_recent_profile[0]
                        )
                        return path
                    if os.path.exists(
                        ATS_DOCUMENTS_PATH + "/steam_profiles/" + most_recent_profile[0]
                    ):
                        path = (
                            ATS_DOCUMENTS_PATH
                            + "/steam_profiles/"
                            + most_recent_profile[0]
                        )
                        return path
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return ID."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to return ID." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: GetCurrentProfile", str(exc))
        print("Error in gamefiles.py: GetCurrentProfile" + str(e))


def GetAllProfiles(game="automatic"):
    """Returns a list of all profiles of the selected game.
    game: "automatic" or "ats" or "ets2"
    """
    get_paths()
    try:
        if ETS2_DOCUMENTS_FOUND or ATS_DOCUMENTS_FOUND:
            if game == "automatic":
                if ETS2_DOCUMENTS_FOUND and ATS_DOCUMENTS_FOUND:
                    if ETS2_LAST_LOG_CHANGE > ATS_LAST_LOG_CHANGE:
                        game = "ets2"
                    else:
                        game = "ats"
                elif ETS2_DOCUMENTS_FOUND:
                    game = "ets2"
                elif ATS_DOCUMENTS_FOUND:
                    game = "ats"

            if game == "ets2":
                profiles = []
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/profiles"):
                        profiles.append((folder))
                if os.path.exists(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ETS2_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append((folder))
                if profiles != []:
                    return profiles
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return IDs."
                        + NORMAL
                    )
                    return None

            if game == "ats":
                profiles = []
                if os.path.exists(ATS_DOCUMENTS_PATH + "/profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/profiles"):
                        profiles.append((folder))
                if os.path.exists(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                    for folder in os.listdir(ATS_DOCUMENTS_PATH + "/steam_profiles"):
                        profiles.append((folder))
                if profiles != []:
                    return profiles
                else:
                    print(
                        RED
                        + "No profiles in documents found, unable to return IDs."
                        + NORMAL
                    )
                    return None

        else:
            print(RED + "No game in documents found, unable to return IDs." + NORMAL)
            return None
    except Exception as e:
        exc = traceback.format_exc()
        SendCrashReport("Error in gamefiles.py: GetAllProfiles", str(exc))
        print("Error in gamefiles.py: GetAllProfiles" + str(e))
