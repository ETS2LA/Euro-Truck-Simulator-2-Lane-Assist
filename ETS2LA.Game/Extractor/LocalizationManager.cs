using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using ETS2LA.Game.Extractor.FileSystem;
using ETS2LA.Logging;

namespace ETS2LA.Game.Extractor.Helpers
{
    public class LocalizationManager
    {
        private readonly Dictionary<string, Dictionary<string, string>> _localization = new Dictionary<string, Dictionary<string, string>>();

        public string SelectedLocalization = "";

        public LocalizationManager()
        {
            _localization.Add("None", new Dictionary<string, string>());
        }

        public void LoadLocaleValues()
        {
            var localeDir = UberFileSystem.Instance.GetDirectory("locale");
            if (localeDir == null)
            {
                Logger.Error("Could not find locale directory.");
                return;
            }
            foreach (var localeDirDirectoryName in localeDir.GetSubDirectoryNames())
            {
                var localeDirDirectory = UberFileSystem.Instance.GetDirectory($"locale/{localeDirDirectoryName}");

                foreach (var localeFilePath in localeDirDirectory.GetFilesByExtension($"locale/{localeDirDirectoryName}", ".sui", ".sii"))
                {
                    ParseLocaleFile(localeFilePath, localeDirDirectoryName);
                }
            }
        }

        private void ParseLocaleFile(string localeFilePath, string locale)
        {
            var localeFile = UberFileSystem.Instance.GetFile(localeFilePath);
            var entryContents = localeFile.Entry.Read();
            var magic = MemoryHelper.ReadUInt32(entryContents, 0);
            var fileContents = (magic == 21720627) ? MemoryHelper.Decrypt3Nk(entryContents) : Encoding.UTF8.GetString(entryContents);
            if (fileContents == null)
            {
                Logger.Error($"Could not read locale file '{localeFilePath}'");
                return;
            }

            var key = string.Empty;

            foreach (var l in fileContents.Split('\n'))
            {
                if (!l.Contains(':')) continue;

                if (l.Contains("key[]"))
                {
                    key = l.Split('"')[1];
                }
                else if (l.Contains("val[]"))
                {
                    var val = l.Split('"')[1];
                    if (key != string.Empty && val != string.Empty)
                    {
                        AddLocaleValue(locale, key, val);
                    }
                }
            }
        }

        /// <summary>
        /// Change the selected localization to the provided one
        /// </summary>
        /// <param name="localeName">Localization to change to</param>
        public void ChangeLocalization(string localeName)
        {
            SelectedLocalization = localeName;
            Logger.Debug($"Switched localization to '{localeName}'");
        }

        private void AddLocale(string localeName)
        {
            if (!_localization.ContainsKey(localeName))
            {
                _localization.Add(localeName, new Dictionary<string, string>());
            }
        }

        /// <summary>
        /// Gets the localized name for the given locale and key.
        /// </summary>
        /// <param name="localized_name_key">Key for the localized name</param>
        /// <param name="localeName">Name of the locale eg. 'en_gb' to get the value in, if not provided will use <see cref="SelectedLocalization"/></param>
        /// <returns>
        /// String - If key exists for the given locale name
        /// <para>Null - If it could not be found</para>
        /// </returns>
        public string GetLocaleValue(string localized_name_key, string localeName = "")
        {
            if (localized_name_key == null) return null;
            if (localeName == "") localeName = SelectedLocalization;
            if (_localization.ContainsKey(localeName) && _localization[localeName].ContainsKey(localized_name_key))
            {
                return _localization[localeName][localized_name_key];
            }
            return null;
        }

        /// <summary>
        /// Adds the localized name and the key to the specified locale
        /// </summary>
        /// <param name="localeName">Name of the locale eg. 'en_gb'</param>
        /// <param name="localized_name_key">Key for the localized name</param>
        /// <param name="localized_name">Localized name</param>
        public void AddLocaleValue(string localeName, string localized_name_key, string localized_name)
        {
            if (!_localization.ContainsKey(localeName))
            {
                AddLocale(localeName);
            }

            if (!_localization[localeName].ContainsKey(localized_name_key))
            {
                 _localization[localeName].Add(localized_name_key, localized_name);
            }
        }

        public List<string> GetLocales() => _localization.Keys.ToList();
    }
}