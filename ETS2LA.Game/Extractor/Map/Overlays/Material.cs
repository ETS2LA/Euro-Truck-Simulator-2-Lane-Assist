using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using ETS2LA.Game.Extractor.FileSystem;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.Map.Overlays
{
    internal class Material
    {
        private readonly string _matFilePath;

        public List<ColorLinear> AuxValues = new List<ColorLinear>();

        public Material(string matFilePath)
        {
            _matFilePath = matFilePath;
        }

        public string EffectName { get; private set; }

        public string TextureSource { get; private set; }

        public bool Parse()
        {
            var matFile = UberFileSystem.Instance.GetFile(_matFilePath);
            if (matFile == null)
            {
                Logger.Error($"Could not load material file '{_matFilePath}'");
                return false;
            }

            var data = matFile.Entry.Read();
            var lines = Encoding.UTF8.GetString(data).Split('\n');

            foreach (var line in lines)
            {
                var (validLine, key, value) = SiiHelper.ParseLine(line);
                if (!validLine) continue;

                if (key == "effect")
                {
                    EffectName = value.Contains("\"")
                        ? value.Split('"')[1]
                        : value.Trim('{').Trim();
                }

                if (key.StartsWith("aux["))
                {
                    var auxStrValues = value.Trim().Trim('{', '}').Split(',');
                    if (auxStrValues.Length != 4) continue;
                    try
                    {
                        AuxValues.Add(
                            new ColorLinear(
                                double.Parse(auxStrValues[0], CultureInfo.InvariantCulture),
                                double.Parse(auxStrValues[1], CultureInfo.InvariantCulture),
                                double.Parse(auxStrValues[2], CultureInfo.InvariantCulture),
                                double.Parse(auxStrValues[3], CultureInfo.InvariantCulture)
                            )
                        );
                    }
                    catch (Exception _)
                    {
                        Logger.Error($"Could not read aux values from '{line}' for mat file '{_matFilePath}'");
                    }
                }
                else if ((key == "texture" || key == "source") && value.Contains(".tobj"))
                {
                    TextureSource =
                        PathHelper.CombinePath(PathHelper.GetDirectoryPath(_matFilePath), value.Split('"')[1]);
                }
            }

            return true;
        }
    }
}
