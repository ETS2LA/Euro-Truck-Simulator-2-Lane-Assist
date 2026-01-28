using ETS2LA.Shared;

namespace AdaptiveCruiseControl;

public static class Controls
{
    public static ControlBinding ToggleAcc => new(AccSettingKeys.Toggle, "Toggle Speed Control", "button", "Toggle ACC on/off.", "n");
    public static ControlBinding IncreaseOffset => new(AccSettingKeys.IncSpeed, "Increase Speed Offset", "button", "Increase ACC speed offset.", "UpArrow");
    public static ControlBinding DecreaseOffset => new(AccSettingKeys.DecSpeed, "Decrease Speed Offset", "button", "Decrease ACC speed offset.", "DownArrow");
}

public record ControlBinding(string Id, string Title, string Type, string Description, string Default);
