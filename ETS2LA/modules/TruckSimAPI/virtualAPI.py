import mmap
import struct
import keyboard

# https://github.com/RenCloud/scs-sdk-plugin/blob/dev/scs-telemetry/inc/scs-telemetry-common.hpp

mmapName = "Local\SCSTelemetry"
mmapSize = 32*1024

stringSize = 64
wheelSize = 14
substanceSize = 25

# Germany
# virtualX = 1710
# virtualZ = 7500

# France
# virtualX = -27700
# virtualZ = 36200

# S[pain]
# virtualX = -36945
# virtualZ = 47590

# Italy
# virtualX = -3500
# virtualZ = 37535

# Balkans
# virtualX = 30900
# virtualZ = 25650

# Sweden
# virtualX = 22600
# virtualZ = -45480

# Baltics
# virtualX = 44000
# virtualZ = -49200

# Working Set (not a specific location)
virtualX = 21275
virtualZ = -48710

class scsTelemetry:
    
    # VARIABLE READING
    
    def readGame(self, offset):
        int = 3
        if int == 1:
            return "ETS2", offset+4
        elif int == 2:
            return "ATS", offset+4
        else:
            return "unknown", offset+4
    
    # SPECIAL READING
    
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
            data["comDouble"]["worldX"] = virtualX   # Duisburg
            offset += 8
            data["comDouble"]["worldY"], offset = self.readDouble(offset)
            data["comDouble"]["worldZ"] = virtualZ
            offset += 8
            data["comDouble"]["rotationX"] = 0
            data["comDouble"]["rotationY"] = 0
            data["comDouble"]["rotationZ"] = 0
            offset += 24
            
            # END OF FIFTH ZONE -> Offset 920
            
            # START OF SIXTH ZONE -> Offset 920
            
            data["conString"] = {}
            data["conString"]["id"], offset = self.readChar(offset, count=stringSize)
            data["conString"]["cargoAcessoryId"], offset = self.readChar(offset, count=stringSize)
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
            
    
    # VALUE READING
    
    def readBool(self, offset, count=1):
        if count == 1:
            bool = False
            return bool, offset+1
        else:
            bools = []
            for i in range(count):
                bools.append(False)
            return bools, offset+count
            
    
    def readInt(self, offset, count=1):
        if count == 1:
            int = 0
            return int, offset+4
        else:
            ints = []
            for i in range(count):
                ints.append(0)
            return ints, offset+count*4
    
    def readFloat(self, offset, count=1):
        if count == 1:
            float = 1.111
            return float, offset+4
        else:
            floats = []
            for i in range(count):
                floats.append(1.111)
            return floats, offset+count*4
    
    def readLong(self, offset, count=1):
        if count == 1:
            long = 1
        return long, offset+8
    
    def readLongLong(self, offset, count=1):
        if count == 1:
            longlong = 1
        return longlong, offset+8
    
    def readChar(self, offset, count):
        char = " "
        for i in range(count):
            char += " "
        
        return char, offset+count
    
    def readDouble(self, offset, count=1):
        if count == 1:
            double = 1
            return double, offset+8
        else:
            doubles = []
            for i in range(count):
                doubles.append(1)
            return doubles, offset+count*8
    
    def readStringArray(self, offset, count, stringSize):
        strings = []
        for i in range(count):
            strings.append(self.readChar(offset+i*stringSize, stringSize)[0])
        return strings, offset+count*stringSize
    
    def update(self, trailerData=False):
        global virtualX, virtualZ
        data = {}
        offset = 0
        
        speed = 5
        if keyboard.is_pressed("shift"):
            speed = 15
        
        # Use the arrowkeys to move the virtual truck
        if keyboard.is_pressed("up"):
            virtualZ -= speed
        if keyboard.is_pressed("down"):
            virtualZ += speed
        if keyboard.is_pressed("left"):
            virtualX -= speed
        if keyboard.is_pressed("right"):
            virtualX += speed
        
        # ALL COMMENTS EXTRACTED FROM https://github.com/RenCloud/scs-sdk-plugin/blob/dev/scs-telemetry/inc/scs-telemetry-common.hpp
        try:
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
            
            # START OF ZONE 8 -> Offset 2200
            
            data["truckPlacement"] = {}
            data["truckPlacement"]["coordinateX"] = virtualX    # Duisburg
            offset = offset + 8
            data["truckPlacement"]["coordinateY"], offset = self.readDouble(offset)
            data["truckPlacement"]["coordinateZ"] = virtualZ    # Duisburg
            offset = offset + 8
            data["truckPlacement"]["rotationX"], offset = self.readDouble(offset)
            data["truckPlacement"]["rotationY"], offset = self.readDouble(offset)
            data["truckPlacement"]["rotationZ"], offset = self.readDouble(offset)

            data["bufferTruckPlacement"], offset = self.readChar(offset, count=52)
            
            # END OF ZONE 8 -> Offset 2300
            
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
            
            # START OF ZONE 10 -> Offset 4000
            # The 10th zone contains unsigned long long and is sorted in sub structures
            
            data["configLongLong"] = {}
            data["configLongLong"]["jobIncome"], offset = self.readLongLong(offset)
            
            data["bufferLongLong"], offset = self.readChar(offset, count=192)
            
            # END OF ZONE 10 -> Offset 4200
            
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
            
            # START OF ZONE 13 -> Offset 4400
            
            data["substances"], offset = self.readStringArray(offset, count=substanceSize, stringSize=stringSize)
            
            # END OF ZONE 13 -> Offset 6000
            
            # START OF ZONE 14 -> Offset 6000
            if trailerData:
                data["trailers"], offset = self.readTrailer(offset, count=10)
        
        except Exception as e:
            print(e)
            try:
                print("Current offset : " + offset)
            except:
                pass
        
        return data
           