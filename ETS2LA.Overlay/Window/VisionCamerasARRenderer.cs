using Hexa.NET.ImGui;
using ETS2LA.Controls;
using ETS2LA.ML.Vision;
using ETS2LA.Overlay.AR;
using ETS2LA.Game.SDK;
using System.Numerics;
using ETS2LA.Logging;
using TruckLib;

namespace ETS2LA.Overlay.Window;

public class VisionCamerasARRenderer
{
    private Vector3 Unproject(Vector3 ndc, Matrix4x4 invViewProj)
    {
        Vector4 p = Vector4.Transform(new Vector4(ndc, 1), invViewProj);
        return new Vector3(p.X, p.Y, p.Z) / p.W;
    }

    public void Register()
    {
        OverlayHandler.Current.AR.RegisterRenderCallback(new ARRenderCallback
        {
            Definition = new ARRendererDefinition
            {
                Name = "Vision Cameras",
                Alpha = 1f,
            },
            Render3D = () =>
            {
                if (VisionHandler.Current.gl == null) return;
                var AR = OverlayHandler.Current.AR;

                var gameCameraData = CameraProvider.Current.GetCurrentData();
                var rotation = gameCameraData.truckRotation;
                var euler = rotation.ToEuler();
                euler.Y = -euler.Y;
                rotation = Quaternion.CreateFromYawPitchRoll(euler.Y, euler.X, euler.Z);

                foreach (var virtualCamera in VisionHandler.Current.Cameras)
                {
                    var positionOffset = virtualCamera.PositionOffset;
                    positionOffset.X *= -1;
                    positionOffset.Z *= -1;
                    Vector3 cameraPos = Vector3.Transform(positionOffset, rotation);

                    AR.Draw3DCircle(
                        new ARCoordinate(cameraPos, ARCoordinateCenter.Truck),
                        2f,
                        0xFFFFFFFF);

                    AR.Draw3DText(
                        new ARCoordinate(cameraPos, ARCoordinateCenter.Truck),
                        virtualCamera.Name,
                        0xFFFFFFFF,
                        xFactor: -0.1f);

                    // Code below this line was written by Gemini.
                    Quaternion cameraRot = virtualCamera.Rotation;
                    var cameraRotEuler = cameraRot.ToEuler();
                    cameraRot = Quaternion.CreateFromYawPitchRoll(cameraRotEuler.Y, -cameraRotEuler.X, cameraRotEuler.Z);
                    cameraRot = rotation * cameraRot;
                    
                    Vector3 forward = Vector3.Normalize(Vector3.Transform(Vector3.UnitZ, cameraRot));
                    Vector3 right   = Vector3.Normalize(Vector3.Transform(Vector3.UnitX, cameraRot));
                    Vector3 up      = Vector3.Normalize(Vector3.Transform(Vector3.UnitY, cameraRot));

                    float near = 0.1f;
                    float far = 1f;

                    float aspect = (float)virtualCamera.Width / virtualCamera.Height;
                    float tanHalfFov = MathF.Tan(MathF.PI / 180f * virtualCamera.FieldOfView * 0.5f);

                    float nearHeight = near * tanHalfFov;
                    float nearWidth = nearHeight * aspect;

                    float farHeight = far * tanHalfFov;
                    float farWidth = farHeight * aspect;

                    Vector3 nearCenter = cameraPos + forward * near;
                    Vector3 farCenter = cameraPos + forward * far;

                    Vector3 ntl = nearCenter + up * nearHeight - right * nearWidth;
                    Vector3 ntr = nearCenter + up * nearHeight + right * nearWidth;
                    Vector3 nbr = nearCenter - up * nearHeight + right * nearWidth;
                    Vector3 nbl = nearCenter - up * nearHeight - right * nearWidth;

                    Vector3 ftl = farCenter + up * farHeight - right * farWidth;
                    Vector3 ftr = farCenter + up * farHeight + right * farWidth;
                    Vector3 fbr = farCenter - up * farHeight + right * farWidth;
                    Vector3 fbl = farCenter - up * farHeight - right * farWidth;

                    void Edge(Vector3 a, Vector3 b)
                    {
                        AR.Draw3DLine(
                            new ARCoordinate(a, ARCoordinateCenter.Truck),
                            new ARCoordinate(b, ARCoordinateCenter.Truck),
                            0xFF00FF88);
                    }

                    // Near plane
                    Edge(ntl, ntr);
                    Edge(ntr, nbr);
                    Edge(nbr, nbl);
                    Edge(nbl, ntl);

                    // Far plane
                    Edge(ftl, ftr);
                    Edge(ftr, fbr);
                    Edge(fbr, fbl);
                    Edge(fbl, ftl);

                    // Connect near and far
                    Edge(ntl, ftl);
                    Edge(ntr, ftr);
                    Edge(nbr, fbr);
                    Edge(nbl, fbl);
                }
            }
        });
    }
}