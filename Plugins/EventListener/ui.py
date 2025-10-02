from ETS2LA.UI import ETS2LAPage, ETS2LAPageLocation, Text, Container, styles, Separator
from Plugins.EventListener.logs import ETS2, ATS, LogMessage


class GameLogPage(ETS2LAPage):
    title = "Game Logs"
    location = ETS2LAPageLocation.SIDEBAR
    refresh_rate = 1
    url = "/logs"

    def format_timestamp(self, timestamp: float):
        from datetime import datetime

        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%H:%M:%S")

    def render_message(self, msg: LogMessage):
        with Container(
            styles.Classname("border rounded-lg bg-input/30 p-2 flex gap-4 items-start")
        ):
            color = "var(--foreground)"
            if "warning" in msg.message.lower():
                color = "#E6C562"  # Yellow
            elif "error" in msg.message.lower():
                color = "#ED6F6F"  # Red
            elif "ets2la" in msg.message.lower():
                color = "#6FCF97"  # Green

            Text(
                f"{self.format_timestamp(msg.timestamp)}",
                styles.Classname("text-muted-foreground"),
            )
            Separator(direction="vertical")
            Text(msg.message, styles.Style(color=color))

    def render(self):
        if not self.is_open():
            Text("Loading...")
            return

        with Container(
            style=styles.Style(padding="24px") + styles.Classname("flex flex-col gap-4")
        ):
            if not self.plugin:
                Text("The Event Listener plugin is not loaded.")
                return

            game = self.plugin.running_game()
            if not game:
                Text("No game is currently running.")
                return

            messages = ETS2.messages if game == "ETS2" else ATS.messages
            if not messages:
                Text("No log messages detected yet.")
                return

            Text(
                "Showing the last 50 log messages",
                styles.Classname("text-muted-foreground"),
            )

            for msg in messages[-50:][::-1]:  # Show only the last 50 messages
                if isinstance(msg, LogMessage):
                    self.render_message(msg)
