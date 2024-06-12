extends Node3D

@onready var Sockets = $/root/Node3D/Sockets

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	if data != {}:
		var apiPosition = Vector3(float(data["x"]), float(data["y"]), float(data["z"]))
		self.position = apiPosition
		var apiRotation = Vector3(float(data["ry"]), float(data["rx"]), float(data["rz"]))
		self.rotation_degrees = apiRotation
