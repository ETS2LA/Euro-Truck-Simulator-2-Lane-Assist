using System.Text;

namespace ETS2LA.Shared
{
    public class MemoryReader
    {
        private byte[] memory;
    
        public MemoryReader(byte[] memory)
        {
            this.memory = memory;
        }
    
        public void SetBool(int offset, bool value)
        {
            memory[offset] = (byte)(value ? 1 : 0);
        }
    
        public bool ReadBool(int offset)
        {
            bool value = memory[offset] != 0;
            return value;
        }

        public bool[] ReadBool(int offset, int count)
        {
            bool[] bools = new bool[count];
            for (int i = 0; i < count; i++)
            {
                bools[i] = memory[offset + i] != 0;
            }
            return bools;
        }

        public int ReadInt(int offset)
        {
            int value = BitConverter.ToInt32(memory, offset);
            return value;
        }

        public int[] ReadInt(int offset, int count)
        {
            int[] ints = new int[count];
            for (int i = 0; i < count; i++)
            {
                ints[i] = BitConverter.ToInt32(memory, offset + i * 4);
            }
            return ints;
        }

        public Int16 ReadInt16(int offset)
        {
            Int16 value = BitConverter.ToInt16(memory, offset);
            return value;
        }

        public float ReadFloat(int offset)
        {
            float value = BitConverter.ToSingle(memory, offset);
            return value;
        }

        public float[] ReadFloat(int offset, int count)
        {
            float[] floats = new float[count];
            for (int i = 0; i < count; i++)
            {
                floats[i] = BitConverter.ToSingle(memory, offset + i * 4);
            }
            return floats;
        }

        public long ReadLong(int offset)
        {
            long value = BitConverter.ToInt64(memory, offset);
            return value;
        }

        public long[] ReadLong(int offset, int count)
        {
            long[] longs = new long[count];
            for (int i = 0; i < count; i++)
            {
                longs[i] = BitConverter.ToInt64(memory, offset + i * 8);
            }
            return longs;
        }

        public ulong ReadLongLong(int offset)
        {
            ulong value = BitConverter.ToUInt64(memory, offset);
            return value;
        }

        public ulong[] ReadLongLong(int offset, int count)
        {
            ulong[] longlongs = new ulong[count];
            for (int i = 0; i < count; i++)
            {
                longlongs[i] = BitConverter.ToUInt64(memory, offset + i * 8);
            }
            return longlongs;
        }

        public string ReadChar(int offset, int count)
        {
            StringBuilder charBuilder = new StringBuilder();
            for (int i = 0; i < count; i++)
            {
                char c = (char)memory[offset + i];
                if (c != '\0') // Skip null characters
                {
                    charBuilder.Append(c);
                }
            }
            return charBuilder.ToString();
        }

        public double ReadDouble(int offset)
        {
            double value = BitConverter.ToDouble(memory, offset);
            return value;
        }

        public double[] ReadDouble(int offset, int count)
        {
            double[] doubles = new double[count];
            for (int i = 0; i < count; i++)
            {
                doubles[i] = BitConverter.ToDouble(memory, offset + i * 8);
            }
            return doubles;
        }

        public string[] ReadStringArray(int offset, int count, int stringSize)
        {
            string[] strings = new string[count];
            for (int i = 0; i < count; i++)
            {
                strings[i] = ReadChar(offset + i * stringSize, stringSize);
            }
            return strings;
        }
    }
}