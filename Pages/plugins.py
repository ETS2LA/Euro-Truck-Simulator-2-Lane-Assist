from ETS2LA.Handlers import plugins
from ETS2LA.UI import *

from ETS2LA.Utils.translator import _
from ETS2LA.Utils import settings
import threading
import time

class BasicModeFeature():
    name: str = "Feature"
    description: str = "Description of the feature."
    plugin_ids: list[str] = "Plugin names to enable this feature."
    default: bool = True
    
    def __init__(self, name: str, description: str, plugin_ids: list[str], default: bool = True):
        self.name = name
        self.description = description
        self.plugin_ids = plugin_ids
        self.default = default


basic_mode_features = [
    BasicModeFeature(
        name=_("Steering"),
        description=_("Enable automated steering using ETS2LA. You can toggle it on and off using the 'Toggle Steering' keybind in the control settings."),
        plugin_ids=["plugins.map"]
    ),
    BasicModeFeature(
        name=_("Lateral Control"),
        description=_("Enable automated acceleration and deceleration using ETS2LA. You can toggle it on and off using the 'Toggle Speed Control' keybind in the control settings."),
        plugin_ids=["plugins.adaptivecruisecontrol"]
    ),
    BasicModeFeature(
        name=_("Visualization"),
        description=_("Enable plugins that are needed for the visualization tab to work.\n\n**This is required for the visualization tab to work.**"),
        plugin_ids=["plugins.visualizationsockets", "plugins.navigationsockets"]
    ),
    BasicModeFeature(
        name=_("HUD"),
        description=_("Enable the HUD to display information about the truck and route. Shown on top of the game screen using accurate 3D mapping."),
        plugin_ids=["plugins.ar", "plugins.hud"],
        default=False
    ),
    BasicModeFeature(
        name=_("Text To Speech"),
        description=_("Enable text-to-speech for notifications and alerts. This is mostly an accessibility feature but some people might find it useful."),
        plugin_ids=["plugins.tts"],
        default=False
    )
]


last_plugins = settings.Get("global", "running_plugins", [])


