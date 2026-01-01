using System.IO;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.TsItem
{
    public class TsCityItem : TsItem // TODO: Add zoom levels/range to show city names and icons correctly
    {
        public TsCity City { get; private set; }
        public ulong NodeUid { get; private set; }
        public float Width { get; private set; }
        public float Height { get; private set; }
        public TsCityItem(TsSector sector, int startOffset) : base(sector, startOffset)
        {
            Valid = true;
            TsCityItem825(startOffset);
        }

        public void TsCityItem825(int startOffset)
        {
            var fileOffset = startOffset + 0x34; // Set position at start of flags

            Hidden = (MemoryHelper.ReadUint8(Sector.Stream, fileOffset) & 0x01) != 0;
            var cityId = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset + 0x05);
            City = Sector.Mapper.LookupCity(cityId);
            if (City == null)
            {
                Valid = false;
                Logger.Error($"Could not find City: '{ScsToken.TokenToString(cityId)}'({cityId:X}) item uid: 0x{Uid:X}, " +
                    $"in {Path.GetFileName(Sector.FilePath)} @ {fileOffset} from '{Sector.GetUberFile().Entry.GetArchiveFile().GetPath()}'");
            }

            Width = MemoryHelper.ReadSingle(Sector.Stream, fileOffset += 0x05 + 0x08); // 0x05(flags) + 0x08(cityId)
            Height = MemoryHelper.ReadSingle(Sector.Stream, fileOffset += 0x04); // 0x08(Width)
            NodeUid = MemoryHelper.ReadUInt64(Sector.Stream, fileOffset += 0x04); // 0x08(height)
            fileOffset += 0x08; // nodeUid
            BlockSize = fileOffset - startOffset;
        }

        public override string ToString()
        {
            if (City == null) return "Error";
            var country = Sector.Mapper.GetCountryByTokenName(City.Country);
            var countryName = (country == null)
                ? City.Country
                : Sector.Mapper.Localization.GetLocaleValue(country.LocalizationToken) ?? country.Name;
            return $"{countryName} - {Sector.Mapper.Localization.GetLocaleValue(City.LocalizationToken) ?? City.Name}";
        }
    }
}
