// This file is based on
// https://github.com/RenCloud/scs-sdk-plugin/blob/dev/scs-telemetry/inc/scs-telemetry-common.hpp

using System.Runtime.InteropServices;

namespace ETS2LA.Shared
{

    // MARK: Trailer
    public class ConBool
    {
        public bool[] wheelSteerable = new bool[16];
        public bool[] wheelSimulated = new bool[16];
        public bool[] wheelPowered = new bool[16];
        public bool[] wheelLiftable = new bool[16];
    }

    public class ComBool
    {
        public bool[] wheelOnGround = new bool[16];
        public bool attached;
    }

    public class ComUI
    {
        public int[] wheelSubstance = new int[16];
        public int wheelCount;
    }

    public class ComFloat
    {
        public float cargoDamage;
        public float wearChassis;
        public float wearWheels;
        public float wearBody;

        public float[] wheelSuspensionDeflection = new float[16];
        public float[] wheelVelocity = new float[16];
        public float[] wheelSteering = new float[16];
        public float[] wheelRotation = new float[16];
        public float[] wheelLift = new float[16];
        public float[] wheelLiftOffset = new float[16];
        public float[] wheelRadius = new float[16];
    }

    public class ComVector
    {
        public Vector3 linearVelocity = Vector3.Zero;
        public Vector3 angularVelocity = Vector3.Zero;
        public Vector3 linearAcceleration = Vector3.Zero;
        public Vector3 angularAcceleration = Vector3.Zero;

        public Vector3 hookPosition = Vector3.Zero;
        public Vector3[] wheelPositions = new Vector3[16];
    }

    public class ComDouble
    {
        public Vector3 worldPosition = Vector3.Zero;
        public Vector3 worldRotation = Vector3.Zero;
    }

    public class ConString
    {
        public string id = string.Empty;
        public string cargoAccessoryId = string.Empty;
        public string bodyType = string.Empty;
        public string brandId = string.Empty;
        public string brand = string.Empty;
        public string name = string.Empty;
        public string chainType = string.Empty;
        public string licensePlate = string.Empty;
        public string licensePlateCountry = string.Empty;
        public string licensePlateCountryId = string.Empty;
    }

    public class TrailerInfo
    {
        public required ConBool conBool;
        public required ComBool comBool;
        public required ComUI comUI;
        public required ComFloat comFloat;
        public required ComVector comVector;
        public required ComDouble comDouble;
        public required ConString conString;
    }

    // MARK: Main
    public class SCSValues
    {
        public int telemetryPluginRevision;
        public int versionMajor;
        public int versionMinor;
        public string game = string.Empty;
        public int telemetryVersionGameMajor;
        public int telemetryVersionGameMinor;
    }

    public class CommonUI
    {
        public int timeAbsolute;
        public string timeReadable = string.Empty;
    }

    public class ConfigUI
    {
        public int gears;
        public int gearsReverse;
        public int retarderStepCount;
        public int truckWheelCount;
        public int selectorCount;
        public int timeAbsDelivery;
        public int maxTrailerCount;
        public int unitCount;
        public int plannedDistanceKm;
    }

    public class TruckUI
    {
        public int shifterSlot;
        public int retarderBrake;
        public int lightsAuxFront;
        public int lightsAuxRoof;
        public int[] truckWheelSubstance = new int[16];
        public int[] hshifterPosition = new int[32];
        public int[] hshifterBitmask = new int[32];
    }

    public class GameplayUI
    {
        public int jobDeliveredDeliveryTime;
        public int jobStartingTime;
        public int jobFinishedTime;
    }

    public class CommonInt
    {
        public int restStop;
    }

    public class TruckInt
    {
        public int gear;
        public int gearDashboard;
        public int[] hshifterResultingGear = new int[32];
    }

    public class CommonFloat
    {
        public float scale;
    }

    public class ConfigFloat
    {
        public float fuelCapacity;
        public float fuelWarningFactor;
        public float adblueCapacity;
        public float adblueWarningFactor;
        public float airPressureWarning;
        public float airPressureEmergency;
        public float oilPressureWarning;
        public float waterTemperatureWarning;
        public float batteryVoltageWarning;
        public float engineRpmMax;
        public float gearDifferential;
        public float cargoMass;
        public float[] truckWheelRadius = new float[16];
        public float[] gearRatiosForward = new float[24];
        public float[] gearRatiosReverse = new float[8];
        public float unitMass;
    }

