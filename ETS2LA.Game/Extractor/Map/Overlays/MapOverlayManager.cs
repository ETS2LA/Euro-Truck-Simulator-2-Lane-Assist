using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using ETS2LA.Game.Extractor.FileSystem;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.Map.Overlays
{
    internal class MapOverlayManager
    {
        private readonly ConcurrentDictionary<ulong, OverlayImage> _overlayImages =
            new ConcurrentDictionary<ulong, OverlayImage>();

        private readonly ConcurrentBag<MapOverlay> _overlays = new ConcurrentBag<MapOverlay>();

        internal MapOverlay CreateOverlay(string overlayName, OverlayType overlayType)
        {
            var overlayImage = GetOrCreateOverlayImage(overlayName, overlayType);
            if (overlayImage == null || !overlayImage.Valid) return null;

            return new MapOverlay(overlayImage, overlayType, overlayName);
        }

        internal void AddOverlay(MapOverlay overlay)
        {
            _overlays.Add(overlay);
        }

        internal bool AddOverlay(string overlayName, OverlayType overlayType, float posX, float posY,
            string typeName, byte dlcGuard, bool isSecret = false)
        {
            var overlay = CreateOverlay(overlayName, overlayType);

            if (overlay == null) return false;

            overlay.SetTypeName(typeName);
            overlay.SetPosition(posX, posY);
            overlay.SetSecret(isSecret);
            overlay.SetDlcGuard(dlcGuard);

            AddOverlay(overlay);

            return true;
        }

        /// <summary>
        ///     Reads the .mat file at the given path, reads the texture file path and returns an <see cref="OverlayImage" /> if
        ///     the texture path is valid
        /// </summary>
        /// <param name="matFilePath"></param>
        /// <returns>
        ///     <see cref="OverlayImage" /> for the given path
        ///     <para>Null if file is not found</para>
        /// </returns>
        private OverlayImage GetOverlayImageFromMatFile(string matFilePath)
        {
            var mat = new Material(matFilePath);

            if (!mat.Parse())
            {
                Logger.Error($"Error reading material file '{matFilePath}'");
                return null;
            }

            return new OverlayImage(mat);
        }

        private OverlayImage GetOrCreateOverlayImage(string overlayName, OverlayType overlayType)
        {
            return null;
            
            if (overlayName == "") return null;

            string path;
            switch (overlayType)
            {
                case OverlayType.Road:
                    path = $"material/ui/map/road/road_{overlayName}.mat";
                    break;
                case OverlayType.Company:
                    path = $"material/ui/company/small/{overlayName}.mat";
                    break;
                case OverlayType.Map:
                    path = $"material/ui/map/{overlayName}.mat";
                    break;
                case OverlayType.BusStop:
                    path = $"tsmap/overlay/{overlayName}.mat";
                    break;
                default:
                    path = $"{PathHelper.EnsureLocalPath(overlayName)}.mat";
                    break;
            }

            var hash = CityHash.CityHash64(path);

            if (_overlayImages.ContainsKey(hash)) return _overlayImages[hash];

            var overlayImage = GetOverlayImageFromMatFile(path);
            if (overlayImage == null)
            {
                Logger.Error($"Could not load overlay image for {path}");
                return null;
            }

            overlayImage.Parse();
            _overlayImages.TryAdd(hash, overlayImage);
            return overlayImage;
        }

        internal List<MapOverlay> GetOverlays()
        {
            return _overlays.ToList();
        }

        internal int GetOverlayImagesCount()
        {
            return _overlayImages.Count;
        }
    }
}