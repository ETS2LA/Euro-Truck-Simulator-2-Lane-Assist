using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Extractor
{
    public enum ExitCode
    {
        /// <summary>
        /// All archives extracted without fatal errors.
        /// </summary>
        Success = 0,

        /// <summary>
        /// At least one archive extracted without fatal errors.
        /// </summary>
        PartialSuccess = 1,

        /// <summary>
        /// The extractor encountered multiple errors types and no archive
        /// extracted successfully.
        /// </summary>
        AllFailed = 2,

        /// <summary>
        /// The user did not specify any input files or directories.
        /// </summary>
        NoInput = 3,

        /// <summary>
        /// The user did not specify any input files or directories.
        /// </summary>
        NotFound = 4,

        /// <summary>
        /// The file passed to --paths or --additional does not exist or 
        /// could not be opened.
        /// </summary>
        PathFileNotFound = 5,

        /// <summary>
        /// Some of the passed options cannot be combined.
        /// </summary>
        IncompatibleOptions = 6,

        /// <summary>
        /// The extractor is in regular extraction mode, no non-root 
        /// start paths have been specified, and none of the passed archives 
        /// have a root directory.
        /// </summary>
        NoRoot = 7,

        /// <summary>
        /// The extractor was not able to open any of the passed archives.
        /// </summary>
        FailedToOpen = 8,
    }

    public enum ExtractionResult
    {        
        /// <summary>
        /// No fatal errros were encountered.
        /// </summary>
        Success,

        /// <summary>
        /// The specified file was not found.
        /// </summary>
        NotFound,

        /// <summary>
        /// Some of the passed options cannot be combined.
        /// </summary>
        IncompatibleOptions,

        /// <summary>
        /// The extractor is in regular extraction mode, no non-root 
        /// start paths have been specified, and the passed archive does not
        /// have a root directory.
        /// </summary>
        RootMissing,

        /// <summary>
        /// The extractor is in regular extraction mode, no non-root 
        /// start paths have been specified, and the passed archive has an
        /// empty root directory.
        /// </summary>
        RootEmpty,

        /// <summary>
        /// The specified file could not be opened.
        /// </summary>
        FailedToOpen,
    }
}
