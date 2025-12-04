using ETS2LA.Shared;

[assembly: PluginInformation("ExampleProvider", "An example data provider plugin.")]
namespace ExampleProvider
{
    public class MyProvider : Plugin
    {
        public override float TickRate => 1.0f;

        public override void Tick()
        {
            if (_bus == null)
                return;
            
            _bus.Publish<float>("ExampleProvider.Time", System.DateTime.Now.Microsecond);
        }
    }
}