using Avalonia.Controls;
using ETS2LA.ML;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using Avalonia.Markup.Xaml;

namespace ETS2LA.UI.Views.Settings;

public partial class ExperimentsSettings : UserControl, INotifyPropertyChanged
{

    public bool RenderVisionCamerasRequiresRestart { get; set; } = false;

    public bool RenderVisionCameras
    {
        get => MLSettings.Current.RenderVisionCameras;
        set
        {
            if (MLSettings.Current.RenderVisionCameras != value)
            {
                MLSettings.Current.RenderVisionCameras = value;
                MLSettings.Current.Save();
                RenderVisionCamerasRequiresRestart = !RenderVisionCamerasRequiresRestart;
                OnPropertyChanged(nameof(RenderVisionCamerasRequiresRestart));
            }
            OnPropertyChanged(nameof(RenderVisionCameras));
        }
    }

    public ExperimentsSettings()
    {
        InitializeComponent();

        AvaloniaXamlLoader.Load(this);
        DataContext = this;
    }

    public new event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}