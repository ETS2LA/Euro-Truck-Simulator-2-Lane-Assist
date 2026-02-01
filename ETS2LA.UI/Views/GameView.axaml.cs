using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

using ETS2LA.Game;
using ETS2LA.UI.Notifications;

using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace ETS2LA.UI.Views;

public partial class GameView : UserControl
{
    public ObservableCollection<GameItem> Installations { get; } = new();

    public GameView()
    {
        InitializeComponent();
        DataContext = this;
        GameHandler.Current.SetNotificationHandler(NotificationHandler.Current);
        UpdateGameList();
    }

    private void ParseMapDataCommand(object? sender, RoutedEventArgs e)
    {
        if (sender is Control { Tag: GameItem item })
        {
            item.ParseMapDataCommand();
        }
    }

    private void UpdateGameList()
    {
        List<Installation> installations = GameHandler.Current.Installations ?? new List<Installation>();
        foreach (var install in installations)
        {
            Installations.Add(new GameItem(install));
        }

        bool hasInstallations = Installations.Count > 0;
        if (this.FindControl<ItemsControl>("GameList") is { } list)
            list.IsVisible = hasInstallations;
        if (this.FindControl<Border>("PlaceholderPanel") is { } placeholder)
            placeholder.IsVisible = !hasInstallations;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}

public class GameItem : INotifyPropertyChanged
{
    private readonly Installation _instance;

    public string Game => TypeToString(_instance.Type);
    public string Path => _instance.Path.Replace("\\", "/").Replace("//", "/");
    public string Version => _instance.Version.Split(" ")[0];
    public bool IsParsed => _instance.IsParsed;
    public bool IsParsing => _instance.IsParsing;
    public IEnumerable<string> Mods => _instance.GetAvailableMods().Select(m => m.ToString());

    private ObservableCollection<string> _selectedMods;
    public ObservableCollection<string> SelectedMods
    {
        get
        {
            if (_selectedMods == null)
            {
                _selectedMods = new ObservableCollection<string>(_instance.GetSelectedMods());
            }
            return _selectedMods;
        }
        set
        {
            _selectedMods = value;
            _instance.SetSelectedMods(new List<string>(value));
            OnPropertyChanged();
        }
    }

    public GameItem(Installation instance)
    {
        _selectedMods = new ObservableCollection<string>(instance.GetSelectedMods());
        _instance = instance;
        instance.OnDataParsed += () => UpdateFields();
        instance.OnDataNotParsed += () => UpdateFields();
        instance.OnParsingStarted += () => UpdateFields();
    }

    public void UpdateFields()
    {
        OnPropertyChanged(nameof(IsParsed));
        OnPropertyChanged(nameof(IsParsing));
        OnPropertyChanged(nameof(Mods));
    }

    public void ParseMapDataCommand()
    {
        if (IsParsing || IsParsed)
            return;
        
        _instance.SetSelectedMods(new List<string>(SelectedMods));
        Task.Run(() => _instance.Parse());
    }

    private string TypeToString(GameType type)
    {
        return type switch
        {
            GameType.EuroTruckSimulator2 => "Euro Truck Simulator 2",
            GameType.AmericanTruckSimulator => "American Truck Simulator",
            _ => "Unknown",
        };
    }

    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