    public class TruckFloat
    {
        public float speed;
        public float engineRpm;
        public float userSteer;
        public float userThrottle;
        public float userBrake;
        public float userClutch;
        public float gameSteer;
        public float gameThrottle;
        public float gameBrake;
        public float gameClutch;
        public float cruiseControlSpeed;
        public float airPressure;
        public float brakeTemperature;
        public float fuel;
        public float fuelAvgConsumption;
        public float fuelRange;
        public float adblue;
        public float oilPressure;
        public float oilTemperature;
        public float waterTemperature;
        public float batteryVoltage;
        public float lightsDashboard;
        public float wearEngine;
        public float wearTransmission;
        public float wearCabin;
        public float wearChassis;
        public float wearWheels;
        public float truckOdometer;
        public float routeDistance;
        public float routeTime;
        public float speedLimit;

        public float[] truckWheelSuspDeflection = new float[16];
        public float[] truckWheelVelocity = new float[16];
        public float[] truckWheelSteering = new float[16];
        public float[] truckWheelRotation = new float[16];
        public float[] truckWheelLift = new float[16];
        public float[] truckWheelLiftOffset = new float[16];
    }

    public class GameplayFloat
    {
        public float jobDeliveredCargoDamage;
        public float jobDeliveredDistanceKm;
        public float refuelAmount;
    }

    public class JobFloat
    {
        public float cargoDamage;
    }

    public class ConfigBool
    {
        public bool[] truckWheelSteerable = new bool[16];
        public bool[] truckWheelSimulated = new bool[16];
        public bool[] truckWheelPowered = new bool[16];
        public bool[] truckWheelLiftable = new bool[16];
        public bool isCargoLoaded;
        public bool specialJob;
    }

    public class TruckBool
    {
        public bool parkingBrake;
        public bool motorBrake;
        public bool airPressureWarning;
        public bool airPressureEmergency;
        public bool fuelWarning;
        public bool adblueWarning;
        public bool oilPressureWarning;
        public bool waterTemperatureWarning;
        public bool batteryVoltageWarning;
        public bool electricEnabled;
        public bool engineEnabled;
        public bool wipers;
        public bool blinkerLeftActive;
        public bool blinkerRightActive;
        public bool blinkerLeftOn;
        public bool blinkerRightOn;
        public bool lightsParking;
        public bool lightsBeamLow;
        public bool lightsBeamHigh;
        public bool lightsBeacon;
        public bool lightsBrake;
        public bool lightsReverse;
        public bool lightsHazard;
        public bool cruiseControl;
        public bool[] truckWheelOnGround = new bool[16];
        public bool[] shifterToggle = new bool[2];
        public bool differentialLock;
        public bool liftAxle;
        public bool liftAxleIndicator;
        public bool trailerLiftAxle;
        public bool trailerLiftAxleIndicator;
    }

    public class GameplayBool
    {
        public bool jobDeliveredAutoparkUsed;
        public bool jobDeliveredAutoloadUsed;
    }

    public class ConfigVector
    {
        public Vector3 cabinPosition = Vector3.Zero;
        public Vector3 headPosition = Vector3.Zero;
        public Vector3 truckHookPosition = Vector3.Zero;
        public Vector3[] truckWheelPositions = new Vector3[16];
    }

    public class TruckVector
    {
        public Vector3 linearVelocityAcceleration = Vector3.Zero;
        public Vector3 angularVelocityAcceleration = Vector3.Zero;
        public Vector3 acceleration = Vector3.Zero;
        public Vector3 angularRotationAcceleration = Vector3.Zero;
        public Vector3 cabinAngularVelocity = Vector3.Zero;
        public Vector3 cabinAngularAcceleration = Vector3.Zero;
    }

    public class HeadPlacement
    {
        public Vector3 cabinOffset = Vector3.Zero;
        public Vector3 cabinOffsetRotation = Vector3.Zero;
        public Vector3 headOffset = Vector3.Zero;
        public Vector3 headOffsetRotation = Vector3.Zero;
    }

    public class TruckPlacement
    {
        public Vector3Double coordinate = Vector3Double.Zero;
        public Vector3Double rotation = Vector3Double.Zero;
    }

