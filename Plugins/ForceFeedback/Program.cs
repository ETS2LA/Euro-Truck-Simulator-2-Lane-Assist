using ETS2LA.Shared;
using ETS2LA.Logging;
using Windows.Gaming.Input;
using Windows.Gaming.Input.ForceFeedback;

// FF listens to "ForceFeedback.Output" bus event for float values between -1.0 and 1.0.
// If you want to use this plugin then make sure you send those events in addition to normal output.
// Example: _bus.Publish<float>("ForceFeedback.Output", steeringValue);

namespace ForceFeedback
{

    public class WheelInformation
    {
        public required RacingWheel Wheel;
        public required ConstantForceEffect Effect;
        public bool IsLowPower = true;

        private bool _isEffectSet = false;
        private float _last = 0;
        private float _lastError = 0;
        private const float Kp = 5f;
        private const float Kd = 15f;

        public void UpdateToAngle(float targetAngle)
        {
            var motor = Wheel.WheelMotor;
            if (motor == null) return;

            var reading = Wheel.GetCurrentReading();
            float currentAngle = (float)reading.Wheel; // -1.0 to 1.0

            float error = targetAngle - currentAngle;
            float derivative = error - _lastError;
            float force = error * Kp + derivative * Kd;
            _lastError = error;

            force = Math.Clamp(force, -1.0f, 1.0f);
            force = _last * 0.8f + force * 0.2f;
            _last = force;

            // Clamp force to make sure weak forces go through on lower end
            // hardware. A G29 for example seems to fully ignore forces below ~0.1.
            if (IsLowPower)
            {
                if(force < 0.20f && force > -0.20f)
                {
                    if(force > 0.06f && force < 0.20f)
                        force = 0.20f;
                    else if(force < -0.06f && force > -0.20f)
                        force = -0.20f;
                }
            }

            if (_isEffectSet && motor.IsEnabled)
            {
                Effect.Stop();
                Effect.SetParameters(new System.Numerics.Vector3(force, 0, 0), TimeSpan.FromMilliseconds(100));
                Effect.Start();
            }
            else if (!_isEffectSet)
            {
                InitializeEffect();
            }
        }

        public async void InitializeEffect()
        {
            if (Wheel.WheelMotor == null) return;

            var motor = Wheel.WheelMotor;
            var status = await motor.LoadEffectAsync(Effect);
            
            if (status == ForceFeedbackLoadEffectResult.Succeeded)
            {
                _isEffectSet = true;
            }
            else
            {
                Logger.Error($"Failed to load effect: {status} for wheel {Wheel.GetHashCode()}");
            }
        }

        public void StopEffect()
        {
            try { Effect.Stop(); } 
            catch (Exception) {}
        }
    }

    public class ForceFeedback : Plugin
    {
        public override float TickRate => 60f;
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Force Feedback",
            Description = "Provides force feedback effects for compatible steering wheels.",
            AuthorName = "Tumppi066",
        };

        private List<WheelInformation> _wheels = new List<WheelInformation>();
        public float TargetAngle = 0;

        private void RemoveWheel(RacingWheel wheel)
        {
            foreach (var wheelInfo in _wheels)
            {
                if (wheelInfo.Wheel == wheel)
                {
                    wheelInfo.StopEffect();
                    _wheels.Remove(wheelInfo);
                    break;
                }
            }
            Logger.Info($"Removed wheel for force feedback: {wheel.GetHashCode()}");
        }

        private void AddWheel(RacingWheel wheel)
        {
            _wheels.Add(new WheelInformation
            {
                Wheel = wheel,
                Effect = new ConstantForceEffect()
            });
            _wheels.Last().InitializeEffect();
            Logger.Info($"Added wheel for force feedback: {wheel.GetHashCode()}");
        }

        public override void Init()
        {
            base.Init();

            RacingWheel.RacingWheelAdded += (sender, wheel) => {
                AddWheel(wheel);
            };
                RacingWheel.RacingWheelRemoved += (sender, wheel) => {
                RemoveWheel(wheel);
            };

            // some wheels are already connected
            var wheels = RacingWheel.RacingWheels;
            Logger.Info($"Found {wheels.Count} connected racing wheels.");
            foreach (var wheel in wheels)
            {
                AddWheel(wheel);
            }
        }

        public override void OnEnable()
        {
            base.OnEnable();
            _bus?.Subscribe<float>("ForceFeedback.Output", OnControlEvent);
        }

        public override void OnDisable()
        {
            base.OnDisable();
            _bus?.Unsubscribe<float>("ForceFeedback.Output", OnControlEvent);
            _window?.CloseNotification("ForceFeedback.Debug");
            foreach (var wheelInfo in _wheels)
            {
                wheelInfo.StopEffect();
            }
        }

        public void OnControlEvent(float steering)
        {
            TargetAngle = steering;
        }

        public override void Tick()
        {
            foreach (var wheelInfo in _wheels)
            {
                wheelInfo.UpdateToAngle(TargetAngle);
            }
        }
    }
}