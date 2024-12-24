extends VBoxContainer

var _notifications = []

@export var fadePercentage = 20
@export var endFadeStartPercentage = 80

@onready var Variables = $/root/Node3D/Variables

class Notification:
	var text
	var time
	var timeout
	var label
	func IsTimedOut():
		if Time.get_ticks_msec() - time > timeout:
			return true
		else:
			return false

func SendNotification(text, timeout, color = null):
	if color == null:
		if Variables != null and Variables.darkMode:
			color = Color8(255, 255, 255, 255)
		else:
			color = Color8(0, 0, 0, 255)
	
	var notif = Notification.new()
	
	notif.text = text
	notif.time = Time.get_ticks_msec()
	
	if timeout < 100:
		notif.timeout = timeout * 1000
	else:
		notif.timeout = timeout
	
	var label = Label.new()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.label_settings = LabelSettings.new()
	label.label_settings.font_color = color
	label.text = notif.text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)
	notif.label = label
	
	_notifications.append(notif)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# Check if the notifications are too old
	for notification in _notifications:
		if notification.IsTimedOut():
			var label = notification.label
			remove_child(label)
			label.queue_free()
			var index = _notifications.find(notification)
			_notifications.remove_at(index)
		else:
			var percentage = (Time.get_ticks_msec() - notification.time) / (notification.timeout / 100)
			if percentage < fadePercentage:
				var curPercentage = (percentage * 100) / fadePercentage
				var alpha = 2.55 * curPercentage
				var curColor = notification.label.label_settings.font_color
				notification.label.label_settings.font_color = Color8(int(curColor.r * 255), int(curColor.g * 255), int(curColor.b * 255), int(alpha))
			elif percentage > endFadeStartPercentage:
				var curPercentage = 100 - ((percentage - endFadeStartPercentage) * 100) / fadePercentage
				var alpha = 2.55 * curPercentage
				var curColor = notification.label.label_settings.font_color
				notification.label.label_settings.font_color = Color8(int(curColor.r * 255), int(curColor.g * 255), int(curColor.b * 255), int(alpha))
