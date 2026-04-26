using ETS2LA.Game.Data;
using ETS2LA.Logging;
using ETS2LA.Game.SDK;
using ETS2LA.Telemetry;
using ETS2LA.Backend.Events;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;
using TruckLib;
namespace InternalVisualization.Renderers;

public class TrafficRenderer : Renderer
{
    private TrafficData? _trafficData;
    public TrafficRenderer()
    {
        Events.Current.Subscribe<TrafficData>(TrafficProvider.Current.EventString, OnTrafficDataReceived);
    }

    private void OnTrafficDataReceived(TrafficData data)
    {
        _trafficData = data;
    }

    private void DrawRectangle(ImDrawListPtr drawList, Vector2 screenPos, float width, float length, float angle)
    {
        width *= InternalVisualizationConstants.Scale;
        length *= InternalVisualizationConstants.Scale;

        Vector2[] corners = new Vector2[]
        {
            new Vector2(-length / 2, -width / 2),
            new Vector2(length / 2, -width / 2),
            new Vector2(length / 2, width / 2),
            new Vector2(-length / 2, width / 2)
        };

        // Rotate the truck corners around the center point.
        for (int i = 0; i < corners.Length; i++)
        {
            corners[i] = Vector2.Transform(
                corners[i], Matrix4x4.CreateRotationZ(Utils.ToRadians(angle))
                
            ) + screenPos;
        }

        for (int i = 0; i < corners.Length; i++)
        {
            Vector2 start = corners[i];
            Vector2 end = corners[(i + 1) % corners.Length];
            drawList.AddLine(start, end, ImGui.GetColorU32(new Vector4(0.6f, 0.6f, 0.6f, 1)), 2 * InternalVisualizationConstants.Scale);
        }
    }

    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        foreach (var vehicle in _trafficData?.vehicles ?? Array.Empty<TrafficVehicle>())
        {
            Vector3 center = vehicle.position;
            Vector2 screenPos = Utils.WorldToScreen(center, telemetryData.truckPlacement.coordinate.ToVector3(), windowSize) + windowPos;

            Quaternion rotation = vehicle.rotation;
            float angle = rotation.ToEulerDeg().Y + 90f;

            float width = vehicle.size.X;
            float length = vehicle.size.Z;

            DrawRectangle(drawList, screenPos, width, length, angle);
            if (ImGui.IsMouseHoveringRect(screenPos - new Vector2(length, width) * InternalVisualizationConstants.Scale, screenPos + new Vector2(length, width) * InternalVisualizationConstants.Scale))
            {
                ImGui.BeginTooltip();
                ImGui.Spacing();
                ImGui.Text($"Traffic Vehicle:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.8f, 1f, 1f, 1f), $"{vehicle.id}");
                ImGui.Indent();
                ImGui.Text($"Speed:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 1f, 1f), $"{vehicle.speed * 3.6f:F1} km/h");
                ImGui.Text($"Acceleration:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 1f, 1f), $"{vehicle.acceleration} m/s²");
                ImGui.Text($"Position:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{center.X:F1}, {center.Y:F1}, {center.Z:F1}");
                ImGui.Text($"Rotation:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{angle:F1}°");
                ImGui.Unindent();
                ImGui.Spacing();
                ImGui.EndTooltip();
            }

            for (int i = 0; i < vehicle.trailers.Length; i++)
            {
                var trailer = vehicle.trailers[i];

                Vector3 trailerCenter = trailer.position;
                Vector2 trailerScreenPos = Utils.WorldToScreen(trailerCenter, telemetryData.truckPlacement.coordinate.ToVector3(), windowSize) + windowPos;

                Quaternion trailerRotation = trailer.rotation;
                float trailerAngle = trailerRotation.ToEulerDeg().Y + 90f;

                float trailerWidth = trailer.size.X;
                float trailerLength = trailer.size.Z;

                DrawRectangle(drawList, trailerScreenPos, trailerWidth, trailerLength, trailerAngle);

                if (ImGui.IsMouseHoveringRect(trailerScreenPos - new Vector2(trailerLength, trailerWidth) * InternalVisualizationConstants.Scale, trailerScreenPos + new Vector2(trailerLength, trailerWidth) * InternalVisualizationConstants.Scale))
                {
                    ImGui.BeginTooltip();
                    ImGui.Spacing();
                    ImGui.Text($"Trailer");
                    ImGui.SameLine();
                    ImGui.TextColored(new Vector4(0.8f, 1f, 1f, 1f), $"{i}");
                    ImGui.SameLine();
                    ImGui.Text("for vehicle:");
                    ImGui.SameLine();
                    ImGui.TextColored(new Vector4(0.8f, 1f, 1f, 1f), $"{vehicle.id}");
                    ImGui.Indent();
                    ImGui.Text($"Position:");
                    ImGui.SameLine();
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{trailerCenter.X:F1}, {trailerCenter.Y:F1}, {trailerCenter.Z:F1}");
                    ImGui.Text($"Rotation:");
                    ImGui.SameLine();
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{trailerAngle:F1}°");
                    ImGui.Unindent();
                    ImGui.Spacing();
                    ImGui.EndTooltip();
                }
            }
        }
    }
}