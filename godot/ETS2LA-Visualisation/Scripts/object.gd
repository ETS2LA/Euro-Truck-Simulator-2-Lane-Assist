extends Node3D

var id:int = 0
var type = "dynamic"

var _defaultMaterial:BaseMaterial3D
var _child: CSGBox3D
var _target = Vector3(0,0,0)
var _target_scale = Vector3(0,0,0)
var _cur_target_time = Time.get_ticks_msec()
var _last_target_time = Time.get_ticks_msec()
var _distance:float = 0

@onready var Socket = $/root/Node3D/Sockets
@export var highlightMaterial = preload("res://Materials/highlight.tres")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	_child = self.get_children()[0]
	_defaultMaterial = _child.material
	pass # Replace with function body.

func UpdatePositionScale(newPosition: Vector3, newScale: Vector3):
	_distance = position.distance_to(newPosition)
	_target = newPosition
	_target_scale = newScale
	_last_target_time = _cur_target_time
	_cur_target_time = Time.get_ticks_msec()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if type == "dynamic":
		position = position.lerp(_target, delta * _distance)
		scale = scale.lerp(_target_scale, delta)
	else:
		return
		
	if "highlights" in Socket.data:
		var highlight: String = Socket.data["highlights"]
		highlight = highlight.replace("[", "")
		highlight = highlight.replace("]", "")
		var highlights: Array = highlight.split(",")
		if str(id) in highlights:
			_child.material = highlightMaterial
		else:
			_child.material = _defaultMaterial
