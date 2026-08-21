using static ETS2LA.Translations.T;

namespace ETS2LA.Controls.Defaults;

public static class DefaultControls
{
    public static ControlDefinition Assist { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Assist",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Assist"),
        Description = _("Will toggle ETS2LA's assists on and off. Will not update the speed, use SET if you want that. You can change how this key (and SET) behave in the Assistance settings."),
        DefaultKeybind = "N",
        Type = ControlType.Boolean
    };

    public static ControlDefinition SET { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.SET",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("SET/OK"),
        Description = _("Works like Assist, but will act the way you select in the Assistance settings. This key will additionally be used for confirmations."),
        DefaultKeybind = "Left",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Next { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Next",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Next/Cancel"),
        Description = _("This key will navigate any ETS2LA menus forward, it will also work as the cancel key for any confirmations."),
        DefaultKeybind = "Right",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Increase { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Increase",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Increase"),
        Description = _("Increases the current value (e.g. target speed) by one step. Without any visual modifier shown in the UI, this will increase the target speed by 1 km/h."),
        DefaultKeybind = "Up",
        Type = ControlType.Boolean
    };

    public static ControlDefinition Decrease { get; } = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Decrease",
        // TRANSLATORS: This is the name of a keybind.
        Name = _("Decrease"),
        Description = _("Decreases the current value (e.g. target speed) by one step. Without any visual modifier shown in the UI, this will decrease the target speed by 1 km/h."),
        DefaultKeybind = "Down",
        Type = ControlType.Boolean
    };

}