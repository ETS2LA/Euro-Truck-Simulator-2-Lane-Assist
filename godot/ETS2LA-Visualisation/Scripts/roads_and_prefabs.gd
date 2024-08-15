extends Node

@export var roadMat = preload("res://Materials/road.tres")
@export var roadDarkMat = preload("res://Materials/roadDark.tres")
@export var markingMat = preload("res://Materials/markings.tres")
@export var markingsDarkMat = preload("res://Materials/markingsDark.tres")
@export var steeringMat = preload("res://Materials/steering.tres")
@export var steeringDarkMat = preload("res://Materials/steeringDark.tres")

@export var markingWidth : float

@onready var MapData = $/root/Node3D/MapData
@onready var Truck = $/root/Node3D/Truck
@onready var Variables = $/root/Node3D/Variables
@onready var Socket = $/root/Node3D/Sockets
@onready var RoadParent = $/root/Node3D/Map/Roads
@onready var PrefabParent = $/root/Node3D/Map/Prefabs

var sphere = preload("res://Objects/sphere.tscn")
var lastData = null

var reload = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	print("Rendering 1/2 of prefabs")
	Variables.ThemeChanged.connect(Reload)
	pass # Replace with function body.

func Reload():
	MapData.send_request()
	reload = true

func JsonPointToLocalCoords(jsonPoint, x, y, z):
	if x > jsonPoint[0]: jsonPoint[0] += x
	else: jsonPoint[0] -= x
	if z > jsonPoint[1]: jsonPoint[1] += z
	else: jsonPoint[1] -= z
	return Vector3(jsonPoint[0], y, jsonPoint[1])
	
func CreateAndRenderMesh(vertices, x, z, mat, meshName="default", parent="road", y=0):
	var mesh = Mesh.new()
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	st.set_material(mat)
	
	for v in vertices.size(): 
		st.set_uv(Vector2(0,0))
		st.set_normal(Vector3(0,1,0))
		st.add_vertex(vertices[v])
	
	mesh = st.commit()
	
	# Render the road mesh
	var meshInstance = MeshInstance3D.new()
	meshInstance.mesh = mesh
	meshInstance.position = Vector3(x, y, z)
	meshInstance.name = meshName
	
	if parent == "road":
		RoadParent.add_child(meshInstance)
	elif parent == "prefab":
		PrefabParent.add_child(meshInstance)
	else:
		add_child(meshInstance)
	
func CreateForwardVectors(points):
	var forwardVectors = []
	for i in range(len(points)):
		if i == len(points) - 1:
			var curPoint = points[-1]
			var lastPoint = points[len(points)-2]
			var vector = lastPoint - curPoint
			forwardVectors.append(vector)
		else:
			var curPoint = points[i]
			var nextPoint = points[i+1]
			var vector = curPoint - nextPoint
			forwardVectors.append(vector)
	
	return forwardVectors
	
func CreateNormalVectors(forwardVectors):
	var normalVectors = []
	for i in range(len(forwardVectors)):
		var fVector = forwardVectors[i]
		fVector = Vector2(fVector.x, fVector.z)
		fVector = fVector.rotated(deg_to_rad(90))
		fVector = fVector.normalized()
		normalVectors.append(fVector)
		
	return normalVectors
	
