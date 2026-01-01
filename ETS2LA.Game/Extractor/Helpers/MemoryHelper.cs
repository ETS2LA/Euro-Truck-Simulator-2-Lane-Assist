using System.Text;
using ETS2LA.Logging;
using ETS2LA.Game.Extractor.FileSystem.libdeflate;

namespace ETS2LA.Game.Extractor.Helpers
{
    internal class MemoryHelper
    {
        internal static ushort ReadUInt16(BinaryReader br, long offset, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadUInt16();
        }

        internal static uint ReadUInt32(BinaryReader br, long offset, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadUInt32();
        }
        internal static int ReadInt32(BinaryReader br, long offset, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadInt32();
        }

        internal static ulong ReadUInt64(BinaryReader br, long offset, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadUInt64();
        }
        internal static long ReadInt64(BinaryReader br, long offset, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadInt64();
        }

        internal static byte[] ReadBytes(BinaryReader br, long offset, int length, SeekOrigin so = SeekOrigin.Begin)
        {
            br.BaseStream.Seek(offset, so);
            return br.ReadBytes(length);
        }

        internal static string ReadString(BinaryReader br, long offset, int length, SeekOrigin so = SeekOrigin.Begin)
        {
            return Encoding.UTF8.GetString(ReadBytes(br, offset, length, so));
        }

        internal static byte ReadUint8(byte[] s, int pos)
        {
            return s[pos];
        }
        internal static sbyte ReadInt8(byte[] s, int pos)
        {
            return (sbyte)s[pos];
        }

        internal static ushort ReadUInt16(byte[] s, int pos)
        {
            return BitConverter.ToUInt16(s, pos);
        }
        internal static short ReadInt16(byte[] s, int pos)
        {
            return BitConverter.ToInt16(s, pos);
        }

        internal static uint ReadUInt32(byte[] s, int pos)
        {
            return BitConverter.ToUInt32(s, pos);
        }
        internal static int ReadInt32(byte[] s, int pos)
        {
            return BitConverter.ToInt32(s, pos);
        }

        internal static float ReadSingle(byte[] s, int pos)
        {
            return BitConverter.ToSingle(s, pos);
        }

        internal static ulong ReadUInt64(byte[] s, int pos)
        {
            return BitConverter.ToUInt64(s, pos);
        }
        internal static long ReadInt64(byte[] s, int pos)
        {
            return BitConverter.ToInt64(s, pos);
        }

        internal static byte ReadUint8(byte[] s, uint pos)
        {
            return s[pos];
        }
        internal static sbyte ReadInt8(byte[] s, uint pos)
        {
            return (sbyte)s[pos];
        }

        internal static ushort ReadUInt16(byte[] s, uint pos)
        {
            return BitConverter.ToUInt16(s, (int)pos);
        }
        internal static short ReadInt16(byte[] s, uint pos)
        {
            return BitConverter.ToInt16(s, (int)pos);
        }

        internal static uint ReadUInt32(byte[] s, uint pos)
        {
            return BitConverter.ToUInt32(s, (int)pos);
        }
        internal static int ReadInt32(byte[] s, uint pos)
        {
            return BitConverter.ToInt32(s, (int)pos);
        }

        internal static float ReadSingle(byte[] s, uint pos)
        {
            return BitConverter.ToSingle(s, (int)pos);
        }

        internal static ulong ReadUInt64(byte[] s, uint pos)
        {
            return BitConverter.ToUInt64(s, (int)pos);
        }
        internal static long ReadInt64(byte[] s, uint pos)
        {
            return BitConverter.ToInt64(s, (int)pos);
        }

        internal static string ReadString(byte[] s, int pos, int length)
        {
            return Encoding.UTF8.GetString(s, pos, length);
        }

        internal static string Decrypt3Nk(byte[] src) // from quickbms scsgames.bms script
        {
            if (src.Length < 0x05 || src[0] != 0x33 && src[1] != 0x6E && src[2] != 0x4B) return null;
            var decrypted = new byte[src.Length - 6];
            var key = src[5];

            for (var i = 6; i < src.Length; i++)
            {
                decrypted[i - 6] = (byte)(((((key << 2) ^ (key ^ 0xff)) << 3) ^ key) ^ src[i]);
                key++;
            }
            return Encoding.UTF8.GetString(decrypted);
        }

        internal static bool IsBitSet(uint flags, byte pos)
        {
            return (flags & (1 << pos)) != 0;
        }

        internal static byte[] InflateZlib(byte[] data, long compressedSize, long size)
        {
            var dest = new byte[size];

            var decompressor = LibdeflateWrapper.libdeflate_alloc_decompressor();
            if (decompressor == IntPtr.Zero)
            {
                Logger.Error("Could not init zlib decompressor");
                return Array.Empty<byte>();
            }

            var result = LibdeflateWrapper.libdeflate_zlib_decompress(decompressor, data,
                (UIntPtr)compressedSize,
                dest,
                (UIntPtr)size, out var bytesWritten);

            LibdeflateWrapper.libdeflate_free_decompressor(decompressor);

            if (result != libdeflate_result.LIBDEFLATE_SUCCESS)
            {
                Logger.Error($"Zlib extraction was not successful: {result}");
                return Array.Empty<byte>();
            }

            if (size != bytesWritten.ToUInt32())
                Logger.Error($"Possible incorrect zlib inflate, {bytesWritten} bytes written, expected {size}");

            return dest;
        }

        internal static uint MakeFourCc(char ch0, char ch1, char ch2, char ch3)
        {
            return ((uint) (byte) (ch0) | ((uint) (byte) (ch1) << 8) | ((uint) (byte) (ch2) << 16) |
             ((uint) (byte) (ch3) << 24));
        }
    }
}