    public class ConfigString
    {
        public string truckBrandId = string.Empty;
        public string truckBrand = string.Empty;
        public string truckId = string.Empty;
        public string truckName = string.Empty;
        public string cargoId = string.Empty;
        public string cargo = string.Empty;
        public string cityDstId = string.Empty;
        public string cityDst = string.Empty;
        public string compDstId = string.Empty;
        public string compDst = string.Empty;
        public string citySrcId = string.Empty;
        public string citySrc = string.Empty;
        public string compSrcId = string.Empty;
        public string compSrc = string.Empty;
        public string shifterType = string.Empty;
        public string truckLicensePlate = string.Empty;
        public string truckLicensePlateCountryId = string.Empty;
        public string truckLicensePlateCountry = string.Empty;
        public string jobMarket = string.Empty;
    }

    public class GameplayString
    {
        public string fineOffence = string.Empty;
        public string ferrySourceName = string.Empty;
        public string ferryTargetName = string.Empty;
        public string ferrySourceId = string.Empty;
        public string ferryTargetId = string.Empty;
        public string trainSourceName = string.Empty;
        public string trainTargetName = string.Empty;
        public string trainSourceId = string.Empty;
        public string trainTargetId = string.Empty;
    }

    public class ConfigLongLong
    {
        public ulong jobIncome;
    }

    public class GameplayLongLong
    {
        public ulong jobCancelledPenalty;
        public ulong jobDeliveredRevenue;
        public ulong fineAmount;
        public ulong tollgatePayAmount;
        public ulong ferryPayAmount;
        public ulong trainPayAmount;
    }
    
    public class SpecialBool
    {
        public bool onJob;
        public bool jobFinished;
        public bool jobCancelled;
        public bool jobDelivered;
        public bool fined;
        public bool tollgate;
        public bool ferry;
        public bool train;
        public bool refuel;
        public bool refuelPaid;
    }

    public class GameTelemetryData
    {
        // Root variables
        public bool sdkActive;
        public bool paused;

        public float time;
        public float simulatedTime;
        public float renderTime;
        public float multiplayerTimeOffset;

        // Other categories
        public SCSValues scsValues;
        public CommonUI commonUI;
        public ConfigUI configUI;
        public TruckUI truckUI;
        public GameplayUI gameplayUI;
        public CommonInt commonInt;
        public TruckInt truckInt;
        public CommonFloat commonFloat;
        public ConfigFloat configFloat;
        public TruckFloat truckFloat;
        public GameplayFloat gameplayFloat;
        public JobFloat jobFloat;
        public ConfigBool configBool;
        public TruckBool truckBool;
        public GameplayBool gameplayBool;
        public ConfigVector configVector;
        public TruckVector truckVector;
        public HeadPlacement headPlacement;
        public TruckPlacement truckPlacement;
        public ConfigString configString;
        public GameplayString gameplayString;
        public ConfigLongLong configLongLong;
        public GameplayLongLong gameplayLongLong;
        public SpecialBool specialBool;
        public TrailerInfo[] trailers;

        public GameTelemetryData()
        {
            scsValues = new SCSValues();
            commonUI = new CommonUI();
            configUI = new ConfigUI();
            truckUI = new TruckUI();
            gameplayUI = new GameplayUI();
            commonInt = new CommonInt();
            truckInt = new TruckInt();
            commonFloat = new CommonFloat();
            configFloat = new ConfigFloat();
            truckFloat = new TruckFloat();
            gameplayFloat = new GameplayFloat();
            jobFloat = new JobFloat();
            configBool = new ConfigBool();
            truckBool = new TruckBool();
            gameplayBool = new GameplayBool();
            configVector = new ConfigVector();
            truckVector = new TruckVector();
            headPlacement = new HeadPlacement();
            truckPlacement = new TruckPlacement();
            configString = new ConfigString();
            gameplayString = new GameplayString();
            configLongLong = new ConfigLongLong();
            gameplayLongLong = new GameplayLongLong();
            specialBool = new SpecialBool();
            trailers = new TrailerInfo[5];
            for (int i = 0; i < trailers.Length; i++)
            {
                trailers[i] = new TrailerInfo
                {
                    conBool = new ConBool(),
                    comBool = new ComBool(),
                    comUI = new ComUI(),
                    comFloat = new ComFloat(),
                    comVector = new ComVector(),
                    comDouble = new ComDouble(),
                    conString = new ConString()
                };
            }
        }
    }
}