extends Node

@onready var Sockets = $/root/Node3D/Sockets
var ObjectScript = preload("res://Scripts/object.gd")

var truckScene = preload("res://Objects/truck.tscn")
var carScene = preload("res://Objects/car.tscn")

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
				var type = vehicle["objectType"]
				var x1 = float(vehicle["raycasts"][0]["point"][0])
				var y1 = float(vehicle["raycasts"][0]["point"][1])
				var z1 = float(vehicle["raycasts"][0]["point"][2])
				var x2 = float(vehicle["raycasts"][1]["point"][0])
				var y2 = float(vehicle["raycasts"][1]["point"][1])
				var z2 = float(vehicle["raycasts"][1]["point"][2])
				var x = (x1 + x2) / 2
				var y = (y1 + y2) / 2
				var z = (z1 + z2) / 2
				var distance = Vector3(x1, y1, z1).distance_to(Vector3(x2, y2, z2))
				
				if distance < 1:
					distance = 1
				
				newObjectIDs.append(str(vehicle["id"]))
				
				if type == "car":
					var car = carScene.instantiate()
					car.name = str(vehicle["id"])
					car.position = Vector3(x,y,z)
					car.scale = Vector3(distance, distance, distance)
					car.set_script(ObjectScript)
					car.id = int(vehicle["id"])
					newObjects.append(car)
				if type == "truck":
					var truck = truckScene.instantiate()
					truck.name = str(vehicle["id"])
					truck.position = Vector3(x,y,z)
					truck.scale = Vector3(distance, distance, distance)
					truck.set_script(ObjectScript)
					truck.id = int(vehicle["id"])
					newObjects.append(truck)
	
		for object in newObjects:
			if not curObjectNames.has(object.name):
				add_child(object)
			else:
				for curObj in curObjects:
					if curObj.name == object.name:
						curObj.UpdatePositionScale(object.position, object.scale)
				
				object.queue_free()
		
		for n in self.get_children():
			if not newObjectIDs.has(n.name):
				self.remove_child(n)
				n.queue_free()
