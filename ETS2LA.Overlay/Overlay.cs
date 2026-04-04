// Much of this file is based on the Hexa.NET.ImGui example code. See the relevant example here:
// https://github.com/HexaEngine/Hexa.NET.ImGui/blob/main/Examples/ExampleGLFWOpenGL3/Program.cs

using Hexa.NET.GLFW;
using Hexa.NET.ImGui;
using Hexa.NET.ImGui.Backends.GLFW;
using Hexa.NET.ImGui.Backends.OpenGL3;
using Hexa.NET.OpenGL;
using HexaGen.Runtime;
using GLFWwindowPtr = Hexa.NET.GLFW.GLFWwindowPtr;

using System.Runtime.CompilerServices;
using System.Numerics;

using ETS2LA.Logging;
using ETS2LA.Controls;
using ETS2LA.Overlay.Windows;
using Avalonia.Data;
using System.Runtime.InteropServices;

namespace ETS2LA.Overlay;

public class OverlayHandler
{
    private static readonly Lazy<OverlayHandler> _instance = new(() => new OverlayHandler());
    public static OverlayHandler Current => _instance.Value;

    public ControlDefinition Interact = new ControlDefinition
    {   
        Id = "ETS2LA.Overlay.Interact",
        Name = "Overlay Interaction",
        Description = "When this key is held, the overlay will receive mouse input and allow you to interact with it. NOTE: Interaction with items below the overlay is not possible during this time.",
        DefaultKeybind = "RightAlt",
        Type = ControlType.Boolean
    };
    private bool _isInteracting = false;
    private float _bgOpacityTarget = 0.0f;
    private float _deltaTime = 0f;
    
    private List<InternalWindow> _windows = new();

    public bool IsOverlayFocused => _isInteracting;
    public float LastFrameTime => _deltaTime;

    public float OverlayWidth => GLFW.GetVideoMode(GLFW.GetPrimaryMonitor()).Width;
    public float OverlayHeight => GLFW.GetVideoMode(GLFW.GetPrimaryMonitor()).Height;

    private string glslVersion = "#version 150";
    private GLFWwindowPtr _window;
    private ImGuiContextPtr _imGuiContext;
    private ImGuiIOPtr _io;
    private GL _gl;

    public OverlayHandler()
    {
        ControlsBackend.Current.RegisterControl(Interact);
        ControlsBackend.Current.On(Interact.Id, HandleInput);

        Task.Run(() => RenderLoop());
        
        _windows.Add(new ConsoleWindow());
        _windows.Add(new ARInfoWindow());
        _windows.Add(new DemoWindow());
        _windows.Add(new StateWindow());
    }

    private void HandleInput(object sender, ControlChangeEventArgs e)
    {
        bool b = (bool)e.NewValue;
        if (b == _isInteracting) { return; }
        _isInteracting = b;
    }

    private void RenderLoop()
    {
        if(!InitGLFW())
        {
            Logger.Error("Failed to initialize overlay");
            return;
        }
        GLFW.MakeContextCurrent(_window);
        _gl = new GL(new BindingsContext(_window));

        if (!InitImGui())
        {
            Logger.Error("Failed to initialize overlay");
            return;
        }

        while (GLFW.WindowShouldClose(_window) == 0)
        {
            float startTime = DateTime.Now.Millisecond;
            if (!_isInteracting) 
            { 
                // This has to be called each frame to properly update the flags.
                // For whatever reason they are set back to default.
                ImGui.GetPlatformIO().Viewports[0].Flags |= ImGuiViewportFlags.NoInputs;

                # if LINUX
                GLFW.SetWindowAttrib(_window, GLFW.GLFW_MOUSE_PASSTHROUGH, 1);
                # endif
                
                _bgOpacityTarget = 0.0f;
            }
            else 
            {
                # if LINUX
                GLFW.SetWindowAttrib(_window, GLFW.GLFW_MOUSE_PASSTHROUGH, 0);
                # endif
                _bgOpacityTarget = 0.5f;
            }

            GLFW.PollEvents();

            // Skip rendering if we're minimized, though this should actually
            // never happen for the overlay.
            if (GLFW.GetWindowAttrib(_window, GLFW.GLFW_ICONIFIED) != 0)
            {
                ImGuiImplGLFW.Sleep(10);
                continue;
            }

            GLFW.MakeContextCurrent(_window);

            ImGuiImplOpenGL3.NewFrame();
            ImGuiImplGLFW.NewFrame();
            ImGui.NewFrame();
            
            OnUIRender();
            
            ImGui.Render();
            GLFW.MakeContextCurrent(_window);

            _gl.ClearColor(0f, 0f, 0f, _bgOpacityTarget);
            _gl.Clear(GLClearBufferMask.ColorBufferBit);
            
            ImGuiImplOpenGL3.RenderDrawData(ImGui.GetDrawData());

            if ((_io.ConfigFlags & ImGuiConfigFlags.ViewportsEnable) != 0)
            {
                ImGui.UpdatePlatformWindows();
                ImGui.RenderPlatformWindowsDefault();
            }

            GLFW.MakeContextCurrent(_window);
            // Swap front and back buffers (double buffering)
            GLFW.SwapBuffers(_window);
            _deltaTime = (DateTime.Now.Millisecond - startTime) / 1000f;
        }

        ImGuiImplOpenGL3.Shutdown();
        ImGuiImplOpenGL3.SetCurrentContext(null);
        ImGuiImplGLFW.Shutdown();
        ImGuiImplGLFW.SetCurrentContext(null);
        ImGui.DestroyContext();
        _gl.Dispose();

        // Clean up and terminate GLFW
        GLFW.DestroyWindow(_window);
        GLFW.Terminate();
    }

