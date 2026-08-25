namespace ETS2LA.UI;

public class WindowState
{
    private static readonly Lazy<WindowState> _instance = new(() => new WindowState());
    public static WindowState Current => _instance.Value;

    public event EventHandler? NeedsFullReload;
    public bool IsSidebarOpen { get; set; } = true;

    public void RequestFullReload()
    {
        NeedsFullReload?.Invoke(this, EventArgs.Empty);
    }
}