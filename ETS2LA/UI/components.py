from typing import Literal

ui = []

class Title():
    def __init__(self, text: str):
        global ui
        ui.append({
            "title": {
                "text": text
            }
        })
        
class Label():
    def __init__(self, text: str):
        global ui
        ui.append({
            "label": {
                "text": text
            }
        })

class Description():
    def __init__(self, text: str):
        global ui
        ui.append({
            "description": {
                "text": text
            }
        })

class Button():
    def __init__(self, text: str, target: object):
        global ui
        ui.append({
            "button": {
                "text": text,
                "target": target.__name__
            }
        })
        
class Input():
    def __init__(self, name: str, key: str, type: Literal["string", "number"], default: any = None, suffix: str = None, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "input": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "type": type,
                    "default": default,
                    "suffix": suffix,
                },
            }
        })

class Switch():
    def __init__(self, name: str, key: str, default: bool, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "switch": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "default": default
                }
            }
        })
        
class Toggle():
    def __init__(self, name: str, key: str, default: bool, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "toggle": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "default": default
                }
            }
        })
        
class Slider():
    def __init__(self, name: str, key: str, default: float, min: float, max: float, step: float, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "slider": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "default": default,
                    "min": min,
                    "max": max,
                    "step": step
                }
            }
        })

class TabView():
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"tabview": ui})
        for element in ui:
            if "tab" not in element:
                raise ValueError("TabView can only contain Tab elements")
        ui = self.previous_ui

class Tab():
    def __init__(self, name: str):
        self.name = name
    
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"tab": {
            "name": self.name,
            "components": ui
        }})
        ui = self.previous_ui
        
class Group():
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"group": ui})
        ui = self.previous_ui

def RenderUI():
    global ui
    temp_ui = ui.copy()
    ui = []
    return temp_ui