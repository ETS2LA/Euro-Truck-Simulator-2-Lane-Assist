using ETS2LA.Shared;
using ETS2LA.Logging;
using SharpDX.DirectInput;
using System.Diagnostics;
using System.Runtime.InteropServices;

// FF listens to "ForceFeedback.Output" bus event for float values between -1.0 and 1.0.
// If you want to use this plugin then make sure you send those events in addition to normal output.
// Example: _bus.Publish<float>("ForceFeedback.Output", steeringValue);

namespace ForceFeedback
{
    public class WheelDevice
    {
        public required Joystick Joystick;
        public required DeviceInstance DeviceInfo;
        public EffectInfo? ConstantForceInfo;
        public Effect? ConstantForceEffect;
        public bool IsInitialized = false;
        public bool IsLowPower = true;

        private readonly object _lock = new object();
        private float _last = 0;
        private float _lastError = 0;
        // PID controller gains - tuned for responsive steering
        private const float Kp = 8f;
        private const float Ki = 0.5f;
        private const float Kd = 3f;
        
        private float _integralError = 0;
        private const float MaxIntegral = 0.5f;

        // Cached effect parameters to reduce GC pressure (reused every tick)
        private EffectParameters? _cachedEffectParams;
        private ConstantForce _cachedConstantForce = new ConstantForce();

        public void UpdateToAngle(float targetAngle)
        {
            lock (_lock)
            {
                if (!IsInitialized || ConstantForceEffect == null) return;

                try
                {
                    var state = Joystick.GetCurrentState();
                    // X axis is typically the steering wheel, normalized to -1.0 to 1.0
                    float currentAngle = (state.X - 32767.5f) / 32767.5f;

                    float error = targetAngle - currentAngle;
                    
                    // Integral term 
                    _integralError += error;
                    _integralError = Math.Clamp(_integralError, -MaxIntegral, MaxIntegral);
                    if (Math.Sign(error) != Math.Sign(_lastError) || Math.Abs(error) < 0.02f)
                    {
                        _integralError *= 0.5f;
                    }
                    
                    // PID calculation
                    float derivative = error - _lastError;
                    _lastError = error;
                    float force = error * Kp + _integralError * Ki + derivative * Kd;
                    force = Math.Clamp(force, -1.0f, 1.0f);
                    force = _last * 0.3f + force * 0.7f;
                    _last = force;

                    // Boost weak forces to overcome static friction on some wheels
                    if (IsLowPower && Math.Abs(force) > 0.03f && Math.Abs(force) < 0.15f)
                    {
                        force = Math.Sign(force) * 0.15f;
                    }

                    // DirectInput force is in the range -10000 to 10000
                    int diForce = (int)(force * 10000);

                    // Initialize cached params on first use
                    if (_cachedEffectParams == null)
                    {
                        _cachedEffectParams = new EffectParameters
                        {
                            Flags = EffectFlags.Cartesian | EffectFlags.ObjectOffsets,
                            Duration = int.MaxValue,
                            Gain = 10000,
                            SamplePeriod = 0,
                            TriggerButton = -1,
                            TriggerRepeatInterval = 0,
                            StartDelay = 0
                        };
                        _cachedEffectParams.SetAxes(new int[] { 0 }, new int[] { 0 });
                    }

                    // Update only the magnitude (reuse cached objects)
                    _cachedConstantForce.Magnitude = diForce;
                    _cachedEffectParams.Parameters = _cachedConstantForce;
                    ConstantForceEffect.SetParameters(_cachedEffectParams, EffectParameterFlags.TypeSpecificParameters);
                }
                catch (Exception ex)
                {
                    Logger.Warn($"Error updating force feedback: {ex.Message}");
                }
            }
        }

        public void InitializeEffect()
        {
            try
            {
                // Find constant force effect
                var effects = Joystick.GetEffects();
                foreach (var effectInfo in effects)
                {
                    if (effectInfo.Guid == EffectGuid.ConstantForce)
                    {
                        ConstantForceInfo = effectInfo;
                        break;
                    }
                }

                if (ConstantForceInfo == null)
                {
                    Logger.Warn($"No constant force effect found for {DeviceInfo.InstanceName}");
                    return;
                }

                // Create the effect parameters
                var constantForce = new ConstantForce { Magnitude = 0 };

                var effectParams = new EffectParameters
                {
                    Flags = EffectFlags.Cartesian | EffectFlags.ObjectOffsets,
                    Duration = int.MaxValue,
                    SamplePeriod = 0,
                    Gain = 10000,
                    TriggerButton = -1,
                    TriggerRepeatInterval = 0,
                    StartDelay = 0
                };

                // Set axes - typically just X for steering
                effectParams.SetAxes(new int[] { 0 }, new int[] { 0 });
                effectParams.Parameters = constantForce;

                // Create and start the effect
                ConstantForceEffect = new Effect(Joystick, EffectGuid.ConstantForce, effectParams);
                ConstantForceEffect.Start();

                IsInitialized = true;
                Logger.Success($"Initialized force feedback for {DeviceInfo.InstanceName}");
            }
            catch (Exception ex)
            {
                Logger.Error($"Failed to initialize force feedback for {DeviceInfo.InstanceName}: {ex.Message}");
                IsInitialized = false;
            }
        }

        public void StopEffect()
        {
            lock (_lock)
            {
                try
                {
                    IsInitialized = false; // Set first to prevent UpdateToAngle from using effect
                    ConstantForceEffect?.Stop();
                    ConstantForceEffect?.Dispose();
                    ConstantForceEffect = null;
                }
                catch (Exception) { }
            }
        }

