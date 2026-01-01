using System.Drawing;
using System.Runtime.InteropServices;
using System.Text;
using ETS2LA.Game.Extractor.FileSystem;
using ETS2LA.Game.Extractor.FileSystem.Hash;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.Map.Overlays
{
    internal class OverlayImage
    {
        private Bitmap _bitmap;

        private UberFile _file;

        private Color8888[] _pixelData;
        private byte[] _stream;

        public OverlayImage(Material mat)
        {
            Mat = mat;
        }

        internal DxgiFormat Format { get; private set; }
        internal bool Valid { get; private set; }
        internal uint Width { get; private set; }
        internal uint Height { get; private set; }

        internal Material Mat { get; }

        /// <summary>
        /// Mixes pixel color values from the material' aux values according to the percentage of color available in mask.
        /// </summary>
        /// <param name="inColor">Mask pixel color</param>
        /// <returns></returns>
        private Color8888 MixAuxColorsFollowingMask(Color8888 inColor)
        {
            if (Mat.AuxValues.Count < 4 || !Mat.EffectName.Contains("ui.sdf"))
            {
                return inColor;
            }

            double totalColor = inColor.R + inColor.G + inColor.B;
            if (totalColor == 0) return new Color8888(0, 0, 0, 0);

            var redRatio = inColor.R / totalColor;
            var greenRatio = inColor.G / totalColor;
            var blueRatio = inColor.B / totalColor;

            var redChannel = Mat.AuxValues[1];
            var greenChannel = Mat.AuxValues[2];
            var blueChannel = Mat.AuxValues[3];

            var newR =
                redChannel.SrgbR * redRatio +
                greenChannel.SrgbR * greenRatio +
                blueChannel.SrgbR * blueRatio;

            var newG =
                redChannel.SrgbG * redRatio +
                greenChannel.SrgbG * greenRatio +
                blueChannel.SrgbG * blueRatio;

            var newB =
                redChannel.SrgbB * redRatio +
                greenChannel.SrgbB * greenRatio +
                blueChannel.SrgbB * blueRatio;

            return new Color8888(inColor.A, (byte)Math.Round(newR), (byte)Math.Round(newG), (byte)Math.Round(newB));
        }

        public Bitmap GetBitmap()
        {
            //if (_bitmap == null)
            //{
            //    _bitmap = new Bitmap((int) Width, (int) Height, PixelFormat.Format32bppArgb);
            //
            //    var bd = _bitmap.LockBits(new Rectangle(0, 0, _bitmap.Width, _bitmap.Height), ImageLockMode.WriteOnly,
            //        PixelFormat.Format32bppArgb);
            //
            //    var ptr = bd.Scan0;
            //
            //    Marshal.Copy(GetData(), 0, ptr, bd.Width * bd.Height * 0x4);
            //
            //    _bitmap.UnlockBits(bd);
            //}

            return _bitmap;
        }

        private byte[] GetData()
        {
            var bytes = new byte[Width * Height * 4];
            for (var i = 0; i < _pixelData.Length; ++i)
            {
                var pixel = MixAuxColorsFollowingMask(_pixelData[i]);
                bytes[i * 4 + 3] = pixel.A;
                bytes[i * 4] = pixel.B;
                bytes[i * 4 + 1] = pixel.G;
                bytes[i * 4 + 2] = pixel.R;
            }

            return bytes;
        }

        internal void Parse()
        {
            Valid = true;
            _file = UberFileSystem.Instance.GetFile(Mat.TextureSource);
            if (_file == null)
            {
                Valid = false;
                Logger.Error($"Could not find TOBJ file ({Mat.TextureSource})");
                return;
            }

            var pixelDataOffset = 0;
            if (_file.Entry is HashEntryV2 entry)
            {
                _stream = ProcessHashFsV2ImageData(entry);
            }
            else
            {
                var tobjData = _file.Entry.Read();
                var ddsPath = PathHelper.EnsureLocalPath(Encoding.UTF8.GetString(tobjData, 0x30, tobjData.Length - 0x30));
                _file = UberFileSystem.Instance.GetFile(ddsPath);
                if (_file == null)
                {
                    Valid = false;
                    Logger.Error($"Could not find DDS file ({ddsPath})");
                    return;
                }

                _stream = _file.Entry.Read();

                if (_stream.Length < 128 ||
                    MemoryHelper.ReadUInt32(_stream, 0x00) != 0x20534444 ||
                    MemoryHelper.ReadUInt32(_stream, 0x04) != 0x7C)
                {
                    Valid = false;
                    Logger.Error($"Invalid DDS header for '{ddsPath}'");
                    return;
                }

                Height = MemoryHelper.ReadUInt32(_stream, 0x0C);
                Width = MemoryHelper.ReadUInt32(_stream, 0x10);
                var ddpf = new DdsPixelFormat
                {
                    Size = MemoryHelper.ReadUInt32(_stream, 0x4c),
                    Flags = MemoryHelper.ReadUInt32(_stream, 0x50),
                    FourCc = MemoryHelper.ReadUInt32(_stream, 0x54),
                    RgbBitCount = MemoryHelper.ReadUInt32(_stream, 0x58),
                    RBitMask = MemoryHelper.ReadUInt32(_stream, 0x5c),
                    GBitMask = MemoryHelper.ReadUInt32(_stream, 0x60),
                    BBitMask = MemoryHelper.ReadUInt32(_stream, 0x64),
                    ABitMask = MemoryHelper.ReadUInt32(_stream, 0x68),
                };
                pixelDataOffset = (ddpf.FourCc == MemoryHelper.MakeFourCc('D', 'X', '1', '0')) ? 0x94 : 0x80;

                Format = Dds.GetDXGIFormat(ddpf);

            }

            if (Format == DxgiFormat.FormatUnknown)
            {
                Logger.Debug($"Could not find dds format for '{Mat.TextureSource}'");
                Valid = false;
                return;
            }

            switch (Format)
            {
                case DxgiFormat.FormatB8G8R8A8Unorm:
                case DxgiFormat.FormatB8G8R8A8UnormSrgb:
                    ParseB8G8R8A8(pixelDataOffset);
                    break;
                case DxgiFormat.FormatB8G8R8X8Unorm:
                case DxgiFormat.FormatB8G8R8X8UnormSrgb:
                    ParseB8G8R8X8(pixelDataOffset);
                    break;
                case DxgiFormat.FormatBc2Unorm:
                case DxgiFormat.FormatBc2UnormSrgb:
                    ParseDxt3(pixelDataOffset);
                    break;
                case DxgiFormat.FormatBc3Unorm:
                case DxgiFormat.FormatBc3UnormSrgb:
                    ParseDxt5(pixelDataOffset);
                    break;
                default:
                    Logger.Error($"No support for dds format '{Format}' for '{Mat.TextureSource}'");
                    Valid = false;
                    break;
            }
        }


        private byte[] ProcessHashFsV2ImageData(HashEntryV2 entry)
        {
            if (!entry._imgMetadata.HasValue)
            {
                Valid = false;
                Logger.Error($"Tobj entry does not have image metadata ({Mat.TextureSource})");
                return Array.Empty<byte>();
            }

            Width = entry._imgMetadata.Value.Width;
            Height = entry._imgMetadata.Value.Height;
            Format = entry._imgMetadata.Value.Format;
            _stream = _file.Entry.Read();

            var result = new List<byte>();

            Dds.FillInitData(Width, Height, 1, entry._imgMetadata.Value.MipmapCount, 1, Format, 0,
                (uint) _stream.Length, _stream,
                out _,
                out _,
                out _,
                out _,
                out var subData);

            uint currentOffset = 0;

            for (uint currentFaceIndex = 0; currentFaceIndex < entry._imgMetadata.Value.Count; ++currentFaceIndex)
            {
                for (var mipmapIndex = 0; mipmapIndex < entry._imgMetadata.Value.MipmapCount; ++mipmapIndex)
                {
                    var mipmapSubData = subData[mipmapIndex];
                    var slicePitch = mipmapSubData.SlicePitch;
                    var rowPitch = mipmapSubData.RowPitch;

                    currentOffset = (uint)Math.Ceiling((double)currentOffset / entry._imgMetadata.Value.ImageAlignment) * entry._imgMetadata.Value.ImageAlignment;

                    for (uint doneBytes = 0; doneBytes < slicePitch; doneBytes += rowPitch)
                    {
                        currentOffset = (uint)Math.Ceiling((double)currentOffset / entry._imgMetadata.Value.PitchAlignment) * entry._imgMetadata.Value.PitchAlignment;

                        result.AddRange(_stream.Skip((int) currentOffset).Take((int) rowPitch));
                        currentOffset += rowPitch;
                    }
                }
            }
            return result.ToArray();
        }

        private void ParseB8G8R8A8(int pixelDataOffset)
        {
            if ((_stream.Length - pixelDataOffset) / 4 < Width * Height)
            {
                Valid = false;
                Logger.Error($"Invalid DDS file (size), '{Mat.TextureSource}'");
                return;
            }

            var fileOffset = pixelDataOffset - 0x04;

            _pixelData = new Color8888[Width * Height];

            for (var i = 0; i < Width * Height; ++i)
            {
                var rgba = MemoryHelper.ReadUInt32(_stream, fileOffset += 0x04);
                _pixelData[i] = new Color8888((byte) ((rgba >> 0x18) & 0xFF), (byte) ((rgba >> 0x10) & 0xFF),
                    (byte) ((rgba >> 0x08) & 0xFF), (byte) (rgba & 0xFF));
            }
        }

        private void ParseB8G8R8X8(int pixelDataOffset)
        {
            if ((_stream.Length - pixelDataOffset) / 4 < Width * Height)
            {
                Valid = false;
                Logger.Error($"Invalid DDS file (size), '{Mat.TextureSource}'");
                return;
            }

            var fileOffset = pixelDataOffset - 0x04;

            _pixelData = new Color8888[Width * Height];

            for (var i = 0; i < Width * Height; ++i)
            {
                var rgba = MemoryHelper.ReadUInt32(_stream, fileOffset += 0x04);
                _pixelData[i] = new Color8888(0xFF, (byte)((rgba >> 0x10) & 0xFF),
                    (byte)((rgba >> 0x08) & 0xFF), (byte)(rgba & 0xFF));
            }
        }

        private void ParseDxt3(int pixelDataOffset) // https://msdn.microsoft.com/en-us/library/windows/desktop/bb694531
        {
            var fileOffset = pixelDataOffset;
            _pixelData = new Color8888[Width * Height];
            for (var y = 0; y < Height; y += 4)
            for (var x = 0; x < Width; x += 4)
            {
                var baseOffset = fileOffset;

                var color0 = new Color565(BitConverter.ToUInt16(_stream, fileOffset += 0x08));
                var color1 = new Color565(BitConverter.ToUInt16(_stream, fileOffset += 0x02));

                var color2 = (double) 2 / 3 * color0 + (double) 1 / 3 * color1;
                var color3 = (double) 1 / 3 * color0 + (double) 2 / 3 * color1;

                var colors = new[]
                {
                    new Color8888(color0, 0xFF), // bit code 00
                    new Color8888(color1, 0xFF), // bit code 01
                    new Color8888(color2, 0xFF), // bit code 10
                    new Color8888(color3, 0xFF) // bit code 11
                };

                fileOffset += 0x02;
                for (var i = 0; i < 4; ++i)
                {
                    var colorRow = _stream[fileOffset + i];
                    var alphaRow = BitConverter.ToUInt16(_stream, baseOffset + i * 2);

                    for (var j = 0; j < 4; ++j)
                    {
                        var colorIndex = (colorRow >> (j * 2)) & 3;
                        var alpha = (alphaRow >> (j * 4)) & 15;
                        var pos = y * Width + i * Width + x + j;
                        _pixelData[pos] = colors[colorIndex];
                        _pixelData[pos].SetAlpha((byte) (alpha / 15f * 255));
                    }
                }

                fileOffset += 0x04;
            }
        }

        private void ParseDxt5(int pixelDataOffset) // https://msdn.microsoft.com/en-us/library/windows/desktop/bb694531
        {
            var fileOffset = pixelDataOffset;
            _pixelData = new Color8888[Width * Height];
            for (var y = 0; y < Height; y += 4)
            for (var x = 0; x < Width; x += 4)
            {
                var alphas = new byte[8];
                alphas[0] = _stream[fileOffset];
                alphas[1] = _stream[fileOffset += 0x01];

                if (alphas[0] > alphas[1])
                {
                    // 6 interpolated alpha values.
                    alphas[2] = (byte) ((double) 6 / 7 * alphas[0] + (double) 1 / 7 * alphas[1]); // bit code 010
                    alphas[3] = (byte) ((double) 5 / 7 * alphas[0] + (double) 2 / 7 * alphas[1]); // bit code 011
                    alphas[4] = (byte) ((double) 4 / 7 * alphas[0] + (double) 3 / 7 * alphas[1]); // bit code 100
                    alphas[5] = (byte) ((double) 3 / 7 * alphas[0] + (double) 4 / 7 * alphas[1]); // bit code 101
                    alphas[6] = (byte) ((double) 2 / 7 * alphas[0] + (double) 5 / 7 * alphas[1]); // bit code 110
                    alphas[7] = (byte) ((double) 1 / 7 * alphas[0] + (double) 6 / 7 * alphas[1]); // bit code 111
                }
                else
                {
                    // 4 interpolated alpha values.
                    alphas[2] = (byte) ((double) 4 / 5 * alphas[0] + (double) 1 / 5 * alphas[1]); // bit code 010
                    alphas[3] = (byte) ((double) 3 / 5 * alphas[0] + (double) 2 / 5 * alphas[1]); // bit code 011
                    alphas[4] = (byte) ((double) 2 / 5 * alphas[0] + (double) 3 / 5 * alphas[1]); // bit code 100
                    alphas[5] = (byte) ((double) 1 / 5 * alphas[0] + (double) 4 / 5 * alphas[1]); // bit code 101
                    alphas[6] = 0; // bit code 110
                    alphas[7] = 255; // bit code 111
                }

                var alphaTexelUlongData = MemoryHelper.ReadUInt64(_stream, fileOffset += 0x01);

                var alphaTexelData =
                    alphaTexelUlongData & 0xFFFFFFFFFFFF; // remove 2 excess bytes (read 8 bytes only need 6)

                var alphaTexels = new byte[16];
                for (var j = 0; j < 2; ++j)
                {
                    var alphaTexelRowData = (alphaTexelData >> (j * 0x18)) & 0xFFFFFF;
                    for (var i = 0; i < 8; ++i)
                    {
                        var index = (alphaTexelRowData >> (i * 0x03)) & 0x07;
                        alphaTexels[i + j * 8] = alphas[index];
                    }
                }

                var color0 = new Color565(MemoryHelper.ReadUInt16(_stream, fileOffset += 0x06));
                var color1 = new Color565(MemoryHelper.ReadUInt16(_stream, fileOffset += 0x02));

                var color2 = (double) 2 / 3 * color0 + (double) 1 / 3 * color1;
                var color3 = (double) 1 / 3 * color0 + (double) 2 / 3 * color1;

                var colors = new[]
                {
                    new Color8888(color0, 0xFF), // bit code 00
                    new Color8888(color1, 0xFF), // bit code 01
                    new Color8888(color2, 0xFF), // bit code 10
                    new Color8888(color3, 0xFF) // bit code 11
                };

                var colorTexelData = MemoryHelper.ReadUInt32(_stream, fileOffset += 0x02);
                for (var j = 3; j >= 0; --j)
                {
                    var colorTexelRowData = (colorTexelData >> (j * 0x08)) & 0xFF;
                    for (var i = 0; i < 4; ++i)
                    {
                        var index = (colorTexelRowData >> (i * 0x02)) & 0x03;
                        var pos = (uint) (y * Width + j * Width + x + i);
                        _pixelData[pos] = colors[index];
                        _pixelData[pos].SetAlpha(alphaTexels[j * 4 + i]);
                    }
                }

                fileOffset += 0x04;
            }
        }
    }
}
