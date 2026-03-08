using Avalonia.Controls;
namespace ETS2LA.UI.Views;

public partial class VisualizationView : UserControl
{
    public VisualizationView()
    {
        // This file should never be accessed outside of Windows systems,
        // but we might as well guard against it just in case.
        # if WINDOWS
        InitializeComponent();
        # endif
    }
}
