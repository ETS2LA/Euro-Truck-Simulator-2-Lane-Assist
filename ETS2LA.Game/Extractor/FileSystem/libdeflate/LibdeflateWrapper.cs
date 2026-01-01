using System;
using System.Runtime.InteropServices;

namespace ETS2LA.Game.Extractor.FileSystem.libdeflate
{
    using libdeflate_decompressor = IntPtr;
    using libdeflate_gdeflate_decompressor = IntPtr;

    internal enum libdeflate_result
    {
        /* Decompression was successful.  */
        LIBDEFLATE_SUCCESS = 0,

        /* Decompressed failed because the compressed data was invalid, corrupt,
         * or otherwise unsupported.  */
        LIBDEFLATE_BAD_DATA = 1,

        /* A NULL 'actual_out_nbytes_ret' was provided, but the data would have
         * decompressed to fewer than 'out_nbytes_avail' bytes.  */
        LIBDEFLATE_SHORT_OUTPUT = 2,

        /* The data would have decompressed to more than 'out_nbytes_avail'
         * bytes.  */
        LIBDEFLATE_INSUFFICIENT_SPACE = 3
    }

    internal static class LibdeflateWrapper
    {
        [DllImport("libdeflate")]
        public static extern libdeflate_decompressor libdeflate_alloc_decompressor();

        [DllImport("libdeflate")]
        public static extern libdeflate_result libdeflate_zlib_decompress(libdeflate_decompressor decompressor,
            byte[] input,
            UIntPtr in_nbytes, byte[] output, UIntPtr out_nbytes_avail, out UIntPtr actual_out_nbytes_ret);

        [DllImport("libdeflate")]
        public static extern void libdeflate_free_decompressor(libdeflate_decompressor decompressor);

        [DllImport("libdeflate")]
        public static extern libdeflate_gdeflate_decompressor libdeflate_alloc_gdeflate_decompressor();

        [DllImport("libdeflate")]
        public static extern libdeflate_result libdeflate_gdeflate_decompress(libdeflate_gdeflate_decompressor decomp,
            ref libdeflate_gdeflate_in_page input_pages,
            uint in_npages,
            byte[] output,
            uint out_nbytes_avail,
            UIntPtr actual_out_nbytes_ret);

        [DllImport("libdeflate")]
        public static extern void libdeflate_free_gdeflate_decompressor(libdeflate_gdeflate_decompressor decompressor);
    }
}