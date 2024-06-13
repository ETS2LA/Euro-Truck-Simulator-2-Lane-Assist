extends Node

@export var roadMat : StandardMaterial3D
@export var markingMat : StandardMaterial3D

@onready var MapData = $/root/Node3D/MapData
@onready var Truck = $/root/Node3D/Truck
var sphere = preload("res://Objects/sphere.tscn")
var lastData = null

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

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

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if MapData.MapData != null:
		var data = MapData.MapData["roads"]
		if data != lastData:
			for n in self.get_children():
				self.remove_child(n)
				n.queue_free() 
			
			for road in data:
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
					
					var forwardVectors = [] # These point towards the next point
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
						
					var normalVectors = [] # These point either straight right or left of the point
					for i in range(len(forwardVectors)):
						var fVector = forwardVectors[i]
						fVector = Vector2(fVector.x, fVector.z)
						fVector = fVector.rotated(deg_to_rad(90))
						fVector = fVector.normalized()
						normalVectors.append(fVector)
						
					# Create the vertices
					for i in range(len(points)):
						# Road
						var leftPoint = points[i] - Vector3((normalVectors[i] * 2.2)[0], 0, (normalVectors[i] * 2.2)[1])
						var rightPoint = points[i] + Vector3((normalVectors[i] * 2.2)[0], 0, (normalVectors[i] * 2.2)[1])
						
						vertices.push_back(leftPoint)
						vertices.push_back(rightPoint)
						
						# Markings
						leftPoint = points[i] + Vector3((normalVectors[i] * 2.2)[0], 0, (normalVectors[i] * 2.2)[1])
						rightPoint = points[i] + Vector3((normalVectors[i] * 2.3)[0], 0, (normalVectors[i] * 2.3)[1])
				
						rightMarkingVertices.push_back(leftPoint)
						rightMarkingVertices.push_back(rightPoint)
						
						leftPoint = points[i] - Vector3((normalVectors[i] * 2.3)[0], 0, (normalVectors[i] * 2.3)[1])
						rightPoint = points[i] - Vector3((normalVectors[i] * 2.2)[0], 0, (normalVectors[i] * 2.2)[1])
				
						leftMarkingVertices.push_back(leftPoint)
						leftMarkingVertices.push_back(rightPoint)
				
					# Render the meshes
					CreateAndRenderMesh(vertices, x, z, roadMat)
					CreateAndRenderMesh(rightMarkingVertices, x, z, markingMat)
					CreateAndRenderMesh(leftMarkingVertices, x, z, markingMat)
					
				
			lastData = data
				
			
		
