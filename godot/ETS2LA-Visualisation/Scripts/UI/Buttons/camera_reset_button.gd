extends Button

@onready var tracker = $/root/Node3D/TruckTracker

# Called when the node enters the scene tree for the first time.
func _pressed() -> void:
	tracker.mouseOffsetRotation = Vector3(0,0,0)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	self.disabled = tracker.mouseOffsetRotation == Vector3(0,0,0)
