extends Node

@export var url = "http://127.0.0.1:37520/api/tags/data"
@export var tag = "elevation_data"
@export var updateRate = 5
@onready var HTTPRequestObject = $/root/Node3D/ElevationHTTPRequest
@onready var Notifications = $/root/Node3D/UI/Notifications

var ElevationData = null
var lastUpdateTime = 0
var elevationLoaded = false

func _ready() -> void:
	pass # Replace with function body.

func send_request() -> void:
	var new_headers = ["Content-Type: application/json"]
	var json = JSON.stringify({
		"tag": tag,
		"zlib": true
	})
	Notifications.SendNotification("Getting elevation...", 2000)
	HTTPRequestObject.request_completed.connect(parse_request)
	HTTPRequestObject.request(url, new_headers, HTTPClient.METHOD_POST, json)
	lastUpdateTime = Time.get_ticks_msec()

func parse_request(result, response_code, headers, body):
	var json = JSON.parse_string(body.get_string_from_utf8())
	if typeof(json) == TYPE_FLOAT:
		return
	ElevationData = json
	if ElevationData != null:
		Notifications.SendNotification("Elevation retrieved, but not implemented yet.", 2000)
	else:
		Notifications.SendNotification("No elevation retrieved yet...", 2000, Color.ORANGE)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if ElevationData == null and Time.get_ticks_msec() - lastUpdateTime > updateRate * 1000:
		send_request()
		lastUpdateTime = Time.get_ticks_msec()
	#elif not elevationLoaded and ElevationData != null:
	#	elevationLoaded = true
	#	var total = len(ElevationData)
	#	var count = 0
	#	for point in ElevationData:
	#		var position = Vector3(point[0], point[2], point[1])
	#		var object = CSGBox3D.new()
	#		object.position = position
	#		add_child(object)
	#		if count % 1000 == 0:
	#			print("Loaded " + str(count) + "/" + str(total) + " points")
	#		count += 1
