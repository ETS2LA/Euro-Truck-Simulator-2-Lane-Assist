extends Node

@export var color = Color.BLACK

@onready var MapData = $/root/Node3D/MapData
@onready var Truck = $/root/Node3D/Truck
var sphere = preload("res://Objects/sphere.tscn")
var lastData = null
var mat = StandardMaterial3D.new()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	mat.albedo_color = color
	pass # Replace with function body.

func JsonPointToLocalCoords(jsonPoint, x, y, z):
	if x > jsonPoint[0]: jsonPoint[0] += x
	else: jsonPoint[0] -= x
	if z > jsonPoint[1]: jsonPoint[1] += z
	else: jsonPoint[1] -= z
	return Vector3(jsonPoint[0], y, jsonPoint[1])

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
				
				var vertices = []
				var UVs = []
				var tmpMesh = Mesh.new()
				
				#for lane in road["ParallelPoints"]:
				#	var points = []
				#	var counter = 0
				#	for point in lane:
				#		points.append(JsonPointToLocalCoords(point, x, z, yValues[counter]))
				#		counter += 1
				#	
				#	var forwardVectors = []
				#	for i in range(len(points)):
				#		pass
				
				for i in range(resolution):
					var roadCount = len(road["ParallelPoints"])
					var perSide = int(roadCount/2) - 1
					var leftPoint = road["ParallelPoints"][perSide][i]
					if roadCount == 1:
						perSide = -1 # Don't throw inde 1 on a base object...
					var rightPoint = road["ParallelPoints"][perSide+1][i]
					
					if x > leftPoint[0]: leftPoint[0] += x
					else: leftPoint[0] -= x
					if z > leftPoint[1]: leftPoint[1] += z
					else: leftPoint[1] -= z
					
					if x > rightPoint[0]: rightPoint[0] += x
					else: rightPoint[0] -= x
					if z > rightPoint[1]: rightPoint[1] += z
					else: rightPoint[1] -= z
					
					leftPoint = Vector3(leftPoint[0], yValues[i], leftPoint[1])
					rightPoint = Vector3(rightPoint[0], yValues[i], rightPoint[1])
					
					vertices.push_back(leftPoint)
					vertices.push_back(rightPoint)
					
					UVs.push_back(Vector2(0,0))
					UVs.push_back(Vector2(0,1))
				
				var st = SurfaceTool.new()
				st.begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
				st.set_material(mat)
				
				for v in vertices.size(): 
					st.set_uv(UVs[v])
					st.set_normal(Vector3(0,1,0))
					st.add_vertex(vertices[v])
				
				tmpMesh = st.commit()
				
				var meshInstance = MeshInstance3D.new()
				meshInstance.mesh = tmpMesh
				meshInstance.position = Vector3(x, 0, z)
				add_child(meshInstance)
				print("Created mesh instance at position: " + str(Vector3(x, 0, z)))
				
			lastData = data
				
			
		
