using Avalonia.Controls;
using ETS2LA.Game;
using ETS2LA.UI.Services;
using ETS2LA.Logging;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

namespace ETS2LA.UI.Views;

public partial class GameView : UserControl
{
    public ObservableCollection<GameItem> Installations { get; } = new();
    private readonly GameHandler? gameHandler;

    public GameView(PluginManagerService service)
    {
        gameHandler = GameHandler.Instance;
        InitializeComponent();
        DataContext = this;
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
        List<Installation> installations = gameHandler?.Installations ?? new List<Installation>();
        foreach (var install in installations)
        {
            Installations.Add(new GameItem(install, gameHandler));
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
    private readonly GameHandler _service;
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

    public GameItem(Installation instance, GameHandler service)
    {
        _instance = instance;
        _service = service;
    }

    public void ParseMapDataCommand()
    {
        _instance.SetSelectedMods(new List<string>(SelectedMods));
        Task.Run(() => _instance.Parse());
        OnPropertyChanged(nameof(IsParsed));
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
