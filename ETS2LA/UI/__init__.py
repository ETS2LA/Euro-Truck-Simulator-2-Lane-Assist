"""
Import all ETS2LA UI components here.

Classes:
    **ETS2LASettingsMenu** - Base class for all settings pages.
    
Components:
    **Title** - A title component.
    **Label** - A label component.
    **Description** - A description component.
    **Button** - A button component.
    **Input** - An input component. This is for either *string* or *number* inputs.
    **Switch** - A switch component.
    **Toggle** - A toggle component.
    **Slider** - A slider component.
    **TabView** - Container to hold tabs, check example below.
    **Tab** - A tab component.
    **Group** - A group component.
    
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