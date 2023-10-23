extends Node

var http

var globalRoads

func _ready():
	http = get_node("/root/Node3D/HTTPRequest")
	http.request_completed.connect(self.RequestComplete)

	# Perform a GET request. The URL below returns JSON as of writing.
	print("Getting data")
	var error = http.request("http://127.0.0.1:39847")
	if error != OK:
		push_error("An error occurred in the HTTP request.")

# Called when the HTTP request is completed.
func RequestComplete(result, response_code, headers, body):
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	
	var roads = response["GPS"]["roads"]
	
	print(roads)

	# Will print the user agent string used by the HTTPRequest node (as recognized by httpbin.org).
	# print(response.headers["User-Agent"])
