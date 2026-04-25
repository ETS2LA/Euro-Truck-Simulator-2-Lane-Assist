using System;
using System.Collections.Generic;

namespace AdaptiveCruiseControl;

public class PidController
{
    private double _kp;
    private double _ki;
    private double _kd;
    private readonly List<double> _integral = new();
    private double _lastError;
    private double _lastOutput;
    private double _lastTime;
    private readonly List<double> _history = new();

    public double OutputSmoothingFactor { get; set; } = 0.6; // 0..1
    public double SampleTime { get; set; } = 0.05; // seconds

    public PidController(double kp, double ki, double kd)
    {
        _kp = kp;
        _ki = ki;
        _kd = kd;
        _lastTime = GetTime();
    }

    public void UpdateGains(double kp, double ki, double kd)
    {
        _kp = kp;
        _ki = ki;
        _kd = kd;
    }

    public double Compute(double targetAccel, double currentAccel, double speed, double speedLimit)
    {
        var now = GetTime();
        var dt = now - _lastTime;
        if (dt <= 0 || dt > 0.5)
            dt = SampleTime;

        var error = targetAccel - currentAccel;

        if (error * dt > 0)
        {
            // Prevent runaway integral when fully throttled; caller should cap inputs.
            _integral.Add(error * dt);
        }
        else
        {
            if (_integral.Count != 0 && _integral[0] > 0)
                _integral.RemoveAt(0);
            _integral.Add(error * dt);
        }

        // Trim integral when overspeeding.
        if (speedLimit > 0 && speed > speedLimit && _integral.Count > 5)
        {
            var overshoot = (int)Math.Round((speed - speedLimit) * 3.6);
            _integral.RemoveRange(0, Math.Min(_integral.Count, Math.Max(1, overshoot) * 2));
        }

        // Reset integral near standstill to avoid jump.
        if (speed < 10 / 3.6)
        {
            _integral.Clear();
            _integral.Add(0);
        }

        var sum = 0d;
        foreach (var v in _integral) sum += v;
        var p = _kp * error;
        var i = _ki * sum;
        var d = dt > 0 ? _kd * (error - _lastError) / dt : 0;

        var raw = p + i + d;
        _history.Add(raw);
        if (_history.Count > 200) _history.RemoveAt(0);
        var smoothed = (1 - OutputSmoothingFactor) * _lastOutput + OutputSmoothingFactor * raw;
        smoothed = Math.Clamp(smoothed, -1.0, 1.0);

        _lastError = error;
        _lastOutput = smoothed;
        _lastTime = now;

        return smoothed;
    }

    public void Reset()
    {
        _integral.Clear();
        _history.Clear();
        _lastOutput = 0;
        _lastError = 0;
        _lastTime = GetTime();
    }

    private static double GetTime() => DateTimeOffset.Now.ToUnixTimeMilliseconds() / 1000.0;
}
