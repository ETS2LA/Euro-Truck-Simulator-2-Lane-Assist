extends Node

@export var target : Node3D
@onready var Sockets = $/root/Node3D/Sockets
var StopSign: CSGBox3D = null

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	StopSign = get_child(0)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var stopping_distance = 0
	if data != {} and "status" in data:
		stopping_distance = float(data["status"].split("m")[0].split(" ")[-1])
		if stopping_distance == -1:
			stopping_distance = 0
	else:
		stopping_distance = 0

	var target_position = target.global_transform.origin
	if target and StopSign and stopping_distance != 0:
		StopSign.global_transform.origin = target_position + Vector3(0, 1, -stopping_distance).rotated(Vector3(0,1,0), target.rotation.y)
		StopSign.global_rotation = target.global_rotation
	else:
		StopSign.global_position = Vector3(0, 100, 0)
