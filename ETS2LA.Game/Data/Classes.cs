using ETS2LA.Notifications;
using TruckLib.ScsMap;
using TruckLib;

using ETS2LA.Game.Utils;
using System.Numerics;

namespace ETS2LA.Game.Data;

/// <summary>
///  List of item types ETS2LA should ignore when
///  reading map data. These item types are ignored
///  when DataFidelity is High or lower. 
///  Extreme loads everything.
/// </summary>
public enum IgnoredItemTypes
{
    Terrain = 0x01,
    Model = 0x05,
    Company = 0x06,
    Service = 0x07,
    CutPlane = 0x08,
    Mover = 0x09,
    EnvironmentArea = 0x0B,
    CityArea = 0x0C,
    Hinge = 0x0D,
    AnimatedModel = 0x0F,
    MapOverlay = 0x12,
    Sound = 0x15,
    Garage = 0x16,
    CameraPoint = 0x17,
    Walker = 0x1C,
    TrafficArea = 0x26,
    BezierPatch = 0x27,
    Compound = 0x28,
    Trajectory = 0x29,
    MapArea = 0x2A,
    FarModel = 0x2B,
    Curve = 0x2C,
    CameraPath = 0x2D,
    Cutscene = 0x2E,
    Hookup = 0x2F,
    VisibilityArea = 0x30,
};

/// <summary>
///  Contains all map data for the game. This class overrides TruckLib.ScsMap.Map
///  with ETS2LA specific notification handling and dropping of items.
/// </summary>
public class MapData : Map
{
    protected override bool PostProcessItem(MapItem item) 
    {
        DataFidelity fidelity = DataSettings.Current.DataFidelity;
        switch (fidelity)
        {
            case DataFidelity.Low:
                // For low fidelity, drop all items that aren't roads or prefabs since
                // they aren't relevant for driving.
                if (item is not Prefab && item is not Road)
                {
                    return false;
                }
                break;
            case DataFidelity.Medium:
            case DataFidelity.High:
                // For medium (and high) fidelity drop all items that aren't in the default enum.
                if (typeof(IgnoredItemTypes).GetEnumNames().Contains(item.ItemType.ToString()))
                {
                    return false;
                }
                break;
            
            // Extreme just keeps everything.
        }
        
        // Additionally we drop terrain data of prefabs and roads as it
        // also saves some memory. Dropping entire prefabs/roads can also be
        // done for items that are "secret" (i.e. not show in the UI map) since
        // they aren't relevant for driving. (in Medium and Low fidelity levels)
        if (item is Prefab p)
        {
            if (fidelity < DataFidelity.High && !p.ShowInUiMap)
                return false;
            
            if (fidelity < DataFidelity.Extreme)
            {
                foreach (var node in p.PrefabNodes)
                {
                    node.Terrain = null;
                }
            }
        }
        else if (item is Road r)
        {
            if (fidelity < DataFidelity.High && !r.ShowInUiMap) 
                return false;
            
            if (fidelity < DataFidelity.Extreme)
            {
                r.Left.Terrain = null;
                r.Right.Terrain = null;
            }
        }         
        return true;
    }

    protected override void OnSectorLoading(Sector sector, int index, int total)
    {
        NotificationHandler.Current.SendNotification(new Notification
        {
            Id = "ETS2LA.Game.Parsing",
            Title = "Parsing Map Data",
            Content = $"Parsing sector {index + 1} of {total}...",
            IsProgressIndeterminate = false,
            Progress = ((index + 1) / (float)total) * 100f,
            CloseAfter = 0
        });
    }
}

public enum Side
{
    Left,
    Right
}

/// <summary>
///  Parsed road that takes into account all ETS2LA specific adjustments,
///  such as lane offsets and Next/Last items etc... <br/><br/>
///  You can get a ParsedRoad by instantiating it with a base Road.
/// </summary>
public class ParsedRoad
{
    /// <summary>
    ///  This is the original base road data as parsed from the map.
    ///  You may use it to access information we don't provide in this parsed version,
    ///  just keep in mind that the offset values won't be accurate (well available at all)
    ///  in the base functions.
    /// </summary>
    public Road Road;
    
