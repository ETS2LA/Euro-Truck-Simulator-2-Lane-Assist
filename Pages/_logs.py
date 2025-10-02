from ETS2LA.UI import (
    ETS2LAPage,
    ETS2LAPageLocation,
    styles,
    Text,
    Container,
    Button,
    Combobox,
    Separator,
)
from ETS2LA import variables
import traceback
import threading
import time
import os
import re


class Page(ETS2LAPage):
    url = "/plugin_logs"

    location = ETS2LAPageLocation.SIDEBAR
    title = "Logs"
    refresh_rate = 1

    target = ""
    files = []
    spinner = ["◐", "◓", "◑", "◒"]
    spinner_index = 0

    def ensure_refreshing(self):
        first = True
        while self.is_open() or first:
            variables.REFRESH_PAGES = True
            time.sleep(self.refresh_rate)
            first = False

    def discover_files(self):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return []

        files = []
        for file in os.listdir(log_dir):
            if file.endswith(".log"):
                files.append(os.path.join(log_dir, file))

        self.files = files

    def open_event(self):
        threading.Thread(target=self.ensure_refreshing, daemon=True).start()
        return super().open_event()

    def init(self):
        self.discover_files()

    def on_file_selected(self, value):
        self.target = value

    def remove_rich_tags(self, text):
        # matches [something] and [/something]
        return re.sub(r"\[.*?\]", "", text)

    def render_line(self, line):
        time = "-".join(line.split("-")[0:3]).strip()
        category = line.split("-")[3].strip()
        content = "-".join(line.split("-")[4:])

        color = "var(--foreground)"
        if "WRN" in category:
            color = "#EEC270"
        elif "ERR" in category or "EXC" in category:
            color = "#FF6E6E"
        elif "INF" in category:
            color = "#6EEB83"

        with Container(
            style=styles.Classname("p-2 rounded-md bg-input/30 border flex gap-2")
        ):
            Text(
                f"{time.split(' ')[1]}", style=styles.Classname("text-muted-foreground")
            )
            Separator(direction="vertical")
            Text(
                f"{category.split('[')[2].split(']')[0]}",
                style=styles.Style(color=color),
            )
            Separator(direction="vertical")
            Text(
                self.remove_rich_tags(content.lstrip()),
                style=styles.Classname("font-mono"),
            )

    def render_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                parts = []
                for line in lines[-100:][::-1]:
                    if "[0m" not in line:
                        parts.append(line)
                    else:
                        parts.append(line)
                        parts = parts[::-1]
                        self.render_line("".join(parts))
                        parts = []

                if parts and any("[0m" in part for part in parts):
                    parts = parts[::-1]
                    self.render_line("".join(parts))

        except Exception:
            text = traceback.format_exc()
            return Text(f"Error reading file:\n{text}")

    def render(self):
        if not variables.DEVELOPMENT_MODE:
            return Text(
                "Telemetry is only available in development mode.", styles.Description()
            )

        if not self.is_open():
            return Text("Please refresh the page or wait for it to load...")

        with Container(style=styles.Classname("p-4 flex flex-col gap-4")):
            with Container(style=styles.Classname("flex gap-2")):
                Combobox(
                    options=self.files,
                    changed=self.on_file_selected,
                    style=styles.Classname("flex-1"),
                )
                with Button(action=self.discover_files):
                    Text("Refresh Files")

            if self.target:
                Text(
                    f"{self.spinner[self.spinner_index]} Showing last 100 lines of {self.target.replace('logs\\', '').replace('logs/', '')}",
                    style=styles.Classname("text-muted-foreground"),
                )
                self.render_file(self.target)
                self.spinner_index = (self.spinner_index + 1) % len(self.spinner)
            else:
                Text(
                    "Please select a log file to view its contents.",
                    style=styles.Classname("text-muted-foreground"),
                )
