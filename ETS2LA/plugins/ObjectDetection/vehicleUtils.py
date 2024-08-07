from ETS2LA.utils.values import SmoothedValue
import math
import time

lastPositionArray = {
    # id : 
    #   xyz: [x, y, z]
    #   speed: SmoothedValue
}

def GetVehicleSpeed(id) -> float:
    if id in lastPositionArray:
        return lastPositionArray[id]["speed"].get()
    else:
        return 0

def UpdateVehicleSpeed(id, position) -> float:
    if id in lastPositionArray:
        if len(position) != 3:
            return 0
        lastPosition = lastPositionArray[id]["xyz"]
        lastTime = lastPositionArray[id]["time"]
        currentTime = time.time()
        distance = math.sqrt((position[0] - lastPosition[0])**2 + (position[1] - lastPosition[1])**2 + (position[2] - lastPosition[2])**2)
        timeDifference = currentTime - lastTime
        speed = distance / timeDifference
        lastPositionArray[id]["xyz"] = position
        lastPositionArray[id]["speed"](speed)
        lastPositionArray[id]["time"] = currentTime
        #print(f"Speed: {speed}, Distance: {distance}")
        return speed
    else:
        if len(position) != 3:
            return 0
        lastPositionArray[id] = {
            "xyz": position,
            "speed": SmoothedValue("time", 1),
            "time": time.time()
        }
        return 0