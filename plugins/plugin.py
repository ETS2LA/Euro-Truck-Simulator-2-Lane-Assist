"""
Helper file for plugins
"""

class PluginInformation():
    """
    Class to store plugin information
    
    Attributes:
        name (str): Name of the plugin (AddsSpacesBetweenUpperCases)
        
        description (str): Description of the plugin
        
        version (str): Version of the plugin
        
        author (str): Author of the plugin
        
        url (str): URL of the plugin
        
        type (str): Type of the plugin ("static" (updated when showing window), "dynamic" (updated every frame))
        
        dynamicOrder (str) (if dynamic): Select at which state the plugin is run
                >>> "before image capture"
                >>> "image capture"
                >>> "before lane detection"
                >>> "lane detection"
                >>> "before controller"
                >>> "controller"
                >>> "before game"
                >>> "game"
                >>> "before UI"
                >>> "last" (reserved for fps limiter, other plugins may make it less accurate)
        
        image (str) (optional): Image path (in the plugin folder) (image file will be scaled to around 120x120)

        disablePlugins (bool) (optional): If true then the panel will prompt to disable plugins when opened
        
        disableLoop (bool) (optional): If true then the panel will prompt to disable the mainloop when opened (useful for panels that use a lot of resources or have problems with dxcam for example)
        
        noUI (bool) (optional): If true then the UI button will not be shown
        
        exclusive (str) (optional): If set to a str then no other plugins of the same 'exclusive' type can be enabled at the same time 
        
        requires (list) (optional): List of plugins that are required for this plugin to work (plugin names)
                >>> ["plugin1", "plugin2"]
    
    """
    def __init__(self, name, description, version, author, url, type, image=None, dynamicOrder=None, disablePlugins=False, disableLoop=False, noUI=False, exclusive=None, requires=None):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.url = url
        self.image = image
        self.type = type
        self.dynamicOrder = dynamicOrder
        self.disablePlugins = disablePlugins
        self.disableLoop = disableLoop
        self.noUI = noUI
        self.exclusive = exclusive
        self.requires = requires