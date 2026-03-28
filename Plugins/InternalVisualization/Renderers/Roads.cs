using ETS2LA.Game;
using ETS2LA.Shared;
using ETS2LA.Telemetry;
using ETS2LA.Logging;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;
using TruckLib;
using ETS2LA.Game.Utils;

namespace InternalVisualization.Renderers;

public class RoadsRenderer : Renderer
{
    private List<string> invalidRoadTypes = new List<string>();
    private Dictionary<string, (float[] Left, float[] Right)> roadLaneCache = new Dictionary<string, (float[] Left, float[] Right)>();
    
    private string LanesToString(float[] lanes)
    {
        if (lanes.Length == 0) return "[0]";
        return "[" + string.Join(", ", lanes) + "]";
    }

    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        Vector3Double center = telemetryData.truckPlacement.coordinate;
        Dictionary<ulong, Road> nearbyRoads = new Dictionary<ulong, Road>();

        foreach (var node in nearbyNodes)
        {
            if(node.BackwardItem is Road)
            {
                Road road = (Road)node.BackwardItem;
                if (!nearbyRoads.ContainsKey(road.Uid))
                {
                    nearbyRoads.Add(road.Uid, road);
                }
            }

            if(node.ForwardItem is Road)
            {
                Road road = (Road)node.ForwardItem;
                if (!nearbyRoads.ContainsKey(road.Uid))
                {
                    nearbyRoads.Add(road.Uid, road);
                }
            }
        }

