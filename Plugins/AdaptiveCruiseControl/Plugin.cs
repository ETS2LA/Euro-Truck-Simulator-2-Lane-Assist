using System;
using System.Collections.Generic;
using System.Linq;
using ETS2LA.Logging;
using ETS2LA.Shared;
using NumVec2 = System.Numerics.Vector2;
using NumVec3 = System.Numerics.Vector3;

[assembly: PluginInformation(
    "Adaptive Cruise Control",
    "Adaptive Cruise Control (ACC) provides automatic acceleration and braking depending on road conditions and vehicles ahead.",
    AuthorName = "Tumppi066",
    AuthorWebsite = "https://github.com/Tumppi066",
    AuthorIcon = "https://avatars.githubusercontent.com/u/83072683?v=4",
    Tags = new[] { "Base", "Speed Control" }
)]

namespace AdaptiveCruiseControl;

public class Plugin : ETS2LA.Shared.Plugin, IPluginUi
{
    private readonly AccSettings _settings = new();
    private readonly AccRuntime _runtime = new();
    private readonly PidController _pid;
    private readonly SmoothedValue _accelSmooth = new(0.2);
    private readonly SmoothedValue _maxSpeedSmooth = new(0.5, 999);

    private GameTelemetryData? _telemetry;
    private TrafficData? _traffic;
    private SemaphoreData? _semaphores;
    private IReadOnlyList<NumVec3>? _roadPoints;
    private IReadOnlyDictionary<string, double>? _stopIn;
    private double _overrideAccel = 0;

    private bool _holdingUp;
    private bool _holdingDown;
    private DateTime _lastChange = DateTime.MinValue;

    public Plugin()
    {
        _pid = new PidController(_settings.PidKp, _settings.PidKi, _settings.PidKd);
        ApplyAggressiveness();
    }

    public override float TickRate => 15.0f; // similar to Python fps_cap

    public override void Init(IEventBus bus)
    {
        base.Init(bus);
        _bus?.Subscribe<GameTelemetryData>("GameTelemetry.Data", t => _telemetry = t);
        _bus?.Subscribe<TrafficData>("ETS2LASDK.Traffic", t => _traffic = t);
        _bus?.Subscribe<SemaphoreData>("ETS2LASDK.Semaphores", s => _semaphores = s);
        _bus?.Subscribe<SteeringPoints>("LaneAssist.SteeringPoints", p => _roadPoints = p.Points.Select(ToVector3).ToList());
        _bus?.Subscribe<Dictionary<string, double>>("LaneAssist.StopIn", s => _stopIn = s);
        _bus?.Subscribe<bool>("takeover", _ => _runtime.Enabled = false);
        _bus?.Subscribe<double>("AdaptiveCruiseControl.OverrideAcceleration", v => _overrideAccel = v);
    }

    public override void Tick()
    {
        if (_telemetry is null)
            return;

        if (_telemetry.paused)
        {
            PublishControls(0, 0);
            return;
        }

        UpdateParameters();
        UpdateManualOffset();

        if (!_runtime.Enabled)
        {
            PublishControls(0, 0);
            _runtime.Reset();
            _pid.Reset();
            return;
        }

        var targetSpeed = ComputeTargetSpeed();
        _runtime.TargetSpeedKph = targetSpeed * 3.6;

        var currentSpeed = _telemetry.truckFloat.speed;
        _runtime.SpeedKph = currentSpeed * 3.6;

        var accelVec = _telemetry.truckVector.acceleration;
        var totalAccel = Math.Sqrt(accelVec.X * accelVec.X + accelVec.Y * accelVec.Y + accelVec.Z * accelVec.Z);
        var sign = currentSpeed >= _runtime.LastSpeed ? 1 : -1;
        _runtime.LastSpeed = currentSpeed;
        _runtime.CurrentAccel = _accelSmooth.Update(totalAccel * sign);

        var inFront = GetVehicleInFront();
        if (inFront != null)
        {
            _runtime.LeadDistance = inFront.Distance;
            _runtime.DesiredGap = DesiredGap(currentSpeed, inFront.length, inFront.isTmp);
        }
        else
        {
            _runtime.LeadDistance = 0;
            _runtime.DesiredGap = 0;
        }

        var light = GetLightInFront();
        var gate = GetGateInFront();
        var stopIn = GetStopInDistance();

        var targetAccel = CalculateTargetAcceleration(targetSpeed, inFront, light, gate, stopIn);
        _runtime.TargetAccel = targetAccel;

        var output = _overrideAccel != 0 ? _overrideAccel : _pid.Compute(targetAccel, _runtime.CurrentAccel, currentSpeed, targetSpeed);
        _overrideAccel = 0;
        PublishControls(output, output < 0 ? -output : 0);
    }

