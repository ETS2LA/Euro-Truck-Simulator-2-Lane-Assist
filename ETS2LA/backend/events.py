import ETS2LA.backend.controls as controls
import ETS2LA.backend.backend as backend
import logging
    
# Events
class ToggleSteering():
    steering = True
    
    def ToggleSteering(self):
        self.steering = not self.steering
        backend.CallEvent('ToggleSteering', self.steering, {})
    
    def __init__(self):
        controls.RegisterKeybind('ToggleSteering', lambda self=self: self.ToggleSteering(), defaultButtonIndex="n")
        
# Start monitoring
def run():
    ToggleSteering()