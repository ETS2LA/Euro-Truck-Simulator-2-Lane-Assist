import ETS2LA.modules.TruckSimAPI.main as API
import ETS2LA.backend.controls as controls
import ETS2LA.backend.backend as backend
from ETS2LA.backend.classes import Job
import threading
import logging
import time

API.Initialize()
    
# Events
class ToggleSteering():
    steering = True
    def ToggleSteering(self):
        self.steering = not self.steering
        backend.CallEvent('ToggleSteering', self.steering, {})
    def __init__(self):
        controls.RegisterKeybind('ToggleSteering', lambda self=self: self.ToggleSteering(), defaultButtonIndex="n")
        
class JobStarted():
    def JobStarted(self, data):
        job = Job()
        job.fromAPIData(data)
        backend.CallEvent('JobStarted', job, {})
        logging.info("Triggered event: JobStarted")
        logging.info(job.json())
    def __init__(self):
        API.listen('jobStarted', self.JobStarted)
        
class JobEnded():
    def JobEnded(self, data):
        job = Job()
        job.fromAPIData(data)
        backend.CallEvent('JobEnded', job, {})
        logging.info("Triggered event: JobEnded")
        logging.info(job.json())
    def __init__(self):
        API.listen('jobEnded', self.JobEnded)
        
        
# Start monitoring

def ApiThread():
    while True:
        API.run()
        time.sleep(0.1)

def run():
    ToggleSteering()
    JobEnded()
    JobStarted()
    
    threading.Thread(target=ApiThread, daemon=True).start()
    logging.info("Event monitor started.")