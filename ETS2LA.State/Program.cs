using ETS2LA.Controls;
using ETS2LA.Controls.Defaults;
using ETS2LA.Backend.Events;
using ETS2LA.Telemetry;

namespace ETS2LA.State;

public enum SteeringAssists
{
    None,
    LaneKeep,
    Full
}

public enum LongitudinalAssists
{
    None,
    EmergencyBraking,
    AdaptiveCruiseControl
}

public enum Units
{
    Metric,
    Imperial,
    Scientific
}

public class ApplicationState
{
    private static readonly Lazy<ApplicationState> _instance = new(() => new ApplicationState());
    public static ApplicationState Current => _instance.Value;

    /// <summary>
    ///  Defines the level of steering assistance the user wants.
    ///  Full is assumed to be everything plugins can provide, however plugins that can only
    ///  provide Lane Keeping, should be disabled when the user selects a higher
    ///  level.
    /// </summary>
    public SteeringAssists DesiredSteeringLevel { get; set; } = SteeringAssists.None;
    /// <summary>
    ///  This value will be set to true if the user has temporarily paused the steering assist,
    ///  e.g. by braking. Once the user resumes assists this value will be set to false again.
    /// </summary>
    public bool PauseSteeringAssist { get; set; } = false;

    /// <summary>
    ///  Defines the level of longitudinal assistance the user wants. It is assumed that lower levels
    ///  are included in higher levels, e.g. Emergency Braking should still be active even if the user
    ///  desires Adaptive Cruise Control.
    /// </summary>
    public LongitudinalAssists DesiredLongitudinalLevel { get; set; } = LongitudinalAssists.AdaptiveCruiseControl;
    /// <summary>
    ///  This value will be set to true if the user has temporarily paused the longitudinal assist,
    ///  e.g. by braking. Once the user resumes assists this value will be set to false again.
    /// </summary>
    public bool PauseLongitudinalAssist { get; set; } = false;
    /// <summary>
    ///  This value will be used by the longitudinal assist to determine the target speed. This value does
    ///  not take into account any environmental factors. That will either be provided by plugins, or the
    ///  user will have to take care of it themselves. <br/><br/>
    ///  **This value is in scientific units, that is m/s.**
    /// </summary>
    public float DesiredSpeed { get; set; } = 0.0f;

    /// <summary>
    ///  This value will determine the currently used units for any values shown in the UI. This value
    ///  is automatically changed by ETS2LA, either when the user sets it in the settings, or when we
    ///  detect a change in the game's units. This unit should determine the units used everywhere, e.g.
    ///  the units used when increasing and decreasing the target speed. (+-1 mph/kph/ms) <br/><br/>
    ///  **Use FromScientificUnits and ToScientificUnits to convert values to and from the current display units.**
    /// </summary>
    public Units DisplayUnits { get; set; } = Units.Metric;

    // Internal value to keep track of the latest telemetry we received.
    private GameTelemetryData _latestTelemetryData = new();

    public ApplicationState()
    {
        Events.Current.Subscribe<GameTelemetryData>(GameTelemetry.Current.EventString, UpdateTelemetryData);

        ControlsBackend.Current.On(DefaultControls.SET.Id, HandleSet);
        ControlsBackend.Current.On(DefaultControls.Increase.Id, HandleIncrease);
        ControlsBackend.Current.On(DefaultControls.Decrease.Id, HandleDecrease);
        ControlsBackend.Current.On(DefaultControls.Assist.Id, HandleAssist);
    }

    public float FromScientificUnits(float speedInMps, Units? overrideDisplayUnits = null)
    {
        var units = overrideDisplayUnits ?? DisplayUnits;
        return units switch
        {
            Units.Metric => speedInMps * 3.6f,       // m/s to km/h
            Units.Imperial => speedInMps * 2.23693f, // m/s to mph
            Units.Scientific => speedInMps,          // m/s
            _ => speedInMps
        };
    }

    public float ToScientificUnits(float speedInDisplayUnits, Units? overrideDisplayUnits = null)
    {
        var units = overrideDisplayUnits ?? DisplayUnits;
        return units switch
        {
            Units.Metric => speedInDisplayUnits / 3.6f,       // km/h to m/s
            Units.Imperial => speedInDisplayUnits / 2.23693f, // mph to m/s
            Units.Scientific => speedInDisplayUnits,          // m/s
            _ => speedInDisplayUnits
        };
    }

    private void UpdateTelemetryData(GameTelemetryData data)
    {
        _latestTelemetryData = data;
    }

    private void HandleSet(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if(b == true) return; // key down event

        if (PauseLongitudinalAssist)
        {
            PauseLongitudinalAssist = false;
            DesiredSpeed = _latestTelemetryData.truckFloat.speed;
        }
        else
        {
            PauseLongitudinalAssist = true;
            PauseSteeringAssist = true; // we also pause steering as it doesn't really
                                        // make sense to have it active when longitudinal assist is paused.
        }
    }

    private void HandleIncrease(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if(b == true) return; // key down event

        if (PauseLongitudinalAssist)
        {
            PauseLongitudinalAssist = false;
            DesiredSpeed = _latestTelemetryData.truckFloat.speed;
            return;
        }

        switch (DisplayUnits)
        {
            case Units.Metric:
                DesiredSpeed += ToScientificUnits(1.0f, Units.Metric); // 1 km/h in m/s
                break;
            case Units.Imperial:
                DesiredSpeed += ToScientificUnits(1.0f, Units.Imperial); // 1 mph in m/s
                break;
            case Units.Scientific:
                DesiredSpeed += 1f; // 1 m/s
                break;
        }
    }

    private void HandleDecrease(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if(b == true) return; // key down event

        if (PauseLongitudinalAssist)
        {
            PauseLongitudinalAssist = false;
            DesiredSpeed = _latestTelemetryData.truckFloat.speed;
            return;
        }

        switch (DisplayUnits)
        {
            case Units.Metric:
                DesiredSpeed -= ToScientificUnits(1.0f, Units.Metric); // 1 km/h in m/s
                break;
            case Units.Imperial:
                DesiredSpeed -= ToScientificUnits(1.0f, Units.Imperial); // 1 mph in m/s
                break;
            case Units.Scientific:
                DesiredSpeed -= 1f; // 1 m/s
                break;
        }
    }

    private void HandleAssist(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if(b == true) return; // key down event

        if (PauseSteeringAssist)
        {
            PauseSteeringAssist = false;
        }
        else
        {
            DesiredSteeringLevel++;
            if (DesiredSteeringLevel > SteeringAssists.Full)
            {
                DesiredSteeringLevel = SteeringAssists.None;
            }
        }
    }
}
