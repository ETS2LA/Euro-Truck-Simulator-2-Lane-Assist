using System;
using System.Linq;
using System.Runtime.InteropServices;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.FileSystem.libdeflate
{
    // https://github.com/microsoft/DirectStorage/blob/main/GDeflate/GDeflate/TileStream.h
    internal struct TileStream
    {
        internal byte Id { get; set; }

        internal byte Magic { get; set; }

        internal ushort NumTiles { get; set; }

        internal uint TileSizeData { get; set; }
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct libdeflate_gdeflate_in_page
    {
        public IntPtr data;
        public uint nbytes;
    }

    internal class Gdeflate
    {
        public const uint KDefaultTileSize = 64 * 1024;

        internal static libdeflate_result Inflate(ref byte[] output,
            uint outputSize,
            byte[] input,
            uint inputSize)
        {
            var header = new TileStream
            {
                Id = input[0],
                Magic = input[1],
                NumTiles = MemoryHelper.ReadUInt16(input, 2),
                TileSizeData = MemoryHelper.ReadUInt32(input, 4)
            };

            if (header.NumTiles != 1) Logger.Error("More than 1 tile.");

            TileDecompressionJob(header, input, ref output);

            return libdeflate_result.LIBDEFLATE_SUCCESS;
        }

        // https://github.com/microsoft/DirectStorage/blob/60a909f351d18293aeae1af7e24fc38519ebe118/GDeflate/GDeflate/GDeflateDecompress.cpp#L70
        // TODO: Support multiple tiles (unknown if required)
        private static void TileDecompressionJob(TileStream header, byte[] input_pages,
            ref byte[] output)
        {
            var decompressor = LibdeflateWrapper.libdeflate_alloc_gdeflate_decompressor();

            var tileOffsetBytes = input_pages.Skip(8).ToArray();
            var tileOffsets = new uint[header.NumTiles];
            Buffer.BlockCopy(tileOffsetBytes, 0, tileOffsets, 0, header.NumTiles * 4);

            var dataStart = input_pages.Skip(8 + 4 * header.NumTiles).ToArray();
            var tileIndex = -1;

            while (true)
            {
                tileIndex++;

                if (tileIndex >= header.NumTiles)
                    break;

                var tileOffset = tileIndex > 0 ? tileOffsets[tileIndex] : 0;

                var data = dataStart.Skip((int) tileOffset).ToArray();

                var bufferPtr = Marshal.AllocHGlobal(data.Length);
                Marshal.Copy(data, 0, bufferPtr, data.Length);

                var compressedPage = new libdeflate_gdeflate_in_page
                {
                    data = bufferPtr,
                    nbytes = tileIndex < header.NumTiles - 1
                        ? tileOffsets[tileIndex + 1] - tileOffset
                        : tileOffsets[0]
                };

                var outputOffset = tileIndex * KDefaultTileSize;

                LibdeflateWrapper.libdeflate_gdeflate_decompress(
                    decompressor,
                    ref compressedPage,
                    1,
                    output,
                    KDefaultTileSize,
                    UIntPtr.Zero
                );

                Marshal.FreeHGlobal(bufferPtr);
            }

            LibdeflateWrapper.libdeflate_free_gdeflate_decompressor(decompressor);
        }
    }
}