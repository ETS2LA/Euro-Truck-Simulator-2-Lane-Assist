using System.Text;
using ETS2LA.Game.Extractor.Common;
using ETS2LA.Game.Extractor.Helpers;
using ETS2LA.Logging;
using File = System.IO.File;

namespace ETS2LA.Game.Extractor.FileSystem.Hash
{
    internal enum HashEntryTypes
    {
        Img = 0x01,
        Sample = 0x02,
        MipProxy = 0x03,
        PmaInfo = 0x05,
        PmgInfo = 0x06,
        Plain = 0x80,
        Directory = 0x81,
        Mip0 = 0x82,
        Mip1 = 0x83,
        MipTail = 0x84
    }

    internal enum HashFsCompressionMethod
    {
        NoCompression = 0,
        Zlib = 1,
        Gdeflate = 3
    }

    public class HashArchiveFile : ArchiveFile
    {
        /// <summary>
        /// Hashing method used in scs files, 'CITY' as utf-8 bytes
        /// </summary>
        internal const uint HashMethod = 1498696003;
        private readonly ushort[] _supportedHashVersions = { 1, 2 };
        private const ushort EntryV1BlockSize = 0x20;
        private const ushort EntryV2BlockSize = 0x10;

        private HashArchiveHeader _hashHeader;

        /// <summary>
        /// Represents a hash archive file.
        /// Need to run <see cref="Parse"/> after to actually read the file contents
        /// </summary>
        /// <param name="path">Path to the hash file</param>
        public HashArchiveFile(string path) : base(path) { }

