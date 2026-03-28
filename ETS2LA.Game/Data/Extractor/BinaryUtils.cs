using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Extractor
{
    public class BinaryUtils
    {
        /// <summary>
        /// Searches for the last occurrence of a byte sequence in a stream.
        /// </summary>
        /// <param name="reader">The <see cref="BinaryReader"/> to read from.</param>
        /// <param name="pattern">The byte sequence to search for.</param>
        /// <returns>The offset from the start of the last occurrence of the sequence in the stream,
        /// or -1 if the sequence was not found.</returns>
        public static long FindBytesBackwards(BinaryReader reader, byte[] pattern)
        {
            const int bufferSize = 8192;
            var buffer = new byte[bufferSize];

            long startPos = reader.BaseStream.Length < bufferSize 
                ? 0 
                : reader.BaseStream.Length - bufferSize;
            int seqIdx = pattern.Length - 1;
            long offset = -1;

            do
            {
                reader.BaseStream.Position = startPos;
                reader.Read(buffer, 0, buffer.Length);

                for (int i = buffer.Length - 1; i >= 0; i--)
                {
                    var current = buffer[i];
                    if (pattern[seqIdx] == current)
                    {
                        seqIdx--;
                        if (seqIdx < 0)
                        {
                            offset = startPos + i;
                            break;
                        }
                    }
                    else
                    {
                        seqIdx = pattern.Length - 1;
                    }
                }

                startPos = Math.Max(0, startPos - bufferSize);
            } while (startPos > 0 && offset < 0);
            return offset;
        }

        public static void CopyStream(Stream input, Stream output, long bytes)
        {
            var buffer = new byte[32768];
            int read;
            while (bytes > 0 && (read = input.Read(buffer, 0, Math.Min(buffer.Length, (int)bytes))) > 0)
            {
                output.Write(buffer, 0, read);
                bytes -= read;
            }
        }
    }
}
