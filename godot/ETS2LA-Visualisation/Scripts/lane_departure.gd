extends Node

@export var target : Node3D
@onready var Sockets = $/root/Node3D/Sockets
var Line: CSGBox3D = null

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	Line = get_child(0)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var lateral_offset = 0
	if data != {} and "lateral_offset" in data:
		lateral_offset = float(data["lateral_offset"])
		if lateral_offset == -1:
			lateral_offset = 0
	else:
		lateral_offset = 0

	#print(lateral_offset)
	if lateral_offset < 0:
		lateral_offset = -2.25-lateral_offset
	else:
		lateral_offset = 2.25-lateral_offset
		
		
	
	if "JSONsteeringPoints" in Sockets.data:
		var SteeringData = Sockets.data["JSONsteeringPoints"].data
		var points = []
		var counter = 0
		for point in SteeringData:
			if typeof(point) == typeof([]):
				if len(point) > 1:
					points.append(Vector3(point[0], point[1] + 0.05, point[2]))
					counter += 1
					
		if counter > 2:
			Line.look_at_from_position(points[0], points[1])
		else:
			Line.global_rotation = target.global_rotation
	else:
		Line.global_rotation = target.global_rotation
	
	if abs(lateral_offset) < 1.5:
		var target_position = target.global_transform.origin
		if target and Line and lateral_offset != 0:
			Line.global_transform.origin = target_position + Vector3(-lateral_offset, 0, 0).rotated(Vector3(0,1,0), target.rotation.y)
	else:
		Line.global_position = Vector3(0, 100, 0)
