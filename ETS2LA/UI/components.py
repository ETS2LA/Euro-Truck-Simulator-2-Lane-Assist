from typing import Literal, Union

ui = []
id = 0

button_variants = Literal["default", "link", "outline", "destructive", "secondary", "ghost"]
toggle_variants = Literal["default", "outline"]
input_types = Literal["string", "number", "password"]
group_directions = Literal["horizontal", "vertical"]

class Label:
    """Represents a label UI component."""
    def __init__(self, text: str, classname: str = "", url: str = ""):
        """
        Args:
            text (str): The text for the label.
            classname (str): Additional CSS classnames.
            url (str): Optional URL for the label.
        """
        global ui
        ui.append({
            "label": {
                "text": text,
                "classname": classname,
                "url": url                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
            }
        })

class Markdown:
    """Represents a markdown UI component."""
    def __init__(self, text: str):
        """
        Args:
            text (str): The markdown content to render.
        """
        global ui
        ui.append({
            "markdown": {
                "text": text
            }
        })

class Button:
    """Represents a button UI component."""
    def __init__(self, text: str, classname: str = "", variant: button_variants = "default", target: Union[callable, str]= None, args: list = []):
        """
        Args:
            text (str): The button label.
            classname (str): Additional CSS classnames.
            variant (button_variants): Button style variant.
            target (callable | str): The function or identifier to call on click.
            args (list): Arguments to pass to the target function.
        """
        global ui
        ui.append({
            "button": {
                "text": text,
                "variant": variant,
                "classname": classname,
                "target": target.__name__ if hasattr(target, "__name__") else target,
                "args": args
            }
        })

class Separator:
    """Represents a separator line in the UI."""
    def __init__(self):
        global ui
        ui.append({"separator": {}})

class Space:
    """Represents vertical space in the UI."""
    def __init__(self, height: int):
        """
        Args:
            height (int): Height of the space in pixels.
        """
        global ui
        ui.append({
            "space": {
                "height": height
            }
        })

class Input:
    """Represents an input field."""
    def __init__(self, name: str, input_type: input_types, setting_key: str, setting_default: any = None, classname: str = "", description: str = "", requires_restart: bool = False):
        """
        Args:
            name (str): Label for the input.
            input_type (input_types): Type of input (e.g., string, number).
            setting_key (str): Key to store the setting.
            setting_default (any): Default value for the input.
            classname (str): Additional CSS classnames.
            description (str): Description of the input.
            requires_restart (bool): Whether changes require a restart.
        """
        global ui
        ui.append({
            "input": {
                "name": name,
                "description": description,
                "input_type": input_type,
                "classname": classname,
                "setting_key": setting_key,
                "setting_default": setting_default,
                "requires_restart": requires_restart
            }
        })

class Switch:
    """Represents a toggle switch."""
    def __init__(self, name: str, setting_key: str, setting_default: bool, classname: str = "", description: str = "", requires_restart: bool = False):
        """
        Args:
            name (str): Label for the switch.
            setting_key (str): Key to store the setting.
            setting_default (bool): Default value for the switch.
            classname (str): Additional CSS classnames.
            description (str): Description of the switch.
            requires_restart (bool): Whether changes require a restart.
        """
        global ui
        ui.append({
            "switch": {
                "name": name,
                "description": description,
                "classname": classname,
                "setting_key": setting_key,
                "setting_default": setting_default,
                "requires_restart": requires_restart
            }
        })

class Toggle:
    """Represents a toggle button."""
    def __init__(self, name: str, setting_key: str, setting_default: bool, variant : toggle_variants = "default", classname: str = "", description: str = "", requires_restart: bool = False):
        """
        Args:
            name (str): Label for the toggle.
            setting_key (str): Key to store the setting.
            setting_default (bool): Default value for the toggle.
            variant (toggle_variants): Toggle style variant.
            classname (str): Additional CSS classnames.
            description (str): Description of the toggle.
            requires_restart (bool): Whether changes require a restart.
        """
        global ui
        ui.append({
            "toggle": {
                "name": name,
                "description": description,
                "variant": variant,
                "classname": classname,
                "setting_key": setting_key,
                "setting_default": setting_default,
                "requires_restart": requires_restart
            }
        })

