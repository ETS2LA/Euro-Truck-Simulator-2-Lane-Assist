using ETS2LA.Game.SDK;
using ETS2LA.Logging;

using System.Numerics;
using Hexa.NET.ImGui;
using TruckLib;

namespace ETS2LA.Overlay.AR;

public class ARRenderer
{
    private CameraData cameraData;
    private List<ARRenderCallback> renderCallbacks = new();
    private Matrix4x4 thisFrameProjection;
    private Matrix4x4 thisFrameView;
    private int thisFrameOffsetX = 0;
    private int thisFrameOffsetZ = 0;

    public ARRenderer()
    {
        cameraData = CameraProvider.Current.GetCurrentData();
    }

    public void Render()
    {
        thisFrameProjection = default;
        thisFrameView = default;
        
        foreach (var callback in renderCallbacks)
        {
            try { callback.Render3D(); }
            catch (Exception ex)
            {
                Logger.Error($"Exception in AR render callback '{callback.Definition.Name}': {ex}");
            }
        }
    }

    public void RegisterRenderCallback(ARRenderCallback callback)
    {
        renderCallbacks.Add(callback);
    }

    public void UnregisterRenderCallback(ARRenderCallback callback)
    {
        renderCallbacks.Remove(callback);
    }

    public Matrix4x4 GetViewMatrix()
    {
        if (thisFrameView != default)
            return thisFrameView;
        

        thisFrameOffsetX = 512 * cameraData.cx;
        thisFrameOffsetZ = 512 * cameraData.cy;

        Vector3 camPos = new Vector3(
            cameraData.position.X, 
            cameraData.position.Y, 
            cameraData.position.Z
        );

        Quaternion camRot = new Quaternion(
            cameraData.rotation.X,
            cameraData.rotation.Y,
            cameraData.rotation.Z,
            cameraData.rotation.W
        );

        // The game's output is a bit weird, so we need to do adjustments to get it
        // to match what System.Numerics expects. There might be multiple inversions here?
        // TODO: Could be simplified?
        Quaternion invQuat = Quaternion.Conjugate(camRot);
        Vector3 euler = invQuat.ToEuler();
        Quaternion filteredRot = Quaternion.CreateFromYawPitchRoll(-euler.Y + (float)Math.PI, -euler.Z + (float)Math.PI, -euler.X);

        Matrix4x4 cameraWorldMatrix = Matrix4x4.CreateFromQuaternion(filteredRot) * 
                                      Matrix4x4.CreateTranslation(camPos);

        Matrix4x4.Invert(cameraWorldMatrix, out Matrix4x4 viewMatrix);
        thisFrameView = viewMatrix;
        return viewMatrix;
    }

    public Matrix4x4 GetProjectionMatrix()
    {
        if (thisFrameProjection != default)
            return thisFrameProjection;
        
        // Game uses 0-1 for depth, but System.Numerics expects -1 to 1.
        // Simple transpose is enough to convert.
        thisFrameProjection = Matrix4x4.Transpose(cameraData.projection);
        return thisFrameProjection;
    }

    public Vector2? WorldToScreen(Vector3 worldPos, int destinationWidth, int destinationHeight)
    {
        Matrix4x4 viewMatrix = GetViewMatrix();
        Matrix4x4 projectionMatrix = GetProjectionMatrix();

        worldPos.X -= thisFrameOffsetX;
        worldPos.Z -= thisFrameOffsetZ;
        Vector4 clipSpacePos = Vector4.Transform(new Vector4(worldPos, 1.0f), viewMatrix * projectionMatrix);
        if (clipSpacePos.W <= 0.1f) return null; // behind the camera

        // perspective divide to normalize coordinates
        // so that means x,y is -1 to 1 where 0,0 is the center
        Vector3 ndc = new Vector3(clipSpacePos.X, clipSpacePos.Y, clipSpacePos.Z) / clipSpacePos.W;
        // now -1 to 1 to screen coordinates
        float x = (ndc.X + 1.0f) * 0.5f * destinationWidth;
        float y = (1.0f - ndc.Y) * 0.5f * destinationHeight;

        return new Vector2(x, y);
    }

    public void Draw3DLine(Vector3 start, Vector3 end, UInt32 color)
    {
        Vector2? p1 = WorldToScreen(start, 3440, 1440);
        Vector2? p2 = WorldToScreen(end, 3440, 1440);

        if (p1.HasValue && p2.HasValue)
        {
            // Input is RBGA, but ImGui wants ABGR
            uint abgrColor = 
                ((color & 0xFF000000) >> 24) |
                ((color & 0x00FF0000) >> 8)  |
                ((color & 0x0000FF00) << 8)  |
                ((color & 0x000000FF) << 24); 
            ImGui.GetBackgroundDrawList().AddLine(p1.Value, p2.Value, abgrColor);
        }
    }
}