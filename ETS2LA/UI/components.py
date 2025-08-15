from ETS2LA.UI.styles import Style
import ETS2LA.UI.styles as styles

from collections.abc import Callable
from typing import Literal
import base64 as b64
import numpy as np
import inspect

dictionary: list[dict] = []
current_id: int = 0

def increment() -> int:
    """Increment the current id and return it."""
    global current_id
    current_id += 1
    return current_id - 1

def get_fully_qualified_name(func: Callable) -> str:
    """
    Get the fully qualified name of a function.
    For example: `Plugins.Map.Reload`.
    """
    mod = inspect.getmodule(func)
    if mod is None or not hasattr(func, "__qualname__"):
        raise ValueError("Cannot get qualified name")

    return f"{mod.__name__}.{func.__qualname__}"

class Side:
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

class Text():
    """
    This class is used to create a basic text element. You can get
    different preset styles from `ETS2LA.UI.styles` or create your own.
    ```python
    Text("Hello Title", styles.Title())
    Text("Hello Description", styles.Description())
    Text("Hello PlainText", styles.PlainText())
    ```
    """
    def __init__(self, text: str, style: Style = Style(), pressed: Callable | None = None):
        self.id = increment()

        self.text = text
        self.style = style
        self.pressed = pressed
        
        dictionary.append({
            "text": {
                "id": self.id,
                "text": text,
                "style": style.to_dict(),
                "pressed": get_fully_qualified_name(self.pressed) if self.pressed else None
            }
        })
        
class Link():
    """
    Identical to the Text class, but with an additional `url` parameter.
    Includes default styling for links, this can be overridden with
    Style.classname or just by editing the CSS with Style.
    """
    def __init__(self, text: str, url: str, style: Style = Style()):
        self.id = increment()

        self.text = text
        self.url = url
        self.style = style
        
        dictionary.append({
            "link": {
                "id": self.id,
                "text": text,
                "url": url,
                "style": style.to_dict()
            }
        })
        
class Markdown():
    """
    Render markdown text. Supports almost all markdown features from
    codeblocks all the way to iframes. The `style` parameter here controls
    the container of the markdown element, not the markdown itself.
    """
    def __init__(self, text: str, style: Style = Style()):
        self.id = increment()

        self.text = text
        self.style = style
        
        dictionary.append({
            "markdown": {
                "id": self.id,
                "text": text,
                "style": style.to_dict()
            }
        })
        
class Icon():
    """
    This class will render any Lucide-React icon. You can
    see a list of them at https://lucide.dev/icons. 
    """
    def __init__(self, icon: str, style: Style = Style()):
        self.id = increment()

        self.icon = icon
        self.style = style
        
        dictionary.append({
            "icon": {
                "id": self.id,
                "icon": icon,
                "style": style.to_dict()
            }
        })
        
class SeparatorType():
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    
class Separator():
    """
    This class is used to create a separator. It is a simple line
    that can be styled with the `style` parameter.
    """
    def __init__(self, style: Style = Style(), direction: Literal["vertical", "horizontal"] = SeparatorType.HORIZONTAL):
        self.id = increment()
        self.style = style
        self.direction = direction
        
        dictionary.append({
            "separator": {
                "id": self.id,
                "direction": direction,
                "style": style.to_dict()
            }
        })
        
class Space():
    """
    This class is used to create a space. It is a simple div that can be
    resized with the `style` parameter. You can use this to create padding
    or margin between elements without styling them directly.
    """
    def __init__(self, style: Style = Style()):
        self.id = increment()
        self.style = style
        
        dictionary.append({
            "space": {
                "id": self.id,
                "style": style.to_dict()
            }
        })
        
class Container():
    """
    This class is used to create a container element. It basically just holds
    other elements inside it. You use this element with the python `with` 
    statement to easily add elements to it.
    ```python
    with Container(styles.FlexVertical):
        Text("Hello World")
        Text("Hello World 2")
    ```
    """
    def __init__(self, style: Style = Style(), pressed: Callable | None = None):
        self.id = increment()
        self.style = style
        self.pressed = pressed
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "container": {
                "id": self.id,
                "style": self.style.to_dict(),
                "pressed": get_fully_qualified_name(self.pressed) if self.pressed else None,
                "children": dictionary
            }
        })
        dictionary = self.previous

_elements = {}
class _SubElement():
    """Do not use. This is an internal class"""
    
    _name: str = ""
    
    def __init__(self, style: Style = Style()):
        self.id = increment()
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary, _elements
        # Get the name of the current class (ie. Trigger() or Content())
        _elements[self._name] = {
            "style": self.style.to_dict(),
            "children": dictionary
        }
        dictionary = self.previous
        
