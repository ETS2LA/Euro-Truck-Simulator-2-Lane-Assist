from ETS2LA.UI.styles import Style
import ETS2LA.UI.styles as styles

from collections.abc import Callable
from typing import Literal
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
    def __init__(self, text: str, style: Style = Style()):
        self.id = increment()

        self.text = text
        self.style = style
        
        dictionary.append({
            "text": {
                "id": self.id,
                "text": text,
                "style": style.to_dict()
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
        
class Separator():
    """
    This class is used to create a separator. It is a simple horizontal line
    that can be styled with the `style` parameter.
    """
    def __init__(self, style: Style = Style()):
        self.id = increment()
        self.style = style
        
        dictionary.append({
            "separator": {
                "id": self.id,
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
            "container": {
                "id": self.id,
                "style": self.style.to_dict(),
                "children": dictionary
            }
        })
        dictionary = self.previous
        
class ButtonType():
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DESTRUCTIVE = "destructive"
    OUTLINE = "outline"
    GHOST = "ghost"

class Button():
    """
    Creates a button element. You can use this to create any types of button.
    Please keep in mind that the callback can only be a function. That function
    should not take any arguments and should be defined before the button is created.
    
    Depending on the context it should also be available in every case the UI
    is loaded. You can't call a plugin function when that plugin is closed.
    
    ```python
    def callback():
        print("Hello World")
        
    Button(
        title="Hello World",
        action=callback,
    )
    ```
    """
    
    def __init__(
        self,
        title: str,
        action: Callable,
        type: Literal["primary", "secondary", "destructive", "outline", "ghost"] = ButtonType.PRIMARY,
        style: Style = Style(),
        enabled: bool = True
    ):
        self.id = increment()
        self.title = title
        self.action = action
        self.type = type
        self.style = style
        self.enabled = enabled
        
        dictionary.append({
            "button": {
                "id": self.id,
                "title": title,
                "type": type,
                "action": get_fully_qualified_name(action),
                "style": style.to_dict(),
                "enabled": enabled
            }
        })
    
class InputType():    
    STRING = "string"
    NUMBER = "number"
    PASSWORD = "password"
    
INPUT_PLACEHOLDERS = {
    InputType.STRING: "Expecting string",
    InputType.NUMBER: "Expecting number",
    InputType.PASSWORD: "●●●●●"
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
        placeholder=current_value,
        changed=callback,
        type=STRING
    )
    ```
    """
    def __init__(
        self,
        placeholder: str = "",
        changed: Callable | None = None,
        type: Literal["string", "number", "password"] = InputType.STRING,
        style: Style = Style(),
        disabled: bool = False
    ):
        self.id = increment()
        
        if not placeholder:
            placeholder = INPUT_PLACEHOLDERS[type]
            
        self.placeholder = placeholder
        self.changed = changed
        self.type = type
        self.style = style
        self.disabled = disabled
        
        dictionary.append({
            "input": {
                "id": self.id,
                "placeholder": placeholder,
                "changed": get_fully_qualified_name(changed) if changed else None,
                "type": type,
                "style": style.to_dict(),
                "disabled": disabled
            }
        })