func CreateVerticesForPoint(point, normalVector, width = 2.25):
	var vertices = []
	var rightMarkingVertices = []
	var leftMarkingVertices = []
	# Road
	var leftPoint = point - Vector3((normalVector * (width - markingWidth))[0], 0, (normalVector * (width - markingWidth))[1])
	var rightPoint = point + Vector3((normalVector * (width - markingWidth))[0], 0, (normalVector * (width - markingWidth))[1])
	
	vertices.push_back(leftPoint)
	vertices.push_back(rightPoint)
	
	# Markings
	leftPoint = point + Vector3((normalVector * 2.2)[0], 0, (normalVector * (2.25 - markingWidth))[1])
	rightPoint = point + Vector3((normalVector * (2.25 + markingWidth))[0], 0, (normalVector * (2.25 + markingWidth))[1])

	rightMarkingVertices.push_back(leftPoint)
	rightMarkingVertices.push_back(rightPoint)
	
	leftPoint = point - Vector3((normalVector * (2.25 + markingWidth))[0], 0, (normalVector * (2.25 + markingWidth))[1])
	rightPoint = point - Vector3((normalVector * (2.25 - markingWidth))[0], 0, (normalVector * (2.25 - markingWidth))[1])

	leftMarkingVertices.push_back(leftPoint)
	leftMarkingVertices.push_back(rightPoint)
	
	return [vertices, leftMarkingVertices, rightMarkingVertices]

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if MapData.MapData != null:
		var data = MapData.MapData
		var totalLines = 0
		if data != lastData or reload and "roads" in data and "prefabs" in data:
			var roadData = data["roads"]
			
			for n in self.get_children():
				self.remove_child(n)
				n.queue_free() 
				
			for n in PrefabParent.get_children():
				PrefabParent.remove_child(n)
				n.queue_free()
				
			for n in RoadParent.get_children():
				RoadParent.remove_child(n)
				n.queue_free()
			
			for road in roadData:
				var yValues = road["YValues"]
				var x = road["X"]
				var z = road["Z"]
				var resolution = len(yValues)
					
				if len(yValues) == 0:
					continue
				
				for lane in road["ParallelPoints"]:
					var vertices = []
					var rightMarkingVertices = []
					var leftMarkingVertices = []
					var points = []
					var counter = 0
					for point in lane:
						# Convert the JSON points to godot Vector3s
						points.append(JsonPointToLocalCoords(point, x, yValues[counter], z))
						counter += 1
					
					# These point towards the next point
					var forwardVectors = CreateForwardVectors(points)
					
					# These point either straight right or left of the point
					var normalVectors = CreateNormalVectors(forwardVectors)
					
					# Create the vertices
					for i in range(len(points)):
						var allVertices = CreateVerticesForPoint(points[i], normalVectors[i])
						vertices += allVertices[0]
						leftMarkingVertices += allVertices[1]
						rightMarkingVertices += allVertices[2]
						
				
					# Render the meshes
					var dark = Variables.darkMode
					CreateAndRenderMesh(vertices, x, z, roadMat if not dark else roadDarkMat)
					#CreateAndRenderMesh(rightMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					#CreateAndRenderMesh(leftMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					totalLines += 1
					
			
			var prefabData = data["prefabs"]
			for prefab in prefabData:
				var x = prefab["X"]
				var y = prefab["Y"] # + prefab["Nodes"][0]["Y"]
				var z = prefab["Z"]
				var lines = []
				for lane in prefab["CurvePoints"]:
					var vertices = []
					var rightMarkingVertices = []
					var leftMarkingVertices = []
					var points = []
					var counter = 0
					for point in lane:
						point = Vector3(point[0], point[2], point[1])
						point.x -= x
						point.z -= z
						#point.y += y
						#points.append(JsonPointToLocalCoords(point, x, pointY, z))
						points.append(point)
						counter += 1
					
					# These point towards the next point
					var forwardVectors = CreateForwardVectors(points)
					
					# These point either straight right or left of the point
					var normalVectors = CreateNormalVectors(forwardVectors)
					
					# Create the vertices
					for i in range(len(points)):
						var allVertices = CreateVerticesForPoint(points[i], normalVectors[i])
						vertices += allVertices[0]
						leftMarkingVertices += allVertices[1]
						rightMarkingVertices += allVertices[2]
						
				
					# Render the meshes
					var dark = Variables.darkMode
					CreateAndRenderMesh(vertices, x, z, roadMat if not dark else roadDarkMat)
					#CreateAndRenderMesh(rightMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					#CreateAndRenderMesh(leftMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					totalLines += 1
				
			lastData = data
			reload = false
			print("Total of " + str(totalLines) + " lines")
	
	if Socket.data != {}:
		var SteeringData = Socket.data["JSONsteeringPoints"].data
		
		if len(SteeringData) == 0:
			return
			
		if typeof(SteeringData[0]) == typeof("Not loaded yet"):
			return
		
		var position = Vector3(float(Socket.data["x"]), float(Socket.data["y"]), float(Socket.data["z"]))
		var vertices = []
		var rightMarkingVertices = []
		var leftMarkingVertices = []
		var points = []
		var counter = 0
		for point in SteeringData:
			# Convert the JSON points to godot Vector3s
			points.append(Vector3(point[0], position.y + 1, point[1]))
			#print(points[-1])
			counter += 1
		
		# These point towards the next point
		var forwardVectors = CreateForwardVectors(points)
		
		# These point either straight right or left of the point
		var normalVectors = CreateNormalVectors(forwardVectors)
		
		# Create the vertices
		for i in range(len(points)):
			var allVertices = CreateVerticesForPoint(points[i], normalVectors[i], 1.0)
			vertices += allVertices[0]
			leftMarkingVertices += allVertices[1]
			rightMarkingVertices += allVertices[2]
			
	
		# Render the meshes
		var dark = Variables.darkMode
		var mat = steeringMat if not dark else steeringDarkMat
		
		for n in self.get_children():
			if n.name == "steering":
				self.remove_child(n)
				n.queue_free() 
		
		CreateAndRenderMesh(vertices, 0, 0, mat, "steering", "self")
		#CreateAndRenderMesh(rightMarkingVertices, 0, 0, mat, "steering", "self", -0.98)
		#CreateAndRenderMesh(leftMarkingVertices, 0, 0, mat, "steering", "self", -0.98)
		
