extends Node

@export var images : Array[CompressedTexture2D]
@export var timePerImage : float
@export var sprite : Sprite2D
@export var modulateTime : float
@export var nextScene : PackedScene

var imageIndex = 0
var startTime = Time.get_ticks_msec()

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if Time.get_ticks_msec() - startTime > timePerImage * 1000:
		imageIndex += 1
		startTime = Time.get_ticks_msec()
	
	# End fading
	if Time.get_ticks_msec() - startTime > timePerImage * 1000 - modulateTime * 1000:
		var curTime = Time.get_ticks_msec() - startTime - timePerImage * 1000 + modulateTime * 1000
		var percentage = curTime / (modulateTime * 1000)
		sprite.self_modulate = Color8(255, 255, 255, int(255 - percentage * 255))
	
	# Start fading
	if Time.get_ticks_msec() - startTime < modulateTime * 1000:
		var curTime = Time.get_ticks_msec() - startTime
		var percentage = curTime / (modulateTime * 1000)
		sprite.self_modulate = Color8(255, 255, 255, int(percentage * 255))
	
	if imageIndex > len(images) - 1:
		get_tree().change_scene_to_packed(nextScene)
	else:
		sprite.texture = images[imageIndex]
