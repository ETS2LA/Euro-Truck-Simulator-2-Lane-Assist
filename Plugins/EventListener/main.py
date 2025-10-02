# Framework
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from ETS2LA.Events import events as event_system
from ETS2LA.Utils.translator import _
from ETS2LA import variables

from Plugins.EventListener.events import ProfileSelected, GameStarted, JobSelected
from Plugins.EventListener.logs import ETS2, ATS, LogMessage
from Plugins.EventListener.ui import GameLogPage

import logging

page = None
if variables.DEVELOPMENT_MODE:
    page = GameLogPage


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("Event Listener"),
        version="1.0",
        description=_(
            "This plugin listens to the events provided by the game SDK and the log files."
        ),
        modules=["TruckSimAPI"],
        tags=["Base", "Events"],
        listen=["*.py"],
        fps_cap=1,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    pages = [page]

    def init(self): ...

    def running_game(self) -> str | None:
        api = self.modules.TruckSimAPI.run()
        if not api["sdkActive"]:
            return None

        return api["scsValues"]["game"]

    def detect_events(self, line: str):
        # New profile selected: 'Development'
        if "New profile selected:" in line:
            profile_name = (
                line.split("New profile selected: ")[1].strip().replace("'", "")
            )
            ProfileSelected().trigger(event_system, profile_name=profile_name)
            logging.info(f"Emitted profile_selected event for profile: {profile_name}")

        # Euro Truck Simulator 2 init ver.1.56.1.5s (rev. 20d0f188bf69)
        if "init ver." in line:
            game = self.running_game()
            GameStarted().trigger(event_system, game=game)

        if "[job selection]: " in line and "from" in line and "to" in line:
            try:
                parts = line.split("[job selection]: ")[1].strip().split(" ")
                parts = [p for p in parts if p not in ["from", "to"]]
                cargo = parts[0].replace("'", "")
                from_company = parts[1].replace("'", "")
                to_company = parts[2].replace("'", "")

                JobSelected().trigger(
                    event_system,
                    cargo=cargo,
                    from_company=from_company,
                    to_company=to_company,
                )
                logging.info(
                    f"Emitted job_selected event for cargo: {cargo}, from: {from_company}, to: {to_company}"
                )
            except Exception as e:
                logging.error(f"Failed to parse job selection line: {line}. Error: {e}")
        ...

    def run(self):
        game = self.running_game()
        if not game:
            return

        new_lines: list[LogMessage] = ETS2.update() if game == "ETS2" else ATS.update()
        for line in new_lines:
            self.detect_events(line.message)
