using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using ETS2LA.Settings.Global;
using System.Runtime.CompilerServices;
using System.Collections.ObjectModel;
using ETS2LA.Game.Data;

namespace ETS2LA.UI.Views.Settings;

public partial class DataSettingsPage : UserControl, INotifyPropertyChanged
{
    public ObservableCollection<TabStripItemHandler> DataFidelityOptions { get; } = new();
    public ObservableCollection<TabStripItemHandler> CurveQualityOptions { get; } = new();

    public int SelectedDataFidelityOption { get; set; }
    public int SelectedCurveQualityOption { get; set; }

    public DataSettingsPage()
    {
        LoadDataFidelityOptions();
        LoadCurveQualityOptions();

        AvaloniaXamlLoader.Load(this);
        DataContext = this;
    }

    private void LoadDataFidelityOptions()
    {
        SelectedDataFidelityOption = (int)DataSettings.Current.DataFidelity;
        foreach (DataFidelity option in Enum.GetValues(typeof(DataFidelity)))
        {
            DataFidelityOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void LoadCurveQualityOptions()
    {
        SelectedCurveQualityOption = (int)DataSettings.Current.CurveQuality;
        foreach (CurveQuality option in Enum.GetValues(typeof(CurveQuality)))
        {
            CurveQualityOptions.Add(new TabStripItemHandler(option.ToString()));
        }
    }

    private void OnDataFidelityChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedDataFidelityOption >= 0)
        {
            DataSettings.Current.DataFidelity = (DataFidelity)SelectedDataFidelityOption;
            DataSettings.Current.Save();
        }
    }

    private void OnCurveQualityChanged(object? sender, SelectionChangedEventArgs e)
    {
        if (SelectedCurveQualityOption >= 0)
        {
            DataSettings.Current.CurveQuality = (CurveQuality)SelectedCurveQualityOption;
            DataSettings.Current.Save();
        }
    }

    public new event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}