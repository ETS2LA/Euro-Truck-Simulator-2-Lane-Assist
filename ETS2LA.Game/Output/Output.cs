using ETS2LA.Shared;
using ETS2LA.Backend.Events;

using System.Diagnostics;
using System.IO.MemoryMappedFiles;

namespace ETS2LA.Game.Output;

class GameOutput
{
    private static readonly Lazy<GameOutput> _instance = new(() => new GameOutput());
    public static GameOutput Current => _instance.Value;
    public string EventString = "ETS2LA.Game.Output.ControlEvent";

    public Dictionary<string, ControlChannel> Channels = new Dictionary<string, ControlChannel>();

    // Example:
    // "steering" : [(0.5, 1.0), (0.2, 0.5)]
    // Where the first value is the weight and the second value is the control value.
    // The channel itself doesn't matter, just their weights.
    private Dictionary<string, List<Tuple<float, float>>> curFrameFloats = new Dictionary<string, List<Tuple<float, float>>>();

    private float TickRate = 1f / 60f;

    // Legacy uses a virtual controller provided through the SCSControls plugin. This
    // system works the same as SteamInput for example.

    string legacyMapName = "Local\\SCSControls";
    string legacyMapNameLinux = "/dev/shm/SCSControls";
    int legacyMapSize = 0;
    Dictionary<string, int> legacyShmOffsets = new Dictionary<string, int>();
    MemoryMappedFile? legacyMmf = null;
    MemoryMappedViewAccessor? legacyAccessor = null;

    // Modern uses ETS2LAPlugin to write directly to the game's memory. This does
    // not however work on all devices, and it doesn't provide such an extensive list
    // of controls as the legacy system does.

    string modernMapName = "Local\\ETS2LAPluginInput";
    string modernMapNameLinux = "/dev/shm/ETS2LAPluginInput";
    int modernMapSize = 26;
    MemoryMappedFile? modernMmf = null;
    MemoryMappedViewAccessor? modernAccessor = null;

    public void Init()
    {
        // Calculate the memory offsets for each of the variables
        // for legacy mode.
        int boolSize = sizeof(bool);
        int floatSize = sizeof(float);

        int offset = 0;
        foreach (var field in typeof(ControlProperties).GetFields())
        {
            legacyShmOffsets[field.Name] = offset;
            if (field.FieldType == typeof(bool?))
                offset += boolSize;
            else if (field.FieldType == typeof(float?))
                offset += floatSize;
        }
        legacyMapSize = offset;

        // And now we can open the maps.
        #if WINDOWS
            legacyMmf = MemoryMappedFile.OpenExisting(legacyMapName);
            modernMmf = MemoryMappedFile.OpenExisting(modernMapName);
        # else
            legacyMmf = MemoryMappedFile.CreateFromFile(legacyMapNameLinux);
            modernMmf = MemoryMappedFile.CreateFromFile(modernMapNameLinux);
        # endif

        legacyAccessor = legacyMmf.CreateViewAccessor(0, legacyMapSize, MemoryMappedFileAccess.Write);
        modernAccessor = modernMmf.CreateViewAccessor(0, modernMapSize, MemoryMappedFileAccess.Write);

        // Then we start listening to events and spin up the update thread.
        Events.Current.Subscribe<ControlEvent>(EventString, OnControlEvent);
        Task.Run(Tick);
    }

    public void OnControlEvent(ControlEvent controlEvent)
    {
        string channel = controlEvent.ChannelDefinition.Id;
        if (!Channels.ContainsKey(channel))
        {
            Channels[channel] = new ControlChannel{
                Definition = controlEvent.ChannelDefinition,
                Properties = controlEvent.Properties,
                Variables = controlEvent.Variables
            };
        }
        else if (controlEvent.Variables == null || controlEvent.Properties == null)
        {
            Channels.Remove(channel);
        }
        else
        {
            Channels[channel].Properties = controlEvent.Properties;
            Channels[channel].Variables = controlEvent.Variables;
            Channels[channel].LastUpdate.Restart();
            Channels[channel].BoolsProcessed = false;
        }
    }

    private void ToggleBool(MemoryMappedViewAccessor accessor, int offset)
    {
        WriteBool(accessor, offset, true);
        Thread.Sleep(50);
        WriteBool(accessor, offset, false);
    }

    private void WriteBool(MemoryMappedViewAccessor accessor, int offset, bool value)
    {
        accessor.Write(offset, value);
    }

    private void WriteFloat(MemoryMappedViewAccessor accessor, int offset, float value)
    {
        accessor.Write(offset, value);
    }

    private void ProcessChannel(ControlChannel channel)
    {
        var boolType = channel.Properties.BooleanType;
        var weight = channel.Properties.Weight;

        foreach (var prop in typeof(ControlVariables).GetFields())
        {
            var value = prop.GetValue(channel.Variables);
            if (value != null)
            {
                if (prop.FieldType == typeof(bool?) && !channel.BoolsProcessed)
                {
                    bool boolValue = (bool)value;
                    if(boolValue && boolType == ControlBooleanType.TrueToToggle)
                        Task.Run(() => ToggleBool(legacyAccessor!, legacyShmOffsets[prop.Name]));
                    else
                        WriteBool(legacyAccessor!, legacyShmOffsets[prop.Name], boolValue);
                }

                if (prop.FieldType == typeof(float?))
                {
                    float floatValue = (float)value;

                    string propName = prop.Name;
                    if (propName == "aforward" || propName == "abackward")
                        propName = "acceleration";

                    if (!curFrameFloats.ContainsKey(prop.Name))
                        curFrameFloats[prop.Name] = new List<Tuple<float, float>>();

                    curFrameFloats[prop.Name].Add(new Tuple<float, float>(weight, floatValue));
                }
            }
        }

        channel.BoolsProcessed = true;
    }

    public void Tick()
    {
        Stopwatch tickTimer = Stopwatch.StartNew();
        while(true)
        {
            float timeLeft = TickRate - (float)tickTimer.Elapsed.TotalSeconds;
            if (timeLeft > 0)
            {   
                Thread.Sleep((int)(timeLeft * 1000));
                continue;
            }

            foreach (var channel in Channels.Values)
            {
                if (channel.Properties == null || channel.Variables == null)
                    continue;

                ProcessChannel(channel);
            }

            long time = DateTimeOffset.Now.ToUnixTimeSeconds();
            foreach (var kvp in curFrameFloats)
            {
                string propName = kvp.Key;
                List<Tuple<float, float>> values = kvp.Value;

                float totalWeight = values.Sum(v => v.Item1);
                float weightedValue = values.Sum(v => v.Item1 * v.Item2) / totalWeight;

                if(propName == "steering")
                {
                    WriteFloat(modernAccessor!, 0, -weightedValue);
                    WriteBool(modernAccessor!, 4, weightedValue != 0.0f);
                    WriteFloat(modernAccessor!, 5, time);
                }
                else if (propName == "acceleration")
                {
                    WriteFloat(modernAccessor!, 13, weightedValue);
                    WriteBool(modernAccessor!, 17, weightedValue != 0.0f);
                    WriteFloat(modernAccessor!, 18, time);
                    // TODO: For legacy x < 0 is abackward and x > 0 is aforward.
                }
                else
                {
                    WriteFloat(legacyAccessor!, legacyShmOffsets[propName], weightedValue);
                }
            }
        }

    }
}