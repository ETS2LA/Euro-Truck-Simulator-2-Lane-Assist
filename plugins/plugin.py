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
                >>> "before lane detection"
                >>> "before steering"
                >>> "before game"
                >>> "before UI"
        
        image (str) (optional): Image path (in the plugin folder) (image file will be scaled to around 120x120)

        disablePlugins (bool) (optional): If true then the panel will prompt to disable plugins when opened
    
    """
    def __init__(self, name, description, version, author, url, type, image=None, dynamicOrder=None, disablePlugins=False):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.url = url
        self.image = image
        self.type = type
        self.dynamicOrder = dynamicOrder
        self.disablePlugins = disablePlugins