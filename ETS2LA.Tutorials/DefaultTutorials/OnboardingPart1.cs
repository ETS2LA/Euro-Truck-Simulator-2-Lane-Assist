using Hexa.NET.ImGui;
using ETS2LA.Overlay;
using ETS2LA.Controls;
using System.Numerics;
using ETS2LA.Backend.Events;

namespace ETS2LA.Tutorials.DefaultTutorials;

public class OnboardingPart1
{
    bool hasMoved = false;

    public Tutorial Create()
    {
        return new Tutorial("OnboardingPart1", "Onboarding until the catalogue plugins were installed.", "ETS2LA", new List<TutorialSection>
        {
            new TutorialSection
            {
                Title = "Introduction to the overlay",
                Actions = new List<TutorialAction>
                {
                    new ShowImguiWindowAction
                    {
                        ImGuiCallback = WelcomePage,
                        ScreenPositionCallback = ETS2LAWindowLocation,
                        SizeCallback = ETS2LAWindowSize,
                        ImGuiWindowFlags = ImGuiWindowFlags.NoDecoration
                    },
                    new WaitForInputAction
                    {
                        ControlId = OverlayHandler.Current.Interact.Id
                    },
                    new ShowImguiWindowAction
                    {
                        ImGuiCallback = OverlayInteractionPage,
                        ScreenPositionCallback = ETS2LAWindowLocation,
                        SizeCallback = ETS2LAWindowSize,
                        ImGuiWindowFlags = ImGuiWindowFlags.NoDecoration
                    },
                    new WaitForEventAction
                    {
                        EventId = "Onboarding.MovedWindow"
                    },
                    new ShowImguiWindowAction
                    {
                        ImGuiCallback = OverlayInteractionPage,
                        ScreenPositionCallback = ETS2LAWindowLocation,
                        SizeCallback = ETS2LAWindowSize,
                        ImGuiWindowFlags = ImGuiWindowFlags.NoDecoration
                    },
                    new WaitForInputAction
                    {
                        ControlId = OverlayHandler.Current.Interact.Id
                    },
                }
            },
            new TutorialSection
            {
                Title = "Introduction to the User Interface",
                Actions = new List<TutorialAction>
                {
                    new ShowMessageAction
                    {
                        Message = "This sidebar has everything you need.\nLet's go to the catalogue page to start with.",
                        ScreenPositionCallback = () =>
                        {
                            var position = ETS2LAWindowLocation();
                            var size = ETS2LAWindowSize();
                            return (position.Item1 + 15, position.Item2 + 230);
                        }
                    },
                    new WaitForEventAction
                    {
                        EventId = "ETS2LA.UI.SwitchedPage.Catalogue"
                    },
                    new ShowMessageAction
                    {
                        Message = "You'll want to install the 'Lane Assist' and 'Adaptive Cruise Control' plugins.",
                        ScreenPositionCallback = () =>
                        {
                            var position = ETS2LAWindowLocation();
                            var size = ETS2LAWindowSize();
                            return (position.Item1 + 230, position.Item2 + 1);
                        }
                    },
                    new WaitForEventAction
                    {
                        EventId = "ETS2LA.Plugins.Installed.tumppi066.adaptivecruisecontrol"
                    },
                    new ShowMessageAction
                    {
                        Message = "You might've noticed we automatically installed dependencies.\nEvery time you install/uninstall plugins or libraries, you need\nto restart ETS2LA. On some systems you may need to restart ETS2LA yourself.",
                        ScreenPositionCallback = () =>
                        {
                            var position = ETS2LAWindowLocation();
                            var size = ETS2LAWindowSize();
                            return (position.Item1 + 140, position.Item2 + 224);
                        }
                    },
                }
            }
        });
    }

    private void AlignForWidth(float width, float alignment = 0.5f)
    {
        float avail = ImGui.GetContentRegionAvail().X;
        float off = (avail - width) * alignment;
        if (off > 0.0f)
            ImGui.SetCursorPosX(ImGui.GetCursorPosX() + off);
    }

