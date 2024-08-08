extends Node3D

var _target = Vector3(0,0,0)
var _target_scale = Vector3(0,0,0)
var _cur_target_time = Time.get_ticks_msec()
var _last_target_time = Time.get_ticks_msec()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.

func UpdatePositionScale(newPosition: Vector3, newScale: Vector3):
	_target = newPosition
	_target_scale = newScale
	_last_target_time = _cur_target_time
	_cur_target_time = Time.get_ticks_msec()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	position = position.lerp(_target, delta)
	scale = scale.lerp(_target_scale, delta)