    private void OnUIRender()
    {
        if (_isInteracting)
        {
            ImGui.Begin("Interaction Mode", ImGuiWindowFlags.NoDecoration | ImGuiWindowFlags.AlwaysAutoResize | ImGuiWindowFlags.NoBackground);
            ImGui.SetWindowPos(new Vector2(OverlayWidth / 2 - 60, 10), ImGuiCond.Always);
            ImGui.TextColored(new Vector4(0.5f, 0.5f, 0.5f, 1f), "Interaction Mode");

            ImGui.Spacing();
            foreach (var window in _windows) {
                bool isOpen = window.IsWindowOpen;
                Vector4 color = isOpen ? new Vector4(0.5f, 0.6f, 0.5f, 1f) : new Vector4(0.6f, 0.5f, 0.5f, 1f);

                ImGui.TextColored(color, isOpen ? "[X]" : "[   ]");
                ImGui.SameLine();
                ImGui.TextColored(color, window.Definition.Title);
    
                if (ImGui.IsItemHovered())
                {
                    ImGui.SetTooltip("Click to " + (isOpen ? "hide" : "show") + " this window");
                }
                if (ImGui.IsItemClicked())
                {
                    window.IsWindowOpen = !window.IsWindowOpen;
                }
            }
            ImGui.End();
        }

        foreach (InternalWindow window in _windows)
        {
            if (!window.IsWindowOpen) { continue; }
            if (window.Definition.NoWindow.GetValueOrDefault(false))
            {
                window.Render();
                continue;
            }

            ImGui.SetNextWindowSize(new Vector2(
                window.Definition.Width.GetValueOrDefault(480), 
                window.Definition.Height.GetValueOrDefault(320)
            ), ImGuiCond.Once);
            
            ImGui.SetNextWindowBgAlpha(window.Definition.Alpha.GetValueOrDefault(1f));
            ImGui.Begin(window.Definition.Title, window.Definition.Flags.GetValueOrDefault(ImGuiWindowFlags.None));
            
            ImGui.SetWindowPos(new Vector2(
                (int)window.Definition.X.GetValueOrDefault(OverlayWidth / 2), 
                (int)window.Definition.Y.GetValueOrDefault(OverlayHeight / 2)
            ), ImGuiCond.Once);

            var isCollapsed = ImGui.IsWindowCollapsed();
            if (isCollapsed) {
                ImGui.End(); 
                continue; 
            }

            RenderWindowContextMenu(window);
            window.Render();
            ImGui.End();
        }
    }

    private unsafe void RenderWindowContextMenu(InternalWindow window)
    {
        if (ImGui.BeginPopupContextWindow((byte*)0, ImGuiPopupFlags.MouseButtonRight))
        {
            window.RenderContextMenu();
            if (ImGui.MenuItem("Close"))
            {
                window.IsWindowOpen = false;
            }
            ImGui.EndPopup();
        }
    }

    private bool InitImGui()
    {
        _imGuiContext = ImGui.CreateContext();
        ImGui.SetCurrentContext(_imGuiContext);

        _io = ImGui.GetIO();
        _io.ConfigFlags |= ImGuiConfigFlags.NavEnableKeyboard;     // Enable Keyboard Controls
        _io.ConfigFlags |= ImGuiConfigFlags.NavEnableGamepad;      // Enable Gamepad Controls
        _io.ConfigFlags |= ImGuiConfigFlags.DockingEnable;         // Enable Docking
        // TODO: This is disabled for now as it causes submenus to appear below main windows.
        //_io.ConfigFlags |= ImGuiConfigFlags.ViewportsEnable;       // Enable Multi-Viewport / Platform Windows

        var mon = GLFW.GetPrimaryMonitor();
        float mainScale = ImGuiImplGLFW.GetContentScaleForMonitor(Unsafe.BitCast<Hexa.NET.GLFW.GLFWmonitorPtr, Hexa.NET.ImGui.Backends.GLFW.GLFWmonitorPtr>(mon));

        ImGui.StyleColorsDark();
        var style = ImGui.GetStyle();
        // style.ScaleAllSizes(1.5f);

        style.ScaleAllSizes(mainScale);
        style.FontScaleDpi = mainScale;
        _io.ConfigDpiScaleFonts = true;
        _io.ConfigDpiScaleViewports = true;

        if ((_io.ConfigFlags & ImGuiConfigFlags.ViewportsEnable) != 0)
        {
            style.WindowRounding = 0.0f;
        }

        // Set fonts
        unsafe
        {
            string fontPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "Fonts", "Geist-Medium.ttf");
            if (!File.Exists(fontPath))
            {
                Logger.Error($"Font file not found at {fontPath}");
                // style.FontSizeBase = 18f;
            }
            else
            {
                _io.Fonts.AddFontFromFileTTF(fontPath);
                style.FontSizeBase = 18f;
            }
        }

