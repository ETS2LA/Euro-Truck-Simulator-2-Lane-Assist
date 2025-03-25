from pydantic import BaseModel
from typing import Literal

class PluginCallData(BaseModel):
    target: str
    args: list
    kwargs: dict
    
class TagFetchData(BaseModel):
    tag: str
    zlib: bool = False

class RelieveData(BaseModel):
    data: dict
    
class PageFetchData(BaseModel):
    page: str = ""
    
class PopupData(BaseModel):
    text: str
    type: Literal["info", "warning", "error", "success"] = "info"