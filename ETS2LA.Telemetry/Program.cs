using ETS2LA.Shared;
using ETS2LA.Backend.Events;
using ETS2LA.Notifications;
using ETS2LA.Logging;

using System.IO.MemoryMappedFiles;
using System.Numerics;
using System.Diagnostics;

namespace ETS2LA.Telemetry;

public class GameTelemetry
{
    private static readonly Lazy<GameTelemetry> _instance = new(() => new GameTelemetry());
    public static GameTelemetry Current => _instance.Value;

    // There's no reason to *increase* this value as the game
    // only reports at a max of 60Hz anyway, but you can decrease it
    // if you really want to. Note that it will affect most ETS2LA
    // features, so be careful.
    // 1f / 60f -> 16.66ms (60Hz)
    // 1/30 -> 33.33ms (30Hz)
    // etc...
    private float UpdateRate { get; set; } = 1f / 60f;

    public string EventString = "ETS2LA.Telemetry.Data";
    
    private MemoryReader? _reader;
    private GameTelemetryData? _currentData = new();
    

    string mmapName = "Local\\SCSTelemetry";
    string mmapNameLinux = "/dev/shm/SCSTelemetry";

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

    private string AbsoluteToReadableTime(int absTime)
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

    private string ReadGame(int offset, byte[] data)
    {
        int game = BitConverter.ToInt32(data, offset);
        string gameName = game switch
        {
            1 => "ETS2",
            2 => "ATS",
            _ => "unknown"
        };
    
        return gameName;
    }

