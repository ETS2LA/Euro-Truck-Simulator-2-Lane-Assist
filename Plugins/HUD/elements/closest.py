# TODO: get the exact distance from the truck to the closest city


from Plugins.AR.classes import Point, Rectangle, Color, Text
from Plugins.HUD.classes import HUDWidget
from ETS2LA.Utils.translator import _


class Widget(HUDWidget):
    name = _("Closest City")
    description = _(
        "Displays the closest city and its distance ( relative to the text )."
    )
    fps = 2

    def __init__(self, plugin):
        super().__init__(plugin)

    def settings(self):
        return super().settings()

    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return

        closest_city = self.plugin.tags.closest_city
        closest_city_distance = self.plugin.tags.closest_city_distance
        closest_country = self.plugin.tags.closest_country

        if closest_city:
            closest_city = self.plugin.tags.merge(closest_city)
        else:
            closest_city = _("Unknown")

        if closest_city_distance:
            closest_city_distance = self.plugin.tags.merge(closest_city_distance)
        else:
            closest_city_distance = 0

        if closest_country:
            closest_country = self.plugin.tags.merge(closest_country)
        else:
            closest_country = ""

        city_display = closest_city
        if closest_country and closest_country != "":
            city_display = f"{closest_city}, {closest_country}"

        if closest_country and "Great Britain" in closest_country:
            corrected_distance = closest_city_distance / 15
        else:
            corrected_distance = closest_city_distance / 19

        distance_text = f"{corrected_distance:.1f} km"

        max_city_length = 20
        if len(city_display) > max_city_length:
            city_display = city_display[: max_city_length - 3] + "..."

        self.data = [
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(10 + offset_x, 6, anchor=self.plugin.anchor),
                text=city_display,
                color=Color(255, 255, 255, 200),
                size=16,
            ),
            Text(
                Point(10 + offset_x, height - 18, anchor=self.plugin.anchor),
                text=distance_text,
                color=Color(255, 255, 255, 200),
                size=14,
            ),
        ]
