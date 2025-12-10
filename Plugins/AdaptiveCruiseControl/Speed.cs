using System.Numerics;
using System.Linq;

namespace AdaptiveCruiseControl;

public static class Speed
{
    private const double G = 9.81; // m/s^2
    private const double MaxDistance = 150; // meters
    private const double MinDistance = 30; // meters

    public static double Mu { get; set; } = 0.5;

    public static double GetMaximumSpeedForPoints(IReadOnlyList<Vector3> points, double x, double z)
    {
        if (points.Count < 3)
            return 999;

        try
        {
            var curvatures = CalculateCurvatures(points, x, z);
            if (curvatures.Count == 0)
                return 999;

            var maxCurvature = curvatures.Max();
            if (maxCurvature <= 0)
                return 999;

            var maxSpeed = Math.Sqrt(Mu * G / maxCurvature);
            if (maxSpeed <= 0)
                return 999;

            return maxSpeed;
        }
        catch
        {
            return 999;
        }
    }

    private static List<double> CalculateCurvatures(IReadOnlyList<Vector3> points, double x, double z)
    {
        var curvatures = new List<double>();
        for (int i = 1; i < points.Count - 1; i++)
        {
            var p0 = points[i - 1];
            var p1 = points[i];
            var p2 = points[i + 1];

            var v1 = new Vector2(p1.X - p0.X, p1.Z - p0.Z);
            var v2 = new Vector2(p2.X - p1.X, p2.Z - p1.Z);

            var dot = Vector2.Dot(v1, v2);
            var norm = v1.Length() * v2.Length();
            if (norm == 0)
                continue;

            var cosAngle = Math.Clamp(dot / norm, -1d, 1d);
            var deltaTheta = Math.Acos(cosAngle);

            var deltaS = (v1.Length() + v2.Length()) / 2d;
            if (deltaS == 0)
                continue;

            var kappa = deltaTheta / deltaS;

            var distance = Math.Sqrt(Math.Pow(x - p1.X, 2) + Math.Pow(z - p1.Z, 2));
            var multiplier = 1 - (distance - MinDistance) / (MaxDistance - MinDistance);
            multiplier = Math.Clamp(multiplier, 0d, 1d);

            curvatures.Add(kappa * multiplier);
        }

        return curvatures;
    }
}
