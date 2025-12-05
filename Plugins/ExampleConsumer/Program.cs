using ETS2LA.Shared;
using ETS2LA.Logging;

[assembly: PluginInformation("ExampleConsumer", "An example data provider plugin.")]
namespace ExampleConsumer
{
    public class MyConsumer : Plugin
    {
        public override void Init(IEventBus bus)
        {
            base.Init(bus);
            _bus?.Subscribe<float>("ExampleProvider.Time", OnTimeReceived);
            _bus?.Subscribe<GameTelemetryData>("GameTelemetry.Data", OnGameTelemetryReceived);
        }

        private void OnTimeReceived(float data)
        {
            if (!_IsRunning)
                return;

            // Logger.Info($"MyConsumer received time: {data}");
            // Logger.Info($"Delay to receive data: {DateTime.Now.Microsecond - data} microseconds");
        }

        int dataCount = 0;
        int lastSecond = DateTime.Now.Second;
        private void OnGameTelemetryReceived(GameTelemetryData data)
        {
            if (!_IsRunning)
                return;

            dataCount++;
            if (DateTime.Now.Second != lastSecond)
            {
                Logger.Info($"MyConsumer received {dataCount} GameTelemetry data packets in the last second.");
                lastSecond = DateTime.Now.Second;
                dataCount = 0;
            }
        }
    }
}