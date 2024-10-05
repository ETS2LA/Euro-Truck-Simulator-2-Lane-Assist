# https://stackoverflow.com/a/70377616
def set_nested_item(dataDict: dict, mapList: list[str], val: any) -> dict:
    """Set item in nested dictionary"""
    current_dict = dataDict
    for key in mapList[:-1]:
        current_dict = current_dict.setdefault(key, {})
    current_dict[mapList[-1]] = val
    return dataDict

def get_nested_item(dataDict: dict, mapList: list[str]) -> any:
    """Get item in nested dictionary"""
    for k in mapList:
        dataDict = dataDict[k]
    return dataDict