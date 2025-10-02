import ETS2LA.variables as variables
from ETS2LA.UI import SendPopup
from typing import Literal
import logging
import time
import os


class LogMessage:
    timestamp: float
    message: str

    def __init__(self, timestamp: float = 0, message: str = ""):
        self.timestamp = timestamp
        self.message = message


class Log:
    game: Literal["ets2", "ats"]
    messages: list[LogMessage]

    _start_time: float
    _filepath: str
    _last_modified: float = 0

    def __init__(self, game: Literal["ets2", "ats"], filepath: str):
        self.game = game
        self._start_time = time.perf_counter()
        self._filepath = filepath
        self.messages = []

    def parse_creation_line(self, line: str):
        # Handle and parse ************ : log created on : Tuesday September 30 2025 @ 13:14:05
        if "log created on" in line.lower():
            try:
                timestamp_str = line.split("log created on : ")[1].strip()
                timestamp = time.mktime(
                    time.strptime(timestamp_str, "%A %B %d %Y @ %H:%M:%S")
                )
                logging.info(f"Log created for game {self.game} at {timestamp}")
                SendPopup(
                    f"Found {self.game.upper()}! Log created at {time.ctime(timestamp)}."
                )
                self._start_time = timestamp
                self.messages = []
            except Exception:
                logging.exception(
                    f"[LogReader] Failed to parse log creation time from line: {line.strip()}"
                )

    def update(self) -> list[LogMessage]:
        try:
            modified = os.path.getmtime(self._filepath)
        except Exception:
            return []

        if modified > self._last_modified:
            self._last_modified = modified
            new_messages: list[LogMessage] = []
            with open(self._filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                inverted = False

                # Parse the initial log message.
                # If that's been done then invert the lines to read from the end
                # to not read the whole log file.
                if len(lines) < len(self.messages) or len(self.messages) == 0:
                    self.parse_creation_line(lines[0])
                    lines = lines[1:]
                else:
                    lines = lines[::-1]
                    inverted = True

                latest_message = self.messages[-1].timestamp if self.messages else 0
                for line in lines:
                    try:
                        timestamp_str = line.split(" : ")[0].strip()  # HH:MM:SS.mmm
                        hours, minutes, seconds = timestamp_str.split(":")
                        seconds, milliseconds = seconds.split(".")
                        timestamp = (
                            self._start_time
                            + (float(hours) * 3600)
                            + (float(minutes) * 60)
                            + float(seconds)
                            + float(milliseconds) / 1000
                        )
                        if timestamp > latest_message:
                            message = line.split(" : ", 1)[1].strip()
                            new_messages.append(
                                LogMessage(timestamp=timestamp, message=message)
                            )
                        else:
                            break  # We've reached already known messages
                    except Exception as e:
                        logging.error(
                            f"Failed to parse log line: {line.strip()}, error: {e}"
                        )

            if inverted:
                new_messages = new_messages[::-1]  # Revert to original order

            self.messages += new_messages
            return new_messages

        return []  # No new messages


ETS2 = Log("ets2", variables.ETS2_LOG_PATH)
ATS = Log("ats", variables.ATS_LOG_PATH)
