using Hexa.NET.OpenGL;
using System.Numerics;
using ETS2LA.Game.SDK;
using ETS2LA.Logging;
using TruckLib;

namespace ETS2LA.ML.Vision;

public class VirtualCamera
{
    public uint FramebufferId { get; private set; }
    public uint TextureId { get; private set; }
    public uint DepthbufferId { get; private set; }

    public int Width { get; private set; }
    public int Height { get; private set; }

    public GL gl { get; private set; }
    public string Name { get; set; } = "";
    public Quaternion Rotation { get; set; } = Quaternion.Identity;
    public Vector3 PositionOffset { get; set; } = Vector3.Zero;
    public float FieldOfView { get; set; } = 90f;

    private readonly byte[] _pixelBuffer;
    private readonly object _pixelLock = new();

    public VirtualCamera(string name, int width, int height, GL gl, Quaternion rotation = default, Vector3 positionOffset = default, float fieldOfView = 90f)
    {
        Name = name;
        Width = width;
        Height = height;
        Rotation = rotation;
        PositionOffset = positionOffset;
        FieldOfView = fieldOfView;
        this.gl = gl;

        _pixelBuffer = new byte[Width * Height * 4]; // RGBA

        InitGLResources();
    }

    private void InitGLResources()
    {
        FramebufferId = gl.GenFramebuffer();
        gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, FramebufferId);

        TextureId = gl.GenTexture();
        gl.BindTexture(GLTextureTarget.Texture2D, TextureId);

        unsafe
        {
            gl.TexImage2D(
                GLTextureTarget.Texture2D, 
                0, 
                GLInternalFormat.Rgba8, 
                Width, 
                Height, 
                0, 
                GLPixelFormat.Rgba, 
                GLPixelType.UnsignedByte, 
                null
            );
        }

        gl.TexParameteri(GLTextureTarget.Texture2D, GLTextureParameterName.MinFilter, (int)GLTextureMinFilter.Linear);
        gl.TexParameteri(GLTextureTarget.Texture2D, GLTextureParameterName.MagFilter, (int)GLTextureMinFilter.Linear);

        gl.FramebufferTexture2D(
            GLFramebufferTarget.Framebuffer, 
            GLFramebufferAttachment.ColorAttachment0, 
            GLTextureTarget.Texture2D, 
            TextureId, 
            0
        );

        DepthbufferId = gl.GenRenderbuffer();
        gl.BindRenderbuffer(GLRenderbufferTarget.Renderbuffer, DepthbufferId);
        gl.RenderbufferStorage(GLRenderbufferTarget.Renderbuffer, GLInternalFormat.DepthComponent24, Width, Height);
        gl.FramebufferRenderbuffer(GLFramebufferTarget.Framebuffer, GLFramebufferAttachment.DepthAttachment, GLRenderbufferTarget.Renderbuffer, DepthbufferId);

        var status = gl.CheckFramebufferStatus(GLFramebufferTarget.Framebuffer);
        if (status != GLEnum.FramebufferComplete)
        {
            throw new Exception($"Framebuffer failed to initialize! Status: {status}");
        }

        gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, 0);
    }

    public Matrix4x4 GetViewProjectionMatrix(Vector3 truckPos, Quaternion truckRot)
    {
        Vector3 camPos = truckPos + Vector3.Transform(PositionOffset, truckRot);
        Quaternion camRot = truckRot * Rotation;

        Matrix4x4 cameraWorldMatrix = Matrix4x4.CreateFromQuaternion(camRot) * 
                                      Matrix4x4.CreateTranslation(camPos);

        Matrix4x4.Invert(cameraWorldMatrix, out Matrix4x4 view);

        Matrix4x4 projection = Matrix4x4.CreatePerspectiveFieldOfView(
            MathF.PI / 180f * FieldOfView,
            (float)Width / Height,
            0.1f,
            1000f
        );
        projection.M11 *= -1;

        return view * projection;
    }

    public void BeginRender()
    {
        gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, FramebufferId);
        gl.Viewport(0, 0, Width, Height);

        gl.Enable(GLEnableCap.DepthTest);
        gl.DepthFunc(GLDepthFunction.Lequal);
        
        gl.ClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        gl.Clear(GLClearBufferMask.ColorBufferBit | GLClearBufferMask.DepthBufferBit);
    }

    public void EndRender()
    {
        // We save the frame data to the buffer before switching back to the
        // default framebuffer. Plugins will then use this data to perform their own processing.
        lock (_pixelLock)
        {
            unsafe
            {
                fixed (byte* ptr = _pixelBuffer)
                {
                    gl.ReadPixels(
                        0, 0, 
                        Width, Height, 
                        GLPixelFormat.Rgba, 
                        GLPixelType.UnsignedByte, 
                        ptr
                    );
                }
            }
        }

        gl.Disable(GLEnableCap.DepthTest);
        gl.BindFramebuffer(GLFramebufferTarget.Framebuffer, 0);
    }

    public byte[] GetPixelData(byte[]? targetBuffer = null)
    {
        int requiredSize = Width * Height * 4;

        if (targetBuffer == null || targetBuffer.Length < requiredSize)
        {
            targetBuffer = new byte[requiredSize];
        }

        lock (_pixelLock)
        {
            Buffer.BlockCopy(_pixelBuffer, 0, targetBuffer, 0, requiredSize);
        }

        return targetBuffer;
    }
}