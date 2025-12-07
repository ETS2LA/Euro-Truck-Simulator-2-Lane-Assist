using System.Collections.Generic;

namespace ETS2LA.Shared;

public enum PluginPageLocation
{
    Manager,
    Settings,
    Helper
}

public interface IPluginUi
{
    IEnumerable<PluginPage> RenderPages();
    void OnAction(string actionId, object? value);
}

public record PluginPage(string Id, PluginPageLocation Location, string Title, string Description, IReadOnlyList<UiElement> Body);

public abstract record UiElement;
public record UiSection(string? Title, string? Description, IReadOnlyList<UiElement> Children) : UiElement;
public record UiText(string Text, bool Muted = false, bool Bold = false) : UiElement;
public record UiCheckbox(string Label, string Description, bool Default, string ActionId) : UiElement;
public record UiSwitch(string Label, string Description, bool Default, string ActionId) : UiElement;
public record UiSlider(string Label, string Description, double Min, double Max, double Step, double Default, string ActionId) : UiElement;
public record UiCombobox(string Label, string Description, IReadOnlyList<string> Options, int SelectedIndex, string ActionId, bool Searchable = true) : UiElement;
public record UiButton(string Label, string Description, string ActionId, bool Emphasized = false) : UiElement;
public record UiInput(string Label, string Description, string Default, string ActionId, string Type = "string") : UiElement;
public record UiTable(string Title, IReadOnlyList<string> Columns, IReadOnlyList<IReadOnlyList<string>> Rows) : UiElement;
public record UiContainer(IReadOnlyList<UiElement> Children) : UiElement;
