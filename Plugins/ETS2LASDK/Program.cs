#pragma warning disable CA1416 // We check OS compatibility.
using System.IO.MemoryMappedFiles;
using ETS2LA.Shared;
using ETS2LA.Backend.Events;
using ETS2LA.Logging;

namespace ETS2LASDK
{
    public class OutputConsumer : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Control Provider",
            Description = "Uses ets2la_plugin to send control information provided by other plugins.",
            AuthorName = "Tumppi066",
        };

        // Tickrate just affects how often the plugin checks
        // for stale data.
        public override float TickRate => 1.0f;
        string mmapName = "Local\\ETS2LAPluginInput";
        string mmapNameLinux = "/dev/shm/ETS2LAPluginInput";
        int mmapSize = 22;

        // TODO: Convert to weight based system.
        //       Plugins can send data with their name and a weight
        //       and then the output is weighted based on those values.

        long lastSteeringWrite = -1;
        float lastSteering;
        long lastThrottleWrite = -1;
        float lastThrottle;
        long lastBrakeWrite = -1;
        float lastBrake;

        public override void Init()
        {
            base.Init();
            // Listen to events from other plugins.
            Events.Current.Subscribe<float>("ETS2LA.Output.Steering", WriteSteering);
            Events.Current.Subscribe<float>("ETS2LA.Output.Throttle", WriteThrottle);
            Events.Current.Subscribe<float>("ETS2LA.Output.Brake", WriteBrake);
        }

        public override void Tick()
        {
            long now = DateTimeOffset.Now.ToUnixTimeSeconds();
            if (now > lastSteeringWrite + 1 && lastSteering != 0.0f)
            {
                WriteSteering(0.0f);
            }
            if (now > lastBrakeWrite + 1 && lastBrake != 0.0f)
            {
                WriteBrake(0.0f);
            }
            if (now > lastThrottleWrite + 1 && lastThrottle != 0.0f)
            {
                WriteThrottle(0.0f);
            }
        }

        private void WriteSteering(float steering)
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            try
            {
                #if WINDOWS
                    mmf = MemoryMappedFile.OpenExisting(mmapName);
                # else
                    mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
                # endif

                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Write);
                accessor.Write(0, -steering);
                accessor.Write(4, steering != 0.0f);
                accessor.Write(15, (int)DateTimeOffset.Now.ToUnixTimeSeconds());
                lastSteeringWrite = DateTimeOffset.Now.ToUnixTimeSeconds();
                lastSteering = steering;
            }
            catch (FileNotFoundException)
            {
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error writing to memory mapped file: {ex.Message}");
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }
        }

        private void WriteThrottle(float throttle)
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            try
            {
                #if WINDOWS
                    mmf = MemoryMappedFile.OpenExisting(mmapName);
                # else
                    mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
                # endif

                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Write);
                accessor.Write(5, throttle);
                accessor.Write(9, throttle != 0.0f);
                accessor.Write(15, (int)DateTimeOffset.Now.ToUnixTimeSeconds());
                lastThrottleWrite = DateTimeOffset.Now.ToUnixTimeSeconds();
                lastThrottle = throttle;
            }
            catch (FileNotFoundException)
            {
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error writing to memory mapped file: {ex.Message}");
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }
        }

        private void WriteBrake(float brake)
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            try
            {
                #if WINDOWS
                    mmf = MemoryMappedFile.OpenExisting(mmapName);
                # else
                    mmf = MemoryMappedFile.CreateFromFile(mmapNameLinux);
                # endif

                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Write);
                accessor.Write(10, brake);
                accessor.Write(14, brake != 0.0f);
                accessor.Write(15, (int)DateTimeOffset.Now.ToUnixTimeSeconds());
                lastBrakeWrite = DateTimeOffset.Now.ToUnixTimeSeconds();
                lastBrake = brake;
            }
            catch (FileNotFoundException)
            {
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error writing to memory mapped file: {ex.Message}");
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }
        }
    }
}