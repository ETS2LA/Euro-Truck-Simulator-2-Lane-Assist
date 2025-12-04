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
    
        public int SetBool(int offset, bool value)
        {
            memory[offset] = (byte)(value ? 1 : 0);
            return offset + 1;
        }
    
        public (bool, int) ReadBool(int offset)
        {
            bool value = memory[offset] != 0;
            return (value, offset + 1);
        }
    
        public (bool[], int) ReadBool(int offset, int count)
        {
            bool[] bools = new bool[count];
            for (int i = 0; i < count; i++)
            {
                bools[i] = memory[offset + i] != 0;
            }
            return (bools, offset + count);
        }
    
        public (int, int) ReadInt(int offset)
        {
            int value = BitConverter.ToInt32(memory, offset);
            return (value, offset + 4);
        }
    
        public (int[], int) ReadInt(int offset, int count)
        {
            int[] ints = new int[count];
            for (int i = 0; i < count; i++)
            {
                ints[i] = BitConverter.ToInt32(memory, offset + i * 4);
            }
            return (ints, offset + count * 4);
        }
    
        public (float, int) ReadFloat(int offset)
        {
            float value = BitConverter.ToSingle(memory, offset);
            return (value, offset + 4);
        }
    
        public (float[], int) ReadFloat(int offset, int count)
        {
            float[] floats = new float[count];
            for (int i = 0; i < count; i++)
            {
                floats[i] = BitConverter.ToSingle(memory, offset + i * 4);
            }
            return (floats, offset + count * 4);
        }
    
        public (long, int) ReadLong(int offset)
        {
            long value = BitConverter.ToInt64(memory, offset);
            return (value, offset + 8);
        }
    
        public (long[], int) ReadLong(int offset, int count)
        {
            long[] longs = new long[count];
            for (int i = 0; i < count; i++)
            {
                longs[i] = BitConverter.ToInt64(memory, offset + i * 8);
            }
            return (longs, offset + count * 8);
        }
    
        public (ulong, int) ReadLongLong(int offset)
        {
            ulong value = BitConverter.ToUInt64(memory, offset);
            return (value, offset + 8);
        }
    
        public (ulong[], int) ReadLongLong(int offset, int count)
        {
            ulong[] longlongs = new ulong[count];
            for (int i = 0; i < count; i++)
            {
                longlongs[i] = BitConverter.ToUInt64(memory, offset + i * 8);
            }
            return (longlongs, offset + count * 8);
        }
    
        public (string, int) ReadChar(int offset, int count)
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
            return (charBuilder.ToString(), offset + count);
        }
    
        public (double, int) ReadDouble(int offset)
        {
            double value = BitConverter.ToDouble(memory, offset);
            return (value, offset + 8);
        }
    
        public (double[], int) ReadDouble(int offset, int count)
        {
            double[] doubles = new double[count];
            for (int i = 0; i < count; i++)
            {
                doubles[i] = BitConverter.ToDouble(memory, offset + i * 8);
            }
            return (doubles, offset + count * 8);
        }
    
        public (string[], int) ReadStringArray(int offset, int count, int stringSize)
        {
            string[] strings = new string[count];
            for (int i = 0; i < count; i++)
            {
                strings[i] = ReadChar(offset + i * stringSize, stringSize).Item1;
            }
            return (strings, offset + count * stringSize);
        }
    }
}