using System.IO;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.TsItem.Shared;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsBezierPatchItem : TsItem
    {
        public TsBezierPatchItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = false;

            if (Sector.Version >= 884)
                TsBezierPatchItem884(startOffset);
            else
                Logger.Error($"Unknown base file version ({Sector.Version}) for item {Type} " +
                                      $"in file '{Path.GetFileName(Sector.FilePath)}' @ {startOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
        }

        public void TsBezierPatchItem884(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags
            var vegSphereCount =
                MemoryHelper.ReadInt32(Sector.Stream,
                    fileOffset += 0x05 + 0xF1); // 0x05(flags) + 0xF1(offset to vegSphereCount)
            fileOffset +=
                0x04 + VegetationSphereBlockSize *
                vegSphereCount; // 0x04(vegSphereCount) + vegSpheres
            fileOffset += QuadInfo.Parse(Sector, fileOffset);
            BlockSize = fileOffset - startOffset;
        }
    }
}
