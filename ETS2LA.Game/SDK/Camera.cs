using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

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
    public Int16 cx;
    public Int16 cy;
    public Quaternion rotation = Quaternion.Identity;
    public Matrix4x4 projection;
}

public class CameraProvider
{
    private static readonly Lazy<CameraProvider> _instance = new(() => new CameraProvider());
    public static CameraProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1f / 144f;
    public string EventString = "ETS2LA.Game.SDK.Camera.Data";

    private MemoryReader? _reader;
    private CameraData? _currentData = new();

    string mmapName = "Local\\ETS2LACameraProps";
    string mmapNameLinux = "/dev/shm/ETS2LACameraProps";
    int mmapSize = 100;

    public CameraProvider()
    {
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
                Logger.Error(ex.ToString(), "Error in camera update loop.");
            }
        }
    }
    
    private void Update()
    {
        if (_currentData == null)
        {
            _currentData = new CameraData();
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
        );

        Events.Current.Publish<CameraData>(EventString, _currentData);
    }
}