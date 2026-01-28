using System.Collections.Concurrent;
using ETS2LA.Logging;
using NAudio.Wave;

namespace ETS2LA.Audio;

public class AudioHandler
{
    private static readonly Lazy<AudioHandler> _instance = new(() => new AudioHandler());
    public static AudioHandler Current => _instance.Value;

    private readonly ConcurrentQueue<AudioJob> _queue = new();
    private CancellationTokenSource? _currentCts;
    private bool _isRunning = true;

    private AudioHandler()
    {
        Task.Run(ProcessAudioQueue);
    }

    public void Queue(string filename, bool overrideCurrent = false, int loopCount = 1)
    {
        if (overrideCurrent)
        {
            while (_queue.TryDequeue(out _)) { }
            
            _currentCts?.Cancel();
        }

        _queue.Enqueue(new AudioJob(filename, false, null, loopCount));
    }

    public void Queue(string filename, Func<bool> loopCondition, int loopCount)
    {
         _queue.Enqueue(new AudioJob(filename, true, loopCondition, loopCount));
    }

    private async Task ProcessAudioQueue()
    {
        while (_isRunning)
        {
            if (_queue.TryDequeue(out var job))
            {
                _currentCts = new CancellationTokenSource();
                try 
                {
                    if (job.Loop)
                    {
                        while ((job.LoopCondition?.Invoke() ?? false) && !_currentCts.Token.IsCancellationRequested)
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
            else
            {
                await Task.Delay(50);
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

    public void Shutdown()
    {
        _isRunning = false;
        _currentCts?.Cancel();
    }
}