    private void PublishControls(double throttle, double brake)
    {
        if (_telemetry == null)
            return;

        var gear = _telemetry.truckInt.gear;
        var clutch = _telemetry.truckFloat.userClutch;
        var speedKph = _telemetry.truckFloat.speed * 3.6;

        // Prevent acceleration while reversing or clutch pressed at speed.
        if (gear < 0)
        {
            _bus?.Publish("ETS2LA.Output.Event", new SDKControlEvent
            {
                aforward = 0.0001f,
                abackward = 0.0001f
            });
            return;
        }

        float forward = 0;
        float backward = 0;

        if (throttle > 0)
        {
            if (clutch < 0.1 || speedKph < 10)
                forward = (float)Math.Clamp(throttle, 0, 1);
            if (speedKph > 10)
                backward = 0;
            else if (backward == 0)
                backward = 0.0001f; // tiny brake bias when creeping
        }
        else if (throttle < 0)
        {
            backward = (float)Math.Clamp(-throttle, 0, 1);
            forward = 0;
        }

        _bus?.Publish("ETS2LA.Output.Event", new SDKControlEvent
        {
            aforward = forward,
            abackward = backward
        });
    }

    private void UpdateParameters()
    {
        ApplyAggressiveness();
        Speed.Mu = _settings.Mu;

        if (_settings.UnlockPid)
        {
            _pid.UpdateGains(_settings.PidKp, _settings.PidKi, _settings.PidKd);
            // Derivative bump when no cargo (reduces oscillations for lighter truck)
            if (string.IsNullOrEmpty(_telemetry?.configString.cargo))
            {
                _pid.UpdateGains(_settings.PidKp, _settings.PidKi, _settings.PidKd * 2);
            }
        }
    }

    private void UpdateManualOffset()
    {
        if ((DateTime.UtcNow - _lastChange).TotalSeconds > 0.2)
        {
            if (_holdingUp)
            {
                _runtime.ManualSpeedOffset += 1;
                _lastChange = DateTime.UtcNow;
                Notify($"Speed offset increased to: {_runtime.ManualSpeedOffset} {(_settings.SpeedOffsetType == "Absolute" ? "km/h" : "%")}");
            }
            else if (_holdingDown)
            {
                _runtime.ManualSpeedOffset -= 1;
                _lastChange = DateTime.UtcNow;
                Notify($"Speed offset decreased to: {_runtime.ManualSpeedOffset} {(_settings.SpeedOffsetType == "Absolute" ? "km/h" : "%")}");
            }
        }
    }

    private double ComputeTargetSpeed()
    {
        double limit = _telemetry?.truckFloat.speedLimit ?? 0;
        if (limit <= 0)
            limit = _settings.OverwriteSpeed / 3.6;

        if (_settings.IgnoreSpeedLimit)
            limit = 999 / 3.6;

        var offset = _settings.SpeedOffset + _runtime.ManualSpeedOffset;
        if (_settings.SpeedOffsetType == "Percentage")
            limit += limit * offset / 100.0;
        else
            limit += offset / 3.6;

        if (_roadPoints != null && _roadPoints.Count > 2)
        {
            var maxCurveSpeed = Speed.GetMaximumSpeedForPoints(_roadPoints, _telemetry!.truckPlacement.coordinate.X, _telemetry.truckPlacement.coordinate.Z);
            if (maxCurveSpeed > 0 && maxCurveSpeed < limit)
                limit = maxCurveSpeed;
        }

        limit = _maxSpeedSmooth.Update(limit);

        if (_settings.MaxSpeed > 0 && limit > _settings.MaxSpeed / 3.6)
            limit = _settings.MaxSpeed / 3.6;

        return limit;
    }

