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
	var x = response["api"]["truckPlacement"]["coordinateX"]
	var y = -response["api"]["truckPlacement"]["coordinateZ"]

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
			var pointZ = point["Z"]
			roadPoints.append([pointX, pointZ])
			
		globalRoads.append(roadPoints)
		
	
	# Now instantiate the points
	print("Instantiating circles")
	for road in globalRoads:
		var roadPoints = []
		for point in road:
			roadPoints.append(Vector3(point[0], 0, point[1]))
			# var sphere = CSGSphere3D.new()
			# sphere.radius = 5
			# add_child(sphere)
			# sphere.position = Vector3(point[0], 0, point[1])
	
		# Now create the road mesh and instantiate the road
		var roadMesh = ArrayMesh.new()
		var roadSurface = SurfaceTool.new()
		var roadWidth = 4.5
		roadSurface.begin(Mesh.PRIMITIVE_LINE_STRIP)
		for point in roadPoints:
			roadSurface.add_vertex(point)
			# Add the same point but with a width
			roadSurface.add_vertex(Vector3(point.x + roadWidth/2, point.y, point.z))
			roadSurface.add_vertex(Vector3(point.x - roadWidth/2, point.y, point.z))

		roadSurface.commit(roadMesh)
		
		var roadInstance = MeshInstance3D.new()
		roadInstance.mesh = roadMesh

		# Give it a material
		var roadMaterial = StandardMaterial3D.new()
		roadMaterial.albedo_color = Color(0.8, 0.8, 0.8)
		roadMaterial.emission_enabled = true
		roadMaterial.emission_energy = 0.5
		roadInstance.material_override = roadMaterial

		add_child(roadInstance)
	

	print("Done")
	var roadCount = len(globalRoads)
	print(len(globalRoads))
	
	camera.position = Vector3(x, 100, y)
	print(camera.position)
	
	var closestDistance = 1000000
	var closestPoint = []

	for road in globalRoads:
		for point in road:
			# Get the distance to the camera
			var distance = camera.position.distance_to(Vector3(point[0], point[1], 0))
			print(distance)
			if distance < closestDistance:
				closestDistance = distance
				closestPoint = point

	# Move the camera to the last point
	camera.position = Vector3(closestPoint[0], 100, closestPoint[1])

	# Turn the camera to face the closest point
	camera.look_at(Vector3(closestPoint[0], 0, closestPoint[1]), Vector3(0, 0, 1))
	# But lock the tilt
	camera.rotation_degrees = Vector3(camera.rotation_degrees.x, camera.rotation_degrees.y, 0)
