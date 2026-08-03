using ETS2LA.Shared;
using ETS2LA.Backend.Events;
using ETS2LA.Notifications;
using ETS2LA.Logging;

using System.IO.MemoryMappedFiles;
using System.Numerics;
using System.Diagnostics;

namespace ETS2LA.Game.Telemetry;

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
    
    private MemoryReader reader;
    private GameTelemetryData? currentData = new();
    private bool shutdown = false;


    string mmapName = "Local\\SCSTelemetry";
    string mmapNameLinux = "/dev/shm/SCSTelemetry";

    int mmapSize = 32 * 1024;
    int stringSize = 64;

    private MemoryMappedFile? mmf;
    private MemoryMappedViewAccessor? accessor;
    private byte[] buffer = Array.Empty<byte>();
    private readonly Stopwatch sinceReconnect = Stopwatch.StartNew();
    
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
        buffer = new byte[mmapSize];
        reader = new MemoryReader(buffer);

        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public GameTelemetryData GetCurrentData()
    {
        if (currentData == null)
            currentData = new();
        
        return currentData;
    }

    private void UpdateThread()
    {
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        while (!shutdown)
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

        CloseMemory();
    }

    private bool TryOpenMemory()
    {
        if (accessor != null)
            return true;

        try
        {
            #if WINDOWS
                mmf = MemoryMappedFile.OpenExisting(mmapName);
            # else
                mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
            # endif

            accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
            return true;
        }
        catch (FileNotFoundException)
        {
            CloseMemory();
            NotificationHandler.Current.SendNotification(new Notification
            {
                Id = "GameTelemetry.MMFNotFound",
                Title = "Game Telemetry",
                Content = $"Couldn't connect to the game. Please open ETS2 or ATS and enable the SDK.",
                IsProgressIndeterminate = true,
            });
            Thread.Sleep(1000);
            return false;
        }
        catch (Exception)
        {
            CloseMemory();
            Thread.Sleep(1000);
            return false;
        }
    }

    private void CloseMemory()
    {
        accessor?.Dispose();
        accessor = null;
        mmf?.Dispose();
        mmf = null;
    }

    private void Update()
    {
        if (currentData == null)
            currentData = new();

        if (!TryOpenMemory())
        {
            currentData.sdkActive = false;
            return;
        }

        try
        {
            accessor!.ReadArray(0, buffer, 0, mmapSize);
        }
        catch (Exception)
        {
            // Mapping went away (e.g. game closed), reconnect on the next update.
            CloseMemory();
            return;
        }

        NotificationHandler.Current.CloseNotification("GameTelemetry.MMFNotFound");

        int offset = 0;

        // Root Values
        currentData.sdkActive = reader.ReadBool(offset); offset += 1;
        offset += 3; // Padding
        currentData.paused = reader.ReadBool(offset); offset += 1;
        offset += 3; // Padding

        currentData.time = reader.ReadLongLong(offset); offset += 8;
        currentData.simulatedTime = reader.ReadLongLong(offset); offset += 8;
        currentData.renderTime = reader.ReadLongLong(offset); offset += 8;
        currentData.multiplayerTimeOffset = reader.ReadInt(offset); offset += 8;

        // SCSValues
        currentData.scsValues.telemetryPluginRevision = reader.ReadInt(offset); offset += 4;
        currentData.scsValues.versionMajor = reader.ReadInt(offset); offset += 4;
        currentData.scsValues.versionMinor = reader.ReadInt(offset); offset += 4;
        currentData.scsValues.game = ReadGame(offset, buffer); offset += 4;
        currentData.scsValues.telemetryVersionGameMajor = reader.ReadInt(offset); offset += 4;
        currentData.scsValues.telemetryVersionGameMinor = reader.ReadInt(offset); offset += 4;

        // CommonUI
        int timeAbsolute = reader.ReadInt(offset); offset += 4;
        if (timeAbsolute != currentData.commonUI.timeAbsolute || string.IsNullOrEmpty(currentData.commonUI.timeReadable))
        {
            currentData.commonUI.timeAbsolute = timeAbsolute;
            currentData.commonUI.timeReadable = AbsoluteToReadableTime(timeAbsolute);
        }

        // ConfigUI
        currentData.configUI.gears = reader.ReadInt(offset); offset += 4;
        currentData.configUI.gearsReverse = reader.ReadInt(offset); offset += 4;
        currentData.configUI.retarderStepCount = reader.ReadInt(offset); offset += 4;
        currentData.configUI.truckWheelCount = reader.ReadInt(offset); offset += 4;
        currentData.configUI.selectorCount = reader.ReadInt(offset); offset += 4;
        currentData.configUI.timeAbsDelivery = reader.ReadInt(offset); offset += 4;
        currentData.configUI.maxTrailerCount = reader.ReadInt(offset); offset += 4;
        currentData.configUI.unitCount = reader.ReadInt(offset); offset += 4;
        currentData.configUI.plannedDistanceKm = reader.ReadInt(offset); offset += 4;

        // TruckUI
        currentData.truckUI.shifterSlot = reader.ReadInt(offset); offset += 4;
        currentData.truckUI.retarderBrake = reader.ReadInt(offset); offset += 4;
        currentData.truckUI.lightsAuxFront = reader.ReadInt(offset); offset += 4;
        currentData.truckUI.lightsAuxRoof = reader.ReadInt(offset); offset += 4;
        reader.ReadInt(offset, currentData.truckUI.truckWheelSubstance.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadInt(offset, currentData.truckUI.hshifterPosition.AsSpan(0, 32)); offset += 32 * 4;
        reader.ReadInt(offset, currentData.truckUI.hshifterBitmask.AsSpan(0, 32)); offset += 32 * 4;

        // GameplayUI
        currentData.gameplayUI.jobDeliveredDeliveryTime = reader.ReadInt(offset); offset += 4;
        currentData.gameplayUI.jobFinishedTime = reader.ReadInt(offset); offset += 4;
        currentData.gameplayUI.jobStartingTime = reader.ReadInt(offset); offset += 4;
        offset += 48; // Padding

        // CommonInt
        currentData.commonInt.restStop = reader.ReadInt(offset); offset += 4;

        // TruckInt
        currentData.truckInt.gear = reader.ReadInt(offset); offset += 4;
        currentData.truckInt.gearDashboard = reader.ReadInt(offset); offset += 4;
        reader.ReadInt(offset, currentData.truckInt.hshifterResultingGear.AsSpan(0, 32)); offset += 32 * 4;
        offset += 56; // Padding
        offset += 4;  // Padding

        // CommonFloat
        currentData.commonFloat.scale = reader.ReadFloat(offset); offset += 4;

        // ConfigFloat
        currentData.configFloat.fuelCapacity = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.fuelWarningFactor = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.adblueCapacity = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.adblueWarningFactor = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.airPressureWarning = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.airPressureEmergency = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.oilPressureWarning = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.waterTemperatureWarning = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.batteryVoltageWarning = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.engineRpmMax = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.gearDifferential = reader.ReadFloat(offset); offset += 4;
        currentData.configFloat.cargoMass = reader.ReadFloat(offset); offset += 4;
        reader.ReadFloat(offset, currentData.configFloat.truckWheelRadius.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.configFloat.gearRatiosForward.AsSpan(0, 24)); offset += 24 * 4;
        reader.ReadFloat(offset, currentData.configFloat.gearRatiosReverse.AsSpan(0, 8)); offset += 8 * 4;
        currentData.configFloat.unitMass = reader.ReadFloat(offset); offset += 4;

        // TruckFloat
        currentData.truckFloat.speed = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.engineRpm = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.userSteer = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.userThrottle = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.userBrake = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.userClutch = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.gameSteer = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.gameThrottle = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.gameBrake = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.gameClutch = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.cruiseControlSpeed = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.airPressure = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.brakeTemperature = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.fuel = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.fuelAvgConsumption = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.fuelRange = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.adblue = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.oilPressure = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.oilTemperature = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.waterTemperature = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.batteryVoltage = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.lightsDashboard = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.wearEngine = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.wearTransmission = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.wearCabin = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.wearChassis = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.wearWheels = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.truckOdometer = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.routeDistance = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.routeTime = reader.ReadFloat(offset); offset += 4;
        currentData.truckFloat.speedLimit = reader.ReadFloat(offset); offset += 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelSuspDeflection.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelVelocity.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelSteering.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelRotation.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelLift.AsSpan(0, 16)); offset += 16 * 4;
        reader.ReadFloat(offset, currentData.truckFloat.truckWheelLiftOffset.AsSpan(0, 16)); offset += 16 * 4;

        // GameplayFloat
        currentData.gameplayFloat.jobDeliveredCargoDamage = reader.ReadFloat(offset); offset += 4;
        currentData.gameplayFloat.jobDeliveredDistanceKm = reader.ReadFloat(offset); offset += 4;
        currentData.gameplayFloat.refuelAmount = reader.ReadFloat(offset); offset += 4;

        // JobFloat
        currentData.jobFloat.cargoDamage = reader.ReadFloat(offset); offset += 4;
        offset += 28; // Padding

        // ConfigBool
        reader.ReadBool(offset, currentData.configBool.truckWheelSteerable.AsSpan(0, 16)); offset += 16 * 1;
        reader.ReadBool(offset, currentData.configBool.truckWheelSimulated.AsSpan(0, 16)); offset += 16 * 1;
        reader.ReadBool(offset, currentData.configBool.truckWheelPowered.AsSpan(0, 16)); offset += 16 * 1;
        reader.ReadBool(offset, currentData.configBool.truckWheelLiftable.AsSpan(0, 16)); offset += 16 * 1;
        currentData.configBool.isCargoLoaded = reader.ReadBool(offset); offset += 1;
        currentData.configBool.specialJob = reader.ReadBool(offset); offset += 1;

        // TruckBool
        currentData.truckBool.parkingBrake = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.motorBrake = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.airPressureWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.airPressureEmergency = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.fuelWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.adblueWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.oilPressureWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.waterTemperatureWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.batteryVoltageWarning = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.electricEnabled = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.engineEnabled = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.wipers = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.blinkerLeftActive = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.blinkerRightActive = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.blinkerLeftOn = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.blinkerRightOn = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsParking = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsBeamLow = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsBeamHigh = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsBeacon = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsBrake = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsReverse = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.lightsHazard = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.cruiseControl = reader.ReadBool(offset); offset += 1;
        reader.ReadBool(offset, currentData.truckBool.truckWheelOnGround.AsSpan(0, 16)); offset += 16 * 1;
        reader.ReadBool(offset, currentData.truckBool.shifterToggle.AsSpan(0, 2)); offset += 2 * 1;
        currentData.truckBool.differentialLock = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.liftAxle = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.liftAxleIndicator = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.trailerLiftAxle = reader.ReadBool(offset); offset += 1;
        currentData.truckBool.trailerLiftAxleIndicator = reader.ReadBool(offset); offset += 1;

        // GameplayBool
        currentData.gameplayBool.jobDeliveredAutoparkUsed = reader.ReadBool(offset); offset += 1;
        currentData.gameplayBool.jobDeliveredAutoloadUsed = reader.ReadBool(offset); offset += 1;
        offset += 25; // Padding

        // ConfigVector
        currentData.configVector.cabinPosition = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.configVector.headPosition = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.configVector.truckHookPosition = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        for (int i = 0; i < 16; i++)
        {
            currentData.configVector.truckWheelPositions[i] = new Vector3(
                reader.ReadFloat(offset + i * 4),
                reader.ReadFloat(offset + 64 + i * 4),
                reader.ReadFloat(offset + 128 + i * 4)
            );
        }
        offset += 3 * 16 * 4;

        // TruckVector
        currentData.truckVector.linearVelocityAcceleration = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.truckVector.angularVelocityAcceleration = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.truckVector.acceleration = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.truckVector.angularRotationAcceleration = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.truckVector.cabinAngularVelocity = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.truckVector.cabinAngularAcceleration = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        offset += 60; // Padding

        // HeadPlacement
        currentData.headPlacement.cabinOffset = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.headPlacement.cabinOffsetRotation = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.headPlacement.headOffset = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        currentData.headPlacement.headOffsetRotation = new Vector3(
            reader.ReadFloat(offset),
            reader.ReadFloat(offset + 4),
            reader.ReadFloat(offset + 8)
        ); offset += 12;
        offset += 152; // Padding


        // TruckPlacement
        currentData.truckPlacement.coordinate = new Vector3Double(
            reader.ReadDouble(offset),
            reader.ReadDouble(offset + 8),
            reader.ReadDouble(offset + 16)
        ); offset += 24;
        currentData.truckPlacement.rotation = new Vector3Double(
            reader.ReadDouble(offset),
            reader.ReadDouble(offset + 8),
            reader.ReadDouble(offset + 16)
        ); offset += 24;
        offset += 52; // Padding

        // ConfigString
        var configString = currentData.configString;
        configString.truckBrandId = reader.ReadChar(offset, stringSize, configString.truckBrandId); offset += stringSize;
        configString.truckBrand = reader.ReadChar(offset, stringSize, configString.truckBrand); offset += stringSize;
        configString.truckId = reader.ReadChar(offset, stringSize, configString.truckId); offset += stringSize;
        configString.truckName = reader.ReadChar(offset, stringSize, configString.truckName); offset += stringSize;
        configString.cargoId = reader.ReadChar(offset, stringSize, configString.cargoId); offset += stringSize;
        configString.cargo = reader.ReadChar(offset, stringSize, configString.cargo); offset += stringSize;
        configString.cityDstId = reader.ReadChar(offset, stringSize, configString.cityDstId); offset += stringSize;
        configString.cityDst = reader.ReadChar(offset, stringSize, configString.cityDst); offset += stringSize;
        configString.compDstId = reader.ReadChar(offset, stringSize, configString.compDstId); offset += stringSize;
        configString.compDst = reader.ReadChar(offset, stringSize, configString.compDst); offset += stringSize;
        configString.citySrcId = reader.ReadChar(offset, stringSize, configString.citySrcId); offset += stringSize;
        configString.citySrc = reader.ReadChar(offset, stringSize, configString.citySrc); offset += stringSize;
        configString.compSrcId = reader.ReadChar(offset, stringSize, configString.compSrcId); offset += stringSize;
        configString.compSrc = reader.ReadChar(offset, stringSize, configString.compSrc); offset += stringSize;
        configString.shifterType = reader.ReadChar(offset, 16, configString.shifterType); offset += 16;
        configString.truckLicensePlate = reader.ReadChar(offset, stringSize, configString.truckLicensePlate); offset += stringSize;
        configString.truckLicensePlateCountryId = reader.ReadChar(offset, stringSize, configString.truckLicensePlateCountryId); offset += stringSize;
        configString.truckLicensePlateCountry = reader.ReadChar(offset, stringSize, configString.truckLicensePlateCountry); offset += stringSize;
        configString.jobMarket = reader.ReadChar(offset, 32, configString.jobMarket); offset += 32;

        // GameplayString
        var gameplayString = currentData.gameplayString;
        gameplayString.fineOffence = reader.ReadChar(offset, 32, gameplayString.fineOffence); offset += 32;
        gameplayString.ferrySourceName = reader.ReadChar(offset, stringSize, gameplayString.ferrySourceName); offset += stringSize;
        gameplayString.ferryTargetName = reader.ReadChar(offset, stringSize, gameplayString.ferryTargetName); offset += stringSize;
        gameplayString.ferrySourceId = reader.ReadChar(offset, stringSize, gameplayString.ferrySourceId); offset += stringSize;
        gameplayString.ferryTargetId = reader.ReadChar(offset, stringSize, gameplayString.ferryTargetId); offset += stringSize;
        gameplayString.trainSourceName = reader.ReadChar(offset, stringSize, gameplayString.trainSourceName); offset += stringSize;
        gameplayString.trainTargetName = reader.ReadChar(offset, stringSize, gameplayString.trainTargetName); offset += stringSize;
        gameplayString.trainSourceId = reader.ReadChar(offset, stringSize, gameplayString.trainSourceId); offset += stringSize;
        gameplayString.trainTargetId = reader.ReadChar(offset, stringSize, gameplayString.trainTargetId); offset += stringSize;
        offset += 20; // Padding

        // ConfigLongLong
        currentData.configLongLong.jobIncome = reader.ReadLongLong(offset); offset += 8;
        offset += 192; // Padding

        // GameplayLongLong
        currentData.gameplayLongLong.jobCancelledPenalty = reader.ReadLongLong(offset); offset += 8;
        currentData.gameplayLongLong.jobDeliveredRevenue = reader.ReadLongLong(offset); offset += 8;
        currentData.gameplayLongLong.fineAmount = reader.ReadLongLong(offset); offset += 8;
        currentData.gameplayLongLong.tollgatePayAmount = reader.ReadLongLong(offset); offset += 8;
        currentData.gameplayLongLong.ferryPayAmount = reader.ReadLongLong(offset); offset += 8;
        currentData.gameplayLongLong.trainPayAmount = reader.ReadLongLong(offset); offset += 8;
        offset += 52;

        // SpecialBool
        currentData.specialBool.onJob = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.jobFinished = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.jobCancelled = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.jobDelivered = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.fined = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.tollgate = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.ferry = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.train = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.refuel = reader.ReadBool(offset); offset += 1;
        currentData.specialBool.refuelPaid = reader.ReadBool(offset); offset += 1;
        offset += 90;

        // Publish to the event bus
        Events.Current.Publish<GameTelemetryData>(EventString, currentData);
        TelemetryEvents.Current.UpdateEvents(currentData);

        // Periodically reopen the mmap to detect game restarts.
        if (sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            sinceReconnect.Restart();
        }
    }

    public void Shutdown()
    {
        shutdown = true;
    }
}
