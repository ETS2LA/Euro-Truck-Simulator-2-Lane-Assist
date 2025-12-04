using System.IO.MemoryMappedFiles;
using ETS2LA.Shared;
using ETS2LA.Logging;
using Serilog.Debugging;

[assembly: PluginInformation("Game Telemetry", "This plugin will read game telemetry and transmit it via events.")]
namespace GameTelemetry
{
    public class GameTelemetry : Plugin
    {
        // Read game telemetry at 60FPS
        public override float TickRate => 60f;

        MemoryReader? _reader;

        string mmapName = "Local\\SCSTelemetry";
        int mmapSize = 32 * 1024;
        
        int stringSize = 64;
        int wheelSize = 14;
        int substanceSize = 25;

        Dictionary<int, string> intToDays = new Dictionary<int, string>
        {
            { 0, "Monday" },
            { 1, "Tuesday" },
            { 2, "Wednesday" },
            { 3, "Thursday" },
            { 4, "Friday" },
            { 5, "Saturday" },
            { 6, "Sunday" }
        };

        string AbsoluteToReadableTime(int absTime)
        {
            var days = absTime / 1440;
            if (days > 6)
                days %= 7;

            var hours = absTime / 60;
            if (hours > 23)
                hours %= 24;

            var minutes = absTime % 60;

            return $"{intToDays[days]} {hours:D2}:{minutes:D2}";
        }

        (string GameName, int NewOffset) ReadGame(int offset, byte[] data)
        {
            if (offset + 4 > data.Length)
                throw new ArgumentOutOfRangeException(nameof(offset), "Offset exceeds data length.");
        
            int game = BitConverter.ToInt32(data, offset);
            string gameName = game switch
            {
                1 => "ETS2",
                2 => "ATS",
                _ => "unknown"
            };
        
            return (gameName, offset + 4);
        }

        public override void Init(IEventBus bus)
        {
            base.Init(bus);
        }

        public override void Tick()
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                Logger.Warn("Game telemetry is only supported on Windows.");
                return;
            }

            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                byte[] buffer = new byte[mmapSize];
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                Logger.Warn("Memory mapped file not found.");
                _reader = null;
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error initializing memory mapped file: {ex.Message}");
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }

            if (_reader == null)
                return;

            GameTelemetryData telemetry = new GameTelemetryData();
        }
    }
}