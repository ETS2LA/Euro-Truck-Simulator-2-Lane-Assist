from Modules.Semaphores.classes import Gate, TrafficLight, Position, Quaternion
from ETS2LA.Module import ETS2LAModule
import logging
import struct
import mmap
import time


class Module(ETS2LAModule):
    start_time = 0
    message_shown = False

    def imports(self):
        self.start_time = time.time()
        self.wait_for_buffer()

    def wait_for_buffer(self):
        self.buf = None
        while self.buf is None:
            size = 2080
            try:
                self.buf = mmap.mmap(0, size, r"Local\ETS2LASemaphore")
            except Exception:
                if time.time() - self.start_time > 5 and not self.message_shown:
                    logging.warning(
                        "ETS2LASemaphore buffer not found. Make sure the SDK is installed and the game is running. This plugin will wait until the buffer is available."
                    )
                    self.message_shown = True

            time.sleep(1)

    def get_route_information(self):
        if self.buf is None:
            return None

        try:
            semaphore_format = "fffffffffifii"
            total_format = "=" + semaphore_format * 40
            data = struct.unpack(total_format, self.buf[:2080])

            semaphores = []
            for i in range(0, 40):
                if data[9] == 1:
                    semaphore = TrafficLight(
                        Position(data[0], data[1], data[2]),
                        data[3],
                        data[4],
                        Quaternion(data[5], data[6], data[7], data[8]),
                        data[10],
                        data[11],
                        data[12],
                    )
                else:
                    semaphore = Gate(
                        Position(data[0], data[1], data[2]),
                        data[3],
                        data[4],
                        Quaternion(data[5], data[6], data[7], data[8]),
                        data[10],
                        data[11],
                        data[12],
                    )

                semaphores.append(semaphore)
                data = data[13:]

            return semaphores
        except Exception:
            logging.exception("Failed to read route information")
            return None

    def run(self):
        return self.get_route_information()
