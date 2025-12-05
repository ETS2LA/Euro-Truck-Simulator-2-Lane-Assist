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
}