extends ProgressBar

@onready var Sockets = $/root/Node3D/Sockets
@onready var Variables = $/root/Node3D/Variables
@export var ValueToDisplay = "speed"
@export var Multiplier: float = -1

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if Sockets != null:
		if Sockets.status == "Connected":
			var socketData = Sockets.GetData()
			var found = false
			for key in socketData:
				if key == ValueToDisplay:
					if socketData[key] == null:
						found = true
						self.value = 0
						break
					else:
						found = true
						if Multiplier != -1: self.value = float(socketData[key]) * Multiplier
						else: self.value = float(socketData[key])
						break
			if not found:
				self.indeterminate = true
			else:
				self.indeterminate = false
		else:
			self.indeterminate = true
	else:
		self.indeterminate = true
