using ETS2LA.Controls;
using ETS2LA.Controls.Defaults;
using ETS2LA.Backend.Events;
using ETS2LA.Telemetry;
using ETS2LA.Settings.Global;
using ETS2LA.Game;
using ETS2LA.UI.Notifications;

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

/// <summary>
///  This state contains the most important ETS2LA variables. Most plugins
///  will use it to follow the user's preferences and read the game data.
/// </summary>
public class ApplicationState
{
    private static readonly Lazy<ApplicationState> _instance = new(() => new ApplicationState());
    public static ApplicationState Current => _instance.Value;

    public ApplicationState()
    {
        // TODO: Move notifications from ETS2LA.UI to ETS2LA.Notifications
        GameHandler.Current.SetNotificationHandler(NotificationHandler.Current);

        Events.Current.Subscribe<GameTelemetryData>(GameTelemetry.Current.EventString, HandleTelemetryUpdate);

        ControlsBackend.Current.On(DefaultControls.SET.Id, HandleSet);
        ControlsBackend.Current.On(DefaultControls.Increase.Id, HandleIncrease);
        ControlsBackend.Current.On(DefaultControls.Decrease.Id, HandleDecrease);
        ControlsBackend.Current.On(DefaultControls.Assist.Id, HandleAssist);

        assistanceSettings = AssistanceSettings.Current;
    }

    private void HandleTelemetryUpdate(GameTelemetryData data)
    {
        latestTelemetryData = data;
        if (data.sdkActive)
        {
            IsGameRunning = true;
            RunningGameType = data.scsValues.game == "ETS2" ? GameType.EuroTruckSimulator2
                                                            : GameType.AmericanTruckSimulator;
            RunningGameVersion = data.scsValues.versionMajor.ToString() + "." 
                               + data.scsValues.versionMinor.ToString();

            if(parsingTask == null)
                // This function will run until game data is successfully parsed.
                // TODO: Handle switching game types!
                WaitForParseSuccessful();
        }
    }



    // MARK: Self-Driving Related
    // NOTE: This class is organized by *category* and not variable/function type.
    //       This makes the most sense to avoid having lots of variables back to back
    //       far from the relevant functions. It is slightly unconventional though.
    //       Follow the marks :+1:



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
    private GameTelemetryData latestTelemetryData = new();
    private AssistanceSettings assistanceSettings;

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

    // The functions below are for handling control events.
    // If determining what they do is hard via code, then take a look at the 
    // example at https://docs.ets2la.com/docs/Rewrite/UserInput#how-to-listen-to-registered-controls

    private void HandleSet(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if(b == true) return; // key down event

        if (PauseLongitudinalAssist)
        {
            PauseLongitudinalAssist = false;
            if (assistanceSettings.SetSpeedBehaviourOption == SetSpeedBehaviour.CurrentSpeed)
                DesiredSpeed = latestTelemetryData.truckFloat.speed;
            else if (assistanceSettings.SetSpeedBehaviourOption == SetSpeedBehaviour.SpeedLimit)
                DesiredSpeed = latestTelemetryData.truckFloat.speedLimit;
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
            DesiredSpeed = latestTelemetryData.truckFloat.speed;
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
            DesiredSpeed = latestTelemetryData.truckFloat.speed;
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



    // MARK: Map Data Related



    public bool IsGameRunning { get; set; } = false;
    public GameType? RunningGameType { get; set; }
    public string? RunningGameVersion { get; set; }
    private Task parsingTask;
    public Installation? RunningGame { get; set; }

    private async Task WaitForParseSuccessful()
    {
        if(parsingTask != null)
            return;

        while (true)
        {
            foreach(Installation install in GameHandler.Current.Installations)
            {
                if (RunningGame != null)
                    break;
                
                if(install.Type == RunningGameType)
                {
                    install.Version = RunningGameVersion;
                    parsingTask = Task.Run(async () =>
                    {
                        bool success = install.Parse();
                        if (success)
                            RunningGame = install;
                    });
                    await parsingTask;
                }
            }

            if (RunningGame != null)
                break;

            await Task.Delay(5000);
        }
    }
}
