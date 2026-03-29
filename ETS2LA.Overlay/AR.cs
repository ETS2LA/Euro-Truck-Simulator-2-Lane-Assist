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
    
    private Dictionary<WindowDefinition, Delegate> WindowRenderers = new();
    private List<Tuple<string, string>> _consoleMessages = new();

    public bool IsOverlayFocused => _isInteracting;
    public bool ShowDemoWindow { get; set; } = false;
    public bool ShowConsole { get; set; } = true;
    public bool ShowARInfo { get; set; } = false;
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
        Logger.OnLog += (log) => {
            _consoleMessages.Add(log);
            if (_consoleMessages.Count > 100) { _consoleMessages.RemoveAt(0); }
        };

        Task.Run(() => RenderLoop());
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
            ImGui.End();
        }

        if (ShowDemoWindow)
            ImGui.ShowDemoWindow();

        if (ShowARInfo)
        {
            ImGui.Begin("Welcome!", ImGuiWindowFlags.AlwaysAutoResize);
            ImGui.SetWindowPos(new Vector2(OverlayWidth/2, OverlayHeight/2), ImGuiCond.Once);
            RenderARInfo();
            RenderWindowContextMenu(() => ShowARInfo = false);
            ImGui.End();
        }

        if (ShowConsole)
        {
            ImGui.SetNextWindowBgAlpha(0.5f);
            ImGui.Begin("Console", ImGuiWindowFlags.NoScrollbar | ImGuiWindowFlags.NoResize | ImGuiWindowFlags.NoSavedSettings | ImGuiWindowFlags.NoDecoration | ImGuiWindowFlags.AlwaysAutoResize);
            ImGui.SetWindowPos(new Vector2(10, 10), ImGuiCond.Once);
            RenderConsole();
            RenderWindowContextMenu(() => ShowConsole = false);
            ImGui.End();
        }

        foreach (var kvp in WindowRenderers)
        {
            var def = kvp.Key;
            var renderAction = kvp.Value;
            ImGui.SetNextWindowSize(new Vector2(def.Width.GetValueOrDefault(480), def.Height.GetValueOrDefault(320)), ImGuiCond.FirstUseEver);
            
            ImGui.Begin(def.Title, def.Flags.GetValueOrDefault(ImGuiWindowFlags.None));
            var isCollapsed = ImGui.IsWindowCollapsed();
            if (isCollapsed) {
                ImGui.End(); 
                continue; 
            }
            
            renderAction.DynamicInvoke();
            ImGui.End();
        }
    }

    private void RenderConsole()
    {
        for(int i = 10; i > 0; i--)
        {
            var color = new Vector4(1f, 1f, 1f, 1f);
            string level, message;
            level = _consoleMessages.ElementAtOrDefault(_consoleMessages.Count - i)?.Item1 ?? "";
            message = _consoleMessages.ElementAtOrDefault(_consoleMessages.Count - i)?.Item2 ?? "";
            if (string.IsNullOrEmpty(level) || string.IsNullOrEmpty(message)) { continue; }

            if (level == "ERR") { color = new Vector4(1f, 0.5f, 0.5f, 1f); }
            else if (level == "WRN") { color = new Vector4(1f, 1f, 0.5f, 1f); }
            else if (level == "INF") { color = new Vector4(0.5f, 0.5f, 1f, 1f); }
            else if (level == "OKK") { color = new Vector4(0.5f, 1f, 0.5f, 1f); }
            ImGui.TextColored(color, $"[{level}]");
            ImGui.SameLine();
            ImGui.Text(message);
        }
    }

    private void RenderARInfo()
    {
        ImGui.Text("*Shock* there's a new window here O_O");
        ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "This is the overlay that will eventually render information on top of the game. For C# we've actually made it a lot more than it was!");
        ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "Plugin developers now have full access... and I mean *full* access to ImGui for rendering, hopefully we'll see some interesting things come from that!");
        ImGui.TextColored(new Vector4(0.7f, 0.7f, 0.7f, 1f), "Right now we've just implemented the basics, and the telemetry plugin will show off some nice performance when rendering a lot of data.");
        ImGui.Separator();
        ImGui.Text("You can interact with the overlay by holding down");
        ImGui.SameLine();
        var controls = ControlsBackend.Current.GetRegisteredControls();        
        var interactKey = controls.FirstOrDefault(c => c.Definition.Id == Interact.Id);
        if (interactKey != null)
            ImGui.TextColored(new Vector4(1f, 0.5f, 0.5f, 1f), interactKey.ControlId.ToString());
        else 
            ImGui.TextColored(new Vector4(1f, 0.5f, 0.5f, 1f), "UNBOUND");
        ImGui.SameLine();
        ImGui.Text("(can be changed in the settings!)");
        ImGui.Text("The overlay is pretty much a full window system, there shouldn't be any crashes... hopefully... but if there are, report them!");
    }

    private unsafe void RenderWindowContextMenu(Action onClose)
    {
        if (ImGui.BeginPopupContextWindow((byte*)0, ImGuiPopupFlags.MouseButtonRight))
        {
            if (ImGui.MenuItem("Close"))
            {
                onClose?.Invoke();
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

        ImGui.StyleColorsDark();
        var style = ImGui.GetStyle();
        // style.ScaleAllSizes(1.5f);

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

    public void RegisterWindow(WindowDefinition def, Action renderAction)
    {
        if (WindowRenderers.ContainsKey(def))
        {
            Logger.Warn($"Window with title {def.Title} is already registered. Overwriting.");
        }
        WindowRenderers[def] = renderAction;
    }

    public void UnregisterWindow(WindowDefinition def)
    {
        if (!WindowRenderers.ContainsKey(def))
        {
            Logger.Warn($"Window with title {def.Title} is not registered. Cannot unregister.");
            return;
        }
        WindowRenderers.Remove(def);
    }
}
