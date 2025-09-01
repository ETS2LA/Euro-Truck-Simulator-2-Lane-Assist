class ETS2LADialog:
    """
    This is a base class for all ETS2LA dialogs.
    NOTE: If you want a return value, then you must wrap the dialog in a form like this:
    ```python
    class Dialog(ETS2LADialog):
        def render(self):
            with Form():
                Title("Example Form")
                Description("Please enter the following information")
                #     title   key     type
                Input("Name", "name", "string", description="Your name")
                #                            ! ---- !
                Button("Confirm?", "Submit", "submit", description="Submit the form")
            return RenderUI()

    # In a plugin class
    return_data = self.dialog(Dialog())
    ```
    """

    _json = {}

    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your dialog has to have a 'render' method.")
        self._json = {}

    def build(self) -> dict:
        if self._json == {}:
            self._json = self.render()  # type: ignore

        return self._json
