#pragma warning disable CA1416 // We check OS compatibility.
using System.IO.MemoryMappedFiles;
using ETS2LA.Shared;
using ETS2LA.Backend.Events;
using ETS2LA.Logging;
using System.Numerics;

namespace ETS2LASDK
{
    public class CameraProvider : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Camera Provider",
            Description = "Reads camera data from ets2la_plugin and publishes it to the event bus.",
            AuthorName = "Tumppi066",
        };

        public override float TickRate => 60.0f;
        string mmapName = "Local\\ETS2LACameraProps";
        MemoryReader? _reader;
        int mmapSize = 36;

        public override void Tick()
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            byte[] buffer = new byte[mmapSize];
            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                Logger.Warn("Memory mapped file not found. Please open ETS2 or ATS and enable the SDK.");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error initializing memory mapped file: {ex.Message}");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }


            int offset = 0;
            Camera camera = new Camera();
            camera.fov = _reader.ReadFloat(offset); offset += 4;
            camera.position = new Vector3(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8)
            ); offset += 12;
            camera.cx = _reader.ReadInt16(offset); offset += 2;
            camera.cy = _reader.ReadInt16(offset); offset += 2;
            camera.rotation = new ETS2LA.Shared.Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;

            Events.Current.Publish<Camera>("ETS2LASDK.Camera", camera);
        }
    }

    public class TrafficProvider : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Traffic Provider",
            Description = "Reads traffic data from ets2la_plugin and publishes it to the event bus.",
            AuthorName = "Tumppi066",
        };

        public override float TickRate => 20.0f;
        string mmapName = "Local\\ETS2LATraffic";
        MemoryReader? _reader;
        int mmapSize = 5360;

        public override void Tick()
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            byte[] buffer = new byte[mmapSize];
            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                Logger.Warn("Memory mapped file not found. Please open ETS2 or ATS and enable the SDK.");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error initializing memory mapped file: {ex.Message}");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }

            TrafficData data = new TrafficData();
            TrafficVehicle[] vehicles = new TrafficVehicle[40];
            int offset = 0;
            for (int i = 0; i < 40; i++)
            {
                TrafficVehicle vehicle = new TrafficVehicle();
                vehicle.position = new Vector3(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8)
                ); offset += 12;

                vehicle.rotation = new ETS2LA.Shared.Quaternion(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8),
                    _reader.ReadFloat(offset + 12)
                ); offset += 16;

                vehicle.size = new Vector3(
                    _reader.ReadFloat(offset),     // Width
                    _reader.ReadFloat(offset + 4), // Height
                    _reader.ReadFloat(offset + 8)  // Length
                ); offset += 12;

                vehicle.speed = _reader.ReadFloat(offset); offset += 4;
                vehicle.acceleration = _reader.ReadFloat(offset); offset += 4;
                vehicle.trailer_count = _reader.ReadInt16(offset); offset += 2;
                vehicle.id = _reader.ReadInt16(offset); offset += 2;

                vehicle.isTMP = _reader.ReadBool(offset); offset += 1;
                vehicle.isTrailer = _reader.ReadBool(offset); offset += 1;

                TrafficTrailer[] trailers = new TrafficTrailer[vehicle.trailer_count];
                for (int j = 0; j < vehicle.trailer_count; j++)
                {
                    TrafficTrailer trailer = new TrafficTrailer();
                    trailer.position = new Vector3(
                        _reader.ReadFloat(offset),
                        _reader.ReadFloat(offset + 4),
                        _reader.ReadFloat(offset + 8)
                    ); offset += 12;

                    trailer.rotation = new ETS2LA.Shared.Quaternion(
                        _reader.ReadFloat(offset),
                        _reader.ReadFloat(offset + 4),
                        _reader.ReadFloat(offset + 8),
                        _reader.ReadFloat(offset + 12)
                    ); offset += 16;

                    trailer.size = new Vector3(
                        _reader.ReadFloat(offset),     // Width
                        _reader.ReadFloat(offset + 4), // Height
                        _reader.ReadFloat(offset + 8)  // Length
                    ); offset += 12;
                    trailers[j] = trailer;
                }

                // Correct offset if no trailers (or under 2)
                if (vehicle.trailer_count < 2)
                {
                    offset += 40 * (2 - vehicle.trailer_count);
                }

                vehicle.trailers = trailers;
                vehicles[i] = vehicle;
            }
            data.vehicles = vehicles;
            Events.Current.Publish<TrafficData>("ETS2LASDK.Traffic", data);
        }
    }

    public class SemaphoreProvider : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Semaphore Provider",
            Description = "Reads semaphore (traffic light) data from ets2la_plugin and publishes it to the event bus.",
            AuthorName = "Tumppi066",
        };
        
        // Semaphores are static, no point in running them at high 
        // tick rates. Just enough where it won't feel slow to respond.
        public override float TickRate => 5.0f;
        string mmapName = "Local\\ETS2LASemaphore";
        MemoryReader? _reader;
        int mmapSize = 2080;

        public override void Tick()
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            byte[] buffer = new byte[mmapSize];
            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                Logger.Warn("Memory mapped file not found. Please open ETS2 or ATS and enable the SDK.");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error initializing memory mapped file: {ex.Message}");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }

            SemaphoreData data = new SemaphoreData();
            data.semaphores = new ETS2LA.Shared.Semaphore[40];
            int offset = 0;
            for (int i = 0; i < 40; i++)
            {
                ETS2LA.Shared.Semaphore semaphore = new ETS2LA.Shared.Semaphore();
                semaphore.position = new Vector3(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8)
                ); offset += 12;

                semaphore.cx = _reader.ReadFloat(offset); offset += 4;
                semaphore.cy = _reader.ReadFloat(offset); offset += 4;

                semaphore.rotation = new ETS2LA.Shared.Quaternion(
                    _reader.ReadFloat(offset),
                    _reader.ReadFloat(offset + 4),
                    _reader.ReadFloat(offset + 8),
                    _reader.ReadFloat(offset + 12)
                ); offset += 16;

                semaphore.type = (ETS2LA.Shared.SemaphoreType)_reader.ReadInt(offset); offset += 4;
                semaphore.time_remaining = _reader.ReadFloat(offset); offset += 4;
                semaphore.state = _reader.ReadInt(offset); offset += 4;
                semaphore.id = _reader.ReadInt(offset); offset += 4;

                data.semaphores[i] = semaphore;
            }

            Events.Current.Publish<SemaphoreData>("ETS2LASDK.Semaphores", data);
        }
    }

    public class NavigationProvider : Plugin
    {

        public override PluginInformation Info => new PluginInformation
        {
            Name = "Navigation Provider",
            Description = "Reads navigation data from ets2la_plugin and publishes it to the event bus.",
            AuthorName = "Tumppi066",
        };

        // Navigation won't be updating often, so a low tick rate is fine.
        public override float TickRate => 0.1f;
        string mmapName = "Local\\ETS2LARoute";
        MemoryReader? _reader;
        int mmapSize = 96000;

        public override void Tick()
        {
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                return;
            }

            byte[] buffer = new byte[mmapSize];
            try
            {
                mmf = MemoryMappedFile.OpenExisting(mmapName);
                accessor = mmf.CreateViewAccessor(0, mmapSize, MemoryMappedFileAccess.Read);
                accessor.ReadArray(0, buffer, 0, mmapSize);
                _reader = new MemoryReader(buffer);
            }
            catch (FileNotFoundException)
            {
                Logger.Warn("Memory mapped file not found. Please open ETS2 or ATS and enable the SDK.");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            catch (Exception ex)
            {
                Logger.Error($"Error initializing memory mapped file: {ex.Message}");
                Thread.Sleep(10000);
                _reader = null;
                return;
            }
            finally
            {
                accessor?.Dispose();
                mmf?.Dispose();
            }

            NavigationData data = new NavigationData();
            data.entries = new NavigationEntry[6000];
            int offset = 0;
            for (int i = 0; i < 6000; i++)
            {
                NavigationEntry entry = new NavigationEntry();
                entry.nodeUid = _reader.ReadLongLong(offset); offset += 8;
                entry.distanceToEnd = _reader.ReadFloat(offset); offset += 4;
                entry.timeToEnd = _reader.ReadFloat(offset); offset += 4;
                data.entries[i] = entry;
            }

            Events.Current.Publish<NavigationData>("ETS2LASDK.Navigation", data);
        }
    }
    

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
                mmf = MemoryMappedFile.OpenExisting(mmapName);
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
                mmf = MemoryMappedFile.OpenExisting(mmapName);
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
                mmf = MemoryMappedFile.OpenExisting(mmapName);
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