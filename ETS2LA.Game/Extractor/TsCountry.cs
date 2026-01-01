using Newtonsoft.Json;
using System.Globalization;
using System.Text;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.FileSystem;

namespace ETS2LA.Game.Extractor
{
    public class TsCountry
    {
        [JsonIgnore]
        public ulong Token { get; }

        public int CountryId { get; }
        public string Name { get; }
        [JsonIgnore]
        public string LocalizationToken { get; }
        public string CountryCode { get; }
        public float X { get; }
        public float Y { get; }

        public TsCountry(string path)
        {
            var file = UberFileSystem.Instance.GetFile(path);

            if (file == null) return;

            var fileContent = file.Entry.Read();

            var lines = Encoding.UTF8.GetString(fileContent).Split('\n');

            foreach (var line in lines)
            {
                var (validLine, key, value) = SiiHelper.ParseLine(line);
                if (!validLine) continue;

                if (key == "country_data")
                {
                    Token = ScsToken.StringToToken(SiiHelper.Trim(value.Split('.')[2]));
                }
                else if (key == "country_id")
                {
                    CountryId = int.Parse(value);
                }
                else if (key == "name")
                {
                    Name = value.Split('"')[1];
                }
                else if (key == "name_localized")
                {
                    LocalizationToken = value.Split('"')[1];
                    LocalizationToken = LocalizationToken.Replace("@", "");
                }
                else if (key == "country_code")
                {
                    CountryCode = value.Split('"')[1];
                }
                else if (key == "pos")
                {
                    var vector = value.Split('(')[1].Split(')')[0];
                    var values = vector.Split(',');
                    X = float.Parse(values[0], CultureInfo.InvariantCulture);
                    Y = float.Parse(values[2], CultureInfo.InvariantCulture);
                }
            }
        }
    }
}