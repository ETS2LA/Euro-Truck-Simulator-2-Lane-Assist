"""Data extraction utilities for map plugin."""

from Plugins.Map.settings import settings
import requests
import logging
import zipfile
import shutil
import orjson
import json
import yaml
import os

fallback = False
plugin = None
index_url = "https://gitlab.com/ETS2LA/data/-/raw/main/index.yaml"


def IsDownloaded(path: str) -> bool:
    if not os.path.exists(path):
        return False
    if "config.json" in os.listdir(path):
        return True
    return False


index = {}


def GetIndex() -> dict:
    global index
    if index != {}:
        return index

    response = requests.get(index_url)
    if response.status_code == 200:
        index = yaml.safe_load(response.text)
        return index

    return {}


configs = {}


def GetConfig(path: str) -> dict:
    global configs
    if configs.get(path):
        return configs[path]

    url = index_url.replace("index.yaml", path)
    response = requests.get(url)
    if response.status_code == 200:
        configs[path] = yaml.safe_load(response.text)
        return configs[path]

    return {}


def ExtractData(filename: str, path: str) -> None:
    if os.path.exists(path):
        logging.warning(f"Deleting existing data folder: {path}")
        shutil.rmtree(path)

    if not os.path.exists(path):
        os.makedirs(path)

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(path)


def ReadData(path: str) -> dict:
    global fallback
    f = open(path, "r", encoding="utf-8")

    if fallback:
        data = json.load(f)
        if not data:
            logging.error(f"Failed to load Map data JSON file: {path}")
    else:
        try:
            data = orjson.loads(f.read())
        except orjson.JSONDecodeError:
            logging.warning(
                "Failed to decode JSON with orjson, falling back to json module."
            )
            fallback = True
            data = ReadData(path)

    f.close()
    return data


def UpdateData(name: str) -> bool:
    global index, configs

    if os.path.exists("Plugins/Map/data.zip"):
        os.remove("Plugins/Map/data.zip")

    if configs == {}:
        return False

    selected_path = ""
    selected_config = None
    for path, config in configs.items():
        if config["name"] == name:
            selected_config = config
            selected_path = path
            break

    if not config or selected_path == "":
        logging.warning(f"Failed to find sufficient data to download {name}.")
        return False

    index_key = [
        key for key, value in index.items() if value["config"] == selected_path
    ]
    if not index_key:
        logging.warning(f"Failed to find index key for {name}.")
        return False
    index_key = index_key[0]

    try:
        url = index_url.replace("index.yaml", index[index_key]["path"])
        response = requests.get(url, stream=True)

        total_size = int(response.headers.get("content-length", config["packed_size"]))
        block_size = 1024

        with open("Plugins/Map/data.zip", "wb") as f:
            for data in response.iter_content(block_size):
                progress = f.tell() / total_size
                plugin.state.progress = progress
                plugin.state.text = f"Downloading {f.tell() / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB"
                f.write(data)

        plugin.state.progress = 0
        plugin.state.text = "Unpacking data..."
        ExtractData("Plugins/Map/data.zip", "Plugins/Map/data")
        os.remove("Plugins/Map/data.zip")

        with open("Plugins/Map/data/config.json", "w") as f:
            json.dump(selected_config, f, indent=4)

        plugin.state.reset()
    except Exception:
        settings.downloaded_data = ""
        plugin.state.reset()
        logging.exception(f"Failed to download and unpack {name}.")
        return False

    settings.downloaded_data = name
    logging.info(f"Downloaded and unpacked {name}.")
    return True
