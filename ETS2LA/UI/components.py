ui = [
    
]

class Title():
    def __init__(self, text: str):
        global ui
        ui.append({
            "title": {
                "text": text
            }
        })
    
class Description():
    def __init__(self, text: str):
        global ui
        ui.append({
            "description": {
                "text": text
            }
        })
    
class Button():
    def __init__(self, text: str, target: object):
        global ui
        ui.append({
            "button": {
                "text": text,
                "target": target.__name__
            }
        })
    
def RenderUI():
    global ui
    temp_ui = ui.copy()
    ui = []
    return temp_ui