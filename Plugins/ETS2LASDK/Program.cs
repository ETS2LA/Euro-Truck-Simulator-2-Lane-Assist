using System.IO.MemoryMappedFiles;
using ETS2LA.Shared;
using ETS2LA.Logging;

[assembly: PluginInformation("ETS2LASDK", "Provider for the custom ets2la_plugin at https://gitlab.com/ETS2LA/ets2la_plugin.")]
namespace ETS2LASDK
{
    public class CameraProvider : Plugin
    {

        public override float TickRate => 60.0f;
        string mmapName = "Local\\ETS2LACameraProps";
        MemoryReader? _reader;
        int mmapSize = 36;

        public override void Tick()
        {
            if (_bus == null)
                return;

            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                Logger.Warn("Game telemetry is only supported on Windows.");
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
            camera.rotation = new Quaternion(
                _reader.ReadFloat(offset),
                _reader.ReadFloat(offset + 4),
                _reader.ReadFloat(offset + 8),
                _reader.ReadFloat(offset + 12)
            ); offset += 16;

            _bus.Publish<Camera>("ETS2LASDK.Camera", camera);
        }
    }

    public class TrafficProvider : Plugin
    {

        public override float TickRate => 20.0f;
        string mmapName = "Local\\ETS2LATraffic";
        MemoryReader? _reader;
        int mmapSize = 5360;

        public override void Tick()
        {
            if (_bus == null)
                return;

            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                Logger.Warn("Game telemetry is only supported on Windows.");
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

                vehicle.rotation = new Quaternion(
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

                    trailer.rotation = new Quaternion(
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
            _bus.Publish<TrafficData>("ETS2LASDK.Traffic", data);
        }
    }
    
    public class SemaphoreProvider : Plugin
    {

        // Semaphores are static, no point in running them at high 
        // tick rates. Just enough where it won't feel slow to respond.
        public override float TickRate => 5.0f;
        string mmapName = "Local\\ETS2LASemaphore";
        MemoryReader? _reader;
        int mmapSize = 2080;

        public override void Tick()
        {
            if (_bus == null)
                return;
                
            MemoryMappedFile? mmf = null;
            MemoryMappedViewAccessor? accessor = null;

            // Check for other OSs
            if (Environment.OSVersion.Platform != PlatformID.Win32NT)
            {
                Logger.Warn("Game telemetry is only supported on Windows.");
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

                semaphore.rotation = new Quaternion(
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

            _bus?.Publish<SemaphoreData>("ETS2LASDK.Semaphores", data);
        }
    }
}