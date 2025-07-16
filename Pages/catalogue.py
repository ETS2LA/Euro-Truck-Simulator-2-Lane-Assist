from ETS2LA.UI import *
import webbrowser
import threading
import requests
import random
import time
import yaml

class CataloguePlugin():
    name: str
    overview: str
    description: str
    
    image_url: str
    version: str
    author: str
    
    def __init__(self, name: str, overview: str, description: str, image_url: str, version: str, author: str):
        self.name = name
        self.overview = overview
        self.description = description
        self.image_url = image_url
        self.version = version
        self.author = author

class Page(ETS2LAPage):
    url = "/catalogue"
    
    loading = False
    catalogue = {}
    catalogues = [
        "https://github.com/ETS2LA/plugins"
    ]
    
    plugins: list[CataloguePlugin] = []
    selected_plugin: CataloguePlugin = None
    
    search_term: str = ""
    
    def get_catalogue_data(self, catalogue: str) -> str:
        url = catalogue
        if "github.com" in url:
            # ex. https://raw.githubusercontent.com/ETS2LA/plugins/refs/heads/main/catalogue.yaml
            url = url.replace("github.com", "raw.githubusercontent.com") + "/refs/heads/main/catalogue.yaml"
            
        response = requests.get(url)
        if response.status_code == 200:
            return yaml.safe_load(response.text)
        else:
            return {}
        
    def get_plugin_data(self, repository: str) -> CataloguePlugin:
        if repository == "":
            return None
        
        url = repository
        if "github.com" in url:
            # ex. https://raw.githubusercontent.com/ETS2LA/plugins/refs/heads/main/plugin.yaml
            url = url.replace("github.com", "raw.githubusercontent.com") + "/refs/heads/main/plugin.yaml"
            
        response = requests.get(url)
        if response.status_code == 200:
            data = yaml.safe_load(response.text)
            return CataloguePlugin(
                name=data.get("name", "Unknown"),
                overview=data.get("overview", "No overview provided."),
                description=data.get("description", "No description provided."),
                image_url=data.get("image_url", ""),
                version=data.get("version", "0.0.0"),
                author=data.get("author", "Unknown")
            )
        
        return None
            
    def crawl_catalogue(self):
        self.plugins = []
        for item in self.catalogue.get("plugins", []):
            time.sleep(random.uniform(0.1, 0.5))  # Simulate network delay
            data = self.get_plugin_data(item.get("repository", ""))
            if data:
                self.plugins.append(data)

    def update_data(self):
        self.catalogue = self.get_catalogue_data(self.catalogues[0])
        self.crawl_catalogue()
        self.loading = False

    def open_event(self):
        if self.plugins:
            return
        
        self.loading = True
        threading.Thread(target=self.update_data).start()
    
    def select_plugin(self, plugin: str):
        for p in self.plugins:
            if p.name == plugin:
                self.selected_plugin = p
                break
            
    def unselect_plugin(self):
        self.selected_plugin = None
        
    def open_source_code(self, plugin: str):
        for p in self.catalogue.get("plugins", []):
            print(p)
            if p.get("name") == plugin:
                repository = p.get("repository", "")
                if repository:
                    webbrowser.open(repository)
                    return
                    
        SendPopup("Couldn't find source code for this plugin.")
    
    def loading_screen(self) -> bool:
        if self.loading:
            with Container(styles.FlexVertical() + styles.Classname("w-full h-full items-center justify-center relative")):
                with Spinner():
                    Icon("loader")
                
                Text("Refreshing...", styles.Description())
                if self.plugins:
                    Text(f"Loaded {len(self.plugins)} plugins", styles.Classname("text-xs text-muted-foreground absolute bottom-2"))
                
                return True
        return False
    
    def render_plugin_card(self, plugin: CataloguePlugin):
        with Button(name=plugin.name, action=self.select_plugin, type="ghost",
                style=styles.FlexHorizontal() 
                    + styles.Classname("w-full border rounded-md p-4 gap-4 bg-input/10 h-max")):
            if plugin.image_url:
                Image(url=plugin.image_url, style=styles.Style(
                    width="60px",
                    height="60px",
                ) + styles.Classname("rounded-md border"))
            
            with Container(
                style=styles.FlexHorizontal() 
                    + styles.Gap("10px") 
                    + styles.Classname("justify-between text-left") 
                    + styles.Height("100%") 
                    + styles.Width("100%")
            ):
                with Container(styles.FlexVertical() + styles.Gap("5px")):
                    Text(plugin.name, styles.Classname("font-semibold"))
                    Text(plugin.overview, styles.Description())
                
                with Container(styles.FlexHorizontal() + styles.Gap("5px")):
                    with Container(styles.Classname("bg-input/30 rounded-md border px-2 py-1 h-min")):
                        Text(plugin.author, styles.Classname("text-xs"))
    
    def render_plugin_details(self):
        if not self.selected_plugin:
            return False
        
        with Container(styles.Classname("w-full h-full p-4 gap-4") + styles.FlexVertical()):
            with Container(styles.FlexHorizontal() + styles.Gap("10px") + styles.Classname("items-center")):
                with Button(action=self.unselect_plugin):
                    Icon("arrow-left")
                    Text("Back", styles.Classname("font-semibold"))
                with Button(name=self.selected_plugin.name, action=self.open_source_code):
                    Icon("github")
                    Text("Source Code", styles.Classname("font-semibold"))
                
            with Container(styles.FlexHorizontal() + styles.Classname("w-full justify-between border rounded-md p-4 bg-input/10")):
                with Container(styles.FlexVertical() + styles.Gap("5px") + styles.Classname("w-full")):
                    with Container(styles.FlexHorizontal() + styles.Classname("justify-between w-full")):
                        with Container(styles.FlexHorizontal() + styles.Classname("gap-2 items-center")):
                            Text(self.selected_plugin.name, styles.Title())
                            with Container(styles.Classname("bg-input/30 rounded-md border px-2 py-1 h-min")):
                                Text(self.selected_plugin.version, styles.Classname("text-xs"))
                            
                        with Container(styles.FlexHorizontal() + styles.Classname("gap-2 items-center")):
                            with Container(styles.Classname("bg-input/30 rounded-md border px-2 py-1 h-min")):
                                Text(self.selected_plugin.author, styles.Classname("text-xs"))
                                
                    Text(self.selected_plugin.description, styles.Description())

                if self.selected_plugin.image_url:
                    Image(url=self.selected_plugin.image_url, style=styles.Style(
                        width="100px",
                        height="100px",
                    ) + styles.Classname("rounded-md border"))
            
            
        return True
    
    def handle_search(self, search_term: str):
        self.search_term = search_term.lower()
    
    def header(self):
        with Container(styles.FlexHorizontal() + styles.Classname("w-full h-16 items-center justify-between px-2 pr-12")):
            with Container(styles.FlexHorizontal() + styles.Classname("gap-2 items-center")):
                Text("Plugin Catalogue", styles.Title())
                
            with Container(styles.FlexHorizontal() + styles.Classname("gap-2 items-center")):
                Input(
                    "Search plugins...",
                    changed=self.handle_search
                )
                with Button(action=self.open_event, type="ghost"):
                    Icon("refresh-ccw")
                    Text("Refresh", styles.Classname("text-xs"))
    
    def render(self):
        if self.loading_screen():
            return

        if not self.plugins:
            with Container(styles.FlexVertical() + styles.Classname("w-full h-full items-center justify-center relative")):
                Text("No plugins found in the plugin catalogue.", styles.Description())
                return
    
        if self.render_plugin_details():
            return
        
        with Container(styles.Classname("w-full h-full p-4 gap-4") + styles.FlexVertical()):
            self.header()
            for plugin in self.plugins:
                if self.search_term \
                   and self.search_term not in plugin.name.lower() \
                   and self.search_term not in plugin.overview.lower():
                    continue
                self.render_plugin_card(plugin)