using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

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

    private MemoryReader? _reader;
    private SemaphoreData? _currentData = new();
    

    string mmapName = "Local\\ETS2LASemaphore";
    string mmapNameLinux = "/dev/shm/ETS2LASemaphore";
    int mmapSize = 1920;

    public SemaphoreProvider()
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
                Logger.Error(ex.ToString(), "Error in semaphore update loop.");
            }
        }
    }
    
    private void Update()
    {
        if (_currentData == null)
        {
            _currentData = new SemaphoreData();
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
    }
}