        foreach (var road in nearbyRoads.Values)
        {
            if (invalidRoadTypes.Contains(road.RoadType.ToString())) continue;
            if (road.RoadType.ToString() == "") continue;
            //if (!road.ShowInUiMap) continue;

            float resolution = 5f;
            float length = road.Length;

            float[] steps = new float[(int)(length / resolution) + 1];
            for (int i = 0; i < steps.Length; i++)
            {
                steps[i] = i * resolution;
            }

            List<OrientedPoint> roadPoints = new List<OrientedPoint>();
            for (int i = 0; i < steps.Length; i++)
            {
                bool isLast = false;
                if (i == steps.Length - 1) isLast = true;

                OrientedPoint? point = isLast ? road.InterpolateCurve(1) : road.InterpolateCurveDist(steps[i]);
                if (point == null) continue;
                
                roadPoints.Add(point.Value);
            }

            float[] left, right;
            if (roadLaneCache.ContainsKey(road.RoadType.ToString()))
            {
                (left, right) = roadLaneCache[road.RoadType.ToString()];
            }
            else
            {
                (left, right) = RoadUtils.CalculateRoadLaneCenters(road);
                roadLaneCache.Add(road.RoadType.ToString(), (left, right));
            }

            // We have to take into account the previous road when doing these calculations.
            // e.g. https://discord.com/channels/1120719484982939790/1120721175337775124/1474091490648133826
            IMapItem previous = road.BackwardItem;
            float[] prevLeft, prevRight;
            if (previous is Road prevRoad)
            {
                if (roadLaneCache.ContainsKey(prevRoad.RoadType.ToString()))
                {
                    (prevLeft, prevRight) = roadLaneCache[prevRoad.RoadType.ToString()];
                }
                else
                {
                    (prevLeft, prevRight) = RoadUtils.CalculateRoadLaneCenters(prevRoad);
                    roadLaneCache.Add(prevRoad.RoadType.ToString(), (prevLeft, prevRight));
                }
            }
            else
            {
                prevLeft = [];
                prevRight = [];
            }

            if (left.Length == 0 && right.Length == 0)
            {
                if (!invalidRoadTypes.Contains(road.RoadType.ToString()))
                {
                    invalidRoadTypes.Add(road.RoadType.ToString());
                    Logger.Warn($"Road type {road.RoadType} has no lane data. It will not be rendered.");
                }
                continue;
            }

            Vector2 minScreenPos = new Vector2(float.MaxValue, float.MaxValue);
            Vector2 maxScreenPos = new Vector2(float.MinValue, float.MinValue);
            for (int laneIndex = 0; laneIndex < left.Length; laneIndex++)
            {
                var laneOffset = left[laneIndex];
                var prevLaneOffset = prevLeft.Length > 0 ? prevLeft[laneIndex] : laneOffset;

                List<Vector3> lanePoints = new List<Vector3>();
                for (int i = 0; i < roadPoints.Count; i++)
                {
                    var pointOffset = RoadUtils.Lerp(prevLaneOffset, laneOffset, i / (float)(roadPoints.Count - 1));
                    Vector3 normal = Vector3.Normalize(Vector3.Transform(Vector3.UnitX, roadPoints[i].Rotation));
                    Vector3 pointOnLane = roadPoints[i].Position + normal * -pointOffset;
                    lanePoints.Add(pointOnLane);
                }

                for (int i = 0; i < lanePoints.Count - 1; i++)
                {
                    Vector2 start = Utils.WorldToScreen(lanePoints[i], center.ToVector3(), windowSize) + windowPos;
                    Vector2 end = Utils.WorldToScreen(lanePoints[i + 1], center.ToVector3(), windowSize) + windowPos;
                    if (start.X < minScreenPos.X) minScreenPos.X = start.X;
                    if (start.Y < minScreenPos.Y) minScreenPos.Y = start.Y;
                    if (start.X > maxScreenPos.X) maxScreenPos.X = start.X;
                    if (start.Y > maxScreenPos.Y) maxScreenPos.Y = start.Y;
                    drawList.AddLine(start, end, ImGui.GetColorU32(new Vector4(0.6f, 0.4f, 0.4f, 1)), 2 * InternalVisualizationConstants.Scale);
                }
            }

            for (int laneIndex = 0; laneIndex < right.Length; laneIndex++)
            {
                List<Vector3> lanePoints = new List<Vector3>();
                var laneOffset = right[laneIndex];
                var prevLaneOffset = prevRight.Length > 0 ? prevRight[laneIndex] : laneOffset;

                for (int i = 0; i < roadPoints.Count; i++)
                {
                    var pointOffset = RoadUtils.Lerp(prevLaneOffset, laneOffset, i / (float)(roadPoints.Count - 1));
                    Vector3 normal = Vector3.Normalize(Vector3.Transform(Vector3.UnitX, roadPoints[i].Rotation));
                    Vector3 pointOnLane = roadPoints[i].Position + normal * -pointOffset;
                    lanePoints.Add(pointOnLane);
                }

                for (int i = 0; i < lanePoints.Count - 1; i++)
                {
                    Vector2 start = Utils.WorldToScreen(lanePoints[i], center.ToVector3(), windowSize) + windowPos;
                    if (start.X < minScreenPos.X) minScreenPos.X = start.X;
                    if (start.Y < minScreenPos.Y) minScreenPos.Y = start.Y;
                    if (start.X > maxScreenPos.X) maxScreenPos.X = start.X;
                    if (start.Y > maxScreenPos.Y) maxScreenPos.Y = start.Y;
                    Vector2 end = Utils.WorldToScreen(lanePoints[i + 1], center.ToVector3(), windowSize) + windowPos;
                    drawList.AddLine(start, end, ImGui.GetColorU32(new Vector4(0.4f, 0.6f, 0.4f, 1)), 2 * InternalVisualizationConstants.Scale);
                }
            }

            if (ImGui.IsMouseHoveringRect(minScreenPos, maxScreenPos))
            {
                ImGui.BeginTooltip();
                ImGui.Spacing();
                ImGui.Text("Road:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.8f, 1f, 1f, 1f), road.RoadType.ToString());
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"({road.Length}m)");
                ImGui.Indent();
                ImGui.Text("Lanes:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 1f, 1f), $"{LanesToString(left)}, {LanesToString(right)}");
                ImGui.Text("Points: ");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{roadPoints.Count * (left.Count() + right.Count())}");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"({roadPoints.Count} per lane)");
                ImGui.Text($"UID:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{road.Uid}");
                ImGui.Unindent();
                ImGui.Spacing();
                ImGui.EndTooltip();
            }
        }
    }
}