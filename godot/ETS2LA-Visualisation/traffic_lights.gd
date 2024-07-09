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
				if object != null and typeof(object) != typeof({}):
					var state = object[0]
					var x = float(object[1])
					var y = float(object[2])
					var z = float(object[3])

					var TrafficLight = TrafficLightScene.instantiate()
					TrafficLight.position = Vector3(x,y,z)
					TrafficLight.scale = 1
					add_child(TrafficLight)
