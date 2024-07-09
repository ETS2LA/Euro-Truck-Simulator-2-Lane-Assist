extends Node

@onready var Sockets = $/root/Node3D/Sockets

var truckScene = preload("res://Objects/truck.tscn")
var carScene = preload("res://Objects/car.tscn")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	for n in self.get_children():
		self.remove_child(n)
		n.queue_free() 
	
	if Sockets.data != {}:
		var vehicleData = Sockets.data["JSONvehicles"].data
		if vehicleData != null:
			for vehicle in vehicleData:
				var type = vehicle["vehicleType"]
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
				
				if type == "car":
					var car = carScene.instantiate()
					car.position = Vector3(x,y,z)
					car.scale = Vector3(distance, distance, distance)
					add_child(car)
				if type == "truck":
					var truck = truckScene.instantiate()
					truck.position = Vector3(x,y,z)
					truck.scale = Vector3(distance, distance, distance)
					add_child(truck)