class BadgeType():
    DEFAULT = "default"
    SECONDARY = "secondary"
    OUTLINE = "outline"
    DESTRUCTIVE = "destructive"
    
class Badge():
    """
    This class is used to create a badge element. It basically gives you a
    container with a background color. You can use the `type` parameter to specify 
    the type of badge you want to create. The default type is `default`.
    ```python
    with Badge(type=BadgeType.SECONDARY):
        Text("Hello World", styles.Description())
    ```
    """
    
    def __init__(self, type: str = BadgeType.DEFAULT, style: Style = Style()):
        self.id = increment()
        self.type = type
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "badge": {
                "id": self.id,
                "type": self.type,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Alert():
    """
    Creates an alert element. This is basically just elements with a large
    background around it. You can customize the background color
    with the Style class.
    ```python
    with Alert(styles.FlexVertical()):
        Text("Hello World", styles.Description())
    ```
    """
    
    def __init__(self, style: Style = Style()):
        self.id = increment()
        self.style = style
    
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "alert": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class ButtonType():
    DEFAULT = "default"
    SECONDARY = "secondary"
    DESTRUCTIVE = "destructive"
    OUTLINE = "outline"
    GHOST = "ghost"
    LINK = "link"

class Button():
    """
    Creates a button element. You can use this to create any types of button.
    Please keep in mind that the callback can only be a function. If `name` is
    specified then the first parameter of the callback will be the name given
    to the button. Otherwise the function will be called with no parameters.
    
    Depending on the context it should also be available in every case the UI
    is loaded. You can't call a plugin function when that plugin is closed.
    
    ```python
    def callback():
        print("Hello World")
        
    with Button(type=ButtonType.OUTLINE, action=callback, style=styles.FlexHorizontal()):
        Icon(Icons.CHECK)
        Text("Accept")
    ```
    """
    
    def __init__(
        self,
        action: Callable | None,
        name: str = "",
        type: Literal["default", "secondary", "destructive", "outline", "ghost", "link"] = ButtonType.DEFAULT,
        style: Style = Style(),
        enabled: bool = True
    ):
        self.id = increment()
        self.action = action
        self.type = type
        self.name = name
        self.style = style
        self.enabled = enabled
    
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "button": {
                "id": self.id,
                "type": self.type,
                "name": self.name,
                "action": get_fully_qualified_name(self.action) if self.action else None,
                "style": self.style.to_dict(),
                "enabled": self.enabled,
                "children": dictionary
            }
        })
        dictionary = self.previous
    
class InputType():    
    STRING = "string"
    NUMBER = "number"
    PASSWORD = "password"
    FILE = "file"
    """
    File will create a file input. It will open the system file picker
    and return the file path. 
    """
    
INPUT_PLACEHOLDERS = {
    InputType.STRING: "Hello World",
    InputType.NUMBER: "0",
    InputType.PASSWORD: "●●●●●",
    InputType.FILE: "No file chosen"
}

class Input():
    """
    Will create an input element. You can explicitly specify the type of
    the input for type checking on the UI side. You can use the `changed`
    parameter to specify a callback function that will be called when
    the input changes. The first parameter of the callback function
    will be the changed value of the input.
    ```python
    current_value = "Value"
    def callback(value: str):
        global current_value
        current_value = value
        print(value) 
        
    Input(
        default=current_value,
        changed=callback,
        type=STRING
    )
    ```
    """
    def __init__(
        self,
        default,
        changed: Callable | None = None,
        type: Literal["string", "number", "password"] = InputType.STRING,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        if not default:
            default = INPUT_PLACEHOLDERS[type]
            
        self.default = default
        self.changed = changed
        self.type = type
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "input": {
                "id": self.id,
                "default": default,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "type": type,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })
        
class TextArea():
    """
    A large text input. You can use the `changed` parameter to specify
    a callback function that will be called when the input changes. The
    first parameter of the callback function will be the changed value
    of the input.
    ```python
    current_value = "Value"
    def callback(value: str):
        global current_value
        current_value = value
        print(value)
        
    TextArea(placeholder="Type something", changed=callback)
    ```
    """
    
    def __init__(
        self,
        placeholder: str = "",
        changed: Callable | None = None,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.placeholder = placeholder
        self.changed = changed
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "textarea": {
                "id": self.id,
                "placeholder": placeholder,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })
        
