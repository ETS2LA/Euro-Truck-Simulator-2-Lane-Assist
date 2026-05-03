using TruckLib;
using TruckLib.Sii;
using ETS2LA.Logging;

namespace ETS2LA.Game.SiiFiles;

public class SiiFileHandler
{
    private static readonly Lazy<SiiFileHandler> _instance = new(() => new SiiFileHandler());
    public static SiiFileHandler Current => _instance.Value;

    Dictionary<string, SiiFile> _siiFileCache = new Dictionary<string, SiiFile>();
    Dictionary<string, Unit> _roadUnitCache = new Dictionary<string, Unit>();

    IFileSystem? _fs;

    public void SetFileSystem(IFileSystem fs)
    {
        _fs = fs;
    }

    public SiiFile? GetSiiFile(string path)
    {
        if (_siiFileCache.ContainsKey(path))
        {
            return _siiFileCache[path];
        }

        try
        {
            var sii = SiiFile.Open(path, _fs);
            _siiFileCache[path] = sii;
            return sii;
        }
        catch (Exception ex)
        {
            Logger.Error($"Failed to load SII file at {path}: {ex.Message}");
            return null;
        }
    }

    private void PopulateRoadUnitCache()
    {
        var worldFiles = _fs?.GetFiles("/def/world/") ?? Array.Empty<string>();
        var roadFiles = worldFiles.Where(f => f.EndsWith(".sii") && f.Contains("road_look")).ToArray();
        if (roadFiles.Length == 0)
        {
            Logger.Error("No road_look SII files found in /def/world/. Cannot populate road unit cache.");
            return;
        }

        foreach (var roadFile in roadFiles)
        {
            var sii = GetSiiFile(roadFile);
            if (sii == null)
            {
                Logger.Error($"Failed to load {roadFile} for road unit cache.");
                continue;
            }

            foreach (var unit in sii.Units)
            {
                _roadUnitCache[unit.Name] = unit;
            }
        }
    }

    public Unit? GetRoadUnit(string roadType)
    {
        if (_roadUnitCache.Count == 0) PopulateRoadUnitCache();
        _roadUnitCache.TryGetValue(roadType, out var unit);
        return unit;
    }
}