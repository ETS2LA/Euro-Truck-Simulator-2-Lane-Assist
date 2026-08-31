using Hexa.NET.OpenGL;

using ETS2LA.Shared;
using ETS2LA.Logging;
using System.Numerics;

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

public enum ARCoordinateCenter
{
    World,
    Truck,
    Camera
}

/// <summary>
///  The conversion from this struct to vector3's is done in AR.cs.
///  You can access the functions there.
/// </summary>
public struct ARCoordinate
{
    public float OffsetX;
    public float OffsetY;
    public float OffsetZ;
    public ARCoordinateCenter Center;

    public ARCoordinate(float offsetX, float offsetY, float offsetZ, ARCoordinateCenter center = ARCoordinateCenter.World)
    {
        OffsetX = offsetX;
        OffsetY = offsetY;
        OffsetZ = offsetZ;
        Center = center;
    }

    public ARCoordinate(Vector3 offset, ARCoordinateCenter center = ARCoordinateCenter.World)
    {
        OffsetX = offset.X;
        OffsetY = offset.Y;
        OffsetZ = offset.Z;
        Center = center;
    }

    public static implicit operator ARCoordinate(Vector3 offset) 
        => new ARCoordinate(offset);

    public Vector3 OffsetToVector3()
    {
        return new Vector3(OffsetX, OffsetY, OffsetZ);
    }
    
    public static ARCoordinate operator +(ARCoordinate a, ARCoordinate b)
    {
        if (a.Center != b.Center)
            throw new InvalidOperationException("Cannot add ARCoordinates with different centers.");

        return new ARCoordinate(a.OffsetX + b.OffsetX, a.OffsetY + b.OffsetY, a.OffsetZ + b.OffsetZ, a.Center);
    }

    public static ARCoordinate operator -(ARCoordinate a, ARCoordinate b)
    {
        if (a.Center != b.Center)
            throw new InvalidOperationException("Cannot subtract ARCoordinates with different centers.");

        return new ARCoordinate(a.OffsetX - b.OffsetX, a.OffsetY - b.OffsetY, a.OffsetZ - b.OffsetZ, a.Center);
    }

    public static ARCoordinate operator *(ARCoordinate a, float scalar)
    {
        return new ARCoordinate(a.OffsetX * scalar, a.OffsetY * scalar, a.OffsetZ * scalar, a.Center);
    }

    public static ARCoordinate operator *(float scalar, ARCoordinate a)
    {
        return new ARCoordinate(a.OffsetX * scalar, a.OffsetY * scalar, a.OffsetZ * scalar, a.Center);
    }
    
    public static ARCoordinate InDirection(Quaternion rotation, float distance, ARCoordinateCenter center = ARCoordinateCenter.World)
    {
        Vector3 forward = Vector3.Transform(Vector3.UnitZ, rotation);
        return new ARCoordinate(forward * distance, center);
    }

    public static ARCoordinate FromAngles(float yaw, float pitch, float roll, float distance, ARCoordinateCenter center = ARCoordinateCenter.World)
    {
        Quaternion rotation = Quaternion.CreateFromYawPitchRoll(yaw, pitch, roll);
        return InDirection(rotation, distance, center);
    }
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