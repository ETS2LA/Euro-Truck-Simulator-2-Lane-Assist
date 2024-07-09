extends Camera3D

var isFrustrum = self.projection == Camera3D.ProjectionType.PROJECTION_FRUSTUM
var targetSize = 0.05 if isFrustrum else 48.4

@onready var Variables = $/root/Node3D/Variables
@onready var Sockets = $/root/Node3D/Sockets

@export var fovMultiplierAt0Speed = 1
@export var fovMultiplierAt80Speed = 0.6

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
	var data = Sockets.data
	var speed = 1
	if data != {}:
		speed = float(data["speed"]) * 3.6 # m/s > kph
	
	if speed < 0.1:
		speed = 0.1
	if speed > 80:
		speed = 80
		
	var zoomMultiplier = fovMultiplierAt0Speed + (speed/80) * (fovMultiplierAt80Speed - fovMultiplierAt0Speed)
	
	if Input.is_action_just_pressed("ZoomIn"):
		if targetSize > 0.01:
			if isFrustrum:
				targetSize -= 0.005
			else: 
				targetSize -= 0.5
	
	if Input.is_action_just_pressed("ZoomOut"):
		if isFrustrum:
			if targetSize < 0.20:
				targetSize += 0.005
		else:
			if targetSize < 180:
				targetSize += 0.5
	
	if isFrustrum:
		self.size = lerp(self.size, targetSize * zoomMultiplier, delta * 5)
	else:
		self.fov = lerp(self.fov, targetSize * zoomMultiplier, delta * 15)
	
	pass
