extends Label

@onready var Sockets = $/root/Node3D/Sockets
@onready var Variables = $/root/Node3D/Variables
@export var DarkModeColor: Color = Color("white")
@export var LightModeColor: Color = Color("black")
@export var EnabledColor: Color = Color()
@export var TargetPlugin = "AdaptiveCruiseControl"
@export var ChangeText: bool = true
@export var EnabledText: String = "auto"
@export var DisabledText: String = ""
@export var Multiplier: float = -1

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	self.text = DisabledText
	if Variables.darkMode:
		self.label_settings.font_color = DarkModeColor
	else:
		self.label_settings.font_color = LightModeColor

	if Sockets != null:
		if Sockets.status == "Connected":
			var socketData = Sockets.GetData()
			var found = false
			if "JSONstatus" in socketData:
				if TargetPlugin in socketData["JSONstatus"].data:
					if socketData["JSONstatus"].data[TargetPlugin] == true:
						self.label_settings.font_color = EnabledColor
						self.text = EnabledText
