extends Label

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
			if Variables.darkMode:
				self.label_settings.font_color = Color8(255, 255, 255, 50)
			else:
				self.label_settings.font_color = Color8(0, 0, 0, 100)
			textToAdd += "\nSlowest data update took " + str(worstResponseTime) + "ms"
		
			responseTimes.append(Time.get_ticks_msec() - Sockets.lastDataEntry)
			if Time.get_ticks_msec() - averageResponseShowTime > 1000: # once per second
				worstResponseTime = responseTimes.max()
				responseTimes = []
				averageResponseShowTime = Time.get_ticks_msec()
			
			var socketData = Sockets.GetData()
			for key in socketData:
				textToAdd += "\n" + str(key) + ": " + str(socketData[key])
				
		text = textToAdd
	else:
		text = "Sockets not found"
