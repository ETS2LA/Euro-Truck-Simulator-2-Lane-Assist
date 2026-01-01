using System.Collections.Generic;
using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsMapAreaItem : TsItem
    {
        public List<ulong> NodeUids { get; private set; }
        public uint ColorIndex { get; private set; }
        public bool DrawOver { get; private set; }

        public bool IsSecret { get; private set; }

        public TsMapAreaItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            TsMapAreaItem825(startOffset);
        }

        public void TsMapAreaItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            DrawOver = MemoryHelper.ReadUint8(Sector.Stream, fileOffset) != 0;
            DlcGuard = MemoryHelper.ReadUint8(Sector.Stream, fileOffset + 0x01);

            Hidden = MemoryHelper.IsBitSet(Flags, 3); // navigation map area
            IsSecret = MemoryHelper.IsBitSet(MemoryHelper.ReadUint8(Sector.Stream, fileOffset), 4);

            NodeUids = new List<ulong>();

            var nodeCount = MemoryHelper.ReadInt32(Sector.Stream, fileOffset += 0x05); // 0x05(flags)
            fileOffset += 0x04; // 0x04(nodeCount)
            for (var i = 0; i < nodeCount; i++)
            {
                NodeUids.Add(MemoryHelper.ReadUInt64(Sector.Stream, fileOffset));
                fileOffset += 0x08;
            }

            ColorIndex = MemoryHelper.ReadUInt32(Sector.Stream, fileOffset);
            fileOffset += 0x04; // 0x04(colorIndex)
            BlockSize = fileOffset - startOffset;
        }
    }
}
