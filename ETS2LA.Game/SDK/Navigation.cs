using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Backend.Events;
using static ETS2LA.Translations.T;

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

    public bool Contains(ulong nodeUid)
    {
        return entries.Any(e => e.nodeUid == nodeUid);
    }

    public int IndexFor(ulong nodeUid)
    {
        for (int i = 0; i < entries.Length; i++)
        {
            if (entries[i].nodeUid == nodeUid)
            {
                return i;
            }
        }
        return -1;
    }
}

public class NavigationProvider
{
    private static readonly Lazy<NavigationProvider> _instance = new(() => new NavigationProvider());
    public static NavigationProvider Current => _instance.Value;

    private float UpdateRate { get; set; } = 1; // No reason to update the navigation data more often than
                                                 // once a second, it's not going to change much.
    public string EventString = "ETS2LA.Game.SDK.Navigation.Data";

    private MemoryReader _reader;
    private NavigationData? _currentData = new();


    string mmapName = "Local\\ETS2LARoute";
    string mmapNameLinux = "/dev/shm/ETS2LARoute";
    int mmapSize = 96000;

    private MemoryMappedFile? _mmf;
    private MemoryMappedViewAccessor? _accessor;
    private byte[] _buffer = Array.Empty<byte>();
    private readonly Stopwatch _sinceReconnect = Stopwatch.StartNew();

    public NavigationProvider()
    {
        _buffer = new byte[mmapSize];
        _reader = new MemoryReader(_buffer);

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
                Logger.Error(ex.ToString(), _("Error in navigation update loop."));
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
            _currentData = new NavigationData();
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

        // Periodically reopen the mmap to detect game restarts.
        if (_sinceReconnect.Elapsed.TotalSeconds > 1.0)
        {
            CloseMemory();
            _sinceReconnect.Restart();
        }
    }
}