class Switch():
    """
    Creat a switch element. You can use the `changed` parameter to specify
    a callback function that will be called when the switch changes. The
    first parameter of the callback function will be the changed value
    of the switch.
    ```python
    current_value = False
    def callback(value: bool):
        global current_value
        current_value = value
        print(value)
    
    with Container(style=styles.FlexHorizontal()):
        Switch(
            default=current_value,
            changed=callback,
        )
        Text("Toggle something", style=styles.PlainText())
    ```
    """
    
    def __init__(
        self,
        default: bool = False,
        changed: Callable | None = None,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.default = default
        self.changed = changed
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "switch": {
                "id": self.id,
                "default": default,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })
        
class Checkbox():
    """
    Create a checkbox element. You can use the `changed` parameter to specify
    a callback function that will be called when the checkbox changes. The
    first parameter of the callback function will be the changed value
    of the checkbox.
    ```python
    current_value = False
    def callback(value: bool):
        global current_value
        current_value = value
        print(value)
    
    with Container(style=styles.FlexHorizontal()):
        CheckBox(
            default=current_value,
            changed=callback,
        )
        Text("Toggle something", style=styles.PlainText())
    ```
    """
    
    def __init__(
        self,
        default: bool = False,
        changed: Callable | None = None,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.default = default
        self.changed = changed
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "checkbox": {
                "id": self.id,
                "default": default,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })
        
class Slider():
    """
    Create a slider element. You can use the `changed` parameter to specify
    a callback function that will be called when the slider changes. The
    first parameter of the callback function will be the changed value
    of the slider.
    ```python
    current_value = 50
    def callback(value: float):
        global current_value
        current_value = value
        print(value)
    
    with Container(style=styles.FlexVertical()):
        Text("Slider")
        Slider(
            default=current_value,
            changed=callback,
            min=0,
            max=100,
            step=1
        )
    ```
    """
    
    def __init__(
        self,
        default: float = 0,
        changed: Callable | None = None,
        min: float = 0,
        max: float = 100,
        step: float = 1,
        style: Style = Style(),
        suffix: str = "",
        disabled: bool = False
    ):
        self.id = increment()
        
        self.default = default
        self.changed = changed
        self.min = min
        self.max = max
        self.step = step
        self.style = style
        self.suffix = suffix
        self.disabled = disabled
        
        dictionary.append({
            "slider": {
                "id": self.id,
                "default": default,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "min": min,
                "max": max,
                "step": step,
                "style": style.to_dict(),
                "suffix": suffix,
                "disabled": disabled
            }
        })
    
class ComboboxSearch():
    """
    This class defines how the search box of the combobox should look like.
    ```python
    Combobox(
        search=ComboboxSearch(
            placeholder="Search something",
            empty="Something not found",
        )
    )
    ```
    """
    def __init__(
        self,
        placeholder: str = "Search...",
        empty: str = "Nothing found.",
        style: Style = Style()
    ):
        self.id = increment()
        
        self.placeholder = placeholder
        self.empty = empty
        self.style = style
        
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "placeholder": self.placeholder,
            "empty": self.empty,
            "style": self.style.to_dict()
        }
        
class Combobox():
    """
    A combobox that allows you to select from a list of options. You can
    use the `changed` parameter to specify a callback function that will
    be called when the combobox changes. The first parameter of the callback
    function will be the changed value of the combobox. If you want to select
    multiple then set the `multiple` parameter to True. In this case the callback
    will be an array of strings, even if just one is selected.
    ```python
    current_value = "Option 1"
    def callback(value: str):
        global current_value
        current_value = value
        print(value)
        
    Combobox(
        options=["Option 1", "Option 2", "Option 3"],
        default=current_value,
        changed=callback,
        search=ComboboxSearch() # Search with default placholders
    )
    ```
    """
    
    def __init__(
        self,
        options: list[str],
        default: str = "",
        changed: Callable | None = None,
        search: ComboboxSearch | None = None,
        side: str = Side.BOTTOM,
        multiple: bool = False,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.options = options
        self.default = default
        self.changed = changed
        self.search = search.to_dict() if search else None
        self.side = side
        self.multiple = multiple
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "combobox": {
                "id": self.id,
                "options": options,
                "default": default,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "search": self.search,
                "side": side,
                "multiple": multiple,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })
        