    private ACCVehicle? GetVehicleInFront()
    {
        if (_traffic?.vehicles is null || _telemetry is null)
            return null;

        var vehicles = ExpandVehicles(_traffic.vehicles);
        if (vehicles.Count == 0)
            return null;

        var points = BuildPathPoints();
        if (points.Count == 0)
            return null;

        var truckPos = _telemetry.truckPlacement.coordinate;
        var rot = _telemetry.truckPlacement.rotation.X * 360;
        if (rot < 0) rot += 360;
        var heading = Math.PI * rot / 180.0;
        var forward = new NumVec2((float)-Math.Sin(heading), (float)-Math.Cos(heading));

        ACCVehicle? best = null;
        float bestDist = float.MaxValue;

        foreach (var v in vehicles)
        {
            var pos = v.position;
            var to = new NumVec2(pos.X - (float)truckPos.X, pos.Z - (float)truckPos.Z);
            var forwardDistance = NumVec2.Dot(forward, to);
            if (forwardDistance <= 0) continue;

            var lateral = MathF.Sqrt(Math.Max(0, to.LengthSquared() - forwardDistance * forwardDistance));
            if (lateral > 6) continue; // coarse lane filter

            var polyDist = DistanceToPolyline(points, new NumVec3(pos.X, pos.Y, pos.Z));
            if (polyDist > 3) continue; // stay in-lane like Python

            var length = v.length;
            var adjusted = v.isTmp ? forwardDistance - length * 0.5f : forwardDistance - length * 0.8f;

            if (adjusted < bestDist)
            {
                bestDist = adjusted;
                v.Distance = adjusted;
                best = v;
            }
        }

        return best;
    }

    private List<ACCVehicle> ExpandVehicles(TrafficVehicle[] vehicles)
    {
        var list = new List<ACCVehicle>();
        foreach (var v in vehicles)
        {
            list.Add(new ACCVehicle(v.position, v.speed, v.acceleration, v.size.Z, v.isTMP, v.isTrailer, v.id));
            foreach (var t in v.trailers)
            {
                list.Add(new ACCVehicle(t.position, v.speed, v.acceleration, t.size.Z, v.isTMP, true, v.id));
            }
        }
        return list;
    }

    private List<NumVec3> BuildPathPoints()
    {
        var pts = _roadPoints?.ToList() ?? new List<NumVec3>();
        if (pts.Count == 1)
        {
            var tp = _telemetry!.truckPlacement.coordinate;
            pts.Insert(0, new NumVec3((float)tp.X, (float)tp.Y, (float)tp.Z));
        }
        if (pts.Count == 2)
        {
            var p0 = pts[0];
            var p1 = pts[1];
            var interpolated = new List<NumVec3>();
            for (int i = 0; i < 10; i++)
            {
                interpolated.Add(new NumVec3(
                    p0.X + (p1.X - p0.X) * i / 9f,
                    p0.Y + (p1.Y - p0.Y) * i / 9f,
                    p0.Z + (p1.Z - p0.Z) * i / 9f));
            }
            pts = interpolated;
        }
        return pts;
    }

    private static float DistanceToPolyline(List<NumVec3> points, NumVec3 p)
    {
        float best = float.MaxValue;
        for (int i = 1; i < points.Count; i++)
        {
            var a = points[i - 1];
            var b = points[i];
            var ab = new NumVec2(b.X - a.X, b.Z - a.Z);
            var ap = new NumVec2(p.X - a.X, p.Z - a.Z);
            var denom = ab.LengthSquared();
            float t = denom > 0 ? NumVec2.Dot(ap, ab) / denom : 0;
            t = Math.Clamp(t, 0, 1);
            var proj = new NumVec2(a.X, a.Z) + ab * t;
            var d = NumVec2.Distance(proj, new NumVec2(p.X, p.Z));
            if (d < best) best = d;
        }
        return best;
    }

