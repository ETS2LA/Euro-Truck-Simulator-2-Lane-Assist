using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Layout;
using Avalonia.Media;
using ETS2LA.Shared;

namespace ETS2LA.UI.Rendering;

public static class PluginUiRenderer
{
    public static Control RenderPage(PluginPage page, IPluginUi handler)
    {
        var stack = new StackPanel { Spacing = 10 };

        if (!string.IsNullOrWhiteSpace(page.Title))
        {
            stack.Children.Add(new TextBlock
            {
                Text = page.Title,
                Classes = { "title" }
            });
        }

        if (!string.IsNullOrWhiteSpace(page.Description))
        {
            stack.Children.Add(new TextBlock
            {
                Text = page.Description,
                Classes = { "subtitle" }
            });
        }

        foreach (var element in page.Body)
        {
            stack.Children.Add(RenderElement(element, handler));
        }

        return new ScrollViewer { Content = stack };
    }

    private static Control RenderElement(UiElement element, IPluginUi handler)
    {
        return element switch
        {
            UiSection s => RenderSection(s, handler),
            UiText t => new TextBlock
            {
                Text = t.Text,
                FontWeight = t.Bold ? FontWeight.SemiBold : FontWeight.Normal,
                Classes = { t.Muted ? "muted" : "body" },
                TextWrapping = TextWrapping.Wrap
            },
            UiCheckbox c => RenderCheckbox(c, handler),
            UiSwitch sw => RenderSwitch(sw, handler),
            UiSlider sl => RenderSlider(sl, handler),
            UiCombobox cb => RenderCombobox(cb, handler),
            UiButton b => RenderButton(b, handler),
            UiInput i => RenderInput(i, handler),
            UiTable t => RenderTable(t),
            UiContainer c => RenderContainer(c, handler),
            _ => new TextBlock { Text = $"Unsupported element {element.GetType().Name}", Foreground = Brushes.OrangeRed }
        };
    }

    private static Control RenderSection(UiSection section, IPluginUi handler)
    {
        var stack = new StackPanel { Spacing = 6 };
        if (!string.IsNullOrWhiteSpace(section.Title))
        {
            stack.Children.Add(new TextBlock
            {
                Text = section.Title,
                Classes = { "label" }
            });
        }
        if (!string.IsNullOrWhiteSpace(section.Description))
        {
            stack.Children.Add(new TextBlock
            {
                Text = section.Description,
                Classes = { "muted" },
                TextWrapping = TextWrapping.Wrap
            });
        }

        foreach (var child in section.Children)
            stack.Children.Add(RenderElement(child, handler));

        return new Border
        {
            Classes = { "card" },
            Padding = new Thickness(12),
            Margin = new Thickness(0, 6, 0, 6),
            Child = stack
        };
    }

