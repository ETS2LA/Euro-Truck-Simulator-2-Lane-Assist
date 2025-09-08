from ETS2LA.UI import RenderUI
from enum import Enum
import time


class ETS2LAPageLocation(Enum):
    """A location marker for the page. If you use anything other
    than hidden, then you can set the `title` variable to the title
    of the button that will open the page.
    """

    SETTINGS = "settings"
    SIDEBAR = "sidebar"
    HIDDEN = "hidden"


class ETS2LAPage:
    """This is a base class for all ETS2LA pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :param url: The relative URL of the page. (eg. /settings/global)
    :param refresh_rate: The refresh rate of the page in seconds. (0 = no limit)
    :param plugin: A reference to the plugin that spawned this page.
    """

    url: str = ""
    last_update_: float = 0
    refresh_rate: int = 0
    need_update: bool = False

    plugin: object = None
    """
    A reference to the plugin that spawned this page.
    If the plugin is disabled, then this object will be None.
    """

    location: ETS2LAPageLocation = ETS2LAPageLocation.HIDDEN
    """
    The location of the page. If you use anything other than hidden,
    then you can set the `title` variable to the title of the button that will open the page.
    """
    title: str = "Custom Page"
    """
    The title of the page. This is used for the button that opens the page.
    If the page is hidden, then this is ignored.
    """

    open_calls: int = 0
    """
    Incremented by open_event(), decremented by close_event().
    """

    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        if self.url == "":
            raise TypeError(
                "You must set the 'url' variable to the relative URL of the page."
            )
        self._json = {}
        try:
            self.init()  # type: ignore # Might or might not exist.
        except Exception:
            pass

    def render(self):
        """This method is called when the page is built. Override this method to render the page."""
        raise NotImplementedError(
            "You must implement the 'render' method in your page class."
        )

    def is_open(self) -> bool:
        """Returns True if the page is currently open."""
        return self.open_calls > 0

    def open_event(self):
        """This method is called when the page is opened. Override this method to handle the open event."""
        self.open_calls += 1

    def close_event(self):
        """This method is called when the page is closed. Override this method to handle the close event."""
        self.open_calls -= 1

    def reset_timer(self):
        # Trigger a timer reset to make sure the
        # page is rerendered.
        self.need_update = True

    def build(self):
        # Some pages only need to be built once.
        if self.refresh_rate == -1 and not self.need_update:
            if self._json:
                return self._json

        # Some pages might not need to be built every time.
        elif self.refresh_rate != 0 and not self.need_update:
            if self.last_update_ + self.refresh_rate > time.perf_counter():
                return self._json

        RenderUI()  # Clear residuals in the UI system
        self.render()  # type: ignore # Might or might not exist.
        self._json = RenderUI()
        self.last_update_ = time.perf_counter()
        self.need_update = False

        self._json.insert(
            0,
            {
                "url": self.url,
                "location": self.location.value,
                "title": self.title,
            },
        )

        return self._json
