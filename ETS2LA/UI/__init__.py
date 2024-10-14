"""
Import all ETS2LA UI components here.

Classes:
    **ETS2LASettingsMenu** - Base class for all settings pages.
    
Components:
    **Title** - A title component.
    **Description** - A description component.
    **Button** - A button component.
    **Input** - An input component.
    **TabView** - A tab view, contains multiple tabs. Check below for example on usage.
    **Tab** - A tab component, contains multiple components. Check below for example on usage.
    **Group** - A group component, contains multiple components. Check below for example on usage.
    
Example:
```python
from ETS2LA.UI import *
from ETS2LA.Plugin import *

class Menu(ETS2LASettingsMenu):
    dynamic = False
    def render(self):
        Title("Title")
        Description("Description")
        
        with TabView():
            with Tab(name="Tab 1"):
                with Group():
                    Input("Input", "input", "string", default="default", description="This is an input")
                    Button("Button", Plugin.function)
            with Tab(name="Tab 2"):
                Description("This is tab 2")
        
        return RenderUI()
        
class Plugin(ETS2LAPlugin):
    settings_menu = Menu()
    def function(self):
        print("Button clicked!")
```
"""
from ETS2LA.UI.settings import ETS2LASettingsMenu
from ETS2LA.UI.components import Title, Description, Button, TabView, Tab, Group, Input
from ETS2LA.UI.components import RenderUI