    /// <summary>
    ///  Start node for the current road piece. Note that this doesn't necessarily
    ///  mean that Start -> End means the right side is going that direction.
    ///  Sometimes roads can be "reversed" in the map data.
    /// </summary>
    public Node? StartNode;
    /// <summary>
    ///  End node for the current road piece. Note that this doesn't necessarily
    ///  mean that Start -> End means the right side is going that direction.
    ///  Sometimes roads can be "reversed" in the map data.
    /// </summary>
    public Node? EndNode;

    /// <summary>
    ///  The MapItem that connects to the StartNode from the other side.
    ///  Use `Last is Road` or `Last is Prefab` to check what type it is before
    ///  casting.
    /// </summary>    
    public MapItem? Last = null;
    /// <summary>
    ///  The MapItem that connects to the EndNode from the other side.
    ///  Use `Next is Road` or `Next is Prefab` to check what type it is before
    ///  casting.    
    /// </summary>
    public MapItem? Next = null;

    // The are all private, as they'll be accessed only inside
    // the functions of this class.
    private float[]? LeftLaneOffsetsStart;
    private float[] LeftLaneOffsetsEnd;
    private float[]? RightLaneOffsetsStart;
    private float[] RightLaneOffsetsEnd;

    public ParsedRoad(Road road)
    {
        Road = road;
        Last = road.BackwardItem as MapItem;
        Next = road.ForwardItem as MapItem;
        LeftLaneOffsetsEnd = RoadUtils.CalculateRoadLaneCenters(road).Left;
        RightLaneOffsetsEnd = RoadUtils.CalculateRoadLaneCenters(road).Right;

        if (Last is Road lastRoad)
        {
            LeftLaneOffsetsStart = RoadUtils.CalculateRoadLaneCenters(lastRoad).Left;
            RightLaneOffsetsStart = RoadUtils.CalculateRoadLaneCenters(lastRoad).Right;
        }
    }

    /// <summary>
    ///  Get the lane count for the specified side. Note that lane counts can be different on each side,
    ///  so for figuring out the total lane count please use `GetTotalLaneCount()`, or tally up the two sides.
    /// </summary>
    /// <param name="side">The side for which to get lane count.</param>
    /// <returns>The number of lanes on the specified side.</returns>
    public int GetLaneCount(Side side) => side == Side.Left ? LeftLaneOffsetsEnd.Length 
                                                            : RightLaneOffsetsEnd.Length;
    /// <summary>
    ///  Get the total lane count for the road, summing up both sides. Note that lane counts can be different
    ///  on each side, so use `GetLaneCount(Side side)` if you want to differentiate between them.
    /// </summary>
    /// <returns>The total number of lanes on the road.</returns>
    public int GetTotalLaneCount() => LeftLaneOffsetsEnd.Length + RightLaneOffsetsEnd.Length;

    // The functions are all wrappers around the base Road functions.
    // They just take into account the last road's offset values, this way
    // we have accurate transitions between roads everywhere.

    /// <summary>
    ///  Interpolate the middle of the road at the t value (between 0 and 1).
    /// </summary>
    /// <param name="t">The interpolation factor/parameter (0 to 1)</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When t is not between 0 and 1.</exception>
    public OrientedPoint Interpolate(float t)
    {
        if (t < 0 || t > 1) throw new ArgumentOutOfRangeException(nameof(t), "t must be between 0 and 1");
        return Road.InterpolateCurve(t);
    }

