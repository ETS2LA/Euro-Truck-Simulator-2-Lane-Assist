extends Node

var darkMode = true
signal ThemeChanged

func SwitchTheme():
	darkMode = not darkMode
	ThemeChanged.emit()
	
func SetTheme(setDarkMode):
	darkMode = setDarkMode
	ThemeChanged.emit()

func _ready() -> void:
	pass
