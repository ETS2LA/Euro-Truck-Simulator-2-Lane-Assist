namespace ETS2LA.Audio;

class AudioJob
{
    public string Filename { get; }
    public Func<bool>? LoopCondition { get; }
    public int LoopCount { get; }

    public AudioJob(string filename, Func<bool>? condition, int loopCount)
    {
        Filename = filename;
        LoopCondition = condition;
        LoopCount = loopCount;
    }
}