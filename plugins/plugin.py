"""
Helper file for plugins
"""

import signal
import functools

class PluginInformation():
    """
    Class to store plugin information
    
    Attributes:
        name (str): Name of the plugin (AddsSpacesBetweenUpperCases)
        
        description (str): Description of the plugin
        
        version (str): Version of the plugin
        
        author (str): Author(s) of the plugin. In the case of multiple authors please seperate them with a , (comma)
        
        url (str): URL of the plugin
        
        type (str): Type of the plugin ("static" (updated when showing window), "dynamic" (updated every frame))
        
        dynamicOrder (str): Select at which state the plugin is run - "before image capture", "image capture", "before lane detection", "lane detection", "before controller", "controller", "before game", "game", "before UI", "last" (reserved for fps limiter, other plugins may make it less accurate)
        
        image (str): Image path (in the plugin folder) (image file will be scaled to around 120x120)

        disablePlugins (bool): If true then the panel will prompt to disable plugins when opened
        
        disableLoop (bool): If true then the panel will prompt to disable the mainloop when opened (useful for panels that use a lot of resources or have problems with dxcam for example)
        
        noUI (bool): If true then the UI button will not be shown
        
        exclusive (str): If set to a str then no other plugins of the same 'exclusive' type can be enabled at the same time 
        
        requires (list): List of plugins that are required for this plugin to work (plugin names) ["plugin1", "plugin2"]
    
        maxExecTime (int): Maximum execution time in ms (if the plugin takes longer than this to execute then it will be skipped) (set to 0 to disable the limit, default:100)
    
    """
    def __init__(self, name, description, version, author, url, type, image=None, dynamicOrder=None, disablePlugins=False, disableLoop=False, noUI=False, exclusive=None, requires=None, maxExecTime=100):
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
        self.maxExecTime = maxExecTime