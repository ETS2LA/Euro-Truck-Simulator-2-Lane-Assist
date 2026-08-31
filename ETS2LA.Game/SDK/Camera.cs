using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;
using static ETS2LA.Translations.T;

using System.Numerics;
using System.IO.MemoryMappedFiles;
using System.Diagnostics;

namespace ETS2LA.Game.SDK;

/// <summary>
///  This frame's camera data from the game. <br/>
///  **NOTE**: This might not match the telemetry in terms of timing!
/// </summary>
public class CameraData
{
    public float fov;
    /// <summary>
    ///  The position of the camera in the current sector. <br/> To convert to world
    ///  coordinates, add the sector's `cx` and `cy` offsets multiplied by 512.
    /// </summary>
    public Vector3 position = Vector3.Zero;
    /// <summary>
    ///  The world space position of the truck during the camera timestamp. <br/> Use
    ///  this to sync anything you use the camera position to with the truck's position. <br/>
    ///  Avoid using the telemetry truck position in this case, to avoid rendering jitter.
    /// </summary>
    public Vector3 truckPosition = Vector3.Zero;
    public Int16 cx;
    public Int16 cy;
    public Quaternion rotation = Quaternion.Identity;
    /// <summary>
    ///  The rotation of the truck during the camera timestamp. <br/> 
    ///  Use this to sync anything you use the camera rotation to with the truck's rotation. <br/> 
    ///  Avoid using the telemetry truck rotation in this case, to avoid rendering jitter.
    /// </summary>
    public Quaternion truckRotation = Quaternion.Identity;
    public Matrix4x4 projection;
}

public class CameraProvider
{
    private static readonly Lazy<CameraProvider> _instance = new(() => new CameraProvider());
    public static CameraProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1f / 60f;
    public string EventString = "ETS2LA.Game.SDK.Camera.Data";

    private MemoryReader _reader;
    private CameraData? _currentData = new();

    string mmapName = "Local\\ETS2LACameraProps";
    string mmapNameLinux = "/dev/shm/ETS2LACameraProps";
    int mmapSize = 128;

    private MemoryMappedFile? _mmf;
    private MemoryMappedViewAccessor? _accessor;
    private byte[] _buffer = Array.Empty<byte>();
    private readonly Stopwatch _sinceReconnect = Stopwatch.StartNew();

    public CameraProvider()
    {
        _buffer = new byte[mmapSize];
        _reader = new MemoryReader(_buffer);

        Thread updateThread = new Thread(UpdateThread)
        {
            IsBackground = true
        };
        updateThread.Start();
    }

    public CameraData GetCurrentData()
    {
        if (_currentData == null)
            _currentData = new CameraData();
            
        return _currentData;
    }

    private void UpdateThread()
    {
        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        while (true)
        {
            int timeLeft = (int)((UpdateRate * 1000) - stopwatch.Elapsed.TotalMilliseconds);
            if (timeLeft > 1)
            {
                Thread.Sleep(timeLeft - 1);
                continue;
            }

            stopwatch.Restart();
            try { Update(); }
            catch (Exception ex)
            {
                Logger.Error(ex.ToString(), _("Error in camera update loop."));
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
            _currentData = new CameraData();
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

        int offset = 0;
        _currentData.fov = _reader.ReadFloat(offset); offset += 4;
        _currentData.position = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;
        _currentData.cx = _reader.ReadInt16(offset); offset += 2;
        _currentData.cy = _reader.ReadInt16(offset); offset += 2;
        _currentData.rotation = new Quaternion(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8),
            _reader.ReadFloat(offset + 12)
        ); offset += 16;
        
        _currentData.projection = new Matrix4x4(
            _reader.ReadFloat(offset)     , _reader.ReadFloat(offset + 4) , _reader.ReadFloat(offset + 8) , _reader.ReadFloat(offset + 12),
            _reader.ReadFloat(offset + 16), _reader.ReadFloat(offset + 20), _reader.ReadFloat(offset + 24), _reader.ReadFloat(offset + 28),
            _reader.ReadFloat(offset + 32), _reader.ReadFloat(offset + 36), _reader.ReadFloat(offset + 40), _reader.ReadFloat(offset + 44),
            _reader.ReadFloat(offset + 48), _reader.ReadFloat(offset + 52), _reader.ReadFloat(offset + 56), _reader.ReadFloat(offset + 60)
        ); offset += 64;

        _currentData.truckPosition = new Vector3(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8)
        ); offset += 12;

        _currentData.truckRotation = new Quaternion(
            _reader.ReadFloat(offset),
            _reader.ReadFloat(offset + 4),
            _reader.ReadFloat(offset + 8),
            _reader.ReadFloat(offset + 12)
        ); offset += 16;

        Events.Current.Publish<CameraData>(EventString, _currentData);

        // Periodically reopen the mmap to detect game restarts.
        if (_sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            _sinceReconnect.Restart();
        }
    }
}