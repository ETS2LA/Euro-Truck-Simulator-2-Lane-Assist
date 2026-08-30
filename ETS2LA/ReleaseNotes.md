### ETS2LA C# 2026.8.30 [NIGHTLY]
This is the first major ETS2LA release after the initial launch a month ago. The headline feature this release is an **Improved User Interface** and **Translations**.

You might've also noticed that we transitioned to a new versioning system. All ETS2LA versions now use the following format:
- `YEAR.MONTH.COMMIT` - For example: `2026.8.4933`

This simplifies versioning for us, and provides information on how old a specific ETS2LA version is without having to check the Github releases page. You'll also see how many actual updates have happened between each release by comparing the `COMMIT` numbers.

### Changelog
- Implemented new web based UI via `photino` and `blazor`. This runs via your system's default webview provider.
- Implemented new translations framework at `ETS2LA.Translations`, this allows translation of ETS2LA, as well as our core plugins.
- Implemented the ability for plugins to create their own UIs in the ETS2LA window. These are called `adjustments`, however plugins can create as many pages as they wish. These pages are accessed through a button in the manager.
- ETS2LA has now transitioned to a new font called `Outfit`. This will be used on all our websites in the future.
- You can now change the ETS2LA window zoom, though we automatically scale based on DPI, this could be useful for languages that use complex characters, such as Chinese or Japanese.
- Added new onboarding process, this replaces the old somewhat confusing tutorial. `ETS2LA.Tutorials` is removed and no longer available for plugins.

---
<!-- Content inside ETS2LA will be cutoff at the line above, do not place lines inside the changelog. -->

> [!CAUTION]
> 如果您来自中国，可访问 [https://cnb.cool/ETS2LA-CN/Euro-Truck-Simulator-2-Lane-Assist/-/releases/latest](https://cnb.cool/ETS2LA-CN/Euro-Truck-Simulator-2-Lane-Assist/-/releases/latest) 这是我们官方的中国镜像仓库，从该仓库下载和安装的文件会优先使用中国仓库进行更新；另外这是开源免费项目，如发现有倒卖/安装收费行为，中国镜像站运营负责人有权利封禁你的ip，如遭遇ip封禁请不要提请任何申诉，我们不会受理  
<sub>The above notice is to make sure Chinese people can find their specific download. They can't download from GitHub without a VPN.</sub>

> [!WARNING]
> If you have issues with your **overlay being fully opaque**, make sure to reinstall your graphics card drivers.  
> **NVIDIA** - Set `OpenGL GDI Compatibility` to `Prefer Compatible` in the **NVIDIA App**.  
> **AMD** - Disable **HDR** in Windows settings.

<sub>ETS2LA is version specific, make sure you use a supported version!  
Older versions are not kept compatible with server side changes.</sub>
<!-- Please include a link to the latest working version for each game version. -->
<!-- 1.59 and 1.60 share the same map data version -->
| Game Version  |  ETS2LA Version  |
| ------------- | ---------------- |
| **1.61**      | *Not Supported*  |
| **1.60**      | [**≥ 3.4.0**](https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist/releases/latest) |
| **1.59**      | [**≥ 3.2.0**](https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist/releases/latest) |

You can download the **latest version** from here.   
**Don't use this if you're not on the latest game version!**

[![Download ETS2LA](https://a.fsdn.com/con/app/sf-download-button)](https://sourceforge.net/projects/ets2la/files/latest/download)

Or download directly from GitHub below:
| Operating System  |      Installer File       | Additional Requirements |
| ----------------- | ------------------------- | ----------------------- |
| Windows           | `ETS2LA-win-*.msi`        | Included                |
| Linux             | `ETS2LA-linux-*.AppImage` | **GLIBC 2.43**          |

<sub>If you're running your game in Proton, please install the Windows version inside the proton instance.  
Press **_Assets_** below to download the installer.</sub>