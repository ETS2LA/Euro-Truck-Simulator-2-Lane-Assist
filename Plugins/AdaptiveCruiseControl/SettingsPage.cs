using ETS2LA.Shared;
using System.Collections.Generic;

namespace AdaptiveCruiseControl;

public static class SettingsPage
{
    private static readonly IReadOnlyList<string> AggOptions = new List<string> { "Eco", "Normal", "Aggressive" };
    private static readonly IReadOnlyList<string> OffsetTypes = new List<string> { "Percentage", "Absolute" };
    private static readonly IReadOnlyList<string> TlModes = new List<string> { "Legacy", "Normal" };

    public static IEnumerable<PluginPage> Render(AccSettings s, AccRuntime r)
    {
        static int SafeIndex(IReadOnlyList<string> list, string value, int fallback = 0)
        {
            var idx = list.ToList().IndexOf(value);
            return idx >= 0 ? idx : fallback;
        }

        var body = new List<UiElement>
        {
            new UiSection("Adaptive Cruise Control", "Configure following distance, speed handling and PID tuning.", new UiElement[]
            {
                new UiSwitch("Enable ACC", "Master enable for ACC.", r.Enabled, "toggle_enable"),
                new UiCombobox("Aggressiveness", "Tuning preset for accel/decel and time gap.", AggOptions, SafeIndex(AggOptions, s.Aggressiveness), "set_agg"),
                new UiSlider("Follow Distance", "Seconds to target behind the lead vehicle.", 0.5, 4.0, 0.1, s.FollowingDistance, "set_follow_dist"),
                new UiCheckbox("Ignore Gates", "If enabled, ACC will not stop for gates.", s.IgnoreGates, "set_ignore_gates"),
                new UiCheckbox("Ignore Traffic Lights", "If enabled, ACC will not stop for lights.", s.IgnoreTrafficLights, "set_ignore_lights"),
                new UiCombobox("Traffic Light Mode", "Legacy raycast or prefab-aware detection.", TlModes, SafeIndex(TlModes, s.TrafficLightMode), "set_tl_mode"),
            }),
            new UiSection("Speed Control", "Limit, offsets, and curve handling.", new UiElement[]
            {
                new UiSlider("Coefficient of Friction", "Higher allows faster in curves.", 0.1, 1.0, 0.1, s.Mu, "set_mu"),
                new UiCheckbox("Ignore Speed Limit", "If enabled, only curvature and max speed apply.", s.IgnoreSpeedLimit, "set_ignore_speed"),
                new UiCombobox("Speed Offset Type", "Apply offset as percentage or absolute.", OffsetTypes, SafeIndex(OffsetTypes, s.SpeedOffsetType), "set_offset_type"),
                new UiSlider("Speed Offset", "Base offset on top of detected limit.", -30, 30, 1, s.SpeedOffset, "set_offset"),
                new UiInput("Maximum Speed (km/h)", "0 disables cap.", s.MaxSpeed.ToString("0"), "set_max_speed", Type: "number"),
                new UiInput("Fallback Speed (km/h)", "Used when game reports 0 speed limit.", s.OverwriteSpeed.ToString("0"), "set_overwrite_speed", Type: "number"),
            }),
            new UiSection("PID", "Unlock to tune gains manually.", new UiElement[]
            {
                new UiCheckbox("Show Debug Data", "Display internal ACC debug info.", s.Debug, "set_debug"),
                new UiCheckbox("Unlock PID", "Allow manual PID tuning.", s.UnlockPid, "set_unlock_pid"),
                new UiSlider("PID Kp", "Proportional gain.", 0.01, 1.0, 0.01, s.PidKp, "set_kp"),
                new UiSlider("PID Ki", "Integral gain.", 0.01, 1.0, 0.01, s.PidKi, "set_ki"),
                new UiSlider("PID Kd", "Derivative gain.", 0.01, 1.0, 0.01, s.PidKd, "set_kd"),
            }),
            new UiSection("Status", null, new UiElement[]
            {
                new UiText($"Enabled: {(r.Enabled ? "Yes" : "No")}", Bold: true),
                new UiText($"Current speed: {r.SpeedKph:F1} km/h, Target: {r.TargetSpeedKph:F1} km/h"),
                new UiText($"Lead distance: {r.LeadDistance:F1} m, Gap target: {r.DesiredGap:F1} m"),
                new UiText($"Manual offset: {r.ManualSpeedOffset} {(s.SpeedOffsetType == "Absolute" ? "km/h" : "%")}")
            })
        };

        yield return new PluginPage("adaptive-cruise-control-settings", PluginPageLocation.Settings, "Adaptive Cruise Control", "ACC configuration and status.", body);
    }
}
