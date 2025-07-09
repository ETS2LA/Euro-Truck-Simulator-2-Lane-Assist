import logging
import json
import time
import os
class Settings(object):
    last_update = 0
    lock = False
    
    def __init__(self, path: str) -> None:
        self._settings = {}
        self._path = path
        self.lock = False
        if not os.path.exists(f"{self._path}/settings.json"):
            os.makedirs(self._path, exist_ok=True)
            self._save()
        else:
            self._load()

    def _load(self):
        try:
            while self.lock:
                time.sleep(0.001)
            
            self.lock = True
            with open(f"{self._path}/settings.json", "r") as file:
                self._settings = json.load(file)
            
            self.last_update = os.path.getmtime(f"{self._path}/settings.json")
            self.lock = False
        except:
            self.lock = False
            logging.warning("Failed to load settings, you can ignore this if it's not repeating consistently.")

    def _save(self):
        try:
            while self.lock:
                time.sleep(0.001)
            
            self.lock = True
            with open(f"{self._path}/settings.json", "w") as file:
                json.dump(self._settings, file, indent=4)

            self.last_update = os.path.getmtime(f"{self._path}/settings.json")
            self.lock = False
        except:
            self.lock = False
            logging.warning("Failed to save settings, you can ignore this if it's not repeating consistently.")

    def get(self, name: str, default=None):
        if self.last_update != os.path.getmtime(f"{self._path}/settings.json"):
            self._load()
        
        return self._settings.get(name, default)

    def __getattr__(self, name):
        if name in ['_path', '_settings', 'last_update', 'lock']:
            return super().__getattr__(name)
        
        if self.last_update != os.path.getmtime(f"{self._path}/settings.json"):
            self._load()
        
        if name in self._settings:
            return self._settings[name]
        
        logging.warning(f"Setting '{name}' not found in settings file")
        return None

    def set(self, name: str, value):
        self._settings[name] = value
        self._save()

    def __setattr__(self, name, value):
        if name in ['_path', '_settings', 'last_update', 'lock']:
            super().__setattr__(name, value)
        else:
            self._settings[name] = value
            self._save()