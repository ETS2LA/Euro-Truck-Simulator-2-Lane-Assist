// CityHash64 in C#
// Copyright (c) 2018, Dario Wouters
//
// - cityhash-c copyright notice -
// city.c - cityhash-c
// CityHash on C
// Copyright (c) 2011-2012, Alexander Nusov
//
// - original copyright notice -
// Copyright (c) 2011 Google, Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
// CityHash, by Geoff Pike and Jyrki Alakuijala
//
// This file provides CityHash64() and related functions.
//
// It's probably possible to create even faster hash functions by
// writing a program that systematically explores some of the space of
// possible hash functions, by using SIMD instructions, or by
// compromising on hash quality.

using System.Text;
using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor.FileSystem
{
    public static class CityHash
    {
        private class Uint128
        {
            public Uint128(ulong first, ulong second)
            {
                First = first;
                Second = second;
            }
            public ulong First { get; }
            public ulong Second { get; }
            public override string ToString()
            {
                return $"({First}, {Second})";
            }
        }

        // Some primes between 2^63 and 2^64 for various uses.
        private const ulong K0 = 0xc3a5c85c97cb3127UL;
        private const ulong K1 = 0xb492b66fbe98f273UL;
        private const ulong K2 = 0x9ae16a3b2f90404fUL;
        private const ulong K3 = 0xc949d7c7509e6557UL;

        // Bitwise right rotate.
        private static ulong Rotate(ulong val, int shift)
        {
            return shift == 0 ? val : ((val >> shift) | (val << (64 - shift)));
        }

        private static ulong RotateByAtleast1(ulong val, int shift)
        {
            return (val >> shift) | (val << (64 - shift));
        }

        private static void Swap<T>(ref T lhs, ref T rhs)
        {
            var temp = lhs;
            lhs = rhs;
            rhs = temp;
        }

        private static ulong ShiftMix(ulong val)
        {
            return val ^ (val >> 47);
        }

        private static ulong Fetch32(byte[] data, ulong pos = 0)
        {
            return MemoryHelper.ReadUInt32(data, (int)pos);
        }

        private static ulong Fetch64(byte[] data, ulong pos = 0)
        {
            return MemoryHelper.ReadUInt64(data, (int)pos);
        }

        // Hash 128 input bits down to 64 bits of output.
        // This is intended to be a reasonably good hash function.
        private static ulong Hash128To64(Uint128 x)
        {
            // Murmur-inspired hashing.
            const ulong kMul = 0x9ddfea08eb382d69UL;
            var a = (x.First ^ x.Second) * kMul;
            a ^= a >> 47;
            var b = (x.Second ^ a) * kMul;
            b ^= b >> 47;
            b *= kMul;
            return b;
        }

        private static ulong HashLen16(ulong u, ulong v)
        {
            return Hash128To64(new Uint128(u, v));
        }

        private static ulong HashLen0To16(byte[] s, ulong len)
        {
            if (len > 8)
            {
                var a = Fetch64(s);
                var b = Fetch64(s, len - 8);
                return HashLen16(a, RotateByAtleast1(b + len, (int) len)) ^ b;
            }

            if (len >= 4)
            {
                var a = Fetch32(s);
                return HashLen16(len + (a << 3), Fetch32(s, len - 4));
            }

            if (len > 0)
            {
                var a = s[0];
                var b = s[len >> 1];
                var c = s[len - 1];
                var y = a + ((uint) b << 8);
                var z = len + ((uint) c << 2);
                return ShiftMix(y * K2 ^ z * K3) * K2;
            }

            return K2;
        }

        // This probably works well for 16-byte strings as well, but it may be overkill
        // in that case.
        private static ulong HashLen17To32(byte[] s, ulong len)
        {
            var a = Fetch64(s) * K1;
            var b = Fetch64(s, 8);
            var c = Fetch64(s, len - 8) * K2;
            var d = Fetch64(s, len - 16) * K0;
            return HashLen16(Rotate(a - b, 43) + Rotate(c, 30) + d,
                             a + Rotate(b ^ K3, 20) - c + len);
        }

        // Return a 16-byte hash for 48 bytes.  Quick and dirty.
        // Callers do best to use "random-looking" values for a and b.
        private static ulong HashLen33To64(byte[] s, ulong len)
        {
            var z = Fetch64(s, 24);
            var a = Fetch64(s) + (len + Fetch64(s, len - 16)) * K0;
            var b = Rotate(a + z, 52);
            var c = Rotate(a, 37);
            a += Fetch64(s, 8);
            c += Rotate(a, 7);
            a += Fetch64(s, 16);
            var vf = a + z;
            var vs = b + Rotate(a, 31) + c;
            a = Fetch64(s, 16) + Fetch64(s, len - 32);
            z = Fetch64(s, len - 8);
            b = Rotate(a + z, 52);
            c = Rotate(a, 37);
            a += Fetch64(s, len - 24);
            c += Rotate(a, 7);
            a += Fetch64(s, len - 16);
            var wf = a + z;
            var ws = b + Rotate(a, 31) + c;
            var r = ShiftMix((vf + ws) * K2 + (wf + vs) * K0);
            return ShiftMix(r * K0 + vs) * K2;
        }

        // Return a 16-byte hash for 48 bytes.  Quick and dirty.
        // Callers do best to use "random-looking" values for a and b.
        private static Uint128 WeakHashLen32WithSeeds(ulong w, ulong x, ulong y, ulong z, ulong a, ulong b)
        {
            a += w;
            b = Rotate(b + a + z, 21);
            var c = a;
            a += x;
            a += y;
            b += Rotate(a, 44);

            return new Uint128(a + z, b + c);
        }

        // Return a 16-byte hash for s[0] ... s[31], a, and b.  Quick and dirty.
        private static Uint128 WeakHashLen32WithSeeds(byte[] s, ulong len, ulong a, ulong b)
        {
            return WeakHashLen32WithSeeds(Fetch64(s, len),
                                          Fetch64(s, len + 8),
                                          Fetch64(s, len + 16),
                                          Fetch64(s, len + 24),
                                          a,
                                          b);
        }

        public static ulong CityHash64(string s)
        {
            return CityHash64(Encoding.UTF8.GetBytes(s), (ulong)s.Length);
        }

        public static ulong CityHash64(byte[] s, ulong len)
        {
            if (len <= 16) return HashLen0To16(s, len);
            if (len <= 32) return HashLen17To32(s, len);
            if (len <= 64) return HashLen33To64(s, len);

            // For strings over 64 bytes we hash the end first, and then as we
            // loop we keep 56 bytes of state: v, w, x, y, and z.

            var x = Fetch64(s, len - 40);
            var y = Fetch64(s, len - 16) + Fetch64(s, len - 56);
            var z = HashLen16(Fetch64(s, len - 48) + len, Fetch64(s, len - 24));
            var v = WeakHashLen32WithSeeds(s, len - 64, len, z);
            var w = WeakHashLen32WithSeeds(s, len - 32, y + K1, x);
            x = x * K1 + Fetch64(s);

            var pos = 0UL;
            // Decrease len to the nearest multiple of 64, and operate on 64-byte chunks.
            len = (len - 1) & ~(ulong)63;
            do
            {
                x = Rotate(x + y + v.First + Fetch64(s, pos + 8), 37) * K1;
                y = Rotate(y + v.Second + Fetch64(s, pos + 48), 42) * K1;
                x ^= w.Second;
                y += v.First + Fetch64(s, pos + 40);
                z = Rotate(z + w.First, 33) * K1;
                v = WeakHashLen32WithSeeds(s, pos, v.Second * K1, x + w.First);
                w = WeakHashLen32WithSeeds(s, pos + 32, z + w.Second, y + Fetch64(s, pos + 16));
                Swap(ref z, ref x);

                pos += 64;
                len -= 64;

            } while (len != 0);

            return HashLen16(HashLen16(v.First, w.First) + ShiftMix(y) * K1 + z,
                             HashLen16(v.Second, w.Second) + x);

        }
    }
}