    private void WelcomePage()
    {
        // Pad top
        ImGui.SetCursorPosY(ImGui.GetCursorPosY() + 100);

        ImGui.PushFont(OverlayHandler.Current.Fonts[FontStyle.Bold], 20);
        AlignForWidth(ImGui.CalcTextSize("Welcome to ETS2LA!").X);
        ImGui.Text("Welcome to ETS2LA!");
        ImGui.Spacing();
        ImGui.PopFont();

        AlignForWidth(ImGui.CalcTextSize("Let's start off by familiarizing you to our User Interface.").X);
        ImGui.Text("Let's start off by familiarizing you to our User Interface.");
        AlignForWidth(ImGui.CalcTextSize("The window you're seeing right now is an overlay.").X);
        ImGui.Text("The window you're seeing right now is an overlay.");
        ImGui.Spacing();
        ImGui.Spacing();

        AlignForWidth(ImGui.CalcTextSize("You can continue by holding down the overlay interaction key.").X);
        ImGui.Text("You can continue by holding down the overlay interaction key.");

        # if LINUX
        AlignForWidth(ImGui.CalcTextSize("Note: You're on Linux, make sure you are allowing X11 global hotkeys on keys you need.").X);
        ImGui.TextColored(new Vector4(0.6f, 0.6f, 0.6f, 1f), "Note: You're on Linux, make sure you are allowing X11 global hotkeys on keys you need.");
        ImGui.Spacing();
        ImGui.Spacing();
        # endif

        var controls = ControlsBackend.Current.GetRegisteredControls();        
        var interactKey = controls.FirstOrDefault(c => c.Definition.Id == OverlayHandler.Current.Interact.Id);
        var text = interactKey != null ? interactKey.ControlId.ToString() : "UNBOUND";

        AlignForWidth(ImGui.CalcTextSize(text).X);
        ImGui.PushFont(OverlayHandler.Current.Fonts[FontStyle.Bold], 18f);
        ImGui.TextColored(new Vector4(1f, 0.5f, 0.5f, 1f), text);
        ImGui.PopFont();
    }

    private void OverlayInteractionPage()
    {
        if (!hasMoved)
        {
            if (ImGui.IsMouseReleased(ImGuiMouseButton.Left))
            {
                Events.Current.Publish("Onboarding.MovedWindow", new EventArgs());
                hasMoved = true;
            }
        }

        // Pad top
        ImGui.SetCursorPosY(ImGui.GetCursorPosY() + 100);

        if (!hasMoved)
        {
            ImGui.PushFont(OverlayHandler.Current.Fonts[FontStyle.Bold], 20);
            AlignForWidth(ImGui.CalcTextSize("Great!").X);
            ImGui.Text("Great!");
            ImGui.Spacing();
            ImGui.PopFont();

            AlignForWidth(ImGui.CalcTextSize("This overlay is used for many features in ETS2LA.").X);
            ImGui.Text("This overlay is used for many features in ETS2LA.");
            AlignForWidth(ImGui.CalcTextSize("If you don't like the keybind you can always change it in the settings later.").X);
            ImGui.Text("If you don't like the keybind you can always change it in the settings later.");
            ImGui.Spacing();
            ImGui.Spacing();

            AlignForWidth(ImGui.CalcTextSize("Now that we're in overlay mode, you can interact with windows.").X);
            ImGui.Text("Now that we're in overlay mode, you can interact with windows.");

            AlignForWidth(ImGui.CalcTextSize("Try to move this window around by dragging it!").X);
            ImGui.TextColored(new Vector4(0.5f, 1f, 0.5f, 1f), "Try to move this window around by dragging it!");
            ImGui.Spacing();
            ImGui.Spacing();
        }

        if (hasMoved)
        {
            ImGui.PushFont(OverlayHandler.Current.Fonts[FontStyle.Bold], 20);
            AlignForWidth(ImGui.CalcTextSize("Fantastic!").X);
            ImGui.Text("Fantastic!");
            ImGui.Spacing();
            ImGui.PopFont();
            
            AlignForWidth(ImGui.CalcTextSize("Remember, if you need to interact with overlay windows, enter interaction mode first!").X);
            ImGui.Text("Remember, if you need to interact with overlay windows, enter interaction mode first!");
            ImGui.Spacing();

            AlignForWidth(ImGui.CalcTextSize("Exit overlay interaction mode to continue.").X);
            ImGui.TextColored(new Vector4(0.5f, 1f, 0.5f, 1f), "Exit overlay interaction mode to continue.");
        }
    }

    private (int, int) ETS2LAWindowLocation()
    {
        // if (Application.Current == null || Application.Current.ApplicationLifetime == null)
        //     return (0, 0);
// 
        // var window = ((IClassicDesktopStyleApplicationLifetime)Application.Current.ApplicationLifetime).MainWindow;
        // if (window == null)
        //     return (0, 0);
        // 
        // return (window.Position.X, window.Position.Y);
        return (0, 0);
    }

    private (int, int) ETS2LAWindowSize()
    {
        //if (Application.Current == null || Application.Current.ApplicationLifetime == null)
        //    return (0, 0);
//
        //var window = ((IClassicDesktopStyleApplicationLifetime)Application.Current.ApplicationLifetime).MainWindow;
        //if (window == null || window.FrameSize == null)
        //    return (0, 0);
        //
        //var size = ((int)window.FrameSize.Value.Width, (int)window.FrameSize.Value.Height);
        //return size;
        return (0, 0);
    }
}