from ETS2LA.backend.classes import Job, CancelledJob, FinishedJob, Refuel
from modules.SDKController.main import SCSController
from ETS2LA.utils.translator import Translate
from ETS2LA.utils.values import SmoothedValue
from ETS2LA.frontend.immediate import value
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import ETS2LA.backend.backend as backend
import ETS2LA.networking.cloud as cloud
import ETS2LA.backend.sounds as sounds
import modules.TruckSimAPI.main as API
import threading
import logging
import time

API = API.Module("global")
API.CHECK_EVENTS = True # DO NOT DO THIS ANYWHERE ELSE!!! PLEASE USE THE EVENTS SYSTEM INSTEAD!!!
callbacks = []
controller = SCSController()

steering_threshold = settings.Get("global", "steering_threshold", 0.1)
braking_threshold = settings.Get("global", "braking_threshold", 0.2)
    
# Events
class ToggleSteering():
    steering = False
    app_braking = SmoothedValue("time", 0.5)
    game_braking = SmoothedValue("time", 0.5)
    def ToggleSteering(self):
        self.steering = not self.steering
        sounds.Play('start' if self.steering else 'end')
        backend.call_event('ToggleSteering', self.steering, {})
        logging.info("Triggered event: ToggleSteering")
        time.sleep(1)
        
    def CheckForUserInput(self, data):
        if self.steering:
            app_braking = self.app_braking(controller.abackward)
            game_braking = self.game_braking(data["truckFloat"]["userBrake"])
            if game_braking == 1.111: game_braking = 0 # Virtual API in use
            need_to_disable_via_braking = abs(app_braking - game_braking) > braking_threshold
            if braking_threshold >= 0 and braking_threshold <= 1:
                if need_to_disable_via_braking:
                    print("Braking: " + str(app_braking) + " - " + str(game_braking) + " = " + str(abs(app_braking - game_braking)))
                    self.ToggleSteering()
                
    def __init__(self):
        controls.RegisterKeybind('ToggleSteering', lambda self=self: self.ToggleSteering(), defaultButtonIndex="n")
        callbacks.append(self.CheckForUserInput)
        
last_started_job = None # This is used to fill out the data for the Job events
class JobStarted():
    def JobStarted(self, data):
        global last_started_job
        job = Job()
        job.fromAPIData(data)
        backend.call_event('JobStarted', job, {})
        logging.info("Triggered event: JobStarted")
        cloud.StartedJob(job)
        last_started_job = job
    def __init__(self):
        API.listen('jobStarted', self.JobStarted)
        
class JobFinished():
    def JobFinished(self, data):
        job = FinishedJob()
        job.fromAPIData(data)
        if job.cargo_id == '' and job.cargo == '' and job.unit_count == 0 and job.unit_mass == 0 and last_started_job != None:
            job.cargo_id = last_started_job.cargo_id
            job.cargo = last_started_job.cargo
            job.unit_count = last_started_job.unit_count
            job.unit_mass = last_started_job.unit_mass
        backend.call_event('JobFinished', job, {})
        logging.info("Triggered event: JobFinished")
        cloud.FinishedJob(job)
    def __init__(self):
        API.listen('jobFinished', self.JobFinished)
        
class JobDelivered():
    def JobDelivered(self, data):
        job = FinishedJob()
        job.fromAPIData(data)
        backend.call_event('JobDelivered', job, {})
        logging.info("Triggered event: JobDelivered")
    def __init__(self):
        API.listen('jobDelivered', self.JobDelivered)
        
class JobCancelled():
    def JobCancelled(self, data):
        job = CancelledJob()
        job.fromAPIData(data)
        backend.call_event('JobCancelled', job, {})
        logging.info("Triggered event: JobCancelled")
        cloud.CancelledJob(job)
    def __init__(self):
        API.listen('jobCancelled', self.JobCancelled)
        
class RefuelStarted():
    def RefuelStarted(self, data):
        refuel = Refuel()
        refuel.fromAPIData(data)
        backend.call_event('RefuelStarted', refuel, {})
        logging.info("Triggered event: RefuelStarted")
    def __init__(self):
        API.listen('refuelStarted', self.RefuelStarted)
        
class RefuelPayed():
    def RefuelPayed(self, data):
        refuel = Refuel()
        refuel.fromAPIData(data)
        backend.call_event('RefuelPayed', refuel, {})
        logging.info("Triggered event: RefuelPayed")
    def __init__(self):
        API.listen('refuelPayed', self.RefuelPayed)

class VehicleChange():
    lastLicensePlate = ""
    firstRun = True
    def VehicleChange(self, data):
        backend.call_event('VehicleChange', data["configString"]["truckLicensePlate"], {})
        logging.info("Triggered event: VehicleChange")
        if self.firstRun: # Ignore the first run as the frontend has not yet started
            self.firstRun = False
            return
        
        # Try to get new FOV value from user
        dict = [{
            "name": "events.vehicle_change.vehicle_change",
            "description": "events.vehicle_change.vehicle_change_description",
            "type": {
                "type": "number",
                "default": settings.Get("global", "FOV", 77)
            }
        }]
        newFOV = value("Vehicle Change Detected", dict)
        if newFOV != 0 and newFOV != None:
            settings.Set("global", "FOV", newFOV["value"])
            logging.info("New FOV value set to: " + str(newFOV))
        
    def ApiCallback(self, data):
        if data["configString"]["truckLicensePlate"] != self.lastLicensePlate:
            self.lastLicensePlate = data["configString"]["truckLicensePlate"]
            self.VehicleChange(data)
        
    def __init__(self):
        callbacks.append(self.ApiCallback)
        
# Start monitoring
def ApiThread():
    while True:
        data = API.run()
        for callback in callbacks:
            try:
                callback(data)
            except:
                logging.exception("Error in callback")
                
        time.sleep(0.1)

def run():
    ToggleSteering()
    JobStarted()
    JobFinished()
    JobDelivered()
    JobCancelled()
    RefuelStarted()
    RefuelPayed()
    VehicleChange()
    
    threading.Thread(target=ApiThread, daemon=True).start()
    logging.info("Event monitor started.")
