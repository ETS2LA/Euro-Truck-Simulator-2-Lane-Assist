using Hexa.NET.ImGui;
using ETS2LA.Controls;
using ETS2LA.ML.Vision;
using System.Numerics;

namespace ETS2LA.Overlay.Window;

class VisionCamerasWindow : InternalWindow
{
    public VisionCamerasWindow()
    {
        Definition = new WindowDefinition
        {
            Title = "Vision Cameras",
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
                        ImGui.Text($"Camera {camera.Name} ({camera.Width}x{camera.Height})");
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