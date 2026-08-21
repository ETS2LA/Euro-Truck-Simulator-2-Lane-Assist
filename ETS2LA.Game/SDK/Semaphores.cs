using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;
using static ETS2LA.Translations.T;

using System.Numerics;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;

namespace ETS2LA.Game.SDK;

public enum TrafficLightState
{
    OFF,
    ORANGETORED,
    RED,
    ORANGETOGREEN = 4,
    GREEN = 8,
    SLEEP = 32,
}

public enum GateStates
{
    CLOSING,
    CLOSED,
    OPENING,
    OPEN
}

public enum SemaphoreType
{
    TRAFFICLIGHT = 1,
    GATE = 2
}

public class Semaphore
{
    public Vector3 position = Vector3.Zero;
    public float cx;
    public float cy;
    public Quaternion rotation = Quaternion.Identity;
    public SemaphoreType type;
    public float time_remaining;
    public int state;
    public int id;

    public Vector3 GetWorldCoordinates()
    {
        return position + new Vector3(cx, 0, cy) * 512;
    }

    public UInt32 GetColor()
    {
        if (type == SemaphoreType.TRAFFICLIGHT)
        {
            return state switch
            {
                (int)TrafficLightState.OFF =>           0x333333FF,
                (int)TrafficLightState.ORANGETORED =>   0xFF9966FF,
                (int)TrafficLightState.RED =>           0xFF6666FF,
                (int)TrafficLightState.ORANGETOGREEN => 0xFF9966FF,
                (int)TrafficLightState.GREEN =>         0x77EE77FF,
                (int)TrafficLightState.SLEEP =>         0x333333FF,
                _ => 0x333333FF,
            };
        }
        else if (type == SemaphoreType.GATE)
        {
            return state switch
            {
                0 => 0xFF9966FF,
                1 => 0xFF6666FF,
                2 => 0xFF9966FF,
                3 => 0x77EE77FF,
                _ => 0x333333FF,
            };
        }
        else
        {
            return 0x333333FF;
        }
    }
}

public class SemaphoreData
{
    public Semaphore[] semaphores = Array.Empty<Semaphore>();
}

public class SemaphoreProvider
{
    private static readonly Lazy<SemaphoreProvider> _instance = new(() => new SemaphoreProvider());
    public static SemaphoreProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1f / 60f;
    public string EventString = "ETS2LA.Game.SDK.Semaphore.Data";

    private MemoryReader _reader;
    private SemaphoreData? _currentData = new();


    string mmapName = "Local\\ETS2LASemaphore";
    string mmapNameLinux = "/dev/shm/ETS2LASemaphore";
    int mmapSize = 1920;

    private MemoryMappedFile? _mmf;
    private MemoryMappedViewAccessor? _accessor;
    private byte[] _buffer = Array.Empty<byte>();
    private readonly Stopwatch _sinceReconnect = Stopwatch.StartNew();

    public SemaphoreProvider()
    {
        _buffer = new byte[mmapSize];
        _reader = new MemoryReader(_buffer);

        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public SemaphoreData? GetCurrentData()
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
                Logger.Error(ex.ToString(), _("Error in semaphore update loop."));
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
            _currentData = new SemaphoreData();
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

        List<Semaphore> semaphores = new List<Semaphore>();
        int offset = 0;
        for (int i = 0; i < 40; i++)
        {
            Semaphore semaphore = new Semaphore();
            semaphore.position = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;

            semaphore.cx = _reader.ReadShort(offset); offset += 2;
            semaphore.cy = _reader.ReadShort(offset); offset += 2;

            semaphore.rotation = new Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;

            semaphore.type = (SemaphoreType)_reader.ReadInt(offset); offset += 4;
            semaphore.time_remaining = _reader.ReadFloat(offset); offset += 4;
            semaphore.state = _reader.ReadInt(offset); offset += 4;
            semaphore.id = _reader.ReadInt(offset); offset += 4;

            semaphores.Add(semaphore);
        }

        _currentData.semaphores = semaphores.ToArray();

        Events.Current.Publish<SemaphoreData>(EventString, _currentData);

        // Periodically reopen the mmap to detect game restarts.
        if (_sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            _sinceReconnect.Restart();
        }
    }
}