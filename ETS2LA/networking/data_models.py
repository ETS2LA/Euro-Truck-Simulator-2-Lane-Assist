from pydantic import BaseModel

class PluginCallData(BaseModel):
    args: list
    kwargs: dict
    
class TagFetchData(BaseModel):
    tag: str

class RelieveData(BaseModel):
    data: dict