using Hexa.NET.ImGui;
using ETS2LA.Controls;
using static ETS2LA.Translations.T;
using ETS2LA.ML.Vision;
using System.Numerics;

namespace ETS2LA.Overlay.Window;

class VisionCamerasWindow : InternalWindow
{
    public VisionCamerasWindow()
    {
        Definition = new WindowDefinition
        {
            Title = _("Vision Cameras"),
            Flags = ImGuiWindowFlags.AlwaysAutoResize,
        };

        IsWindowOpen = false;

        Render = () =>
        {
            unsafe
            {
                if (ImGui.BeginTable("CameraTable", 3, ImGuiTableFlags.NoPadInnerX))
                {
                    int cameraIndex = 0;
                    foreach (var camera in VisionHandler.Current.Cameras)
                    {
                        ImGui.TableNextColumn();
                        ImGui.Text(_("Camera {0} ({1}x{2})", camera.Name, camera.Width, camera.Height));
                        var texRef = new ImTextureRef(
                            texId: new ImTextureID((nint)camera.TextureId)
                        );

                        ImGui.Image(texRef, new Vector2(camera.Width, camera.Height));
                        cameraIndex++;
                    }
                    ImGui.EndTable();
                }
            }
        };
    }
}