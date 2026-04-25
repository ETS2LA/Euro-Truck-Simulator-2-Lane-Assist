using ETS2LA.Logging;

namespace AdaptiveCruiseControl;

public class AccSettings
{
    public double Mu { get; set; } = 0.5;
    public bool IgnoreTrafficLights { get; set; } = false;
    public bool IgnoreGates { get; set; } = false;
    public string Aggressiveness { get; set; } = "Normal"; // Eco, Normal, Aggressive
    public double FollowingDistance { get; set; } = 2.0; // seconds
    public double OverwriteSpeed { get; set; } = 30; // km/h
    public string SpeedOffsetType { get; set; } = "Absolute"; // Absolute or Percentage
    public double SpeedOffset { get; set; } = 0;
    public bool IgnoreSpeedLimit { get; set; } = false;
    public bool UnlockPid { get; set; } = false;
    public double PidKp { get; set; } = 0.30;
    public double PidKi { get; set; } = 0.08;
    public double PidKd { get; set; } = 0.05;
    public string TrafficLightMode { get; set; } = "Normal"; // Legacy or Normal
    public double MaxSpeed { get; set; } = 0; // km/h, 0 = unlimited
    public bool Debug { get; set; } = false;
}

public static class AccSettingKeys
{
    public const string Toggle = "toggle_acc";
    public const string IncSpeed = "increment_speed";
    public const string DecSpeed = "decrement_speed";
}

public static class SettingLogger
{
    public static void Safe(Action act)
    {
        try { act(); }
        catch (Exception ex) { Logger.Warn($"ACC settings apply failed: {ex.Message}"); }
    }
}
