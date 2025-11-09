from ETS2LA.UI import ETS2LAPage, styles, Container, Text, Tooltip, Markdown
import multiprocessing
import threading
import psutil
import time

descriptions = {
    "trucksbook": "Trucksbook will invalidate any jobs you do while having ETS2LA running / the SDK installed.",
    "Nightwish.Tracker": "Jobs that are done with ETS2LA will not get Xps, and it can cause issues with tracker.",
}


class PerformanceMetrics:
    output: multiprocessing.Queue

    def __init__(self, output: multiprocessing.Queue, pids: list[int]):
        self.output = output
        self.pids = pids
        threading.Thread(target=self.ram_thread, daemon=True).start()
        threading.Thread(target=self.unsupported_thread, daemon=True).start()
        while True:
            time.sleep(1)

    def ram_thread(self):
        while True:
            python_memory = 0
            plugin_memory = {}
            for proc in psutil.process_iter():
                try:
                    time.sleep(0.01)  # Prevents high CPU usage
                    if "python" in proc.name().lower():  # ETS2LA proper
                        python_memory += proc.memory_percent()

                    if proc.pid in self.pids:  # Plugins
                        mem = proc.memory_percent()
                        plugin_memory[proc.pid] = mem

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass

            self.output.put(
                {
                    "ram": {
                        "total": psutil.virtual_memory(),
                        "python": python_memory,
                        "plugins": plugin_memory,
                    }
                }
            )
            time.sleep(10)

    def unsupported_thread(self) -> list[str]:
        while True:
            execs = descriptions.keys()
            found = []
            for p in psutil.process_iter():
                for app in execs:
                    try:
                        if app in p.name():
                            found.append(app)
                    except psutil.NoSuchProcess:
                        pass  # Usually indicates that a process has exited

            self.output.put({"unsupported": found})
            time.sleep(30)


class Page(ETS2LAPage):
    url = "/stats"
    refresh_rate = 5
    loading = True
    plugins_handler = None

    def init(self):
        threading.Thread(target=self.data_thread, daemon=True).start()

    data = {
        "ram": psutil.virtual_memory(),
        "python_mem_usage": 0.0,
        "plugin_mem_usage": {},
        "unsupported": [],
    }

    def data_thread(self):
        import ETS2LA.Handlers.plugins as p

        self.plugins_handler = p
        while self.plugins_handler.loading:
            time.sleep(0.1)

        self.loading = False
        self.input = multiprocessing.Queue()
        self.metrics_process = multiprocessing.Process(
            target=PerformanceMetrics,
            args=(self.input, [plugin.pid for plugin in self.plugins_handler.plugins]),
            daemon=True,
        )
        self.metrics_process.start()
        while True:
            try:
                data = self.input.get(timeout=1)
                if "unsupported" in data:
                    self.data["unsupported"] = data["unsupported"]
                if "ram" in data:
                    self.data["ram"] = data["ram"]["total"]
                    self.data["python_mem_usage"] = data["ram"]["python"]
                    self.data["plugin_mem_usage"] = data["ram"]["plugins"]

            except multiprocessing.queues.Empty:
                continue
            time.sleep(1)

    def format_bytes(self, size):
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
        while size > power:
            size /= power
            n += 1

        if size >= 1000:
            return f"{size:6.0f} {power_labels[n]}B"  # No decimal
        elif size >= 100:
            return f"{size:6.1f} {power_labels[n]}B"  # 1 decimal
        else:
            return f"{size:6.2f} {power_labels[n]}B"  # 2 decimals

    def render(self):
        if "plugin_mem_usage" not in self.data or self.loading:
            with Container(
                styles.FlexHorizontal()
                + styles.Style(
                    classname="w-full border rounded-lg justify-center shadow-md",
                    height="2.2rem",
                    padding="0 4px 0 0",
                    gap="4px",
                )
            ):
                with Tooltip() as t:
                    with t.trigger:
                        Text(
                            "Loading...",
                            style=styles.Description(),
                        )
                    with t.content as c:
                        Text(
                            "ETS2LA is still loading plugins, please wait for it to finish before viewing stats.",
                            style=styles.Classname("text-xs"),
                        )

        unsupported = self.data["unsupported"]
        if unsupported:
            with Container(
                styles.FlexHorizontal()
                + styles.Style(
                    classname="w-full border rounded-lg justify-center shadow-md",
                    height="2.2rem",
                    background="#321b1b",
                    padding="0 4px 0 0",
                    gap="4px",
                )
            ):
                with Tooltip() as t:
                    with t.trigger:
                        Text(
                            "Conflicting software!",
                            style=styles.Style(
                                classname="text-xs text-red-500 default"
                            ),
                        )
                    with t.content:
                        for app in unsupported:
                            Text(f"{app}", style=styles.Classname("text-xs"))
                            Text(
                                f"{descriptions.get(app, 'No description available')}",
                                style=styles.Classname("text-xs")
                                + styles.Description(),
                            )
        else:
            with Container(
                styles.FlexHorizontal()
                + styles.Classname("w-full border rounded-lg justify-center shadow-md")
                + styles.Height("2.2rem")
                + styles.Padding("0 4px 0 0")
                + styles.Gap("4px")
            ):
                content_style = styles.Style()
                content_style.background = "#1e1e1e"
                content_style.padding = "2px"
                content_style.classname = "border"
                with Tooltip() as t:
                    with t.trigger:
                        Text(
                            f"RAM: {round(self.data['ram'].percent, 1)}%",
                            style=styles.Description() + styles.Classname("text-xs"),
                        )
                    with t.content as c:
                        c.style = content_style
                        Markdown(
                            f"```\n{round(self.data['ram'].used / 1024**3, 1)} GB / {round(self.data['ram'].total / 1024**3, 1)} GB\n```"
                        )

                process_mem, per_plugin = (
                    self.data["python_mem_usage"],
                    self.data["plugin_mem_usage"],
                )
                tooltip_text = "```\n┏ Plugins\n"

                try:
                    for pid, usage in sorted(
                        per_plugin.items(), key=lambda item: item[1], reverse=True
                    ):
                        name = [
                            p.description.name
                            for p in self.plugins_handler.plugins
                            if p.pid == pid
                        ][0]
                        tooltip_text += f"┃  {self.format_bytes(usage * self.data['ram'].total / 100)} - {name}\n"
                except Exception:
                    pass

                tooltip_text += "┃\n"
                tooltip_text += f"┗ Total: {self.format_bytes(process_mem * self.data['ram'].total / 100)}\n```"

                with Tooltip() as t:
                    with t.trigger:
                        Text(
                            f"<- {round(process_mem, 1)}% ETS2LA",
                            style=styles.Description() + styles.Classname("text-xs"),
                        )
                    with t.content as c:
                        c.style = content_style
                        Markdown(tooltip_text)
