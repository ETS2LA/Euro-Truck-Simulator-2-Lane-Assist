extends Node3D

@onready var Sockets = $/root/Node3D/Sockets
@export var target : Node3D
@export var offset : Vector3
@export var offsetRotationDegrees : Vector3

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if target == null:
		print("WARNING: Camera has no target set!")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var followSpeed = 10
	if data != {}:
		followSpeed = (float(data["speed"]) + 1) * 2
	
	# Lerp the position to the target position
	self.position = self.position.lerp(target.position + offset, delta * followSpeed)
	
	# Lerp the rotation to the target rotation
	self.rotation_degrees = target.rotation_degrees + offsetRotationDegrees
	
	pass
