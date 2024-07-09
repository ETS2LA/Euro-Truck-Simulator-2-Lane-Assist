extends Node

@export var roadMat = preload("res://Materials/road.tres")
@export var roadDarkMat = preload("res://Materials/roadDark.tres")
@export var markingMat = preload("res://Materials/markings.tres")
@export var markingsDarkMat = preload("res://Materials/markingsDark.tres")

@export var markingWidth : float

@onready var MapData = $/root/Node3D/MapData
@onready var Truck = $/root/Node3D/Truck
@onready var Variables = $/root/Node3D/Variables

var sphere = preload("res://Objects/sphere.tscn")
var lastData = null

var reload = false

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
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
	
func CreateAndRenderMesh(vertices, x, z, mat):
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
	meshInstance.position = Vector3(x, 0, z)
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
	
func CreateVerticesForPoint(point, normalVector):
	var vertices = []
	var rightMarkingVertices = []
	var leftMarkingVertices = []
	# Road
	var leftPoint = point - Vector3((normalVector * (2.25 - markingWidth))[0], 0, (normalVector * (2.25 - markingWidth))[1])
	var rightPoint = point + Vector3((normalVector * (2.25 - markingWidth))[0], 0, (normalVector * (2.25 - markingWidth))[1])
	
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
		if data != lastData or reload and "roads" in data and "prefabs" in data:
			var roadData = data["roads"]
			
			for n in self.get_children():
				self.remove_child(n)
				n.queue_free() 
			
			for road in roadData:
				var yValues = road["YValues"]
				var x = road["X"]
				var z = road["Z"]
				var resolution = len(yValues)
				
				
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
					CreateAndRenderMesh(rightMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					CreateAndRenderMesh(leftMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					
			
			var prefabData = data["prefabs"]
			for prefab in prefabData:
				var x = prefab["X"]
				var y = prefab["Y"]
				var z = prefab["Z"]
				var lines = []
				var counter = 0
				for point in prefab["CurvePoints"]:
					# Convert the JSON points to godot Vector3s
					var p1 = Vector3(point[0], point[4], point[1])
					var p2 = Vector3(point[2], point[5], point[3])
					
					#if x > p1.x: p1.x -= x
					#else: p1.x += x
					#if z > p1.z: p1.z -= z
					#else: p1.z += z
					
					#if x > p2.x: p2.x -= x
					#else: p2.x += x
					#if z > p2.z: p2.z -= z
					#else: p2.z += z
					
					p1.x -= x
					p1.z -= z
					
					p2.x -= x
					p2.z -= z
					
					lines.append([p1, p2])
					
					counter += 1
					
				var count = 0
				for line in lines:
					var vertices = []
					var rightMarkingVertices = []
					var leftMarkingVertices = []
					var points = line
					var forwardVectors = CreateForwardVectors(points)
					
					# These point either straight right or left of the point
					var normalVectors = CreateNormalVectors(forwardVectors)
					
					# Create the vertices
					for i in range(len(points)):
						var allVertices = CreateVerticesForPoint(points[i], normalVectors[i])
						vertices += allVertices[0]
						#leftMarkingVertices += allVertices[1]
						#rightMarkingVertices += allVertices[2]
				
					# Render the meshes
					var dark = Variables.darkMode
					CreateAndRenderMesh(vertices, x, z, roadMat if not dark else roadDarkMat)
					#CreateAndRenderMesh(rightMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					#CreateAndRenderMesh(leftMarkingVertices, x, z, markingMat if not dark else markingsDarkMat)
					
				
			lastData = data
			reload = false
				
			
		
