using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

using System.Numerics;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;

namespace ETS2LA.Game.SDK;

public class TrafficTrailer
{
    public Vector3 position = Vector3.Zero;
    public System.Numerics.Quaternion rotation = System.Numerics.Quaternion.Identity;
    public Vector3 size = Vector3.Zero;
}

public class TrafficVehicle
{
    public Vector3 position = Vector3.Zero;
    public System.Numerics.Quaternion rotation = System.Numerics.Quaternion.Identity;
    /// <summary>
    ///  Size, X = Width, Y = Height, Z = Length. Note that the length is not always accurate, especially for trailers.
    /// </summary>
    public Vector3 size = Vector3.Zero;
    public float speed;
    public float acceleration;
    public Int16 trailer_count;
    public Int16 id;

    // These only affect vehicles in TMP
    public bool isTMP;
    public bool isTrailer;

    public TrafficTrailer[] trailers = Array.Empty<TrafficTrailer>();
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
    public string EventString = "ETS2LA.Game.SDK.Traffic.Data";

    private MemoryReader? _reader;
    private TrafficData? _currentData = new();
    

    string mmapName = "Local\\ETS2LATraffic";
    string mmapNameLinux = "/dev/shm/ETS2LATraffic";
    int mmapSize = 6800;

    public TrafficProvider()
    {
        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
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
                Logger.Error(ex.ToString(), "Error in camera update loop.");
            }
        }
    }
    
    private void Update()
    {
        if (_currentData == null)
        {
            _currentData = new TrafficData();
        }

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
            Thread.Sleep(10000);
            _reader = null;
            return;
        }
        catch (Exception ex)
        {
            Logger.Error($"Error initializing memory mapped file: {ex.Message}");
            Thread.Sleep(10000);
            _reader = null;
            return;
        }
        finally
        {
            accessor?.Dispose();
            mmf?.Dispose();
        }


        List<TrafficVehicle> vehicles = new List<TrafficVehicle>();
        int offset = 0;
        for (int i = 0; i < 40-1; i++)
        {
            TrafficVehicle vehicle = new TrafficVehicle();

            // 0
            vehicle.position = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;

            // 12
            vehicle.rotation = new System.Numerics.Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;

            // 28
            vehicle.size = new Vector3(
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
                TrafficTrailer trailer = new TrafficTrailer();
                trailer.position = new Vector3(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8)
                ); offset += 12;

                // 12
                trailer.rotation = new System.Numerics.Quaternion(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8),
                    _reader.ReadFloat(offset + 12)
                ); offset += 16;

                // 28
                trailer.size = new Vector3(
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

        _currentData.vehicles = vehicles.ToArray();
        Events.Current.Publish<TrafficData>(EventString, _currentData);
    }
}