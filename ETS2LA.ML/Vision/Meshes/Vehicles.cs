using Hexa.NET.OpenGL;
using System.Numerics;
using ETS2LA.Game.SDK;
using ETS2LA.Logging;
using TruckLib;

namespace ETS2LA.ML.Vision;

// This is basically just a container that tells OpenGL *what* to render. How it's rendered is determined
// by the shader we use. i.e. the included SolidColor shader.
public class VehicleMesh : IDisposable
{
    private readonly GL _gl;

    public uint Vao { get; private set; }
    public uint Vbo { get; private set; }

    public int VertexCount { get; private set; }

    public VehicleMesh(GL gl)
    {
        _gl = gl;

        Vao = _gl.GenVertexArray();
        Vbo = _gl.GenBuffer();

        _gl.BindVertexArray(Vao);
        _gl.BindBuffer(GLBufferTargetARB.ArrayBuffer, Vbo);

        unsafe
        {
            _gl.VertexAttribPointer(
                0,
                3,
                GLVertexAttribPointerType.Float,
                false,
                3 * sizeof(float),
                (void*)0);
        }

        _gl.EnableVertexAttribArray(0);

        _gl.BindVertexArray(0);
        _gl.BindBuffer(GLBufferTargetARB.ArrayBuffer, 0);
    }


    public unsafe void UpdateVertices(List<Vector3> vertices)
    {
        VertexCount = vertices.Count;

        if (VertexCount == 0)
            return;

        _gl.BindBuffer(
            GLBufferTargetARB.ArrayBuffer,
            Vbo);

        fixed(Vector3* ptr = vertices.ToArray())
        {
            _gl.BufferData(
                GLBufferTargetARB.ArrayBuffer,
                vertices.Count * sizeof(Vector3),
                ptr,
                GLBufferUsageARB.DynamicDraw);
        }

        _gl.BindBuffer(GLBufferTargetARB.ArrayBuffer, 0);
    }


    public void Draw()
    {
        if (VertexCount == 0)
            return;

        _gl.BindVertexArray(Vao);

        _gl.DrawArrays(
            GLPrimitiveType.Triangles,
            0,
            VertexCount);

        _gl.BindVertexArray(0);
    }


    public void Dispose()
    {
        if (Vao != 0)
            _gl.DeleteVertexArray(Vao);

        if (Vbo != 0)
            _gl.DeleteBuffer(Vbo);
    }
}

// This util class will build vehicle geometry from the data
// we get from the game. Just a simple box for each vehicle.
public static class VisionVehicleUtils
{
    public static List<Vector3> BuildVehicleGeometry(
        TrafficData? traffic,
        ParkedVehicleData? parked)
    {
        List<Vector3> vertices = new();

        if (parked != null)
        {
            foreach (var vehicle in parked.vehicles)
            {
                AddBox(
                    vertices,
                    vehicle.Position,
                    vehicle.Rotation,
                    vehicle.Size);
            }
        }

        if (traffic != null)
        {
            foreach (var vehicle in traffic.vehicles)
            {
                AddBox(
                    vertices,
                    vehicle.Position,
                    vehicle.Rotation,
                    vehicle.Size);

                foreach (var trailer in vehicle.trailers)
                {
                    AddBox(
                        vertices,
                        trailer.Position,
                        trailer.Rotation,
                        trailer.Size);
                }
            }
        }

        return vertices;
    }

    private static void AddBox(
        List<Vector3> vertices,
        Vector3 center,
        Quaternion rotation,
        Vector3 size)
    {
        Vector3 halfSize = size / 2f;
        Vector3[] corners =
        {
            new(-halfSize.X,-halfSize.Y,-halfSize.Z),
            new( halfSize.X,-halfSize.Y,-halfSize.Z),
            new( halfSize.X,-halfSize.Y, halfSize.Z),
            new(-halfSize.X,-halfSize.Y, halfSize.Z),

            new(-halfSize.X, halfSize.Y,-halfSize.Z),
            new( halfSize.X, halfSize.Y,-halfSize.Z),
            new( halfSize.X, halfSize.Y, halfSize.Z),
            new(-halfSize.X, halfSize.Y, halfSize.Z),
        };

        var euler = rotation.ToEuler();
        euler.Y = -euler.Y + (float)Math.PI;
        //euler.X = -euler.X + (float)Math.PI;
        rotation = Quaternion.CreateFromYawPitchRoll(euler.Y, euler.X, euler.Z);

        Matrix4x4 transform =
            Matrix4x4.CreateFromQuaternion(rotation) *
            Matrix4x4.CreateTranslation(center);

        for(int i = 0; i < corners.Length; i++)
            corners[i] = Vector3.Transform(corners[i], transform);

        int[] indices =
        {
            0,1,2, 0,2,3, // bottom
            4,6,5, 4,7,6, // top

            0,4,5, 0,5,1, // front
            1,5,6, 1,6,2, // right
            2,6,7, 2,7,3, // back
            3,7,4, 3,4,0  // left
        };

        foreach(var i in indices)
            vertices.Add(corners[i]);
    }
}