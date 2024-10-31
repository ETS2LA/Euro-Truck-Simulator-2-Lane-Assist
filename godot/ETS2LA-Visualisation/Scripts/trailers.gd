extends Node

@onready var Sockets = $/root/Node3D/Sockets
@onready var TrailerObject = preload("res://Objects/user_trailer.tscn")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var data = Sockets.data
	var followSpeed = 4
	
	var cur_trailers = []
	for n in get_children():
		cur_trailers.append(n)
	
	if data != {}:
		if "JSONtrailers" in data:
			var trailer_data = data["JSONtrailers"].data
			var index = 0
			for trailer in trailer_data:
				while len(cur_trailers) < index + 1:
					var new_object = TrailerObject.instantiate(PackedScene.GEN_EDIT_STATE_DISABLED)
					add_child(new_object)
					cur_trailers = []
					for n in get_children():
						cur_trailers.append(n)
				
				var trailer_object = cur_trailers[index]
				var hook = trailer_object.get_children()[0].get_children()[0]
				var left_wheel = trailer_object.get_children()[0].get_children()[1]
				var right_wheel = trailer_object.get_children()[0].get_children()[2]
				
				# This will make sure that the hook is in the correct position.
				var api_hook = float(trailer["hookZ"])
				var offset = api_hook - hook.position.x
				offset = Vector3(0, 0, offset)

				var api_position = Vector3(float(trailer["x"]), float(trailer["y"]), float(trailer["z"]))
				trailer_object.position = trailer_object.position.lerp(api_position + offset.rotated(Vector3(0,1,0), trailer_object.rotation.y), delta * followSpeed)
				
				var api_rotation = Vector3(float(trailer["ry"]), float(trailer["rx"]), float(trailer["rz"]))
				trailer_object.rotation_degrees = api_rotation
				
				index += 1
				
			while len(cur_trailers) > len(trailer_data):
				var removed = cur_trailers.pop_back()
				remove_child(removed)
				removed.queue_free()
