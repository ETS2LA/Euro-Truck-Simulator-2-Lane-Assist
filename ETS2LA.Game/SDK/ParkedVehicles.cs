using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;
using static ETS2LA.Translations.T;

using System.Numerics;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;

namespace ETS2LA.Game.SDK;

public class ParkedVehicle : BaseVehicle
{
    public int id;
    public bool isTrailer;
}

public class ParkedVehicleData
{
    public required List<ParkedVehicle> vehicles;
}

public class ParkedVehiclesProvider
{
    private static readonly Lazy<ParkedVehiclesProvider> _instance = new(() => new ParkedVehiclesProvider());
    public static ParkedVehiclesProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1f / 60f;
    public string EventString = "ETS2LA.Game.SDK.ParkedVehicles.Data";

    private MemoryReader _reader;
    private ParkedVehicleData? _currentData;

    string mmapName = "Local\\ETS2LAParkedVehicles";
    string mmapNameLinux = "/dev/shm/ETS2LAParkedVehicles";
    int mmapSize = 1720;

    private MemoryMappedFile? _mmf;
    private MemoryMappedViewAccessor? _accessor;
    private byte[] _buffer = Array.Empty<byte>();
    private readonly Stopwatch _sinceReconnect = Stopwatch.StartNew();

    public ParkedVehiclesProvider()
    {
        _buffer = new byte[mmapSize];
        _reader = new MemoryReader(_buffer);

        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public ParkedVehicleData? GetCurrentParkedVehicleData()
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
                Logger.Error(ex.ToString(), _("Error in parked vehicles update loop."));
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
            Logger.Error(_("Error initializing memory mapped file: {0}", ex.Message));
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
            _currentData = new ParkedVehicleData{ vehicles = new List<ParkedVehicle>() };
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

        List<ParkedVehicle> vehicles = new List<ParkedVehicle>();
        int offset = 0;
        for (int i = 0; i < 40; i++)
        {
            ParkedVehicle vehicle = new ParkedVehicle();
            vehicle.Position = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            vehicle.Rotation = new Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;
            vehicle.Size = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            vehicle.id = _reader.ReadShort(offset); offset += 2;
            vehicle.isTrailer = _reader.ReadBool(offset); offset += 1;

            vehicles.Add(vehicle);
        }

        _currentData.vehicles = vehicles;
        Events.Current.Publish<ParkedVehicleData>(EventString, _currentData);

        // Periodically reopen the mmap to detect game restarts.
        if (_sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            _sinceReconnect.Restart();
        }
    }
}