using System.Collections.Generic;

namespace ETS2LA.Game.Extractor.Common
{
    internal static class Consts
    {
        /// <summary>
        /// List of DLC guards that are in the game, DLC guards can be found in the map editor.
        /// <!--DLC guards seem to be hardcoded in the exe of the game, so no real easy way to make this dynamic-->
        /// </summary>
        public static readonly List<DlcGuard> DefaultAtsDlcGuards = new List<DlcGuard>()
        {
            new DlcGuard("No Guard", 0),
            new DlcGuard("dlc_nevada", 1),
            new DlcGuard("dlc_arizona", 2),
            new DlcGuard("dlc_nm", 3),
            new DlcGuard("dlc_or", 4),
            new DlcGuard("dlc_wa", 5),
            new DlcGuard("dlc_wa_and_or", 6),
            new DlcGuard("dlc_ut", 7),
            new DlcGuard("dlc_ut_and_nm", 8),
            new DlcGuard("dlc_id", 9),
            new DlcGuard("dlc_id_and_or", 10),
            new DlcGuard("dlc_id_and_ut", 11),
            new DlcGuard("dlc_id_and_wa", 12),
            new DlcGuard("dlc_co", 13),
            new DlcGuard("dlc_co_and_nm", 14),
            new DlcGuard("dlc_co_and_ut", 15),
            new DlcGuard("dlc_wy", 16),
            new DlcGuard("dlc_wy_and_co", 17),
            new DlcGuard("dlc_wy_and_id", 18),
            new DlcGuard("dlc_wy_and_ut", 19),
            new DlcGuard("dlc_tx", 20),
            new DlcGuard("dlc_tx_and_nm", 21),
            new DlcGuard("dlc_mt", 22),
            new DlcGuard("dlc_mt_and_id", 23),
            new DlcGuard("dlc_mt_and_wy", 24),
            new DlcGuard("dlc_ok", 25),
            new DlcGuard("dlc_ok_and_co", 26),
            new DlcGuard("dlc_ok_and_nm", 27),
            new DlcGuard("dlc_ok_and_tx", 28),
            new DlcGuard("dlc_ks", 29),
            new DlcGuard("dlc_ks_and_co", 30),
            new DlcGuard("dlc_ks_and_ok", 31),
            new DlcGuard("dlc_ne", 32),
            new DlcGuard("dlc_ne_and_co", 33),
            new DlcGuard("dlc_ne_and_ks", 34),
            new DlcGuard("dlc_ne_and_wy", 35),
            new DlcGuard("dlc_ar", 36),
            new DlcGuard("dlc_ar_and_ok", 37),
            new DlcGuard("dlc_ar_and_tx", 38),
            new DlcGuard("dlc_mo", 39),
            new DlcGuard("dlc_mo_and_ar", 40),
            new DlcGuard("dlc_mo_and_ks", 41),
            new DlcGuard("dlc_mo_and_ne", 42),
            new DlcGuard("dlc_mo_and_ok", 43),
            new DlcGuard("dlc_ia", 44),
            new DlcGuard("dlc_ia_and_mo", 45),
            new DlcGuard("dlc_ia_and_ne", 46),
            new DlcGuard("dlc_la", 47),
            new DlcGuard("dlc_la_and_ar", 48),
            new DlcGuard("dlc_la_and_tx", 49),

        };

        /// <summary>
        /// List of DLC guards that are in the game, DLC guards can be found in the map editor.
        /// <!--DLC guards seem to be hardcoded in the exe of the game, so no real easy way to make this dynamic-->
        /// </summary>
        public static readonly List<DlcGuard> DefaultEts2DlcGuards = new List<DlcGuard>()
        {
            new DlcGuard("No Guard", 0),
            new DlcGuard("dlc_east", 1),
            new DlcGuard("dlc_north", 2),
            new DlcGuard("dlc_fr", 3),
            new DlcGuard("dlc_it", 4),
            new DlcGuard("dlc_fr_and_it", 5),
            new DlcGuard("dlc_balt", 6),
            new DlcGuard("dlc_balt_and_east", 7),
            new DlcGuard("dlc_balt_and_north", 8),
            new DlcGuard("dlc_blke", 9),
            new DlcGuard("dlc_blke_and_east", 10),
            new DlcGuard("dlc_iberia", 11),
            new DlcGuard("dlc_iberia_and_fr", 12),
            new DlcGuard("dlc_russia", 13, false),
            new DlcGuard("dlc_balt_and_russia", 14, false),
            new DlcGuard("dlc_krone", 15),
            new DlcGuard("dlc_blkw", 16),
            new DlcGuard("dlc_blkw_and_east", 17),
            new DlcGuard("dlc_blkw_and_blke", 18),
            new DlcGuard("dlc_feldbinder", 19),
            new DlcGuard("dlc_greece", 20),
            new DlcGuard("dlc_greece_and_blke", 21),
            new DlcGuard("dlc_greece_and_blkw", 22),
            new DlcGuard("dlc_polar", 23),
            new DlcGuard("dlc_polar_and_balt", 24),
            new DlcGuard("dlc_polar_and_north", 25),

        };

        public const float LaneWidth = 4.5f;

        /// <summary>
        /// Magic mark that should be at the start of the file, 'SCS#' as utf-8 bytes
        /// </summary>
        internal const uint ScsMagic = 592659283;
    }
}