using Avalonia.Controls;

namespace ETS2LA.Controls.Defaults;

public class DefaultControls
{
    public ControlDefinition Assist = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Assist",
        Name = "Assist",
        Description = "Will toggle ETS2LA's assists on and off. Will not update the speed, use SET if you want that. You can change how this key (and SET) behave in the Assistance settings.",
        DefaultKeybind = "N",
        Type = ControlType.Boolean
    };

    public ControlDefinition SET = new ControlDefinition
    {
        Id = "ETS2LA.Controls.SET",
        Name = "SET/OK",
        Description = "Works like Assist, but will act the way you select in the Assistance settings. This key will additionally be used for confirmations.",
        DefaultKeybind = "Left",
        Type = ControlType.Boolean
    };

    public ControlDefinition Next = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Next",
        Name = "Next/Cancel",
        Description = "This key will navigate any ETS2LA menus forward, it will also work as the cancel key for any confirmations.",
        DefaultKeybind = "Right",
        Type = ControlType.Boolean
    };

    public ControlDefinition Increase = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Increase",
        Name = "Increase",
        Description = "Increases the current value (e.g. target speed) by one step. Without any visual modifier shown in the UI, this will increase the target speed by 1 km/h.",
        DefaultKeybind = "Up",
        Type = ControlType.Boolean
    };

    public ControlDefinition Decrease = new ControlDefinition
    {
        Id = "ETS2LA.Controls.Decrease",
        Name = "Decrease",
        Description = "Decreases the current value (e.g. target speed) by one step. Without any visual modifier shown in the UI, this will decrease the target speed by 1 km/h.",
        DefaultKeybind = "Down",
        Type = ControlType.Boolean
    };

}