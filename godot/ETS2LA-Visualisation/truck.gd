extends Node3D

@export var offset : Vector3
@onready var Sockets = $/root/Node3D/Sockets


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var followSpeed = 10
	if data != {}:
		followSpeed = 4 #(float(data["speed"]) + 1)
	
		# Lerp the position to the target position
		var apiPosition = Vector3(float(data["x"]), float(data["y"]), float(data["z"])) + offset
		self.position = self.position.lerp(apiPosition, delta * followSpeed)
		
		# Lerp the rotation to the target rotation
		var apiRotation = Vector3(-float(data["ry"]), float(data["rx"]), float(data["rz"]))
		self.rotation_degrees = apiRotation
