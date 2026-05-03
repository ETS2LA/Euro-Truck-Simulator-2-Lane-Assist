using ETS2LA.Game.Data;
using ETS2LA.Shared;
using ETS2LA.Telemetry;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;

namespace InternalVisualization.Renderers;

public class StatisticsRenderer : Renderer
{
    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        Vector3Double center = telemetryData.truckPlacement.coordinate;
        float speed = telemetryData.truckFloat.speed;

        drawList.AddText(windowPos + new Vector2(10, 30), ImGui.GetColorU32(new Vector4(1, 1, 1, 1)), $"Speed: {speed * 3.6f:F1} km/h");
        drawList.AddText(windowPos + new Vector2(10, 50), ImGui.GetColorU32(new Vector4(1, 1, 1, 1)), $"Position: {center.X:F1}, {center.Y:F1}, {center.Z:F1}");
    }
}