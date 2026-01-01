using System;

namespace ETS2LA.Game.Extractor.Map.Overlays
{
    internal struct Color8888
    {
        internal byte A { get; private set; }
        internal byte R { get; }
        internal byte G { get; }
        internal byte B { get; }

        internal Color8888(byte a, byte r, byte g, byte b)
        {
            A = a;
            R = r;
            G = g;
            B = b;
        }

        internal Color8888(Color565 color565, byte a)
        {
            A = a;
            R = (byte) (color565.R << 3);
            G = (byte) (color565.G << 2);
            B = (byte) (color565.B << 3);
        }

        internal void SetAlpha(byte a)
        {
            A = a;
        }
    }

    internal struct Color565
    {
        internal byte R { get; }
        internal byte G { get; }
        internal byte B { get; }

        private Color565(byte r, byte g, byte b)
        {
            R = r;
            G = g;
            B = b;
        }

        internal Color565(ushort color) : this((byte) ((color >> 11) & 0x1F), (byte) ((color >> 5) & 0x3F),
            (byte) (color & 0x1F))
        {
        }

        public static Color565 operator +(Color565 col1, Color565 col2)
        {
            return new Color565((byte) (col1.R + col2.R), (byte) (col1.G + col2.G), (byte) (col1.B + col2.B));
        }

        public static Color565 operator *(Color565 col1, double val)
        {
            return new Color565((byte) (col1.R * val), (byte) (col1.G * val), (byte) (col1.B * val));
        }

        public static Color565 operator *(double val, Color565 col1)
        {
            return col1 * val;
        }
    }

    internal struct ColorLinear
    {
        internal double LinearR { get; }
        internal double LinearG { get; }
        internal double LinearB { get; }
        internal double LinearA { get; }

        internal double SrgbR => Linear2Srgb(LinearR) * 255;
        internal double SrgbG => Linear2Srgb(LinearG) * 255;
        internal double SrgbB => Linear2Srgb(LinearB) * 255;
        internal double SrgbA => Linear2Srgb(LinearA) * 255;

        private static double Linear2Srgb(double x)
        {
            if (x <= 0.0031308)
                return 12.92 * x;

            return Math.Pow(x, 1.0 / 2.4) * 1.055 - 0.055;
        }

        internal ColorLinear(double linearR, double linearG, double linearB, double linearA)
        {
            LinearR = linearR;
            LinearG = linearG;
            LinearB = linearB;
            LinearA = linearA;
        }
    }
}