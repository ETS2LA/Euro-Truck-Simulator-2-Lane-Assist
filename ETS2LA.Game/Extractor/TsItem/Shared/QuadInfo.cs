using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem.Shared
{
    public static class QuadInfo
    {
        public static int Parse(TsSector sector, int startOffset)
        {
            if (sector.Version >= 884)
                return Parse884(sector, startOffset);
            Logger.Error($"Unknown version ({sector.Version}) for QuadInfo " +
                                  $"in file '{Path.GetFileName(sector.FilePath)}' @ {startOffset} from '{sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            return 0;
        }

        private static int Parse884(TsSector sector, int startOffset)
        {
            var fileOffset = startOffset;
            var materialCount = MemoryHelper.ReadUInt16(sector.Stream, fileOffset);
            var colorCount =
                MemoryHelper.ReadUInt16(sector.Stream,
                    fileOffset += 0x02 + 0x0A * materialCount); // 0x02(materialCount) + materials
            var storageCount =
                MemoryHelper.ReadInt32(sector.Stream,
                    fileOffset += 0x02 + 0x04 * colorCount + 0x04); // 0x02(colorCount) + color + 0x04(size_x, size_y)
            var offsetCount =
                MemoryHelper.ReadInt32(sector.Stream,
                    fileOffset += 0x04 + 0x04 * storageCount); // 0x04(storageCount) + storage
            var normalCount =
                MemoryHelper.ReadInt32(sector.Stream,
                    fileOffset += 0x04 + 0x10 * offsetCount); // 0x04(offsetCount) + offsets
            fileOffset += 0x04 + 0x10 * normalCount; // 0x04(normalCount) + normals
            return fileOffset - startOffset;
        }
    }
}
