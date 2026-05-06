using Hexa.NET.OpenGL;
using Avalonia.Data;

using ETS2LA.Logging;

namespace ETS2LA.Overlay.AR;

public struct ARRendererDefinition
{
    public string Name;
    public Optional<float> Alpha;
}

public class ARRenderCallback
{
    public ARRendererDefinition Definition;
    public Action Render3D = () => { };
}

/// <summary>
///  This class is used to render an ImGui window into a texture.
///  That texture can then be used to render the window in 3D space using
///  AddImageQuad().
/// </summary>
public unsafe class ARWindowBuffer
{
    public uint Fbo;
    public uint Texture;
    public int Width;
    public int Height;
    private GL _gl;

    public ARWindowBuffer(GL gl, int width, int height)
    {
        _gl = gl;
        Width = width;
        Height = height;

        // texture
        Texture = _gl.GenTexture();
        _gl.BindTexture(GLTextureTarget.Texture2D, Texture);
        _gl.TexImage2D(GLTextureTarget.Texture2D, 0, GLInternalFormat.Rgba, Width, Height, 0, GLPixelFormat.Rgba, GLPixelType.UnsignedByte, null);
        _gl.TexParameteri(GLTextureTarget.Texture2D, GLTextureParameterName.MinFilter, (int)GLTextureMinFilter.Linear);
        _gl.TexParameteri(GLTextureTarget.Texture2D, GLTextureParameterName.MagFilter, (int)GLTextureMagFilter.Linear);

        // framebuffer
        Fbo = _gl.GenFramebuffer();
        _gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, Fbo);
        _gl.FramebufferTexture2D(GLFramebufferTarget.Framebuffer, GLFramebufferAttachment.ColorAttachment0, GLTextureTarget.Texture2D, Texture, 0);

        if (_gl.CheckFramebufferStatus(GLFramebufferTarget.Framebuffer) != GLEnum.FramebufferComplete)
            Logger.Error("Framebuffer is not complete!");

        _gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, 0);
    }
}