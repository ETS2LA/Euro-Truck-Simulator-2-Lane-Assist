extends Node3D

@onready var Sockets = $/root/Node3D/Sockets
@export var target : Node3D
@export var offset : Vector3
@export var offsetRotation : Vector3
@export var reverseOffsetRotation : Vector3
@export var mouseRotationResetTime : int = 5000
var mouseOffsetRotation = Vector3(0,0,0)
var mouseRotationTime = Time.get_ticks_msec()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if target == null:
		print("WARNING: Camera has no target set!")
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var speed = 0
	var followSpeed = 10
	var rotationOffset = offsetRotation
	if data != {}:
		speed = float(data["speed"])
		followSpeed = (speed + 1) * 2
	if followSpeed < 0:
		followSpeed = -followSpeed
		rotationOffset = reverseOffsetRotation
		
	if Input.is_action_pressed("MouseHold"):
		var mouseVelocity = Input.get_last_mouse_velocity()
		if mouseVelocity.abs().x > 25 or mouseVelocity.abs().y > 25:
			mouseOffsetRotation.y -= mouseVelocity.x / DisplayServer.screen_get_size().x / 1.5 # Yaw
			mouseOffsetRotation.x += mouseVelocity.y / DisplayServer.screen_get_size().y / 1.5 # Tilt
			mouseRotationTime = Time.get_ticks_msec()
	elif Time.get_ticks_msec() - mouseRotationTime > mouseRotationResetTime and speed * 3.6 > 20: # Reset back after time and if speed is over 20kph
		mouseOffsetRotation = Vector3(0, 0, 0)
		
	# Lerp the position to the target position
	self.position = self.position.lerp(target.position + offset, delta * followSpeed)
	
	# Yaw
	var currentRotation = Quaternion(self.basis)
	var targetRotation = Quaternion(Vector3(0,1,0), target.rotation.y + rotationOffset.y + mouseOffsetRotation.y)
	var smoothrot = currentRotation.slerp(targetRotation, delta * 5)
	
	self.basis = Basis(smoothrot)
	
	# Tilt
	#currentRotation = Quaternion(self.basis)
	#targetRotation = Quaternion(Vector3(1,0,0), target.rotation.x + rotationOffset.x + mouseOffsetRotation.x)
	#smoothrot = currentRotation.slerp(targetRotation, delta * 5)
	
	#self.basis = Basis(smoothrot)
	
	
	
	pass