    private static Control RenderCheckbox(UiCheckbox cb, IPluginUi handler)
    {
        var panel = new StackPanel { Spacing = 4 };
        var check = new CheckBox { IsChecked = cb.Default };
        check.Checked += (_, _) => handler.OnAction(cb.ActionId, true);
        check.Unchecked += (_, _) => handler.OnAction(cb.ActionId, false);

        panel.Children.Add(new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children =
            {
                check,
                new TextBlock { Text = cb.Label, Classes = { "label" }, VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center }
            }
        });
        panel.Children.Add(new TextBlock { Text = cb.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap });
        return panel;
    }

    private static Control RenderSwitch(UiSwitch sw, IPluginUi handler)
    {
        var toggle = new ToggleSwitch { IsChecked = sw.Default, HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left };
        toggle.Classes.Add("primary-toggle");
        toggle.Checked += (_, _) => handler.OnAction(sw.ActionId, true);
        toggle.Unchecked += (_, _) => handler.OnAction(sw.ActionId, false);

        return new StackPanel
        {
            Spacing = 4,
            Children =
            {
                new StackPanel
                {
                    Orientation = Orientation.Horizontal,
                    Spacing = 8,
                    Children =
                    {
                        toggle,
                        new TextBlock { Text = sw.Label, Classes = { "label" }, VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center }
                    }
                },
                new TextBlock { Text = sw.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap }
            }
        };
    }

    private static Control RenderSlider(UiSlider sl, IPluginUi handler)
    {
        var slider = new Slider
        {
            Minimum = sl.Min,
            Maximum = sl.Max,
            Value = sl.Default,
            TickFrequency = sl.Step,
            IsSnapToTickEnabled = true
        };
        slider.PropertyChanged += (_, args) =>
        {
            if (args.Property == RangeBase.ValueProperty)
                handler.OnAction(sl.ActionId, slider.Value);
        };

        return new StackPanel
        {
            Spacing = 4,
            Children =
            {
                new TextBlock { Text = sl.Label, Classes = { "label" } },
                slider,
                new TextBlock { Text = sl.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap }
            }
        };
    }

    private static Control RenderCombobox(UiCombobox cb, IPluginUi handler)
    {
        var combo = new ComboBox
        {
            ItemsSource = cb.Options,
            SelectedIndex = cb.SelectedIndex >= 0 && cb.SelectedIndex < cb.Options.Count ? cb.SelectedIndex : 0
        };
        combo.SelectionChanged += (_, _) =>
        {
            handler.OnAction(cb.ActionId, combo.SelectedItem);
        };

        return new StackPanel
        {
            Spacing = 4,
            Children =
            {
                new TextBlock { Text = cb.Label, Classes = { "label" } },
                combo,
                new TextBlock { Text = cb.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap }
            }
        };
    }

    private static Control RenderButton(UiButton b, IPluginUi handler)
    {
        var btn = new Button
        {
            Content = b.Label,
            Padding = new Thickness(12, 8),
            Classes = { b.Emphasized ? "primary-button" : "ghost-button" },
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left
        };
        btn.Click += (_, _) => handler.OnAction(b.ActionId, null);

        var stack = new StackPanel { Spacing = 4 };
        stack.Children.Add(btn);
        if (!string.IsNullOrWhiteSpace(b.Description))
        {
            stack.Children.Add(new TextBlock { Text = b.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap });
        }
        return stack;
    }

    private static Control RenderInput(UiInput input, IPluginUi handler)
    {
        var box = new TextBox { Text = input.Default ?? string.Empty };
        box.LostFocus += (_, _) => handler.OnAction(input.ActionId, box.Text ?? string.Empty);
        return new StackPanel
        {
            Spacing = 4,
            Children =
            {
                new TextBlock { Text = input.Label, Classes = { "label" } },
                box,
                new TextBlock { Text = input.Description, Classes = { "muted" }, FontSize = 12, TextWrapping = TextWrapping.Wrap }
            }
        };
    }

    private static Control RenderTable(UiTable table)
    {
        var grid = new Grid();
        for (int i = 0; i < table.Columns.Count; i++)
            grid.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Auto));

        int row = 0;
        grid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));
        var headerRow = new Grid();
        for (int c = 0; c < table.Columns.Count; c++)
        {
            headerRow.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Auto));
            headerRow.Children.Add(new TextBlock
            {
                Text = table.Columns[c],
                FontWeight = FontWeight.SemiBold,
                Foreground = Brushes.White,
                Margin = new Thickness(8, 0)
            }.WithGridColumn(c));
        }
        grid.Children.Add(headerRow.WithGridRow(row++));

        foreach (var r in table.Rows)
        {
            grid.RowDefinitions.Add(new RowDefinition(GridLength.Auto));
            var rowGrid = new Grid();
            for (int c = 0; c < table.Columns.Count; c++)
            {
                rowGrid.ColumnDefinitions.Add(new ColumnDefinition(GridLength.Auto));
                var val = c < r.Count ? r[c] : string.Empty;
                rowGrid.Children.Add(new TextBlock
                {
                    Text = val,
                    Foreground = Brushes.LightGray,
                    Margin = new Thickness(8, 0)
                }.WithGridColumn(c));
            }
            grid.Children.Add(rowGrid.WithGridRow(row++));
        }

        return new Border
        {
            Background = new SolidColorBrush(Color.Parse("#111214")),
            BorderBrush = new SolidColorBrush(Color.Parse("#1F252C")),
            BorderThickness = new Thickness(1),
            CornerRadius = new CornerRadius(10),
            Padding = new Thickness(10),
            Child = grid
        };
    }

    private static Control RenderContainer(UiContainer container, IPluginUi handler)
    {
        var stack = new StackPanel { Spacing = 8 };
        foreach (var child in container.Children)
        {
            stack.Children.Add(RenderElement(child, handler));
        }
        return stack;
    }

    private static T WithGridColumn<T>(this T control, int column) where T : Control
    {
        Grid.SetColumn(control, column);
        return control;
    }

    private static T WithGridRow<T>(this T control, int row) where T : Control
    {
        Grid.SetRow(control, row);
        return control;
    }
}
