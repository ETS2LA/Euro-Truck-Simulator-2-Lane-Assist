# Framework
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from Plugins.AR.classes import Coordinate, Color, Fade, Line
from Modules.Traffic.classes import Vehicle


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Test",
        version="1.0",
        description="Test",
        modules=["Traffic", "TruckSimAPI"],
        listen=["*.py"],
        fps_cap=30,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    def init(self): ...

    def run(self):
        vehicles: list[Vehicle] = self.modules.Traffic.run()
        ar_data = []
        fade = Fade(1, 5, 80, 120)
        for vehicle in vehicles:
            path = vehicle.get_path_for(3)  # seconds

            offset = vehicle.position - path[-1]
            if offset.is_zero():
                continue

            total = len(path)
            for i in range(len(path) - 1):
                alpha = int(255 * (1 - (i / total)))
                if i != 0:
                    ar_data.append(
                        Line(
                            start=Coordinate(path[i].x, path[i].y, path[i].z),
                            end=Coordinate(path[i + 1].x, path[i + 1].y, path[i + 1].z),
                            color=Color(50, 255, 50, alpha),
                            thickness=4,
                            fade=fade,
                        )
                    )

        self.tags.AR = ar_data
