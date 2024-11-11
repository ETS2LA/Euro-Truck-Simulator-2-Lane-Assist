import mmap
import struct
import logging
import os
print = logging.info


# https://github.com/RenCloud/scs-sdk-plugin/blob/dev/scs-telemetry/inc/scs-telemetry-common.hpp

LINUX = os.path.exists("/etc/os-release")
if LINUX:
    mmapName = "/dev/shm/SCS/SCSTelemetry"
else:
    mmapName = "Local\\SCSTelemetry"
mmapSize = 32*1024

stringSize = 64
wheelSize = 14
substanceSize = 25


import time

class scsTelemetry:
    
    specialBoolOffsets = {
        "onJob": 4300,
        "jobFinished": 4301,
        "jobCancelled": 4302,
        "jobDelivered": 4303,
        "fined": 4304,
        "tollgate": 4305,
        "ferry": 4306,
        "train": 4307,
        "refuel": 4308,
        "refuelPayed": 4309
    }
    
    # MARK: VARIABLE READING
    
    def readGame(self, offset):
        int = struct.unpack('i', self.mm[offset:offset+4])[0]
        if int == 1:
            return "ETS2", offset+4
        elif int == 2:
            return "ATS", offset+4
        else:
            return "unknown", offset+4
    
    # MARK: SPECIAL READING
    
    def readTrailer(self, offset, count=1):
        trailers = []
        for i in range(count):
            data = {}
            
            # START OF FIRST ZONE AT OFFSET 0 
            
            data["conBool"] = {}
            data["conBool"]["wheelSteerable"], offset = self.readBool(offset, count=16)
            data["conBool"]["wheelSimulated"], offset = self.readBool(offset, count=16)
            data["conBool"]["wheelPowered"], offset = self.readBool(offset, count=16)
            data["conBool"]["wheelLiftable"], offset = self.readBool(offset, count=16)

            data["comBool"] = {}
            data["comBool"]["wheelOnGround"], offset = self.readBool(offset, count=16)
            data["comBool"]["attached"], offset = self.readBool(offset)
            
            data["bufferBool"], offset = self.readChar(offset, count=3)
            
            # END OF FIRST ZONE -> Offset 84
            
            # START OF SECOND ZONE -> Offset 84
            
            data["comUI"] = {}
            data["comUI"]["wheelSubstance"], offset = self.readInt(offset, count=16)
            
            data["conUI"] = {}
            data["conUI"]["wheelCount"], offset = self.readInt(offset)
            
            # END OF SECOND ZONE -> Offset 152
            
            # START OF THIRD ZONE -> Offset 152
            
            data["comFloat"] = {}
            data["comFloat"]["cargoDamage"], offset = self.readFloat(offset)
            data["comFloat"]["wearChassis"], offset = self.readFloat(offset)
            data["comFloat"]["wearWheels"], offset = self.readFloat(offset)
            data["comFloat"]["wearBody"], offset = self.readFloat(offset)

            data["comFloat"]["wheelSuspDeflection"], offset = self.readFloat(offset, count=16)
            data["comFloat"]["wheelVelocity"], offset = self.readFloat(offset, count=16)
            data["comFloat"]["wheelSteering"], offset = self.readFloat(offset, count=16)
            data["comFloat"]["wheelRotation"], offset = self.readFloat(offset, count=16)
            data["comFloat"]["wheelLift"], offset = self.readFloat(offset, count=16)
            data["comFloat"]["wheelLiftOffset"], offset = self.readFloat(offset, count=16)

            data["conFloat"] = {}
            data["conFloat"]["wheelRadius"], offset = self.readFloat(offset, count=16)
            
            # END OF THIRD ZONE -> Offset 616
            
            # START OF FOURTH ZONE -> Offset 616
            
            data["comVector"] = {}
            data["comVector"]["linearVelocityX"], offset = self.readFloat(offset)
            data["comVector"]["linearVelocityY"], offset = self.readFloat(offset)
            data["comVector"]["linearVelocityZ"], offset = self.readFloat(offset)
            data["comVector"]["angularVelocityX"], offset = self.readFloat(offset)
            data["comVector"]["angularVelocityY"], offset = self.readFloat(offset)
            data["comVector"]["angularVelocityZ"], offset = self.readFloat(offset)
            data["comVector"]["linearAccelerationX"], offset = self.readFloat(offset)
            data["comVector"]["linearAccelerationY"], offset = self.readFloat(offset)
            data["comVector"]["linearAccelerationZ"], offset = self.readFloat(offset)
            data["comVector"]["angularAccelerationX"], offset = self.readFloat(offset)
            data["comVector"]["angularAccelerationY"], offset = self.readFloat(offset)
            data["comVector"]["angularAccelerationZ"], offset = self.readFloat(offset)

            data["conVector"] = {}
            data["conVector"]["hookPositionX"], offset = self.readFloat(offset)
            data["conVector"]["hookPositionY"], offset = self.readFloat(offset)
            data["conVector"]["hookPositionZ"], offset = self.readFloat(offset)
            data["conVector"]["wheelPositionX"], offset = self.readFloat(offset, count=16)
            data["conVector"]["wheelPositionY"], offset = self.readFloat(offset, count=16)
            data["conVector"]["wheelPositionZ"], offset = self.readFloat(offset, count=16)

            data["bufferVector"], offset = self.readChar(offset, count=4)
            
            # END OF FOURTH ZONE -> Offset 872
            
            # START OF FIFTH ZONE -> Offset 872
            
            data["comDouble"] = {}
            data["comDouble"]["worldX"], offset = self.readDouble(offset)
            data["comDouble"]["worldY"], offset = self.readDouble(offset)
            data["comDouble"]["worldZ"], offset = self.readDouble(offset)
            data["comDouble"]["rotationX"], offset = self.readDouble(offset)
            data["comDouble"]["rotationY"], offset = self.readDouble(offset)
            data["comDouble"]["rotationZ"], offset = self.readDouble(offset)
            
            # END OF FIFTH ZONE -> Offset 920
            
            # START OF SIXTH ZONE -> Offset 920
            
            data["conString"] = {}
            data["conString"]["id"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["cargoAccessoryId"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["bodyType"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["brandId"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["brand"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["name"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["chainType"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["licensePlate"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["licensePlateCountry"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["licensePlateCountryId"], offset = self.readChar(offset, count=stringSize)
            
            # END OF SIXTH ZONE -> Offset 1560
            
            trailers.append(data)
            
        return trailers, offset
            
    
    # MARK: VALUE SETTING
    
    def setBool(self, offset, value):
        self.mm = mmap.mmap(0, mmapSize, mmapName)
        self.mm[offset:offset+1] = struct.pack('?', value)
        self.mm.close()
        return offset+1
    
    # MARK: VALUE READING
    
    def readBool(self, offset, count=1):
        if count == 1:
            bool = struct.unpack('?', self.mm[offset:offset+1])[0]
            return bool, offset+1
        else:
            bools = []
            for i in range(count):
                bools.append(struct.unpack('?', self.mm[offset+i:offset+i+1])[0])
            return bools, offset+count
    
    def readInt(self, offset, count=1):
        if count == 1:
            int = struct.unpack('i', self.mm[offset:offset+4])[0]
            return int, offset+4
        else:
            ints = []
            for i in range(count):
                ints.append(struct.unpack('i', self.mm[offset+i*4:offset+i*4+4])[0])
            return ints, offset+count*4
    
    def readFloat(self, offset, count=1):
        if count == 1:
            float = struct.unpack('f', self.mm[offset:offset+4])[0]
            return float, offset+4
        else:
            floats = []
            for i in range(count):
                floats.append(struct.unpack('f', self.mm[offset+i*4:offset+i*4+4])[0])
            return floats, offset+count*4
    
    def readLong(self, offset, count=1):
        if count == 1:
            long = struct.unpack('q', self.mm[offset:offset+8])[0]
        return long, offset+8
    
    def readLongLong(self, offset, count=1):
        if count == 1:
            longlong = struct.unpack('Q', self.mm[offset:offset+8])[0]
        return longlong, offset+8
    
    def readChar(self, offset, count):
        char = ""
        newChar = ""
        for i in range(count):
            try:
                newChar = struct.unpack('s', self.mm[offset+i:offset+i+1])[0].decode("utf-8")
            except:
                newChar == "\u0000"
                
            if newChar == "\u0000":
                char += ""
            else:
                char += newChar 
            
        
        char.replace(r"\u0000", "")
        
        return char, offset+count
    
    def readDouble(self, offset, count=1):
        if count == 1:
            double = struct.unpack('d', self.mm[offset:offset+8])[0]
            return double, offset+8
        else:
            doubles = []
            for i in range(count):
                doubles.append(struct.unpack('d', self.mm[offset+i*8:offset+i*8+8])[0])
            return doubles, offset+count*8
    
    def readStringArray(self, offset, count, stringSize):
        strings = []
        for i in range(count):
            strings.append(self.readChar(offset+i*stringSize, stringSize)[0])
        return strings, offset+count*stringSize
    
    # MARK: UPDATE
    
    def update(self, trailerData=False):
        if LINUX:
            self.fd = open(mmapName)
            self.mm = mmap.mmap(self.fd.fileno(), length=0, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ)
        else:
            self.mm = mmap.mmap(0, mmapSize, mmapName)
        
        data = {}
        offset = 0
        
        # ALL COMMENTS EXTRACTED FROM https://github.com/RenCloud/scs-sdk-plugin/blob/dev/scs-telemetry/inc/scs-telemetry-common.hpp
        try:
            # MARK: ZONE 1 - 0
            # ZONE 1 -> Start at offset 0
            
            data["sdkActive"], offset = self.readBool(offset)
            data["placeHolder"], offset = self.readChar(offset, 3)
            data["pause"], offset = self.readBool(offset)
            data["placeHolder2"], offset = self.readChar(offset, 3)
            
            data["time"], offset = self.readLongLong(offset)
            data["simulatedTime"], offset = self.readLongLong(offset)
            data["renderTime"], offset = self.readLongLong(offset)
            data["multiplayerTimeOffset"], offset = self.readLongLong(offset)
            
            # END OF ZONE 1 -> Offset 40
            
            # MARK: ZONE 2 - 40
            # START OF ZONE 2 -> Offset 40
            # The Second zone contains unsigned integers and it sorted in sub structures
            
            data["scsValues"] = {}
            data["scsValues"]["telemetryPluginRevision"], offset = self.readInt(offset)
            data["scsValues"]["versionMajor"], offset = self.readInt(offset)
            data["scsValues"]["versionMinor"], offset = self.readInt(offset)
            data["scsValues"]["game"], offset = self.readGame(offset)
            data["scsValues"]["telemetryVersionGameMajor"], offset = self.readInt(offset)
            data["scsValues"]["telemetryVersionGameMinor"], offset = self.readInt(offset)
            
            data["commonUI"] = {}
            data["commonUI"]["timeAbs"], offset = self.readInt(offset)
            
            data["configUI"] = {}
            data["configUI"]["gears"], offset = self.readInt(offset)
            data["configUI"]["gearsReverse"], offset = self.readInt(offset)
            data["configUI"]["retarderStepCount"], offset = self.readInt(offset)
            data["configUI"]["truckWheelCount"], offset = self.readInt(offset)
            data["configUI"]["selectorCount"], offset = self.readInt(offset)
            data["configUI"]["timeAbsDelivery"], offset = self.readInt(offset)
            data["configUI"]["maxTrailerCount"], offset = self.readInt(offset)
            data["configUI"]["unitCount"], offset = self.readInt(offset)
            data["configUI"]["plannedDistanceKm"], offset = self.readInt(offset)
            
            data["truckUI"] = {}
            data["truckUI"]["shifterSlot"], offset = self.readInt(offset)
            data["truckUI"]["retarderBrake"], offset = self.readInt(offset)
            data["truckUI"]["lightsAuxFront"], offset = self.readInt(offset)
            data["truckUI"]["lightsAuxRoof"], offset = self.readInt(offset)
            data["truckUI"]["truckWheelSubstance"], offset = self.readInt(offset, count=16)
            data["truckUI"]["hshifterPosition"], offset = self.readInt(offset, count=32)
            data["truckUI"]["hshifterBitmask"], offset = self.readInt(offset, count=32)
            
            data["gameplayUI"] = {}
            data["gameplayUI"]["jobDeliveredDeliveryTime"], offset = self.readInt(offset)
            data["gameplayUI"]["jobStartingTime"], offset = self.readInt(offset)
            data["gameplayUI"]["jobFinishedTime"], offset = self.readInt(offset)
            
            data["bufferUI"], offset = self.readChar(offset, 48)
            
            # END OF ZONE 2 -> Offset 500
            
            # MARK: ZONE 3 - 500
            # START OF ZONE 3 -> Offset 500
            # The third zone contains integers and is sorted in sub structures
            
            data["commonInt"] = {}
            data["commonInt"]["restStop"], offset = self.readInt(offset)
            
            data["truckInt"] = {}
            data["truckInt"]["gear"], offset = self.readInt(offset)
            data["truckInt"]["gearDashboard"], offset = self.readInt(offset)
            data["truckInt"]["hshifterResulting"], offset = self.readInt(offset, count=32)
            
            data["bufferInt"], offset = self.readChar(offset, 56)
            
            # END OF ZONE 3 -> Offset 696
            
            offset += 4
            
            # MARK: ZONE 4 - 700
            # START IF ZONE 4 -> Offset 700
            # The fourth zone contains floats and is sorted in sub structures
            
            data["commonFloat"] = {}
            data["commonFloat"]["scale"], offset = self.readFloat(offset)
            
            data["configFloat"] = {}
            data["configFloat"]["fuelCapacity"], offset = self.readFloat(offset)
            data["configFloat"]["fuelWarningFactor"], offset = self.readFloat(offset)
            data["configFloat"]["adblueCapacity"], offset = self.readFloat(offset)
            data["configFloat"]["adblueWarningFactor"], offset = self.readFloat(offset)
            data["configFloat"]["airPressureWarning"], offset = self.readFloat(offset)
            data["configFloat"]["airPressureEmergency"], offset = self.readFloat(offset)
            data["configFloat"]["oilPressureWarning"], offset = self.readFloat(offset)
            data["configFloat"]["waterTemperatureWarning"], offset = self.readFloat(offset)
            data["configFloat"]["batteryVoltageWarning"], offset = self.readFloat(offset)
            data["configFloat"]["engineRpmMax"], offset = self.readFloat(offset)
            data["configFloat"]["gearDifferential"], offset = self.readFloat(offset)
            data["configFloat"]["cargoMass"], offset = self.readFloat(offset)
            data["configFloat"]["truckWheelRadius"], offset = self.readFloat(offset, count=16)
            data["configFloat"]["gearRatiosForward"], offset = self.readFloat(offset, count=24)
            data["configFloat"]["gearRatiosReverse"], offset = self.readFloat(offset, count=8)
            data["configFloat"]["unitMass"], offset = self.readFloat(offset)
            
            data["truckFloat"] = {}
            data["truckFloat"]["speed"], offset = self.readFloat(offset)
            data["truckFloat"]["engineRpm"], offset = self.readFloat(offset)
            data["truckFloat"]["userSteer"], offset = self.readFloat(offset)
            data["truckFloat"]["userThrottle"], offset = self.readFloat(offset)
            data["truckFloat"]["userBrake"], offset = self.readFloat(offset)
            data["truckFloat"]["userClutch"], offset = self.readFloat(offset)
            data["truckFloat"]["gameSteer"], offset = self.readFloat(offset)
            data["truckFloat"]["gameThrottle"], offset = self.readFloat(offset)
            data["truckFloat"]["gameBrake"], offset = self.readFloat(offset)
            data["truckFloat"]["gameClutch"], offset = self.readFloat(offset)
            data["truckFloat"]["cruiseControlSpeed"], offset = self.readFloat(offset)
            data["truckFloat"]["airPressure"], offset = self.readFloat(offset)
            data["truckFloat"]["brakeTemperature"], offset = self.readFloat(offset)
            data["truckFloat"]["fuel"], offset = self.readFloat(offset)
            data["truckFloat"]["fuelAvgConsumption"], offset = self.readFloat(offset)
            data["truckFloat"]["fuelRange"], offset = self.readFloat(offset)
            data["truckFloat"]["adblue"], offset = self.readFloat(offset)
            data["truckFloat"]["oilPressure"], offset = self.readFloat(offset)
            data["truckFloat"]["oilTemperature"], offset = self.readFloat(offset)
            data["truckFloat"]["waterTemperature"], offset = self.readFloat(offset)
            data["truckFloat"]["batteryVoltage"], offset = self.readFloat(offset)
            data["truckFloat"]["lightsDashboard"], offset = self.readFloat(offset)
            data["truckFloat"]["wearEngine"], offset = self.readFloat(offset)
            data["truckFloat"]["wearTransmission"], offset = self.readFloat(offset)
            data["truckFloat"]["wearCabin"], offset = self.readFloat(offset)
            data["truckFloat"]["wearChassis"], offset = self.readFloat(offset)
            data["truckFloat"]["wearWheels"], offset = self.readFloat(offset)
            data["truckFloat"]["truckOdometer"], offset = self.readFloat(offset)
            data["truckFloat"]["routeDistance"], offset = self.readFloat(offset)
            data["truckFloat"]["routeTime"], offset = self.readFloat(offset)
            data["truckFloat"]["speedLimit"], offset = self.readFloat(offset)
            data["truckFloat"]["truck_wheelSuspDeflection"], offset = self.readFloat(offset, count=16)
            data["truckFloat"]["truck_wheelVelocity"], offset = self.readFloat(offset, count=16)
            data["truckFloat"]["truck_wheelSteering"], offset = self.readFloat(offset, count=16)
            data["truckFloat"]["truck_wheelRotation"], offset = self.readFloat(offset, count=16)
            data["truckFloat"]["truck_wheelLift"], offset = self.readFloat(offset, count=16)
            data["truckFloat"]["truck_wheelLiftOffset"], offset = self.readFloat(offset, count=16)
            
            data["gameplayFloat"] = {}
            data["gameplayFloat"]["jobDeliveredCargoDamage"], offset = self.readFloat(offset)
            data["gameplayFloat"]["jobDeliveredDistanceKm"], offset = self.readFloat(offset)
            data["gameplayFloat"]["refuelAmount"], offset = self.readFloat(offset)
            
            data["jobFloat"] = {}
            data["jobFloat"]["cargoDamage"], offset = self.readFloat(offset)
            
            data["bufferFloat"], offset = self.readChar(offset, 28)
            
            # END OF ZONE 4 -> Offset 1500
            
            # MARK: ZONE 5 - 1500
            # START OF ZONE 5 -> Offset 1500
            # The fifth zone contains bool and is sorted in sub structures
            
            data["configBool"] = {}
            data["configBool"]["truckWheelSteerable"], offset = self.readBool(offset, count=16)
            data["configBool"]["truckWheelSimulated"], offset = self.readBool(offset, count=16)
            data["configBool"]["truckWheelPowered"], offset = self.readBool(offset, count=16)
            data["configBool"]["truckWheelLiftable"], offset = self.readBool(offset, count=16)
            data["configBool"]["isCargoLoaded"], offset = self.readBool(offset)
            data["configBool"]["specialJob"], offset = self.readBool(offset)

            data["truckBool"] = {}
            data["truckBool"]["parkBrake"], offset = self.readBool(offset)
            data["truckBool"]["motorBrake"], offset = self.readBool(offset)
            data["truckBool"]["airPressureWarning"], offset = self.readBool(offset)
            data["truckBool"]["airPressureEmergency"], offset = self.readBool(offset)
            data["truckBool"]["fuelWarning"], offset = self.readBool(offset)
            data["truckBool"]["adblueWarning"], offset = self.readBool(offset)
            data["truckBool"]["oilPressureWarning"], offset = self.readBool(offset)
            data["truckBool"]["waterTemperatureWarning"], offset = self.readBool(offset)
            data["truckBool"]["batteryVoltageWarning"], offset = self.readBool(offset)
            data["truckBool"]["electricEnabled"], offset = self.readBool(offset)
            data["truckBool"]["engineEnabled"], offset = self.readBool(offset)
            data["truckBool"]["wipers"], offset = self.readBool(offset)
            data["truckBool"]["blinkerLeftActive"], offset = self.readBool(offset)
            data["truckBool"]["blinkerRightActive"], offset = self.readBool(offset)
            data["truckBool"]["blinkerLeftOn"], offset = self.readBool(offset)
            data["truckBool"]["blinkerRightOn"], offset = self.readBool(offset)
            data["truckBool"]["lightsParking"], offset = self.readBool(offset)
            data["truckBool"]["lightsBeamLow"], offset = self.readBool(offset)
            data["truckBool"]["lightsBeamHigh"], offset = self.readBool(offset)
            data["truckBool"]["lightsBeacon"], offset = self.readBool(offset)
            data["truckBool"]["lightsBrake"], offset = self.readBool(offset)
            data["truckBool"]["lightsReverse"], offset = self.readBool(offset)
            data["truckBool"]["lightsHazard"], offset = self.readBool(offset)
            data["truckBool"]["cruiseControl"], offset = self.readBool(offset)
            data["truckBool"]["truck_wheelOnGround"], offset = self.readBool(offset, count=16)
            data["truckBool"]["shifterToggle"], offset = self.readBool(offset, count=2)
            data["truckBool"]["differentialLock"], offset = self.readBool(offset)
            data["truckBool"]["liftAxle"], offset = self.readBool(offset)
            data["truckBool"]["liftAxleIndicator"], offset = self.readBool(offset)
            data["truckBool"]["trailerLiftAxle"], offset = self.readBool(offset)
            data["truckBool"]["trailerLiftAxleIndicator"], offset = self.readBool(offset)

            data["gameplayBool"] = {}
            data["gameplayBool"]["jobDeliveredAutoparkUsed"], offset = self.readBool(offset)
            data["gameplayBool"]["jobDeliveredAutoloadUsed"], offset = self.readBool(offset)

            data["bufferBool"], offset = self.readChar(offset, count=25)
            
            # END OF ZONE 5 -> Offset 1640
            
            # MARK: ZONE 6 - 1640
            # START OF ZONE 6 -> Offset 1640
            # The sixth zone contains fvector and is sorted in sub structures
            
            data["configVector"] = {}
            data["configVector"]["cabinPositionX"], offset = self.readFloat(offset)
            data["configVector"]["cabinPositionY"], offset = self.readFloat(offset)
            data["configVector"]["cabinPositionZ"], offset = self.readFloat(offset)
            data["configVector"]["headPositionX"], offset = self.readFloat(offset)
            data["configVector"]["headPositionY"], offset = self.readFloat(offset)
            data["configVector"]["headPositionZ"], offset = self.readFloat(offset)
            data["configVector"]["truckHookPositionX"], offset = self.readFloat(offset)
            data["configVector"]["truckHookPositionY"], offset = self.readFloat(offset)
            data["configVector"]["truckHookPositionZ"], offset = self.readFloat(offset)
            data["configVector"]["truckWheelPositionX"], offset = self.readFloat(offset, count=16)
            data["configVector"]["truckWheelPositionY"], offset = self.readFloat(offset, count=16)
            data["configVector"]["truckWheelPositionZ"], offset = self.readFloat(offset, count=16)

            data["truckVector"] = {}
            data["truckVector"]["lv_accelerationX"], offset = self.readFloat(offset)
            data["truckVector"]["lv_accelerationY"], offset = self.readFloat(offset)
            data["truckVector"]["lv_accelerationZ"], offset = self.readFloat(offset)
            data["truckVector"]["av_accelerationX"], offset = self.readFloat(offset)
            data["truckVector"]["av_accelerationY"], offset = self.readFloat(offset)
            data["truckVector"]["av_accelerationZ"], offset = self.readFloat(offset)
            data["truckVector"]["accelerationX"], offset = self.readFloat(offset)
            data["truckVector"]["accelerationY"], offset = self.readFloat(offset)
            data["truckVector"]["accelerationZ"], offset = self.readFloat(offset)
            data["truckVector"]["aa_accelerationX"], offset = self.readFloat(offset)
            data["truckVector"]["aa_accelerationY"], offset = self.readFloat(offset)
            data["truckVector"]["aa_accelerationZ"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAVX"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAVY"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAVZ"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAAX"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAAY"], offset = self.readFloat(offset)
            data["truckVector"]["cabinAAZ"], offset = self.readFloat(offset)

            data["bufferVector"], offset = self.readChar(offset, count=60)
            
            # END OF ZONE 6 -> Offset 2000
            
            # MARK: ZONE 7 - 2000
            # START OF ZONE 7 -> Offset 2000
            # The 7th zone contains fplacement and is sorted in sub structures
            data["headPlacement"] = {}
            data["headPlacement"]["cabinOffsetX"], offset = self.readFloat(offset)
            data["headPlacement"]["cabinOffsetY"], offset = self.readFloat(offset)
            data["headPlacement"]["cabinOffsetZ"], offset = self.readFloat(offset)
            data["headPlacement"]["cabinOffsetrotationX"], offset = self.readFloat(offset)
            data["headPlacement"]["cabinOffsetrotationY"], offset = self.readFloat(offset)
            data["headPlacement"]["cabinOffsetrotationZ"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetX"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetY"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetZ"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetrotationX"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetrotationY"], offset = self.readFloat(offset)
            data["headPlacement"]["headOffsetrotationZ"], offset = self.readFloat(offset)

            data["bufferHeadPlacement"], offset = self.readChar(offset, count=152)
            
            # END OF ZONE 7 -> Offset 2200
            
            # MARK: ZONE 8 - 2200
            # START OF ZONE 8 -> Offset 2200
            
            data["truckPlacement"] = {}
            data["truckPlacement"]["coordinateX"], offset = self.readDouble(offset)
            data["truckPlacement"]["coordinateY"], offset = self.readDouble(offset)
            data["truckPlacement"]["coordinateZ"], offset = self.readDouble(offset)
            data["truckPlacement"]["rotationX"], offset = self.readDouble(offset)
            data["truckPlacement"]["rotationY"], offset = self.readDouble(offset)
            data["truckPlacement"]["rotationZ"], offset = self.readDouble(offset)

            data["bufferTruckPlacement"], offset = self.readChar(offset, count=52)
            
            # END OF ZONE 8 -> Offset 2300
            
            # MARK: ZONE 9 - 2300
            # START OF ZONE 9 -> Offset 2300
            # The 9th zone contains strings and is sorted in sub structures
            
            data["configString"] = {}
            data["configString"]["truckBrandId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["truckBrand"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["truckId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["truckName"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["cargoId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["cargo"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["cityDstId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["cityDst"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["compDstId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["compDst"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["citySrcId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["citySrc"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["compSrcId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["compSrc"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["shifterType"], offset = self.readChar(offset, count=16)
            data["configString"]["truckLicensePlate"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["truckLicensePlateCountryId"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["truckLicensePlateCountry"], offset = self.readChar(offset, count=stringSize)
            data["configString"]["jobMarket"], offset = self.readChar(offset, count=32)

            data["gameplayString"] = {}
            data["gameplayString"]["fineOffence"], offset = self.readChar(offset, count=32)
            data["gameplayString"]["ferrySourceName"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["ferryTargetName"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["ferrySourceId"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["ferryTargetId"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["trainSourceName"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["trainTargetName"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["trainSourceId"], offset = self.readChar(offset, count=stringSize)
            data["gameplayString"]["trainTargetId"], offset = self.readChar(offset, count=stringSize)

            data["bufferString"], offset = self.readChar(offset, count=20)
            
            # END OF ZONE 9 -> Offset 4000
            
            # MARK: ZONE 10 - 4000
            # START OF ZONE 10 -> Offset 4000
            # The 10th zone contains unsigned long long and is sorted in sub structures
            
            data["configLongLong"] = {}
            data["configLongLong"]["jobIncome"], offset = self.readLongLong(offset)
            
            data["bufferLongLong"], offset = self.readChar(offset, count=192)
            
            # END OF ZONE 10 -> Offset 4200
            
            # MARK: ZONE 11 - 4200
            # START OF ZONE 11 -> Offset 4200
            # The 11th zone contains long long and is sorted in sub structures
            
            data["gameplayLongLong"] = {}
            data["gameplayLongLong"]["jobCancelledPenalty"], offset = self.readLongLong(offset)
            data["gameplayLongLong"]["jobDeliveredRevenue"], offset = self.readLongLong(offset)
            data["gameplayLongLong"]["fineAmount"], offset = self.readLongLong(offset)
            data["gameplayLongLong"]["tollgatePayAmount"], offset = self.readLongLong(offset)
            data["gameplayLongLong"]["ferryPayAmount"], offset = self.readLongLong(offset)
            data["gameplayLongLong"]["trainPayAmount"], offset = self.readLongLong(offset)

            data["bufferLongLong"], offset = self.readChar(offset, count=52)
            
            # END OF ZONE 11 -> Offset 4300
            
            # MARK: ZONE 12 - 4300
            # START OF ZONE 12 -> Offset 4300
            # The 12th zone contains special events and is sorted in sub structures
            
            data["specialBool"] = {}
            data["specialBool"]["onJob"], offset = self.readBool(offset)
            data["specialBool"]["jobFinished"], offset = self.readBool(offset)
            data["specialBool"]["jobCancelled"], offset = self.readBool(offset)
            data["specialBool"]["jobDelivered"], offset = self.readBool(offset)
            data["specialBool"]["fined"], offset = self.readBool(offset)
            data["specialBool"]["tollgate"], offset = self.readBool(offset)
            data["specialBool"]["ferry"], offset = self.readBool(offset)
            data["specialBool"]["train"], offset = self.readBool(offset)
            data["specialBool"]["refuel"], offset = self.readBool(offset)
            data["specialBool"]["refuelPayed"], offset = self.readBool(offset)

            data["bufferSpecial"], offset = self.readChar(offset, count=90)
            
            # END OF ZONE 12 -> Offset 4400
            
            # MARK: ZONE 13 - 4400
            # START OF ZONE 13 -> Offset 4400
            
            data["substances"], offset = self.readStringArray(offset, count=substanceSize, stringSize=stringSize)
            
            # END OF ZONE 13 -> Offset 6000
            
            # MARK: ZONE 14 - 6000
            # START OF ZONE 14 -> Offset 6000
            if trailerData:
                data["trailers"], offset = self.readTrailer(offset, count=10)
        
        except Exception as e:
            print(e)
            try:
                print("Current offset : " + offset)
            except:
                pass
        
        self.mm.close()
        
        return data
           