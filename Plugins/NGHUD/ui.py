from ETS2LA.UI import *

class UI(ETS2LAPage):
    url = "/settings/NGHUD"
    refresh_rate = 0.5
    location = ETS2LAPageLocation.SETTINGS
    title = "NGHUD"
    
    def handle_x_offset(self, value: int):
        """Handle the offset X setting change."""
        self.plugin.settings.offset_x = value
        self.plugin.update_anchor()
        
    def handle_y_offset(self, value: int):
        """Handle the offset Y setting change."""
        self.plugin.settings.offset_y = value
        self.plugin.update_anchor()
        
    def handle_z_offset(self, value: int):
        """Handle the offset Z setting change."""
        self.plugin.settings.offset_z = value
        self.plugin.update_anchor()
        
    def handle_left_width_change(self, value: int):
        """Handle the left width setting change."""
        self.plugin.settings.left_width = value
        self.plugin.layout()
        
    def handle_center_width_change(self, value: int):
        """Handle the center width setting change."""
        self.plugin.settings.center_width = value
        self.plugin.layout()
        
    def handle_right_width_change(self, value: int):
        """Handle the right width setting change."""
        self.plugin.settings.right_width = value
        self.plugin.layout()
    
    def render(self):
        TitleAndDescription(
            "NGHUD",
            "This plugin provides a HUD using the AR plugin as the renderer."
        )
        
        if not self.plugin:
            Text("Please enable the plugin to edit the settings.")
            return
        
        with Tabs():
            with Tab("Transform", container_style=styles.FlexVertical() + styles.Gap("24px")):
                SliderWithTitleDescription(
                    title="Offset X",
                    description="The horizontal offset of the HUD.",
                    default=self.plugin.settings.offset_x,
                    min=-1,
                    max=1,
                    step=0.1,
                    changed=self.handle_x_offset
                )
                SliderWithTitleDescription(
                    title="Offset Y",
                    description="The vertical offset of the HUD.",
                    default=self.plugin.settings.offset_y,
                    min=-1,
                    max=1,
                    step=0.1,
                    changed=self.handle_y_offset
                )
                SliderWithTitleDescription(
                    title="Offset Z",
                    description="The depth offset of the HUD.",
                    default=self.plugin.settings.offset_z,
                    min=-10,
                    max=10,
                    step=0.1,
                    changed=self.handle_z_offset
                )
                
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text("Widget Widths", styles.Classname("text-semibold"))
                    Text("These settings control the width of each widget in pixels. Defaults are 90, 120, 90. Elements will attempt to resize to fit, but please keep in mind they are not made to be resized too much.", styles.Description())
                
                with Container(styles.FlexHorizontal()):
                    InputWithTitleDescription(
                        title="Left",
                        default=self.plugin.settings.left_width,
                        type="number",
                        changed=self.handle_left_width_change,
                    )
                    InputWithTitleDescription(
                        title="Center",
                        default=self.plugin.settings.center_width,
                        type="number",
                        changed=self.handle_center_width_change,
                    )
                    InputWithTitleDescription(
                        title="Right",
                        default=self.plugin.settings.right_width,
                        type="number",
                        changed=self.handle_right_width_change,
                    )