    /// <summary>
    ///  Interpolate the middle of the road at the distance along the road. Distance must be between 0 and road length.
    /// </summary>
    /// <param name="dist">The distance along the road (0 to road length)</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When dist is not between 0 and road length.</exception>
    public OrientedPoint? InterpolateDist(float dist)
    {
        if (dist < 0 || dist > Road.Length) throw new ArgumentOutOfRangeException(nameof(dist), "dist must be between 0 and road length");
        return Road.InterpolateCurveDist(dist);
    }

    /// <summary>
    ///  Interpolate the lane position at the t value (between 0 and 1) for the specified lane index and side. 
    ///  Lane index must be between 0 and lane count for the specified side.
    /// </summary>
    /// <param name="t">The interpolation factor/parameter (0 to 1)</param>
    /// <param name="side">The side for which to interpolate.</param>
    /// <param name="laneIndex">The index of the lane for which to interpolate.</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When t is not between 0 and 1, or when laneIndex is not valid for the specified side.</exception>
    public OrientedPoint InterpolateLane(float t, Side side, int laneIndex)
    {
        if (t < 0 || t > 1) throw new ArgumentOutOfRangeException(nameof(t), "t must be between 0 and 1");
        if (side == Side.Left && (laneIndex < 0 || laneIndex >= LeftLaneOffsetsEnd.Length)) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {LeftLaneOffsetsEnd.Length - 1} for left side");
        if (side == Side.Right && (laneIndex < 0 || laneIndex >= RightLaneOffsetsEnd.Length)) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {RightLaneOffsetsEnd.Length - 1} for right side");

        float offset = side == Side.Left ? LeftLaneOffsetsEnd[laneIndex] : RightLaneOffsetsEnd[laneIndex];
        float lastOffset = side == Side.Left ? (LeftLaneOffsetsStart != null ? LeftLaneOffsetsStart[laneIndex] : offset) 
                                             : (RightLaneOffsetsStart != null ? RightLaneOffsetsStart[laneIndex] : offset);

        if (offset != lastOffset)
            offset = RoadUtils.Lerp(lastOffset, offset, t);
        
        OrientedPoint point = Road.InterpolateCurve(t);
        Vector3 normal = Vector3.Normalize(Vector3.Transform(Vector3.UnitX, point.Rotation));
        point.Position = point.Position + normal * -offset;

        return point;
    }

    /// <summary>
    ///  Interpolate the lane position at the t value (between 0 and 1) for the specified lane index. 
    ///  Lane index must be between 0 and total lane count.
    /// </summary>
    /// <param name="t">The interpolation factor/parameter (0 to 1)</param>
    /// <param name="laneIndex">The index of the lane for which to interpolate.</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When t is not between 0 and 1, or when laneIndex is not valid for the specified side.</exception>
    public OrientedPoint InterpolateLane(float t, int laneIndex)
    {
        int leftLaneCount = LeftLaneOffsetsEnd.Length;
        if (laneIndex < 0 || laneIndex >= leftLaneCount + RightLaneOffsetsEnd.Length) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {leftLaneCount + RightLaneOffsetsEnd.Length - 1}");
        
        if (laneIndex < leftLaneCount)
            return InterpolateLane(t, Side.Left, laneIndex);
        else
            return InterpolateLane(t, Side.Right, laneIndex - leftLaneCount);
    }

