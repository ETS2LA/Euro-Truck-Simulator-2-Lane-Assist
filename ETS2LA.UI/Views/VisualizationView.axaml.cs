using Avalonia.Controls;
using ETS2LA.UI.Services;
using WebViewControl;

namespace ETS2LA.UI.Views;

public partial class VisualizationView : UserControl
{
    private readonly PluginManagerService? _pluginService;

    public VisualizationView(PluginManagerService? service = null)
    {
        InitializeComponent();
        _pluginService = service;
    }
}
