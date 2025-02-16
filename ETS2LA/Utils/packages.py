import logging
import sys
from typing import Literal
from urllib.parse import urlparse
from ETS2LA.Utils.Console.colors import *
from ETS2LA.Utils.network import ChooseBestProvider
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Networking.cloud as cloud
from importlib.metadata import version
import traceback
from pip._internal.network.session import user_agent

malicious_packages = {"ultralytics": ["8.3.41", "8.3.42", "8.3.45", "8.3.46"]}


def CheckForMaliciousPackages():
    for package in malicious_packages.keys():
        try:
            ver = version(package)
            if ver in malicious_packages[package]:
                print(
                    RED +
                    f"Your installed version of the '{package}' package might be malicious! Trying to remove it... (Package Version: {ver})"
                    + END)
                ExecuteCommand(f"pip uninstall {package} -y & pip cache purge")
                InstallPackages([f"{package}"], force_reinstall=True)
                cloud.SendCrashReport(
                    package, f"Successfully updated a malicious package.",
                    f"From version {ver} to the latest version.")
                print(
                    GREEN +
                    f"Successfully updated the '{package}' package to the latest version."
                    + END)
        except:
            cloud.SendCrashReport(package, "Update malicious package error.",
                                  traceback.format_exc())
            print(
                RED +
                f"Unable to check the version of the '{package}' package. Please update your '{package}' package manually if you have one of these versions installed: {malicious_packages[package]}"
                + END)


PYPI_GLOBAL = 'https://pypi.org/simple/'
PYPI_MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple/'

selected_pypi_provider = ChooseBestProvider(
    [PYPI_GLOBAL, PYPI_MIRROR],
    timeout=3,
    headers={"User-Agent": user_agent()})


def InstallPackages(packages: list[str], *, force_reinstall: bool = False):
    index_url = selected_pypi_provider
    for package in packages:
        try:
            args = [
                sys.executable, "-m", "pip", "install", package, "--index-url",
                index_url, "--trusted-host",
                urlparse(index_url).netloc
            ]
            if force_reinstall:
                args.append("--force-reinstall")
            print(args)
            ExecuteCommand(args, shell=False)
        except:
            cloud.SendCrashReport(package, "Install package error.",
                                  traceback.format_exc())
            logging.error(
                f"Unable to install the '{package}' package. Please install it manually."
            )


def ParseVersion(ver: str | tuple) -> tuple:
    if isinstance(ver, tuple):
        return ver
    return tuple(map(int, ver.split(".")))


def CompareVersions(a: str | tuple, b: str | tuple) -> Literal[-1, 0, 1]:
    if isinstance(a, tuple) and isinstance(b, tuple):
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0
    else:
        parsed_a, parsed_b = ParseVersion(a), ParseVersion(b)
        return CompareVersions(parsed_a, parsed_b)


def FixModule(module: str, ver: str | tuple, url: str):
    try:
        cur_ver = version(module)
    except:
        cur_ver = "0.0.0"

    if CompareVersions(cur_ver, ver) < 0:
        print(
            f"Please wait, we need to install the correct version of {module}..."
        )
        InstallPackages([f"{url}"])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    selected_pypi_provider = ChooseBestProvider(
        [PYPI_GLOBAL, PYPI_MIRROR],
        verbose=True,
        timeout=3,
        headers={"User-Agent": user_agent()})
    print("Selected PyPI provider:", selected_pypi_provider)
    InstallPackages(["opencv-contrib-python"])
