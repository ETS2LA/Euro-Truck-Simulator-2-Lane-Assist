using Velopack;
using Velopack.Sources;

namespace ETS2LA.Backend.Updates;

public class UpdaterSource
{
    public IUpdateSource source;
    public string sourceName;

    public UpdaterSource(IUpdateSource source, string sourceName)
    {
        this.source = source;
        this.sourceName = sourceName;
    }
}

[Serializable]
public class UpdaterSettings
{
    public string SelectedSource { get; set; } = "GitHub";
}