class Author:
    name: str
    url: str
    icon: str = ""

    def __init__(self, name: str, url: str, icon: str = "") -> None:
        self.name = name
        self.url = url
        self.icon = icon
