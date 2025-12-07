using Avalonia.Controls;
using ETS2LA.Shared;
using ETS2LA.UI.Rendering;

namespace ETS2LA.UI.Views;

public partial class PluginUiWindow : Window
{
    public PluginUiWindow()
    {
        InitializeComponent();
    }

    public void LoadPage(PluginPage page, IPluginUi handler)
    {
        Title = $"{page.Title} - Plugin";
        if (this.FindControl<StackPanel>("Root") is { } root)
        {
            root.Children.Clear();
            root.Children.Add(PluginUiRenderer.RenderPage(page, handler));
        }
    }
}