    private double DesiredGap(double speed, double length, bool isTmp)
    {
        var minGap = isTmp ? 5 + length / 2.0 : 5 + length * 0.8;
        var gap = Math.Max(_runtime.TimeGapSeconds * speed, minGap);
        return gap;
    }

    private ACCTrafficLight? GetLightInFront()
    {
        if (_semaphores?.semaphores is null || _telemetry is null)
            return null;

        if (_settings.TrafficLightMode == "Normal")
            return GetLightLegacy(); // acts as prefab-aware placeholder
        else
            return GetLightLegacy();
    }

    private ACCTrafficLight? GetLightLegacy()
    {
        var truckPos = _telemetry.truckPlacement.coordinate;
        var rot = _telemetry.truckPlacement.rotation.X * 360;
        if (rot < 0) rot += 360;
        var heading = Math.PI * rot / 180.0;
        var forward = new NumVec2((float)-Math.Sin(heading), (float)-Math.Cos(heading));

        ACCTrafficLight? best = null;
        float bestDist = float.MaxValue;
        foreach (var s in _semaphores.semaphores)
        {
            if (s.type != SemaphoreType.TRAFFICLIGHT) continue;
            var pos = s.position;
            var to = new NumVec2(pos.X + s.cx * 512 - (float)truckPos.X, pos.Z + s.cy * 512 - (float)truckPos.Z);
            var forwardDistance = NumVec2.Dot(forward, to);
            if (forwardDistance <= 0 || forwardDistance > 200) continue;
            var lateral = MathF.Sqrt(Math.Max(0, to.LengthSquared() - forwardDistance * forwardDistance));
            if (lateral > 11) continue;

            if (forwardDistance < bestDist)
            {
                bestDist = forwardDistance;
                best = new ACCTrafficLight(pos, s.cx, s.cy, s.rotation, s.state, forwardDistance);
            }
        }

        return best;
    }

    private ACCGate? GetGateInFront()
    {
        if (_semaphores?.semaphores is null || _telemetry is null || _settings.IgnoreGates)
            return null;

        var truckPos = _telemetry.truckPlacement.coordinate;
        var rot = _telemetry.truckPlacement.rotation.X * 360;
        if (rot < 0) rot += 360;
        var heading = Math.PI * rot / 180.0;
        var forward = new NumVec2((float)-Math.Sin(heading), (float)-Math.Cos(heading));

        ACCGate? best = null;
        float bestDist = float.MaxValue;
        foreach (var s in _semaphores.semaphores)
        {
            if (s.type != SemaphoreType.GATE) continue;
            var pos = s.position;
            var to = new NumVec2(pos.X + s.cx * 512 - (float)truckPos.X, pos.Z + s.cy * 512 - (float)truckPos.Z);
            var forwardDistance = NumVec2.Dot(forward, to);
            if (forwardDistance <= 0 || forwardDistance > 200) continue;
            var lateral = MathF.Sqrt(Math.Max(0, to.LengthSquared() - forwardDistance * forwardDistance));
            if (lateral > 11) continue;

            if (forwardDistance < bestDist)
            {
                bestDist = forwardDistance;
                best = new ACCGate(pos, s.cx, s.cy, s.rotation, s.state, forwardDistance);
            }
        }

        return best;
    }

    private double GetStopInDistance()
    {
        if (_stopIn == null || _stopIn.Count == 0)
            return double.MaxValue;
        return _stopIn.Values.Where(v => v > 0).DefaultIfEmpty(double.MaxValue).Min();
    }