        public void Dispose()
        {
            StopEffect();
            try
            {
                Joystick?.Unacquire();
                Joystick?.Dispose();
            }
            catch (Exception) { }
        }
    }

    public class ForceFeedback : Plugin
    {
        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        private static extern IntPtr GetDesktopWindow();

        public override float TickRate => 60f;
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Force Feedback",
            Description = "Provides force feedback effects for compatible steering wheels (Moza, Logitech, Thrustmaster, Fanatec, etc.).",
            AuthorName = "Tumppi066",
        };

        private DirectInput? _directInput;
        private List<WheelDevice> _wheels = new List<WheelDevice>();
        public float TargetAngle = 0;
        private IntPtr _windowHandle = IntPtr.Zero;

        private IntPtr GetWindowHandle()
        {
            // Try to get the main window handle of the current process
            var process = Process.GetCurrentProcess();
            if (process.MainWindowHandle != IntPtr.Zero)
            {
                return process.MainWindowHandle;
            }
            
            // Fallback to foreground window
            var fg = GetForegroundWindow();
            if (fg != IntPtr.Zero)
            {
                return fg;
            }
            
            // Cannot use desktop window for exclusive access - return zero to indicate failure
            Logger.Warn("No valid window handle found for force feedback. Will retry on next scan.");
            return IntPtr.Zero;
        }

        private void ScanForWheels()
        {
            if (_directInput == null)
            {
                Logger.Error("DirectInput is null, cannot scan for wheels");
                return;
            }

            try
            {
                // First, list ALL devices to see what's available
                var allDevices = _directInput.GetDevices(DeviceClass.GameControl, DeviceEnumerationFlags.AllDevices);
                Logger.Info($"Found {allDevices.Count} total game control devices.");
                foreach (var dev in allDevices)
                {
                    Logger.Info($"  Device: {dev.InstanceName} ({dev.ProductName}) - Type: {dev.Type}");
                }

                // Get all game controllers and driving devices with force feedback
                var devices = _directInput.GetDevices(DeviceClass.GameControl, DeviceEnumerationFlags.ForceFeedback);

                Logger.Info($"Found {devices.Count} force feedback capable devices.");

                foreach (var deviceInstance in devices)
                {
                    // Check if we already have this device
                    bool alreadyAdded = _wheels.Any(w => w.DeviceInfo.InstanceGuid == deviceInstance.InstanceGuid);
                    if (alreadyAdded) continue;

                    Joystick? joystick = null;
                    try
                    {
                        joystick = new Joystick(_directInput, deviceInstance.InstanceGuid);
                        
                        // Get window handle for exclusive access (required for force feedback on some devices)
                        if (_windowHandle == IntPtr.Zero)
                        {
                            _windowHandle = GetWindowHandle();
                            if (_windowHandle == IntPtr.Zero)
                            {
                                Logger.Warn("Cannot initialize force feedback: no valid window handle available.");
                                joystick.Dispose();
                                continue;
                            }
                            Logger.Info($"Using window handle: {_windowHandle}");
                        }
                        
                        // Set cooperative level - exclusive access is required for force feedback
                        joystick.SetCooperativeLevel(_windowHandle, CooperativeLevel.Background | CooperativeLevel.Exclusive);
                        
                        joystick.Acquire();

                        // Disable auto-center spring
                        try
                        {
                            joystick.Properties.AutoCenter = false;
                        }
                        catch (Exception) { /* Some devices don't support this */ }

                        var wheel = new WheelDevice
                        {
                            Joystick = joystick,
                            DeviceInfo = deviceInstance
                        };

                        wheel.InitializeEffect();
                        _wheels.Add(wheel);
                        joystick = null; // Prevent disposal in finally block - wheel now owns it

                        Logger.Info($"Added wheel: {deviceInstance.InstanceName} ({deviceInstance.ProductName})");
                    }
                    catch (Exception ex)
                    {
                        Logger.Warn($"Could not add device {deviceInstance.InstanceName}: {ex.Message}");
                    }
                    finally
                    {
                        // Dispose joystick if it wasn't successfully added to a wheel
                        joystick?.Dispose();
                    }
                }
            }
            catch (Exception ex)
            {
                Logger.Error($"Error scanning for wheels: {ex.Message}");
            }
        }

        public override void Init()
        {
            base.Init();
            Logger.Info("ForceFeedback plugin Init() called");

            try
            {
                _directInput = new DirectInput();
                Logger.Info("DirectInput created successfully");
                ScanForWheels();
            }
            catch (Exception ex)
            {
                Logger.Error($"Failed to initialize DirectInput: {ex.Message}");
                Logger.Error(ex.ToString());
            }
        }

        public override void OnEnable()
        {
            base.OnEnable();
            Logger.Info("ForceFeedback plugin OnEnable() called");
            _bus?.Subscribe<float>("ForceFeedback.Output", OnControlEvent);

            // Re-scan for wheels in case new ones were connected
            ScanForWheels();
        }

        public override void OnDisable()
        {
            base.OnDisable();
            _bus?.Unsubscribe<float>("ForceFeedback.Output", OnControlEvent);
            _window?.CloseNotification("ForceFeedback.Debug");

            // Properly dispose all resources
            DisposeResources();
        }

        public void OnControlEvent(float steering)
        {
            TargetAngle = steering;
        }

        public override void Tick()
        {
            foreach (var wheel in _wheels)
            {
                wheel.UpdateToAngle(TargetAngle);
            }
        }

        private void DisposeResources()
        {
            foreach (var wheel in _wheels)
            {
                wheel.Dispose();
            }
            _wheels.Clear();
            _directInput?.Dispose();
            _directInput = null;
            _windowHandle = IntPtr.Zero; // Reset for potential re-initialization
        }
    }
}