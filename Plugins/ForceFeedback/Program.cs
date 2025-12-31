using ETS2LA.Shared;
using ETS2LA.Logging;
using Windows.Gaming.Input;
using Windows.Gaming.Input.ForceFeedback;

namespace ForceFeedback
{
    public class ForceFeedback : Plugin
    {
        public override float TickRate => 60f;
        public override PluginInformation Info => new PluginInformation
        {
            Name = "Force Feedback",
            Description = "Provides force feedback effects for compatible steering wheels.",
            AuthorName = "Tumppi066",
        };

        private List<RacingWheel> _wheels = new List<RacingWheel>();
        
        // Map wheels to their loaded effects to avoid reloading every tick
        private Dictionary<RacingWheel, ConstantForceEffect> _activeEffects = new Dictionary<RacingWheel, ConstantForceEffect>();

        public double TargetAngle = 0; // Normalized -1.0 to 1.0
        public double StartAngle = 0.0;
        public DateTime LastUpdate = DateTime.MinValue;

        private const float Kp = 5f;
        private const float Kd = 15f;
        private double _lastError = 0;
        private float _last = 0;

        private void RemoveWheel(RacingWheel wheel)
        {
            if (_activeEffects.TryGetValue(wheel, out var effect))
            {
                effect.Stop();
                _activeEffects.Remove(wheel);
            }
            _wheels.Remove(wheel);
            Logger.Info($"Removed wheel for force feedback: {wheel.GetHashCode()}");
        }

        private void AddWheel(RacingWheel wheel)
        {
            Logger.Info($"Adding wheel for force feedback: {wheel.GetHashCode()}");
            _wheels.Add(wheel);
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
            foreach (var effect in _activeEffects.Values)
            {
                effect.Stop();
            }
        }

        public void OnControlEvent(float steering)
        {
            // steering is usually -1.0 to 1.0
            TargetAngle = steering;
        }

        public override void Tick()
        {
            // if ((DateTime.Now - LastUpdate).TotalSeconds >= 3)
            // {
            //     Random rand = new Random();
            //     StartAngle = TargetAngle;
            //     TargetAngle = rand.NextDouble() * 2.0 - 1.0; // Random value between -1.0 and 1.0
            //     LastUpdate = DateTime.Now;
            // }

            foreach (var wheel in _wheels)
            {
                var motor = wheel.WheelMotor;
                if (motor == null) continue;

                var reading = wheel.GetCurrentReading();
                double currentAngle = reading.Wheel; // Usually -1.0 to 1.0

                // PD
                double error = TargetAngle - currentAngle;
                double derivative = error - _lastError;
                float force = (float)(error * Kp + derivative * Kd);
                _lastError = error;

                force = Math.Clamp(force, -1.0f, 1.0f);
                force = _last * 0.8f + force * 0.2f;
                _last = force;

                _window?.SendNotification(new Notification
                {
                    Id = "ForceFeedback.Debug",
                    Title = "Force Feedback Debug",
                    // pad these values to avoid flickering
                    Content = $"{Math.Round(force * 100)}% pwr, {Math.Round(Math.Abs((currentAngle - TargetAngle) * 450))}° error",
                    IsProgressIndeterminate = false,
                    CloseAfter = 0
                });

                if(force < 0.20f && force > -0.20f)
                {
                    // Clamp force to make sure weak forces go through
                    if(force > 0.06f && force < 0.20f)
                        force = 0.20f;
                    else if(force < -0.06f && force > -0.20f)
                        force = -0.20f;
                }

                // 4. Update the effect
                if (_activeEffects.TryGetValue(wheel, out var effect))
                {
                    if (motor.IsEnabled)
                    {
                        // Vector3.X is usually the primary axis for steering wheels
                        effect.Stop();
                        effect.SetParameters(new System.Numerics.Vector3(force, 0, 0), TimeSpan.FromMilliseconds(100));
                        effect.Start();
                    }
                }
                else
                {
                    // Initialize effect for this wheel if not already done
                    InitializeEffectForWheel(wheel);
                }
            }
        }

        private async void InitializeEffectForWheel(RacingWheel wheel)
        {
            if (wheel.WheelMotor == null) return;

            var motor = wheel.WheelMotor;
            var effect = new ConstantForceEffect();
            
            // Load the effect onto the motor hardware
            var status = await motor.LoadEffectAsync(effect);
            
            if (status == ForceFeedbackLoadEffectResult.Succeeded)
            {
                _activeEffects[wheel] = effect;
                Logger.Info("Force Feedback effect loaded successfully.");
            }
            else
            {
                Logger.Error($"Failed to load effect: {status}");
            }
        }
    }
}