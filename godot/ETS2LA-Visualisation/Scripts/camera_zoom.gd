extends Camera3D

var targetSize = 0.05
@onready var Variables = $/root/Node3D/Variables

@export var lightEnvironment = preload("res://Environments/default.tres")
@export var darkEnvironment = preload("res://Environments/defaultDark.tres")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	Variables.ThemeChanged.connect(OnThemeChange)

func OnThemeChange():
	var darkMode = Variables.darkMode
	if darkMode:
		self.environment = darkEnvironment
	else:
		self.environment = lightEnvironment

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	
	if Input.is_action_just_pressed("ZoomIn"):
		if targetSize > 0.01:
			targetSize -= 0.005
	
	if Input.is_action_just_pressed("ZoomOut"):
		if targetSize < 0.20:
			targetSize += 0.005
	
	self.size = lerp(self.size, targetSize, delta * 5)
	
	pass
