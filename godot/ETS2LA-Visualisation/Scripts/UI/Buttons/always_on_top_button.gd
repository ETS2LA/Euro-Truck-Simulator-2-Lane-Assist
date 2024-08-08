extends CheckButton

@onready var Variables = $/root/Node3D/Variables

func _setColors(color):
	self.add_theme_color_override("font_color", color)
	self.add_theme_color_override("font_focus_color", color)
	self.add_theme_color_override("font_pressed_color", color)
	self.add_theme_color_override("font_hover_color", color)
	self.add_theme_color_override("font_hover_pressed_color", color)

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	self.button_pressed = DisplayServer.window_get_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP)
	Variables.ThemeChanged.connect(_changeTheme)
	_changeTheme()

func _changeTheme():
	if Variables.darkMode:
		_setColors(Color8(255, 255, 255, 255))
	else:
		_setColors(Color8(0, 0, 0, 255))
	
func _toggled(toggled_on: bool) -> void:
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, toggled_on)
