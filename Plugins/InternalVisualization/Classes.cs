using ETS2LA.Game.Data;
using ETS2LA.Telemetry;
using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;
using TruckLib;

namespace InternalVisualization;

public class Renderer
{
    public virtual void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                               GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        // Implement your rendering logic here using the provided data.
        // This is where you would use ImGui to visualize the data.
    }
}

public static class InternalVisualizationConstants
{
    public static float Scale = 1.25f;
}