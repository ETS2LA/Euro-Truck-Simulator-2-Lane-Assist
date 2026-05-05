using Hexa.NET.ImGui;
using ETS2LA.Controls;
using System.Numerics;

namespace ETS2LA.Overlay.Window;

class OverlayInfoWindow : InternalWindow
{
    public OverlayInfoWindow()
    {
        Definition = new WindowDefinition
        {
            Title = "Overlay Info",
            Flags = ImGuiWindowFlags.AlwaysAutoResize | ImGuiWindowFlags.NoSavedSettings,
        };

        Render = () =>
        {
            ImGui.Text("*Shock* there's a new window here O_O");
            ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "This is the overlay that will eventually render information on top of the game. For C# we've actually made it a lot more than it was!");
            ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "Plugin developers now have full access... and I mean *full* access to ImGui for rendering, hopefully we'll see some interesting things come from that!");
            ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "Right now we've just implemented the basics, and the telemetry plugin will show off some nice performance when rendering a lot of data.");
            ImGui.Separator();
            ImGui.Text("You can interact with the overlay by holding down");
            ImGui.SameLine();
            var controls = ControlsBackend.Current.GetRegisteredControls();        
            var interactKey = controls.FirstOrDefault(c => c.Definition.Id == OverlayHandler.Current.Interact.Id);
            if (interactKey != null)
                ImGui.TextColored(new Vector4(1f, 0.5f, 0.5f, 1f), interactKey.ControlId.ToString());
            else 
                ImGui.TextColored(new Vector4(1f, 0.5f, 0.5f, 1f), "UNBOUND");
            ImGui.SameLine();
            ImGui.Text("(can be changed in the settings!)");
            ImGui.Text("The overlay is pretty much a full window system, there shouldn't be any crashes... hopefully... but if there are, report them!");
        };
    }
}