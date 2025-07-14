from ETS2LA.UI import *

from ETS2LA.Handlers.controls import get_event_information_dictionary, edit_event, unbind_event, event_information_update
from ETS2LA.Handlers.plugins import match_plugin_by_id
from ETS2LA.Utils.translator import _

class Control:
    alias: str = ""
    guid: str = ""
    key: str = ""
    type: str = ""
    name: str = ""
    description: str = ""
    device: str = ""
    plugin: str = ""
    
    def from_dict(self, dict):
        self.alias = dict["alias"]
        self.guid = dict["guid"]
        self.key = dict["key"]
        self.type = dict["type"]
        self.name = dict["name"]
        self.description = dict["description"]
        self.device = dict["device"]
        self.plugin = dict.get("plugin", "")

class Page(ETS2LAPage):
    url = "/settings/controls"    
    
    target_plugin = ""
    target_control = ""
    
    def handle_sort_change(self, value: str):
        if value == _("Show all plugins"):
            self.target_plugin = ""
        else:
            self.target_plugin = value

    def handle_search(self, value: str):
        if value == "":
            self.target_control = ""
        else:
            self.target_control = value
            
    def handle_change(self, alias: str):
        SendPopup(_("Please press the key / button you want to bind to this event."), type="info")
        edit_event(alias)
        
    def handle_unbind(self, alias: str):
        unbind_event(alias)
        SendPopup(_("Event unbound."), type="success")

    def render(self):
        event_information = get_event_information_dictionary()
        
        controls: list[Control] = []
        plugin_names = []
        for alias, event in event_information.items():
            event = Control()
            dict = event_information[alias]
            dict["alias"] = alias
            event.from_dict(dict)
            controls.append(event)
            
            plugin = event.plugin
            if plugin not in plugin_names:
                plugin_names.append(plugin)
        
        with Container(styles.FlexHorizontal() + styles.Classname("justify-between")):
            with Container(styles.FlexVertical() + styles.Gap("12px")):
                Text(_("Controls"), styles.Title())
                Text(_("You can change plugins' control events here."), styles.Description())

            Combobox(
                [_("Show all plugins")] + plugin_names,
                default=_("Show all plugins"),
                style=styles.MinWidth("250px"),
                search=ComboboxSearch(),
                changed=self.handle_sort_change
            )
            
        Input(
            default=_("Search Controls or Plugins"),
            changed=self.handle_search,
        )
        
        valid_controls = []
        for control in controls:
            if self.target_plugin and control.plugin != self.target_plugin:
                continue
            
            if self.target_control != "":
                has_in_name = self.target_control and self.target_control.lower() in control.name.lower()
                has_in_plugin = self.target_control and self.target_control.lower() in control.plugin.lower()
                if not has_in_name and not has_in_plugin:
                    continue
            
            valid_controls.append(control)
            
        if len(valid_controls) == 0:
            with Alert(style=styles.Padding("14px")):
                with Container(styles.FlexHorizontal() + styles.Gap("12px") + styles.Classname("items-start")):
                    style = styles.Style()
                    style.margin_top = "2px"
                    style.width = "1rem"
                    style.height = "1rem"
                    style.color = "var(--muted-foreground)"
                    Icon("triangle-alert", style)
                    Text(_("No controls found, try again with different filters."), styles.Classname("text-muted-foreground"))

        for control in valid_controls:
            pointer = styles.Style()
            pointer.cursor = "pointer"
            
            left_style = styles.Style()
            left_style.border_radius = "8px 0px 0px 8px"
            left_style.border_right = "0px"
            
            right_style = styles.Style()
            right_style.border_radius = "0px 8px 8px 0px"
            with Container(styles.FlexHorizontal() + styles.Gap("0px")):
                
                with Container(styles.FlexVertical() + left_style + styles.Gap("8px") + styles.Classname("w-full rounded-md border p-4 bg-input/10")):
                    with Container(styles.FlexHorizontal() + styles.Gap("24px") + styles.Classname("items-center")):
                        with Container(styles.FlexVertical() + styles.Gap("4px") + styles.Classname("min-w-max")):
                            Text(control.name, styles.Classname("font-semibold"))
                            try:
                                plugin = match_plugin_by_id(control.plugin)
                                if plugin:
                                    Text(plugin.description.name, styles.Description() + styles.Classname("text-xs"))
                                else:
                                    Text(control.plugin, styles.Description() + styles.Classname("text-xs"))
                            except:
                                Text(control.plugin, styles.Description() + styles.Classname("text-xs"))

                        Separator(direction="vertical", style=styles.Width("1px") + styles.Height("100%"))
                        
                        with Container(styles.FlexVertical() + styles.Gap("4px")):
                            Text(control.description, styles.Description())
                            if control.device == "":
                                Text(_("This event has not been bound to a device yet."))
                            elif control.device == "Keyboard":
                                # TRANSLATORS: This text will be followed by the key name, e.g. "Keyboard: A"
                                Text(_("Keyboard: ") + control.key.capitalize().replace("_", " "))
                            else:
                                Text(control.device + ": " + control.key.capitalize().replace("_", " "))
                                
                with Container(styles.FlexVertical() + styles.Gap("4px") + right_style + styles.Classname("rounded-md border justify-center pl-2 pr-2 bg-input/10")):
                    with Button(action=self.handle_change, 
                                name=control.alias,
                                style=styles.Width("28px") + styles.Height("28px") + styles.Classname("default") + pointer):
                        Icon("Pencil")
                    
                    enabled = control.device != ""
                    with Button(action=self.handle_unbind, 
                                name=control.alias,
                                style=styles.Width("28px") + styles.Height("28px") + styles.Classname("default") + pointer, enabled=enabled):
                        Icon("Trash")