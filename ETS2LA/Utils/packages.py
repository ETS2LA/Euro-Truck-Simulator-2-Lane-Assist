from ETS2LA.Utils.Console.colors import *
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Networking.cloud as cloud
from importlib.metadata import version
from typing import TypeAlias, Union
import traceback
import os

malicious_packages = {
    "ultralytics": ["8.3.41", "8.3.42", "8.3.45", "8.3.46"]
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

VersionType: TypeAlias = Union[
    int,
    tuple[int],
    tuple[int, int],
    tuple[int, int, int],
    str,
]

def ConvertVersionToTuple(ver: VersionType) -> tuple:
    if isinstance(ver, str):
        return tuple(map(int, ver.split(".")))
    elif isinstance(ver, int):
        return (ver,)
    elif isinstance(ver, tuple):
        return ver
    else:
        raise ValueError(f"Invalid version type: {type(ver)}")

def CompareVersions(ver1: VersionType, ver2: VersionType) -> int:
    a, b = ConvertVersionToTuple(ver1), ConvertVersionToTuple(ver2)
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0

def FixModule(module: str, ver: VersionType, install_source: str):
    try:
        cur_ver = version(module)
    except:
        cur_ver = "0.0.0"
        
    if CompareVersions(cur_ver, ver) < 0:
        print(f"Please wait, we need to install the correct version of {module}...")
        ExecuteCommand(f"pip install {install_source}")