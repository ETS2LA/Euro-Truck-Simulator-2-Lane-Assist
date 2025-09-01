from typing import Any
from enum import Enum

id: int = 0


def increment() -> int:
    """Increment the ID counter and return a new ID."""
    global id
    id = (id + 1) % 1000000
    return id


class Channel(Enum):
    # General
    SUCCESS = 0
    FAILURE = 1

    # Tag operations
    GET_TAGS = 2
    UPDATE_TAGS = 3

    # Plugin management
    ENABLE_PLUGIN = 4
    STOP_PLUGIN = 5
    RESTART_PLUGIN = 6
    CRASHED = 7
    GET_DESCRIPTION = 8

    # Page operations
    UPDATE_PAGE = 9
    OPEN_EVENT = 10
    CLOSE_EVENT = 11

    # UI operations
    NOTIFICATION = 12
    DIALOG = 13
    NAVIGATE = 14
    ASK = 15

    # State operations
    GET_STATE = 16
    STATE_UPDATE = 17

    # Events
    CALL_EVENT = 18
    EMMIT_EVENT = 19

    # Controls
    GET_CONTROLS = 20
    CONTROL_STATE_UPDATE = 21

    # Functions
    CALL_FUNCTION = 22

    # Performance
    FRAMETIME_UPDATE = 23

    # Shared Memory
    GET_MEM_TAGS = 24
    MEM_TAGS_RECEIVED = 25


class State(Enum):
    PENDING = 0
    PROCESSING = 1
    DONE = 2
    ERROR = 3


class PluginMessage:
    channel: Channel
    """The channel this message was sent on."""

    data: Any
    """The data that this message carries."""

    id: int = increment()
    """The ID of this message on the side of the sender."""

    is_backend: bool = False
    """Whether this message originates from the backend."""

    state: State = State.PENDING
    """The state of this message's processing."""

    def __init__(self, channel: Channel, data: Any):
        self.channel = channel
        self.data = data
