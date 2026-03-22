using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;

using System.Diagnostics;
using System.IO.MemoryMappedFiles;

namespace ETS2LA.Game.SDK;

public class NavigationEntry
{
    public ulong nodeUid;
    public float distanceToEnd;
    public float timeToEnd;
}

public class NavigationData
{
    public NavigationEntry[] entries = Array.Empty<NavigationEntry>();
}

public class NavigationProvider
{
    private static readonly Lazy<NavigationProvider> _instance = new(() => new NavigationProvider());
    public static NavigationProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1; // No reason to update the navigation data more often than
                                                 // once a second, it's not going to change much.
    public string EventString = "ETS2LA.Game.SDK.Navigation.Data";

    private MemoryReader? _reader;
    private NavigationData? _currentData = new();
    

    string mmapName = "Local\\ETS2LARoute";
    string mmapNameLinux = "/dev/shm/ETS2LARoute";
    int mmapSize = 96000;

    public NavigationProvider()
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
                Logger.Error(ex.ToString(), "Error in navigation update loop.");
            }
        }
    }
    
    private void Update()
    {
        if (_currentData == null)
        {
            _currentData = new NavigationData();
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


        NavigationData data = new NavigationData();
        data.entries = new NavigationEntry[6000];
        int offset = 0;
        for (int i = 0; i < 6000; i++)
        {
            NavigationEntry entry = new NavigationEntry();
            entry.nodeUid = _reader.ReadLongLong(offset); offset += 8;
            entry.distanceToEnd = _reader.ReadFloat(offset); offset += 4;
            entry.timeToEnd = _reader.ReadFloat(offset); offset += 4;
            data.entries[i] = entry;
        }

        
        Events.Current.Publish<NavigationData>(EventString, data);
    }
}