using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Extractor.Deep
{
    using CheckFunc = Func<byte[], bool>;

    public static class FileTypeHelper
    {
        private static readonly Dictionary<FileType, CheckFunc> FileTypeCheckers = new() {
            { FileType.Bmp, IsBmpFile },
            { FileType.Dds, IsDdsFile },
            { FileType.OpenExr, IsExrFile },
            { FileType.Fbx, IsFbxFile },
            { FileType.Font, IsFontFile },
            { FileType.Jpeg, IsJpegFile },
            { FileType.Material, IsMatFile },
            { FileType.MayaFile, IsMayaFile },
            { FileType.Ogg, IsOggFile },
            { FileType.Pdn, IsPdnFile },
            { FileType.Pmg, IsPmgFile },
            { FileType.Pmc, IsPmcFile },
            { FileType.Pmd, IsPmdFile },
            { FileType.Pma, IsPmaFile },
            { FileType.Png, IsPngFile },
            { FileType.Psd, IsPsdFile },
            { FileType.Ppd, IsPpdFile },
            { FileType.Rar, IsRarFile },
            { FileType.Sii, IsSiiFile },
            { FileType.SoundBank, IsSoundBankFile },
            { FileType.SoundBankGuids, IsSoundBankGuidsFile },
            { FileType.TgaMask, IsTgaFile },
            { FileType.Tobj, IsTobjFile },
            { FileType.GimpXcf, IsXcfFile },
            { FileType.ZlibBlob, IsZlibBlob },
            { FileType._7z, Is7zFile },
            { FileType.SoundRef, IsSoundRefFile },
        };

        public static FileType Infer(byte[] fileBuffer)
        {
            if (fileBuffer.Length == 0)
                return FileType.Unknown;

            foreach (var (type, checker) in FileTypeCheckers)
            {
                if (checker(fileBuffer))
                    return type;
            }
            return FileType.Unknown;
        }

        private static bool IsSiiFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 4)
                return false;

            var magic = Encoding.UTF8.GetString(fileBuffer[0..4]);
            return magic == "SiiN"        // regular SII
                || magic == "\uFEFFS"      // regular SII with BOM, ugh
                || magic == "ScsC"         // encrypted SII
                || magic.StartsWith("3nK") // 3nK-encoded SII
            ;
        }

        private static bool IsPdnFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 3 &&
                Encoding.ASCII.GetString(fileBuffer[0..3]) == "PDN";
        }

        private static bool IsPmgFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[1..4]) == "gmP";
        }

        private static bool IsMatFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 10)
                return false;

            var start = Encoding.UTF8.GetString(fileBuffer[0..10]).Trim('\uFEFF');
            return start.StartsWith("material") || start.StartsWith("effect");
        }

        private static bool IsSoundBankFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[0..4]) == "RIFF";
        }

        private static bool IsDdsFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 3 &&
                Encoding.ASCII.GetString(fileBuffer[0..3]) == "DDS";
        }

        private static bool IsSoundRefFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length > 10000)
                return false;

            var lines = Encoding.UTF8.GetString(fileBuffer)
                .Trim(['\uFEFF', '\0'])
                .Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries);
            foreach (var line in lines)
            {
                if (line.StartsWith("source="))
                    return true;
            }
            return false;
        }

        private const uint MaxPlausiblePmdPieceCount = 5000;

        private static bool IsPmdFile(byte[] fileBuffer)
        {
            // PMD/PMA/PMC don't have any magic bytes to distinguish them,
            // so we need to make an educated guess.
            // PMC is on version 6, I haven't seen any lower versions in
            // the wild so far, and PMD and PMA are still below 6, so
            // for PMC, checking the version is sufficient.
            // PMA and PMD, however, have overlapping versions. PMD is
            // on version 4, and PMA is on version 5, but version 4 still
            // exists in the wild. To distinguish between the two, I read
            // an integer from offset 12, which in PMD is the part count
            // and in PMA is the MSB of a hash, so if this integer is too
            // large to plausibly be a part count, the file must be a
            // PMA file.

            if (fileBuffer.Length < 20)
                return false;

            if (BitConverter.ToInt32(fileBuffer.AsSpan()[0..4]) != 4)
                return false;

            var partCountMaybe = BitConverter.ToUInt32(fileBuffer.AsSpan()[12..16]);
            return partCountMaybe <= MaxPlausiblePmdPieceCount;
        }

        private static bool IsPmaFile(byte[] fileBuffer)
        {
            // See the comment in IsPmdFile for an explanation.

            if (fileBuffer.Length < 20)
                return false;

            var version = BitConverter.ToInt32(fileBuffer.AsSpan()[0..4]);
            if (version is not (4 or 5))
                return false;

            var pieceCountMaybe = BitConverter.ToUInt32(fileBuffer.AsSpan()[12..16]);
            return pieceCountMaybe is 0 or > MaxPlausiblePmdPieceCount;
        }

        private static bool IsPmcFile(byte[] fileBuffer)
        {
            // See the comment in IsPmdFile for an explanation.

            return fileBuffer.Length > 4
                && BitConverter.ToInt32(fileBuffer.AsSpan()[0..4]) == 6;
        }

        private static bool IsTobjFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4
                && BitConverter.ToInt32(fileBuffer.AsSpan()[0..4]) == 0x70b10a01;
        }

        private static bool IsSoundBankGuidsFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 38 &&
                Guid.TryParse(Encoding.ASCII.GetString(fileBuffer[0..38]), out var _);
        }

        private static bool IsFontFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 10 &&
                Encoding.UTF8.GetString(fileBuffer[0..10]) == "# SCS Font";
        }

        private static bool IsJpegFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 2
                && fileBuffer[0] == 0xFF && fileBuffer[1] == 0xD8;
        }

        private static bool IsTgaFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 18
                && Encoding.ASCII.GetString(fileBuffer[^18..^2]) == "TRUEVISION-XFILE";
        }

        private static bool IsPngFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 8)
                return false;

            byte[] magic = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
            return magic.SequenceEqual(fileBuffer[0..8]);
        }

        private static bool IsPsdFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[0..4]) == "8BPS";
        }

        private static bool IsZlibBlob(byte[] fileBuffer)
        {
            return fileBuffer.Length > 2 && 
                fileBuffer[0] == 0x78 && 
                (fileBuffer[1] == 0xDA || fileBuffer[1] == 0x9C 
                || fileBuffer[1] == 0x5E || fileBuffer[1] == 0x01);
        }

        private static bool IsPpdFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 4)
                return false;

            var version = BitConverter.ToInt32(fileBuffer.AsSpan()[0..4]);
            return version is >= 0x15 and <= 0x18;
        }

        private static bool IsMayaFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[0..4]) == "FOR4";
        }

        private static bool IsOggFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[0..4]) == "OggS";
        }
        
        private static bool IsRarFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 4 &&
                Encoding.ASCII.GetString(fileBuffer[0..4]) == "Rar!";
        }
        
        private static bool IsFbxFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 18 &&
                Encoding.ASCII.GetString(fileBuffer[0..18]) == "Kaydara FBX Binary";
        }

        private static bool IsXcfFile(byte[] fileBuffer)
        {
            return fileBuffer.Length > 13 &&
                Encoding.ASCII.GetString(fileBuffer[0..13]) == "gimp xcf file";
        }

        private static bool IsExrFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 4)
                return false;

            byte[] magic = [0x76, 0x2F, 0x31, 0x01];
            return magic.SequenceEqual(fileBuffer[0..4]);
        }

        private static bool IsBmpFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 2)
                return false;

            return fileBuffer[0] == 0x42 && fileBuffer[1] == 0x4D;
        }

        private static bool Is7zFile(byte[] fileBuffer)
        {
            if (fileBuffer.Length < 6) // 37 7A BC AF 27 1C
                return false;

            byte[] magic = [0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C];
            return magic.SequenceEqual(fileBuffer[0..6]);
        }

        public static FileType PathToFileType(string filePath)
        {
            var extension = Path.GetExtension(filePath).ToLowerInvariant();
            if (extension == ".dat" && filePath.Contains("glass"))
            {
                return FileType.Sui;
            }
            return ExtensionToFileType(extension);
        }

        public static FileType ExtensionToFileType(string extension)
        {
            // Maya junk; presumably autosaves? I've never used it
            if (extension.StartsWith(".maa"))
                return FileType.MayaAsciiScene;

            return extension switch
            {
                ".7z" => FileType._7z,
                ".bank" => FileType.SoundBank,
                ".bmp" => FileType.Bmp,
                ".dds" => FileType.Dds,
                ".exr" => FileType.OpenExr,
                ".fbx" => FileType.Fbx,
                ".font" => FileType.Font,
                ".fso" => FileType.Fso,
                ".guids" => FileType.SoundBankGuids,
                ".bank.guids" => FileType.SoundBankGuids,
                ".ini" => FileType.Ini,
                ".jpg" => FileType.Jpeg,
                ".mask" => FileType.TgaMask,
                ".mat" => FileType.Material,
                ".ma" => FileType.MayaAsciiScene,
                ".mb" => FileType.MayaBinaryScene,
                ".oga" => FileType.Ogg,
                ".ogg" => FileType.Ogg,
                ".ogv" => FileType.Ogg,
                ".pdn" => FileType.Pdn,
                ".pma" => FileType.Pma,
                ".pmc" => FileType.Pmc,
                ".pmd" => FileType.Pmd,
                ".pmg" => FileType.Pmg,
                ".png" => FileType.Png,
                ".ppd" => FileType.Ppd,
                ".psd" => FileType.Psd,
                ".rar" => FileType.Rar,
                ".rfx" => FileType.Rfx,
                ".rpl" => FileType.Replay,
                ".sbs" => FileType.SubstanceDesignerSource,
                ".sct" => FileType.Sct,
                ".sii" => FileType.Sii,
                ".vso" => FileType.Vso,
                ".xcf" => FileType.GimpXcf,
                ".xrc" => FileType.WxWidgetsResource,
                ".soundref" => FileType.SoundRef,
                ".swatch" => FileType.MayaSwatch,
                ".swatches" => FileType.MayaSwatches,
                ".sui" => FileType.Sui,
                ".svg" => FileType.Svg,
                ".tobj" => FileType.Tobj,
                ".mbd" => FileType.MapRoot,
                ".base" => FileType.MapBase,
                ".aux" => FileType.MapAux,
                ".snd" => FileType.MapSnd,
                ".data" => FileType.MapData,
                ".desc" => FileType.MapDesc,
                ".layer" => FileType.MapLayer,
                ".sbd" => FileType.MapSelection,
                _ => FileType.Unknown,
            };
        }

        public static string FileTypeToExtension(FileType fileType)
        {
            return fileType switch
            {
                FileType.SoundBank => ".bank",
                FileType.Bmp => ".bmp",
                FileType.Dds => ".dds",
                FileType.OpenExr => ".exr",
                FileType.Fbx => ".fbx",
                FileType.Font => ".font",
                FileType.Ini => ".ini",
                FileType.SoundBankGuids => ".bank.guids",
                FileType.Jpeg => ".jpg",
                FileType.TgaMask => ".mask",
                FileType.Material => ".mat",
                FileType.MayaAsciiScene => ".ma",
                FileType.MayaBinaryScene => ".mb",
                FileType.Ogg => ".ogg",
                FileType.Pdn => ".pdn",
                FileType.Pma => ".pma",
                FileType.Pmc => ".pmc",
                FileType.Pmd => ".pmd",
                FileType.Pmg => ".pmg",
                FileType.Png => ".png",
                FileType.Ppd => ".ppd",
                FileType.Psd => ".psd",
                FileType.Rar => ".rar",
                FileType.Replay => ".rpl",
                FileType.Rfx => ".rfx",
                FileType.SubstanceDesignerSource => ".sbs",
                FileType.Sct => ".sct",
                FileType.Sii => ".sii",
                FileType.SoundRef => ".soundref",
                FileType.Sui => ".sui",
                FileType.Svg => ".svg",
                FileType.MayaSwatch => ".swatch",
                FileType.MayaSwatches => ".swatches",
                FileType.Tobj => ".tobj",
                FileType.GimpXcf => ".xcf",
                FileType.WxWidgetsResource => ".xrc",
                FileType._7z => ".7z",
                FileType.MapRoot => ".mbd",
                FileType.MapBase => ".base",
                FileType.MapAux => ".aux",
                FileType.MapSnd => ".snd",
                FileType.MapData => ".data",
                FileType.MapDesc => ".desc",
                FileType.MapLayer => ".layer",
                FileType.MapSelection => ".sbd",
                _ => string.Empty,
            };
        }
    }
}
