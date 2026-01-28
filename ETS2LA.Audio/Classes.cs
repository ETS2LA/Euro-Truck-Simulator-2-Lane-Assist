namespace ETS2LA.Audio;

class AudioJob
{
    public string Filename { get; }
    public bool Loop { get; }
    public Func<bool>? LoopCondition { get; }
    public int LoopCount { get; }

    public AudioJob(string filename, bool loop, Func<bool>? condition, int loopCount)
    {
        Filename = filename;
        Loop = loop;
        LoopCondition = condition;
        LoopCount = loopCount;
    }
}