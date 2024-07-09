extends Node

@onready var Sockets = $/root/Node3D/Sockets

var TrafficLightScene = preload("res://Objects/trafficLight.tscn")

func _ready() -> void:
	pass

func _process(delta: float) -> void:
	for n in self.get_children():
		self.remove_child(n)
		n.queue_free()

	if Sockets.data != {}:
		var TrafficLightData = Sockets.data["JSONTrafficLights"].data
		if TrafficLightData != null:
			for object in TrafficLightData:
				var state = object["State"]
				var x = float(object["X"])
				var y = float(object["Y"])
				var z = float(object["Z"])
				var pitch = float(object["Pitch"])
				var yaw = float(object["Yaw"])
				var roll = float(object["Roll"])

				var TrafficLight = TrafficLightScene.instantiate()
				TrafficLight.position = Vector3(x,y,z)
				TrafficLight.rotation_degrees = Vector3(pitch, yaw, roll)
				TrafficLight.scale = 1
				add_child(TrafficLight)
