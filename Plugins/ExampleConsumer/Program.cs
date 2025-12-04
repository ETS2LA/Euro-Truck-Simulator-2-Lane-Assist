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
        }

        private void OnTimeReceived(float data)
        {
            if (!_IsRunning)
                return;
                
            // Logger.Info($"MyConsumer received time: {data}");
            // Logger.Info($"Delay to receive data: {DateTime.Now.Microsecond - data} microseconds");
        }
    }
}