"""Settings classes for ETS2LA.

Example usage:
```python
from ETS2LA.Settings import ETS2LASettings

class MySettings(ETS2LASettings):
    value: int = 10
    some_text: str = "Hello, World!"

settings = MySettings("category_name")
settings.value # 10
settings.some_text = "Great!"
settings.some_text # "Great!"
```
"""

import json
import sqlite3
import threading
from typing import Any

root_path = "ETS2LA/settings.db"
_JSON_PREFIX = "json:"


def _init_db():
    conn = sqlite3.connect(root_path, timeout=0.1, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS settings (
    category TEXT,
    key TEXT,
    value TEXT,
    PRIMARY KEY (category, key)
    )
    """
    )
    conn.close()


_init_db()


class ETS2LASettings:
    _listener_thread_object: threading.Thread = None
    _listener_function_calls: list = []

    def __init__(self, category: str) -> None:
        self._category = category
        self._cache = {}
        self._lock = threading.RLock()

        for key, _typ in getattr(self.__class__, "__annotations__", {}).items():
            default = getattr(self.__class__, key, None)
            self._cache[key] = default

        self._load_from_db()

    def _get_connection(self):
        return sqlite3.connect(root_path, timeout=0.1, isolation_level=None)

    def defer(self, func, args, time):
        timer = threading.Timer(time, func, args=args)
        timer.daemon = True
        timer.start()

    def _serialize_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (str, int, float)):
            return str(value)
        try:
            return _JSON_PREFIX + json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Unsupported setting value for {self._category}: {type(value).__name__}"
            ) from exc

    def _deserialize_value(self, raw_value: str, default: Any) -> Any:
        if raw_value.startswith(_JSON_PREFIX):
            try:
                return json.loads(raw_value[len(_JSON_PREFIX) :])
            except (TypeError, ValueError):
                return default

        if raw_value.startswith("b'") or raw_value.startswith('b\"'):
            return default

        typ = type(default)
        try:
            if typ is bool:
                return raw_value.lower() in ("true", "1", "yes")
            if default is None:
                return raw_value
            return typ(raw_value)
        except Exception:
            return raw_value

    def _load_from_db(self, i=0):
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT key, value FROM settings WHERE category = ?",
                    (self._category,),
                )
                for key, value in cur.fetchall():
                    if key in self._cache:
                        self._cache[key] = self._deserialize_value(
                            value, self._cache[key]
                        )

        except sqlite3.OperationalError:
            if i < 5:
                self.defer(self._load_from_db, [i + 1], 0.1 + 0.05 * i)

    def __getattribute__(self, name):
        if name.startswith("_") or name in (
            "__class__",
            "__dict__",
            "__annotations__",
            "listen",
            "stop_listen",
            "defer",
        ):
            return super().__getattribute__(name)

        cache = super().__getattribute__("_cache")
        if name in cache:
            return cache[name]

        if name not in self.__dict__:
            return None

        return super().__getattribute__(name)

    def __setattr__(self, name, value, i=0):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        with self._lock:
            self._cache[name] = value
            serialized_value = self._serialize_value(value)
            try:
                with self._get_connection() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO settings (category, key, value) VALUES (?, ?, ?)",
                        (self._category, name, serialized_value),
                    )

            except sqlite3.OperationalError:
                if i < 5:
                    self.defer(self.__setattr__, [name, value, i + 1], 0.1 + 0.05 * i)

    def _listener_thread(self):
        last_cache = self._cache.copy()
        while True:
            threading.Event().wait(1)
            self._load_from_db()

            if last_cache != self._cache:
                last_cache = self._cache.copy()
                for func in self._listener_function_calls:
                    try:
                        func()
                    except Exception:
                        pass

    def listen(self, func):
        if not self._listener_thread_object:
            self._listener_thread_object = threading.Thread(
                target=self._listener_thread
            )
            self._listener_thread_object.daemon = True
            self._listener_thread_object.start()

        if func not in self._listener_function_calls:
            self._listener_function_calls.append(func)

    def stop_listen(self, func):
        if func in self._listener_function_calls:
            self._listener_function_calls.remove(func)
