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
    def __init__(self, text: str, title: str, target: object, description: str = "", border: bool = True):
        global ui
        ui.append({
            "button": {
                "text": text,
                "title": title,
                "description": description,
                "options": {
                    "target": target.__name__,
                    "border": border
                }
            }
        })
        
class Separator():
    def __init__(self):
        global ui
        ui.append({
            "separator": {}
        })
        
class Space():
    def __init__(self, height: int):
        global ui
        ui.append({
            "space": {
                "height": height
            }
        })
        
class Input():
    def __init__(self, name: str, key: str, type: Literal["string", "number"], default: any = None, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "input": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "type": type,
                    "default": default
                },
            }
        })

class Switch():
    def __init__(self, name: str, key: str, default: bool, description: str = "", requires_restart: bool = False, border: bool = True):
        global ui
        ui.append({
            "switch": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "default": default,
                    "border": border
                }
            }
        })
        
class Toggle():
    def __init__(self, name: str, key: str, default: bool, description: str = "", requires_restart: bool = False, separator: bool = True, border: bool = True):
        global ui
        ui.append({
            "toggle": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "separator": separator,
                    "default": default,
                    "border": border
                }
            }
        })
        
class Slider():
    def __init__(self, name: str, key: str, default: float, min: float, max: float, step: float, description: str = "", requires_restart: bool = False, suffix: str = ""):
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
                    "step": step,
                    "suffix": suffix
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
        self.previous_ui.append({"tabview": {
            "components": ui
        }})
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
    def __init__(self, direction: Literal["horizontal", "vertical"] = "horizontal", gap: int = 2, border: bool = False):
        self.direction = direction
        self.gap = gap
        self.border = border
    
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"group": {
            "direction": self.direction,
            "gap": self.gap,
            "border": self.border,
            "components": ui
        }})
        ui = self.previous_ui

class RefreshRate():
    """
    Set the refresh rate of the UI in seconds.
    ie. RefreshRate(0.5) will refresh the UI every 0.5 seconds (2fps).
    
    **WARNING**: This will affect ALL plugins' performance while the UI is open!
    """
    def __init__(self, time: int):
        """
        Set the refresh rate of the UI in seconds.
        ie. RefreshRate(0.5) will refresh the UI every 0.5 seconds (2fps).
        
        **WARNING**: This will affect ALL plugins' performance while the UI is open!
        """
        global ui
        ui.insert(0, {
            "refresh_rate": time
        })

def RenderUI():
    global ui
    temp_ui = ui.copy()
    ui = []
    return temp_ui