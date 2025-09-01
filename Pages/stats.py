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

    def __init__(self, output: multiprocessing.Queue):
        self.output = output
        threading.Thread(target=self.ram_thread, daemon=True).start()
        threading.Thread(target=self.unsupported_thread, daemon=True).start()
        while True:
            time.sleep(1)

    def ram_thread(self):
        while True:
            time.sleep(10)
            total = 0
            python = 0
            node = 0
            for proc in psutil.process_iter():
                try:
                    time.sleep(0.01)  # Prevents high CPU usage
                    if "python" in proc.name().lower():  # backend
                        total += proc.memory_percent()
                        python += proc.memory_percent()
                    if "node" in proc.name().lower():  # frontend
                        total += proc.memory_percent()
                        node += proc.memory_percent()

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
                        "python": python,
                        "node": node,
                    }
                }
            )

    def unsupported_thread(self) -> list[str]:
        while True:
            time.sleep(30)
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


class Page(ETS2LAPage):
    url = "/stats"
    refresh_rate = 5

    def init(self):
        threading.Thread(target=self.data_thread, daemon=True).start()

    data = {
        "ram": psutil.virtual_memory(),
        "python_mem_usage": 0.0,
        "python_per_type": [0.0, 0.0],
        "plugin_mem_usage": {},
        "unsupported": [],
    }

    def data_thread(self):
        self.input = multiprocessing.Queue()
        self.metrics_process = multiprocessing.Process(
            target=PerformanceMetrics, args=(self.input,), daemon=True
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
                    self.data["python_per_type"] = [
                        data["ram"]["python"],
                        data["ram"]["node"],
                    ]

            except multiprocessing.queues.Empty:
                continue
            time.sleep(1)

    def render(self):
        if "python_per_type" not in self.data:
            return

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

                process_mem, per_type = (
                    self.data["python_mem_usage"],
                    self.data["python_per_type"],
                )
                tooltip_text = f"```\n┏ Python: {round(per_type[0] * self.data['ram'].total / 100 / 1024**3, 1)} GB\n"

                try:
                    for key, value in self.data["plugin_mem_usage"].items():
                        tooltip_text += f"┃  {key}: {round(value * self.data['ram'].total / 100 / 1024**3, 1)} GB\n"
                except Exception:
                    pass

                if per_type[1] > 0:
                    tooltip_text += "┃\n"
                    tooltip_text += f"┣ Node: {round(per_type[1] * self.data['ram'].total / 100 / 1024**3, 1)} GB\n"

                tooltip_text += "┃\n"
                tooltip_text += f"┗ Total: {round(process_mem * self.data['ram'].total / 100 / 1024**3, 1)} GB\n```"

                with Tooltip() as t:
                    with t.trigger:
                        Text(
                            f"<- {round(process_mem, 1)}% ETS2LA",
                            style=styles.Description() + styles.Classname("text-xs"),
                        )
                    with t.content as c:
                        c.style = content_style
                        Markdown(tooltip_text)
