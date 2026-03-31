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
    }
}