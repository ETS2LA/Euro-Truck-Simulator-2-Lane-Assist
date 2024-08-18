extends Node

@onready var Sockets = $/root/Node3D/Sockets

var TrafficLightScene = preload("res://Objects/traffic_light.tscn")

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
				if object != null and typeof(object) != typeof({}) and typeof(object) != typeof(float(1)) and len(object) >= 4:
					var state = object[0]
					var x = object[1]
					var y = object[2]
					var z = object[3]

					var TrafficLight = TrafficLightScene.instantiate()
					TrafficLight.position = Vector3(x,y,z)
					TrafficLight.scale = Vector3(1, 1, 1)
					add_child(TrafficLight)
