extends Node

@onready var Sockets = $/root/Node3D/Sockets
var ObjectScript = preload("res://Scripts/object.gd")
var truckScene = preload("res://Objects/truck.tscn")
var carScene = preload("res://Objects/car.tscn")
var vanScene = preload("res://Objects/van.tscn")
var busScene = preload("res://Objects/bus.tscn")
var trailerScene = preload("res://Objects/trailer.tscn")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var curObjects = []
	var curObjectNames = []
	for n in self.get_children():
		curObjectNames.append(n.name)
		curObjects.append(n)
	
	var newObjectIDs = []
	var newObjects = []
	if Sockets.data != {}:
		if not Sockets.data.has("JSONvehicles"):
			return
		var vehicleData = Sockets.data["JSONvehicles"].data
		if vehicleData != null:
			for vehicle in vehicleData:
				var x = vehicle["position"]["x"]
				var y = vehicle["position"]["y"]
				var z = vehicle["position"]["z"]
				var width = vehicle["size"]["width"]
				var height = vehicle["size"]["height"]
				var length = vehicle["size"]["length"]
				var yaw = vehicle["rotation"]["yaw"]
				var pitch = vehicle["rotation"]["pitch"]
				var roll = vehicle["rotation"]["roll"]
				var id = vehicle["id"]
				
				var type = ""
				if vehicle["trailer_count"] != 0:
					type = "truck"
				elif length > 8:
					type = "bus"
				elif height > 1.8:
					type = "van"
				else:
					type = "car"
				
				newObjectIDs.append(str(id))
				
				if type == "car":
					var car = carScene.instantiate()
					car.name = str(id)
					car.position = Vector3(x,y,z)
					car.scale = Vector3(width, height, length)
					car.rotation_degrees = Vector3(pitch, yaw, roll)
					car.set_script(ObjectScript)
					car.id = int(id)
					newObjects.append(car)
				if type == "van":
					var van = vanScene.instantiate()
					van.name = str(id)
					van.position = Vector3(x,y,z)
					van.scale = Vector3(width, height, length)
					van.rotation_degrees = Vector3(pitch, yaw, roll)
					van.set_script(ObjectScript)
					van.id = int(id)
					newObjects.append(van)
				if type == "truck":
					var truck = truckScene.instantiate()
					truck.name = str(id)
					truck.position = Vector3(x,y,z)
					truck.scale = Vector3(width, height, length)
					truck.rotation_degrees = Vector3(pitch, yaw, roll)
					truck.set_script(ObjectScript)
					truck.id = int(id)
					newObjects.append(truck)
				if type == "bus":
					var bus = busScene.instantiate()
					bus.name = str(id)
					bus.position = Vector3(x,y,z)
					bus.scale = Vector3(width, height, length)
					bus.rotation_degrees = Vector3(pitch, yaw, roll)
					bus.set_script(ObjectScript)
					bus.id = int(id)
					newObjects.append(bus)
					
				var trailer_id = 0
				for trailer in vehicle["trailers"]:
					x = trailer["position"]["x"]
					y = trailer["position"]["y"]
					z = trailer["position"]["z"]
					width = trailer["size"]["width"]
					height = trailer["size"]["height"]
					length = trailer["size"]["length"]
					yaw = trailer["rotation"]["yaw"]
					pitch = trailer["rotation"]["pitch"]
					roll = trailer["rotation"]["roll"]
					
					var trailer_object = trailerScene.instantiate()
					trailer_object.name = str(id) + str(trailer_id)
					newObjectIDs.append(str(id) + str(trailer_id))
					trailer_object.position = Vector3(x,y,z)
					trailer_object.scale = Vector3(width, height, length)
					trailer_object.rotation_degrees = Vector3(pitch, yaw, roll)
					trailer_object.set_script(ObjectScript)
					trailer_object.id = int(id)
					newObjects.append(trailer_object)
					
	
		for object in newObjects:
			if not curObjectNames.has(object.name):
				add_child(object)
			else:
				for curObj in curObjects:
					if curObj.name == object.name:
						curObj.UpdatePositionScaleRotation(object.position, object.scale, object.rotation_degrees)
				
				object.queue_free()
		
		for n in self.get_children():
			if not newObjectIDs.has(n.name):
				self.remove_child(n)
				n.queue_free()
