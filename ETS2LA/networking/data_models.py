from pydantic import BaseModel

class PluginCallData(BaseModel):
    args: list
    kwargs: dict
    
class TagFetchData(BaseModel):
    tag: str
    zlib: bool = False

class RelieveData(BaseModel):
    data: dict