namespace ETS2LA.Game.Extractor.Map.Overlays
{
    public enum OverlayType
    {
        /// <summary>
        /// Overlays which are not in a specific directory
        /// </summary>
        Custom = -1,

        /// <summary>
        /// Overlays located in 'material/ui/map/road'
        /// </summary>
        Road,

        /// <summary>
        /// Overlays located in 'material/ui/company/small'
        /// </summary>
        Company,

        /// <summary>
        /// Overlays located in 'material/ui/map'
        /// </summary>
        Map,

        /// <summary>
        /// Bus Stop overlay located in 'tsmap/overlay'
        /// </summary>
        BusStop
    }
}