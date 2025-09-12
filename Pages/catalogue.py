from ETS2LA.UI import (
    ETS2LAPage,
    styles,
    Container,
    Text,
    Button,
    Icon,
    Image,
    Input,
    Alert,
    AdSense,
    Spinner,
    Space,
    Markdown,
    SendPopup,
)
from ETS2LA.Settings import GlobalSettings
from ETS2LA.Handlers import plugins
from ETS2LA.Utils.translator import _
from typing import Literal
import webbrowser
import threading
import requests
import random
import shutil
import time
import yaml
import git
import os

settings = GlobalSettings()


class CataloguePlugin:
    name: str
    overview: str
    description: str
    repository: str

    image_url: str
    version: str
    author: str

    type: Literal["plugin", "soundpack"] = "plugin"

    installed: bool = False
    installed_version: str = ""

    def __init__(
        self,
        name: str,
        overview: str,
        description: str,
        image_url: str,
        version: str,
        author: str,
        repository: str = "",
        type: Literal["plugin", "soundpack"] = "plugin",
    ):
        self.name = name
        self.overview = overview
        self.description = description
        self.image_url = image_url
        self.version = version
        self.author = author
        self.repository = repository
        self.type = type


class Page(ETS2LAPage):
    url = "/catalogue"
    refresh_rate = 10

    loading = False
    catalogue = {}
    catalogues = ["https://github.com/ETS2LA/plugins"]

    plugins: list[CataloguePlugin] = []
    selected_plugin: CataloguePlugin = None

    search_term: str = ""

    want_to_install: bool = False
    installing: bool = False
    installing_state: str = ""
    installing_error: str = ""

    want_to_uninstall: bool = False
    uninstalling: bool = False
    uninstalling_state: str = ""
    uninstalling_error: str = ""

    def get_catalogue_data(self, catalogue: str) -> str:
        url = catalogue
        if "github.com" in url:
            # ex. https://raw.githubusercontent.com/ETS2LA/plugins/refs/heads/main/catalogue.yaml
            url = (
                url.replace("github.com", "raw.githubusercontent.com")
                + "/refs/heads/main/catalogue.yaml"
            )

        response = requests.get(url)
        if response.status_code == 200:
            return yaml.safe_load(response.text)
        else:
            return {}

    def get_plugin_data(self, repository: str) -> CataloguePlugin:
        if repository == "":
            return None

        url = repository
        if "github.com" in url:
            # ex. https://raw.githubusercontent.com/ETS2LA/plugins/refs/heads/main/plugin.yaml
            url = (
                url.replace("github.com", "raw.githubusercontent.com")
                + "/refs/heads/main/plugin.yaml"
            )

        response = requests.get(url)
        if response.status_code == 200:
            data = yaml.safe_load(response.text)
            return CataloguePlugin(
                name=data.get("name", _("Unknown")),
                overview=data.get("overview", _("No overview provided.")),
                description=data.get("description", _("No description provided.")),
                image_url=data.get("image_url", ""),
                version=data.get("version", "0.0.0"),
                author=data.get("author", _("Unknown")),
                repository=repository,
            )

        return None

    def crawl_catalogue(self):
        self.plugins = []
        for item in self.catalogue.get("plugins", []):
            self.reset_timer()
            time.sleep(random.uniform(0.1, 0.5))  # Simulate network delay
            data = self.get_plugin_data(item.get("repository", ""))
            if data:
                self.plugins.append(data)

    def update_data(self):
        self.catalogue = self.get_catalogue_data(self.catalogues[0])
        self.crawl_catalogue()
        self.loading = False
        self.reset_timer()

    def refresh_data(self):
        self.loading = True
        self.plugins = []
        threading.Thread(target=self.update_data, daemon=True).start()

    def open_event(self):
        super().open_event()
        if self.plugins:
            return

        if not self.loading and not self.catalogue:
            self.refresh_data()

    def trigger_install_page(self):
        self.want_to_install = True

    def trigger_uninstall_page(self):
        self.want_to_uninstall = True

    def trigger_install(self, plugin: str):
        threading.Thread(
            target=self.install_plugin, args=(plugin,), daemon=True
        ).start()

    def trigger_uninstall(self, plugin: str):
        threading.Thread(
            target=self.uninstall_plugin, args=(plugin,), daemon=True
        ).start()

    def install_plugin(self, plugin: str):
        self.installing = True
        self.installing_state = _("Installing")
        self.installing_error = ""
        self.want_to_install = False

        target = None
        for p in self.plugins:
            if p.name == plugin:
                target = p
                break

        if not target:
            SendPopup(_("Plugin not found in the catalogue."))
            return

        try:
            # updating logic
            if target.installed_version != target.version:
                self.installing_state = _("Closing existing plugin processes")
                self.reset_timer()
                if plugins.match_plugin_by_folder(f"CataloguePlugins/{target.name}"):
                    if not plugins.stop_plugin(
                        folder=f"CataloguePlugins/{target.name}", stop_process=True
                    ):
                        raise Exception(_("Failed to stop existing plugin processes."))

                self.installing_state = _("Updating existing installation")
                self.reset_timer()
                repo = git.cmd.Git(f"CataloguePlugins/{target.name}")
                repo.stash()
                success = repo.pull()
                time.sleep(1)  # Wait a bit for user experience
                if success:
                    self.installing_state = _("Restarting plugin process")
                    self.reset_timer()
                    if not plugins.create_process(
                        folder=f"CataloguePlugins\\{target.name}"
                    ):
                        raise Exception(
                            _(
                                "Failed to start plugin background process, but the plugin files were updated."
                            )
                        )

                    self.installing_state = _("Success")
                    self.reset_timer()
                    self.installing = False
                    self.unselect_plugin()
                    SendPopup(
                        _("Plugin '{name}' updated successfully.").format(
                            name=target.name
                        )
                    )
                    return
                else:
                    self.installing_state = _("Failed")
                    self.reset_timer()
                    self.installing_error = _(
                        "Failed to update plugin '{name}'"
                    ).format(name=target.name)
                    SendPopup(self.installing_error)
                    return

            # install logic
            self.installing_state = _("Cloning repository")
            self.reset_timer()
            git.Repo.clone_from(target.repository, f"CataloguePlugins/{target.name}")
            if os.path.exists(f"CataloguePlugins/{target.name}/requirements.txt"):
                self.installing_state = _("Installing requirements")
                self.reset_timer()
                os.system(
                    f"pip install -r CataloguePlugins/{target.name}/requirements.txt"
                )

            self.installing_state = _("Starting plugin background process")
            self.reset_timer()
            if not plugins.create_process(folder=f"CataloguePlugins\\{target.name}"):
                raise Exception(
                    _(
                        "Failed to start plugin background process, but the plugin files were installed."
                    )
                )

            self.installing_state = _("Success")
            self.reset_timer()
            self.installing = False
            self.unselect_plugin()
            SendPopup(
                _("Plugin '{name}' installed successfully.").format(name=target.name)
            )
        except Exception as e:
            self.installing_state = _("Failed")
            self.reset_timer()
            self.installing_error = str(e)
            SendPopup(
                _("Failed to install plugin '{name}': {error}").format(
                    name=target.name, error=str(e)
                )
            )

    def uninstall_plugin(self, plugin: str):
        self.uninstalling = True
        self.uninstalling_state = _("Uninstalling")
        self.uninstalling_error = ""
        self.want_to_uninstall = False

        target = None
        for p in self.plugins:
            if p.name == plugin:
                target = p
                break

        if not target:
            SendPopup(_("Plugin not found in the catalogue."))
            return

        try:
            self.uninstalling_state = _("Closing plugin processes")
            self.reset_timer()
            if plugins.match_plugin_by_folder(f"CataloguePlugins/{target.name}"):
                if not plugins.stop_plugin(
                    folder=f"CataloguePlugins/{target.name}", stop_process=True
                ):
                    raise Exception(_("Failed to stop plugin processes."))

            self.uninstalling_state = _("Unregistering git repository")
            self.reset_timer()
            # Close any git handles
            if os.path.exists(f"CataloguePlugins/{target.name}/.git"):
                repo = git.Repo(f"CataloguePlugins/{target.name}")
                repo.git.clear_cache()
                del repo  # and delete the repo object from python

            # Wait a bit for user experience
            time.sleep(1)
            self.uninstalling_state = _("Removing plugin files")
            self.reset_timer()

            max_retries = 3
            retry_count = 0
            success = False
            while not success and retry_count < max_retries:
                try:
                    # Make read only files writable
                    for root, _dirs, files in os.walk(
                        f"CataloguePlugins/{target.name}", topdown=False
                    ):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                os.chmod(
                                    file_path, 0o666
                                )  # Magic value = writable by all
                            except Exception:
                                pass

                    shutil.rmtree(f"CataloguePlugins/{target.name}")
                    success = True
                except Exception:
                    retry_count += 1
                    self.uninstalling_state = _(
                        "Retrying removal ({cur}/{max})"
                    ).format(cur=retry_count, max=max_retries)
                    self.reset_timer()
                    time.sleep(1)

            if not success:
                raise Exception(
                    _("Failed to remove plugin files after {max} attempts").format(
                        max=max_retries
                    )
                )

            self.uninstalling_state = _("Success")
            self.reset_timer()
            self.uninstalling = False
            self.unselect_plugin()
            SendPopup(
                _("Plugin '{name}' uninstalled successfully.").format(name=target.name)
            )
        except Exception as e:
            self.uninstalling_state = _("Failed")
            self.uninstalling_error = str(e)
            SendPopup(
                _("Failed to uninstall plugin '{name}': {error}").format(
                    name=target.name, error=str(e)
                )
            )

    def select_plugin(self, plugin: str):
        for p in self.plugins:
            if p.name == plugin:
                self.selected_plugin = p
                break

    def unselect_plugin(self):
        self.want_to_install = False
        self.installing = False
        self.installing_state = ""
        self.installing_error = ""

        self.want_to_uninstall = False
        self.uninstalling = False
        self.uninstalling_state = ""
        self.uninstalling_error = ""

        self.search_term = ""
        self.selected_plugin = None

    def open_source_code(self, plugin: str):
        for p in self.catalogue.get("plugins", []):
            print(p)
            if p.get("name") == plugin:
                repository = p.get("repository", "")
                if repository:
                    webbrowser.open(repository)
                    return

        SendPopup(_("Couldn't find source code for this plugin."))

    def loading_screen(self) -> bool:
        if self.loading:
            with Container(
                styles.FlexVertical()
                + styles.Classname("w-full h-full items-center justify-center relative")
            ):
                with Spinner():
                    Icon("loader")

                # TRANSLATORS: This text is shown when the plugin catalogue is refreshing the database.
                Text(_("Refreshing..."), styles.Description())
                if self.plugins:
                    Text(
                        _("Found {count} plugins").format(count=len(self.plugins)),
                        styles.Classname(
                            "text-xs text-muted-foreground absolute bottom-2"
                        ),
                    )

                return True
        return False

    def render_plugin_card(self, plugin: CataloguePlugin):
        with Button(
            name=plugin.name,
            action=self.select_plugin,
            type="ghost",
            style=styles.FlexHorizontal()
            + styles.Classname("w-full border rounded-md p-4 gap-4 bg-input/10 h-max"),
        ):
            if plugin.image_url:
                Image(
                    url=plugin.image_url,
                    style=styles.Style(
                        width="60px",
                        height="60px",
                    )
                    + styles.Classname("rounded-md border"),
                )

            with Container(
                style=styles.FlexHorizontal()
                + styles.Gap("10px")
                + styles.Classname("justify-between text-left")
                + styles.Height("100%")
                + styles.Width("100%")
            ):
                with Container(styles.FlexVertical() + styles.Gap("5px")):
                    with Container(
                        styles.FlexHorizontal() + styles.Classname("gap-2 items-center")
                    ):
                        Text(plugin.name, styles.Classname("font-semibold"))
                    Text(plugin.overview, styles.Description())

                with Container(styles.FlexHorizontal() + styles.Gap("5px")):
                    if plugin.installed:
                        if plugin.version != plugin.installed_version:
                            with Container(
                                styles.Classname(
                                    "bg-input/30 rounded-md border px-2 py-1 h-min"
                                )
                            ):
                                Text(
                                    _("Update Available {new}").format(
                                        new=plugin.version,
                                    ),
                                    styles.Classname("text-xs"),
                                )
                        with Container(
                            styles.Classname(
                                "bg-input/30 rounded-md border px-2 py-1 h-min"
                            )
                        ):
                            Text(
                                _(f"{plugin.installed_version}"),
                                styles.Classname("text-xs"),
                            )

                    with Container(
                        styles.Classname(
                            "bg-input/30 rounded-md border px-2 py-1 h-min"
                        )
                    ):
                        Text(plugin.type.capitalize(), styles.Classname("text-xs"))

                    with Container(
                        styles.Classname(
                            "bg-input/30 rounded-md border px-2 py-1 h-min"
                        )
                    ):
                        Text(plugin.author, styles.Classname("text-xs"))

    def render_plugin_details(self):
        if not self.selected_plugin:
            return False

        installed = self.selected_plugin.installed
        with Container(
            styles.Classname("w-full h-full p-4 gap-4") + styles.FlexVertical()
        ):
            with Container(
                styles.FlexHorizontal()
                + styles.Gap("10px")
                + styles.Classname("items-center")
            ):
                with Button(action=self.unselect_plugin):
                    Icon("arrow-left")
                    Text(_("Back"), styles.Classname("font-semibold"))
                with Button(
                    name=self.selected_plugin.name, action=self.open_source_code
                ):
                    Icon("github")
                    Text(_("Source Code"), styles.Classname("font-semibold"))

                if installed:
                    with Button(action=self.trigger_uninstall_page):
                        Icon("trash-2")
                        Text(_("Uninstall"), styles.Classname("font-semibold"))
                    if (
                        self.selected_plugin.version
                        != self.selected_plugin.installed_version
                    ):
                        with Button(action=self.trigger_install_page, type="primary"):
                            Icon("download")
                            Text(_("Update"), styles.Classname("font-semibold"))
                else:
                    with Button(action=self.trigger_install_page, type="primary"):
                        Icon("download")
                        Text(_("Install"), styles.Classname("font-semibold"))

            with Container(
                styles.FlexHorizontal()
                + styles.Classname(
                    "w-full justify-between border rounded-md p-4 bg-input/10"
                )
            ):
                with Container(
                    styles.FlexVertical()
                    + styles.Gap("5px")
                    + styles.Classname("w-full")
                ):
                    with Container(
                        styles.FlexHorizontal()
                        + styles.Classname("justify-between w-full")
                    ):
                        with Container(
                            styles.FlexHorizontal()
                            + styles.Classname("gap-2 items-center")
                        ):
                            Text(self.selected_plugin.name, styles.Title())
                            with Container(
                                styles.Classname(
                                    "bg-input/30 rounded-md border px-2 py-1 h-min"
                                )
                            ):
                                Text(
                                    self.selected_plugin.version,
                                    styles.Classname("text-xs"),
                                )

                        with Container(
                            styles.FlexHorizontal()
                            + styles.Classname("gap-2 items-center")
                        ):
                            with Container(
                                styles.Classname(
                                    "bg-input/30 rounded-md border px-2 py-1 h-min"
                                )
                            ):
                                Text(
                                    self.selected_plugin.author,
                                    styles.Classname("text-xs"),
                                )

                    Markdown(
                        self.selected_plugin.description,
                        styles.Description() + styles.MaxWidth("700px"),
                    )

                if self.selected_plugin.image_url:
                    Image(
                        url=self.selected_plugin.image_url,
                        style=styles.Style(
                            width="100px",
                            height="100px",
                        )
                        + styles.Classname("rounded-md border"),
                    )

        return True

    def render_install_page(self):
        if not self.want_to_install:
            return False

        with Container(
            styles.FlexVertical()
            + styles.Classname("w-full h-full items-center justify-center relative")
        ):
            Text(
                _("Are you sure you want to install this plugin?")
                + "\n"
                + self.selected_plugin.name
                + " ("
                + self.selected_plugin.version
                + ")",
                styles.Classname("text-center"),
            )
            Text(
                _(
                    "ETS2LA is not responsible for any issues caused by 3rd party plugins."
                ),
                styles.Classname("text-xs text-muted-foreground"),
            )
            with Container(
                styles.FlexHorizontal() + styles.Gap("10px") + styles.Classname("pt-4")
            ):
                with Button(action=self.unselect_plugin, type="ghost"):
                    Icon("arrow-left")
                    Text(_("Cancel"), styles.Classname("font-semibold"))
                with Button(
                    action=self.trigger_install,
                    name=self.selected_plugin.name,
                    type="primary",
                ):
                    Icon("download")
                    Text(_("Install"), styles.Classname("font-semibold"))

        return True

    def render_installing_page(self):
        with Container(
            styles.FlexVertical()
            + styles.Classname("w-full h-full items-center justify-center relative")
        ):
            Text(
                _("Installing {plugin}").format(plugin=self.selected_plugin.name),
                styles.Classname("text-center"),
            )
            Text(
                self.installing_state, styles.Classname("text-xs text-muted-foreground")
            )
            if self.installing_error:
                Text(self.installing_error, styles.Classname("text-xs text-red-500"))
                with Button(action=self.unselect_plugin, type="ghost"):
                    Icon("x")
                    Text(_("Close"), styles.Classname("font-semibold"))

    def render_uninstalling_page(self):
        with Container(
            styles.FlexVertical()
            + styles.Classname("w-full h-full items-center justify-center relative")
        ):
            Text(
                _("Uninstalling {plugin}").format(plugin=self.selected_plugin.name),
                styles.Classname("text-center"),
            )
            Text(
                self.uninstalling_state,
                styles.Classname("text-xs text-muted-foreground"),
            )
            if self.uninstalling_error:
                Text(self.uninstalling_error, styles.Classname("text-xs text-red-500"))
                with Button(action=self.unselect_plugin, type="ghost"):
                    Icon("x")
                    Text(_("Close"), styles.Classname("font-semibold"))

    def render_uninstall_page(self):
        if not self.want_to_uninstall:
            return False

        with Container(
            styles.FlexVertical()
            + styles.Classname("w-full h-full items-center justify-center relative")
        ):
            Text(
                _("Are you sure you want to uninstall this plugin?")
                + "\n"
                + self.selected_plugin.name,
                styles.Classname("text-center"),
            )
            with Container(
                styles.FlexHorizontal() + styles.Gap("10px") + styles.Classname("pt-4")
            ):
                with Button(action=self.unselect_plugin, type="ghost"):
                    Icon("arrow-left")
                    Text(_("Cancel"), styles.Classname("font-semibold"))
                with Button(
                    action=self.trigger_uninstall,
                    name=self.selected_plugin.name,
                    type="primary",
                ):
                    Icon("trash-2")
                    Text(_("Uninstall"), styles.Classname("font-semibold"))

        return True

    def handle_search(self, search_term: str):
        self.search_term = search_term.lower()

    def header(self):
        with Container(
            styles.FlexHorizontal()
            + styles.Classname("w-full h-16 items-center justify-between")
            + styles.Padding("4px 4px 8px 4px")
        ):
            with Container(
                styles.FlexHorizontal() + styles.Classname("gap-2 items-center")
            ):
                Input(_("Search plugins..."), changed=self.handle_search)
                with Button(action=self.refresh_data, type="ghost"):
                    Icon("refresh-ccw")
                    Text(_("Refresh"), styles.Classname("text-xs"))

    def render(self):
        ads = settings.ad_preference

        if self.loading_screen():
            return

        if not self.plugins:
            with Container(
                styles.FlexVertical()
                + styles.Classname("w-full h-full items-center justify-center relative")
            ):
                Text(
                    _("No plugins found in the plugin catalogue."), styles.Description()
                )
                with Button(
                    action=self.refresh_data,
                    type="ghost",
                    style=styles.Classname("default mt-4"),
                ):
                    Icon("refresh-ccw")
                    Text(_("Refresh Catalogue"), styles.Classname("text-xs"))
                return

        if self.installing:
            self.render_installing_page()
            return

        if self.uninstalling:
            self.render_uninstalling_page()
            return

        if self.want_to_install and self.selected_plugin:
            if self.render_install_page():
                return

        if self.want_to_uninstall and self.selected_plugin:
            if self.render_uninstall_page():
                return

        if self.render_plugin_details():
            return

        self.want_to_install = False
        with Container(
            styles.Classname("w-full h-full p-4 gap-4") + styles.FlexVertical()
        ):
            self.header()

            installed_plugins = []
            not_installed_plugins = []
            for plugin in self.plugins:
                if (
                    self.search_term
                    and self.search_term not in plugin.name.lower()
                    and self.search_term not in plugin.overview.lower()
                    and self.search_term not in plugin.author.lower()
                ):
                    continue
                if os.path.exists(f"CataloguePlugins/{plugin.name}"):
                    plugin.installed = True
                    data = yaml.safe_load(
                        open(f"CataloguePlugins/{plugin.name}/plugin.yaml", "r").read()
                    )
                    plugin.installed_version = data.get("version", "")
                    installed_plugins.append(plugin)
                else:
                    plugin.installed = False
                    not_installed_plugins.append(plugin)

            with Container(
                styles.FlexVertical() + styles.Gap("20px") + styles.Padding("0px 4px")
            ):
                Text(_("Installed Plugins"), styles.Classname("font-semibold"))
                if not installed_plugins:
                    with Alert():
                        Text(_("No plugins are installed."), styles.Description())
                else:
                    for plugin in installed_plugins:
                        self.render_plugin_card(plugin)

            with Container(
                styles.FlexVertical() + styles.Gap("20px") + styles.Padding("0px 4px")
            ):
                Text(_("Available Plugins"), styles.Classname("font-semibold"))
                if ads >= 2:
                    with Container(
                        style=styles.FlexHorizontal()
                        + styles.Classname("justify-center")
                    ):
                        AdSense(
                            client="ca-pub-6002744323117854",
                            slot="3283698879",
                            style=styles.Style(
                                display="inline-block", width="100%", height="120px"
                            ),
                        )

                if not not_installed_plugins:
                    with Alert():
                        Text(
                            _("You have installed all available plugins."),
                            styles.Description(),
                        )
                else:
                    for plugin in not_installed_plugins:
                        self.render_plugin_card(plugin)

            Space(styles.Height("80px"))
