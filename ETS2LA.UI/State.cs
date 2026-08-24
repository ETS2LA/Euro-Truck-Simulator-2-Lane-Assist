namespace ETS2LA.UI;

public class UserInterfaceState
{
    private static readonly Lazy<UserInterfaceState> _instance = new(() => new UserInterfaceState());
    public static UserInterfaceState Current => _instance.Value;

    public bool IsSidebarOpen { get; set; } = true;
}