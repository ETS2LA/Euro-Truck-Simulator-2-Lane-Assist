using System;
using System.Collections.Generic;
using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor.Map.Overlays
{
    // https://learn.microsoft.com/en-us/windows/win32/api/d3d11/ns-d3d11-d3d11_subresource_data
    internal class SubresourceData
    {
        internal uint Offset { get; set; }
        internal uint RowPitch { get; set; }
        internal uint SlicePitch { get; set; }
    }

    // https://learn.microsoft.com/en-us/windows/win32/api/dxgiformat/ne-dxgiformat-dxgi_format
    internal enum DxgiFormat : uint
    {
        FormatUnknown = 0,
        FormatR32G32B32A32Typeless = 1,
        FormatR32G32B32A32Float = 2,
        FormatR32G32B32A32Uint = 3,
        FormatR32G32B32A32Sint = 4,
        FormatR32G32B32Typeless = 5,
        FormatR32G32B32Float = 6,
        FormatR32G32B32Uint = 7,
        FormatR32G32B32Sint = 8,
        FormatR16G16B16A16Typeless = 9,
        FormatR16G16B16A16Float = 10,
        FormatR16G16B16A16Unorm = 11,
        FormatR16G16B16A16Uint = 12,
        FormatR16G16B16A16Snorm = 13,
        FormatR16G16B16A16Sint = 14,
        FormatR32G32Typeless = 15,
        FormatR32G32Float = 16,
        FormatR32G32Uint = 17,
        FormatR32G32Sint = 18,
        FormatR32G8X24Typeless = 19,
        FormatD32FloatS8X24Uint = 20,
        FormatR32FloatX8X24Typeless = 21,
        FormatX32TypelessG8X24Uint = 22,
        FormatR10G10B10A2Typeless = 23,
        FormatR10G10B10A2Unorm = 24,
        FormatR10G10B10A2Uint = 25,
        FormatR11G11B10Float = 26,
        FormatR8G8B8A8Typeless = 27,
        FormatR8G8B8A8Unorm = 28,
        FormatR8G8B8A8UnormSrgb = 29,
        FormatR8G8B8A8Uint = 30,
        FormatR8G8B8A8Snorm = 31,
        FormatR8G8B8A8Sint = 32,
        FormatR16G16Typeless = 33,
        FormatR16G16Float = 34,
        FormatR16G16Unorm = 35,
        FormatR16G16Uint = 36,
        FormatR16G16Snorm = 37,
        FormatR16G16Sint = 38,
        FormatR32Typeless = 39,
        FormatD32Float = 40,
        FormatR32Float = 41,
        FormatR32Uint = 42,
        FormatR32Sint = 43,
        FormatR24G8Typeless = 44,
        FormatD24UnormS8Uint = 45,
        FormatR24UnormX8Typeless = 46,
        FormatX24TypelessG8Uint = 47,
        FormatR8G8Typeless = 48,
        FormatR8G8Unorm = 49,
        FormatR8G8Uint = 50,
        FormatR8G8Snorm = 51,
        FormatR8G8Sint = 52,
        FormatR16Typeless = 53,
        FormatR16Float = 54,
        FormatD16Unorm = 55,
        FormatR16Unorm = 56,
        FormatR16Uint = 57,
        FormatR16Snorm = 58,
        FormatR16Sint = 59,
        FormatR8Typeless = 60,
        FormatR8Unorm = 61,
        FormatR8Uint = 62,
        FormatR8Snorm = 63,
        FormatR8Sint = 64,
        FormatA8Unorm = 65,
        FormatR1Unorm = 66,
        FormatR9G9B9E5Sharedexp = 67,
        FormatR8G8B8G8Unorm = 68,
        FormatG8R8G8B8Unorm = 69,
        FormatBc1Typeless = 70,
        FormatBc1Unorm = 71,
        FormatBc1UnormSrgb = 72,
        FormatBc2Typeless = 73,
        FormatBc2Unorm = 74,
        FormatBc2UnormSrgb = 75,
        FormatBc3Typeless = 76,
        FormatBc3Unorm = 77,
        FormatBc3UnormSrgb = 78,
        FormatBc4Typeless = 79,
        FormatBc4Unorm = 80,
        FormatBc4Snorm = 81,
        FormatBc5Typeless = 82,
        FormatBc5Unorm = 83,
        FormatBc5Snorm = 84,
        FormatB5G6R5Unorm = 85,
        FormatB5G5R5A1Unorm = 86,
        FormatB8G8R8A8Unorm = 87,
        FormatB8G8R8X8Unorm = 88,
        FormatR10G10B10XrBiasA2Unorm = 89,
        FormatB8G8R8A8Typeless = 90,
        FormatB8G8R8A8UnormSrgb = 91,
        FormatB8G8R8X8Typeless = 92,
        FormatB8G8R8X8UnormSrgb = 93,
        FormatBc6HTypeless = 94,
        FormatBc6HUf16 = 95,
        FormatBc6HSf16 = 96,
        FormatBc7Typeless = 97,
        FormatBc7Unorm = 98,
        FormatBc7UnormSrgb = 99,
        FormatAyuv = 100,
        FormatY410 = 101,
        FormatY416 = 102,
        FormatNv12 = 103,
        FormatP010 = 104,
        FormatP016 = 105,
        Format420Opaque = 106,
        FormatYuy2 = 107,
        FormatY210 = 108,
        FormatY216 = 109,
        FormatNv11 = 110,
        FormatAi44 = 111,
        FormatIa44 = 112,
        FormatP8 = 113,
        FormatA8P8 = 114,
        FormatB4G4R4A4Unorm = 115,
        FormatP208 = 130,
        FormatV208 = 131,
        FormatV408 = 132,
        FormatSamplerFeedbackMinMipOpaque,
        FormatSamplerFeedbackMipRegionUsedOpaque
    }

    // https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
    internal class DdsPixelFormat
    {
        internal uint Size { get; set; }
        internal uint Flags { get; set; }
        internal uint FourCc { get; set; }
        internal uint RgbBitCount { get; set; }
        internal uint RBitMask { get; set; }
        internal uint GBitMask { get; set; }
        internal uint BBitMask { get; set; }
        internal uint ABitMask { get; set; }
    }

    internal static class Dds
    {
        private static bool IsBitMask(DdsPixelFormat ddpf, uint r, uint g, uint b, uint a)
        {
            return ddpf.RBitMask == r && ddpf.GBitMask == g && ddpf.BBitMask == b && ddpf.ABitMask == a;
        }

        // https://github.com/microsoft/DirectStorage/blob/60a909f351d18293aeae1af7e24fc38519ebe118/Samples/BulkLoadDemo/Core/DDSTextureLoader.cpp#L689
        internal static bool FillInitData(uint width,
            uint height,
            uint depth,
            uint mipCount,
            uint arraySize,
            DxgiFormat format,
            uint maxSize,
            uint bitSize,
            byte[] bitData,
            out uint twidth,
            out uint theight,
            out uint tdepth,
            out uint skipMip,
            out List<SubresourceData> result)
        {
            skipMip = 0;
            twidth = 0;
            theight = 0;
            tdepth = 0;

            result = new List<SubresourceData>();

            if (bitData.Length == 0) return false;

            var offset = 0u;

            uint index = 0;
            for (uint j = 0; j < arraySize; j++)
            {
                var w = width;
                var h = height;
                var d = depth;
                for (uint i = 0; i < mipCount; i++)
                {
                    GetSurfaceInfo(w,
                        h,
                        format,
                        out var numBytes,
                        out var rowBytes,
                        out _
                    );

                    if (mipCount <= 1 || maxSize == 0 || (w <= maxSize && h <= maxSize && d <= maxSize))
                    {
                        if (twidth == 0)
                        {
                            twidth = w;
                            theight = h;
                            tdepth = d;
                        }

                        result.Add(new SubresourceData
                        {
                            Offset = offset,
                            RowPitch = rowBytes,
                            SlicePitch = numBytes
                        });
                        ++index;
                    }
                    else if (j == 0)
                    {
                        // Count number of skipped mipmaps (first item only)
                        ++skipMip;
                    }

                    if (numBytes * d > bitSize) return false;

                    offset += numBytes * d;

                    w >>= 1;
                    h >>= 1;
                    d >>= 1;
                    if (w == 0) w = 1;
                    if (h == 0) h = 1;
                    if (d == 0) d = 1;
                }
            }

            return index > 0;
        }

        // https://github.com/microsoft/DirectStorage/blob/60a909f351d18293aeae1af7e24fc38519ebe118/Samples/BulkLoadDemo/Core/DDSTextureLoader.cpp#L162
        private static uint BitsPerPixel(DxgiFormat fmt)
        {
            switch (fmt)
            {
                case DxgiFormat.FormatR32G32B32A32Typeless:
                case DxgiFormat.FormatR32G32B32A32Float:
                case DxgiFormat.FormatR32G32B32A32Uint:
                case DxgiFormat.FormatR32G32B32A32Sint:
                    return 128;

                case DxgiFormat.FormatR32G32B32Typeless:
                case DxgiFormat.FormatR32G32B32Float:
                case DxgiFormat.FormatR32G32B32Uint:
                case DxgiFormat.FormatR32G32B32Sint:
                    return 96;

                case DxgiFormat.FormatR16G16B16A16Typeless:
                case DxgiFormat.FormatR16G16B16A16Float:
                case DxgiFormat.FormatR16G16B16A16Unorm:
                case DxgiFormat.FormatR16G16B16A16Uint:
                case DxgiFormat.FormatR16G16B16A16Snorm:
                case DxgiFormat.FormatR16G16B16A16Sint:
                case DxgiFormat.FormatR32G32Typeless:
                case DxgiFormat.FormatR32G32Float:
                case DxgiFormat.FormatR32G32Uint:
                case DxgiFormat.FormatR32G32Sint:
                case DxgiFormat.FormatR32G8X24Typeless:
                case DxgiFormat.FormatD32FloatS8X24Uint:
                case DxgiFormat.FormatR32FloatX8X24Typeless:
                case DxgiFormat.FormatX32TypelessG8X24Uint:
                case DxgiFormat.FormatY416:
                case DxgiFormat.FormatY210:
                case DxgiFormat.FormatY216:
                    return 64;

                case DxgiFormat.FormatR10G10B10A2Typeless:
                case DxgiFormat.FormatR10G10B10A2Unorm:
                case DxgiFormat.FormatR10G10B10A2Uint:
                case DxgiFormat.FormatR11G11B10Float:
                case DxgiFormat.FormatR8G8B8A8Typeless:
                case DxgiFormat.FormatR8G8B8A8Unorm:
                case DxgiFormat.FormatR8G8B8A8UnormSrgb:
                case DxgiFormat.FormatR8G8B8A8Uint:
                case DxgiFormat.FormatR8G8B8A8Snorm:
                case DxgiFormat.FormatR8G8B8A8Sint:
                case DxgiFormat.FormatR16G16Typeless:
                case DxgiFormat.FormatR16G16Float:
                case DxgiFormat.FormatR16G16Unorm:
                case DxgiFormat.FormatR16G16Uint:
                case DxgiFormat.FormatR16G16Snorm:
                case DxgiFormat.FormatR16G16Sint:
                case DxgiFormat.FormatR32Typeless:
                case DxgiFormat.FormatD32Float:
                case DxgiFormat.FormatR32Float:
                case DxgiFormat.FormatR32Uint:
                case DxgiFormat.FormatR32Sint:
                case DxgiFormat.FormatR24G8Typeless:
                case DxgiFormat.FormatD24UnormS8Uint:
                case DxgiFormat.FormatR24UnormX8Typeless:
                case DxgiFormat.FormatX24TypelessG8Uint:
                case DxgiFormat.FormatR9G9B9E5Sharedexp:
                case DxgiFormat.FormatR8G8B8G8Unorm:
                case DxgiFormat.FormatG8R8G8B8Unorm:
                case DxgiFormat.FormatB8G8R8A8Unorm:
                case DxgiFormat.FormatB8G8R8X8Unorm:
                case DxgiFormat.FormatR10G10B10XrBiasA2Unorm:
                case DxgiFormat.FormatB8G8R8A8Typeless:
                case DxgiFormat.FormatB8G8R8A8UnormSrgb:
                case DxgiFormat.FormatB8G8R8X8Typeless:
                case DxgiFormat.FormatB8G8R8X8UnormSrgb:
                case DxgiFormat.FormatAyuv:
                case DxgiFormat.FormatY410:
                case DxgiFormat.FormatYuy2:
                    return 32;

                case DxgiFormat.FormatP010:
                case DxgiFormat.FormatP016:
                    return 24;

                case DxgiFormat.FormatR8G8Typeless:
                case DxgiFormat.FormatR8G8Unorm:
                case DxgiFormat.FormatR8G8Uint:
                case DxgiFormat.FormatR8G8Snorm:
                case DxgiFormat.FormatR8G8Sint:
                case DxgiFormat.FormatR16Typeless:
                case DxgiFormat.FormatR16Float:
                case DxgiFormat.FormatD16Unorm:
                case DxgiFormat.FormatR16Unorm:
                case DxgiFormat.FormatR16Uint:
                case DxgiFormat.FormatR16Snorm:
                case DxgiFormat.FormatR16Sint:
                case DxgiFormat.FormatB5G6R5Unorm:
                case DxgiFormat.FormatB5G5R5A1Unorm:
                case DxgiFormat.FormatA8P8:
                case DxgiFormat.FormatB4G4R4A4Unorm:
                    return 16;

                case DxgiFormat.FormatNv12:
                case DxgiFormat.Format420Opaque:
                case DxgiFormat.FormatNv11:
                    return 12;

                case DxgiFormat.FormatR8Typeless:
                case DxgiFormat.FormatR8Unorm:
                case DxgiFormat.FormatR8Uint:
                case DxgiFormat.FormatR8Snorm:
                case DxgiFormat.FormatR8Sint:
                case DxgiFormat.FormatA8Unorm:
                case DxgiFormat.FormatAi44:
                case DxgiFormat.FormatIa44:
                case DxgiFormat.FormatP8:
                    return 8;

                case DxgiFormat.FormatR1Unorm:
                    return 1;

                case DxgiFormat.FormatBc1Typeless:
                case DxgiFormat.FormatBc1Unorm:
                case DxgiFormat.FormatBc1UnormSrgb:
                case DxgiFormat.FormatBc4Typeless:
                case DxgiFormat.FormatBc4Unorm:
                case DxgiFormat.FormatBc4Snorm:
                    return 4;

                case DxgiFormat.FormatBc2Typeless:
                case DxgiFormat.FormatBc2Unorm:
                case DxgiFormat.FormatBc2UnormSrgb:
                case DxgiFormat.FormatBc3Typeless:
                case DxgiFormat.FormatBc3Unorm:
                case DxgiFormat.FormatBc3UnormSrgb:
                case DxgiFormat.FormatBc5Typeless:
                case DxgiFormat.FormatBc5Unorm:
                case DxgiFormat.FormatBc5Snorm:
                case DxgiFormat.FormatBc6HTypeless:
                case DxgiFormat.FormatBc6HUf16:
                case DxgiFormat.FormatBc6HSf16:
                case DxgiFormat.FormatBc7Typeless:
                case DxgiFormat.FormatBc7Unorm:
                case DxgiFormat.FormatBc7UnormSrgb:
                    return 8;

                default:
                    return 0;
            }
        }

        // https://github.com/microsoft/DirectStorage/blob/60a909f351d18293aeae1af7e24fc38519ebe118/Samples/BulkLoadDemo/Core/DDSTextureLoader.cpp#L312
        private static void GetSurfaceInfo(uint width,
            uint height,
            DxgiFormat fmt,
            out uint numBytes,
            out uint rowBytes,
            out uint numRows)
        {
            var bc = false;
            var packed = false;
            var planar = false;
            uint bpe = 0;
            switch (fmt)
            {
                case DxgiFormat.FormatBc1Typeless:
                case DxgiFormat.FormatBc1Unorm:
                case DxgiFormat.FormatBc1UnormSrgb:
                case DxgiFormat.FormatBc4Typeless:
                case DxgiFormat.FormatBc4Unorm:
                case DxgiFormat.FormatBc4Snorm:
                    bc = true;
                    bpe = 8;
                    break;

                case DxgiFormat.FormatBc2Typeless:
                case DxgiFormat.FormatBc2Unorm:
                case DxgiFormat.FormatBc2UnormSrgb:
                case DxgiFormat.FormatBc3Typeless:
                case DxgiFormat.FormatBc3Unorm:
                case DxgiFormat.FormatBc3UnormSrgb:
                case DxgiFormat.FormatBc5Typeless:
                case DxgiFormat.FormatBc5Unorm:
                case DxgiFormat.FormatBc5Snorm:
                case DxgiFormat.FormatBc6HTypeless:
                case DxgiFormat.FormatBc6HUf16:
                case DxgiFormat.FormatBc6HSf16:
                case DxgiFormat.FormatBc7Typeless:
                case DxgiFormat.FormatBc7Unorm:
                case DxgiFormat.FormatBc7UnormSrgb:
                    bc = true;
                    bpe = 16;
                    break;

                case DxgiFormat.FormatR8G8B8G8Unorm:
                case DxgiFormat.FormatG8R8G8B8Unorm:
                case DxgiFormat.FormatYuy2:
                    packed = true;
                    bpe = 4;
                    break;

                case DxgiFormat.FormatY210:
                case DxgiFormat.FormatY216:
                    packed = true;
                    bpe = 8;
                    break;

                case DxgiFormat.FormatNv12:
                case DxgiFormat.Format420Opaque:
                    planar = true;
                    bpe = 2;
                    break;

                case DxgiFormat.FormatP010:
                case DxgiFormat.FormatP016:
                    planar = true;
                    bpe = 4;
                    break;
            }

            if (bc)
            {
                uint numBlocksWide = 0;
                if (width > 0) numBlocksWide = Math.Max(1, (width + 3) / 4);
                uint numBlocksHigh = 0;
                if (height > 0) numBlocksHigh = Math.Max(1, (height + 3) / 4);
                rowBytes = numBlocksWide * bpe;
                numRows = numBlocksHigh;
                numBytes = rowBytes * numBlocksHigh;
            }
            else if (packed)
            {
                rowBytes = ((width + 1) >> 1) * bpe;
                numRows = height;
                numBytes = rowBytes * height;
            }
            else if (fmt == DxgiFormat.FormatNv11)
            {
                rowBytes = ((width + 3) >> 2) * 4;
                numRows = height *
                          2; // Direct3D makes this simplifying assumption, although it is larger than the 4:1:1 data
                numBytes = rowBytes * numRows;
            }
            else if (planar)
            {
                rowBytes = ((width + 1) >> 1) * bpe;
                numBytes = rowBytes * height + ((rowBytes * height + 1) >> 1);
                numRows = height + ((height + 1) >> 1);
            }
            else
            {
                var bpp = BitsPerPixel(fmt);
                rowBytes = (width * bpp + 7) / 8; // round up to nearest byte
                numRows = height;
                numBytes = rowBytes * height;
            }
        }

        // https://github.com/microsoft/DirectStorage/blob/60a909f351d18293aeae1af7e24fc38519ebe118/Samples/BulkLoadDemo/Core/DDSTextureLoader.cpp#L445
        internal static DxgiFormat GetDXGIFormat(DdsPixelFormat ddpf)
        {
            if ((ddpf.Flags & 0x40 /*DDS_RGB*/) != 0)
            {
                // Note that sRGB formats are written using the "DX10" extended header

                switch (ddpf.RgbBitCount)
                {
                    case 32:
                        if (IsBitMask(ddpf, 0x000000ff, 0x0000ff00, 0x00ff0000, 0xff000000))
                            return DxgiFormat.FormatR8G8B8A8Unorm;

                        if (IsBitMask(ddpf, 0x00ff0000, 0x0000ff00, 0x000000ff, 0xff000000))
                            return DxgiFormat.FormatB8G8R8A8Unorm;

                        if (IsBitMask(ddpf, 0x00ff0000, 0x0000ff00, 0x000000ff, 0x00000000))
                            return DxgiFormat.FormatB8G8R8X8Unorm;

                        // No DXGI format maps to ISBITMASK(0x000000ff,0x0000ff00,0x00ff0000,0x00000000) aka D3DFMT_X8B8G8R8

                        // Note that many common DDS reader/writers (including D3DX) swap the
                        // the RED/BLUE masks for 10:10:10:2 formats. We assumme
                        // below that the 'backwards' header mask is being used since it is most
                        // likely written by D3DX. The more robust solution is to use the 'DX10'
                        // header extension and specify the DXGI_FORMAT_R10G10B10A2Unorm format directly

                        // For 'correct' writers, this should be 0x000003ff,0x000ffc00,0x3ff00000 for RGB data
                        if (IsBitMask(ddpf, 0x3ff00000, 0x000ffc00, 0x000003ff, 0xc0000000))
                            return DxgiFormat.FormatR10G10B10A2Unorm;

                        // No DXGI format maps to ISBITMASK(0x000003ff,0x000ffc00,0x3ff00000,0xc0000000) aka D3DFMT_A2R10G10B10

                        if (IsBitMask(ddpf, 0x0000ffff, 0xffff0000, 0x00000000, 0x00000000))
                            return DxgiFormat.FormatR16G16Unorm;

                        if (IsBitMask(ddpf, 0xffffffff, 0x00000000, 0x00000000, 0x00000000))
                        {
                            // Only 32-bit color channel format in D3D9 was R32F
                            return DxgiFormat.FormatR32Float; // D3DX writes this out as a FourCC of 114
                        }

                        break;

                    case 24:
                        // No 24bpp DXGI formats aka D3DFMT_R8G8B8
                        break;

                    case 16:
                        if (IsBitMask(ddpf, 0x7c00, 0x03e0, 0x001f, 0x8000)) return DxgiFormat.FormatB5G5R5A1Unorm;
                        if (IsBitMask(ddpf, 0xf800, 0x07e0, 0x001f, 0x0000)) return DxgiFormat.FormatB5G6R5Unorm;

                        // No DXGI format maps to ISBITMASK(0x7c00,0x03e0,0x001f,0x0000) aka D3DFMT_X1R5G5B5

                        if (IsBitMask(ddpf, 0x0f00, 0x00f0, 0x000f, 0xf000)) return DxgiFormat.FormatB4G4R4A4Unorm;

                        // No DXGI format maps to ISBITMASK(0x0f00,0x00f0,0x000f,0x0000) aka D3DFMT_X4R4G4B4

                        // No 3:3:2, 3:3:2:8, or paletted DXGI formats aka D3DFMT_A8R3G3B2, D3DFMT_R3G3B2, D3DFMT_P8, D3DFMT_A8P8, etc.
                        break;
                }
            }
            else if ((ddpf.Flags & 0x20000 /*DDS_LUMINANCE*/) != 0)
            {
                if (8 == ddpf.RgbBitCount)
                {
                    if (IsBitMask(ddpf, 0x000000ff, 0x00000000, 0x00000000,
                            0x00000000)) return DxgiFormat.FormatR8Unorm; // D3DX10/11 writes this out as DX10 extension

                    // No DXGI format maps to ISBITMASK(0x0f,0x00,0x00,0xf0) aka D3DFMT_A4L4
                }

                if (16 == ddpf.RgbBitCount)
                {
                    if (IsBitMask(ddpf, 0x0000ffff, 0x00000000, 0x00000000, 0x00000000))
                        return DxgiFormat.FormatR16Unorm; // D3DX10/11 writes this out as DX10 extension
                    if (IsBitMask(ddpf, 0x000000ff, 0x00000000, 0x00000000, 0x0000ff00))
                        return DxgiFormat.FormatR8G8Unorm; // D3DX10/11 writes this out as DX10 extension
                }
            }
            else if ((ddpf.Flags & 0x2 /*DDS_ALPHA*/) != 0)
            {
                if (8 == ddpf.RgbBitCount) return DxgiFormat.FormatA8Unorm;
            }
            else if ((ddpf.Flags & 0x4 /*DDS_FOURCC*/) != 0)
            {
                if (MemoryHelper.MakeFourCc('D', 'X', 'T', '1') == ddpf.FourCc) return DxgiFormat.FormatBc1Unorm;
                if (MemoryHelper.MakeFourCc('D', 'X', 'T', '3') == ddpf.FourCc) return DxgiFormat.FormatBc2Unorm;
                if (MemoryHelper.MakeFourCc('D', 'X', 'T', '5') == ddpf.FourCc) return DxgiFormat.FormatBc3Unorm;

                // While pre-mulitplied alpha isn't directly supported by the DXGI formats,
                // they are basically the same as these BC formats so they can be mapped
                if (MemoryHelper.MakeFourCc('D', 'X', 'T', '2') == ddpf.FourCc) return DxgiFormat.FormatBc2Unorm;
                if (MemoryHelper.MakeFourCc('D', 'X', 'T', '4') == ddpf.FourCc) return DxgiFormat.FormatBc3Unorm;

                if (MemoryHelper.MakeFourCc('A', 'T', 'I', '1') == ddpf.FourCc) return DxgiFormat.FormatBc4Unorm;
                if (MemoryHelper.MakeFourCc('B', 'C', '4', 'U') == ddpf.FourCc) return DxgiFormat.FormatBc4Unorm;
                if (MemoryHelper.MakeFourCc('B', 'C', '4', 'S') == ddpf.FourCc) return DxgiFormat.FormatBc4Snorm;

                if (MemoryHelper.MakeFourCc('A', 'T', 'I', '2') == ddpf.FourCc) return DxgiFormat.FormatBc5Unorm;
                if (MemoryHelper.MakeFourCc('B', 'C', '5', 'U') == ddpf.FourCc) return DxgiFormat.FormatBc5Unorm;
                if (MemoryHelper.MakeFourCc('B', 'C', '5', 'S') == ddpf.FourCc) return DxgiFormat.FormatBc5Snorm;

                // BC6H and BC7 are written using the "DX10" extended header

                if (MemoryHelper.MakeFourCc('R', 'G', 'B', 'G') == ddpf.FourCc) return DxgiFormat.FormatR8G8B8G8Unorm;
                if (MemoryHelper.MakeFourCc('G', 'R', 'G', 'B') == ddpf.FourCc) return DxgiFormat.FormatG8R8G8B8Unorm;

                if (MemoryHelper.MakeFourCc('Y', 'U', 'Y', '2') == ddpf.FourCc) return DxgiFormat.FormatYuy2;

                // Check for D3DFORMAT enums being set here
                switch (ddpf.FourCc)
                {
                    case 36: // D3DFMT_A16B16G16R16
                        return DxgiFormat.FormatR16G16B16A16Unorm;

                    case 110: // D3DFMT_Q16W16V16U16
                        return DxgiFormat.FormatR16G16B16A16Snorm;

                    case 111: // D3DFMT_R16F
                        return DxgiFormat.FormatR16Float;

                    case 112: // D3DFMT_G16R16F
                        return DxgiFormat.FormatR16G16Float;

                    case 113: // D3DFMT_A16B16G16R16F
                        return DxgiFormat.FormatR16G16B16A16Float;

                    case 114: // D3DFMT_R32F
                        return DxgiFormat.FormatR32Float;

                    case 115: // D3DFMT_G32R32F
                        return DxgiFormat.FormatR32G32Float;

                    case 116: // D3DFMT_A32B32G32R32F
                        return DxgiFormat.FormatR32G32B32A32Float;
                }
            }

            return DxgiFormat.FormatUnknown;
        }
    }
}
