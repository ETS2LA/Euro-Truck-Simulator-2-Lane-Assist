// NOTE: You should not use this system for generating plugin windows.
//       Please make your custom windows with OverlayHandler.RegisterWindow instead!

namespace ETS2LA.Overlay.Window;

class InternalWindow
{
    public WindowDefinition Definition;
    public Action Render = () => { };
    public Action RenderContextMenu = () => { };

    public bool IsWindowOpen = true;
}

class ExternalWindow : InternalWindow
{
    public ExternalWindow(WindowDefinition definition, Action renderAction, Action renderContextMenuAction)
    {
        Definition = definition;
        Render = renderAction;
        RenderContextMenu = renderContextMenuAction;
    }
}