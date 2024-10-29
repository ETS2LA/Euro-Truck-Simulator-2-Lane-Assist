extends Button

@onready var Map = $/root/Node3D/Map/RoadsAndPrefabs

func _pressed() -> void:
	Map.Reload()
