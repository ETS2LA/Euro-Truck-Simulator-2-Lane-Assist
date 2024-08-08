extends CheckButton

@onready var Variables = $/root/Node3D/Variables

func _setColors(color):
	self.add_theme_color_override("font_color", color)
	self.add_theme_color_override("font_focus_color", color)
	self.add_theme_color_override("font_pressed_color", color)
	self.add_theme_color_override("font_hover_color", color)
	self.add_theme_color_override("font_hover_pressed_color", color)

func _ready() -> void:
	self.button_pressed = Variables.darkMode
	if Variables.darkMode:
		_setColors(Color8(255, 255, 255, 255))
	else:
		_setColors(Color8(0, 0, 0, 255))
	

func _toggled(button_pressed: bool) -> void:
	Variables.SetTheme(button_pressed)
	if button_pressed:
		_setColors(Color8(255, 255, 255, 255))
	else:
		_setColors(Color8(0, 0, 0, 255))
