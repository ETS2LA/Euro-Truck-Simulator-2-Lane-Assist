extends Node

var http
var camera

var globalRoads = []

func _ready():
	http = get_node("/root/Node3D/HTTPRequest")
	camera = get_node("/root/Node3D/Camera3D")
	http.request_completed.connect(self.RequestComplete)

	# Perform a GET request. The URL below returns JSON as of writing.
	print("Getting data")
	var error = http.request("http://127.0.0.1:39847")
	if error != OK:
		push_error("An error occurred in the HTTP request.")

# Called when the HTTP request is completed.
func RequestComplete(result, response_code, headers, body):
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	var roads = response["GPS"]["roads"]

	# Road Data Includes
	# Uid = 0
	# StartNodeUid = 0
	# StartNode = None
	# EndNodeUid = 0
	# EndNode = None
	# Nodes = None
	# BlockSize = 0
	# Valid = False
	# Type = 0
	# X = 0
	# Z = 0
	# Hidden = False
	# Flags = 0
	# Navigation = None
	# RoadLook = None
	# Points = None
	# IsSecret = False	
	for road in roads:
		# We are interested in the points
		var roadPoints = []
		for point in road["Points"]:
			var pointX = point["X"]
			var pointY = point["Z"]
			roadPoints.append([pointX, pointY])
			
		globalRoads.append(roadPoints)
		
	
	# Now instantiate the points
	print("Instantiating circles")
	for road in globalRoads:
		for point in road:
			var sphere = CSGSphere3D.new()
			add_child(sphere)
			sphere.position = Vector3(point[0], point[1], 0)
	print("Done")
	
	camera.position = Vector3(globalRoads[-1][0][0], globalRoads[-1][0][1], 0)
			