    /// <summary>
    ///  Interpolate the lane position at the distance along the road for the specified lane index and side. 
    ///  Distance must be between 0 and road length.
    /// </summary>
    /// <param name="dist">The distance along the road (0 to road length)</param>
    /// <param name="side">The side of the road (left or right)</param>
    /// <param name="laneIndex">The index of the lane for which to interpolate.</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When dist is not between 0 and road length.</exception>
    /// <exception cref="ArgumentOutOfRangeException">When laneIndex is not valid for the specified side.</exception>
    public OrientedPoint? InterpolateLaneDist(float dist, Side side, int laneIndex)
    {
        if (dist < 0 || dist > Road.Length) throw new ArgumentOutOfRangeException(nameof(dist), "dist must be between 0 and road length");
        if (side == Side.Left && (laneIndex < 0 || laneIndex >= LeftLaneOffsetsEnd.Length)) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {LeftLaneOffsetsEnd.Length - 1} for left side");
        if (side == Side.Right && (laneIndex < 0 || laneIndex >= RightLaneOffsetsEnd.Length)) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {RightLaneOffsetsEnd.Length - 1} for right side");

        float offset = side == Side.Left ? LeftLaneOffsetsEnd[laneIndex] : RightLaneOffsetsEnd[laneIndex];
        float lastOffset = side == Side.Left ? (LeftLaneOffsetsStart != null ? LeftLaneOffsetsStart[laneIndex] : offset) 
                                             : (RightLaneOffsetsStart != null ? RightLaneOffsetsStart[laneIndex] : offset);

        if (offset != lastOffset)
            offset = RoadUtils.Lerp(lastOffset, offset, dist / Road.Length);
        
        OrientedPoint? point = Road.InterpolateCurveDist(dist);
        if (point == null) return null;
        OrientedPoint p = point.Value;

        Vector3 normal = Vector3.Normalize(Vector3.Transform(Vector3.UnitX, point.Value.Rotation));
        p.Position = p.Position + normal * -offset;

        return p;
    }

    /// <summary>
    ///  Interpolate the lane position at the distance along the road for the specified lane index. 
    ///  Distance must be between 0 and road length. Lane index must be between 0 and total lane count.
    /// </summary>
    /// <param name="dist">The distance along the road (0 to road length)</param>
    /// <param name="laneIndex">The index of the lane for which to interpolate.</param>
    /// <returns>TruckLib.OrientedPoint at this location.</returns>
    /// <exception cref="ArgumentOutOfRangeException">When dist is not between 0 and road length.</exception>
    /// <exception cref="ArgumentOutOfRangeException">When laneIndex is not valid for the specified side.</exception>
    public OrientedPoint? InterpolateLaneDist(float dist, int laneIndex)
    {
        int leftLaneCount = LeftLaneOffsetsEnd.Length;
        if (laneIndex < 0 || laneIndex >= leftLaneCount + RightLaneOffsetsEnd.Length) 
            throw new ArgumentOutOfRangeException(nameof(laneIndex), $"laneIndex must be between 0 and {leftLaneCount + RightLaneOffsetsEnd.Length - 1}");
        
        if (laneIndex < leftLaneCount)
            return InterpolateLaneDist(dist, Side.Left, laneIndex);
        else
            return InterpolateLaneDist(dist, Side.Right, laneIndex - leftLaneCount);
    }

    /// <summary>
    ///  This method calculates the factor for a given point on the road.
    ///  Used when you need the equivalent location on a road, for whatever
    ///  starting point.
    /// </summary>
    /// <param name="point">Point to project onto the road.</param>
    /// <returns>Factor from 0-1 along the road.</returns>
    public float GetFactorForPoint(Vector3 point)
    {
        Vector3 ab = Road.Node.Position - Road.ForwardNode.Position;
        float lengthSquared = Vector3.Dot(ab, ab);
        if (lengthSquared == 0) return 0;

        float t = Vector3.Dot(point - Road.ForwardNode.Position, ab) / lengthSquared;
        return Math.Clamp(t, 0, 1);
    }

    /// <summary>
    ///  Converts a factor to a distance along the road.
    ///  Note that this always goes from Start - End, meaning
    ///  the distance and factor can *decrease* as you drive along
    ///  the road.
    /// </summary>
    /// <param name="factor">Input factor.</param>
    /// <returns>Distance in meters along the road.</returns>
    public float FactorToDistance(float factor)
    {
        return factor * Road.Length;
    }

    /// <summary>
    ///  Converts a distance along the road to a factor.
    /// </summary>
    /// <param name="distance">Input distance in meters.</param>
    /// <returns>Factor from 0-1 along the road.</returns>
    public float DistanceToFactor(float distance)
    {
        return distance / Road.Length;
    }
}