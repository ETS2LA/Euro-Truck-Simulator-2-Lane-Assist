#pragma warning disable CA1416 // We check OS compatibility.
using System.IO.MemoryMappedFiles;
using ETS2LA.Shared;
using ETS2LA.UI.Notifications;
using ETS2LA.Logging;
using System.Numerics;

namespace GameTelemetry
{
    public class GameTelemetry : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Game Telemetry",
            Description = "This plugin reads game telemetry from ETS2/ATS and publishes it to the event bus.",
            AuthorName = "Tumppi066",
        };

        // Read game telemetry at 60FPS
        public override float TickRate => 60f;

        MemoryReader? _reader;

        string mmapName = "Local\\SCSTelemetry";
        int mmapSize = 32 * 1024;
        
        int stringSize = 64;

        Dictionary<int, string> intToDays = new Dictionary<int, string>
        {
            { 0, "Monday" },
            { 1, "Tuesday" },
            { 2, "Wednesday" },
            { 3, "Thursday" },
            { 4, "Friday" },
            { 5, "Saturday" },
            { 6, "Sunday" }
        };

        string AbsoluteToReadableTime(int absTime)
        {
            var days = absTime / 1440;
            if (days > 6)
                days %= 7;

            var hours = absTime / 60;
            if (hours > 23)
                hours %= 24;

            var minutes = absTime % 60;

            return $"{intToDays[days]} {hours:D2}:{minutes:D2}";
        }

        string ReadGame(int offset, byte[] data)
        {
            if (offset + 4 > data.Length)
                throw new ArgumentOutOfRangeException(nameof(offset), "Offset exceeds data length.");
        
            int game = BitConverter.ToInt32(data, offset);
            string gameName = game switch
            {
                1 => "ETS2",
                2 => "ATS",
                _ => "unknown"
            };
        
            return gameName;
        }

        public override void Init()
        {
            base.Init();
            Logger.Info("Game Telemetry plugin initialized.");
        }

        public override void OnDisable()
        {
            base.OnDisable();
            NotificationHandler.Instance.CloseNotification("GameTelemetry.MMFNotFound");
        }

        public override void Tick()
        {
            if (_bus == null)
                return;
                
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            byte[] buffer = new byte[mmapSize];
            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                NotificationHandler.Instance.SendNotification(new Notification
                {
                    Id = "GameTelemetry.MMFNotFound",
                    Title = "Game Telemetry",
                    Content = $"Couldn't connect to the game. Please open ETS2 or ATS and enable the SDK.",
                    IsProgressIndeterminate = true,
                });
                Thread.Sleep(1000);
                _reader = null;
                return;
            }
            catch (Exception)
            {
                Thread.Sleep(1000);
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }

            if (_reader == null)
            {
                Logger.Debug("Memory reader is null, skipping telemetry read.");
                return;
            }

            NotificationHandler.Instance.CloseNotification("GameTelemetry.MMFNotFound");

            int offset = 0;
            GameTelemetryData telemetry = new GameTelemetryData();

            // Root Values
            telemetry.sdkActive = _reader.ReadBool(offset); offset += 1;
            offset += 3; // Padding
            telemetry.paused = _reader.ReadBool(offset); offset += 1;
            offset += 3; // Padding

            telemetry.time = _reader.ReadLongLong(offset); offset += 8;
            telemetry.simulatedTime = _reader.ReadLongLong(offset); offset += 8;
            telemetry.renderTime = _reader.ReadLongLong(offset); offset += 8;
            telemetry.multiplayerTimeOffset = _reader.ReadLongLong(offset); offset += 8;

            // SCSValues
            telemetry.scsValues.telemetryPluginRevision = _reader.ReadInt(offset); offset += 4;
            telemetry.scsValues.versionMajor = _reader.ReadInt(offset); offset += 4;
            telemetry.scsValues.versionMinor = _reader.ReadInt(offset); offset += 4;
            telemetry.scsValues.game = ReadGame(offset, buffer); offset += 4;
            telemetry.scsValues.telemetryVersionGameMajor = _reader.ReadInt(offset); offset += 4;
            telemetry.scsValues.telemetryVersionGameMinor = _reader.ReadInt(offset); offset += 4;

            // CommonUI
            telemetry.commonUI.timeAbsolute = _reader.ReadInt(offset); offset += 4;
            telemetry.commonUI.timeReadable = AbsoluteToReadableTime(telemetry.commonUI.timeAbsolute);

            // ConfigUI
            telemetry.configUI.gears = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.gearsReverse = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.retarderStepCount = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.truckWheelCount = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.selectorCount = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.timeAbsDelivery = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.maxTrailerCount = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.unitCount = _reader.ReadInt(offset); offset += 4;
            telemetry.configUI.plannedDistanceKm = _reader.ReadInt(offset); offset += 4;

            // TruckUI
            telemetry.truckUI.shifterSlot = _reader.ReadInt(offset); offset += 4;
            telemetry.truckUI.retarderBrake = _reader.ReadInt(offset); offset += 4;
            telemetry.truckUI.lightsAuxFront = _reader.ReadInt(offset); offset += 4;
            telemetry.truckUI.lightsAuxRoof = _reader.ReadInt(offset); offset += 4;
            telemetry.truckUI.truckWheelSubstance = _reader.ReadInt(offset, 16); offset += 16 * 4;
            telemetry.truckUI.hshifterPosition = _reader.ReadInt(offset, 32); offset += 32 * 4;
            telemetry.truckUI.hshifterBitmask = _reader.ReadInt(offset, 32); offset += 32 * 4;

            // GameplayUI
            telemetry.gameplayUI.jobDeliveredDeliveryTime = _reader.ReadInt(offset); offset += 4;
            telemetry.gameplayUI.jobFinishedTime = _reader.ReadInt(offset); offset += 4;
            telemetry.gameplayUI.jobStartingTime = _reader.ReadInt(offset); offset += 4;
            offset += 48; // Padding

            // CommonInt
            telemetry.commonInt.restStop = _reader.ReadInt(offset); offset += 4;

            // TruckInt
            telemetry.truckInt.gear = _reader.ReadInt(offset); offset += 4;
            telemetry.truckInt.gearDashboard = _reader.ReadInt(offset); offset += 4;
            telemetry.truckInt.hshifterResultingGear = _reader.ReadInt(offset, 32); offset += 32 * 4;
            offset += 56; // Padding
            offset += 4;  // Padding

            // CommonFloat
            telemetry.commonFloat.scale = _reader.ReadFloat(offset); offset += 4;

            // ConfigFloat
            telemetry.configFloat.fuelCapacity = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.fuelWarningFactor = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.adblueCapacity = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.adblueWarningFactor = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.airPressureWarning = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.airPressureEmergency = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.oilPressureWarning = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.waterTemperatureWarning = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.batteryVoltageWarning = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.engineRpmMax = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.gearDifferential = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.cargoMass = _reader.ReadFloat(offset); offset += 4;
            telemetry.configFloat.truckWheelRadius = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.configFloat.gearRatiosForward = _reader.ReadFloat(offset, 24); offset += 24 * 4;
            telemetry.configFloat.gearRatiosReverse = _reader.ReadFloat(offset, 8); offset += 8 * 4;
            telemetry.configFloat.unitMass = _reader.ReadFloat(offset); offset += 4;

            // TruckFloat
            telemetry.truckFloat.speed = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.engineRpm = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.userSteer = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.userThrottle = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.userBrake = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.userClutch = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.gameSteer = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.gameThrottle = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.gameBrake = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.gameClutch = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.cruiseControlSpeed = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.airPressure = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.brakeTemperature = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.fuel = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.fuelAvgConsumption = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.fuelRange = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.adblue = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.oilPressure = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.oilTemperature = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.waterTemperature = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.batteryVoltage = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.lightsDashboard = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.wearEngine = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.wearTransmission = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.wearCabin = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.wearChassis = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.wearWheels = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.truckOdometer = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.routeDistance = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.routeTime = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.speedLimit = _reader.ReadFloat(offset); offset += 4;
            telemetry.truckFloat.truckWheelSuspDeflection = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.truckFloat.truckWheelVelocity = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.truckFloat.truckWheelSteering = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.truckFloat.truckWheelRotation = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.truckFloat.truckWheelLift = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            telemetry.truckFloat.truckWheelLiftOffset = _reader.ReadFloat(offset, 16); offset += 16 * 4;

            // GameplayFloat
            telemetry.gameplayFloat.jobDeliveredCargoDamage = _reader.ReadFloat(offset); offset += 4;
            telemetry.gameplayFloat.jobDeliveredDistanceKm = _reader.ReadFloat(offset); offset += 4;
            telemetry.gameplayFloat.refuelAmount = _reader.ReadFloat(offset); offset += 4;

            // JobFloat
            telemetry.jobFloat.cargoDamage = _reader.ReadFloat(offset); offset += 4;
            offset += 28; // Padding

            // ConfigBool
            telemetry.configBool.truckWheelSteerable = _reader.ReadBool(offset, 16); offset += 16 * 1;
            telemetry.configBool.truckWheelSimulated = _reader.ReadBool(offset, 16); offset += 16 * 1;
            telemetry.configBool.truckWheelPowered = _reader.ReadBool(offset, 16); offset += 16 * 1;
            telemetry.configBool.truckWheelLiftable = _reader.ReadBool(offset, 16); offset += 16 * 1;
            telemetry.configBool.isCargoLoaded = _reader.ReadBool(offset); offset += 1;
            telemetry.configBool.specialJob = _reader.ReadBool(offset); offset += 1;

            // TruckBool
            telemetry.truckBool.parkingBrake = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.motorBrake = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.airPressureWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.airPressureEmergency = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.fuelWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.adblueWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.oilPressureWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.waterTemperatureWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.batteryVoltageWarning = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.electricEnabled = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.engineEnabled = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.wipers = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.blinkerLeftActive = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.blinkerRightActive = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.blinkerLeftOn = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.blinkerRightOn = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsParking = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsBeamLow = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsBeamHigh = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsBeacon = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsBrake = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsReverse = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.lightsHazard = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.cruiseControl = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.truckWheelOnGround = _reader.ReadBool(offset, 16); offset += 16 * 1;
            telemetry.truckBool.shifterToggle = _reader.ReadBool(offset, 2); offset += 2 * 1;
            telemetry.truckBool.differentialLock = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.liftAxle = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.liftAxleIndicator = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.trailerLiftAxle = _reader.ReadBool(offset); offset += 1;
            telemetry.truckBool.trailerLiftAxleIndicator = _reader.ReadBool(offset); offset += 1;

            // GameplayBool
            telemetry.gameplayBool.jobDeliveredAutoparkUsed = _reader.ReadBool(offset); offset += 1;
            telemetry.gameplayBool.jobDeliveredAutoloadUsed = _reader.ReadBool(offset); offset += 1;
            offset += 25; // Padding

            // ConfigVector
            telemetry.configVector.cabinPosition = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.configVector.headPosition = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.configVector.truckHookPosition = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.configVector.truckWheelPositions = new Vector3[16];
            float[] wheelX = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            float[] wheelY = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            float[] wheelZ = _reader.ReadFloat(offset, 16); offset += 16 * 4;
            for (int i = 0; i < 16; i++)
            {
                telemetry.configVector.truckWheelPositions[i] = new Vector3(
                    wheelX[i],
                    wheelY[i],
                    wheelZ[i]
                );
            }

            // TruckVector
            telemetry.truckVector.linearVelocityAcceleration = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.truckVector.angularVelocityAcceleration = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.truckVector.acceleration = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.truckVector.angularRotationAcceleration = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.truckVector.cabinAngularVelocity = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.truckVector.cabinAngularAcceleration = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            offset += 60; // Padding

            // HeadPlacement
            telemetry.headPlacement.cabinOffset = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.headPlacement.cabinOffsetRotation = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.headPlacement.headOffset = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            telemetry.headPlacement.headOffsetRotation = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            offset += 152; // Padding


            // TruckPlacement
            telemetry.truckPlacement.coordinate = new Vector3Double(
                _reader.ReadDouble(offset),
                _reader.ReadDouble(offset + 8),
                _reader.ReadDouble(offset + 16)
            ); offset += 24;
            telemetry.truckPlacement.rotation = new Vector3Double(
                _reader.ReadDouble(offset),
                _reader.ReadDouble(offset + 8),
                _reader.ReadDouble(offset + 16)
            ); offset += 24;
            offset += 52; // Padding

            // ConfigString
            telemetry.configString.truckBrandId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.truckBrand = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.truckId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.truckName = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.cargoId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.cargo = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.cityDstId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.cityDst = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.compDstId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.compDst = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.citySrcId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.citySrc = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.compSrcId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.compSrc = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.shifterType = _reader.ReadChar(offset, 16); offset += 16;
            telemetry.configString.truckLicensePlate = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.truckLicensePlateCountryId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.truckLicensePlateCountry = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.configString.jobMarket = _reader.ReadChar(offset, 32); offset += 32;

            // GameplayString
            telemetry.gameplayString.fineOffence = _reader.ReadChar(offset, 32); offset += 32;
            telemetry.gameplayString.ferrySourceName = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.ferryTargetName = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.ferrySourceId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.ferryTargetId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.trainSourceName = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.trainTargetName = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.trainSourceId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            telemetry.gameplayString.trainTargetId = _reader.ReadChar(offset, stringSize); offset += stringSize;
            offset += 20; // Padding

            // ConfigLongLong
            telemetry.configLongLong.jobIncome = _reader.ReadLongLong(offset); offset += 8;
            offset += 192; // Padding

            // GameplayLongLong
            telemetry.gameplayLongLong.jobCancelledPenalty = _reader.ReadLongLong(offset); offset += 8;
            telemetry.gameplayLongLong.jobDeliveredRevenue = _reader.ReadLongLong(offset); offset += 8;
            telemetry.gameplayLongLong.fineAmount = _reader.ReadLongLong(offset); offset += 8;
            telemetry.gameplayLongLong.tollgatePayAmount = _reader.ReadLongLong(offset); offset += 8;
            telemetry.gameplayLongLong.ferryPayAmount = _reader.ReadLongLong(offset); offset += 8;
            telemetry.gameplayLongLong.trainPayAmount = _reader.ReadLongLong(offset); offset += 8;
            offset += 52;

            // SpecialBool
            telemetry.specialBool.onJob = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.jobFinished = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.jobCancelled = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.jobDelivered = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.fined = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.tollgate = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.ferry = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.train = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.refuel = _reader.ReadBool(offset); offset += 1;
            telemetry.specialBool.refuelPaid = _reader.ReadBool(offset); offset += 1;
            offset += 90;

            // Publish to the event bus
            _bus.Publish<GameTelemetryData>("GameTelemetry.Data", telemetry);
        }
    }
}