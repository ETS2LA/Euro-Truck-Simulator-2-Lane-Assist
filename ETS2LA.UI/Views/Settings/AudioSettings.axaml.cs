using ETS2LA.Audio;
using Avalonia.Controls;

namespace ETS2LA.UI.Views.Settings;

public partial class AudioSettings : UserControl
{
    private AudioHandler _audioHandler;

    public AudioSettings()
    {
        InitializeComponent();
        _audioHandler = AudioHandler.Current;
        VolumeSlider.Value = _audioHandler.GetVolume() * 100.0;
    }

    private void OnVolumeChanged(object? sender, Avalonia.Controls.Primitives.RangeBaseValueChangedEventArgs e)
    {
        float volume = (float)(e.NewValue / 100.0);
        _audioHandler.SetVolume(volume);
    }
}
