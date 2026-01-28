using System.Collections.Concurrent;
using ETS2LA.Logging;
using ETS2LA.Settings;
using NAudio.Wave;

namespace ETS2LA.Audio;

public class AudioHandler
{
    private static readonly Lazy<AudioHandler> _instance = new(() => new AudioHandler());
    public static AudioHandler Current => _instance.Value;

    private readonly ConcurrentQueue<AudioJob> _queue = new();
    private CancellationTokenSource? _currentCts;
    private bool _isRunning = true;

    private SettingsHandler _settingsHandler;
    private AudioSettings _settings;

    private AudioHandler()
    {
        _settingsHandler = new SettingsHandler();
        _settings = _settingsHandler.Load<AudioSettings>("AudioSettings.json");
        _settingsHandler.RegisterListener<AudioSettings>("AudioSettings.json", OnSettingsChanged);
        Task.Run(ProcessAudioQueue);
    }

    /// <summary>
    ///  Set the current audio volume.
    /// </summary>
    /// <param name="volume">from 0.0f to 1.0f</param>
    public void SetVolume(float volume)
    {
        _settings.Volume = volume;
    }

    /// <summary>
    ///  Get the current audio volume.
    /// </summary>
    public float GetVolume()
    {
        return _settings.Volume;
    }

    /// <summary>
    ///  Queue an audio file for playback.
    /// </summary>
    /// <param name="filepath">Filepath of the audio file to play.</param>
    /// <param name="overrideCurrent">Whether playing this audio should override the currently playing audio (and queue).</param>
    /// <param name="loopCount">How many times this file should be played.</param>
    public void Queue(string filepath, bool overrideCurrent = false, int loopCount = 1)
    {
        if (overrideCurrent)
        {
            while (_queue.TryDequeue(out _)) { }
            
            _currentCts?.Cancel();
        }

        _queue.Enqueue(new AudioJob(filepath, null, loopCount));
    }

    /// <summary>
    ///  Queue an audio file for playback with a loop condition.
    /// </summary>
    /// <param name="filepath">The filepath of the audio file to play.</param>
    /// <param name="loopCondition">The condition under which the audio should loop. (function with bool return)</param>
    public void Queue(string filepath, Func<bool> loopCondition)
    {
         _queue.Enqueue(new AudioJob(filepath, loopCondition, 1));
    }

    private async Task ProcessAudioQueue()
    {
        while (_isRunning)
        {
            if (!_queue.TryDequeue(out var job))
            {
                await Task.Delay(50);
                continue;
            }

            _currentCts = new CancellationTokenSource();
            try 
            {
                if (job.LoopCondition != null)
                {
                    var conditionMet = job.LoopCondition.Invoke();
                    while (conditionMet && !_currentCts.Token.IsCancellationRequested)
                    {
                        await PlaySound(job, _currentCts.Token);
                    }
                }
                else
                {
                    for (int i = 0; i < job.LoopCount; i++)
                    {
                        if (_currentCts.Token.IsCancellationRequested) break;
                        await PlaySound(job, _currentCts.Token);
                    }
                }
            }
            catch (OperationCanceledException)
            {
                Logger.Info("Audio playback canceled");
            }
            finally 
            {
                _currentCts.Dispose();
                _currentCts = null;
            }
        }
    }

    private async Task PlaySound(AudioJob job, CancellationToken token)
    {
        if (token.IsCancellationRequested) return;
        Logger.Info($"Playing sound: {job.Filename}");
        using(var audioFile = new AudioFileReader(job.Filename))
        using(var outputDevice = new WaveOutEvent())
        {
            outputDevice.Init(audioFile);
            outputDevice.Volume = _settings.Volume;
            outputDevice.Play();
            while (!token.IsCancellationRequested && outputDevice.PlaybackState == PlaybackState.Playing)
            {
                await Task.Delay(100, token);
            }
            if (token.IsCancellationRequested)
            {
                outputDevice.Stop();
            }
        }
    }

    private void OnSettingsChanged(AudioSettings audioSettings)
    {
        _settings = audioSettings;
    }

    public void Shutdown()
    {
        _isRunning = false;
        _currentCts?.Cancel();
        _settingsHandler.Save<AudioSettings>("AudioSettings.json", _settings);
    }
}