        ImGuiImplGLFW.SetCurrentContext(_imGuiContext);
        if (!ImGuiImplGLFW.InitForOpenGL(Unsafe.BitCast<GLFWwindowPtr, Hexa.NET.ImGui.Backends.GLFW.GLFWwindowPtr>(_window), true))
        {
            Logger.Error("Failed to init ImGui Impl GLFW");
            GLFW.Terminate();
            return false;
        }

        ImGuiImplOpenGL3.SetCurrentContext(_imGuiContext);
        if (!ImGuiImplOpenGL3.Init(glslVersion))
        {
            Logger.Error("Failed to init ImGui Impl OpenGL3");
            GLFW.Terminate();
            return false;
        }

        _gl.Enable(GLEnableCap.Blend);
        _gl.BlendFunc(GLBlendingFactor.SrcAlpha, GLBlendingFactor.OneMinusSrcAlpha);
        _gl.ClearColor(0f, 0f, 0f, 0f); // Transparent background
        return true;
    }

    private bool InitGLFW()
    {
        unsafe
        {
            GLFW.SetErrorCallback((error, description) =>
            {
                # if DEBUG
                Logger.Error($"GLFW Error {error}: {Utils.DecodeStringUTF8(description)}");
                # endif
            });
        }

        unsafe
        {
            Logger.Info("Initializing GLFW Version: " + Utils.DecodeStringUTF8(GLFW.GetVersionString()));
        }

        // This code sets the platform to X11 instead of wayland. This only needs to be
        // done inside vscode for whatever reason. https://github.com/opentk/opentk/issues/1823
        string? sessionType = Environment.GetEnvironmentVariable("XDG_SESSION_TYPE");
        string? useWayland = Environment.GetEnvironmentVariable("GLFW_USE_WAYLAND");
        if (sessionType == "wayland" && useWayland == "0")
        {
            GLFW.InitHint(GLFW.GLFW_PLATFORM, GLFW.GLFW_PLATFORM_X11);
        }

        Console.WriteLine("Initializing GLFW...");
        GLFW.Init();
        GLFW.WindowHint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3);
        GLFW.WindowHint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 2);
        GLFW.WindowHint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only

        GLFW.WindowHint(GLFW.GLFW_TRANSPARENT_FRAMEBUFFER, 1);  // Transparent
        GLFW.WindowHint(GLFW.GLFW_DECORATED, 0);                // No window decorations
        GLFW.WindowHint(GLFW.GLFW_FLOATING, 1);                 // Always on top
        GLFW.WindowHint(GLFW.GLFW_FOCUSED, 0);                  // Start unfocused
        GLFW.WindowHint(GLFW.GLFW_FOCUS_ON_SHOW, 0);            // Start unfocused
        
        var mon = GLFW.GetPrimaryMonitor();
        int width, height;
        width = GLFW.GetVideoMode(mon).Width;
        height = GLFW.GetVideoMode(mon).Height;

        // NOTE: Width and height set to screen-1
        // If they are set to the screen size, windows does some optimizations that cause the window
        // to go full black when focused. Setting these to -1 seems to prevent that.
        _window = GLFW.CreateWindow(width-1, height-1, "ETS2LA overlay", null, null);
        if (_window.IsNull)
        {
            Logger.Error("Failed to create GLFW window");
            GLFW.Terminate();
            return false;
        }

        return true;
    }

    public void RegisterWindow(WindowDefinition def, Action renderAction, Optional<Action> renderContextMenuAction = default)
    {
        foreach (var window in _windows)
        {
            if (window.Definition.Title == def.Title)
            {
                window.Definition = def;
                window.Render = renderAction;
                window.RenderContextMenu = renderContextMenuAction.GetValueOrDefault(() => { });
                return;
            }
        }
        
        var newWindow = new ExternalWindow(def, renderAction, renderContextMenuAction.GetValueOrDefault(() => { }));
        _windows.Add(newWindow);
    }

    public void UnregisterWindow(WindowDefinition def)
    {
        _windows.RemoveAll(w => w.Definition.Title == def.Title);
    }
}
