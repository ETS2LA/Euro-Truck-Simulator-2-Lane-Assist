using Hexa.NET.ImGui;

using ETS2LA.Controls;
using ETS2LA.State;
using static ETS2LA.Translations.T;

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
            Title = _("State Info"),
            Flags = ImGuiWindowFlags.AlwaysAutoResize,
        };

        IsWindowOpen = false;

        Render = () =>
        {
            DescriptionText(_("Desired Steering Level: ")); ImGui.SameLine(); Text(ApplicationState.Current.SteeringLevelTranslation[ApplicationState.Current.DesiredSteeringLevel]);

            DescriptionText(_("Pause Steering Assist: ")); ImGui.SameLine(); ColoredBoolean(ApplicationState.Current.PauseSteeringAssist, invert: true);

            DescriptionText(_("Desired Longitudinal Level: ")); ImGui.SameLine(); Text(ApplicationState.Current.LongitudinalLevelTranslation[ApplicationState.Current.DesiredLongitudinalLevel]);

            DescriptionText(_("Pause Longitudinal Assist: ")); ImGui.SameLine(); ColoredBoolean(ApplicationState.Current.PauseLongitudinalAssist, invert: true);

            float speed = ApplicationState.Current.DesiredSpeed;
            Units displayUnits = ApplicationState.Current.DisplayUnits;
            float speedInUnits = UnitConversions.FromScientificUnits(UnitType.Speed, speed, displayUnits);
            string unitAbbreviation = UnitConversions.GetUnitAbbreviation(UnitType.Speed, displayUnits);
            DescriptionText(_("Desired Speed: ")); ImGui.SameLine(); Text(_("{0} m/s ({1} in {2})", speed.ToString("F1"), speedInUnits.ToString("F1"), unitAbbreviation));

            DescriptionText(_("Display Units: ")); ImGui.SameLine(); Text(ApplicationState.Current.DisplayUnitsTranslation[ApplicationState.Current.DisplayUnits]);
        };
    }
}