    private double CalculateTargetAcceleration(double targetSpeed, ACCVehicle? inFront, ACCTrafficLight? light, ACCGate? gate, double stopIn)
    {
        var accels = new List<double>();

        // Speed limit tracking (matches Python logic)
        var speedError = targetSpeed - _telemetry!.truckFloat.speed;
        var speedAccel = speedError * 0.5;

        if (speedError * 3.6 > 10)
        {
            speedAccel = Math.Min(_runtime.MaxAccel, Math.Max(_runtime.EmergencyDecel, speedAccel));
        }
        else
        {
            speedAccel = Math.Min(_runtime.MaxAccel, Math.Max(_runtime.ComfortDecel, speedAccel));
        }

        if (_telemetry!.truckFloat.speed < targetSpeed + 5 / 3.6)
            speedAccel *= 0.75;

        if (_telemetry.truckFloat.speed > targetSpeed + 10 / 3.6)
            speedAccel *= 1.5;

        accels.Add(speedAccel);

        // Following vehicle
        if (inFront != null)
        {
            var desiredGap = DesiredGap(_telemetry.truckFloat.speed, inFront.length, inFront.isTmp);
            _runtime.DesiredGap = desiredGap;
            var relSpeed = _telemetry.truckFloat.speed - inFront.speed;
            var gapError = (inFront.Distance - desiredGap) / Math.Max(desiredGap / 30.0, 1);
            double followAccel;
            if (_telemetry.truckFloat.speed > 10 / 3.6)
                followAccel = 0.5 * gapError - 1.0 * relSpeed;
            else
                followAccel = 1.0 * gapError - 0.7 * relSpeed;

            followAccel += 0.3 * inFront.acceleration;
            followAccel = Math.Min(_runtime.MaxAccel, followAccel);
            accels.Add(followAccel);
        }

        // Stop-in distance
        if (stopIn < double.MaxValue && stopIn > 0)
        {
            accels.Add(CalculateStopAccel(stopIn, allowAccel: true));
        }

        // Traffic light
        if (light != null && !_settings.IgnoreTrafficLights)
        {
            if (light.state == (int)TrafficLightState.RED || light.state == (int)TrafficLightState.ORANGETORED)
            {
                accels.Add(CalculateStopAccel(light.distance));
            }
        }

        // Gate
        if (gate != null && !_settings.IgnoreGates)
        {
            if (gate.state < (int)GateStates.OPEN)
            {
                accels.Add(CalculateStopAccel(gate.distance));
            }
        }

        if (accels.Count == 0)
            return 0;

        return accels.Min();
    }

    private double CalculateStopAccel(double distance, bool allowAccel = false)
    {
        var speed = _telemetry!.truckFloat.speed;
        if (distance > speed * 6 && (distance > 40 || allowAccel))
            return 999;

        distance -= 5;
        if (distance <= 0)
            return _runtime.EmergencyDecel;

        var requiredDecel = (speed * speed) / (2 * distance);
        var accel = -requiredDecel * 1.2;
        if (distance < 50) accel *= 1.2;

        if (distance > 20)
            accel = Math.Max(_runtime.ComfortDecel, accel);
        else
            accel = Math.Max(_runtime.EmergencyDecel, accel);

        if (accel < 0.02 && speed < 1)
            accel = Math.Min(-1, accel);

        return accel;
    }

    public IEnumerable<PluginPage> RenderPages() => SettingsPage.Render(_settings, _runtime);

