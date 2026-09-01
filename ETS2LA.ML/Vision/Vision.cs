using Hexa.NET.OpenGL;

using System.Numerics;
using System.Diagnostics;

using ETS2LA.State;
using ETS2LA.Shared;
using ETS2LA.Logging;
using ETS2LA.Game.Telemetry;
using ETS2LA.Game.SDK;

using TruckLib.ScsMap;
using TruckLib;

namespace ETS2LA.ML.Vision;

public class VisionHandler
{
    private static readonly Lazy<VisionHandler> _instance = new(() => new VisionHandler());
    public static VisionHandler Current => _instance.Value;

    public List<VirtualCamera> Cameras { get; private set; } = new();
    public GL? gl;

    private int viewDistance = 300;
    private float nodeUpdateInterval = 5f; // seconds
    private IReadOnlyList<Node> nearbyNodes = new List<Node>();
    private List<Vector3> roadGeometryBuffer = new();

    private SolidColor? solidColor;
    private RoadMesh? roadMesh;
    private VehicleMesh? trafficMesh;
    private VehicleMesh? vehicleMesh;

    private bool shutdown = false;

    public bool Initialized => gl != null;

    public VisionHandler()
    {
    }

    public void Initialize(GL gl)
    {
        this.gl = gl;
        gl.DepthMask(true);
        
        // AddCamera("Left", 320, 480, 
        //     fieldOfView: 45f,
        //     rotation: Quaternion.CreateFromAxisAngle(Vector3.UnitY, -MathF.PI / 1.1f), 
        //     offset: new Vector3(1.25f, -0.5f, -2.5f));
        AddCamera("Front", 480, 480, 
            rotation: Quaternion.CreateFromAxisAngle(Vector3.UnitX, MathF.PI / 10f), 
            offset: new Vector3(0f, -1f, 3f));
        AddCamera("Top", 240, 480, 
            fieldOfView: 14f,
            rotation: Quaternion.CreateFromAxisAngle(Vector3.UnitX, MathF.PI / 2f), 
            offset: new Vector3(0f, -900f, 0f));
        // AddCamera("Right", 320, 480, 
        //     fieldOfView: 45f,
        //     rotation: Quaternion.CreateFromAxisAngle(Vector3.UnitY, MathF.PI / 1.1f), 
        //     offset: new Vector3(-1.25f, -0.5f, -2.5f));

        solidColor = new SolidColor(gl);
        roadMesh = new RoadMesh(gl);
        trafficMesh = new VehicleMesh(gl);
        vehicleMesh = new VehicleMesh(gl);

        Task.Run(() =>
        {
            while (!shutdown)
            {
                UpdateNearbyNodes();
                Thread.Sleep((int)(nodeUpdateInterval * 1000));
            }
        });
    }


    private void UpdateNearbyNodes()
    {
        var cameraData = CameraProvider.Current.GetCurrentData();
        if (cameraData == null) return;
        
        Vector3 center = cameraData.truckPosition;
        double minX = center.X - viewDistance;
        double maxX = center.X + viewDistance;
        double minZ = center.Z - viewDistance;
        double maxZ = center.Z + viewDistance;
        nearbyNodes = ApplicationState.Current.RunningGame?.GetMapData()?.Nodes.Within(minX, minZ, maxX, maxZ) ?? new List<Node>();

        roadGeometryBuffer = VisionRoadUtils.BuildRoadGeometry(nearbyNodes.ToArray());
    }

    public void Render()
    {
        var cameraData = CameraProvider.Current.GetCurrentData();
        if (gl == null) return;
        if (cameraData == null) return;

        Vector3 center = cameraData.truckPosition;
        Quaternion truckRot = cameraData.truckRotation;
        var euler = truckRot.ToEuler();
        euler.Y = -euler.Y - (float)Math.PI;
        truckRot = Quaternion.CreateFromYawPitchRoll(euler.Y, euler.X, euler.Z);

        // For road / prefab rendering
        Vector3[] currentFrameRoadVertices = new Vector3[roadGeometryBuffer.Count + 1];
        for (int i = 0; i < roadGeometryBuffer.Count; i++)
        {
            try { currentFrameRoadVertices[i] = roadGeometryBuffer[i] - center; }
            catch { }
        }
        roadMesh?.UpdateVertices(currentFrameRoadVertices);

        // For vehicle rendering
        var vehicleVertices = VisionVehicleUtils.BuildVehicleGeometry(
                              TrafficProvider.Current.GetCurrentTrafficData(),
                              ParkedVehiclesProvider.Current.GetCurrentParkedVehicleData());
        for(int i = 0; i < vehicleVertices.Count; i++)
            vehicleVertices[i] -= center;
        trafficMesh?.UpdateVertices(vehicleVertices);

        var truckVertices = VisionVehicleUtils.BuildCurrentVehicleGeometry();
        for(int i = 0; i < truckVertices.Count; i++)
            truckVertices[i] -= center;
        vehicleMesh?.UpdateVertices(truckVertices);

        solidColor?.Use();
        foreach (var camera in Cameras)
        {
            camera.BeginRender();
            solidColor?.SetViewProjection(camera.GetViewProjectionMatrix(Vector3.Zero, truckRot));

            solidColor?.SetColor(new Vector4(0.0f, 1.0f, 0.0f, 1.0f));
            roadMesh?.Draw();

            solidColor?.SetColor(new Vector4(1.0f, 0.0f, 0.0f, 1.0f));
            trafficMesh?.Draw();

            solidColor?.SetColor(new Vector4(0.0f, 0.0f, 1.0f, 1.0f));
            vehicleMesh?.Draw();

            camera.EndRender();
        }
        solidColor?.End();
    }

    public void AddCamera(string name, int width, int height, Quaternion? rotation = null, Vector3? offset = null, float fieldOfView = 90f)
    {
        if (gl == null)
        {
            Logger.Error("VisionHandler: Cannot add camera, GL context is not initialized.");
            return;
        }

        Cameras.Add(new VirtualCamera(name, width, height, gl, rotation ?? Quaternion.Identity, offset ?? Vector3.Zero, fieldOfView));
    }

    public void Shutdown()
    {
        shutdown = true;
    }
}