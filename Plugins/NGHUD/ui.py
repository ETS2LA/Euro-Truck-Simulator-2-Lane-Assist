from Plugins.NGHUD.classes import HUDRenderer, HUDWidget
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
        
    def handle_left_widget_change(self, value: str):
        self.plugin.settings.left_widget = value
        
    def handle_center_widget_change(self, value: str):
        self.plugin.settings.center_widget = value
        
    def handle_right_widget_change(self, value: str):
        self.plugin.settings.right_widget = value
        
    def handle_renderer_add(self, value: str):
        current = self.plugin.settings.renderers
        if not current:
            current = []
            
        if value not in current:
            current.append(value)
            self.plugin.settings.renderers = current
            
    def handle_renderer_remove(self, value: str):
        current = self.plugin.settings.renderers
        if value in current:
            current.remove(value)
            self.plugin.settings.renderers = current
    
    def handle_darkness_change(self, value: float):
        """Handle the darkness setting change."""
        self.plugin.settings.darkness = value
        
    def handle_day_darkness_change(self, value: float):
        """Handle the day darkness setting change."""
        self.plugin.settings.day_darkness = value
    
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
                
                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    InputWithTitleDescription(
                        title="L",
                        default=self.plugin.settings.left_width,
                        type="number",
                        changed=self.handle_left_width_change,
                    )
                    InputWithTitleDescription(
                        title="C",
                        default=self.plugin.settings.center_width,
                        type="number",
                        changed=self.handle_center_width_change,
                    )
                    InputWithTitleDescription(
                        title="R",
                        default=self.plugin.settings.right_width,
                        type="number",
                        changed=self.handle_right_width_change,
                    )
                    
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text("Widget Background", styles.Classname("text-semibold"))
                    Text("You can control how much the widget background should be darkened by, either all the time or just during the day.", styles.Description())
                
                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    SliderWithTitleDescription(
                        title="Darkness",
                        description="The darkness of the widget background. 0 is no darkness, 1 is fully dark.",
                        default=self.plugin.settings.darkness,
                        min=0,
                        max=1,
                        step=0.01,
                        changed=self.handle_darkness_change
                    )
                    
                    SliderWithTitleDescription(
                        title="Day Darkness",
                        description="The darkness of the widget background during the day. 0 is no darkness, 1 is fully dark.",
                        default=self.plugin.settings.day_darkness,
                        min=0,
                        max=1,
                        step=0.01,
                        changed=self.handle_day_darkness_change
                    )
                
                    
            with Tab("Elements", container_style=styles.FlexVertical() + styles.Gap("24px")):
                left_widget = self.plugin.settings.left_widget
                center_widget = self.plugin.settings.center_widget
                right_widget = self.plugin.settings.right_widget
                
                all_widgets = [runner.element for runner in self.plugin.runners if runner.element.__class__.__name__ == "Widget"]
                all_widgets.sort(key=lambda x: x.name)
                
                names = [widget.name for widget in all_widgets]
                
                left_names = [widget.name for widget in all_widgets if widget.name != right_widget and widget.name != center_widget]
                ComboboxWithTitleDescription(
                    options=left_names,
                    default=self.plugin.settings.left_widget,
                    title="Left Widget",
                    description="Select the widget to display on the left side of the HUD.",
                    changed=self.handle_left_widget_change,
                )
                
                center_names = [widget.name for widget in all_widgets if widget.name != left_widget and widget.name != right_widget]
                ComboboxWithTitleDescription(
                    options=center_names,
                    default=self.plugin.settings.center_widget,
                    title="Center Widget",
                    description="Select the widget to display in the center of the HUD.",
                    changed=self.handle_center_widget_change,
                )
                
                right_names = [widget.name for widget in all_widgets if widget.name != left_widget and widget.name != center_widget]
                ComboboxWithTitleDescription(
                    options=right_names,
                    default=self.plugin.settings.right_widget,
                    title="Right Widget",
                    description="Select the widget to display on the right side of the HUD.",
                    changed=self.handle_right_widget_change,
                )
                
                selected_renderers = [runner.name for runner in self.plugin.renderers]
                
                all_renderers = [runner.element for runner in self.plugin.runners if isinstance(runner.element, HUDRenderer)]
                all_renderers.sort(key=lambda x: x.name)
                
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text("Renderers", styles.Classname("text-semibold"))
                    Text("These renderers are used to draw non anchored elements. These are usually elements in the game world that move around.", styles.Description())
                    
                for renderer in all_renderers:
                    enabled = renderer.name in selected_renderers
                    with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("rounded-md border p-4 bg-input/10")):
                        with Container(styles.FlexHorizontal() + styles.Gap("8px")):
                            Text(renderer.name, styles.Classname("text-semibold"))
                            Text(renderer.description, styles.Description())
                        with Button(name=renderer.name, action=self.handle_renderer_add if not enabled else self.handle_renderer_remove):
                            Text("Enable" if not enabled else "Disable", styles.Classname("text-semibold"))