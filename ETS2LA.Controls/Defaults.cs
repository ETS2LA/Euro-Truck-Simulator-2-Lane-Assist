using static ETS2LA.Translations.T;

namespace ETS2LA.Controls.Defaults;

public static class DefaultControls
{
    public static ControlDefinition Increase { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Increase",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Increase/RES"),
        Description = _("Increases the current target speed by one step. If assists are disabled, this key acts like RES. Meaning it will resume the last set target speed. If a last target speed was not set, this key acts like SET."),
        DefaultKeybind = "Up",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Decrease { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Decrease",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Decrease/SET"),
        Description = _("Decreases the current target speed by one step. If speed control and lane assist are off, this key acts like SET. Meaning it will set the current speed to speedlimit."),
        DefaultKeybind = "Down",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Cancel { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Cancel",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Cancel/MODE"),
        Description = _("Will disable ETS2LA's assists when pressed. If assists are already disabled, this key will switch between driving modes."),
        DefaultKeybind = "Left",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Next { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Next",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Next/OK"),
        Description = _("This key is used to select in UI menus. It also acts as the approval key for any notifications."),
        DefaultKeybind = "Right",
        Type = ControlType.Boolean
    };
}