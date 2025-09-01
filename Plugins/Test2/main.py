# Framework
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author

import time


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Test2",
        version="1.0",
        description="Test",
        modules=["Camera"],
        listen=["*.py"],
        fps_cap=99999,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    def init(self): ...

    def run(self):
        print("Test 2 gettings tags")
        receive = self.globals.tags.test
        if receive is None:
            print("Test 2 tag not set")
            return

        receive = receive["Test"]
        diff = time.time() - receive
        print(f"Test 2 received the tag {diff * 1000:.1f}ms late")
        print(f"@{1 / self.performance[-1][1]:.1f}fps")