        /// <summary>
        /// Does minimal validation on the file and reads all the <see cref="Entry">Entries</see>
        /// </summary>
        /// <returns>Whether parsing was successful or not</returns>
        public override bool Parse()
        {
            if (!File.Exists(_path))
            {
                Logger.Error($"Could not find file {_path}");
                return false;
            }

            Br = new BinaryReader(File.OpenRead(_path));

            _hashHeader = new HashArchiveHeader
            {
                Magic = MemoryHelper.ReadUInt32(Br, 0x0),
                Version = MemoryHelper.ReadUInt16(Br, 0x04),
                Salt = MemoryHelper.ReadUInt16(Br, 0x06),
                HashMethod = MemoryHelper.ReadUInt32(Br, 0x08),
                EntryCount = MemoryHelper.ReadUInt32(Br, 0x0C),
                StartOffset = MemoryHelper.ReadUInt32(Br, 0x10)
            };

            if (_hashHeader.Magic != Consts.ScsMagic)
            {
                Logger.Error("Incorrect File Structure");
                return false;
            }

            if (_hashHeader.HashMethod != HashMethod)
            {
                Logger.Error("Incorrect Hash Method");
                return false;
            }

            if (!_supportedHashVersions.Contains(_hashHeader.Version))
            {
                Logger.Error("Unsupported Hash Version");
                return false;
            }
            
            if (_hashHeader.Version == 1)
            {

                Br.BaseStream.Seek(_hashHeader.StartOffset, SeekOrigin.Begin);
                var entriesRaw =
                    Br.ReadBytes((int) _hashHeader.EntryCount *
                                 EntryV1BlockSize); // read all entries at once for performance

                for (var i = 0; i < _hashHeader.EntryCount; i++)
                {
                    var offset = i * EntryV1BlockSize;
                    var entry = new HashEntryV1(this)
                    {
                        Hash = MemoryHelper.ReadUInt64(entriesRaw, offset),
                        Offset = MemoryHelper.ReadUInt64(entriesRaw, offset + 0x08),
                        Flags = MemoryHelper.ReadUInt32(entriesRaw, offset + 0x10),
                        Crc = MemoryHelper.ReadUInt32(entriesRaw, offset + 0x14),
                        Size = MemoryHelper.ReadUInt32(entriesRaw, offset + 0x18),
                        CompressedSize = MemoryHelper.ReadUInt32(entriesRaw, offset + 0x1C),
                    };

                    if (entry.IsDirectory())
                    {
                        UberDirectory dir = UberFileSystem.Instance.GetDirectory(entry.GetHash());
                        if (dir == null)
                        {
                            dir = new UberDirectory();
                            dir.AddNewEntry(entry);
                            UberFileSystem.Instance.Directories[entry.GetHash()] = dir;
                        }

                        var lines = Encoding.UTF8.GetString(entry.Read()).Split('\n');
                        foreach (var line in lines)
                        {
                            if (line == "") continue;

                            if (line.StartsWith("*")) // dir
                            {
                                dir.AddSubDirName(line.Substring(1));
                            }
                            else
                            {
                                dir.AddSubFileName(line);
                            }
                        }
                    }
                    else
                    {
                        if (UberFileSystem.Instance.Files.ContainsKey(entry.GetHash()))
                        {
                            UberFileSystem.Instance.Files[entry.GetHash()] =
                                new UberFile(entry); // overwrite if there already is a file with the current hash
                        }
                        else
                        {
                            UberFileSystem.Instance.Files.Add(entry.GetHash(), new UberFile(entry));
                        }
                    }
                }
            }
            else if (_hashHeader.Version == 2)
            {
                var entryTableBlockSize = MemoryHelper.ReadUInt32(Br, 0x10);
                var metadataCount = MemoryHelper.ReadUInt32(Br, 0x14);
                var metadataTableBlockSize = MemoryHelper.ReadUInt32(Br, 0x18);
                var entryTableBlockOffset = MemoryHelper.ReadInt64(Br, 0x1C);
                var metadataTableBlockOffset = MemoryHelper.ReadInt64(Br, 0x24);

                Br.BaseStream.Seek(entryTableBlockOffset, SeekOrigin.Begin);
                var entriesBlockRaw =
                    Br.ReadBytes((int)entryTableBlockSize);

                var rawEntries =
                    MemoryHelper.InflateZlib(entriesBlockRaw, entriesBlockRaw.Length,
                        (int)(_hashHeader.EntryCount * EntryV2BlockSize));

                Br.BaseStream.Seek(metadataTableBlockOffset, SeekOrigin.Begin);
                var metadataBlockRaw =
                    Br.ReadBytes((int)metadataTableBlockSize);

                var rawMetadataBytes =
                    MemoryHelper.InflateZlib(metadataBlockRaw, metadataBlockRaw.Length,
                        (int)(metadataCount * 0x04));

                for (var i = 0; i < _hashHeader.EntryCount; i++)
                {
                    var offset = i * EntryV2BlockSize;

                    var entry = new HashEntryV2(this)
                    {
                        Hash = MemoryHelper.ReadUInt64(rawEntries, offset),
                        Flags = MemoryHelper.ReadUInt32(rawEntries, offset + 0x0c)
                    };

                    var metadataStartIndex = MemoryHelper.ReadInt32(rawEntries, offset + 0x08);
                    var entryMetadataCount = MemoryHelper.ReadUInt16(rawEntries, offset + 0x0c);
                    for (var j = 0; j < entryMetadataCount; j++)
                    {
                        var metadata0 = MemoryHelper.ReadUInt32(rawMetadataBytes, (metadataStartIndex + j) * 4);
                        var entryType = (HashEntryTypes)(metadata0 >> 0x18);
                        var referencedMetadataOffset = (metadata0 & 0xFF_FF_FF) * 4;

                        switch (entryType)
                        {
                            case HashEntryTypes.Plain:
                            case HashEntryTypes.Directory:
                            case HashEntryTypes.Mip0:
                            case HashEntryTypes.Mip1:
                            case HashEntryTypes.MipTail:
                                entry._plainMetadata = new PlainMetadata(
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset),
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset + 0x04),
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset + 0x08),
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset + 0x0c));
                                break;
                            case HashEntryTypes.Img:
                                entry._imgMetadata = new ImgMetadata(
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset),
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset + 0x04));
                                break;
                            case HashEntryTypes.Sample:
                                entry._sampleMetadata = new SampleMetadata(
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset));
                                break;
                            case HashEntryTypes.PmaInfo:
                                entry._pmaInfoMetadata = new PmaInfoMetadata(
                                    MemoryHelper.ReadUInt32(rawMetadataBytes, referencedMetadataOffset),
                                    MemoryHelper.ReadSingle(rawMetadataBytes, referencedMetadataOffset + 0x04),
                                    MemoryHelper.ReadUInt64(rawMetadataBytes, referencedMetadataOffset + 0x08),
                                    MemoryHelper.ReadSingle(rawMetadataBytes, referencedMetadataOffset + 0x10),
                                    MemoryHelper.ReadSingle(rawMetadataBytes, referencedMetadataOffset + 0x14),
                                    MemoryHelper.ReadSingle(rawMetadataBytes, referencedMetadataOffset + 0x18),
                                    MemoryHelper.ReadSingle(rawMetadataBytes, referencedMetadataOffset + 0x1c));
                                break;
                            case HashEntryTypes.PmgInfo:
                                entry._pmgInfoMetadata = new PmgInfoMetadata(
                                    MemoryHelper.ReadUInt64(rawMetadataBytes, referencedMetadataOffset));
                                break;
                            default:
                                Logger.Error(
                                    $"Metadata type {metadata0 >> 0x18} 0x{metadata0 >> 0x18:X} for entry {entry.GetHash()} (0x{entry.GetHash():X}) not implemented.");
                                break;
                        }
                    }


                    if (entry.IsDirectory())
                    {
                        var dir = UberFileSystem.Instance.GetDirectory(entry.GetHash());
                        if (dir == null)
                        {
                            dir = new UberDirectory();
                            dir.AddNewEntry(entry);
                            UberFileSystem.Instance.Directories[entry.GetHash()] = dir;
                        }

                        var dirSubData = entry.Read();
                        if (dirSubData.Length < 4) continue;

                        var subItemCount = MemoryHelper.ReadUInt32(dirSubData, 0);
                        var strOffset = (int)(4 + subItemCount);
                        for (var j = 0; j < subItemCount; j++)
                        {
                            var length = dirSubData[4 + j];
                            try
                            {
                                var subItem = MemoryHelper.ReadString(dirSubData, strOffset, length);
                                if (subItem.StartsWith("/"))
                                    dir.AddSubDirName(subItem.Substring(1));
                                else
                                    dir.AddSubFileName(subItem);
                                strOffset += length;
                            }
                            catch (Exception ex)
                            {
                                Logger.Debug($"Could not read dir entry {entry.GetHash()} (0x{entry.GetHash():X}), {_path}: {ex.Message}");
                                break;
                            }
                        }
                    }
                    else
                    {
                        if (UberFileSystem.Instance.Files.ContainsKey(entry.GetHash()))
                        {
                            UberFileSystem.Instance.Files[entry.GetHash()] =
                                new UberFile(entry); // overwrite if there already is a file with the current hash
                        }
                        else
                        {
                            UberFileSystem.Instance.Files.Add(entry.GetHash(), new UberFile(entry));
                        }
                    }
                }
            }

            Logger.Info($"Mounted '{Path.GetFileName(_path)}' with {_hashHeader.EntryCount} entries");
            return true;
        }
    }
}