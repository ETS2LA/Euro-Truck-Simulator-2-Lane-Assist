using System.IO;
using System.IO.Compression;
using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor.FileSystem.Zip
{
    public class ZipEntry : Entry
    {
        public ZipEntry(ZipArchiveFile fsFile) : base(fsFile)
        {
        }

        public override byte[] Read()
        {
            var buff = MemoryHelper.ReadBytes(GetArchiveFile().Br, (long)GetOffset(), (int)GetCompressedSize());
            return IsCompressed() ? Inflate(buff) : buff;
        }

        protected override byte[] Inflate(byte[] buff)
        {
            var inflatedBytes = new byte[GetSize()];
            using (var ms = new MemoryStream(buff))
            using (var ds = new DeflateStream(ms, CompressionMode.Decompress))
            {
                ds.Read(inflatedBytes, 0, (int)GetSize());

                return inflatedBytes;
            }
        }

        public override bool IsDirectory()
        {
            return GetCompressedSize() == 0;
        }

        public override bool IsCompressed()
        {
            return GetCompressedSize() != GetSize();
        }
    }
}