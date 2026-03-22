# Extractor
A cross-platform .scs extractor for both HashFS and ZIP.


## Features
* Supports HashFS v1 and v2 as well as ZIP (including "locked" ZIP files)
* Can extract multiple archives at once
* Partial extraction
* Raw dumps
* Built-in path-finding mode for HashFS archives without directory listings
* Automatic conversion of 3nK-encoded and encrypted SII files


## Build
For x64 Windows and Linux, a standalone executable is available on the Releases page. On other platforms, install the
.NET 8 SDK and run the following:

```sh
git clone https://github.com/sk-zk/Extractor.git
cd Extractor
dotnet publish -c Release
```


## Usage
```
extractor path... [options]
```

### General options
<table>
<thead>
  <tr>
    <td><b>Short</b></td>
    <td><b>Long&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</b></td>
    <td><b>Description</b></td>
  </tr>
</thead>
<tr>
  <td><code>-a</code></td>
  <td><code>--all</code></td>
  <td>Extracts all .scs archives in the specified directory.</td>
</tr>
<tr>
  <td><code>-d</code></td>
  <td><code>--dest</code></td>
  <td>Sets the output directory. Defaults to <code>./extracted</code>.</td>
</tr>
<tr>
  <td></td>
  <td><code>--dry-run</code></td>
  <td>Don't write anything to disk.</td>
</tr>
<tr>
  <td><code>-f</code></td>
  <td><code>--filter</code></td>
  <td><p>Limits extraction to files whose paths match one or more of the specified filter patterns. A filter pattern can be a simple wildcard pattern, 
  where <code>?</code> matches one character and <code>*</code> matches zero or more characters, or a regex enclosed in <code>r/.../</code>.</p>
  <p>Examples:<br>
  <code>-f=*volvo_fh_2024*</code>: extract files or directories containing the string "volvo_fh_2024"<br>
  <code>-f=*volvo*,*scania*</code>: extract files or directories containing the string "volvo" or "scania"<br>
  <code>-f=/def/vehicle/truck/*/engine/*</code>: extract engine definitions for trucks</code><br>
  <code>-f=r/\.p(m[acdg]|pd)$/</code>: extract model files (.pmd, .pmg, ...)</code>
  </p>
  <p>When using regex, remember to insert escape characters where necessary.</p>
  </td>
</tr>
<tr>
  <td></td>
  <td><code>--list</code></td>
  <td>Lists paths contained in the archive. Can be combined with <code>--all</code>, <code>--deep</code>, <code>--filter</code>, and <code>--partial</code>.</td>
</tr>
<tr>
  <td></td>
  <td><code>--list-all</code></td>
  <td>Lists all paths referenced by files in the archive, even if they are not contained in it.
  (Implicitly activates <code>--deep</code>.) Can be combined with <code>--all</code>, <code>--filter</code>, and <code>--partial</code>.</td>
</tr>
<tr>
  <td><code>-p</code></td>
  <td><code>--partial</code></td>
  <td><p>Limits extraction to the comma-separated list of files and/or directories specified.</p>
  <p>Examples:<br>
  <code>-p=/locale</code><br>
  <code>-p=/def,/map</code><br>
  <code>-p=/def/world/road.sii</code></p>
  <p>When extracting a HashFS archive (without <code>--deep</code>), <b>directory traversal begins at the given paths</b>, allowing for
  extraction of known directories and files not discoverable from the top level. This makes <code>--partial</code> distinctly different
  from <code>--filter</code>. (In all other modes, extraction is limited to files whose paths begin with any of the strings given to 
  this parameter.)</p>
  </td>
</tr>
<tr>
  <td><code>-P</code></td>
  <td><code>--paths</code></td>
  <td>Same as <code>--partial</code>, but expects a text file containing paths to extract, separated by
  line breaks.</td>
</tr>
<tr>
  <td><code>-q</code></td>
  <td><code>--quiet</code></td>
  <td>Don't print paths of extracted files.</td>
</tr>
<tr>
  <td><code>-S</code></td>
  <td><code>--separate</code></td>
  <td>When extracting multiple archives, extract each archive to a separate directory.</td>
</tr>
<tr>
  <td><code>-s</code></td>
  <td><code>--skip-existing</code></td>
  <td>Don't overwrite existing files.</td>
</tr>
<tr>
  <td></td>
  <td><code>--tree</code></td>
  <td>Prints the archive's directory tree. Can be combined with <code>--all</code>, <code>--deep</code>, and <code>--partial</code>.</td>
</tr>
<tr>
  <td><code>-?</code>, <code>-h</code></td>
  <td><code>--help</code></td>
  <td>Prints the extractor's version and usage information.</td>
</tr>
</table>


### HashFS options
<table>
<thead>
  <tr>
    <td><b>Short</b></td>
    <td><b>Long&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</b></td>
    <td><b>Description</b></td>
  </tr>
</thead>
<tr>
  <td></td>
  <td><code>--additional</code></td>
  <td>When using <code>--deep</code>, specifies additional start paths to search.
  Expects a text file containing paths to extract, separated by line breaks.</td>
</tr>
<tr>
  <td><code>-D</code></td>
  <td><code>--deep</code></td>
  <td>An extraction mode which scans the contained entries for referenced paths instead of traversing
  the directory tree from <code>/</code>. Use this option to extract archives without a top level directory listing.</td>
</tr>
<tr>
  <td></td>
  <td><code>--list-entries</code></td>
  <td>Lists entries contained in the archive.</td>
</tr>
<tr>
  <td><code>-r</code></td>
  <td><code>--raw</code></td>
  <td>Dumps the contained files with their hashed filenames rather than traversing
  the archive's directory tree.</td>
</tr>
<tr>
  <td></td>
  <td><code>--salt</code></td>
  <td>Ignores the salt specified in the archive header and uses the given one instead.</td>
</tr>
<tr>
  <td></td>
  <td><code>--table-at-end</code></td>
  <td>[v1 only] Ignores what the archive header says and reads the entry table from
  the end of the file.</td>
</tr>
</table>


### Examples
Normal extraction:
```sh
extractor "path\to\file.scs"
```

Extract two .scs files at once:
```sh
extractor "path\to\file1.scs" "path\to\file2.scs"
```

Extract all .scs files in a directory:
```sh
extractor "path\to\directory" --all
```

Extract `def` and `manifest.sii` only:
```sh
extractor "path\to\file.scs" --partial=/def,/manifest.sii
```

Extract model files only:
```sh
extractor "path\to\file.scs" --filter=r/\.p(m[acdg]|pd)$/
```

Extract with deep mode:
```sh
extractor "path\to\file.scs" --deep
```

Extract with deep mode when the mod is split into multiple archives:
```sh
extractor "file1.scs" "file2.scs" "file3.scs" --deep --separate
```

Alternatively:
```sh
extractor "path\to\mod\directory" --all --deep --separate
```
