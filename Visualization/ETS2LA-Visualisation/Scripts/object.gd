extends Node3D

var id:int = 0
var type = "dynamic"

var _defaultMaterial:BaseMaterial3D
var _child = null
var _target = Vector3(0,0,0)
var _last_target = Vector3(0,0,0)
var _target_scale = Vector3(0,0,0)
var _cur_target_time = Time.get_ticks_msec()
var _last_target_time = Time.get_ticks_msec()
var _distance:float = 0
var _rotation = Vector3(0,0,0)

@onready var Socket = $/root/Node3D/Sockets
@export var highlightMaterial = preload("res://Materials/highlight.tres")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	_child = self.get_children()[0]
	if "material" in _child:
		_defaultMaterial = _child.material

func UpdatePositionScale(newPosition: Vector3, newScale: Vector3):
	_distance = position.distance_to(newPosition)
	if position.distance_to(_last_target) > 8: # limit the distance so that they don't spin at traffic lights
		_last_target = position
	_target = newPosition
	_target_scale = newScale
	_last_target_time = _cur_target_time
	_cur_target_time = Time.get_ticks_msec()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if type == "dynamic":
		position = position.lerp(_target, delta * (_cur_target_time - _last_target_time))
		scale = scale.lerp(_target_scale, delta)
		rotation.y = atan2(-(_target.x - _last_target.x),-(_target.z - _last_target.z))
		#rotation.y=lerp(rotation.y,atan2(-(_target.x - _last_target.x),-(_target.z - _last_target.z)),delta*10)
		#self.look_at_from_position(_last_target, _target)
	else:
		return
		
	if "highlights" in Socket.data:
		var highlight: String = Socket.data["highlights"]
		highlight = highlight.replace("[", "")
		highlight = highlight.replace("]", "")
		var highlights: Array = highlight.split(",")
		
		if "material" in _child:
			if str(id) in highlights:
				_child.material = highlightMaterial
			else:
				_child.material = _defaultMaterial
