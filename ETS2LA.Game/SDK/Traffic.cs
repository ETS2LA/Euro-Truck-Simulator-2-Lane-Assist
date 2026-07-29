using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

using System.Numerics;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;
using TruckLib;

namespace ETS2LA.Game.SDK;

public class BaseVehicle
{
    public Vector3 Position { get; set; }
    public Quaternion Rotation { get; set; }
    public Vector3 Size { get; set; }

    public List<Vector3> GetCornersOnGround()
    {
        List<Vector3> corners = new List<Vector3>();
        Vector3 halfSize = Size / 2;

        corners.Add(Position + new Vector3(-halfSize.X, -halfSize.Y, -halfSize.Z));
        corners.Add(Position + new Vector3(halfSize.X, -halfSize.Y, -halfSize.Z));
        corners.Add(Position + new Vector3(halfSize.X, -halfSize.Y, halfSize.Z));
        corners.Add(Position + new Vector3(-halfSize.X, -halfSize.Y, halfSize.Z));

        Quaternion invQuat = Quaternion.Conjugate(Rotation);
        Vector3 euler = invQuat.ToEuler();
        Quaternion filteredRot = Quaternion.CreateFromYawPitchRoll(-euler.Y + (float)Math.PI, -euler.Z + (float)Math.PI, -euler.X);
        for (int i = 0; i < corners.Count; i++)
        {
            corners[i] = Vector3.Transform(corners[i] - Position, filteredRot) + Position;
        }

        return corners;
    }
}

public class TrafficTrailer : BaseVehicle
{
    public required TrafficVehicle parent;
}

public class TrafficVehicle : BaseVehicle
{
    public float speed;
    public float acceleration;
    public Int16 trailer_count;
    public Int16 id;

    // These only affect vehicles in TMP
    public bool isTMP;
    public bool isTrailer;

    public TrafficTrailer[] trailers = Array.Empty<TrafficTrailer>();

    // These are only internal
    public KalmanFilter speedFilter = new KalmanFilter(q: 0.008f, r: 0.4f);
    public Vector3 lastPosition = Vector3.Zero;
    public float lastUpdateTime = 0f;
}

public class TrafficData
{
    public TrafficVehicle[] vehicles = Array.Empty<TrafficVehicle>();
}

public class TrafficProvider
{
    private static readonly Lazy<TrafficProvider> _instance = new(() => new TrafficProvider());
    public static TrafficProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1f / 60f;
    private float SpeedUpdateRateInTMP = 1f / 10f;
    public string EventString = "ETS2LA.Game.SDK.Traffic.Data";

    private MemoryReader _reader;
    private TrafficData? _currentData = new();
    private TrafficVehicle[] _lastVehicles = Array.Empty<TrafficVehicle>();
    private readonly Dictionary<short, TrafficVehicle> _lastVehicleById = new();


    string mmapName = "Local\\ETS2LATraffic";
    string mmapNameLinux = "/dev/shm/ETS2LATraffic";
    int mmapSize = 6800;

    private MemoryMappedFile? _mmf;
    private MemoryMappedViewAccessor? _accessor;
    private byte[] _buffer = Array.Empty<byte>();
    private readonly Stopwatch _sinceReconnect = Stopwatch.StartNew();

