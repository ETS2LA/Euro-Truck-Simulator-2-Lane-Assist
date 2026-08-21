using ETS2LA.Backend.Events;

namespace ETS2LA.Game.Telemetry;


class TelemetryEvents
{
    private static readonly Lazy<TelemetryEvents> _instance = new(() => new TelemetryEvents());
    public static TelemetryEvents Current => _instance.Value;

    private Dictionary<string, object> previousEventValues = new Dictionary<string, object> {
        { "truckFloat.speedLimit", 0f }
    };

    public void UpdateEvents(GameTelemetryData data)
    {
        if (data.truckFloat.speedLimit != (float)previousEventValues["truckFloat.speedLimit"])
        {
            previousEventValues["truckFloat.speedLimit"] = data.truckFloat.speedLimit;
            Events.Current.Publish("TelemetryEvents.SpeedLimitChanged", data.truckFloat.speedLimit);
        }
    }
}