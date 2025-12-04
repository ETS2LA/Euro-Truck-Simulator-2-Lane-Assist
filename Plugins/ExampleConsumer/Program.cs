using ETS2LA.Shared;

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
            Console.WriteLine($"MyConsumer received time: {data}");
            Console.WriteLine($"Delay to receive data: {DateTime.Now.Microsecond - data} microseconds");
        }
    }
}