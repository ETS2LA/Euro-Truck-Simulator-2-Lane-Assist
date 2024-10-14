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
    def __init__(self, name: str, key: str, type: Literal["string", "number", "boolean", "array", "object", "enum"], default: any = None, min: float = None, max: float = None, step: float = None, suffix: str = None, values: list = None, description: str = "", requires_restart: bool = False):
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
                    "min": min,
                    "max": max,
                    "step": step,
                    "suffix": suffix,
                    "values": values,
                },
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