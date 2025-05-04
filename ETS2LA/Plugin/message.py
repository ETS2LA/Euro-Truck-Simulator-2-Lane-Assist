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
    
    # Plugin management
    ENABLE_PLUGIN = 3
    STOP_PLUGIN = 4
    RESTART_PLUGIN = 5
    CRASHED = 6
    
    # Page operations
    GET_PAGE_DESCRIPTIONS = 7
    GET_PAGE_DATA = 8
    
    # UI operations
    NOTIFICATION = 9
    DIALOG = 10
    NAVIGATE = 11
    ASK = 12
    
    # State operations
    GET_STATE = 13
    STATE_UPDATE = 14
    
    # Events
    CALL_EVENT = 15
    EMMIT_EVENT = 16
    
    # Controls
    GET_CONTROLS = 17
    CONTROL_STATE_UPDATE = 18
    
    # Functions
    CALL_FUNCTION = 19
    
class State(Enum):
    PENDING = 0
    PROCESSING = 1
    DONE = 2
    ERROR = 3

class PluginMessage:
    channel: Channel
    """The channel this message was sent on."""
    
    data: dict
    """The data that this message carries."""
    
    id: int = increment()
    """The ID of this message on the side of the sender."""
    
    is_backend: bool = False
    """Whether this message originates from the backend."""
    
    state: State = State.PENDING
    """The state of this message's processing."""
    
    def __init__(self, channel: Channel, data: dict):
        self.channel = channel
        self.data = data