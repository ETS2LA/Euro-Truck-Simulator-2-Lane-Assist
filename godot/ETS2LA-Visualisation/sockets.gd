extends Node
var socket = WebSocketPeer.new()
var data = {}
var lastDataEntry = Time.get_ticks_msec()

func GetData():
	return data

func _ready():
	socket.connect_to_url("ws://localhost:37522")

func _process(delta):
	socket.poll()
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		var tempData = {}
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			# Decode it
			packet = packet.get_string_from_utf8()
			packet = packet.split(",")
			for packetData in packet:
				packetData = packetData.split(":")
				if len(packetData) != 2:
					continue
				tempData.get_or_add(packetData[0])
				tempData[packetData[0]] = packetData[1]
		
		if tempData != {}:
			data = tempData
			lastDataEntry = Time.get_ticks_msec()
			# Acknowledge the packet
			socket.send_text("ok")
		
	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass
		
	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
