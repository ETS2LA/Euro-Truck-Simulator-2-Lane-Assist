using System.IO;

namespace ETS2LA.Game.Extractor.Helpers
{
    internal class PathHelper
    {
        /// <summary>
        /// Combines two paths together with forward slashes with the leading slash removed
        /// </summary>
        /// <param name="firstPath"></param>
        /// <param name="secondPath"></param>
        /// <returns>The combined path</returns>
        internal static string CombinePath(string firstPath, string secondPath)
        {
            var fullPath = Path.Combine(firstPath, secondPath);

            return EnsureLocalPath(fullPath.Replace('\\', '/'));
        }

        /// <summary>
        /// Removes leading slash if the path contains it
        /// </summary>
        internal static string EnsureLocalPath(string path)
        {
            if (path.StartsWith("/"))
            {
                return path.Substring(1);
            }
            return path;
        }

        /// <summary>
        /// <para>If <paramref name="path"/> is not absolute <paramref name="currentPath"/> gets joined before it</para>
        /// <para>If it is absolute it will return the <paramref name="path"/> with the leading slash removed</para>
        /// </summary>
        /// <param name="path"></param>
        /// <param name="currentPath">string to be prefixed if path is not absolute</param>
        internal static string GetFilePath(string path, string currentPath = "")
        {
            if (path.StartsWith("/")) // absolute path
            {
                path = path.Substring(1);
                return path;
            }
            return CombinePath(currentPath, path);
        }

        /// <summary>
        /// Get Path to Directory from FilePath
        /// <para>Example: 'def/world/prefab.sii' will return 'def/world'</para>
        /// </summary>
        /// <param name="filePath"></param>
        /// <returns></returns>
        internal static string GetDirectoryPath(string filePath)
        {
            var lastSlash = filePath.LastIndexOf("/");
            return filePath.Substring(0, lastSlash);
        }

        /// <summary>
        /// Get FileName with extension from FilePath
        /// <para>Example: 'def/world/prefab.sii' will return 'prefab.sii'</para>
        /// </summary>
        /// <param name="filePath"></param>
        /// <returns></returns>
        internal static string GetFileNameFromPath(string filePath)
        {
            return Path.GetFileName(filePath);
        }

        /// <summary>
        /// Get FileName without extension from FilePath
        /// <para>Example: 'def/world/prefab.sii' will return 'prefab'</para>
        /// </summary>
        /// <param name="filePath"></param>
        /// <returns></returns>
        internal static string GetFileNameWithoutExtensionFromPath(string filePath)
        {
            return Path.GetFileNameWithoutExtension(filePath);
        }
    }
}