from typing import Literal

ui = []
id = 0

class Title():
    def __init__(self, text: str, size: Literal["xs", "sm", "md", "lg", "xl", "2xl"] = "lg", weight: Literal["thin", "light", "normal", "medium", "semibold", "bold"] = "semibold"):
        global ui
        ui.append({
            "title": {
                "text": text,
                "options": {
                    "weight": weight,
                    "size": size,
                }
            }
        })
        
class Label():
    def __init__(self, text: str, size: Literal["xs", "sm", "md", "lg", "xl", "2xl"] = "sm", weight: Literal["thin", "light", "normal", "medium", "semibold", "bold"] = "normal"):
        global ui
        ui.append({
            "label": {
                "text": text,
                "options": {
                    "weight": weight,
                    "size": size,
                }
            }
        })

class Description():
    def __init__(self, text: str, size: Literal["xs", "sm", "md", "lg", "xl", "2xl"] = "sm", weight: Literal["thin", "light", "normal", "medium", "semibold", "bold", "black"] = "normal"):
        global ui
        ui.append({
            "description": {
                "text": text,
                "options": {
                    "weight": weight,
                    "size": size,
                }
            }
        })

class Button():
    def __init__(self, text: str, title: str, target: object | Literal["submit"], description: str = "", border: bool = True):
        global ui
        ui.append({
            "button": {
                "text": text,
                "title": title,
                "description": description,
                "options": {
                    "target": target.__name__ if hasattr(target, "__name__") else target,
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
    def __init__(self, name: str, key: str, type: Literal["string", "number", "password"], default: any = None, description: str = "", requires_restart: bool = False):
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

class Selector():
    def __init__(self, name: str, key: str, default: any, options: list, description: str = "", requires_restart: bool = False):
        global ui
        ui.append({
            "selector": {
                "name": name,
                "key": key,
                "description": description,
                "requires_restart": requires_restart,
                "options": {
                    "default": default,
                    "options": options
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
        
class Padding():
    def __init__(self, padding: int):
        """Add padding to the UI.

        :param int padding: Padding in pixels.
        """
        self.padding = padding
        
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"padding": {
            "padding": self.padding,
            "components": ui
        }})
        ui = self.previous_ui
        
class Geist():
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"geist": {
            "components": ui
        }})
        ui = self.previous_ui

class Form():
    """
    Form for dialogs.
    
    **NOTE**: You can override the submit button by adding a custom button with the target set to "submit".
    """
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        
        has_submit = False
        for element in ui:
            if "button" in element:
                if element["button"]["options"]["target"] == "submit":
                    has_submit = True
        
        if not has_submit:
            Button("submit", "", "submit", border=False)
        
        self.previous_ui.append({"form": {
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
        
class ProgressBar():
    def __init__(self, value: float, min: float, max: float, description: str = ""):
        global ui, id
        ui.append({
            "progress_bar": {
                "value": value,
                "min": min,
                "max": max,
                "description": description,
                "id": id
            }
        })
        id += 1

class EnabledLock():
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"enabled_lock": {
            "components": ui
        }})
        ui = self.previous_ui

def RenderUI():
    global ui
    temp_ui = ui.copy()
    ui = []
    return temp_ui