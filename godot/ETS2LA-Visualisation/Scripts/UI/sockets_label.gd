extends Label

@export var RenderSockets = true
var Sockets = null
@onready var Truck = $/root/Node3D/Truck
@onready var TruckTracker = $/root/Node3D/TruckTracker
@onready var Variables = $/root/Node3D/Variables
var averageResponseShowTime = Time.get_ticks_msec()
var responseTimes = []
var worstResponseTime = 0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	Sockets = get_node("/root/Node3D/Sockets")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if Sockets != null:
		var textToAdd = ""
		textToAdd += Sockets.status	
		if Sockets.status != "Connected":
			self.label_settings.font_color = Color.RED
		else:
			
			responseTimes.append(Time.get_ticks_msec() - Sockets.lastDataEntry)
			if Time.get_ticks_msec() - averageResponseShowTime > 1000: # once per second
				worstResponseTime = responseTimes.max()
				responseTimes = []
				averageResponseShowTime = Time.get_ticks_msec()
			
			if Variables.darkMode:
				self.label_settings.font_color = Color8(255, 255, 255, 50)
			else:
				self.label_settings.font_color = Color8(0, 0, 0, 100)
			if RenderSockets != false:
				var fps = 1000 / (worstResponseTime + 0.01)
				textToAdd += "\nSlowest data update took " + str(worstResponseTime) + "ms (" + str(round(fps)) + "fps)"
				
				var socketData = Sockets.GetData()
				for key in socketData:
					if "JSON" in key:
						if socketData[key] == null or socketData[key].data == null:
							textToAdd += "\n" + str(key) + ": unknown"
						else:
							#print(str(socketData[key].data))
							if typeof(socketData[key].data) == typeof({}):
								textToAdd += "\n" + str(key) + ": " + str(len(socketData[key].data)) + " entries"
							else: 
								textToAdd += "\n" + str(key) + ": " + str(socketData[key])
					else:
						textToAdd += "\n" + str(key) + ": " + str(socketData[key])
			else:
				var fps = 1000 / (worstResponseTime + 0.01)
				textToAdd += " @ " + str(round(fps)) + "fps"
		text = textToAdd
	else:
		text = "Sockets not found"
