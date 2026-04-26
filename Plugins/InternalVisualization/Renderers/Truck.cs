using ETS2LA.Game.Data;
using ETS2LA.Shared;
using ETS2LA.Telemetry;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;

namespace InternalVisualization.Renderers;

public class TruckRenderer : Renderer
{
    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        Vector3Double center = telemetryData.truckPlacement.coordinate;
        Vector2 screenPos = Utils.WorldToScreen(center.ToVector3(), center.ToVector3(), windowSize) + windowPos;

        Vector3Double rotation = telemetryData.truckPlacement.rotation;
        float angle = (float)rotation.X * 360f;
        if (angle < 0) angle += 360f;
        angle = 360f - angle + 90;

        // Create a 3x8 rectangle representing the truck, centered on the screen position.
        float width = 8 * InternalVisualizationConstants.Scale;
        float length = 3 * InternalVisualizationConstants.Scale;
        Vector2[] truckCorners = new Vector2[]
        {
            new Vector2(-width / 2, -length / 2),
            new Vector2(width / 2, -length / 2),
            new Vector2(width / 2, length / 2),
            new Vector2(-width / 2, length / 2)
        };

        // Rotate the truck corners around the center point.
        for (int i = 0; i < truckCorners.Length; i++)
        {
            truckCorners[i] = Vector2.Transform(
                truckCorners[i], Matrix4x4.CreateRotationZ(Utils.ToRadians(angle))
            ) + screenPos;
        }

        for (int i = 0; i < truckCorners.Length; i++)
        {
            Vector2 start = truckCorners[i];
            Vector2 end = truckCorners[(i + 1) % truckCorners.Length];
            drawList.AddLine(start, end, ImGui.GetColorU32(new Vector4(0, 1, 0.2f, 1)), 2 * InternalVisualizationConstants.Scale);
        }
    }
}