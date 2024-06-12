extends Camera3D

@export var target : Node3D
@export var offset : Vector3

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	if target == null:
		print("WARNING: Camera has no target set!")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	
	pass
