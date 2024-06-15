extends Label

@onready var MapData = $/root/Node3D/MapData
@onready var Variables = $/root/Node3D/Variables

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	
	text = "Updating in " + str(round((MapData.updateRate * 1000 - (Time.get_ticks_msec() - MapData.lastUpdateTime))/1000)) + " seconds"
	
	if MapData.MapData == null:
		text += "\nPlease enable the Map plugin for roads and prefabs"
		label_settings.font_color = Color.RED
	else:
		text += "\nData loaded (" + str(MapData.loadedPrefabs) + " prefabs, " + str(MapData.loadedRoads) + " roads)"
		if Variables.darkMode:
			self.label_settings.font_color = Color8(255, 255, 255, 50)	
		else:
			self.label_settings.font_color = Color8(0, 0, 0, 100)
		
