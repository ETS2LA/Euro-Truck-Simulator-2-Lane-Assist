using ETS2LA.Game.Data;
using ETS2LA.Game.PpdFiles;
using ETS2LA.Shared;
using ETS2LA.Telemetry;
using ETS2LA.Logging;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;
using TruckLib;
using Avalonia.Controls;
using TruckLib.Models.Ppd;
using ETS2LA.Game.Utils;

namespace InternalVisualization.Renderers;

public class PrefabsRenderer : Renderer
{

    private List<string> invalidPrefabTypes = new List<string>();

    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        Vector3Double center = telemetryData.truckPlacement.coordinate;
        Dictionary<ulong, Prefab> nearbyPrefabs = new Dictionary<ulong, Prefab>();

        foreach (var node in nearbyNodes)
        {
            if(node.BackwardItem is Prefab)
            {
                Prefab prefab = (Prefab)node.BackwardItem;
                if (!nearbyPrefabs.ContainsKey(prefab.Uid))
                {
                    nearbyPrefabs.Add(prefab.Uid, prefab);
                }
            }

            if(node.ForwardItem is Prefab)
            {
                Prefab prefab = (Prefab)node.ForwardItem;
                if (!nearbyPrefabs.ContainsKey(prefab.Uid))
                {
                    nearbyPrefabs.Add(prefab.Uid, prefab);
                }
            }
        }


        float resolution = 0.25f; // meters
        foreach (var prefab in nearbyPrefabs.Values)
        {
            //if (!prefab.ShowInUiMap) continue;
            if (invalidPrefabTypes.Contains(prefab.Model.ToString())) continue;

            var ppd = PpdFileHandler.Current.GetPpdFile(prefab.Model.ToString());
            if (ppd == null)
            {
                invalidPrefabTypes.Add(prefab.Model.ToString());
                Logger.Error($"Failed to load PPD file for prefab {prefab.Model}");
                continue;
            }

            PrefabDescriptor desc = (PrefabDescriptor)ppd;
            int origin = prefab.Origin;

            Vector3 prefabStart = prefab.Nodes[0].Position - desc.Nodes[origin].Position;
            Vector3 prefabRotation = prefab.Nodes[0].Rotation.ToEuler() - MathEx.GetNodeRotation(desc.Nodes[origin].Direction).ToEuler();
            Matrix4x4 rotationMatrix = Matrix4x4.CreateRotationY(prefabRotation.Y, prefab.Nodes[0].Position);

            Vector2 minScreenPos = new Vector2(float.MaxValue, float.MaxValue);
            Vector2 maxScreenPos = new Vector2(float.MinValue, float.MinValue);
            foreach (var curve in desc.NavCurves)
            {
                List<Vector3> curvePoints = new List<Vector3>();
                float step = 1 / curve.Length / resolution;
                for (float t = -step; t <= 1 + step; t += step)
                {
                    var point = PrefabUtils.InterpolateNavCurve(curve, t);
                    curvePoints.Add(point);
                }

                // Convert from 0,0 to world coordinates.
                for (int i = 0; i < curvePoints.Count; i++)
                {
                    curvePoints[i] = Vector3.Transform(curvePoints[i] + prefabStart, rotationMatrix);
                }

                // Render in screenspace
                for (int i = 0; i < curvePoints.Count - 1; i++)
                {
                    Vector2 screenPos = Utils.WorldToScreen(curvePoints[i], center.ToVector3(), windowSize) + windowPos;
                    Vector2 nextScreenPos = Utils.WorldToScreen(curvePoints[i + 1], center.ToVector3(), windowSize) + windowPos;
                    if (screenPos.X < minScreenPos.X) minScreenPos.X = screenPos.X;
                    if (screenPos.Y < minScreenPos.Y) minScreenPos.Y = screenPos.Y;
                    if (screenPos.X > maxScreenPos.X) maxScreenPos.X = screenPos.X;
                    if (screenPos.Y > maxScreenPos.Y) maxScreenPos.Y = screenPos.Y;

                    drawList.AddLine(screenPos, nextScreenPos, ImGui.GetColorU32(new Vector4(0.5f, 0.5f, 0.4f, 1)), 2 * InternalVisualizationConstants.Scale);
                }

            }
            if (ImGui.IsMouseHoveringRect(minScreenPos, maxScreenPos))
            {
                ImGui.BeginTooltip();
                ImGui.Spacing();
                ImGui.Text("Prefab:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.8f, 1f, 1f, 1f), prefab.Model.ToString());
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"({prefab.Look}, {prefab.Variant})");
                ImGui.Indent();
                ImGui.Text($"UID:");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{prefab.Uid}");
                ImGui.Unindent();
                ImGui.Spacing();
                ImGui.EndTooltip();
            }
        }
    }
}