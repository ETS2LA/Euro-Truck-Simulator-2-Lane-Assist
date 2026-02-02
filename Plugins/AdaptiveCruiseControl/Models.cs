using System.Collections.Generic;
using ETS2LA.Shared;

namespace AdaptiveCruiseControl;

public record SteeringPoints(IReadOnlyList<Vector3Double> Points);

public record ACCVehicle(Vector3 position, float speed, float acceleration, float length, bool isTmp, bool isTrailer, int id)
{
    public float Distance { get; set; }
}

public record ACCTrafficLight(Vector3 position, float cx, float cy, Quaternion rotation, int state, float distance);

public record ACCGate(Vector3 position, float cx, float cy, Quaternion rotation, int state, float distance);
