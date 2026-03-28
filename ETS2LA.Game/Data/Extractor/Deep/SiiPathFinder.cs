using Sprache;
using System;
using System.Collections.Frozen;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using TruckLib;
using TruckLib.HashFs;
using TruckLib.Sii;
using static Extractor.PathUtils;

namespace Extractor.Deep
{
    internal partial class SiiPathFinder
    {
        /// <summary>
        /// Unit keys whose corresponding values are never paths and can thus be skipped.
        /// </summary>
        private static readonly FrozenSet<string> ignorableUnitKeys = new HashSet<string> {
            "package_version", "compatible_versions", "suitable_for",
            "conflict_with", "truck_y_override",

            // names
            "name", "names", "category", "sign_name", "display_name", "ferry_name",
            "static_lod_name", "board_name", "sign_template_names", "editor_name",
            "default_name", "stamp_name",

            // city
            "city_name", "city_name_localized", "short_city_name", "truck_lp_template",

            // curve_model
            "variation", "vegetation", "overlay", "no_stretch_start", "no_stretch_end",

            // vehicle
            "vehicle_brands", "acc_list", "trailer_chains", "info",

            // academy
            "map_title", "map_desc", "intro_cutscene_tag", "start_position_tag",

            // cutscene
            "condition_data", "str_params",

            "color_variant", // model 
            "allowed_vehicle", // traffic logic
            "overlay_schemes", // road
        }.ToFrozenSet();

        /// <summary>
        /// Unit classes which never contain paths and can thus be skipped entirely.
        /// </summary>
        private static readonly FrozenSet<string> ignorableUnitClasses = new HashSet<string> {
            "cargo_def", "traffic_spawn_condition", "traffic_rule_data", "mail_text", "driver_names",
            "localization_db", "input_device_config", "default_input_config", "default_input_entry",
            "default_setup_entry", "academy_scenario_goal",
        }.ToFrozenSet();

        [GeneratedRegex(@"(?:src|face)=(\S*)")]
        private static partial Regex uiHtmlPathRegex();

        /// <summary>
        /// Returns paths referenced in the given SII file.
        /// If the file fails to parse, an empty set is returned.
        /// </summary>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fs">The archive which is being read from as <see cref="IFileSystem"/>.</param>
        /// <returns>Paths referenced in the file.</returns>
        public static (PotentialPaths Paths, HashSet<string> ConsumedSuis) FindPathsInSii(
            byte[] fileBuffer, string filePath, IFileSystem fs)
        {
            var magic = Encoding.UTF8.GetString(fileBuffer[0..4]);
            if (!(magic == "SiiN" // regular sii
                || magic == "\uFEFFS" // regular sii with fucking BOM
                || magic == "ScsC" // encrypted sii
                || magic.StartsWith("3nK") // 3nK-encoded sii
                ))
            {
                #if DEBUG
                Console.Error.WriteLine($"Not a sii file: {filePath}");
                #endif
                return ([], []);
            }

            var siiDirectory = GetParent(filePath);
            try
            {
                var sii = SiiFile.Load(fileBuffer, siiDirectory, fs, true);
                var paths = FindPathsInSii(sii, fs);
                var suis = sii.Includes.ToHashSet();
                return (paths, suis);
            }
            catch (ParseException)
            {
                if (!filePath.StartsWith("/ui/template"))
                    Debugger.Break();
                throw;
            }
            catch (Exception)
            {
                Debugger.Break();
                throw;
            }
        }

        public static (PotentialPaths Paths, HashSet<string> ConsumedSuis) FindPathsInSii(
            string siiStr, string filePath, IFileSystem fs)
        {
            var siiDirectory = GetParent(filePath);
            try
            {
                var sii = SiiFile.Load(siiStr, siiDirectory, fs, true);
                var paths = FindPathsInSii(sii, fs);
                var suis = sii.Includes.ToHashSet();
                return (paths, suis);
            }
            catch (Exception)
            {
                Debugger.Break();
                throw;
            }
        }

        private static PotentialPaths FindPathsInSii(SiiFile sii, IFileSystem fs)
        {
            PotentialPaths potentialPaths = [];

            foreach (var include in sii.Includes)
            {
                if (include.StartsWith('/'))
                    potentialPaths.Add(include);
                else
                    potentialPaths.Add('/' + include);
            }

            foreach (var unit in sii.Units)
            {
                if (unit.Class == "company_permanent")
                {
                    var companyUnitName = unit.Name.Split('.')[^1];
                    potentialPaths.Add($"/material/ui/company/small/{companyUnitName}.mat", null);
                }
                else if (unit.Class == "country_data")
                {
                    var country = unit.Name.Split('.')[^1];
                    potentialPaths.Add($"/font/license_plate/{country}.font", null);
                    ConstructLicensePlateMatPaths(country, potentialPaths, fs);
                }
                else if (unit.Class == "mod_package")
                {
                    ConstructLocalizedModDescriptionPaths(unit, potentialPaths);
                }

                foreach (var attrib in unit.Attributes)
                {
                    ProcessSiiUnitAttribute(unit.Class, attrib, potentialPaths);
                }
            }

            return potentialPaths;
        }

