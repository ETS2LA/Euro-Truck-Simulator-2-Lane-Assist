using System.Numerics;
using Hexa.NET.OpenGL;
using ETS2LA.Logging;

namespace ETS2LA.ML.Vision;

// This basically tells OpenGL *how* to render the meshes we send to it.
// In this case it's just a solid color, but we could do more complex things like textures, lighting, etc...
public class SolidColor : IDisposable
{
    private readonly GL _gl;
    public uint Handle { get; private set; }

    private const string VertexShaderSource = @"
        #version 330 core
        layout (location = 0) in vec3 aPos;

        uniform mat4 uViewProjection;

        void main()
        {
            gl_Position = uViewProjection * vec4(aPos, 1.0);
        }
    ";

    private const string FragmentShaderSource = @"
        #version 330 core
        out vec4 FragColor;
        uniform vec4 uColor;

        void main()
        {
            FragColor = uColor;
        }
    ";

    public SolidColor(GL gl)
    {
        _gl = gl;

        uint vert = CompileShader(GLShaderType.VertexShader, VertexShaderSource);
        uint frag = CompileShader(GLShaderType.FragmentShader, FragmentShaderSource);

        Handle = _gl.CreateProgram();
        _gl.AttachShader(Handle, vert);
        _gl.AttachShader(Handle, frag);
        _gl.LinkProgram(Handle);

        _gl.DeleteShader(vert);
        _gl.DeleteShader(frag);
    }

    private uint CompileShader(GLShaderType type, string source)
    {
        uint shader = _gl.CreateShader(type);
        _gl.ShaderSource(shader, source);
        _gl.CompileShader(shader);
        return shader;
    }

    public void Use() => _gl.UseProgram(Handle);
    public void End() => _gl.UseProgram(0);

    public void SetViewProjection(Matrix4x4 matrix)
    {
        int location = _gl.GetUniformLocation(Handle, "uViewProjection");
        unsafe
        {
            _gl.UniformMatrix4fv(location, 1, false, (float*)&matrix);
        }
    }

    public void SetColor(Vector4 color)
    {
        int location = _gl.GetUniformLocation(Handle, "uColor");
        unsafe
        {
            _gl.Uniform4fv(location, 1, (float*)&color);
        }
    }

    public void Dispose()
    {
        if (Handle != 0)
        {
            _gl.DeleteProgram(Handle);
            Handle = 0;
        }
    }
}