class Slider:
    """Represents a slider input component."""
    def __init__(self, name: str, setting_key: str, setting_default: float, setting_min: float, setting_max: float, setting_step: float, classname: str = "", description: str = "", requires_restart: bool = False):
        """
        Args:
            name (str): Label for the slider.
            setting_key (str): Key to store the setting.
            setting_default (float): Default value for the slider.
            setting_min (float): Minimum value for the slider.
            setting_max (float): Maximum value for the slider.
            setting_step (float): Step size for the slider.
            classname (str): Additional CSS classnames.
            description (str): Description of the slider.
            requires_restart (bool): Whether changes require a restart.
        """
        global ui
        ui.append({
            "slider": {
                "name": name,
                "description": description,
                "setting_key": setting_key,
                "setting_default": setting_default,
                "setting_min": setting_min,
                "setting_max": setting_max,
                "setting_step": setting_step,
                "classname": classname,
                "requires_restart": requires_restart
            }
        })

class Selector:
    """Represents a dropdown selector component."""
    def __init__(self, name: str, setting_key: str, setting_default: any, setting_options: list, description: str = "", requires_restart: bool = False):
        """
        Args:
            name (str): Label for the selector.
            setting_key (str): Key to store the setting.
            setting_default (any): Default selected option.
            setting_options (list): List of selectable options.
            description (str): Description of the selector.
            requires_restart (bool): Whether changes require a restart.
        """
        global ui
        ui.append({
            "selector": {
                "name": name,
                "description": description,
                "setting_key": setting_key,
                "setting_default": setting_default,
                "setting_options": setting_options,
                "requires_restart": requires_restart
            }
        })

class TabView:
    """Represents a container for tabs."""
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

class Tab:
    """Represents an individual tab."""
    def __init__(self, name: str):
        """
        Args:
            name (str): The name of the tab.
        """
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

class Group:
    """Represents a grouped set of components."""
    def __init__(self, direction: group_directions, classname: str = "", border: bool = False):
        """
        Args:
            classname (str): Additional CSS classnames for the group.
            border (bool): Whether the group should have a border.
        """
        # Add flex direction, border, and classnames together
        self.classname = f"flex flex-{'col' if direction == 'vertical' else 'row'} {classname}{' border rounded-md' if border else ''}"

    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"group": {
            "classname": self.classname,
            "components": ui
        }})
        ui = self.previous_ui

class Tooltip:
    """Represents a tooltip for a component."""
    def __init__(self, text: str, classname: str = ""):
        """
        Args:
            text (str): Tooltip text.
            classname (str): Additional CSS classnames.
        """
        self.text = text
        self.classname = classname

    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui
        self.previous_ui.append({"tooltip": {
            "text": self.text,
            "classname": self.classname,
            "components": ui
        }})
        ui = self.previous_ui

class Padding:
    """Represents padding around a group of components."""
    def __init__(self, padding: int):
        """
        Args:
            padding (int): Padding value in pixels.
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

class Geist:
    """Represents a Geist-style container."""
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

class Form:
    """Represents a form container with optional submit handling."""
    def __enter__(self):
        global ui
        self.previous_ui = ui
        ui = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global ui

        print("ETS2LA UI: Forms are not currently supported. All components in the form will be discarded.")
        return

        has_submit = False
        for element in ui:
            if "button" in element:
                if element["button"].get("target") == "submit":
                    has_submit = True

        if not has_submit:
            Button("submit", "", "default", target="submit")

        self.previous_ui.append({"form": {
            "components": ui
        }})
        ui = self.previous_ui

class RefreshRate:
    """Sets the refresh rate of the UI."""
    def __init__(self, time: int):
        """
        Args:
            time (int): Refresh rate in seconds.
        """
        global ui

        ui.insert(0, {
            "refresh_rate": time
        })

class ProgressBar:
    """Represents a progress bar component."""
    def __init__(self, value: float, min: float, max: float, classname: str = "", description: str = ""):
        """
        Args:
            value (float): Current progress value.
            min (float): Minimum value.
            max (float): Maximum value.
            classname (str): Additional CSS classnames.
            description (str): Description of the progress bar.
        """
        global ui, id
        ui.append({
            "progress_bar": {
                "value": value,
                "min": min,
                "max": max,
                "classname": classname,
                "description": description,
                "id": id
            }
        })
        id += 1

class EnabledLock:
    """Represents a container that locks UI components based on conditions."""
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

class ButtonGroup:
    """Represents a card with a title, description, and a button"""
    def __init__(self, title: str, description: str, button_text: str, target: callable, target_args: list = [], classname: str = ""):
        with Group("horizontal", classname=f"flex justify-between p-4 items-center {classname}", border=True):
            with Group("vertical", classname="flex flex-col gap-1 pr-12"):
                Label(title, classname="text-lg font-bold")
                Label(description, classname="text-xs text-muted-foreground")
            Button(button_text, target=target, args=target_args, classname="w-128 justify-end")

def RenderUI():
    """Renders the UI components as a list and resets the global UI state."""
    global ui
    temp_ui = ui.copy()
    ui = []
    return temp_ui