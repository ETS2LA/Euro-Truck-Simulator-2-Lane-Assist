extends Node

@onready var Sockets = $/root/Node3D/Sockets

var truckScene = preload("res://Objects/truck.tscn")
var carScene = preload("res://Objects/car.tscn")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# Kill all childs
	for n in self.get_children():
		self.remove_child(n)
		n.queue_free() 
	
	if Sockets.data != {}:
		var vehicleData = Sockets.data["JSONvehicles"].data
		if vehicleData != null:
			for vehicle in vehicleData:
				var type = vehicle["vehicleType"]
				var x = float(vehicle["raycasts"][0]["point"][0])
				var y = float(vehicle["raycasts"][0]["point"][1])
				var z = float(vehicle["raycasts"][0]["point"][2])
				if type == "car":
					var car = carScene.instantiate()
					car.position = Vector3(x,y,z)
					add_child(car)
				if type == "truck":
					var truck = truckScene.instantiate()
					truck.position = Vector3(x,y,z)
					add_child(truck)