    public void OnAction(string actionId, object? value)
    {
        switch (actionId)
        {
            case AccSettingKeys.Toggle:
                if (value is bool pressed && !pressed) break; // ignore release
                _runtime.Enabled = !_runtime.Enabled;
                break;
            case AccSettingKeys.IncSpeed:
                _holdingUp = value is bool bu && bu;
                if (!_holdingUp) _lastChange = DateTime.MinValue;
                break;
            case AccSettingKeys.DecSpeed:
                _holdingDown = value is bool bd && bd;
                if (!_holdingDown) _lastChange = DateTime.MinValue;
                break;
            case "toggle_enable":
                _runtime.Enabled = value is bool en && en;
                break;
            case "set_agg":
                if (value is string agg) _settings.Aggressiveness = agg;
                ApplyAggressiveness();
                break;
            case "set_follow_dist":
                if (value is double fd) _settings.FollowingDistance = fd;
                ApplyAggressiveness();
                break;
            case "set_ignore_gates":
                if (value is bool ig) _settings.IgnoreGates = ig;
                break;
            case "set_ignore_lights":
                if (value is bool il) _settings.IgnoreTrafficLights = il;
                break;
            case "set_tl_mode":
                if (value is string tl) _settings.TrafficLightMode = tl;
                break;
            case "set_mu":
                if (value is double mu) _settings.Mu = mu;
                break;
            case "set_ignore_speed":
                if (value is bool ispeed) _settings.IgnoreSpeedLimit = ispeed;
                break;
            case "set_offset_type":
                if (value is string ot) _settings.SpeedOffsetType = ot;
                break;
            case "set_offset":
                if (value is double off) _settings.SpeedOffset = off;
                break;
            case "set_max_speed":
                if (double.TryParse(value?.ToString(), out var ms)) _settings.MaxSpeed = ms;
                break;
            case "set_overwrite_speed":
                if (double.TryParse(value?.ToString(), out var os)) _settings.OverwriteSpeed = os;
                break;
            case "set_debug":
                if (value is bool dbg) _settings.Debug = dbg;
                break;
            case "set_unlock_pid":
                if (value is bool unlock) _settings.UnlockPid = unlock;
                break;
            case "set_kp":
                if (value is double kp) _settings.PidKp = kp;
                break;
            case "set_ki":
                if (value is double ki) _settings.PidKi = ki;
                break;
            case "set_kd":
                if (value is double kd) _settings.PidKd = kd;
                break;
        }
    }

    private void ApplyAggressiveness()
    {
        _runtime.TimeGapSeconds = _settings.FollowingDistance;
        _runtime.MaxAccel = _runtime.BaseMaxAccel;
        _runtime.ComfortDecel = _runtime.BaseComfortDecel;
        _runtime.EmergencyDecel = _runtime.BaseEmergencyDecel;

        if (_settings.Aggressiveness == "Aggressive")
        {
            _runtime.MaxAccel = _runtime.BaseMaxAccel * 2;
            _runtime.ComfortDecel = _runtime.BaseComfortDecel * 2;
            _runtime.TimeGapSeconds = _runtime.TimeGapSeconds * 0.75;
        }
        else if (_settings.Aggressiveness == "Eco")
        {
            _runtime.MaxAccel = _runtime.BaseMaxAccel * 0.66;
            _runtime.ComfortDecel = _runtime.BaseComfortDecel * 0.66;
            _runtime.TimeGapSeconds = _runtime.TimeGapSeconds * 1.25;
        }
    }

    private static NumVec3 ToVector3(Vector3Double v) => new((float)v.X, (float)v.Y, (float)v.Z);

    private void Notify(string message)
    {
        Logger.Info($"[ACC] {message}");
    }
}

public class AccRuntime
{
    public bool Enabled { get; set; } = false;
    public double TargetSpeedKph { get; set; }
    public double SpeedKph { get; set; }
    public double CurrentAccel { get; set; }
    public double TargetAccel { get; set; }
    public double LastSpeed { get; set; }
    public double ManualSpeedOffset { get; set; }
    public double LeadDistance { get; set; }
    public double DesiredGap { get; set; }
    public double TimeGapSeconds { get; set; } = 2.0;

    public double BaseMaxAccel { get; set; } = 3.0;
    public double BaseComfortDecel { get; set; } = -2.0;
    public double BaseEmergencyDecel { get; set; } = -6.0;

    public double MaxAccel { get; set; } = 3.0;
    public double ComfortDecel { get; set; } = -2.0;
    public double EmergencyDecel { get; set; } = -6.0;

    public void Reset()
    {
        ManualSpeedOffset = 0;
        TargetAccel = 0;
        TargetSpeedKph = 0;
    }
}
