using Avalonia.Data;

namespace ETS2LA.Overlay.AR;

public struct ARRendererDefinition
{
    public string Name;
    public Optional<float> Alpha;
}

public class ARRenderCallback
{
    public ARRendererDefinition Definition;
    public Action Render3D = () => { };
}