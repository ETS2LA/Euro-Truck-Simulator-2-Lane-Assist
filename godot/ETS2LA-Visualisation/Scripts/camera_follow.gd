extends Node3D

@onready var Sockets = $/root/Node3D/Sockets
@export var target : Node3D
@export var offset : Vector3
@export var offsetRotationDegrees : Vector3
@export var reverseOffsetRotationDegrees : Vector3

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if target == null:
		print("WARNING: Camera has no target set!")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var followSpeed = 10
	var rotationOffset = offsetRotationDegrees
	if data != {}:
		followSpeed = (float(data["speed"]) + 1) * 2
	if followSpeed < 0:
		followSpeed = -followSpeed
		rotationOffset = reverseOffsetRotationDegrees
		
	# Lerp the position to the target position
	self.position = self.position.lerp(target.position + offset, delta * followSpeed)
	
	# Lerp the rotation to the target rotation
	var targetRotation = target.rotation_degrees
	targetRotation.z = 0
	targetRotation.x = 0
	self.rotation_degrees = self.rotation_degrees.lerp(target.rotation_degrees + rotationOffset, delta * 10)
	# Override the tilt and roll since otherwise those would break
	self.rotation_degrees.z = target.rotation_degrees.z
	self.rotation_degrees.x = target.rotation_degrees.x
	
	pass
