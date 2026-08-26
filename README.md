![](Assets/markdown_logo.png)

# ETS2LA
ETS2LA is a project that aims to finally bring self-driving technology to SCS Software's Truck Simulators. This page includes some information, but if you want to read all the documentation then please head over to [our website](https://ets2la.com)!

<img alt="Discord" src="https://img.shields.io/discord/1120719484982939790?style=for-the-badge&logo=discord"> <img alt="GitHub License" src="https://img.shields.io/github/license/ETS2LA/ETS2LA?style=for-the-badge">


### Important Links
- [Download](https://github.com/ETS2LA/ETS2LA/releases/latest) - Instructions on how to download and install the current version.
- [Discord](https://ets2la.com/discord) - Join our community to talk to the developers and get support.
- [Website](https://ets2la.com) - For troubleshooting and help. *Out of date with the current version!*
- [Docs](https://docs.ets2la.com) - Developer documentation. If you want to work on ETS2LA or plugins you should start here.

### I have a problem with ETS2LA
Please check the [FAQ](https://ets2la.com/faq) for answers. If your question is not listed there, please join the [Discord](https://ets2la.com/discord) and ask in the support channel. We will add the answer to the FAQ if it becomes a common question!

### Acknowledgements
- [SCS Software](https://scssoft.com) - For making Euro Truck Simulator 2 and American Truck Simulator.
- [TruckLib](https://github.com/sk-zk/TruckLib) - For being the project we use to extract game files. This version of ETS2LA is fundamentally linked to TruckLib.
- [ts-map](https://github.com/dariowouters/ts-map) and [maps](https://github.com/truckermudgeon/maps) - For their help and examples in parsing SCS map files and rendering a usable map.

---

> [!WARNING]  
> Information below this line is meant for **developers**. If you're a "normal" user then please use the information above.

### Building the Project
Download .NET 10 from Microsoft. You can find that [here](https://dotnet.microsoft.com/en-us/download/dotnet/10.0). You'll also have to install [Bun](https://bun.sh/).

Now clone the repository and open the solution file in your preferred IDE. We recommend [VSCode](https://code.visualstudio.com). Any code editor should work, but the project comes prepackaged with VSCode tasks for Windows and Linux. You should also download the `C# Dev Kit` extension, other IDEs should have their own equivalent extensions.

Before you can run ETS2LA, you'll need to make sure you have all the required dotnet tools installed. To install them, just run `dotnet restore` and `dotnet tool restore` in the **root** of the repository.

Building (and running) depends on your IDE. If you're using VSCode, you just press `F5`.

### Testing Translations
Weblate will commit translations every so often, usually within a few hours. However if you want to test your translations immediately, you can:
1. Click your language
2. At the top, click `Files`, then `Download original translation files as ZIP file`
3. Copy `ets2la/ets2la/ETS2LA.Translations/Localization/lang_code.po` into your local `ETS2LA.Translations/Localization/lang_code.po` folder.
4. Build ETS2LA, your new translations will be included.

You can also directly edit the translations files in `ETS2LA.Translations/Localization/`. **However**, do not upload those back to weblate. You can edit the files, and then in weblate edit the text manually. Uploading translation files can (and will) break credits as well as cause the loss of some translations.

### Contributing
Please read CONTRIBUTING.md for guidelines. We welcome all contributions, but please make sure to follow our guidelines to ensure a smooth review process. If you have any questions, feel free to ask in our Discord server. (https://ets2la.com/discord)

---

> [!NOTE]  
> For further information please check the documentation on https://docs.ets2la.com. It's where we gather our knowledgebase.
