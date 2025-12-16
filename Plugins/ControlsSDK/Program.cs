#pragma warning disable CA1416 // We check OS compatibility.
using System.IO.MemoryMappedFiles;
using ETS2LA.Logging;
using ETS2LA.Shared;

[assembly: PluginInformation("ControlsSDK", "This plugin provides a consumer for control events. Other plugins can access ETS2LA's virtual controller with it.")]
namespace ControlsSDK
{
    public class EventConsumer : Plugin
    {
        public override float TickRate => 1.0f;

        string mmapName = "Local\\SCSControls";
        int mmapSize = 0;
        Dictionary<string, int> _shmOffsets = new Dictionary<string, int>();

        MemoryMappedFile? mmf = null;
        MemoryMappedViewAccessor? accessor = null;

        public override void Init(IEventBus bus)
        {
            base.Init(bus);

            // Calculate the memory offsets for each of the variables
            int boolSize = sizeof(bool);
            int floatSize = sizeof(float);

            int offset = 0;
            foreach (var field in typeof(SDKControlEvent).GetFields())
            {
                _shmOffsets[field.Name] = offset;
                if (field.FieldType == typeof(bool?))
                    offset += boolSize;
                else if (field.FieldType == typeof(float?))
                    offset += floatSize;
            }
            mmapSize = offset;

            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            // Open the memory-mapped file, it's fine to leave it open as
            // only this plugin will ever have access to it.
            mmf = MemoryMappedFile.OpenExisting(mmapName, MemoryMappedFileRights.Write);
            accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Write);

            // And finally start listening to events
            _bus?.Subscribe<SDKControlEvent>("ETS2LA.Output.Event", OnControlEvent);
        }

        private void OnControlEvent(SDKControlEvent controlEvent)
        {
            // Loop through all properties and see if they're not null
            foreach (var prop in typeof(SDKControlEvent).GetFields())
            {
                var value = prop.GetValue(controlEvent);
                if (value != null)
                {
                    if (prop.FieldType == typeof(bool?))
                    {
                        bool boolValue = (bool)value;
                        accessor!.Write(_shmOffsets[prop.Name], boolValue);
                    }
                    else if (prop.FieldType == typeof(float?))
                    {
                        float floatValue = (float)value;
                        accessor!.Write(_shmOffsets[prop.Name], floatValue);
                    }
                }
            }
        }

        public override void Shutdown()
        {
            base.Shutdown();
            accessor?.Dispose();
            mmf?.Dispose();
        }
    }
}