class Page(ETS2LAPage):
    url = "/plugins"
    
    # MARK: Basic mode
    feature_toggles = {
        feature.name: feature.default for feature in basic_mode_features
    }
    update_queue: list[str] = []
    running: bool = False
    first_run: bool = True
    
    def basic_mode_updater(self):
        while True:
            while self.update_queue:
                self.update_basic_mode_plugins()
                self.update_queue.pop(0)
            time.sleep(1)
    
    def update_basic_mode_plugins(self):
        if not settings.Get("global", "advanced_plugin_mode", False):
            for feature in basic_mode_features:
                if self.feature_toggles[feature.name] and self.running:
                    for id in feature.plugin_ids:
                        plugins.start_plugin(id=id)
                else:
                    for id in feature.plugin_ids:
                        plugins.stop_plugin(id=id)

    def toggle_feature(self, name: str):
        if name in self.feature_toggles:
            self.feature_toggles[name] = not self.feature_toggles[name]
        else:
            SendPopup(_("Feature '{0}' not found.").format(name), type="error")

        self.update_queue.append(name)
        return True
    
    def toggle_running(self):
        self.running = not self.running
        self.update_queue.append("running")

    def handle_advanced_mode_toggle(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("global", "advanced_plugin_mode", False)
        settings.Set("global", "advanced_plugin_mode", value)
    
    # MARK: Advanced mode
    search_term: str = ""
    tags: list[str] = ["Base"]
    authors: list[str] = []
    
    enabling: list[object] = [] # List of plugins currently being enabled
    disabling: list[object] = [] # List of plugins currently being disabled
    
    def open_event(self):
        self.search_term = ""
        self.tags = ["Base"]
        self.authors = []
    
    def handle_search(self, search_term: str):
        self.search_term = search_term.strip().lower()
    
    def handle_tags(self, tags: list[str]):
        self.tags = tags  
    
    def handle_authors(self, authors: list[str]):
        self.authors = [author.strip().lower() for author in authors if author.strip()]
    
    def clear_filters(self):
        self.search_term = ""
        self.tags = ["Base"]
        self.authors = []
        SendPopup("Filters cleared.", type="success")
        
    def enable_last_plugins(self):
        for plugin_name in last_plugins:
            if plugin_name not in self.enabling and plugin_name not in self.disabling:
                self.enabling.append(plugin_name)
                threading.Thread(
                    target=plugins.start_plugin,
                    kwargs={"id": plugin_name},
                    daemon=True
                ).start()
        
    def enable_plugin(self, plugin_name: str):
        if plugin_name in self.enabling:
            return
        
        self.enabling.append(plugin_name)
        if plugin_name in self.disabling:
            self.disabling.remove(plugin_name)
            
        threading.Thread(target=plugins.start_plugin, kwargs={"folder": plugin_name}, daemon=True).start()

    def disable_plugin(self, plugin_name: str):
        if plugin_name in self.disabling:
            return
        
        self.disabling.append(plugin_name)
        if plugin_name in self.enabling:
            self.enabling.remove(plugin_name)
        
        threading.Thread(target=plugins.stop_plugin, kwargs={"folder": plugin_name}, daemon=True).start()

    def render_plugin(self, plugin):
        if plugin.folder in self.enabling and plugin.running:
            self.enabling.remove(plugin.folder)
        if plugin.folder in self.disabling and not plugin.running:
            self.disabling.remove(plugin.folder)
        
        with Button(
            name=plugin.folder, 
            action=self.enable_plugin if not plugin.running else self.disable_plugin, 
            style=styles.FlexVertical() 
                + styles.Gap("10px") 
                + styles.Padding("15px") 
                + styles.Classname("rounded-md border") 
                + styles.Height("100%") 
                + styles.Width("100%") 
                + (styles.Classname("bg-input/20") if plugin.running else styles.Classname("bg-input/10"))
        ):
            with Container(
                style=styles.FlexHorizontal() 
                    + styles.Gap("10px") 
                    + styles.Classname("justify-between text-left") 
                    + styles.Height("100%") 
                    + styles.Width("100%")
            ):
                with Container(
                    style=styles.FlexHorizontal() 
                        + styles.Gap("15px")
                ):  
                    if plugin.folder in self.enabling:
                        with Spinner():
                            Icon("loader")
                    with Container(
                        style=styles.FlexVertical() 
                            + styles.Gap("5px")
                    ):
                        Text(plugin.description.name, styles.Classname("font-semibold"))
                        Text(plugin.description.description, styles.Description() + styles.Classname("text-xs"))
                        
                with Container(styles.FlexHorizontal() + styles.Gap("5px")):
                    if not isinstance(plugin.authors, list):
                        with Container(styles.Classname("bg-input/30 rounded-md border px-2 py-1 h-min")):
                            Text(plugin.authors.name, styles.Classname("text-xs"))
                    else:
                        for author in plugin.authors:
                            with Container(styles.Classname("bg-input/30 rounded-md border px-2 py-1 h-min")):
                                Text(author.name, styles.Classname("text-xs"))
    
    def render_plugin_list(self, plugins_list):
        i = 0
        while i < len(plugins_list):
            with Container(styles.FlexHorizontal() + styles.Gap("20px") + styles.Height("100%")):
                if i + 1 == len(plugins_list):
                    with Container(styles.Width("50%") + styles.Height("auto")):
                        self.render_plugin(plugins_list[i])
                    
                    with Container(styles.Width("50%") + styles.Height("auto")): ... # Fake second item to fill the space
                else:
                    for j in range(2):
                        if i + j < len(plugins_list):
                            with Container(styles.Width("50%") + styles.Height("auto")):
                                self.render_plugin(plugins_list[i + j])
                i += 2
    
    # MARK: Body
    def init(self):
        threading.Thread(target=self.basic_mode_updater, daemon=True).start()
    
    def render(self):
        if plugins.loading:
            with Container(styles.FlexVertical() + styles.Classname("w-full h-full items-center justify-center relative")):
                with Spinner():
                    Icon("loader")
                
                Text(_("Loading plugins..."), styles.Description())
                if plugins.plugins:
                    target = plugins.plugins[-1]
                    if not hasattr(target, "description") and len(plugins.plugins) > 1:
                        target = plugins.plugins[-2]
                        
                    Text(target.description.name, styles.Classname("text-xs text-muted-foreground absolute bottom-2"))
            return
        
        isBasic = not settings.Get("global", "advanced_plugin_mode", False)
        if isBasic:
            with Container(styles.FlexHorizontal() + styles.Padding("40px") + styles.Gap("40px")):
                with Container(styles.FlexVertical() + styles.Gap("20px") + styles.Width("400px") + styles.Classname("relative")):
                    Text(_("Plugins (Basic)"), styles.Title())
                    Text(_("You can enable different ETS2LA features on the right side. All of the plugins described by these features will be enabled automatically without any additional configuration."), styles.Description())
                    with Button(
                        self.toggle_running,
                        enabled=not self.update_queue
                    ):
                        if self.update_queue:
                            with Spinner():
                                Icon("loader")
                        Text(_("Disable Plugins") if self.running else _("Enable Plugins"))

                    enabled_plugins = [plugin.description.name for plugin in plugins.plugins if plugin.running]
                    Markdown(_("Currently enabled plugins:") + "\n- " + ("\n- ".join(enabled_plugins) if enabled_plugins else _("None")), styles.Description())

                with Container(styles.FlexVertical() + styles.Gap("20px") + styles.Width("525px")):
                    for feature in basic_mode_features:
                        with Button(
                            self.toggle_feature,
                            name=feature.name, 
                            style=styles.FlexVertical() 
                                + styles.Padding("20px") 
                                + styles.Classname("w-full h-max " + ("bg-background" if not self.feature_toggles[feature.name] else "")),
                            enabled=feature.name not in self.update_queue
                        ):
                            text_lg = styles.Style()
                            text_lg.font_size = "1rem"
                            with Container(styles.FlexVertical() + styles.Gap("5px") + styles.Classname("text-left w-full")):
                                with Container(styles.FlexHorizontal() + styles.Classname("justify-between items-center")):
                                    Text(feature.name, styles.Classname("font-semibold" + ("" if self.feature_toggles[feature.name] else " text-muted-foreground")) + text_lg)
                                    
                                    if feature.name in self.update_queue:
                                        with Spinner():
                                            Icon("loader")
                                    else:
                                        Text(_("Enabled") if self.feature_toggles[feature.name] else _("Disabled"), styles.Classname("text-xs font-semibold" + ("" if self.feature_toggles[feature.name] else " text-muted-foreground")))

                                Markdown(feature.description, styles.Description() + styles.Classname("font-normal"))
                    
                    with Button(self.handle_advanced_mode_toggle):
                        Text(_("Switch to Advanced Mode"))

        else:
            tags = []
            authors = []
            for plugin in plugins.plugins:
                if not hasattr(plugin, "description"):
                    continue
                
                for tag in plugin.description.tags:
                    if tag not in tags:
                        tags.append(tag)
                if not isinstance(plugin.authors, list):
                    if plugin.authors.name not in authors:
                        authors.append(plugin.authors.name)
                else:
                    for author in plugin.authors:
                        if author.name not in authors:
                            authors.append(author.name)
            tags.sort()
            
            with Container(styles.FlexVertical() + styles.Classname("w-full") + styles.Padding("20px 20px 0 20px")):
                # Top bar with search and tags
                with Container(styles.FlexHorizontal() + styles.Gap("20px") + styles.Classname("items-center") + styles.Padding("0 40px 0 0")):
                    Input(
                        _("Search plugins..."),
                        changed=self.handle_search
                    )
                    Combobox(
                        options=tags,
                        default="Base",
                        changed=self.handle_tags,
                        multiple=True,
                        search=ComboboxSearch(
                            placeholder=_("Search tags..."),
                            empty=_("No tags found")
                        )
                    )
                    Combobox(
                        options=authors,
                        default="",
                        changed=self.handle_authors,
                        multiple=True,
                        search=ComboboxSearch(
                            placeholder=_("Search authors..."),
                            empty=_("No authors found")
                        )
                    )
                    with Button(self.handle_advanced_mode_toggle):
                        Text(_("Back to Basic Mode"))

            running_plugins = [plugin for plugin in plugins.plugins if plugin.running and plugin.folder not in self.disabling]
            running_plugins += [plugin for plugin in plugins.plugins if plugin.folder in self.enabling and plugin not in running_plugins]
            running_plugins.sort(key=lambda p: p.description.name.lower())
                
            # filter out running plugins
            filtered_plugins = [
                plugin for plugin in plugins.plugins
                if plugin not in running_plugins
            ]
            # filter by search term
            filtered_plugins = [
                plugin for plugin in filtered_plugins
                if (self.search_term.lower() in plugin.description.name.lower() if self.search_term else True)
            ]
            # filter by tags
            filtered_plugins = [
                plugin for plugin in filtered_plugins
                if (not self.tags or any(tag in plugin.description.tags for tag in self.tags))
            ]
            # filter by authors
            filtered_plugins = [
                plugin for plugin in filtered_plugins
                if (not self.authors or (isinstance(plugin.authors, list) and any(author.name.lower() in self.authors for author in plugin.authors)) or (not isinstance(plugin.authors, list) and plugin.authors.name.lower() in self.authors))
            ]
            # sort by name
            filtered_plugins.sort(key=lambda p: p.description.name.lower())
            
            # Render the lists
            with Container(styles.FlexVertical() + styles.Padding("0 20px") + styles.Gap("20px")):
                Text(_("Running Plugins"), styles.Classname("font-semibold"))
                if not running_plugins:
                    if not last_plugins:
                        with Alert():
                            Text(_("No plugins are currently running."), styles.Description())
                    else:
                        with Alert(style=styles.Gap("20px") + styles.FlexVertical()):
                            Markdown(f"{_('Want to enable the plugins you had running last time?')}\n\n**{', '.join(last_plugins)}**", styles.Description())
                            with Button(action=self.enable_last_plugins):
                                Text(_("Enable Last Plugins"))

                else:
                    self.render_plugin_list(running_plugins)
            
            with Container(styles.FlexVertical() + styles.Gap("20px") + styles.Padding("0 20px")):
                Text(_("Available Plugins"), styles.Classname("font-semibold"))
                self.render_plugin_list(filtered_plugins)