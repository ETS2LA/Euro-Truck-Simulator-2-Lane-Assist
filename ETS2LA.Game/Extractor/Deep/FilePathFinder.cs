using System;
using System.Collections.Frozen;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using TruckLib;
using TruckLib.Models;
using TruckLib.Sii;
using static Extractor.PathUtils;

namespace Extractor.Deep
{
    using FinderFunc = Func<byte[], string, PotentialPaths>;

    internal partial class FilePathFinder
    {
        /// <summary>
        /// File types which can be ignored because they don't contain
        /// any path references.
        /// </summary>
        public static readonly FrozenSet<FileType> IgnorableFileTypes = new HashSet<FileType>() {
            FileType.Bmp,
            FileType.Dds,
            FileType.Fbx,
            FileType.Fso,
            FileType.GimpXcf,
            FileType.Ini,
            FileType.Jpeg,
            FileType.MapRoot,
            FileType.MapBase,
            FileType.MapAux,
            FileType.MapSnd,
            FileType.MapData,
            FileType.MapDesc,
            FileType.MapLayer,
            FileType.MapSelection,
            FileType.MayaAsciiScene,
            FileType.MayaBinaryScene,
            FileType.MayaFile,
            FileType.MayaSwatch,
            FileType.MayaSwatches,
            FileType.Ogg,
            FileType.OpenExr,
            FileType.Pma,
            FileType.Pmc,
            FileType.Pmg,
            FileType.Png,
            FileType.Ppd,
            FileType.Psd,
            FileType.Rar,
            FileType.Replay,
            FileType.Rfx,
            FileType.Sct,
            FileType.SoundBank,
            FileType.SoundBankGuids,
            FileType.SubstanceDesignerSource,
            FileType.Sui,
            FileType.Svg,
            FileType.TgaMask,
            FileType.Vso,
            FileType.WxWidgetsResource,
            FileType.ZlibBlob,
        }.ToFrozenSet();

        /// <summary>
        /// Associates a file type with a method which analyzes it.
        /// </summary>
        private readonly FrozenDictionary<FileType, FinderFunc> finders;

        /// <summary>
        /// Paths that have been visited so far.
        /// </summary>
        private readonly HashSet<string> visited;

        /// <summary>
        /// File paths that are referenced by files in this archive.
        /// </summary>
        private readonly HashSet<string> referencedFiles;

        /// <summary>
        /// Directories discovered during the first phase which might contain tobj files.
        /// This is used to find the absolute path of tobj files that are referenced in 
        /// mat files for which the mat path was not found and the tobj is referenced as
        /// relative path only.
        /// </summary>
        private readonly HashSet<string> dirsToSearchForRelativeTobj;

        /// <summary>
        /// The archive (or the <see cref="TruckLib.HashFs.AssetLoader">AssetLoader</see>
        /// for a multi-mod archive) which is being analyzed.
        /// </summary>
        private readonly IFileSystem fs;

        [GeneratedRegex(@"image:(.*?),")]
        private static partial Regex fontImagePathRegex();

        private readonly HashSet<string> consumedSuis;

        /// <summary>
        /// Instantiates a <c>FilePathFinder</c>.
        /// </summary>
        /// <param name="fs">The archive (or the <see cref="TruckLib.HashFs.AssetLoader">AssetLoader</see>
        /// for a multi-mod archive) which is being analyzed (of the parenting PathFinder).</param>
        /// <param name="visited">The set of visited paths (of the parenting PathFinder).</param>
        /// <param name="referencedFiles">The set of files referenced in the archive 
        /// (of the parenting PathFinder).</param>
        /// <param name="dirsToSearchForRelativeTobj">The set of dirs which may contain tobj files
        /// (of the parenting PathFinder).</param>
        public FilePathFinder(IFileSystem fs, HashSet<string> visited,
            HashSet<string> referencedFiles, HashSet<string> dirsToSearchForRelativeTobj,
            HashSet<string> consumedSuis)
        {
            this.visited = visited;
            this.dirsToSearchForRelativeTobj = dirsToSearchForRelativeTobj;
            this.referencedFiles = referencedFiles;
            this.fs = fs;
            this.consumedSuis = consumedSuis;
            finders = new Dictionary<FileType, FinderFunc>()
            {
                { FileType.Sii, FindPathsInSii },
                { FileType.SoundRef, FindPathsInSoundref },
                { FileType.Pmd, FindPathsInPmd },
                { FileType.Tobj, FindPathsInTobj },
                { FileType.Material, FindPathsInMat },
                { FileType.Font, FindPathsInFont },
            }.ToFrozenDictionary();
        }