        private static void ConstructLocalizedModDescriptionPaths(Unit unit, PotentialPaths potentialPaths)
        {
            if (!unit.Attributes.TryGetValue("description_file", out var descriptionFile))
            {
                return;
            }

            string[] locales = [
                "bg_bg", "ca_es", "cs_cz", "da_dk", "de_de", "el_gr", "en_gb", "en_us",
                "es_es", "es_la", "et_ee", "eu_es", "fi_fi", "fr_ca", "fr_fr", "gl_es",
                "hr_hr", "hu_hu", "it_it", "ja_jp", "ka_ge", "ko_kr", "lt_lt", "lv_lv",
                "mk_mk", "nl_nl", "no_no", "pl_pl", "pl_si", "pt_br", "pt_pt", "ro_ro",
                "ru_ru", "sk_sk", "sl_sl", "sr_sp", "sr_sr", "sv_se", "tr_tr", "uk_uk",
                "vi_vn", "zh_cn", "zh_tw"
            ];
            foreach (var locale in locales)
            {
                potentialPaths.Add(PathUtils.AppendBeforeExtension(descriptionFile, '.' + locale));
            }
        }

        private static void ConstructLicensePlateMatPaths(string country, PotentialPaths potentialPaths,
            IFileSystem fs)
        {
            potentialPaths.Add($"/material/ui/lp/{country}/trailer.mat", null);

            var licensePlateSiiPath = $"/def/country/{country}/license_plates.sii";
            if (!fs.FileExists(licensePlateSiiPath))
                return;

            try
            {
                var licensePlates = SiiFile.Open(licensePlateSiiPath, fs);
                ConstructLicensePlateMatPaths(country, potentialPaths, licensePlates);
            }
            catch
            {
                Debugger.Break();
            }
        }

        internal static void ConstructLicensePlateMatPaths(string country, PotentialPaths potentialPaths,
            SiiFile licensePlates)
        {
            // See https://modding.scssoft.com/wiki/Games/ETS2/Modding_guides/1.36#Traffic_data.

            potentialPaths.Add($"/material/ui/lp/{country}/trailer.mat");
            potentialPaths.Add($"/material/ui/lp/{country}/truck_front.mat");
            potentialPaths.Add($"/material/ui/lp/{country}/truck_rear.mat");
            potentialPaths.Add($"/material/ui/lp/{country}/police_front.mat");
            potentialPaths.Add($"/material/ui/lp/{country}/police_rear.mat");

            foreach (var lp in licensePlates.Units)
            {
                if (!lp.Attributes.TryGetValue("type", out var type))
                    continue;

                // special case, handled above
                if (type == "trailer")
                    continue;

                var typePrefix = type == "car" ? "" : type + "_";

                if (lp.Attributes.TryGetValue("background_front", out var bgFront))
                {
                    potentialPaths.Add($"/material/ui/lp/{country}/{bgFront}.mat", null);
                }
                else
                {
                    potentialPaths.Add($"/material/ui/lp/{country}/{typePrefix}front.mat", null);
                }

                if (lp.Attributes.TryGetValue("background_rear", out var bgRear))
                {
                    potentialPaths.Add($"/material/ui/lp/{country}/{bgRear}.mat", null);
                }
                else
                {
                    potentialPaths.Add($"/material/ui/lp/{country}/{typePrefix}rear.mat", null);
                }
            }
        }

        internal static void ProcessSiiUnitAttribute(string unitClass,
            KeyValuePair<string, dynamic> attrib, PotentialPaths potentialPaths)
        {
            if (ignorableUnitClasses.Contains(unitClass))
                return;

            if (ignorableUnitKeys.Contains(attrib.Key))
                return;

            if (attrib.Value is string)
            {
                ProcessStringAttribute(attrib, unitClass, potentialPaths);
            }
            else if (attrib.Value is IList<dynamic> && attrib.Value[0] is string)
            {
                ProcessArrayAttribute(attrib, unitClass, potentialPaths);
            }
        }

