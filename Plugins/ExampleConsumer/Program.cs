using ETS2LA.Shared;
using ETS2LA.Logging;
using Huskui.Avalonia.Models;

namespace ExampleConsumer
{
    public class MyConsumer : Plugin
    {
        public override float TickRate => 60f;
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Example Consumer",
            Description = "An example data consumer plugin.",
            AuthorName = "Tumppi066",
        };

        public override void OnEnable()
        {
            base.OnEnable();
            _bus?.Subscribe<float>("ExampleProvider.Time", OnTimeReceived);
            _bus?.Subscribe<GameTelemetryData>("GameTelemetry.Data", OnGameTelemetryReceived);
            _bus?.Subscribe<Camera>("ETS2LASDK.Camera", OnCameraReceived);
            _bus?.Subscribe<TrafficData>("ETS2LASDK.Traffic", OnTrafficReceived);
            _bus?.Subscribe<SemaphoreData>("ETS2LASDK.Semaphores", OnSemaphoreReceived);
            _bus?.Subscribe<NavigationData>("ETS2LASDK.Navigation", OnNavigationReceived);
        }

        public override void OnDisable()
        {
            base.OnDisable();
            _window?.CloseNotification("ExampleConsumer.Speed");
            _window?.CloseNotification("ExampleConsumer.RPM");
        }

        private float output = 0;
        private float speed = 0;
        private float rpm = 0;
        public override void Tick()
        {
            // sine wave output from -1 to 1
            double time = DateTime.Now.TimeOfDay.TotalSeconds;
            output = (float)Math.Sin(time * 2 * Math.PI / 8);

            // _window?.SendNotification(new Notification
            // {
            //     Id = "ExampleConsumer.Speed",
            //     Title = "Truck Speed",
            //     Content = $"{speed:F2} km/h",
            //     Level = GrowlLevel.Information,
            //     Progress = speed / (100 * 3.6f) * 100f,
            //     IsProgressIndeterminate = false,
            //     CloseAfter = 0 
            // });

            // _window?.SendNotification(new Notification
            // {
            //     Id = "ExampleConsumer.RPM",
            //     Title = "Engine RPM",
            //     Content = $"{rpm:F0} RPM",
            //     Level = GrowlLevel.Information,
            //     Progress = rpm / 3000.0f * 100f,
            //     IsProgressIndeterminate = false,
            //     CloseAfter = 0 
            // });

            _bus?.Publish<float>("ForceFeedback.Output", output);
            _window?.SendNotification(new Notification
            {
                Id = "ExampleConsumer.Output",
                Title = "Steering Output",
                Content = $"Output: {output:F2}",
                Level = GrowlLevel.Information,
                Progress = (output + 1.0f) / 2.0f * 100f,
                IsProgressIndeterminate = false,
                CloseAfter = 0 
            });

            // SDKControlEvent controlEvent = new SDKControlEvent
            // {
            //     steering = output,
            //     light = true,
            //     hblight = false
            // };
            // _bus?.Publish<SDKControlEvent>("ETS2LA.Output.Event", controlEvent);
        }

        private void OnTimeReceived(float data)
        {
            if (!_IsRunning)
                return;

            // Logger.Info($"MyConsumer received time: {data}");
            // Logger.Info($"Delay to receive data: {DateTime.Now.Microsecond - data} microseconds");
        }

        private void OnGameTelemetryReceived(GameTelemetryData data)
        {
            if (!_IsRunning)
                return;

            speed = data.truckFloat.speed;
            rpm = data.truckFloat.engineRpm;
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

        private void OnSemaphoreReceived(SemaphoreData data)
        {
            if (!_IsRunning)
                return;

            foreach (var semaphore in data.semaphores)
            {
                if (semaphore.type != SemaphoreType.TRAFFICLIGHT)
                    continue;
                //Logger.Info($"Semaphore ID: {semaphore.id}, Type: {semaphore.type}, State: {semaphore.state}, Time Remaining: {semaphore.time_remaining}");
            }
        }

        private void OnNavigationReceived(NavigationData data)
        {
            if (!_IsRunning)
                return;

            // int valid = 0;
            // foreach (var entry in data.entries)
            // {
            //     if (entry.nodeUid != 0)
            //         valid++;
            // }
            // Logger.Info($"MyConsumer received {valid} valid navigation waypoints.");
        }
    }
}