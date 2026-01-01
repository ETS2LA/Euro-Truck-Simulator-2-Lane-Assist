using System;
using ETS2LA.Game.Extractor.FileSystem.libdeflate;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.FileSystem.Hash
{
    public class HashEntryV2 : Entry
    {
        internal ImgMetadata? _imgMetadata;
        internal PlainMetadata _plainMetadata;
        internal SampleMetadata? _sampleMetadata;
        internal PmaInfoMetadata? _pmaInfoMetadata;
        internal PmgInfoMetadata? _pmgInfoMetadata;

        public HashEntryV2(HashArchiveFile fsFile) : base(fsFile)
        {
        }

        internal uint Flags { get; set; }

        public override byte[] Read()
        {
            var buff = MemoryHelper.ReadBytes(GetArchiveFile().Br, (long) GetOffset(), (int) GetCompressedSize());
            return IsCompressed() ? Inflate(buff) : buff;
        }

        protected override byte[] Inflate(byte[] buff)
        {
            try
            {
                var dest = new byte[(int) GetSize()];
                if (_plainMetadata.CompressionMethod == HashFsCompressionMethod.Zlib)
                {
                    var decompressor = LibdeflateWrapper.libdeflate_alloc_decompressor();
                    if (decompressor == IntPtr.Zero)
                    {
                        Logger.Error(
                            $"Could not init zlib decompressor for entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}'");
                        return Array.Empty<byte>();
                    }

                    var result = LibdeflateWrapper.libdeflate_zlib_decompress(decompressor, buff,
                        (UIntPtr) GetCompressedSize(),
                        dest,
                        (UIntPtr) GetSize(), out var bytesWritten);

                    LibdeflateWrapper.libdeflate_free_decompressor(decompressor);

                    if (result != libdeflate_result.LIBDEFLATE_SUCCESS)
                    {
                        Logger.Error(
                            $"Could not extract zlib entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}'");
                        return Array.Empty<byte>();
                    }

                    if (GetSize() != bytesWritten.ToUInt32())
                    {
                        Logger.Error(
                            $"Possible incorrect zlib inflate for entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}', {bytesWritten} bytes written out of {GetSize()}");
                    }
                }
                else if (_plainMetadata.CompressionMethod == HashFsCompressionMethod.Gdeflate)
                {
                    var result = Gdeflate.Inflate(ref dest, GetSize(), buff, GetCompressedSize());

                    if (result != libdeflate_result.LIBDEFLATE_SUCCESS)
                    {
                        Logger.Error(
                            $"Could not extract gdeflate entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}'");
                        return Array.Empty<byte>();
                    }
                }
                else
                {
                    Logger.Error(
                        $"Incompatible compression method found ({(int) _plainMetadata.CompressionMethod}) for entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}'.");
                    return Array.Empty<byte>();
                }

                return dest;
            }
            catch (Exception e)
            {
                Logger.Error(
                    $"Could not inflate hash entry: 0x{GetHash():X}, of '{GetArchiveFile().GetPath()}', reason: {e.Message}");
                return Array.Empty<byte>();
            }
        }

        public override bool IsDirectory()
        {
            return MemoryHelper.IsBitSet(Flags >> 16, 0);
        }

        public override bool IsCompressed()
        {
            return GetSize() != GetCompressedSize();
        }

        public override uint GetSize()
        {
            return _plainMetadata.Size;
        }

        public override uint GetCompressedSize()
        {
            return _plainMetadata.CompressedSize;
        }

        public override ulong GetOffset()
        {
            return _plainMetadata.Offset;
        }
    }
}