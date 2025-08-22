from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import *

class Widget(HUDWidget):
    name = _("Income")
    description = _("Shows the income from the current job.")
    fps = 2

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        job_income = self.plugin.data["configLongLong"].get("jobIncome", 0)
        game = self.plugin.data["scsValues"]["game"]
        currency = "$" if game == "ATS" else "€"
        on_job = self.plugin.data.get("specialBool", {}).get("onJob", False)

        if not on_job:
            income_text = _("No job")
        else:
            income_text = f"{currency}{job_income:,}"

        self.data = [
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(10 + offset_x, 8, anchor=self.plugin.anchor),
                text=income_text,
                color=Color(255, 255, 255, 200),
                size=22
            ),
            Text(
                Point(width-50 + offset_x, height-20, anchor=self.plugin.anchor),
                text=_("Income"),
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]
