using TruckLib;
using TruckLib.Sii;
using TruckLib.ScsMap;
using TruckLib.Models.Ppd;

using System.Numerics;
using System.Collections.Concurrent;

using ETS2LA.Logging;
using ETS2LA.Game.SiiFiles;
using System.Formats.Asn1;
namespace ETS2LA.Game.Utils;

public static class RoadUtils
{
    private static readonly ConcurrentDictionary<string, (float[] Left, float[] Right)> _roadLaneCache = new ConcurrentDictionary<string, (float[] Left, float[] Right)>();

    /// <summary>
    ///  Calculates the lane center positions for a given road. Code originally from skzk in this gist:<br/>
    ///  https://gist.github.com/sk-zk/8e9a2921f7d0b196773678c475d166ca <br/>
    ///  Modified heavily to bring up to date with mod support and things he missed.
    /// </summary>
    /// <param name="road">The road to calculate lane centers for.</param>
    /// <returns>A tuple containing two float arrays: the left lane centers and the right lane centers.</returns>
    public static (float[] Left, float[] Right) CalculateRoadLaneCenters(Road road)
    {
        var key = road.RoadType.ToString();
        if (_roadLaneCache.TryGetValue(key, out var cached))
        {
            return cached;
        }

        Unit? roadTmpl;
        // Usually templates seem to have the "road." prefix
        // however some don't, so we gotta check for both.
        roadTmpl = SiiFileHandler.Current.GetRoadUnit("road." + road.RoadType.ToString());
        if (roadTmpl == null) roadTmpl = SiiFileHandler.Current.GetRoadUnit(road.RoadType.ToString());
        if (roadTmpl == null)
        {
            Logger.Error($"Road template for {road.RoadType} not found in SII file.");
            return ([], []);
        }

        // Some roads seem to have differing lane widths, is there 
        // any way to detect that?
        const float laneWidth = 4.5f;
        const float halfLaneWidth = laneWidth / 2f;

        var hasRightModel = roadTmpl.Attributes.TryGetValue("lanes_right", out var rightLanes);
        var hasLeftModel = roadTmpl.Attributes.TryGetValue("lanes_left", out var leftLanes);

        var roadCenter = 0f;
        var totalLanes = (hasLeftModel ? leftLanes?.Count : 0) + (hasRightModel ? rightLanes?.Count : 0);

        // Some roads are not even, e.g. the left side of the road has two lanes
        // while the right has one. In these cases the offset should be moved to
        // keep it in the "middle" of the road.
        if (hasRightModel && hasLeftModel && totalLanes % 2 == 1)
        {
            int offset = leftLanes?.Count - rightLanes?.Count;
            roadCenter = offset * laneWidth;
        }

        float[] rightCenters;
        rightCenters = new float[hasRightModel ? rightLanes.Count : 0];
        if (hasRightModel)
        {
            rightCenters[0] = 0;

            // In most cases roads have both a right and left side. For this reason ETS2LA keeps the right side
            // as the "primary side" when calculating offsets. Turns out Project Japan does things differently,
            // so you'll find some duplicated if statements in the left centers. If there's a unified way to do
            // this then go ahead and make a PR. Just be sure to provide test samples in cases where the road is
            // entirely on the left side.
        
            // Unbalanced two-way roads (e.g. 2 lanes on the right, 1 lane on the left) are centered around the middle lane, 
            // so we need to offset the right lanes accordingly.
            // Two sided road.
            if (hasLeftModel)
                rightCenters[0] = roadCenter + halfLaneWidth;
            // One-way with only one lane
            else if (!hasLeftModel && rightLanes?.Count == 1)
                rightCenters[0] = roadCenter + halfLaneWidth;
            // One-way with an odd number of lanes, so there's a center lane
            else if (rightLanes?.Count % 2 == 1 && !hasLeftModel)
                rightCenters[0] = roadCenter - halfLaneWidth;
            // Others, e.g. one-way with an even number of lanes
            else
                rightCenters[0] = roadCenter + MathF.Ceiling(rightLanes?.Count / 2f) * (-laneWidth) + halfLaneWidth;

            // This applies the offsets to the full side.
            // Each lane is separated by a full 4.5m.
            for (int i = 1; i < rightLanes?.Count; i++)
                rightCenters[i] = rightCenters[i - 1] + laneWidth;
        }

        float[] leftCenters;
        leftCenters = new float[hasLeftModel ? leftLanes.Count : 0];
        if (hasLeftModel)
        {
            if (hasRightModel)
            {
                leftCenters[0] = roadCenter - halfLaneWidth;
                for (int i = 1; i < leftLanes?.Count; i++)
                    leftCenters[i] = leftCenters[i - 1] - laneWidth;
            }
            else // So far only Project Japan
            {
                // One way with one lane
                if (leftLanes?.Count == 1)
                    leftCenters[0] = roadCenter - halfLaneWidth;
                // One way with odd number of lanes
                else if (leftLanes?.Count % 2 == 1)
                    leftCenters[0] = roadCenter + halfLaneWidth;
                // One way with even number of lanes
                else
                    leftCenters[0] = roadCenter + MathF.Ceiling(leftLanes?.Count / 2f) * (+laneWidth) - halfLaneWidth;

                for (int i = 1; i < leftLanes?.Count; i++)
                    leftCenters[i] = leftCenters[i - 1] - laneWidth;
            }
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
        if (hasRightModel && roadTmpl.Attributes.TryGetValue("lane_offsets_right", out var laneOffsetsRight))
        {
            for (int i = 0; i < rightCenters.Length; i++)
            {
                // some parsing weirdness, sorry about that
                // ^ sk-zk
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

        var result = (leftCenters, rightCenters);
        _roadLaneCache[key] = result;

        return result;
    }

    public static float Lerp(float a, float b, float t)
    {
        return a + (b - a) * t;
    }

    public static float GetRoadResolution(Road road)
    {
        switch (road.Resolution)
        {
            case RoadResolution.Normal:
                return 15f;
            case RoadResolution.HighPoly:
                return 5f;
            case RoadResolution.Superfine:
                return 1f;
            default:
                return 15f;
        }
    }
}

public static class PrefabUtils
{
    public static Vector3 InterpolateNavCurve(NavCurve curve, float t)
    {
        var fakeStart = new FakeNode(curve.StartPosition, curve.StartRotation);
        var fakeEnd = new FakeNode(curve.EndPosition, curve.EndRotation);
        
        return HermiteSpline.InterpolatePolyline(fakeStart, fakeEnd, t);
    }

    /// <summary>
    ///  This class is effectively just a position/rotation container so that we can use the existing HermiteSpline
    ///  interpolation code without needing to touch TruckLib. Should not be used for any other purpose!
    /// </summary>
    public class FakeNode : INode
    {
        public ulong Uid { get; set; }
        public byte BackwardCountry { get; set; }
        public IMapObject BackwardItem { get; set; }
        public byte ForwardCountry { get; set; }
        public IMapObject ForwardItem { get; set; }
        public bool FreeRotation { get; set; }
        public bool IsCountryBorder { get; set; }
        public bool IsRed { get; set; }
        public bool Locked { get; set; }

        public Vector3 Position { get; set; }
        public Quaternion Rotation { get; set; }

        public IItemContainer Parent { get; set; }
        public bool IsCurveLocator { get; set; }
        public bool PlayerVehicleTypeChange { get; set; }
        public bool FwdTruck { get; set; }
        public bool FwdBus { get; set; }
        public bool FwdCar { get; set; }
        public bool BwdTruck { get; set; }
        public bool BwdBus { get; set; }
        public bool BwdCar { get; set; }
        public bool IsOrphaned() { return false; }
        public void Move(Vector3 newPos) {}
        public void Translate(Vector3 translation) {}
        public void Merge(INode n2) {}
        public INode Split() { return this; }
        public string ToString() { return ""; }
        public void UpdateItemReferences(Dictionary<ulong, MapItem> allItems) {}
        public void Deserialize(BinaryReader r, uint? version = null) {}
        public void Serialize(BinaryWriter w) {}

        public FakeNode(Vector3 position, Quaternion rotation)
        {
            Position = position;
            Rotation = rotation;

            BackwardItem = new Node();
            ForwardItem = new Node();
        }
    }
}