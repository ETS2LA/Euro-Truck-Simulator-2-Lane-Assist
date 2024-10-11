extends Node

@onready var Sockets = $/root/Node3D/Sockets

var ObjectScript = preload("res://Scripts/object.gd")
var RoadMarkerScene = preload("res://Objects/road_marker.tscn")
var SignScene = preload("res://Objects/sign.tscn")

func _ready() -> void:
	pass

func _process(delta: float) -> void:
	if Sockets.data != {}:
		var curObjects = []
		var curObjectNames = []
		for n in self.get_children():
			curObjectNames.append(n.name)
			curObjects.append(n)
		
		var newObjectIDs = []
		var newObjects = []
		if typeof(Sockets.data) == typeof({}):
			if not "JSONobjects" in Sockets.data:
				return
			var objectData = Sockets.data["JSONobjects"].data
			if objectData != null:
				for object in objectData:
					if object != null and typeof(object) == typeof({}):
						var id = object["id"]
						var position = object["position"]
						position = Vector3(position[0], position[1], position[2])
						var type = object["objectType"]
						var screenPoints = object["screenPoints"]
						if type == "road_marker":
							var markerType = object["markerType"]
							var newObject = RoadMarkerScene.instantiate()
							newObject.name = str(id)
							newObject.position = position
							newObject.set_script(ObjectScript)
							newObject.type = "static"
							newObject.id = int(id)
							newObjects.append(newObject)
							newObjectIDs.append(str(id))
						if type == "sign":
							var newObject = SignScene.instantiate()
							newObject.name = str(id)
							newObject.position = position
							newObject.set_script(ObjectScript)
							newObject.type = "static"
							newObject.id = int(id)
							newObjects.append(newObject)
							newObjectIDs.append(str(id))

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
