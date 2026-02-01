using TruckLib.Sii;
using System.Numerics;
using TruckLib.ScsMap;
using TruckLib;
using ETS2LA.Logging;

namespace ETS2LA.Game.Utils;

public static class RoadUtils
{
    /// <summary>
    ///  Calculates the lane center positions for a given road. Code from skzk in this <br>
    ///  gist: https://gist.github.com/sk-zk/8e9a2921f7d0b196773678c475d166ca
    /// </summary>
    /// <param name="road">The road to calculate lane centers for.</param>
    /// <returns>A tuple containing two float arrays: the left lane centers and the right lane centers.</returns>
    public static (float[] Left, float[] Right) CalculateRoadLaneCenters(Road road, IFileSystem fs)
    {
        // Load in the road template
        Logger.Info($"Calculating lane centers for road type: {road.RoadType}");
        var sii = SiiFile.Open(@"/def/world/road_look.template.sii", fs);
        var roadTmpl = sii.Units.First(u => u.Name == road.RoadType);

        const float laneWidth = 4.5f;
        const float halfLaneWidth = 2.25f;

        if (!roadTmpl.Attributes.TryGetValue("lanes_right", out var rightLanes))
        {
            // Rail model without any traffic lanes
            return ([], []);
        }
        var hasLeftModel = roadTmpl.Attributes.TryGetValue("lanes_left", out var leftLanes);

        // Generate lane center sequence
        var rightCenters = new float[rightLanes.Count];
        rightCenters[0] = hasLeftModel
            ? halfLaneWidth
            : MathF.Ceiling(rightLanes.Count / 2f) * (-laneWidth) + halfLaneWidth;
        for (int i = 1; i < rightLanes.Count; i++)
            rightCenters[i] = rightCenters[i - 1] + laneWidth;

        float[] leftCenters;
        if (hasLeftModel)
        {
            leftCenters = new float[leftLanes?.Count];
            leftCenters[0] = -halfLaneWidth;
            for (int i = 1; i < leftLanes?.Count; i++)
                leftCenters[i] = leftCenters[i - 1] - laneWidth;
        }
        else
        {
            leftCenters = [];
        }

        // Apply road_offset
        if (roadTmpl.Attributes.TryGetValue("road_offset", out var roadOffset))
        {
            for (int i = 0; i < rightCenters.Length; i++)
                rightCenters[i] += roadOffset;
            for (int i = 0; i < leftCenters.Length; i++)
                leftCenters[i] -= roadOffset;
        }

        // Apply lane_offsets
        if (roadTmpl.Attributes.TryGetValue("lane_offsets_right", out var laneOffsetsRight))
        {
            for (int i = 0; i < rightCenters.Length; i++)
            {
                // some parsing weirdness, sorry about that
                if (laneOffsetsRight[i] is Vector2 v)
                    rightCenters[i] += v.X;
                else if (laneOffsetsRight[i] is ValueTuple<int, int> t)
                    rightCenters[i] += t.Item1;
            }
        }
        if (hasLeftModel && roadTmpl.Attributes.TryGetValue("lane_offsets_left", out var laneOffsetsLeft))
        {
            for (int i = 0; i < leftCenters.Length; i++)
            {
                if (laneOffsetsLeft[i] is Vector2 v)
                    leftCenters[i] -= v.X;
                else if (laneOffsetsLeft[i] is ValueTuple<int, int> t)
                    leftCenters[i] -= t.Item1;
            }
        }

        return (leftCenters, rightCenters);
    }
}