using System;

namespace AdaptiveCruiseControl;

/// <summary>
/// Simple exponential smoothing helper to approximate the Python SmoothedValue.
/// </summary>
public class SmoothedValue
{
    private readonly double _timeConstantSeconds;
    private double _value;
    private bool _initialized;
    private DateTime _lastUpdate = DateTime.UtcNow;

    public SmoothedValue(double timeConstantSeconds, double initial = 0)
    {
        _timeConstantSeconds = timeConstantSeconds;
        _value = initial;
        _initialized = false;
    }

    public double Update(double newValue)
    {
        var now = DateTime.UtcNow;
        var dt = (now - _lastUpdate).TotalSeconds;
        _lastUpdate = now;

        if (!_initialized || dt <= 0 || dt > 1.0)
        {
            _value = newValue;
            _initialized = true;
            return _value;
        }

        var alpha = Math.Clamp(dt / (_timeConstantSeconds + dt), 0, 1);
        _value = alpha * newValue + (1 - alpha) * _value;
        return _value;
    }

    public double Get() => _value;
}
