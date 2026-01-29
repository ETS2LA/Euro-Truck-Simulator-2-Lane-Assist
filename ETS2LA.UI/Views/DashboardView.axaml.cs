using System.Reflection;
using Avalonia.Controls;
using Avalonia.Markup.Xaml.MarkupExtensions;
using ETS2LA.Logging;

namespace ETS2LA.UI.Views;

public partial class DashboardView : UserControl
{

    public string CurrentRelease { get; set; } = "Unknown";
    public int UsersOnline { get; set; } = 123;
    public int UsersOver24h { get; set; } = 456;

    public DashboardView()
    {
        CurrentRelease = $"v{Assembly.GetEntryAssembly()?.GetName().Version?.ToString(3)}";
        InitializeComponent();
        DataContext = this;
    }
}