    public TrafficProvider()
    {
        _buffer = new byte[mmapSize];
        _reader = new MemoryReader(_buffer);

        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public TrafficData? GetCurrentTrafficData()
    {
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
                Logger.Error(ex.ToString(), "Error in traffic update loop.");
            }
        }
    }
    
    private bool TryOpenMemory()
    {
        if (_accessor != null)
            return true;

        try
        {
            #if WINDOWS
                _mmf = MemoryMappedFile.OpenExisting(mmapName);
            # else
                _mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
            # endif

            _accessor = _mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
            return true;
        }
        catch (FileNotFoundException)
        {
            CloseMemory();
            Thread.Sleep(10000);
            return false;
        }
        catch (Exception ex)
        {
            CloseMemory();
            Logger.Error($"Error initializing memory mapped file: {ex.Message}");
            Thread.Sleep(10000);
            return false;
        }
    }

    private void CloseMemory()
    {
        _accessor?.Dispose();
        _accessor = null;
        _mmf?.Dispose();
        _mmf = null;
    }

    private void Update()
    {
        if (_currentData == null)
        {
            _currentData = new TrafficData();
        }

        if (!TryOpenMemory())
            return;

        try
        {
            _accessor!.ReadArray(0, _buffer, 0, mmapSize);
        }
        catch (Exception)
        {
            // Mapping went away (e.g. game closed), reconnect on the next update.
            CloseMemory();
            return;
        }

        List<TrafficVehicle> vehicles = new List<TrafficVehicle>();
        int offset = 0;
        for (int i = 0; i < 40-1; i++)
        {
            TrafficVehicle vehicle = new TrafficVehicle();

            // 0
            vehicle.Position = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;

            // 12
            vehicle.Rotation = new System.Numerics.Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;

            // 28
            vehicle.Size = new Vector3(
                _reader.ReadFloat(offset),     // Width
                _reader.ReadFloat(offset + 4), // Height
                _reader.ReadFloat(offset + 8)  // Length
            ); offset += 12;

            // 40
            vehicle.speed = _reader.ReadFloat(offset); offset += 4;
            vehicle.acceleration = _reader.ReadFloat(offset); offset += 4;
            vehicle.trailer_count = _reader.ReadInt16(offset); offset += 2;
            vehicle.id = _reader.ReadInt16(offset); offset += 2;

            // 52
            vehicle.isTMP = _reader.ReadBool(offset); offset += 1;
            vehicle.isTrailer = _reader.ReadBool(offset); offset += 1;

            // 54
            if(vehicle.trailer_count > 2) { vehicle.trailer_count = 2; }
            if(vehicle.trailer_count < 0) { vehicle.trailer_count = 0; }

            TrafficTrailer[] trailers = new TrafficTrailer[3];
            for (int j = 0; j < 3; j++)
            {
                // 0
                TrafficTrailer trailer = new TrafficTrailer{ parent = vehicle };
                trailer.Position = new Vector3(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8)
                ); offset += 12;

                // 12
                trailer.Rotation = new System.Numerics.Quaternion(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8),
                    _reader.ReadFloat(offset + 12)
                ); offset += 16;

                // 28
                trailer.Size = new Vector3(
                    _reader.ReadFloat(offset),     // Width
                    _reader.ReadFloat(offset + 4), // Height
                    _reader.ReadFloat(offset + 8)  // Length
                ); offset += 12;

                // 40
                trailers[j] = trailer;
            }

            vehicle.trailers = trailers;
            vehicles.Add(vehicle);
        }

        _lastVehicles = _currentData.vehicles;
        _currentData.vehicles = vehicles.ToArray();

        bool anyTMP = false;
        foreach (var vehicle in _currentData.vehicles)
        {
            if (vehicle.isTMP) { anyTMP = true; break; }
        }

        _lastVehicleById.Clear();
        if (anyTMP)
        {
            foreach (var lastVehicle in _lastVehicles)
                _lastVehicleById.TryAdd(lastVehicle.id, lastVehicle);
        }

        // Update vehicle speeds
        var curTime = Environment.TickCount / 1000f;
        foreach (var vehicle in _currentData.vehicles)
        {
            if (vehicle.isTMP && _lastVehicleById.TryGetValue(vehicle.id, out var lastVehicle))
            {
                vehicle.speed = lastVehicle.speed;
                vehicle.speedFilter = lastVehicle.speedFilter;
                vehicle.lastPosition = lastVehicle.lastPosition;
                vehicle.lastUpdateTime = lastVehicle.lastUpdateTime;
                if (curTime - vehicle.lastUpdateTime > SpeedUpdateRateInTMP)
                {
                    var distance = Vector3.Distance(vehicle.lastPosition, vehicle.Position);
                    vehicle.speed = vehicle.speedFilter.Update(distance / (curTime - vehicle.lastUpdateTime));
                    vehicle.lastPosition = vehicle.Position;
                    vehicle.lastUpdateTime = curTime;
                }
            }
        }

        Events.Current.Publish<TrafficData>(EventString, _currentData);

        // Periodically reopen the mmap to detect game restarts.
        if (_sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            _sinceReconnect.Restart();
        }
    }
}