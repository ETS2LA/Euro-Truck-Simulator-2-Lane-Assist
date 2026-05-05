using Hexa.NET.ImGui;
using ETS2LA.Controls;
using ETS2LA.State;
using System.Numerics;

namespace ETS2LA.Overlay.Window;

class StateWindow : InternalWindow
{
    private void Text(string text)
    {
        ImGui.TextColored(new Vector4(0.9f, 0.9f, 0.9f, 1f), text);
    }

    private void DescriptionText(string text)
    {
        ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), text);
    }
    
    private void ColoredBoolean(bool value, bool invert = false)
    {
        if (invert) value = !value;
        Vector4 color = value ? new Vector4(0.5f, 1f, 0.5f, 1f) : new Vector4(1f, 0.5f, 0.5f, 1f);
        if (invert) value = !value; // revert back to original value for text
        ImGui.TextColored(color, $"{value}");
    }

    public StateWindow()
    {
        Definition = new WindowDefinition
        {
            Title = "State Info",
            Flags = ImGuiWindowFlags.AlwaysAutoResize | ImGuiWindowFlags.NoSavedSettings,
        };

        Render = () =>
        {
            DescriptionText("Desired Steering Level: "); ImGui.SameLine(); Text(ApplicationState.Current.DesiredSteeringLevel.ToString());

            DescriptionText("Pause Steering Assist: "); ImGui.SameLine(); ColoredBoolean(ApplicationState.Current.PauseSteeringAssist, invert: true);

            DescriptionText("Desired Longitudinal Level: "); ImGui.SameLine(); Text(ApplicationState.Current.DesiredLongitudinalLevel.ToString());

            DescriptionText("Pause Longitudinal Assist: "); ImGui.SameLine(); ColoredBoolean(ApplicationState.Current.PauseLongitudinalAssist, invert: true);

            float speedInUnits = ApplicationState.Current.FromScientificUnits(ApplicationState.Current.DesiredSpeed);
            DescriptionText("Desired Speed: "); ImGui.SameLine(); Text($"{ApplicationState.Current.DesiredSpeed:F1} m/s ({speedInUnits:F1} in {ApplicationState.Current.DisplayUnits})");

            DescriptionText("Display Units: "); ImGui.SameLine(); Text(ApplicationState.Current.DisplayUnits.ToString());
        };
    }
}