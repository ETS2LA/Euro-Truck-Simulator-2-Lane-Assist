extends Label

@onready var ElevationData = $/root/Node3D/Elevation
@onready var Variables = $/root/Node3D/Variables

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if ElevationData.ElevationData == null:
		text = "Updating in " + str(round((ElevationData.updateRate * 1000 - (Time.get_ticks_msec() - ElevationData.lastUpdateTime))/1000)) + " seconds"
		text += "\nPlease enable the Map plugin for elevation data"
		label_settings.font_color = Color.RED
	else:
		text = "\nLoaded " + str(len(ElevationData.ElevationData)) + " elevation points"
		if Variables.darkMode:
			self.label_settings.font_color = Color8(255, 255, 255, 50)	
		else:
			self.label_settings.font_color = Color8(0, 0, 0, 100)
		
