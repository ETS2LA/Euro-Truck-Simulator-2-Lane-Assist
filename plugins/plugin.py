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
        image (str): Image path (in the plugin folder) (image file will be scaled to around 120x120)
    
    """
    def __init__(self, name, description, version, author, url, image=None):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.url = url
        self.image = image