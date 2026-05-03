using ETS2LA.Game.Data;
using ETS2LA.Shared;
using ETS2LA.Telemetry;
using ETS2LA.Logging;

using TruckLib.ScsMap;
using Hexa.NET.ImGui;
using System.Numerics;
using TruckLib;

namespace InternalVisualization.Renderers;

public class NodesRenderer : Renderer
{
    private void DrawItemTooltip(IMapObject item, MapData mapData)
    {
        mapData.MapItems.TryGetValue(item.Uid, out var mapItem);
        if (mapItem != null)
        {
            ImGui.Text($"Type: {mapItem.ItemType}");
            ImGui.Indent();
            switch (mapItem.ItemType)
            {
                case ItemType.Road:
                    Road road = (Road)item;
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{road.RoadType}");
                    break;
                case ItemType.Prefab:
                    Prefab prefab = (Prefab)item;
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{prefab.Model}");
                    break;
                case ItemType.Sign:
                    Sign sign = (Sign)item;
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{sign.Model}");
                    break;
                case ItemType.Buildings:
                    Buildings building = (Buildings)item;
                    ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{building.Name}");
                    break;
                default:
                    break;
            }
            ImGui.Unindent();
        }
        else
        {
            ImGui.TextColored(new Vector4(0.6f, 0.5f, 0.5f, 1f), "Culled to save memory");
        }
        return;
    }

    public override void Render(ImDrawListPtr drawList, Vector2 windowPos, Vector2 windowSize, 
                                GameTelemetryData telemetryData, MapData mapData, Road[] roads, Prefab[] prefabs, IReadOnlyList<Node> nearbyNodes)
    {
        Vector3Double center = telemetryData.truckPlacement.coordinate;
        foreach (var node in nearbyNodes)
        {
            var forwardItem = node.ForwardItem;
            var backwardItem = node.BackwardItem;
            if (forwardItem == null && backwardItem == null) continue;
            
            Vector2 screenPos = Utils.WorldToScreen(node.Position, center.ToVector3(), windowSize);
            drawList.AddCircle(screenPos + windowPos, 3 * InternalVisualizationConstants.Scale, ImGui.GetColorU32(new Vector4(1, 1, 1, 0.1f)));
            if (ImGui.IsMouseHoveringRect(screenPos + windowPos - new Vector2(5, 5), screenPos + windowPos + new Vector2(5, 5)))
            {
                ImGui.BeginTooltip();
                ImGui.Spacing();
                ImGui.Text($"Node");
                ImGui.SameLine();
                ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), $"{node.Uid}");
                ImGui.Indent();

                ImGui.Text("Forward:");
                ImGui.Indent();
                if (node.ForwardItem != null) { DrawItemTooltip(node.ForwardItem, mapData); }
                else { ImGui.TextColored(new Vector4(0.6f, 0.5f, 0.5f, 1f), "None"); }
                ImGui.Unindent();
                
                ImGui.Text($"Backward:");
                ImGui.Indent();
                if (node.BackwardItem != null) { DrawItemTooltip(node.BackwardItem, mapData); }
                else { ImGui.TextColored(new Vector4(0.6f, 0.5f, 0.5f, 1f), "None"); }
                ImGui.Unindent();
                
                ImGui.Unindent();
                ImGui.Spacing();
                ImGui.EndTooltip();
            }
        }
    }
}