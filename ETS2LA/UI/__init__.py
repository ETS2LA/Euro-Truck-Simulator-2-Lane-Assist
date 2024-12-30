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
    **Selector** - A selector component.
    **TabView** - Container to hold tabs, check example below.
    **Tab** - A tab component.
    **Group** - A group component.
    **Separator** - A separator component.
    **Space** - A space component.
    **RefreshRate** - Set the refresh rate of the plugin.
    **ProgressBar** - A progress bar component. NOTE: Only works with dynamic pages.
    **EnabledLock** - A lock to disable the page (after the lock) if the plugin is disabled.
    **Form** - A form component, used only as a wrapper for dialogs.
    **Padding** - A padding component.
    **Geist** - Import the Geist font.
    **Markdown** - Render markdown text.
    **Tooltip** - Render a tooltip on hover.
    
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
from ETS2LA.UI.components import Title, Description, Label, Markdown, Button, Separator, Space, Input, Switch, Toggle, Slider, Selector, TabView, Tab, Group, Tooltip, Padding, Geist, Form, RefreshRate, ProgressBar, EnabledLock, ButtonGroup, RenderUI
from ETS2LA.UI.presets import TITLE_CLASSNAME, DESCRIPTION_CLASSNAME
from ETS2LA.UI.settings import ETS2LASettingsMenu
from ETS2LA.UI.dialog import ETS2LADialog
from ETS2LA.UI.page import ETS2LAPage
from ETS2LA.UI.utils import SendPopup