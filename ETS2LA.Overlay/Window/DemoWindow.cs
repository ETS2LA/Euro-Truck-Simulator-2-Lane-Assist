using Hexa.NET.ImGui;

using static ETS2LA.Translations.T;

namespace ETS2LA.Overlay.Window;

class DemoWindow : InternalWindow
{
    public DemoWindow()
    {
        Definition = new WindowDefinition
        {
            Title = _("Demo Window"),
            NoWindow = true
        };

        IsWindowOpen = false;

        Render = () =>
        {
            ImGui.ShowDemoWindow();
        };
    }
}