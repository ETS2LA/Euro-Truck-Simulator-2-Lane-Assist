extends Label

@onready var Sockets = $/root/Node3D/Sockets
@onready var Variables = $/root/Node3D/Variables
@export var DarkModeColor: Color = Color("white")
@export var LightModeColor: Color = Color("black")
@export var ValueToDisplay = "speed"
@export var Multiplier: float = -1
@export var EnableDisable: bool = false
@export var EnabledColor: Color = Color()
@export var TargetPlugin: String = "AdaptiveCruiseControl"

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if Variables.darkMode:
		self.label_settings.font_color = DarkModeColor
	else:
		self.label_settings.font_color = LightModeColor

	if Sockets != null:
		if Sockets.status == "Connected":
			var socketData = Sockets.GetData()
			var found = false
			for key in socketData:
				if key == ValueToDisplay:
					if socketData[key] == null:
						found = true
						self.text = ValueToDisplay
						break
					else:
						found = true
						if Multiplier != -1: self.text = str(round(float(socketData[key]) * Multiplier))
						else: self.text = str(socketData[key])
						break
			if not found:
				self.text = ValueToDisplay
		else:
			self.text = ValueToDisplay
	else:
		self.text = ValueToDisplay
		
	if Sockets != null and EnableDisable:
		if Sockets.status == "Connected":
			var socketData = Sockets.GetData()
			var found = false
			if "JSONstatus" in socketData:
				if TargetPlugin in socketData["JSONstatus"].data:
					if socketData["JSONstatus"].data[TargetPlugin] == true:
						self.label_settings.font_color = EnabledColor
