extends CheckButton

func _toggled(button_pressed: bool) -> void:
	print(button_pressed)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if button_pressed else DisplayServer.VSYNC_DISABLED)
