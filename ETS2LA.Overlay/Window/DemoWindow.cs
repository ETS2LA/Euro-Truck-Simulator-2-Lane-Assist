using Hexa.NET.ImGui;

namespace ETS2LA.Overlay.Window;

class DemoWindow : InternalWindow
{
    public DemoWindow()
    {
        Definition = new WindowDefinition
        {
            Title = "Demo Window",
            NoWindow = true
        };

        IsWindowOpen = false;

        Render = () =>
        {
            ImGui.ShowDemoWindow();
        };
    }
}