from typing import get_type_hints


class Event:
    alias: str
    validate_args: bool = True

    @classmethod
    def trigger(cls, events, *args, **kwargs):
        if not events:
            raise ValueError("Event.trigger called without an EventSystem instance!")
        if not events.emit:
            raise ValueError(
                "Event.trigger called with an invalid EventSystem instance!"
            )

        instance = cls()

        if cls.validate_args:
            # get child class type hints
            annotations = get_type_hints(cls)
            annotations.pop("alias", None)
            annotations.pop("validate_args", None)

            # validate kwargs
            for key, value in kwargs.items():
                if key not in annotations:
                    raise ValueError(f"Unexpected argument '{key}' for {cls.__name__}")
                expected_type = annotations[key]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"'{key}' must be of type {expected_type.__name__}, got {type(value).__name__}"
                    )

            # update instance attributes
            for key, value in kwargs.items():
                setattr(instance, key, value)

        # emit the event
        # we keep args and kwargs so that legacy listeners like
        # controls don't break (at least for now)
        events.emit(cls.alias, instance, *args, **kwargs)
