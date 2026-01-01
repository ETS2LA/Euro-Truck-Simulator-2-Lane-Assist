using Newtonsoft.Json;
using System.Text;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.FileSystem;

namespace ETS2LA.Game.Extractor
{
    public class TsCity
    {
        public string Name { get; set; }
        public string Group { get; set; }
        [JsonIgnore]
        public string LocalizationToken { get; set; }
        public string Country { get; set; }
        [JsonIgnore]
        public ulong Token { get; set; }
        [JsonIgnore]
        public List<int> XOffsets { get; }
        [JsonIgnore]
        public List<int> YOffsets { get; }

        public TsCity(string path)
        {
            var file = UberFileSystem.Instance.GetFile(path);

            if (file == null) return;

            var fileContent = file.Entry.Read();

            var lines = Encoding.UTF8.GetString(fileContent).Split('\n');
            var offsetCount = 0;
            XOffsets = new List<int>();
            YOffsets = new List<int>();

            foreach (var line in lines)
            {
                var (validLine, key, value) = SiiHelper.ParseLine(line);
                if (!validLine) continue;

                if (key == "city_data")
                {
                    Token = ScsToken.StringToToken(SiiHelper.Trim(value.Split('.')[1]));
                }
                else if (key == "city_name")
                {
                    Name = line.Split('"')[1];
                }
                else if (key == "city_name_localized")
                {
                    LocalizationToken = value.Split('"')[1];
                    LocalizationToken = LocalizationToken.Replace("@", "");
                }
                else if (key == "city_group")
                {
                    Group = value;
                }
                else if (key == "country")
                {
                    Country = value;
                }
                else if (key.Contains("map_x_offsets[]"))
                {
                    if (++offsetCount > 4)
                    {
                        if (int.TryParse(value, out var offset)) XOffsets.Add(offset);
                    }
                    if (offsetCount == 8) offsetCount = 0;
                }
                else if (key.Contains("map_y_offsets[]"))
                {
                    if (++offsetCount > 4)
                    {
                        if (int.TryParse(value, out var offset)) YOffsets.Add(offset);
                    }
                }
            }
        }
    }
}