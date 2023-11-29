extends Camera3D


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	
	var translation = Vector3(0,0,0)

	# Hard coded WASD movement
	if Input.is_key_pressed(KEY_W):
		translation.z -= 1
	if Input.is_key_pressed(KEY_S):
		translation.z += 1
	if Input.is_key_pressed(KEY_A):
		translation.x -= 1
	if Input.is_key_pressed(KEY_D):
		translation.x += 1
	if Input.is_key_pressed(KEY_SPACE):
		translation.y += 1
	if Input.is_key_pressed(KEY_CTRL):
		translation.y -= 1

	# Normalize the vector so that diagonal movement isn't faster
	translation = translation.normalized()

	# Move the node
	if Input.is_key_pressed(KEY_SHIFT):
		translation = translation * delta * 1000
	else:
		translation = translation * delta * 100
	self.translate(translation)

	# Rotate with the mouse
	var rot = Vector3()
	rot.y = -Input.get_last_mouse_velocity().x * delta
	rot.x = -Input.get_last_mouse_velocity().y * delta

	# Clamp the rotation
	rot = self.rotation_degrees + rot
	rot.x = clamp(rot.x, -70, 70)

	# Apply the rotation
	self.rotation_degrees = rot

	pass