    public GameTelemetry()
    {
        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public GameTelemetryData GetCurrentData()
    {
        if (_currentData == null)
            _currentData = new();
        
        return _currentData;
    }

    private void UpdateThread()
    {
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        while (true)
        {
            int timeLeft = (int)((UpdateRate * 1000) - stopwatch.Elapsed.TotalMilliseconds);
            if (timeLeft > 0)
            {
                Thread.Sleep(timeLeft);
                continue;
            }

            stopwatch.Restart();
            try { Update(); }
            catch (Exception ex)
            {
                Logger.Error(ex.ToString(), "Error in telemetry update loop.");
            }
        }
    }

    private void Update()
    {
        if (_currentData == null)
            _currentData = new();
        
        MemoryMappedFile? mmf = null;
        MemoryMappedViewAccessor? accessor = null;
        byte[] buffer = new byte[mmapSize];

        try
        {
            #if WINDOWS
                mmf = MemoryMappedFile.OpenExisting(mmapName);
            # else
                mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
            # endif
            
            accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
            accessor.ReadArray(0, buffer, 0, mmapSize);
            _reader = new MemoryReader(buffer);
        }
        catch (FileNotFoundException)
        {
            _currentData.sdkActive = false;
            NotificationHandler.Current.SendNotification(new Notification
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
            Logging.Logger.Debug("Memory reader is null, skipping telemetry read.");
            return;
        }

        NotificationHandler.Current.CloseNotification("GameTelemetry.MMFNotFound");

        int offset = 0;

        // Root Values
        _currentData.sdkActive = _reader.ReadBool(offset); offset += 1;
        offset += 3; // Padding
        _currentData.paused = _reader.ReadBool(offset); offset += 1;
        offset += 3; // Padding

        _currentData.time = _reader.ReadLongLong(offset); offset += 8;
        _currentData.simulatedTime = _reader.ReadLongLong(offset); offset += 8;
        _currentData.renderTime = _reader.ReadLongLong(offset); offset += 8;
        _currentData.multiplayerTimeOffset = _reader.ReadLongLong(offset); offset += 8;

        // SCSValues
        _currentData.scsValues.telemetryPluginRevision = _reader.ReadInt(offset); offset += 4;
        _currentData.scsValues.versionMajor = _reader.ReadInt(offset); offset += 4;
        _currentData.scsValues.versionMinor = _reader.ReadInt(offset); offset += 4;
        _currentData.scsValues.game = ReadGame(offset, buffer); offset += 4;
        _currentData.scsValues.telemetryVersionGameMajor = _reader.ReadInt(offset); offset += 4;
        _currentData.scsValues.telemetryVersionGameMinor = _reader.ReadInt(offset); offset += 4;

        // CommonUI
        _currentData.commonUI.timeAbsolute = _reader.ReadInt(offset); offset += 4;
        _currentData.commonUI.timeReadable = AbsoluteToReadableTime(_currentData.commonUI.timeAbsolute);

        // ConfigUI
        _currentData.configUI.gears = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.gearsReverse = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.retarderStepCount = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.truckWheelCount = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.selectorCount = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.timeAbsDelivery = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.maxTrailerCount = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.unitCount = _reader.ReadInt(offset); offset += 4;
        _currentData.configUI.plannedDistanceKm = _reader.ReadInt(offset); offset += 4;

        // TruckUI
        _currentData.truckUI.shifterSlot = _reader.ReadInt(offset); offset += 4;
        _currentData.truckUI.retarderBrake = _reader.ReadInt(offset); offset += 4;
        _currentData.truckUI.lightsAuxFront = _reader.ReadInt(offset); offset += 4;
        _currentData.truckUI.lightsAuxRoof = _reader.ReadInt(offset); offset += 4;
        _currentData.truckUI.truckWheelSubstance = _reader.ReadInt(offset, 16); offset += 16 * 4;
        _currentData.truckUI.hshifterPosition = _reader.ReadInt(offset, 32); offset += 32 * 4;
        _currentData.truckUI.hshifterBitmask = _reader.ReadInt(offset, 32); offset += 32 * 4;

        // GameplayUI
        _currentData.gameplayUI.jobDeliveredDeliveryTime = _reader.ReadInt(offset); offset += 4;
        _currentData.gameplayUI.jobFinishedTime = _reader.ReadInt(offset); offset += 4;
        _currentData.gameplayUI.jobStartingTime = _reader.ReadInt(offset); offset += 4;
        offset += 48; // Padding

        // CommonInt
        _currentData.commonInt.restStop = _reader.ReadInt(offset); offset += 4;

        // TruckInt
        _currentData.truckInt.gear = _reader.ReadInt(offset); offset += 4;
        _currentData.truckInt.gearDashboard = _reader.ReadInt(offset); offset += 4;
        _currentData.truckInt.hshifterResultingGear = _reader.ReadInt(offset, 32); offset += 32 * 4;
        offset += 56; // Padding
        offset += 4;  // Padding

        // CommonFloat
        _currentData.commonFloat.scale = _reader.ReadFloat(offset); offset += 4;

        // ConfigFloat
        _currentData.configFloat.fuelCapacity = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.fuelWarningFactor = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.adblueCapacity = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.adblueWarningFactor = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.airPressureWarning = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.airPressureEmergency = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.oilPressureWarning = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.waterTemperatureWarning = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.batteryVoltageWarning = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.engineRpmMax = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.gearDifferential = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.cargoMass = _reader.ReadFloat(offset); offset += 4;
        _currentData.configFloat.truckWheelRadius = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.configFloat.gearRatiosForward = _reader.ReadFloat(offset, 24); offset += 24 * 4;
        _currentData.configFloat.gearRatiosReverse = _reader.ReadFloat(offset, 8); offset += 8 * 4;
        _currentData.configFloat.unitMass = _reader.ReadFloat(offset); offset += 4;

        // TruckFloat
        _currentData.truckFloat.speed = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.engineRpm = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.userSteer = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.userThrottle = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.userBrake = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.userClutch = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.gameSteer = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.gameThrottle = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.gameBrake = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.gameClutch = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.cruiseControlSpeed = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.airPressure = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.brakeTemperature = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.fuel = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.fuelAvgConsumption = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.fuelRange = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.adblue = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.oilPressure = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.oilTemperature = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.waterTemperature = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.batteryVoltage = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.lightsDashboard = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.wearEngine = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.wearTransmission = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.wearCabin = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.wearChassis = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.wearWheels = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.truckOdometer = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.routeDistance = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.routeTime = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.speedLimit = _reader.ReadFloat(offset); offset += 4;
        _currentData.truckFloat.truckWheelSuspDeflection = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.truckFloat.truckWheelVelocity = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.truckFloat.truckWheelSteering = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.truckFloat.truckWheelRotation = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.truckFloat.truckWheelLift = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        _currentData.truckFloat.truckWheelLiftOffset = _reader.ReadFloat(offset, 16); offset += 16 * 4;

        // GameplayFloat
        _currentData.gameplayFloat.jobDeliveredCargoDamage = _reader.ReadFloat(offset); offset += 4;
        _currentData.gameplayFloat.jobDeliveredDistanceKm = _reader.ReadFloat(offset); offset += 4;
        _currentData.gameplayFloat.refuelAmount = _reader.ReadFloat(offset); offset += 4;

        // JobFloat
        _currentData.jobFloat.cargoDamage = _reader.ReadFloat(offset); offset += 4;
        offset += 28; // Padding

        // ConfigBool
        _currentData.configBool.truckWheelSteerable = _reader.ReadBool(offset, 16); offset += 16 * 1;
        _currentData.configBool.truckWheelSimulated = _reader.ReadBool(offset, 16); offset += 16 * 1;
        _currentData.configBool.truckWheelPowered = _reader.ReadBool(offset, 16); offset += 16 * 1;
        _currentData.configBool.truckWheelLiftable = _reader.ReadBool(offset, 16); offset += 16 * 1;
        _currentData.configBool.isCargoLoaded = _reader.ReadBool(offset); offset += 1;
        _currentData.configBool.specialJob = _reader.ReadBool(offset); offset += 1;

        // TruckBool
        _currentData.truckBool.parkingBrake = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.motorBrake = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.airPressureWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.airPressureEmergency = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.fuelWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.adblueWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.oilPressureWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.waterTemperatureWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.batteryVoltageWarning = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.electricEnabled = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.engineEnabled = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.wipers = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.blinkerLeftActive = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.blinkerRightActive = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.blinkerLeftOn = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.blinkerRightOn = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsParking = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsBeamLow = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsBeamHigh = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsBeacon = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsBrake = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsReverse = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.lightsHazard = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.cruiseControl = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.truckWheelOnGround = _reader.ReadBool(offset, 16); offset += 16 * 1;
        _currentData.truckBool.shifterToggle = _reader.ReadBool(offset, 2); offset += 2 * 1;
        _currentData.truckBool.differentialLock = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.liftAxle = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.liftAxleIndicator = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.trailerLiftAxle = _reader.ReadBool(offset); offset += 1;
        _currentData.truckBool.trailerLiftAxleIndicator = _reader.ReadBool(offset); offset += 1;

        // GameplayBool
        _currentData.gameplayBool.jobDeliveredAutoparkUsed = _reader.ReadBool(offset); offset += 1;
        _currentData.gameplayBool.jobDeliveredAutoloadUsed = _reader.ReadBool(offset); offset += 1;
        offset += 25; // Padding

        // ConfigVector
        _currentData.configVector.cabinPosition = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.configVector.headPosition = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.configVector.truckHookPosition = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.configVector.truckWheelPositions = new Vector3[16];
        float[] wheelX = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        float[] wheelY = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        float[] wheelZ = _reader.ReadFloat(offset, 16); offset += 16 * 4;
        for (int i = 0; i < 16; i++)
        {
            _currentData.configVector.truckWheelPositions[i] = new Vector3(
                wheelX[i],
                wheelY[i],
                wheelZ[i]
            );
        }

        // TruckVector
        _currentData.truckVector.linearVelocityAcceleration = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.truckVector.angularVelocityAcceleration = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.truckVector.acceleration = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.truckVector.angularRotationAcceleration = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.truckVector.cabinAngularVelocity = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.truckVector.cabinAngularAcceleration = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        offset += 60; // Padding

        // HeadPlacement
        _currentData.headPlacement.cabinOffset = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.headPlacement.cabinOffsetRotation = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.headPlacement.headOffset = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.headPlacement.headOffsetRotation = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        offset += 152; // Padding


        // TruckPlacement
        _currentData.truckPlacement.coordinate = new Vector3Double(
            _reader.ReadDouble(offset),
            _reader.ReadDouble(offset + 8),
            _reader.ReadDouble(offset + 16)
        ); offset += 24;
        _currentData.truckPlacement.rotation = new Vector3Double(
            _reader.ReadDouble(offset),
            _reader.ReadDouble(offset + 8),
            _reader.ReadDouble(offset + 16)
        ); offset += 24;
        offset += 52; // Padding

        // ConfigString
        _currentData.configString.truckBrandId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.truckBrand = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.truckId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.truckName = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.cargoId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.cargo = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.cityDstId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.cityDst = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.compDstId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.compDst = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.citySrcId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.citySrc = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.compSrcId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.compSrc = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.shifterType = _reader.ReadChar(offset, 16); offset += 16;
        _currentData.configString.truckLicensePlate = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.truckLicensePlateCountryId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.truckLicensePlateCountry = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.configString.jobMarket = _reader.ReadChar(offset, 32); offset += 32;

        // GameplayString
        _currentData.gameplayString.fineOffence = _reader.ReadChar(offset, 32); offset += 32;
        _currentData.gameplayString.ferrySourceName = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.ferryTargetName = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.ferrySourceId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.ferryTargetId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.trainSourceName = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.trainTargetName = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.trainSourceId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        _currentData.gameplayString.trainTargetId = _reader.ReadChar(offset, stringSize); offset += stringSize;
        offset += 20; // Padding

        // ConfigLongLong
        _currentData.configLongLong.jobIncome = _reader.ReadLongLong(offset); offset += 8;
        offset += 192; // Padding

        // GameplayLongLong
        _currentData.gameplayLongLong.jobCancelledPenalty = _reader.ReadLongLong(offset); offset += 8;
        _currentData.gameplayLongLong.jobDeliveredRevenue = _reader.ReadLongLong(offset); offset += 8;
        _currentData.gameplayLongLong.fineAmount = _reader.ReadLongLong(offset); offset += 8;
        _currentData.gameplayLongLong.tollgatePayAmount = _reader.ReadLongLong(offset); offset += 8;
        _currentData.gameplayLongLong.ferryPayAmount = _reader.ReadLongLong(offset); offset += 8;
        _currentData.gameplayLongLong.trainPayAmount = _reader.ReadLongLong(offset); offset += 8;
        offset += 52;

        // SpecialBool
        _currentData.specialBool.onJob = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.jobFinished = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.jobCancelled = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.jobDelivered = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.fined = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.tollgate = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.ferry = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.train = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.refuel = _reader.ReadBool(offset); offset += 1;
        _currentData.specialBool.refuelPaid = _reader.ReadBool(offset); offset += 1;
        offset += 90;

        // Publish to the event bus
        Events.Current.Publish<GameTelemetryData>(EventString, _currentData);
    }
}