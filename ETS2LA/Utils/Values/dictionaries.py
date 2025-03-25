# https://stackoverflow.com/a/70377616
def set_nested_item(dataDict: dict, mapList: list[str], val) -> dict:
    current_dict = dataDict
    for key in mapList[:-1]:
        if key not in current_dict:
            current_dict[key] = {}
        current_dict = current_dict[key]
    current_dict[mapList[-1]] = val
    return dataDict

def get_nested_item(dataDict: dict, mapList: list[str]):
    """Get item in nested dictionary"""
    for k in mapList:
        dataDict = dataDict[k]
    return dataDict

# https://stackoverflow.com/a/7205107
def merge(a: dict, b: dict, path=[]):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a