extends Node
var socket = WebSocketPeer.new()
var data = {}
var lastDataEntry = Time.get_ticks_msec()
var connectRetryTime = 2000 # msec
var connectingSince = Time.get_ticks_msec()
var status = ""

@onready var Notifications = $/root/Node3D/UI/Notifications

func GetData():
	return data

func Connect():
	Notifications.SendNotification("Connecting to socket...", 2000)
	socket.connect_to_url("ws://localhost:37522")
	connectingSince = Time.get_ticks_msec()
	status = "Connecting"

func _ready() -> void:
	socket.inbound_buffer_size = 65535*10
	Connect()

# https://forum.godotengine.org/t/working-example-of-compress-decompress-with-streampeergzip/51831/2
func gzip_decode(data):
	var gzip = StreamPeerGZIP.new()
	gzip.start_decompression()
	gzip.put_data(data)
	gzip.finish()
	var string = gzip.get_utf8_string(gzip.get_available_bytes())
	return string

func gzip_encode(text: String):
	var gzip = StreamPeerGZIP.new()
	gzip.start_compression()
	gzip.put_data(text.to_utf8_buffer())
	gzip.finish()
	return gzip.get_data(gzip.get_available_bytes())[1]

func _process(delta):
	socket.poll()
	var state = socket.get_ready_state()
	
	if Time.get_ticks_msec() - connectingSince > connectRetryTime and state == 0:
		Connect()
	elif state == 0:
		status = "Please enable the Sockets plugin!\nRetrying connection in " + str(2000 - (Time.get_ticks_msec() - connectingSince)) + "ms"

	
	if state == WebSocketPeer.STATE_OPEN:
		if status == "Connecting":
			Notifications.SendNotification("Socket connected!", 2000)
		status = "Connected"
		var tempData = {}
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			packet = gzip_decode(packet)
			packet = packet.split(";")
			for packetData in packet:
				# Find the first :
				var index = 0
				for character in packetData:
					if character == ":":
						break
					index += 1

				if index == 0:
					continue
			
				if index == len(packetData):
					continue
					
				# Split the string
				var key = packetData.substr(0, index)
				var data = packetData.substr(index + 1, -1)
				
				# Convert to json if needed
				if "JSON" in key:
					key.replace("JSON", "")
					var json = JSON.new()
					var error = json.parse(data)
					if error == OK:
						data = json
					else:
						data = "Error parsing JSON: " + str(error_string(error))
					
				tempData.get_or_add(key)
				tempData[key] = data
		
		if tempData != {}:
			data = tempData
			lastDataEntry = Time.get_ticks_msec()
			# Acknowledge the packet
			socket.send_text("ok")
		
	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass
		
	elif state == WebSocketPeer.STATE_CLOSED:
		Notifications.SendNotification("Socket lost connection!", 2000, Color.YELLOW)
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		Connect()