        private static void ProcessArrayAttribute(KeyValuePair<string, dynamic> attrib, string unitClass,
            PotentialPaths potentialPaths)
        {
            IList<dynamic> items = attrib.Value;
            var strings = items.Where(x => x is string).Cast<string>();

            if (unitClass == "license_plate_data" || unitClass == "city_data")
            {
                if (attrib.Key.Contains("def"))
                {
                    foreach (var str in strings)
                    {
                        // Extract paths from img and font tags of the faux-HTML
                        // used in UI strings.
                        var matches = uiHtmlPathRegex().Matches(str);
                        foreach (Match match in matches)
                        {
                            potentialPaths.Add(match.Groups[1].Value, null);
                        }
                    }
                }
            }
            else
            {
                foreach (var str in strings)
                {
                    var key = attrib.Key;
                    if (key == "sounds" || key == "sound_path")
                    {
                        potentialPaths.Add(GetSoundPath(str), null);
                    }
                    else if (key == "adr_info_icon" || key == "fallback")
                    {
                        var parts = str.Split("|");
                        if (parts.Length == 2)
                            potentialPaths.Add(parts[1], null);
                        else
                            Debugger.Break();
                    }
                    else if (unitClass == "company_permanent" && key == "sound")
                    {
                        var parts = str.Split("|");
                        if (parts.Length == 2)
                            potentialPaths.Add(parts[1], null);
                        else
                            Debugger.Break();
                    }
                    else if (unitClass == "overlay_def")
                    {
                        potentialPaths.Add($"/material/overlay/{str}.mat", null);
                        if (attrib.Key == "road_names")
                        {
                            potentialPaths.Add($"/material/ui/map/road/road_{str}.mat", null);
                        }
                    }
                    else
                    {
                        potentialPaths.Add(str, null);
                    }
                }
            }
        }

        private static string GetSoundPath(string str)
        {
            var pipeIdx = str.IndexOf('|');
            if (pipeIdx == -1)
                pipeIdx = 0;
            else
                pipeIdx += 1;

            var hashIdx = str.IndexOf('#');
            if (hashIdx == -1)
                hashIdx = str.Length;

            var soundPath = str[pipeIdx..hashIdx];
            return soundPath;
        }

        private static void ProcessStringAttribute(KeyValuePair<string, dynamic> attrib,
            string unitClass, PotentialPaths potentialPaths)
        {
            string str = attrib.Value;
            string key = attrib.Key;

            if (unitClass == "ui::text"
                || unitClass == "ui::text_template"
                || unitClass == "ui::text_common"
                || unitClass == "ui_text_bar"
                || (unitClass == "sign_template_text" && key == "text")
                || key == "offence_message")
            {
                // Extract paths from img and font tags of the faux-HTML
                // used in UI strings.
                var matches = Regex.Matches(attrib.Value, @"(?:src|face)=(\S*)");
                foreach (Match match in matches)
                {
                    potentialPaths.Add(match.Groups[1].Value, null);
                }
            }
            else if (key == "icon" && unitClass != "mod_package")
            {
                // See https://modding.scssoft.com/wiki/Documentation/Engine/Units/trailer_configuration
                // and https://modding.scssoft.com/wiki/Documentation/Engine/Units/accessory_data
                var iconPath = $"/material/ui/accessory/{attrib.Value}.mat";
                potentialPaths.Add(iconPath, null);
            }
            else if (key == "sound_path" || key == "sound_sfx" || key == "scene_music")
            {
                potentialPaths.Add(GetSoundPath(str), null);
            }
            else
            {
                potentialPaths.Add(str, null);
            }
        }

        public static void FindPathsInUnconsumedSuis(HashSet<string> consumedSuis,
            HashSet<string> everything, AssetLoader multiModWrapper)
        {
            var allSuis = everything.Where(p => p.EndsWith(".sui"));
            var unconsumedSuis = allSuis.Except(consumedSuis).ToList();
            var paths = FindPathsInUnconsumedSuis(unconsumedSuis, multiModWrapper);
            everything.UnionWith(paths);
        }

        public static PotentialPaths FindPathsInUnconsumedSuis(IEnumerable<string> unconsumedSuis, IFileSystem fs)
        {
            PotentialPaths paths = [];
            foreach (var sui in unconsumedSuis)
            {
                if (!fs.FileExists(sui))
                    continue;

                var text = fs.ReadAllText(sui);
                var siiText = string.Format("""
                    SiiNunit 
                    {{
                        foo : bar 
                        {{
                    @include "{0}"
                        }}
                    }}
                    """, sui);

                try
                {
                    var (discovered, _) = FindPathsInSii(siiText, sui, fs);
                    paths.UnionWith(discovered.Except([sui]));
                }
                catch (Exception ex)
                {
                    #if DEBUG
                    Console.WriteLine(ex.ToString());
                    Debugger.Break();
                    #endif
                }
            }
            return paths;
        }
    }
}
