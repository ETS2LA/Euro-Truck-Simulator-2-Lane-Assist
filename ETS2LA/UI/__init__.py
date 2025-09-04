"""Import all ETS2LA UI components here.

NOTE: This information is out of date, please check the file itself
for the most up to date information on components.

Better documentation is being actively worked on!

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
"""

from ETS2LA.UI.components import (
    Side,
    Text,
    Link,
    Markdown,
    Icon,
    SeparatorType,
    Separator,
    Space,
    Container,
    BadgeType,
    Badge,
    Alert,
    ButtonType,
    Button,
    InputType,
    Input,
    TextArea,
    Switch,
    Checkbox,
    Slider,
    ComboboxSearch,
    Combobox,
    Tabs,
    Tab,
    RadioGroup,
    RadioItem,
    Tooltip,
    Progress,
    Table,
    PopoverTrigger,
    Popover,
    DialogTrigger,
    Dialog,
    ContextMenuTrigger,
    ContextMenuItem,
    ContextMenuSubMenu,
    Spinner,
    Image,
    GraphType,
    GraphAxisOptions,
    Graph,
    AdSense,
    Youtube,
    RenderUI,
    ButtonWithTitleDescription,
    SliderWithTitleDescription,
    ComboboxWithTitleDescription,
    CheckboxWithTitleDescription,
    InputWithTitleDescription,
    TitleAndDescription,
)
from ETS2LA.UI.dialog import ETS2LADialog
from ETS2LA.UI.page import ETS2LAPage, ETS2LAPageLocation
from ETS2LA.UI.utils import SendPopup

__all__ = [
    "Side",
    "Text",
    "Link",
    "Markdown",
    "Icon",
    "SeparatorType",
    "Separator",
    "Space",
    "Container",
    "BadgeType",
    "Badge",
    "Alert",
    "ButtonType",
    "Button",
    "InputType",
    "Input",
    "TextArea",
    "Switch",
    "Checkbox",
    "Slider",
    "ComboboxSearch",
    "Combobox",
    "Tabs",
    "Tab",
    "RadioGroup",
    "RadioItem",
    "Tooltip",
    "Progress",
    "Table",
    "PopoverTrigger",
    "Popover",
    "DialogTrigger",
    "Dialog",
    "ContextMenuTrigger",
    "ContextMenuItem",
    "ContextMenuSubMenu",
    "Spinner",
    "Image",
    "GraphType",
    "GraphAxisOptions",
    "Graph",
    "AdSense",
    "Youtube",
    "RenderUI",
    "ButtonWithTitleDescription",
    "SliderWithTitleDescription",
    "ComboboxWithTitleDescription",
    "CheckboxWithTitleDescription",
    "InputWithTitleDescription",
    "TitleAndDescription",
    "ETS2LADialog",
    "ETS2LAPage",
    "ETS2LAPageLocation",
    "SendPopup",
]
