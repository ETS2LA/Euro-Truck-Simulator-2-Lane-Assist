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
            _bus?.Subscribe<Camera>("ETS2LASDK.Camera", OnCameraReceived);
            _bus?.Subscribe<TrafficData>("ETS2LASDK.Traffic", OnTrafficReceived);
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

        private void OnCameraReceived(Camera camera)
        {
            if (!_IsRunning)
                return;

            // Vector3 euler = camera.rotation.ToEuler();
            // Logger.Info($"MyConsumer received camera FOV: {camera.fov}, Position: ({camera.position.X}, {camera.position.Y}, {camera.position.Z}), Rotation: ({euler.X}, {euler.Y}, {euler.Z})");
        }

        private void OnTrafficReceived(TrafficData traffic)
        {
            if (!_IsRunning)
                return;

            // Logger.Info($"MyConsumer received {traffic.vehicles.Length} traffic vehicles.");
            // Logger.Info($"First vehicle position: ({traffic.vehicles[0].position.X}, {traffic.vehicles[0].position.Y}, {traffic.vehicles[0].position.Z}), has {traffic.vehicles[0].trailer_count} trailers.");
        }
    }
}