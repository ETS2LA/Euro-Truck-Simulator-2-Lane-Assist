using Hexa.NET.ImGui;
using Avalonia.Data;

namespace ETS2LA.Overlay
{
    public struct WindowDefinition
    {
        public string Title;
        public Optional<ImGuiWindowFlags> Flags;
        public Optional<int> Width;
        public Optional<int> Height;
        public Optional<int> X;
        public Optional<int> Y;
        public Optional<float> Alpha;
        /// <summary>
        ///  This might be useful if you want a reliable callback to when
        ///  the overlay is rendered. Setting this variable to true will mean
        ///  the OverlayHandler will call the render outside of the ImGui system.
        ///  WARNING: If you want a window, you have to create it yourself!
        /// </summary>
        public Optional<bool> NoWindow;
    }
}