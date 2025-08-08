from Plugins.HUD.classes import HUDRenderer, HUDWidget
from ETS2LA.Utils.translator import _
from ETS2LA.UI import *

class UI(ETS2LAPage):
    url = "/settings/HUD"
    refresh_rate = 0.5
    location = ETS2LAPageLocation.SETTINGS
    title = "HUD"
    
    def handle_x_offset(self, value: int):
        """Handle the offset X setting change."""
        self.plugin.settings.offset_x = value
        if self.plugin:
            self.plugin.update_anchor()
        
    def handle_y_offset(self, value: int):
        """Handle the offset Y setting change."""
        self.plugin.settings.offset_y = value
        if self.plugin:
            self.plugin.update_anchor()
        
    def handle_z_offset(self, value: int):
        """Handle the offset Z setting change."""
        self.plugin.settings.offset_z = value
        if self.plugin:
            self.plugin.update_anchor()
        
    def handle_left_width_change(self, value: int):
        """Handle the left width setting change."""
        self.plugin.settings.left_width = value
        if self.plugin:
            self.plugin.layout()
        
    def handle_center_width_change(self, value: int):
        """Handle the center width setting change."""
        self.plugin.settings.center_width = value
        if self.plugin:
            self.plugin.layout()
        
    def handle_right_width_change(self, value: int):
        """Handle the right width setting change."""
        self.plugin.settings.right_width = value
        if self.plugin:
            self.plugin.layout()
        
    def handle_widget_scaling(self, value: float):
        """Handle the widget scaling setting change."""
        self.plugin.settings.widget_scaling = value
        if self.plugin:
            self.plugin.widget_scaling = value
        
    def handle_widget_add(self, value: str):
        """Handle the addition of a widget."""
        current = self.plugin.settings.get("widgets", self.plugin.default_widgets)
        if not current:
            current = []
            
        if value not in current:
            current.append(value)
            self.plugin.settings.widgets = current
            
    def handle_widget_remove(self, value: str):
        """Handle the removal of a widget."""
        current = self.plugin.settings.get("widgets", self.plugin.default_widgets)
        if value in current:
            current.remove(value)
            self.plugin.settings.widgets = current

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

    def handle_widget_height_change(self, *args):
        """Handle the widget height scaling setting change."""
        if args:
            self.plugin.settings.scale_height = args[0]
        else:
            self.plugin.settings.scale_height = not self.plugin.settings.get("scale_height", False)

    def render_widget(self, widget: HUDWidget, enabled: bool):
        with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("rounded-md border p-4 bg-input/10")):
            with Container(styles.FlexHorizontal() + styles.Gap("8px")):
                Text(widget.name, styles.Classname("text-semibold"))
                Text(widget.description, styles.Description())
            with Button(name=widget.name, action=self.handle_widget_add if not enabled else self.handle_widget_remove):
                Text(_("Enable") if not enabled else _("Disable"), styles.Classname("text-semibold"))

    def render(self):
        TitleAndDescription(
            _("HUD"),
            _("This plugin provides a HUD using the AR plugin as the renderer.")
        )
        
        if not self.plugin:
            Text(_("Please enable the plugin to edit the settings."))
            return
        
        with Tabs():
            # TRANSLATORS: Transform in this context means positioning and resizing, they are often called transforms in UI design.
            with Tab(_("Transform"), container_style=styles.FlexVertical() + styles.Gap("24px")):
                SliderWithTitleDescription(
                    title=_("Offset X"),
                    description=_("The horizontal offset of the HUD."),
                    default=self.plugin.settings.offset_x,
                    min=-1,
                    max=1,
                    step=0.1,
                    changed=self.handle_x_offset
                )
                SliderWithTitleDescription(
                    title=_("Offset Y"),
                    description=_("The vertical offset of the HUD."),
                    default=self.plugin.settings.offset_y,
                    min=-1,
                    max=1,
                    step=0.1,
                    changed=self.handle_y_offset
                )
                SliderWithTitleDescription(
                    title=_("Offset Z"),
                    description=_("The depth offset of the HUD."),
                    default=self.plugin.settings.offset_z,
                    min=-10,
                    max=10,
                    step=0.1,
                    changed=self.handle_z_offset
                )
                
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text(_("Widget Sizing"), styles.Classname("text-semibold"))
                    Text(_("These settings control the sizing of the widgets."), styles.Description())

                SliderWithTitleDescription(
                    min=0.5,
                    default=self.plugin.settings.get("widget_scaling", 1.0),
                    max=2.0,
                    step=0.05,
                    title=_("Widget Scaling"),
                    description=_("The scaling factor for the widgets. 1 is normal size, 0.5 is half size, 2 is double size."),
                    changed=self.handle_widget_scaling
                )
                
                CheckboxWithTitleDescription(
                    title=_("Scale Height"),
                    description=_("Scale the height of widgets too, please note that this will cause layout issues with some widgets, use with caution."),
                    default=self.plugin.settings.get("scale_height", False),
                    changed=self.handle_widget_height_change
                )
                    
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text(_("Widget Background"), styles.Classname("text-semibold"))
                    Text(_("You can control how much the widget background should be darkened by, either all the time or just during the day."), styles.Description())

                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    SliderWithTitleDescription(
                        title=_("Darkness"),
                        description=_("The darkness of the widget background. 0 is no darkness, 1 is fully dark."),
                        default=self.plugin.settings.darkness,
                        min=0,
                        max=1,
                        step=0.01,
                        changed=self.handle_darkness_change
                    )
                    
                    SliderWithTitleDescription(
                        title=_("Day Darkness"),
                        description=_("The darkness of the widget background during the day. 0 is no darkness, 1 is fully dark."),
                        default=self.plugin.settings.day_darkness,
                        min=0,
                        max=1,
                        step=0.01,
                        changed=self.handle_day_darkness_change
                    )


            with Tab(_("Elements"), container_style=styles.FlexVertical() + styles.Gap("24px")):
                all_widgets = [runner.element for runner in self.plugin.runners if runner.element.__class__.__name__ == "Widget"]
                all_widgets.sort(key=lambda x: x.name)
                
                enabled_widgets = self.plugin.settings.get("widgets", self.plugin.default_widgets)
                sizes = self.plugin.widget_sizes
                height = 50 # pixels
                
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text(_("Enabled Widgets"), styles.Classname("text-semibold"))
                    Text(_("This displays your enabled widgets and their respective sizes. Click one to disable it, you cannot yet move them around, you will instead have to Disable -> Enable to get them where you want them."), styles.Description())

                # Display the widgets with containers in the UI
                container_height = 80
                with Container(styles.FlexHorizontal() + styles.Width(f"100%") + styles.MaxWidth(f"100%") + styles.Height(f"{container_height}px") + styles.Classname("items-center justify-center rounded-md border p-4 bg-input/10")):
                    with Container(styles.FlexHorizontal() + styles.Gap("10px") + styles.Padding("0px")):
                        for widget in enabled_widgets:
                            width = sizes.get(widget, {"width": 100})["width"]
                            with Button(
                                name=widget,
                                action=self.handle_widget_remove,
                                type="ghost",
                                style=styles.Style(
                                    text_align="left",
                                    display="flex",
                                    flex_direction="column",
                                    align_items="flex-start",
                                    justify_content="center",
                                    width=f"{width}px",
                                    height=f"{height}px",
                                    gap="2px",
                                    classname="rounded-md border bg-input/20 p-2"
                                )
                            ):
                                Text(widget, styles.Classname("text-xs"))
                                Text(f"{width}x{height}", styles.Classname("text-xs text-muted-foreground"))
                        
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text(_("Available Widgets"), styles.Classname("text-semibold"))
                    Text(_("These widgets are available to be enabled:"), styles.Description())

                for widget in all_widgets:
                    enabled = widget.name in enabled_widgets
                    if not enabled:
                        self.render_widget(widget, enabled)
                
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    Text(_("Renderers"), styles.Classname("text-semibold"))
                    Text(_("These renderers are used to draw non anchored elements. These are usually elements in the game world that move around."), styles.Description())

                selected_renderers = self.plugin.settings.renderers
                if selected_renderers is None:
                    selected_renderers = []

                all_renderers = [runner.element for runner in self.plugin.runners if isinstance(runner.element, HUDRenderer)]
                all_renderers.sort(key=lambda x: x.name)
                    
                for renderer in all_renderers:
                    enabled = renderer.name in selected_renderers
                    with Container(styles.FlexVertical() + styles.Gap("8px") + styles.Classname("rounded-md border p-4 bg-input/10")):
                        with Container(styles.FlexHorizontal() + styles.Gap("8px")):
                            Text(renderer.name, styles.Classname("text-semibold"))
                            Text(renderer.description, styles.Description())
                        with Button(name=renderer.name, action=self.handle_renderer_add if not enabled else self.handle_renderer_remove):
                            Text(_("Enable") if not enabled else _("Disable"), styles.Classname("text-semibold"))