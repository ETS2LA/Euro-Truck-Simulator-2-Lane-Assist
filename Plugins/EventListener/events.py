from ETS2LA.Events import Event


class GameStarted(Event):
    alias = "game_started"
    description = "Triggered when the game starts."
    game: str  # "ETS2" or "ATS"


class ProfileSelected(Event):
    alias = "profile_selected"
    description = "Triggered when a profile is selected."
    profile_name: str


class JobSelected(Event):
    alias = "job_selected"
    description = "Triggered when a job is selected."
    cargo: str
    from_company: str
    to_company: str
