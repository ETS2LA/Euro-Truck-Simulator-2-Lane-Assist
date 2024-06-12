extends Label

var Sockets = null
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
		textToAdd += "Slowest data update took " + str(worstResponseTime) + "ms"
		
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
