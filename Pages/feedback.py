from ETS2LA.Networking.cloud import SendFeedback
from ETS2LA.Settings import ETS2LASettings
from ETS2LA.UI import (
    ETS2LAPage,
    styles,
    Container,
    Text,
    Button,
    Switch,
    Input,
    TextArea,
    Space,
    SendPopup,
)

from Modules.TruckSimAPI.api import scsTelemetry

api = scsTelemetry()
map_settings = ETS2LASettings("Map")


class Page(ETS2LAPage):
    url = "/feedback"
    refresh_rate = 5

    message = ""
    username = ""
    want_response = False
    share_location = False

    def change_message(self, value):
        self.message = value

    def change_username(self, value):
        print(value)
        self.username = value

    def change_want_response(self, value):
        self.want_response = value

    def change_share_location(self, value):
        self.share_location = value

    def send_feedback(self):
        if self.message == "":
            SendPopup("Please write a message before sending feedback.", "error")
            return
        if self.want_response and self.username == "":
            SendPopup(
                "Please provide your Discord username or email address if you would like a response.",
                "error",
            )
            return

        fields = {}
        if self.want_response:
            fields["Wants response"] = "Yes"
            fields["Response contact"] = (
                self.username
                if self.username != ""
                else "None given, ignore the request."
            )

        if self.share_location:
            data = api.update()
            text = str(data.get("scsValues", {}).get("game"))
            text += f" ({map_settings.selected_data})"
            text += " @ " + f"{data.get('truckPlacement', {}).get('coordinateX'):.0f}"
            text += ", " + f"{data.get('truckPlacement', {}).get('coordinateY'):.0f}"
            text += ", " + f"{data.get('truckPlacement', {}).get('coordinateZ'):.0f}"
            fields["In-game location"] = text

        success = SendFeedback(self.message, self.username, fields)
        if success:
            SendPopup("Feedback sent successfully. Thank you!", "success")
        else:
            SendPopup(
                "Could not send feedback. Please check your internet connection and try again later.",
                "error",
            )

    def render(self):
        with Container(
            styles.Style(
                padding="20px",
            )
        ):
            Text("Feedback", styles.Title())
            Space(styles.Style(height="20px"))
            with Container(
                styles.FlexHorizontal()
                + styles.Classname("align_center items-center")
                + styles.Height("50px")
            ):
                with Container(styles.FlexHorizontal()):
                    Switch(False, changed=self.change_want_response)
                    Text(
                        "I would like a response",
                        styles.Style(margin_left="10px", min_width="150px"),
                    )
                if self.want_response:
                    Input(
                        "Your Discord username.",
                        changed=self.change_username,
                        style=styles.Style(margin_left="20px"),
                    )

            with Container(
                styles.FlexHorizontal()
                + styles.Classname("align_center items-center")
                + styles.Height("50px")
            ):
                with Container(styles.FlexHorizontal()):
                    Switch(False, changed=self.change_share_location)
                    Text(
                        "Share my in-game location (e.g. for reporting map issues)",
                        styles.Style(margin_left="10px", min_width="380px"),
                    )

                data = api.update()
                with Container(
                    styles.Classname(
                        "border rounded-md p-2 w-full "
                        + ("bg-input/10" if not self.share_location else "bg-input/30")
                    )
                ):
                    text = str(data.get("scsValues", {}).get("game"))
                    text += f" ({map_settings.selected_data})"
                    text += (
                        " @ "
                        + f"{data.get('truckPlacement', {}).get('coordinateX'):.0f}"
                    )
                    text += (
                        ", "
                        + f"{data.get('truckPlacement', {}).get('coordinateY'):.0f}"
                    )
                    text += (
                        ", "
                        + f"{data.get('truckPlacement', {}).get('coordinateZ'):.0f}"
                    )
                    Text(
                        text,
                        styles.Classname("text-muted-foreground")
                        if not self.share_location
                        else styles.Style(),
                    )

            Space(styles.Style(height="10px"))
            TextArea("Write your feedback here.", changed=self.change_message)
            Space(styles.Style(height="16px"))
            with Button(self.send_feedback, style=styles.Classname("default w-full")):
                Text("Send Feedback")
