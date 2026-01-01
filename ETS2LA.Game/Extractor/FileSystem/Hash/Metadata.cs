using ETS2LA.Game.Extractor.Map.Overlays;

namespace ETS2LA.Game.Extractor.FileSystem.Hash
{
    internal readonly struct PlainMetadata
    {
        private readonly uint _data0;
        private readonly uint _data1;
        private readonly uint _data2;
        private readonly uint _data3;

        internal uint CompressedSize => _data0 & 0xF_FF_FF_FF;
        internal HashFsCompressionMethod CompressionMethod => (HashFsCompressionMethod) (_data0 >> 0x1c);
        internal uint Size => _data1 & 0xF_FF_FF_FF;
        internal ulong Offset => _data3 * 0x10ul;

        public PlainMetadata(uint data0, uint data1, uint data2, uint data3)
        {
            _data0 = data0;
            _data1 = data1;
            _data2 = data2;
            _data3 = data3;
        }
    }

    internal readonly struct ImgMetadata
    {
        private readonly uint _data0;
        private readonly uint _data1;

        public ImgMetadata(uint data0, uint data1)
        {
            _data0 = data0;
            _data1 = data1;
        }

        // Thanks to mwl4 for figuring these out: https://github.com/mwl4/ConverterPIX/blob/502733681eabc659cd814d711a9fe3fdec39d450/src/structs/fs.h#L49
        internal uint Width => 1 + (_data0 & 0xFFFF); // [0] 00000000 00000000 XXXXXXXX XXXXXXXX
        internal uint Height => 1 + (_data0 >> 16); // [0] XXXXXXXX XXXXXXXX 00000000 00000000

        internal uint MipmapCount => 1 + (_data1 & 0x0F); // [1] 00000000 00000000 00000000 0000XXXX
        internal DxgiFormat Format => (DxgiFormat) ((_data1 >> 4) & 0xFF); // [1] 00000000 00000000 0000XXXX XXXX0000
        internal bool Cube => ((_data1 >> 12) & 0b11) != 0; // [1] 00000000 00000000 00XX0000 00000000
        internal uint Count => 1 + ((_data1 >> 14) & 0b111111); // [1] 00000000 0000XXXX XX000000 00000000
        internal uint PitchAlignment => 1u << ((byte)(_data1 >> 20) & 0xF); // [1] 00000000 XXXX0000 00000000 00000000
        internal uint ImageAlignment => 1u << ((byte)(_data1 >> 24) & 0xF); // [1] 0000XXXX 00000000 00000000 00000000
    }

    internal readonly struct SampleMetadata
    {
        private readonly uint _data0;

        public SampleMetadata(uint data0)
        {
            _data0 = data0;
        }
    }

    internal readonly struct PmaInfoMetadata
    {
        private readonly uint _data0; // flag
        private readonly float _data1; // anim_length
        private readonly ulong _data2; // skeleton_hash
        private readonly float _data3; // bsphere_rad
        private readonly float _data4; // bsphere_org_x
        private readonly float _data5; // bsphere_org_y
        private readonly float _data6; // bsphere_org_z

        public PmaInfoMetadata(uint data0, float data1, ulong data2, float data3, float data4, float data5, float data6)
        {
            _data0 = data0;
            _data1 = data1;
            _data2 = data2;
            _data3 = data3;
            _data4 = data4;
            _data5 = data5;
            _data6 = data6;
        }
    }

    internal readonly struct PmgInfoMetadata
    {
        private readonly ulong _data0; // skeleton_hash

        public PmgInfoMetadata(ulong skeletonHash)
        {
            _data0 = skeletonHash;
        }
    }
}