class Tabs():
    """
    Create a tab container, this container will hold all the `Tab` trigger 
    elements. By styling this container you style the top bar with the list of
    tabs. You can use the `changed` parameter to specify a callback function
    when the current tab is changed.
    ```python
    with Tabs():
        with Tab("Tab 1"):
            ...
        with Tab("Tab 2"):
            ...
    ```
    """
    
    def __init__(self, style: Style = Style(), changed: Callable | None = None):
        self.id = increment()
        self.style = style
        self.changed = changed
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "tabs": {
                "id": self.id,
                "style": self.style.to_dict(),
                "changed": get_fully_qualified_name(self.changed) if self.changed else None,
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Tab():
    """
    This class will create a tab element. These elements can only be placed
    inside the `Tabs` container. There are two styles for these tabs. The 
    `container_style` and `trigger_style`. Container style will style the container
    that the tab's children are in. And the trigger will style the button on the
    tabs bar that will open the tab.
    ```python
    with Tabs():
        with Tab("Tab 1", container_style=styles.FlexHorizontal()):
            Text("Hello World")
            Text("<- Is what I would say")
        with Tab("Tab 2"):
            Text("Hello World 2")
    ```
    """
    
    def __init__(
        self,
        name: str,
        container_style: Style = Style(),
        trigger_style: Style = Style()
    ):
        self.id = increment()
        
        self.name = name
        self.container_style = container_style
        self.trigger_style = trigger_style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "tab": {
                "id": self.id,
                "name": self.name,
                "container_style": self.container_style.to_dict(),
                "trigger_style": self.trigger_style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class RadioGroup():
    """
    A radio group is a group of radio buttons. Basically it's like a 
    combobox but with all the options visible. You can use the `changed`
    parameter to specify a callback function that will be called when
    the radio group changes. The first parameter of the callback function
    will be the id of the selected radio button.
    ```python
    current_value = "option_1"
    def callback(value: str):
        global current_value
        current_value = value
        print(value)
        
    with RadioGroup(changed=callback, default=current_value):
        with RadioItem("option_1"):
            Text("Option 1")
        with RadioItem("option_2"):
            Text("Option 2")
    ```
    """
    
    def __init__(
        self,
        changed: Callable | None = None,
        default: str = "",
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.changed = changed
        self.default = default
        self.style = style
        self.disabled = disabled
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "radio_group": {
                "id": self.id,
                "changed": get_fully_qualified_name(self.changed) if self.changed else None,
                "default": self.default,
                "style": self.style.to_dict(),
                "disabled": self.disabled,
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class RadioItem():
    """
    A radio item is a single radio button. This button can only be placed
    inside the `RadioGroup` container. You can use the `id` parameter to
    specify the id of the radio button. This id will be passed to the 
    callback function of the `RadioGroup` when the radio button is selected.
    ```python
    with RadioItem("option_1"):
        Text("Option 1")
    ```
    """
    
    def __init__(self, id: str, style: Style = Style()):
        self.id = increment()
        
        self.name = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "radio_item": {
                "id": self.id,
                "name": self.name,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Tooltip():
    """
    Create a tooltip element. This element will show a tooltip when hovered
    over. Styles will be inputted to the relevant elements.
    ```python
    with Tooltip() as t:
        with t.trigger:
            Text("Hover me")
        with t.content as content: # if you want custom styling
            content.style = styles.Style(...)
            Text("Hello World")
            Text("This is a tooltip")
    ```
    """
    
    def __init__(self, side: Literal["bottom", "top", "left", "right"] = Side.TOP):
        self.id = increment()
        self.side = side
        
    def __enter__(self):
        global dictionary, _elements
        self.trigger = _SubElement()
        self.trigger._name = "trigger"
        self.content = _SubElement()
        self.content._name = "content"
        self.previous = dictionary
        dictionary = []
        _elements = {}
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary, _elements
        self.previous.append({
            "tooltip": {
                "id": self.id,
                "side": self.side,
                "trigger": _elements["trigger"],
                "content": _elements["content"],
            }
        })
        _elements = {}
        dictionary = self.previous
        
class Progress():
    """
    A simple progress bar. Nothing much to it. Just be careful to not
    update at like thousands of times a second, the UI will be sent to 
    the frontend for each of those updates.
    ```python
    Progress(min=0, value=50, max=100)
    """
    
    def __init__(
        self,
        value: int = 0,
        max: int = 100,
        style: Style = Style()
    ):
        self.id = increment()
        
        self.value = value
        self.max = max
        self.style = style
        
        dictionary.append({
            "progress": {
                "id": self.id,
                "value": self.value,
                "max": self.max,
                "style": self.style.to_dict()
            }
        })

class Table():
    """
    An automatically generated table. You can input a list of dictionaries
    and the table will be generated based on that. The keys of the dictionary
    will be the column names and the values will be the data.
    ```python
    data = [
        {
            "name": "John",
            "age": 25,
            "city": "New York"
        },
        {
            "name": "Jane",
            "age": 30,
            "city": "Los Angeles"
        }
        ...
    ]
    
    Table(
        data=data,
        columns={ # Optional to specify custom names
            "name": "Name",
            "age": "Age",
            "city": "City"
        }
    )
    ```
    """
    
    def __init__(
        self,
        data: list[dict],
        columns: dict[str, str] | None = None,
        style: Style = Style()
    ):
        self.id = increment()
        
        self.data = data
        self.columns = columns
        self.style = style
        
        dictionary.append({
            "table": {
                "id": self.id,
                "data": data,
                "columns": columns,
                "style": style.to_dict()
            }
        })
        
class PopoverTrigger():
    """
    A trigger element for a popover. This element will show the popover
    when clicked.
    ```python
    with PopoverTrigger(id="popover_1"):
        Text("Click me")
    ```
    """
    
    def __init__(self, id: str, style: Style = Style()):
        self.id = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "popover_trigger": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Popover():
    """
    A popover element. This will show a card with the content when
    the trigger is clicked.
    ```python
    with PopoverTrigger(id="popover_1"):
        Text("Click me")
    
    with Popover(id="popover_1"):
        Text("Hello World")
        Text("This is a popover")
    ```
    """
    def __init__(self, id: str, style: Style = Style()):
        self.id = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "popover": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class DialogTrigger():
    """
    A trigger element for a dialog. This element will show the dialog
    when clicked.
    ```python
    with DialogTrigger(id="dialog_1"):
        Text("Click me")
    ```
    """
    
    def __init__(self, id: str, style: Style = Style()):
        self.id = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "dialog_trigger": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Dialog():
    """
    A dialog element. This will show a card with the content when
    the trigger is clicked.
    ```python
    with DialogTrigger(id="dialog_1"):
        Text("Click me")
    
    with Dialog(id="dialog_1"):
        Text("Hello World")
        Text("This is a dialog")
    ```
    """
    
    def __init__(self, id: str, style: Style = Style()):
        self.id = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "dialog": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class ContextMenuTrigger():
    """
    A trigger element for a context menu. This element will show the
    context menu when right clicked. This element acts as a Container,
    so if you want your entire UI to trigger a context menu, then this
    should be the root element. (note that you have to define the context
    menu before this element though)
    ```python
    with ContextMenuTrigger(id="context_menu_1"):
        Text("Right click me")
    ```
    """
    
    def __init__(self, id: str, style: Style = Style()):
        self.id = id
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "context_menu_trigger": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class ContextMenuItem():
    """
    This is a singular item in the context menu. It is essentially a button
    and acts like one. You can use the `action` parameter to specify a callback
    function that will be called when the item is clicked. If `name` is specified
    then the first parameter of `action` will be the name of the item.
    ```python
    def callback(name: str):
        print(name)
        
    with ContextMenu():
        with ContextMenuItem(name="item_1", action=callback):
            Text("Item 1")
        with ContextMenuItem(name="item_2", action=callback):
            Text("Item 2")
    ```  
    """
    
    def __init__(
        self,
        name: str,
        action: Callable | None = None,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        self.name = name
        self.action = action
        self.style = style
        self.disabled = disabled
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "context_menu_item": {
                "id": self.id,
                "name": self.name,
                "action": get_fully_qualified_name(self.action) if self.action else None,
                "style": self.style.to_dict(),
                "disabled": self.disabled,
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class ContextMenuSubMenu():
    """
    This will create a sub menu inside the context menu when hovered over.
    ```python
    with ContextMenuSubMenu("More Options"):
        with ContextMenuItem(name="item_1", action=callback):
            Text("Item 1")
        with ContextMenuItem(name="item_2", action=callback):
            Text("Item 2")
    ```
    """
    
    def __init__(
        self,
        title: str,
        style: Style = Style()
    ):
        self.id = increment()
        
        self.title = title
        self.style = style
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "context_menu_submenu": {
                "id": self.id,
                "title": self.title,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Spinner():
    """
    A spinner element that will cause anything inside it to
    spin. This is useful for loading state.
    ```python
    with Spinner():
        Icon("loader-circle")
    ```
    """
    def __init__(self):
        self.id = increment()
        
    def __enter__(self):
        global dictionary
        self.previous = dictionary
        dictionary = []
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global dictionary
        self.previous.append({
            "spinner": {
                "id": self.id,
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class Image():
    """
    An image element. You can use the style to specify the size and
    other properties. By default the image will fill the container it is in.
    
    Please note that using URLs is the preferred way, as sending file information
    to the frontend will take some time, especially for high quality images.
    ```python
    with Container():
        Image(file="path/to/image.png") # only .png supported
        # or as a base64 encoded string (this is what's sent when using file too)
        Image(base64="iVBORw0KGgoAAAANSUhEUgAA...")
        # or a URL
        Image(url="https://example.com/image.png")
    ```
    """
    def __init__(
        self,
        file: str | None = None,
        base64: str | None = None,
        url: str | None = None,
        style: Style = Style(),
        alt: str = ""
    ):
        self.id = increment()
        
        if file and base64:
            raise ValueError("You can only specify one of file or base64.")
        if not (file or base64 or url):
            raise ValueError("You must specify either file, base64 or url.")
        if file and url:
            raise ValueError("You cannot specify both file and url.")
        if base64 and url:
            raise ValueError("You cannot specify both base64 and url.")
        
        self.file = file
        self.url = url
        self.style = style
        self.alt = alt
        self.base64 = base64
        
        if file:
            array = np.fromfile(file, dtype=np.uint8)
            base64 = b64.b64encode(array).decode('utf-8')
            
        dictionary.append({
            "image": {
                "id": self.id,
                "base64": base64,
                "url": url,
                "style": style.to_dict(),
                "alt": alt
            }
        })
        
class GraphType():
    BAR = "bar"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
        
class GraphAxisOptions():
    data_key: str
    hide: bool = True
    color: str | None = None
    max: int | None = None
    min: int | None = None
    tick_count: int | None = None
        
    def __init__(self, data_key: str, hide: bool = True, color: str | None = None, max: int | None = None, min: int | None = None, tick_count: int | None = None):
        self.data_key = data_key
        self.hide = hide
        self.color = color
        self.max = max
        self.min = min
        self.tick_count = tick_count
        
    def to_dict(self) -> dict:
        return {
            "data_key": self.data_key,
            "hide": self.hide,
            "color": self.color,
            "max": self.max,
            "min": self.min,
            "tick_count": self.tick_count
        }
        
class Graph():
    """
    A graph element that can be used to display data in a visual
    way. The input data is a list of dictionaries, where each key
    is the data label and the value is the data point.
    
    The config parameter is a dictionary that defines how each key
    is represented in the graph.
    
    Please see the shadcn documentation for more information on
    the correct formatting: https://ui.shadcn.com/docs/components/chart
    
    ```python
    # Example data
    data = [                              # You can set a custom fill color
        { "browser": "chrome", "visitors": 275, "fill": "var(--color-chrome)" },
        { "browser": "safari", "visitors": 200, "fill": "var(--color-safari)" },
    ]
    
    # Example config
    config = {
        "visitors": {
            "label": "Total Visitors",
        },
        "chrome": {
            "label": "Chrome",
            "icon": "chrome",  # If you want icons it has to be a valid icon name like the Icon component.
            "color": "hsl(var(--chart-1))",
        },
        "safari": {
            "label": "Safari",
            "icon": "compass",
            "color": "hsl(var(--chart-2))",
        },
    }
    
    Graph(
        data=data,
        config=config,
        x=GraphAxisOptions("browser"),   # The key that will be used for the x-axis
        y=GraphAxisOptions("visitors"),  # The key that will be used for the y-axis
        style=Style(),  # You can specify a style to change the container properties
    )
    ```
    """
    
    def __init__(
        self,
        data: list[dict],
        config: dict,
        x: GraphAxisOptions,
        y: GraphAxisOptions | list[GraphAxisOptions],
        type: GraphType = GraphType.AREA,
        style: Style = Style(),
    ):
        self.id = increment()
        
        self.data = data
        self.config = config
        self.style = style
        self.x = x
        self.y = y
        
        dictionary.append({
            "graph": {
                "id": self.id,
                "data": self.data,
                "config": self.config,
                "x": self.x.to_dict(),
                "y": [axis.to_dict() for axis in self.y] if isinstance(self.y, list) else self.y.to_dict(),
                "type": type,
                "style": self.style.to_dict()
            }
        })

class AdSense():
    """
    Embed an adsense ad. Please provide at least the `client` and `slot` 
    parameters, you can customize the ad further with the `style` parameter.
    
    ```python
    AdSense(
        client="ca-pub-XXXXXXXXXXXXXXXX",
        slot="XXXXXXXXXX",
        style=Style()
    )
    ```
    """
    def __init__(
        self,
        client: str,
        slot: str,
        style: Style = Style(),
    ):
        self.id = increment()
        
        if not client or not slot:
            raise ValueError("You must specify both client and slot.")
        
        self.client = client
        self.slot = slot
        self.style = style
        
        dictionary.append({
            "adsense": {
                "id": self.id,
                "client": self.client,
                "slot": self.slot,
                "style": self.style.to_dict()
            }
        })

class Youtube():
    """
    A Youtube video embed. Provide the youtube video ID and it will embed the video.
    You can use the `style` parameter to specify the size and other properties.
    
    ```python
    Youtube("dQw4w9WgXcQ", style=Style())
    ```
    """
    def __init__(
        self,
        video_id: str,
        style: Style = Style(),
    ):
        self.id = increment()
        
        if not video_id:
            raise ValueError("You must specify a video ID.")
        
        self.video_id = video_id
        self.style = style
        
        dictionary.append({
            "youtube": {
                "id": self.id,
                "video_id": self.video_id,
                "style": self.style.to_dict()
            }
        })

def RenderUI():
    global dictionary, current_id
    current_id = 0
    tmp = dictionary
    dictionary = []
    return tmp

# MARK: Helper functions
class ButtonWithTitleDescription():
    """
    This helper function will let you create a button with a title and
    a description. 
    ```python
    def action():
        print("Hello World")
    
    ButtonWithTitleDescription(
        action=action,
        title="Do Something",
        description="This will do something",
        text="Click me", # The text inside the button
    )
    ```
    """
    
    def __init__(
        self,
        action: Callable,
        title: str,
        description: str,
        text: str = "Click me",
        style: Style = Style()
    ):
        global dictionary
        
        self.id = increment()
        
        self.action = action
        self.title = title
        self.description = description
        self.text = text
        self.style = style
        
        self.previous = dictionary
        dictionary = []
        
        with Container(style=styles.FlexHorizontal() + styles.Classname("border items-center border-muted rounded-md p-4 w-full justify-between bg-input/10") + styles.Gap("10px") + self.style):
            with Container(style=styles.FlexVertical() + styles.Gap("2px")):
                Text(title, styles.Classname("font-semibold"))
                Text(description, styles.Description() + styles.Classname("text-xs"))
            
            with Button(action, style=styles.MinWidth("75px")):
                Text(text)
                
        self.previous += dictionary
        dictionary = self.previous
        
class SliderWithTitleDescription():
    """
    This helper function will let you create a slider with a title and
    a description. 
    ```python
    def action(value: float):
        print(value)
    
    SliderWithTitleDescription(
        min=500,
        default=720
        max=2560,
        step=10,
        suffix="px",
        changed=action,
    )
    ```
    """
    
    def __init__(
        self,
        min: float = 0,
        default: float = 0,
        max: float = 100,
        step: float = 1,
        suffix: str = "",
        changed: Callable | None = None,
        title: str = "",
        description: str = "",
        style: Style = Style()
    ):
        global dictionary
        
        self.id = increment()
        
        self.min = min
        self.default = default
        self.max = max
        self.step = step
        self.suffix = suffix
        self.changed = changed
        self.title = title
        self.description = description
        self.style = style
        
        self.previous = dictionary
        dictionary = []
        
        with Container(style=styles.FlexVertical() + styles.Classname("border rounded-md p-4 w-full bg-input/10") + styles.Gap("10px") + self.style):
            with Container(style=styles.FlexHorizontal() + styles.Classname("justify-between")):
                Text(title, styles.Classname("font-semibold"))
                Text(f"{default}{suffix}", styles.Classname("text-muted-foreground"))
            Slider(
                min=min,
                default=default,
                max=max,
                step=step,
                suffix=suffix,
                changed=changed
            )
            Text(description, styles.Description() + styles.Classname("text-xs"))
                
        self.previous += dictionary
        dictionary = self.previous
        
class ComboboxWithTitleDescription():
    """
    This helper function will let you create a combobox with a title and
    a description. 
    ```python
    def action(value: str):
        print(value)
    
    ComboboxWithTitleDescription(
        options=["Option 1", "Option 2", "Option 3"],
        default="Option 1",
        changed=action,
        title="Do Something",
        description="This will do something",
    )
    ```
    """
    
    def __init__(
        self,
        options: list[str],
        default: str = "",
        changed: Callable | None = None,
        title: str = "",
        description: str = "",
        style: Style = Style(),
        search: ComboboxSearch | None = None,
        side: str = Side.BOTTOM,
        multiple: bool = False
    ):
        global dictionary
        
        self.id = increment()
        
        self.options = options
        self.default = default
        self.changed = changed
        self.title = title
        self.description = description
        self.style = style
        self.search = search
        self.multiple = multiple
        
        self.previous = dictionary
        dictionary = []
        
        with Container(style=styles.FlexHorizontal() + styles.Classname("border justify-between rounded-md p-4 w-full bg-input/10") + styles.Gap("10px") + self.style):
            with Container(style=styles.FlexVertical()):
                Text(title, styles.Classname("font-semibold"))
                Text(description, styles.Classname("text-xs") + styles.Description())
            Combobox(
                options=options,
                default=default,
                changed=changed,
                side=side,
                search=search,
                multiple=multiple
            )
                
        self.previous += dictionary
        dictionary = self.previous
       
class CheckboxWithTitleDescription():
    """
    A toggle with a title and description. This is basically a checkbox
    with a title and description. You can use the `changed` parameter to
    specify a callback function that will be called when the toggle changes.
    The first parameter of the callback function will be the changed value
    of the toggle.
    ```python
    current_value = False
    def callback(value: bool):
        global current_value
        current_value = value
        print(value)
        
    ToggleWithTitleDescription(
        default=current_value,
        changed=callback,
        title="Do Something",
        description="This will do something",
    )
    ```
    """
    
    def __init__(
        self,
        default: bool = False,
        changed: Callable | None = None,
        title: str = "",
        description: str = "",
        style: Style = Style(),
        disabled: bool = False
    ):
        global dictionary
        
        self.id = increment()
        
        self.default = default
        self.changed = changed
        self.title = title
        self.description = description
        self.style = style
        self.disabled = disabled
        
        self.previous = dictionary
        dictionary = []
        
        with Container(
            styles.FlexHorizontal() + styles.Gap("16px") + styles.Padding("14px 16px 16px 16px") + styles.Classname("border rounded-md w-full " + ("bg-input/30" if default else "bg-input/10")),
            pressed=self.changed, # This allows for the entire container to act as the toggle
        ):
            Checkbox(
                default=default, # type: ignore
                changed=self.changed,
                style=styles.Margin("4px 0px 0px 0px")
            )
            with Container(styles.FlexVertical() + styles.Gap("6px")):
                Text(title, styles.Classname("font-semibold"))
                Text(description, styles.Classname("text-xs text-muted-foreground"))
                
        self.previous += dictionary
        dictionary = self.previous
        
class InputWithTitleDescription():
    """
    An input with a title and description. This is basically a text input
    with a title and description. You can use the `changed` parameter to
    specify a callback function that will be called when the input changes.
    The first parameter of the callback function will be the changed value
    of the input.
    ```python
    current_value = "Value"
    def callback(value: str):
        global current_value
        current_value = value
        print(value)
        
    InputWithTitleDescription(
        default=current_value,
        changed=callback,
        title="Change Something",
        description="This will change something",
    )
    ```
    """
    
    def __init__(
        self,
        default,
        changed: Callable | None = None,
        title: str = "",
        description: str = "",
        type: Literal["string", "number", "password"] = InputType.STRING,
        style: Style = Style(),
        disabled: bool = False
    ):
        global dictionary
        
        self.id = increment()
        
        self.default = default
        self.changed = changed
        self.title = title
        self.description = description
        self.type = type
        self.style = style
        self.disabled = disabled
        
        self.previous = dictionary
        dictionary = []
        
        with Container(style=styles.FlexHorizontal() + styles.Gap("16px") + styles.Padding("14px 16px 16px 16px") + styles.Classname("border justify-between items-center rounded-md w-full bg-input/10") + self.style):
            with Container(style=styles.FlexVertical() + styles.Gap("6px")):
                Text(title, styles.Classname("font-semibold"))
                Text(description, styles.Classname("text-xs") + styles.Description())
            Input(
                default=default,
                changed=changed,
                type=type,
                style=styles.MaxWidth("200px"),
            )
                
        self.previous += dictionary
        dictionary = self.previous
        
class TitleAndDescription():
    """
    A simple standardized title and description
    for settings pages.
    ```python
    TitleAndDescription(
        title="Hello World",
        description="This is a description"
    )
    ```
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        style: Style = Style()
    ):
        global dictionary
        
        self.id = increment()
        
        self.title = title
        self.description = description
        self.style = style
        
        self.previous = dictionary
        dictionary = []
        
        flex = styles.FlexVertical()
        flex.gap = "12px"
        with Container(flex + self.style):
            Text(title, styles.Title())
            Text(description, styles.Description())
                
        self.previous += dictionary
        dictionary = self.previous