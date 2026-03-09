using System;
using System.Runtime.InteropServices;

namespace ETS2LA.Overlay;

internal class WinHelpers
{
    public IntPtr WindowHandle;
    public bool IsClickThrough = true;
    private const int GWL_EXSTYLE = -20;
    private const long WS_EX_LAYERED = 0x00080000L;
    private const long WS_EX_TRANSPARENT = 0x00000020L;
    private const uint LWA_COLORKEY = 0x00000001;
    private const uint LWA_ALPHA = 0x00000002;
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_FRAMECHANGED = 0x0020;
    
    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW", SetLastError = true)]
    private static extern IntPtr GetWindowLongPtr64(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtrW", SetLastError = true)]
    private static extern IntPtr SetWindowLongPtr64(IntPtr hWnd, int nIndex, IntPtr dwNewLong);
    [DllImport("user32.dll", EntryPoint = "GetWindowLongW", SetLastError = true)]
    private static extern int GetWindowLong32(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll", EntryPoint = "SetWindowLongW", SetLastError = true)]
    private static extern int SetWindowLong32(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool SetForegroundWindow(IntPtr hWnd);
    

    private IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex)
    {
        return IntPtr.Size == 8 ? GetWindowLongPtr64(hWnd, nIndex) : new IntPtr(GetWindowLong32(hWnd, nIndex));
    }

    private IntPtr SetWindowLongPtr(IntPtr hWnd, int nIndex, IntPtr value)
    {
        return IntPtr.Size == 8 ? SetWindowLongPtr64(hWnd, nIndex, value) : new IntPtr(SetWindowLong32(hWnd, nIndex, value.ToInt32()));
    }

    public void MakeClickThrough()
    {
        if (WindowHandle == IntPtr.Zero) return;

        IntPtr style = GetWindowLongPtr(WindowHandle, GWL_EXSTYLE);
        long newStyle = style.ToInt64() | WS_EX_LAYERED | WS_EX_TRANSPARENT;

        SetWindowLongPtr(WindowHandle, GWL_EXSTYLE, new IntPtr(newStyle));
        //SetWindowPos(WindowHandle, IntPtr.Zero, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
        IsClickThrough = true;
    }

    public void MakeClickable()
    {
        if (WindowHandle == IntPtr.Zero) return;
        var ex = (long)GetWindowLongPtr(WindowHandle, GWL_EXSTYLE);
        ex &= ~(WS_EX_TRANSPARENT);
        ex |= WS_EX_LAYERED;
        SetWindowLongPtr(WindowHandle, GWL_EXSTYLE, new IntPtr(ex));
        SetLayeredWindowAttributes(WindowHandle, 0, 255, LWA_ALPHA);
        //SetWindowPos(WindowHandle, IntPtr.Zero, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED);
        
        IsClickThrough = false;
    }

    public void UnfocusWindow()
    {
        if (WindowHandle != IntPtr.Zero)
        {
            SetForegroundWindow(IntPtr.Zero);
        }
    }
}