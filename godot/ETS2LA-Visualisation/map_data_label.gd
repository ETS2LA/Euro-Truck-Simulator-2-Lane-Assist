extends Label

@onready var MapData = $/root/Node3D/MapData

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if MapData.MapData == null:
		text = "Please enable the Map plugin for roads and prefabs"
		label_settings.font_color = Color.RED
	else:
		text = "Map data loaded"
		label_settings.font_color = Color.WHITE
		
	text += "\nUpdating map data in " + str(round((MapData.updateRate * 1000 - (Time.get_ticks_msec() - MapData.lastUpdateTime))/1000)) + " seconds"