        /// <summary>
        /// Returns paths referenced in the given file which have not yet been visited.
        /// If the file type is ignored, an empty set is returned.
        /// </summary>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileType">The file type.</param>
        /// <returns>Paths referenced in the file.</returns>
        public PotentialPaths FindPathsInFile(byte[] fileBuffer, string filePath, FileType fileType)
        {
            if (IgnorableFileTypes.Contains(fileType))
            {
                return [];
            }

            if (finders.TryGetValue(fileType, out var finder))
            {
                try
                {
                    return finder(fileBuffer, filePath);
                }
                catch (Exception ex)
                {
                    #if DEBUG
                    Console.Error.WriteLine($"Unable to parse {filePath}: " +
                        $"{ex.GetType().Name}: {ex.Message.Trim()}");
                    #endif
                    return [];
                }
            }
            else
            {
                return [];
            }
        }

        /// <summary>
        /// Returns paths referenced in a SII file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInSii(byte[] fileBuffer, string filePath)
        {
            var (potentialPaths, newSuis) = SiiPathFinder.FindPathsInSii(fileBuffer, filePath, fs);
            consumedSuis.UnionWith(newSuis);
            potentialPaths.ExceptWith(visited);
            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in a .font file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInFont(byte[] fileBuffer, string filePath)
        {
            PotentialPaths potentialPaths = [];

            var matches = fontImagePathRegex().Matches(Encoding.UTF8.GetString(fileBuffer));
            foreach (Match match in matches)
            {
                var path = match.Groups[1].Value;
                potentialPaths.Add(path, visited);
                if (path.EndsWith(".mat"))
                {
                    potentialPaths.Add(Path.ChangeExtension(path, ".font"), visited);
                }
            }

            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in a .mat file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInMat(byte[] fileBuffer, string filePath)
        {
            PotentialPaths potentialPaths = [];

            MatFile mat;
            try
            {
                mat = MatFile.Load(Encoding.UTF8.GetString(fileBuffer));
            }
            catch (Exception)
            {
                //Debugger.Break();
                throw;
            }

            foreach (var texture in mat.Textures)
            {
                if (!texture.Attributes.TryGetValue("source", out var value)
                    || value is not string path)
                {
                    continue;
                }

                if (path.StartsWith('/'))
                {
                    potentialPaths.Add(path, visited);
                }
                else
                {
                    if (filePath == null)
                    {
                        foreach (var dir in dirsToSearchForRelativeTobj)
                        {
                            var potentialAbsPath = $"{dir}/{path}";
                            if (fs.FileExists(potentialAbsPath))
                            {
                                potentialPaths.Add(potentialAbsPath, visited);
                            }
                        }
                    }
                    else
                    {
                        var matDirectory = GetParent(filePath);
                        path = $"{matDirectory}/{path}";
                        potentialPaths.Add(path, visited);
                    }
                }
            }

            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in a .tobj file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInTobj(byte[] fileBuffer, string filePath)
        {
            PotentialPaths potentialPaths = [];

            var tobj = Tobj.Load(fileBuffer);
            potentialPaths.Add(tobj.TexturePath);
            referencedFiles.Add(tobj.TexturePath);

            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in a .pmd file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInPmd(byte[] fileBuffer, string filePath)
        {
            PotentialPaths potentialPaths = [];

            var model = Model.Load(fileBuffer, []);
            foreach (var look in model.Looks)
            {
                potentialPaths.UnionWith(look.Materials);
                referencedFiles.UnionWith(look.Materials);
            }

            return potentialPaths;
        }

        /// <summary>
        /// Returns paths referenced in a .soundref file.
        /// </summary>
        /// <param name="filePath">The path of the file in the archive.</param>
        /// <param name="fileBuffer">The extracted content of the file.</param>
        /// <returns>Discovered paths.</returns>
        private PotentialPaths FindPathsInSoundref(byte[] fileBuffer, string filePath)
        {
            PotentialPaths potentialPaths = [];

            var lines = Encoding.UTF8.GetString(fileBuffer)
                .Trim(['\uFEFF', '\0'])
                .Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries);
            foreach (var line in lines)
            {
                if (line.StartsWith("source="))
                {
                    var path = line[(line.IndexOf('"') + 1)..line.IndexOf('#')];
                    potentialPaths.Add(path, visited);
                }
            }

            return potentialPaths;
        }
    }
}
