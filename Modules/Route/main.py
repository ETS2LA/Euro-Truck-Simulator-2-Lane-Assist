from Modules.Route.classes import RouteItem
from ETS2LA.Module import ETS2LAModule
import logging
import struct
import mmap
import time


class Module(ETS2LAModule):
    def imports(self):
        self.wait_for_buffer()
        self.last_update = 0
        self.last_data = []

    def wait_for_buffer(self):
        self.buf = None
        while self.buf is None:
            size = 96_000
            self.buf = mmap.mmap(0, size, r"Local\ETS2LARoute")
            time.sleep(0.1)

    def get_route_information(self, force=False):
        if self.buf is None:
            return []

        if not force and time.time() - self.last_update < 60:
            return self.last_data

        self.last_update = time.perf_counter()

        try:
            route_piece_format = "qff"
            total_format = "=" + route_piece_format * 6000
            data = struct.unpack(total_format, self.buf[:96_000])

            items = []
            for _i in range(0, 6000):
                if data[0] == 0:
                    break

                item = RouteItem(data[0], data[1], data[2])
                items.append(item)
                data = data[3:]

            self.last_data = items
            return items
        except Exception:
            logging.exception("Failed to read route information")
            return []

    def run(self, force=False):
        return self.get_route_information(force=force)
