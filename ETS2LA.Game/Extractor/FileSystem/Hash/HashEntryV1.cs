using System;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using ETS2LA.Game.Extractor.FileSystem.libdeflate;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.FileSystem.Hash
{
    public class HashEntryV1 : Entry
    {
        /// <summary>
        /// <para>0001 => Directory</para>
        /// <para>0010 => Compressed</para>
        /// </summary>
        public uint Flags { get; set; }
        public uint Crc { get; set; }

        public HashEntryV1(HashArchiveFile fsFile) : base(fsFile)
        {
        }

        public override byte[] Read()
        {
            var buff = MemoryHelper.ReadBytes(GetArchiveFile().Br, (long)GetOffset(), (int)GetCompressedSize());
            return IsCompressed() ? Inflate(buff) : buff;
        }

        protected override byte[] Inflate(byte[] buff)
        {
            var dest = new byte[(int)GetSize()];
            try
            {
                var decompressor = LibdeflateWrapper.libdeflate_alloc_decompressor();
                if (decompressor == IntPtr.Zero)
                {
                    Logger.Error(
                        $"Could not init zlib decompressor for entry {GetHash()} (0x{GetHash():x}) of '{GetArchiveFile().GetPath()}'");
                    return Array.Empty<byte>();
                }

                var result = LibdeflateWrapper.libdeflate_zlib_decompress(decompressor, buff,
                    (UIntPtr)GetCompressedSize(),
                    dest,
                    (UIntPtr)GetSize(), out var bytesWritten);

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
            catch (Exception e)
            {
                Logger.Error($"Could not inflate hash entry: 0x{GetHash():X}, of '{GetArchiveFile().GetPath()}', reason: {e.Message}");
                return Array.Empty<byte>();
            }
            return dest;
        }

        public override bool IsDirectory()
        {
            return MemoryHelper.IsBitSet(Flags, 0);
        }
        public override bool IsCompressed()
        {
            return MemoryHelper.IsBitSet(Flags, 1);
        }
    }
}