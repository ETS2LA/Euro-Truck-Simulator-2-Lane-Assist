using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using TruckLib;
using TruckLib.Sii;
using static Extractor.PathSubstitution;

namespace Extractor
{
    /// <summary>
    /// Base class for archive extractors.
    /// </summary>
    public abstract class Extractor : IDisposable
    {
        public abstract IFileSystem FileSystem { get; }

        /// <summary>
        /// Gets or sets whether existing files should be overwritten.
        /// </summary>
        public bool Overwrite { get; set; } = true;

        /// <summary>
        /// The absolute path of the archive file.
        /// </summary>
        public string ScsPath { get; init; }

        /// <summary>
        /// Files which were renamed because they contained invalid characters.
        /// </summary>
        protected List<(string ArchivePath, string SanitizedPath)> renamedFiles = [];

        /// <summary>
        /// Files which were modified to replace references to paths which had 
        /// to be renamed.
        /// </summary>
        protected List<string> modifiedFiles = [];

        /// <summary>
        /// The command line options set by the user.
        /// </summary>
        protected Options opt;

        public Extractor(string scsPath, Options opt) 
        { 
            ScsPath = scsPath;
            Overwrite = !opt.SkipIfExists;
            this.opt = opt;
        }

        /// <summary>
        /// Extracts the archive to the given directory.
        /// </summary>
        /// <param name="destination">The directory to which the extracted files will be written.</param>
        public abstract void Extract(string destination);

        public abstract List<Tree.Directory> GetDirectoryTree();

        public abstract void PrintPaths(bool includeAll);

        public abstract void PrintContentSummary();

        public abstract void PrintExtractionResult();

        public abstract void Dispose();

        protected static bool PerformSubstitutionIfRequired(string archivePath, ref byte[] buffer, 
            Dictionary<string, string> substitutions)
        {
            var wasModified = false;

            var extension = Path.GetExtension(archivePath).ToLowerInvariant();
            if (substitutions is not null && substitutions.Count > 0)
            {
                if (extension == ".sii" || extension == ".sui" || extension == ".mat")
                {
                    (wasModified, buffer) = SubstitutePathsInTextFormats(buffer, substitutions, extension);
                }
                else if (extension == ".tobj")
                {
                    (wasModified, buffer) = SubstitutePathsInTobj(buffer, substitutions);
                }
            }
            else
            {
                if (extension == ".sii" || extension == ".sui")
                {
                    buffer = SiiFile.Decode(buffer);
                }
            }

            return wasModified;
        }

        protected void WriteRenamedSummary(string outputRoot)
        {
            if (renamedFiles.Count == 0)
                return;

            if (opt.DryRun)
                return;

            var path = Path.Combine(outputRoot, "_renamed.txt");
            path = PathUtils.IncrementPathIfExists(path);

            using var sw = new StreamWriter(path);
            foreach (var (before, after) in renamedFiles)
            {
                sw.WriteLine($"{before}\t{after}");
            }         
        }

        protected void WriteModifiedSummary(string outputRoot)
        {
            if (modifiedFiles.Count == 0)
                return;

            if (opt.DryRun)
                return;

            var path = Path.Combine(outputRoot, "_modified.txt");
            path = PathUtils.IncrementPathIfExists(path);

            using var sw = new StreamWriter(path);
            foreach (var file in modifiedFiles)
            {
                sw.WriteLine(file);
            }
        }
    }
}
