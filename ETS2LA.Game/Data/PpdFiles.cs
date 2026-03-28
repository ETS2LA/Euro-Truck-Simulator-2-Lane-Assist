using TruckLib;
using TruckLib.Models.Ppd;

using ETS2LA.Logging;
using ETS2LA.Game.SiiFiles;

namespace ETS2LA.Game.PpdFiles;

public enum PpdFileType
{
    PrefabDescriptor
}

public class PpdFileHandler
{
    private static readonly Lazy<PpdFileHandler> _instance = new(() => new PpdFileHandler());
    public static PpdFileHandler Current => _instance.Value;

    Dictionary<string, string> _prefabPathCache = new Dictionary<string, string>();
    Dictionary<string, IBinarySerializable> _ppdCache = new Dictionary<string, IBinarySerializable>();
    
    IFileSystem? _fs;

    public void SetFileSystem(IFileSystem fs)
    {
        _fs = fs;
    }

    private void UpdatePrefabPathCache()
    {
        if (_fs == null)
        {
            Logger.Error("File system not set for PpdFileHandler. Cannot update prefab path cache.");
            return;
        }

        SiiFileHandler.Current.SetFileSystem(_fs);
        var prefabFiles = _fs.GetFiles("/def/world/");
        prefabFiles = prefabFiles.Where(f => f.EndsWith(".sii") && f.StartsWith("/def/world/prefab.")).ToArray();

        foreach (var file in prefabFiles)
        {
            var sii = SiiFileHandler.Current.GetSiiFile(file);
            if (sii == null)
            {
                Logger.Error($"Failed to load {file} for prefab path cache.");
                continue;
            }

            foreach (var unit in sii.Units)
            {
                var token = unit.Name.Split('.').Last();
                var path = unit.Attributes["prefab_desc"].Trim('"');
                if (!_prefabPathCache.ContainsKey(token))
                {
                    _prefabPathCache[token] = path;
                }
            }
        }
    }

    private IBinarySerializable? LoadPpdFile(string path, PpdFileType type)
    {
        try
        {
            switch (type)
            {
                case PpdFileType.PrefabDescriptor:
                    if(_prefabPathCache.Count == 0) UpdatePrefabPathCache();
                    if (!_prefabPathCache.ContainsKey(path))
                    {
                        Logger.Error($"Prefab token {path} not found in prefab path cache.");
                        return null;
                    }

                    path = _prefabPathCache[path];
                    return PrefabDescriptor.Open(path, _fs);
                default:
                    Logger.Error($"Unsupported PPD file type: {type}");
                    return null;
            }
        }
        catch (Exception ex)
        {
            Logger.Error($"Failed to load PPD file at {path}: {ex.Message}");
            return null;
        }
    }

    public IBinarySerializable? GetPpdFile(string path, PpdFileType type = PpdFileType.PrefabDescriptor)
    {
        if (_ppdCache.ContainsKey(path))
        {
            return _ppdCache[path];
        }

        var file = LoadPpdFile(path, type);
        if (file != null)
        {
            _ppdCache[path] = file;
        }

        return file;
    }
}